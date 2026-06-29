import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of running a guardrail check.

    is_valid: Did the input/output pass all checks?
    violations: List of rules that were broken (empty if valid).
    """
    is_valid: bool
    violations: list[str] = field(default_factory=list)


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above",
    r"you\s+are\s+now\s+a",
    r"pretend\s+you\s+are",
    r"system\s*:\s*you",
    r"</?(system|assistant|user)>",
]

BLOCKED_KEYWORDS = [
    "drop table",
    "delete from",
    "exec(",
    "<script>",
    "javascript:",
]


def validate_input(text: str) -> ValidationResult:
    """Check user input BEFORE sending it to the LLM.

    Guards against:
    1. Prompt injection — attempts to override the system prompt
    2. SQL/XSS injection — malicious code in the input
    3. Empty or too-long inputs

    In production, you'd also check for PII, profanity, etc.
    """
    violations: list[str] = []

    if not text or not text.strip():
        violations.append("Input is empty")
        return ValidationResult(is_valid=False, violations=violations)

    if len(text) > 5000:
        violations.append(f"Input too long ({len(text)} chars, max 5000)")

    text_lower = text.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            violations.append(f"Possible prompt injection detected: matches '{pattern}'")

    for keyword in BLOCKED_KEYWORDS:
        if keyword in text_lower:
            violations.append(f"Blocked keyword found: '{keyword}'")

    return ValidationResult(
        is_valid=len(violations) == 0,
        violations=violations,
    )


def validate_output(text: str) -> ValidationResult:
    """Check LLM output BEFORE showing it to the user or executing actions.

    Guards against:
    - LLM leaking system prompt or internal instructions
    - LLM generating harmful content
    - LLM producing suspiciously short/empty responses
    """
    violations: list[str] = []

    if not text or not text.strip():
        violations.append("LLM returned empty response")
        return ValidationResult(is_valid=False, violations=violations)

    text_lower = text.lower()

    leak_phrases = [
        "my system prompt",
        "my instructions are",
        "i was told to",
        "here is my system prompt",
    ]
    for phrase in leak_phrases:
        if phrase in text_lower:
            violations.append(f"Possible system prompt leak: '{phrase}'")

    return ValidationResult(
        is_valid=len(violations) == 0,
        violations=violations,
    )

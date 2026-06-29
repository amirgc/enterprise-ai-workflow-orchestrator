import json
from enum import Enum

from pydantic import BaseModel, Field


class RequestCategory(str, Enum):
    """Valid categories for vendor requests — must match the prompt template."""
    NEW_VENDOR = "new_vendor"
    UPDATE_VENDOR = "update_vendor"
    COMPLIANCE_CHECK = "compliance_check"
    PAYMENT_CHANGE = "payment_change"


class ClassificationResult(BaseModel):
    """Validates the LLM's classification output.

    If the LLM returns {"category": "banana", "confidence": 2.0},
    Pydantic will reject it because:
    - "banana" is not in RequestCategory
    - 2.0 is not between 0.0 and 1.0
    """
    category: RequestCategory
    confidence: float = Field(ge=0.0, le=1.0)


class VendorInfo(BaseModel):
    """Validates the LLM's extracted vendor fields.

    Fields are Optional (str | None) because the user's request
    might not mention all of them. That's fine — we detect missing
    fields in a later pipeline step.
    """
    vendor_name: str | None = None
    vendor_type: str | None = None
    payment_terms: str | None = None
    contact_email: str | None = None
    country: str | None = None

    def missing_fields(self) -> list[str]:
        """Return names of fields that are still None.

        Used later to ask the user for missing information.
        """
        return [
            field_name
            for field_name, value in self.model_dump().items()
            if value is None
        ]


def parse_llm_json(raw_text: str, model_class: type[BaseModel]) -> BaseModel:
    """Parse LLM text output into a validated Pydantic model.

    LLMs sometimes wrap JSON in markdown code blocks like ```json ... ```.
    This function strips that before parsing.

    Args:
        raw_text: The raw string from the LLM (may include markdown).
        model_class: Which Pydantic model to validate against.

    Returns:
        A validated instance of model_class.

    Raises:
        ValueError: If the JSON is invalid or doesn't match the schema.
    """
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]  # remove opening ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # remove closing ```
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}")

    return model_class.model_validate(data)

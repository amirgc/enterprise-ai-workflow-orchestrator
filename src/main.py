"""Vendor Onboarding Pipeline — wires all components together.

Pipeline steps:
1. Validate input (guardrails)
2. Classify the request
3. Extract vendor fields
4. Search relevant policies (RAG)
5. Check compliance (tool use)
6. Human approval
7. Create vendor record (tool use)
8. Log metrics
"""

from src.config import settings
from src.providers.claude import ClaudeProvider
from src.providers.openai_provider import OpenAIProvider
from src.providers.base import BaseLLMProvider
from src.prompts.registry import PromptRegistry
from src.models.schemas import (
    ClassificationResult,
    VendorInfo,
    parse_llm_json,
)
from src.rag.store import PolicyStore
from src.tools.registry import ToolRegistry
from src.tools.compliance import check_vendor_compliance, COMPLIANCE_TOOL_DEFINITION
from src.tools.workflow import create_vendor_record, WORKFLOW_TOOL_DEFINITION
from src.guardrails.validators import validate_input, validate_output
from src.approval.gate import ApprovalGate
from src.observability.logger import PipelineMetrics, Timer


def create_provider() -> BaseLLMProvider:
    """Create the LLM provider based on settings.

    This is the provider pattern in action — the rest of the code
    doesn't know or care whether it's Claude or OpenAI.
    """
    if settings.default_provider.value == "claude":
        return ClaudeProvider()
    return OpenAIProvider()


def setup_tools() -> ToolRegistry:
    """Register all tools the LLM can call.

    This is where we connect tool DEFINITIONS (what the LLM sees)
    to tool HANDLERS (the actual Python functions).
    """
    registry = ToolRegistry()

    registry.register(
        **COMPLIANCE_TOOL_DEFINITION,
        handler=check_vendor_compliance,
    )
    registry.register(
        **WORKFLOW_TOOL_DEFINITION,
        handler=create_vendor_record,
    )

    return registry


def run_pipeline(request_text: str):
    """Run the full vendor onboarding pipeline.

    This is the main function that orchestrates all 8 steps.
    """
    metrics = PipelineMetrics()
    provider = create_provider()
    prompts = PromptRegistry()
    policies = PolicyStore()
    tools = setup_tools()
    approval = ApprovalGate()

    print(f"\nProcessing: \"{request_text}\"")
    print(f"Provider: {settings.default_provider.value}")
    print(f"Model: {provider.model}")

    # ── Step 1: Validate input ──────────────────────────────────
    print("\n[Step 1] Validating input...")
    validation = validate_input(request_text)
    if not validation.is_valid:
        print(f"  BLOCKED: {validation.violations}")
        return
    print("  Input is clean.")

    # ── Step 2: Classify the request ────────────────────────────
    print("\n[Step 2] Classifying request...")
    classify_prompt = prompts.get("classify_v1", request_text=request_text)

    with Timer() as t:
        response = provider.generate(classify_prompt)

    output_check = validate_output(response.content)
    if not output_check.is_valid:
        print(f"  OUTPUT BLOCKED: {output_check.violations}")
        return

    classification = parse_llm_json(response.content, ClassificationResult)
    metrics.record_call("classify", response.model, response.input_tokens,
                        response.output_tokens, t.elapsed_ms)

    print(f"  Category: {classification.category.value}")
    print(f"  Confidence: {classification.confidence}")

    # ── Step 3: Extract vendor fields ───────────────────────────
    print("\n[Step 3] Extracting vendor fields...")
    extract_prompt = prompts.get("extract_v1", request_text=request_text)

    with Timer() as t:
        response = provider.generate(extract_prompt)

    vendor_info = parse_llm_json(response.content, VendorInfo)
    metrics.record_call("extract", response.model, response.input_tokens,
                        response.output_tokens, t.elapsed_ms)

    print(f"  Vendor: {vendor_info.vendor_name}")
    print(f"  Type: {vendor_info.vendor_type}")
    print(f"  Payment: {vendor_info.payment_terms}")
    print(f"  Country: {vendor_info.country}")
    print(f"  Email: {vendor_info.contact_email}")

    missing = vendor_info.missing_fields()
    if missing:
        print(f"  Missing fields: {missing}")

    # ── Step 4: Retrieve relevant policies (RAG) ────────────────
    print("\n[Step 4] Searching policies (RAG)...")
    query = f"{vendor_info.vendor_type} {vendor_info.country} {vendor_info.payment_terms}"
    matches = policies.search(query)

    for match in matches:
        print(f"  Found: {match.title} (relevance: {match.relevance_score:.0%})")

    policy_context = policies.format_context(matches)

    # ── Step 5: Check compliance (tool use) ─────────────────────
    print("\n[Step 5] Running compliance check...")

    if vendor_info.vendor_name and vendor_info.country and vendor_info.vendor_type:
        compliance_result = tools.execute("check_vendor_compliance", {
            "vendor_name": vendor_info.vendor_name,
            "country": vendor_info.country,
            "vendor_type": vendor_info.vendor_type,
        })

        print(f"  Passed: {compliance_result['passed']}")
        print(f"  Requires review: {compliance_result['requires_review']}")
        for issue in compliance_result["issues"]:
            print(f"    - {issue}")

        if not compliance_result["passed"]:
            print("\n  PIPELINE STOPPED — vendor failed compliance.")
            metrics.print_report()
            return
    else:
        print("  Skipped — missing required fields for compliance check.")
        compliance_result = None

    # ── Step 6: Human approval ──────────────────────────────────
    print("\n[Step 6] Requesting approval...")

    approval_details = vendor_info.model_dump()
    approval_details["category"] = classification.category.value
    approval_details["compliance"] = compliance_result

    request = approval.request_approval(
        action="create_vendor_record",
        details=approval_details,
        reason=f"New vendor onboarding — {classification.category.value}",
    )

    if not approval.is_approved(request):
        print(f"\n  REJECTED: {request.reviewer_notes}")
        metrics.print_report()
        return

    # ── Step 7: Create vendor record (tool use) ─────────────────
    print("\n[Step 7] Creating vendor record...")

    vendor_record = tools.execute("create_vendor_record", {
        "vendor_name": vendor_info.vendor_name or "Unknown",
        "vendor_type": vendor_info.vendor_type or "Unknown",
        "payment_terms": vendor_info.payment_terms or "Net 30",
        "contact_email": vendor_info.contact_email or "not provided",
        "country": vendor_info.country or "US",
    })

    print(f"  Vendor ID: {vendor_record['vendor_id']}")
    print(f"  Status: {vendor_record['status']}")

    # ── Step 8: Print metrics ───────────────────────────────────
    metrics.print_report()

    print("\n  Pipeline complete!")
    return vendor_record


if __name__ == "__main__":
    request = input("\nEnter a vendor request (or press Enter for a sample):\n> ").strip()

    if not request:
        request = (
            "Onboard ABC Supplies as a new vendor. "
            "They provide office equipment from Germany. "
            "Payment terms are Net 30. Contact: vendor@abc-supplies.de"
        )

    run_pipeline(request)

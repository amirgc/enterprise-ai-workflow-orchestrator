import uuid
from datetime import datetime, timezone


def create_vendor_record(
    vendor_name: str,
    vendor_type: str,
    payment_terms: str,
    contact_email: str,
    country: str,
) -> dict:
    """Create a new vendor record in the system.

    In production, this would write to a database or call an ERP API.
    Here we simulate by returning what the record would look like.

    The LLM calls this tool after all checks pass and approval is granted.
    """
    return {
        "vendor_id": str(uuid.uuid4())[:8],
        "vendor_name": vendor_name,
        "vendor_type": vendor_type,
        "payment_terms": payment_terms,
        "contact_email": contact_email,
        "country": country,
        "status": "pending_approval",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


WORKFLOW_TOOL_DEFINITION = {
    "name": "create_vendor_record",
    "description": "Create a new vendor record in the system after compliance checks pass",
    "parameters": {
        "type": "object",
        "properties": {
            "vendor_name": {
                "type": "string",
                "description": "Legal name of the vendor",
            },
            "vendor_type": {
                "type": "string",
                "description": "Type of goods or services provided",
            },
            "payment_terms": {
                "type": "string",
                "description": "Payment terms (e.g., Net 30)",
            },
            "contact_email": {
                "type": "string",
                "description": "Primary contact email address",
            },
            "country": {
                "type": "string",
                "description": "Country of operation",
            },
        },
        "required": ["vendor_name", "vendor_type", "payment_terms", "contact_email", "country"],
    },
}

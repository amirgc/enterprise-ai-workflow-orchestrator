SANCTIONED_COUNTRIES = {"North Korea", "Iran", "Syria", "Cuba", "Russia"}


def check_vendor_compliance(vendor_name: str, country: str, vendor_type: str) -> dict:
    """Check if a vendor passes basic compliance rules.

    In production, this would call external APIs (sanctions databases,
    business registries, etc). Here we simulate with simple rules.

    This function is registered as a 'tool' — the LLM can decide to call it
    when processing a vendor onboarding request.
    """
    issues: list[str] = []
    requires_review = False

    if country in SANCTIONED_COUNTRIES:
        issues.append(f"{country} is a sanctioned country — vendor is blocked")

    if country != "US":
        requires_review = True
        issues.append("International vendor — requires compliance team review")

    if vendor_type and vendor_type.lower() in ("it services", "software", "saas"):
        requires_review = True
        issues.append("IT/Software vendor — requires security assessment (SOC 2)")

    passed = len(issues) == 0 or all("requires" in i for i in issues)

    return {
        "vendor_name": vendor_name,
        "passed": passed,
        "requires_review": requires_review,
        "issues": issues if issues else ["No compliance issues found"],
    }


COMPLIANCE_TOOL_DEFINITION = {
    "name": "check_vendor_compliance",
    "description": "Check if a vendor meets compliance requirements based on their country and type of service",
    "parameters": {
        "type": "object",
        "properties": {
            "vendor_name": {
                "type": "string",
                "description": "The name of the vendor to check",
            },
            "country": {
                "type": "string",
                "description": "The country where the vendor operates",
            },
            "vendor_type": {
                "type": "string",
                "description": "The type of goods or services the vendor provides",
            },
        },
        "required": ["vendor_name", "country", "vendor_type"],
    },
}

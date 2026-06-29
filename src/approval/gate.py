from dataclasses import dataclass
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalRequest:
    """A request waiting for human approval.

    Contains all the context a human reviewer needs to make a decision.
    """
    action: str
    details: dict
    reason: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewer_notes: str = ""


class ApprovalGate:
    """Pauses the pipeline and waits for human approval before executing.

    Why human-in-the-loop?
    - AI can make mistakes — a human catches errors before they hit production
    - Compliance may require human sign-off for certain actions
    - Builds trust — users see what the AI wants to do before it happens

    In production, this would integrate with Slack, email, or a web UI.
    Here we use terminal input to simulate the approval flow.
    """

    def __init__(self):
        self.history: list[ApprovalRequest] = []

    def request_approval(self, action: str, details: dict, reason: str) -> ApprovalRequest:
        """Create an approval request and prompt the human reviewer.

        Args:
            action: What the AI wants to do (e.g., "create_vendor_record")
            details: The data it will use (e.g., vendor name, country)
            reason: Why it needs approval (e.g., "International vendor")
        """
        request = ApprovalRequest(action=action, details=details, reason=reason)

        print("\n" + "=" * 60)
        print("  APPROVAL REQUIRED")
        print("=" * 60)
        print(f"  Action:  {action}")
        print(f"  Reason:  {reason}")
        print(f"  Details:")
        for key, value in details.items():
            print(f"    {key}: {value}")
        print("=" * 60)

        response = input("\n  Approve? (y/n): ").strip().lower()

        if response == "y":
            request.status = ApprovalStatus.APPROVED
            notes = input("  Notes (optional, press Enter to skip): ").strip()
            request.reviewer_notes = notes
        else:
            request.status = ApprovalStatus.REJECTED
            notes = input("  Rejection reason: ").strip()
            request.reviewer_notes = notes

        self.history.append(request)
        return request

    def is_approved(self, request: ApprovalRequest) -> bool:
        """Check if a request was approved."""
        return request.status == ApprovalStatus.APPROVED

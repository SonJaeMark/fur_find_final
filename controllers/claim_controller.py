from repositories.claim_repository import ClaimRepository
from repositories.match_repository import MatchRepository
from repositories.report_repository import ReportRepository
from repositories.audit_repository import AuditRepository
from core.exceptions import ValidationError, AuthorizationError, ResourceNotFoundError


class ClaimController:
    """Handles claim verification requests and disputes raised by pet owners."""
    TYPES = ("Claim", "Dispute")

    def __init__(self, claim_repo=None, match_repo=None, report_repo=None, audit_repo=None):
        self.claim_repo = claim_repo or ClaimRepository()
        self.match_repo = match_repo or MatchRepository()
        self.report_repo = report_repo or ReportRepository()
        self.audit_repo = audit_repo or AuditRepository()

    def submit_claim(self, user_id: int, match_id: int, claim_type: str, message: str) -> int:
        if claim_type not in self.TYPES:
            raise ValidationError("Invalid submission type.")
        message = (message or "").strip()
        if len(message) < 10:
            raise ValidationError("Please provide at least 10 characters of explanation.")

        match = self.match_repo.get_match_by_id(match_id)
        if not match:
            raise ResourceNotFoundError("Match record not found.")
        lost = self.report_repo.get_by_id(match["lost_report_id"])
        found = self.report_repo.get_by_id(match["found_report_id"])
        if not lost or not found:
            raise ResourceNotFoundError("One of the reports in this match no longer exists.")
        if user_id not in (lost["user_id"], found["user_id"]):
            raise AuthorizationError("You can only submit claims for your own cases.")
        if claim_type == "Claim" and match["status"] in ("Approved", "Rejected"):
            raise ValidationError("This match is already closed. Submit a dispute instead.")

        claim_id = self.claim_repo.create_claim(match_id, user_id, claim_type, message)
        self.audit_repo.log_action(user_id=user_id, action=f"{claim_type.upper()}_SUBMITTED",
                                   details=f"{claim_type} submitted for match {match_id}.")
        return claim_id

    def get_claims_for_match(self, match_id: int) -> list[dict]:
        return self.claim_repo.get_by_match(match_id)
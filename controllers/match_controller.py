from repositories.match_repository import MatchRepository
from repositories.report_repository import ReportRepository
from repositories.audit_repository import AuditRepository
from core.exceptions import ValidationError, DatabaseError


class MatchController:
    """Manages match queue processing, admin approvals, rejections, and final case closures."""

    def __init__(self, match_repo: MatchRepository = None, report_repo: ReportRepository = None, audit_repo: AuditRepository = None):
        self.match_repo = match_repo or MatchRepository()
        self.report_repo = report_repo or ReportRepository()
        self.audit_repo = audit_repo or AuditRepository()

    def get_pending_matches(self) -> list[dict]:
        """Retrieve matches awaiting human admin review."""
        return self.match_repo.get_matches_by_status("Pending Admin Verification")

    def approve_match(self, match_id: int, admin_user_id: int, notes: str = "") -> bool:
        """Approve match, resolve reports, and log recovery in audit trail."""
        match_item = self.match_repo.get_match_by_id(match_id)
        if not match_item:
            raise ValidationError("Match record not found.")

        # Update Match Record Status
        self.match_repo.update_match_status(match_id, status="Approved", notes=notes)

        # Update underlying lost & found report statuses to Resolved/Recovered
        self.report_repo.update_report_status(match_item["lost_report_id"], status="Resolved")
        self.report_repo.update_report_status(match_item["found_report_id"], status="Resolved")

        self.audit_repo.log_action(
            user_id=admin_user_id,
            action="VERIFY_MATCH_APPROVE",
            details=f"Admin ID {admin_user_id} approved match {match_id}. Case closed."
        )
        return True

    def reject_match(self, match_id: int, admin_user_id: int, reason: str = "") -> bool:
        """Reject potential match suggestion."""
        match_item = self.match_repo.get_match_by_id(match_id)
        if not match_item:
            raise ValidationError("Match record not found.")

        self.match_repo.update_match_status(match_id, status="Rejected", notes=reason)
        self.audit_repo.log_action(
            user_id=admin_user_id,
            action="VERIFY_MATCH_REJECT",
            details=f"Admin ID {admin_user_id} rejected match {match_id}. Reason: {reason}"
        )
        return True
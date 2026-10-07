import os
from datetime import datetime
from models.pet_report import PetReport
from repositories.report_repository import ReportRepository
from repositories.match_repository import MatchRepository
from repositories.audit_repository import AuditRepository
from utils.matching_engine import MatchingEngine
from utils.validator import Validator
from core.exceptions import ValidationError, DatabaseError


class ReportController:
    """Handles submission, edit, search, and automatic match generation for pet reports."""

    def __init__(self, report_repo: ReportRepository = None, match_repo: MatchRepository = None, audit_repo: AuditRepository = None):
        self.report_repo = report_repo or ReportRepository()
        self.match_repo = match_repo or MatchRepository()
        self.audit_repo = audit_repo or AuditRepository()

    def submit_report(self, user_id: int, category: str, pet_name: str, species: str, breed: str,
                      gender: str, primary_color: str, secondary_color: str,
                      distinguishing_marks: str, incident_date: datetime, location: str, photo_path: str) -> PetReport:
        """Submit a new Lost or Found pet report and run match detection."""
        # Validate photo path
        if not photo_path or not os.path.exists(photo_path):
            raise ValidationError("A valid photo file must be provided and exist on disk.")

        report = PetReport(
            report_id=None,
            user_id=user_id,
            category=category,  # "Lost" or "Found"
            pet_name=pet_name.strip() if pet_name else "Unknown",
            species=species.strip(),
            breed=breed.strip(),
            gender=gender.strip(),
            primary_color=primary_color.strip(),
            secondary_color=secondary_color.strip() if secondary_color else "",
            distinguishing_marks=distinguishing_marks.strip() if distinguishing_marks else "",
            incident_date=incident_date,
            location=location.strip(),
            photo_path=photo_path,
            status="Active"
        )

        created_report = self.report_repo.create_report(report)
        self.audit_repo.log_action(
            user_id=user_id,
            action="CREATE_REPORT",
            details=f"Created {category} pet report ID {created_report.report_id}"
        )

        # Trigger Matching Engine against existing complementary reports
        self._trigger_matching_engine(created_report)
        return created_report

    def search_reports(self, filters: dict) -> list[PetReport]:
        """Unified search across reports using specified filter criteria."""
        return self.report_repo.search_reports(filters)

    def _trigger_matching_engine(self, target_report: PetReport) -> None:
        """Compare submitted report against existing inverse-category reports."""
        opposite_category = "Found" if target_report.category == "Lost" else "Lost"
        candidates = self.report_repo.get_reports_by_category(opposite_category, status="Active")

        for candidate in candidates:
            if target_report.category == "Lost":
                lost_rep, found_rep = target_report, candidate
            else:
                lost_rep, found_rep = candidate, target_report

            score = MatchingEngine.calculate_match_score(lost_rep, found_rep)
            if score >= 50.0:  # Match threshold score
                self.match_repo.create_match_entry(
                    lost_report_id=lost_rep.report_id,
                    found_report_id=found_rep.report_id,
                    score=score,
                    status="Pending Admin Verification"
                )
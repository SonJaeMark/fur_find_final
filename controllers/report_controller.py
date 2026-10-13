import os
from datetime import datetime
from models.pet_report import PetReport
from repositories.report_repository import ReportRepository
from repositories.match_repository import MatchRepository
from repositories.audit_repository import AuditRepository
from utils.matching_engine import MatchingEngine
from utils.validator import Validator
from core.exceptions import ValidationError, ResourceNotFoundError


class ReportController:
    """Handles submission, edit, search, soft-delete and automatic match generation for pet reports."""

    def __init__(self, report_repo: ReportRepository = None, match_repo: MatchRepository = None,
                 audit_repo: AuditRepository = None):
        self.report_repo = report_repo or ReportRepository()
        self.match_repo = match_repo or MatchRepository()
        self.audit_repo = audit_repo or AuditRepository()

    def submit_report(self, user_id: int, category: str, pet_name: str, species: str, breed: str,
                      gender: str, primary_color: str, secondary_color: str,
                      distinguishing_marks: str, incident_date: datetime, location: str,
                      photo_path: str) -> PetReport:
        if not photo_path or not os.path.exists(photo_path):
            raise ValidationError("A valid photo file must be provided and exist on disk.")

        report = PetReport(
            report_id=None, user_id=user_id, category=category,
            pet_name=pet_name.strip() if pet_name else "Unknown",
            species=species.strip(), breed=breed.strip(), gender=gender.strip(),
            primary_color=primary_color.strip(),
            secondary_color=secondary_color.strip() if secondary_color else "",
            distinguishing_marks=distinguishing_marks.strip() if distinguishing_marks else "",
            incident_date=incident_date, location=location.strip(),
            photo_path=photo_path, status="Active")

        report.report_id = self.report_repo.create_report({
            "user_id": user_id, "report_type": category, "pet_name": report.pet_name,
            "species": report.species, "breed": report.breed, "gender": report.gender,
            "primary_color": report.primary_color, "secondary_color": report.secondary_color,
            "distinguishing_marks": report.distinguishing_marks, "incident_date": incident_date,
            "location": report.location, "photo_path": photo_path, "status": report.status,
        })
        self.audit_repo.log_action(user_id=user_id, action="CREATE_REPORT",
                                   details=f"Created {category} pet report ID {report.report_id}")
        self._trigger_matching_engine(report)
        return report

    def search_reports(self, filters: dict) -> list[dict]:
        """filters may contain: species, report_type, status, keyword."""
        return self.report_repo.search_reports(**(filters or {}))

    def get_my_reports(self, user_id: int) -> list[dict]:
        return self.report_repo.get_by_user(user_id)

    def update_report(self, actor_id: int, report_id: int, data: dict) -> bool:
        if not self.report_repo.get_by_id(report_id):
            raise ResourceNotFoundError("Report not found.")
        clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in data.items()}
        for field in ("species", "primary_color", "location"):
            if field in clean:
                Validator.validate_non_empty(clean[field], field.replace("_", " ").title())
        self.report_repo.update_report(report_id, clean)
        self.audit_repo.log_action(user_id=actor_id, action="UPDATE_REPORT",
                                   details=f"User {actor_id} edited report {report_id}.")
        return True

    def delete_report(self, actor_id: int, report_id: int) -> bool:
        if not self.report_repo.get_by_id(report_id):
            raise ResourceNotFoundError("Report not found.")
        self.report_repo.soft_delete(report_id)
        self.audit_repo.log_action(user_id=actor_id, action="DELETE_REPORT",
                                   details=f"User {actor_id} soft-deleted report {report_id}.")
        return True

    def _trigger_matching_engine(self, target_report: PetReport) -> None:
        opposite = "Found" if target_report.category == "Lost" else "Lost"
        for candidate in self.report_repo.get_reports_by_category(opposite, status="Active"):
            if candidate.user_id == target_report.user_id:
                continue
            lost_rep, found_rep = ((target_report, candidate) if target_report.category == "Lost"
                                   else (candidate, target_report))
            score = MatchingEngine.calculate_match_score(lost_rep, found_rep)
            if score >= 50.0:
                self.match_repo.create_match_entry(
                    lost_report_id=lost_rep.report_id, found_report_id=found_rep.report_id,
                    score=score, status="Pending Admin Verification")
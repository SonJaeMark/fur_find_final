import csv
import io
from repositories.audit_repository import AuditRepository


class AuditController:
    """Handles retrieval and formatting of auditable system logs."""

    def __init__(self, audit_repo: AuditRepository = None):
        self.audit_repo = audit_repo or AuditRepository()

    def fetch_logs(self, limit: int = 100, user_id: int | None = None) -> list[dict]:
        """Fetch system audit log records."""
        return self.audit_repo.get_audit_logs(limit=limit, user_id=user_id)

    def export_logs_to_csv(self, file_path: str) -> str:
        """Export system activity trail to a CSV file."""
        logs = self.fetch_logs(limit=1000)
        
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Log ID", "Timestamp", "User ID", "Action", "Details"])
            for log in logs:
                writer.writerow([
                    log.get("log_id"),
                    log.get("timestamp"),
                    log.get("user_id"),
                    log.get("action"),
                    log.get("details")
                ])
        return file_path
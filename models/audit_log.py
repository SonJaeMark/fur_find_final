from datetime import datetime
from typing import Optional

class AuditLog:
    """Data model representing a recorded activity event in the audit trail."""

    def __init__(
        self,
        log_id: Optional[int],
        user_id: int,
        action: str,
        target_entity: str,
        target_id: Optional[int],
        details: str,
        ip_address: Optional[str] = "127.0.0.1",
        timestamp: Optional[datetime] = None
    ):
        self.log_id = log_id
        self.user_id = user_id
        self.action = action  # e.g., 'LOGIN', 'REPORT_CREATED', 'MATCH_APPROVED'
        self.target_entity = target_entity  # e.g., 'tbl_reports', 'tbl_users'
        self.target_id = target_id
        self.details = details
        self.ip_address = ip_address
        self.timestamp = timestamp or datetime.now()
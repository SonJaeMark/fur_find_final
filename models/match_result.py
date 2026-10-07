from datetime import datetime
from typing import Optional

class MatchResult:
    """Data model representing a calculated match between a lost and found report."""

    def __init__(
        self,
        match_id: Optional[int],
        lost_report_id: int,
        found_report_id: int,
        match_score: float,
        status: str = "Pending",  # 'Pending', 'Approved', 'Rejected'
        admin_notes: Optional[str] = "",
        created_at: Optional[datetime] = None
    ):
        self.match_id = match_id
        self.lost_report_id = lost_report_id
        self.found_report_id = found_report_id
        self.match_score = round(match_score, 2)
        self.status = status
        self.admin_notes = admin_notes
        self.created_at = created_at or datetime.now()
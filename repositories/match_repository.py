from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository

class MatchRepository(BaseRepository):
    """Data Access Object for tbl_matches."""

    def save_match(self, lost_report_id: int, found_report_id: int, match_score: float, status: str = "Pending") -> int:
        query = """
            INSERT INTO tbl_matches (lost_report_id, found_report_id, match_score, status)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (lost_report_id, found_report_id, match_score, status), commit=True)

    def get_match_by_id(self, match_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM tbl_matches WHERE match_id = %s"
        return self.execute_query(query, (match_id,), fetch_one=True)

    def get_pending_matches(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tbl_matches WHERE status = 'Pending' ORDER BY match_score DESC"
        return self.execute_query(query, fetch_all=True)

    def update_verification_status(self, match_id: int, status: str, admin_notes: Optional[str] = None) -> bool:
        query = "UPDATE tbl_matches SET status = %s, admin_notes = %s WHERE match_id = %s"
        self.execute_query(query, (status, admin_notes, match_id), commit=True)
        return True
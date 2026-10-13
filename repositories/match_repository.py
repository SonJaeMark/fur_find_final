from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository

class MatchRepository(BaseRepository):
    """Data Access Object for tbl_matches."""

    _DETAIL_SQL = """
        SELECT m.match_id, m.match_score, m.status, m.admin_notes, m.created_at,
               m.lost_report_id, m.found_report_id,
               l.pet_name AS lost_pet_name, l.species AS lost_species, l.breed AS lost_breed,
               l.primary_color AS lost_color, l.location AS lost_location,
               l.incident_date AS lost_date, l.photo_path AS lost_photo, l.user_id AS lost_user_id,
               lu.full_name AS lost_owner, lu.contact_no AS lost_contact,
               f.pet_name AS found_pet_name, f.species AS found_species, f.breed AS found_breed,
               f.primary_color AS found_color, f.location AS found_location,
               f.incident_date AS found_date, f.photo_path AS found_photo, f.user_id AS found_user_id,
               fu.full_name AS found_owner, fu.contact_no AS found_contact
        FROM tbl_matches m
        JOIN tbl_reports l ON l.report_id = m.lost_report_id
        JOIN tbl_reports f ON f.report_id = m.found_report_id
        JOIN tbl_users lu ON lu.user_id = l.user_id
        JOIN tbl_users fu ON fu.user_id = f.user_id
    """

    def get_matches_by_status(self, status: str) -> List[Dict[str, Any]]:
        q = "SELECT * FROM tbl_matches WHERE status = %s ORDER BY match_score DESC"
        return self.execute_query(q, (status,), fetch_all=True)

    def create_match_entry(self, lost_report_id: int, found_report_id: int, score: float,
                           status: str = "Pending Admin Verification") -> int:
        return self.save_match(lost_report_id, found_report_id, score, status)

    def update_match_status(self, match_id: int, status: str, notes: Optional[str] = None) -> bool:
        return self.update_verification_status(match_id, status, notes)

    def get_detailed_by_status(self, status: str) -> List[Dict[str, Any]]:
        q = self._DETAIL_SQL + " WHERE m.status = %s AND l.is_deleted = 0 AND f.is_deleted = 0 ORDER BY m.match_score DESC"
        return self.execute_query(q, (status,), fetch_all=True)

    def get_detailed_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        q = (self._DETAIL_SQL + " WHERE (l.user_id = %s OR f.user_id = %s)"
             " AND l.is_deleted = 0 AND f.is_deleted = 0 ORDER BY m.created_at DESC")
        return self.execute_query(q, (user_id, user_id), fetch_all=True)

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
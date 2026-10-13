from typing import List, Dict, Any
from repositories.base_repository import BaseRepository


class ClaimRepository(BaseRepository):
    """Data Access Object for tbl_claims (claim verification requests and disputes)."""

    def create_claim(self, match_id: int, user_id: int, claim_type: str, message: str) -> int:
        q = "INSERT INTO tbl_claims (match_id, user_id, claim_type, message) VALUES (%s, %s, %s, %s)"
        return self.execute_query(q, (match_id, user_id, claim_type, message), commit=True)

    def get_by_match(self, match_id: int) -> List[Dict[str, Any]]:
        q = """SELECT c.claim_id, c.claim_type, c.message, c.status, c.created_at,
                      u.full_name, u.contact_no
               FROM tbl_claims c JOIN tbl_users u ON u.user_id = c.user_id
               WHERE c.match_id = %s ORDER BY c.created_at"""
        return self.execute_query(q, (match_id,), fetch_all=True)
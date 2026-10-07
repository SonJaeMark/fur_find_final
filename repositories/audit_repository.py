from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository

class AuditRepository(BaseRepository):
    """Data Access Object for tbl_audit_log."""

    def log_activity(self, user_id: Optional[int], action: str, table_affected: str, details: Optional[str] = None) -> int:
        query = """
            INSERT INTO tbl_audit_log (user_id, action, table_affected, details)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (user_id, action, table_affected, details), commit=True)

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tbl_audit_log ORDER BY timestamp DESC LIMIT %s"
        return self.execute_query(query, (limit,), fetch_all=True)
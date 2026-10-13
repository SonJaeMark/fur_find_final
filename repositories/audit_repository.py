from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository

class AuditRepository(BaseRepository):
    """Data Access Object for tbl_audit_log."""

    def log_action(self, user_id: Optional[int], action: str, details: Optional[str] = None,
                   table_affected: str = "system") -> int:
        return self.log_activity(user_id, action, table_affected, details)

    def get_audit_logs(self, limit: int = 100, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        q = ("SELECT a.log_id, a.user_id, u.full_name, a.action, a.table_affected, a.details, a.timestamp "
             "FROM tbl_audit_log a LEFT JOIN tbl_users u ON u.user_id = a.user_id")
        params = []
        if user_id:
            q += " WHERE a.user_id = %s"
            params.append(user_id)
        q += " ORDER BY a.timestamp DESC, a.log_id DESC LIMIT %s"
        params.append(limit)
        return self.execute_query(q, tuple(params), fetch_all=True)

    def log_activity(self, user_id: Optional[int], action: str, table_affected: str, details: Optional[str] = None) -> int:
        query = """
            INSERT INTO tbl_audit_log (user_id, action, table_affected, details)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (user_id, action, table_affected, details), commit=True)

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tbl_audit_log ORDER BY timestamp DESC LIMIT %s"
        return self.execute_query(query, (limit,), fetch_all=True)
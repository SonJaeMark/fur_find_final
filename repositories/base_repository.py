from typing import Any, Dict, List, Optional
from core.db_manager import DatabaseManager
from core.exceptions import DatabaseError

class BaseRepository:
    """Base DAO class executing parameterized queries with DatabaseManager."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def execute_query(self, query: str, params: Optional[tuple] = None, fetch_one: bool = False, fetch_all: bool = False, commit: bool = False) -> Any:
        """Executes a parameterized SQL query safely against SQL injection."""
        try:
            with self.db.get_cursor(commit=commit) as cursor:
                cursor.execute(query, params or ())
                if fetch_one:
                    return cursor.fetchone()
                if fetch_all:
                    return cursor.fetchall()
                if commit:
                    return cursor.lastrowid
                return None
        except Exception as e:
            raise DatabaseError(f"Database query error: {str(e)}")
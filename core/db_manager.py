import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from config.init import load_db_config
from core.exceptions import DatabaseError


class DatabaseManager:
    """
    Singleton Database Manager class responsible for managing 
    MySQL connection lifecycles and context-managed cursors.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._config = load_db_config()
            cls._instance._connection = None
        return cls._instance

    def get_connection(self):
        """Retrieves or initializes an active MySQL connection."""
        try:
            if self._connection is None or not self._connection.is_connected():
                self._connection = mysql.connector.connect(**self._config)
            return self._connection
        except Error as e:
            raise DatabaseError(f"Failed to connect to MySQL database: {e}")

    @contextmanager
    def get_cursor(self, dictionary=True, commit=False):
        """
        Context manager to automatically manage cursor lifecycle and transactions.
        Usage:
            with db_manager.get_cursor(commit=True) as cursor:
                cursor.execute("SELECT * FROM tbl_users WHERE user_id = %s", (user_id,))
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Error as e:
            conn.rollback()
            raise DatabaseError(f"Database query execution failed: {e}")
        finally:
            cursor.close()

    def close(self):
        """Closes the active database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
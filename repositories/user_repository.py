from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository
from models.user import User, PetOwner, Admin, SuperAdmin


class UserRepository(BaseRepository):
    """Data Access Object for user table operations."""

    def _map_row_to_user(self, row: Dict[str, Any]) -> Optional[User]:
        """Factory mapper that constructs concrete User objects based on role_id."""
        if not row:
            return None
            
        role_id = row.get("role_id")
        user_kwargs = {
            "user_id": row.get("user_id"),
            "full_name": row.get("full_name"),
            "email": row.get("email"),
            "contact_no": row.get("contact_no"),
            "status": row.get("status", "Active"),
            "password_hash": row.get("password_hash"),
            "salt": row.get("salt")
        }

        if role_id == 1:
            return PetOwner(**user_kwargs)
        elif role_id == 2:
            return Admin(**user_kwargs)
        elif role_id == 3:
            return SuperAdmin(**user_kwargs)
        return None

    def create_user(self, user: User) -> int:
        """Inserts a new user record into the database."""
        query = """
            INSERT INTO tbl_users (full_name, email, contact_no, role_id, status, password_hash, salt)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user.full_name,
            user.email,
            user.contact_no,
            user.role_id,
            user.status,
            user.password_hash,
            user.salt
        )
        return self.execute_query(query, params, commit=True)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieves a single user by ID."""
        query = "SELECT * FROM tbl_users WHERE user_id = %s"
        row = self.execute_query(query, (user_id,), fetch_one=True)
        return self._map_row_to_user(row)

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a single user by email address."""
        query = "SELECT * FROM tbl_users WHERE email = %s"
        row = self.execute_query(query, (email,), fetch_one=True)
        return self._map_row_to_user(row)

    def update_profile(self, user_id: int, full_name: str, contact_no: str) -> bool:
        """Updates full name and contact number for a user."""
        query = "UPDATE tbl_users SET full_name = %s, contact_no = %s WHERE user_id = %s"
        self.execute_query(query, (full_name, contact_no, user_id), commit=True)
        return True

    def get_all_users(self) -> List[User]:
        """Retrieves all registered system users."""
        query = "SELECT * FROM tbl_users"
        rows = self.execute_query(query, fetch_all=True)
        return [self._map_row_to_user(r) for r in rows if r]
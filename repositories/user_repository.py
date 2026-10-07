from typing import Optional, Dict, Any, List
from repositories.base_repository import BaseRepository
from models.user import User, PetOwner, Admin, SuperAdmin

class UserRepository(BaseRepository):
    """Data Access Object for tbl_users."""

    def _map_row_to_user(self, row: Dict[str, Any]) -> Optional[User]:
        if not row:
            return None
        role_id = row.get("role_id")
        user_kwargs = {
            "user_id": row["user_id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "contact_no": row["contact_no"],
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
        query = "SELECT * FROM tbl_users WHERE user_id = %s"
        row = self.execute_query(query, (user_id,), fetch_one=True)
        return self._map_row_to_user(row)

    def get_by_email(self, email: str) -> Optional[User]:
        query = "SELECT * FROM tbl_users WHERE email = %s"
        row = self.execute_query(query, (email,), fetch_one=True)
        return self._map_row_to_user(row)

    def update_profile(self, user_id: int, full_name: str, contact_no: str) -> bool:
        query = """
            UPDATE tbl_users 
            SET full_name = %s, contact_no = %s 
            WHERE user_id = %s
        """
        self.execute_query(query, (full_name, contact_no, user_id), commit=True)
        return True

    def update_status(self, user_id: int, status: str) -> bool:
        query = "UPDATE tbl_users SET status = %s WHERE user_id = %s"
        self.execute_query(query, (status, user_id), commit=True)
        return True

    def get_all_users(self) -> List[User]:
        query = "SELECT * FROM tbl_users"
        rows = self.execute_query(query, fetch_all=True)
        return [self._map_row_to_user(row) for row in rows if row]
from abc import ABC, abstractmethod
import hashlib
import os

class User(ABC):
    """Abstract Base Class representing a user in the FurFind system."""

    def __init__(self, user_id: int, full_name: str, email: str, contact_no: str, role_id: int, status: str = "Active", password_hash: str = None, salt: str = None):
        self._user_id = user_id
        self._full_name = full_name
        self._email = email
        self._contact_no = contact_no
        self._role_id = role_id
        self._status = status
        self._password_hash = password_hash
        self._salt = salt

    # Encapsulation via Properties
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str):
        if not value or len(value.strip()) == 0:
            raise ValueError("Full name cannot be empty.")
        self._full_name = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        self._email = value

    @property
    def contact_no(self) -> str:
        return self._contact_no

    @contact_no.setter
    def contact_no(self, value: str):
        self._contact_no = value

    @property
    def role_id(self) -> int:
        return self._role_id

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        if value not in ["Active", "Suspended", "Inactive"]:
            raise ValueError("Invalid account status.")
        self._status = value

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def salt(self) -> str:
        return self._salt

    # Password Management & Hashing
    def set_password(self, plain_password: str):
        """Hashes and sets the user's password using SHA-256 with a unique salt."""
        salt_bytes = os.urandom(16)
        self._salt = salt_bytes.hex()
        self._password_hash = self._hash_password(plain_password, self._salt)

    def verify_password(self, plain_password: str) -> bool:
        """Verifies a plain text password against the stored hash and salt."""
        if not self._password_hash or not self._salt:
            return False
        return self._password_hash == self._hash_password(plain_password, self._salt)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

    @abstractmethod
    def get_role_name(self) -> str:
        """Polymorphic method returning the user role name."""
        pass


class PetOwner(User):
    def __init__(self, user_id: int, full_name: str, email: str, contact_no: str, status: str = "Active", password_hash: str = None, salt: str = None):
        super().__init__(user_id, full_name, email, contact_no, role_id=1, status=status, password_hash=password_hash, salt=salt)

    def get_role_name(self) -> str:
        return "Pet Owner"


class Admin(User):
    def __init__(self, user_id: int, full_name: str, email: str, contact_no: str, status: str = "Active", password_hash: str = None, salt: str = None):
        super().__init__(user_id, full_name, email, contact_no, role_id=2, status=status, password_hash=password_hash, salt=salt)

    def get_role_name(self) -> str:
        return "Admin"


class SuperAdmin(User):
    def __init__(self, user_id: int, full_name: str, email: str, contact_no: str, status: str = "Active", password_hash: str = None, salt: str = None):
        super().__init__(user_id, full_name, email, contact_no, role_id=3, status=status, password_hash=password_hash, salt=salt)

    def get_role_name(self) -> str:
        return "Super Admin"
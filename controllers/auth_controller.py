import re
from models.user import User, PetOwner, Admin, SuperAdmin
from repositories.user_repository import UserRepository
from repositories.audit_repository import AuditRepository
# Change this import line in controllers/auth_controller.py
from core.exceptions import AuthenticationError, ValidationError, AuthError, DatabaseError


class AuthController:
    """Handles authentication, session tracking, registration, and security authorization."""

    def __init__(self, user_repo: UserRepository = None, audit_repo: AuditRepository = None):
        self.user_repo = user_repo or UserRepository()
        self.audit_repo = audit_repo or AuditRepository()
        self.current_user: User | None = None

    def login(self, email_or_username: str, password: str) -> User:
        """Authenticate user credentials and set current session user."""
        if not email_or_username or not password:
            raise ValidationError("Email/Username and Password are required.")

        user = self.user_repo.get_by_email_or_username(email_or_username.strip())
        if not user:
            raise AuthError("Invalid login credentials.")

        if not user.verify_password(password):
            raise AuthError("Invalid login credentials.")

        if hasattr(user, "is_active") and not user.is_active:
            raise AuthError("Account is deactivated. Please contact support.")

        self.current_user = user
        self.audit_repo.log_action(
            user_id=user.user_id,
            action="LOGIN",
            details=f"User {user.email} logged in successfully."
        )
        return user

    def register_pet_owner(self, full_name: str, email: str, contact_no: str, password: str, confirm_pass: str) -> PetOwner:
        """Register a new Pet Owner / Finder standard user."""
        if password != confirm_pass:
            raise ValidationError("Passwords do not match.")

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            raise ValidationError("Invalid email format.")

        existing = self.user_repo.get_by_email_or_username(email)
        if existing:
            raise ValidationError("An account with this email already exists.")

        new_user = PetOwner(
            user_id=None,
            full_name=full_name.strip(),
            email=email.strip().lower(),
            contact_no=contact_no.strip()
        )
        new_user.set_password(password)

        created_user = self.user_repo.create_user(new_user, role_name="Pet Owner")
        self.audit_repo.log_action(
            user_id=created_user.user_id,
            action="REGISTER",
            details=f"New Pet Owner account created: {created_user.email}"
        )
        return created_user

    def logout(self) -> None:
        """Clear session and log user logout."""
        if self.current_user:
            self.audit_repo.log_action(
                user_id=self.current_user.user_id,
                action="LOGOUT",
                details=f"User {self.current_user.email} logged out."
            )
            self.current_user = None

    def require_role(self, allowed_roles: list[str]) -> None:
        """Enforce role checking for protected endpoints/views."""
        if not self.current_user:
            raise AuthError("Active user session required.")
        if self.current_user.get_role_name() not in allowed_roles:
            raise AuthError("Unauthorized access attempt.")
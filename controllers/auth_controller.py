from models.user import User, PetOwner
from repositories.user_repository import UserRepository
from repositories.audit_repository import AuditRepository
from utils.validator import Validator
from core.exceptions import ValidationError, AuthError


class AuthController:
    """Handles authentication, session tracking, registration, and security authorization."""

    def __init__(self, user_repo: UserRepository = None, audit_repo: AuditRepository = None):
        self.user_repo = user_repo or UserRepository()
        self.audit_repo = audit_repo or AuditRepository()
        self.current_user: User | None = None

    def login(self, email_or_username: str, password: str) -> User:
        if not email_or_username or not password:
            raise ValidationError("Email and Password are required.")

        user = self.user_repo.get_by_email_or_username(email_or_username.strip())
        if not user or not user.verify_password(password):
            raise AuthError("Invalid login credentials.")
        if user.status != "Active":
            raise AuthError("Account is locked or inactive. Please contact an administrator.")

        self.current_user = user
        self.audit_repo.log_action(user_id=user.user_id, action="LOGIN",
                                   details=f"User {user.email} logged in successfully.")
        return user

    def register_pet_owner(self, full_name: str, email: str, contact_no: str,
                           password: str, confirm_pass: str) -> PetOwner:
        full_name = Validator.validate_non_empty(full_name, "Full name")
        email = Validator.validate_email(email).lower()
        contact_no = Validator.validate_contact_no(contact_no)
        if len(password or "") < 8:
            raise ValidationError("Password must be at least 8 characters.")
        if password != confirm_pass:
            raise ValidationError("Passwords do not match.")
        if self.user_repo.get_by_email_or_username(email):
            raise ValidationError("An account with this email already exists.")

        new_user = PetOwner(user_id=None, full_name=full_name, email=email, contact_no=contact_no)
        new_user.set_password(password)

        new_id = self.user_repo.create_user(new_user)
        created = self.user_repo.get_by_id(new_id)
        self.audit_repo.log_action(user_id=new_id, action="REGISTER",
                                   details=f"New Pet Owner account created: {email}")
        return created

    def logout(self) -> None:
        if self.current_user:
            self.audit_repo.log_action(user_id=self.current_user.user_id, action="LOGOUT",
                                       details=f"User {self.current_user.email} logged out.")
            self.current_user = None

    def require_role(self, allowed_roles: list[str]) -> None:
        if not self.current_user:
            raise AuthError("Active user session required.")
        if self.current_user.get_role_name() not in allowed_roles:
            raise AuthError("Unauthorized access attempt.")
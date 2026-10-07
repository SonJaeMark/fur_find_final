from repositories.user_repository import UserRepository
from repositories.audit_repository import AuditRepository
from core.exceptions import ValidationError


class UserController:
    """Handles Super Admin privilege operations for user administration."""

    def __init__(self, user_repo: UserRepository = None, audit_repo: AuditRepository = None):
        self.user_repo = user_repo or UserRepository()
        self.audit_repo = audit_repo or AuditRepository()

    def set_user_active_status(self, super_admin_id: int, target_user_id: int, is_active: bool) -> bool:
        """Activate or deactivate a user account."""
        if super_admin_id == target_user_id and not is_active:
            raise ValidationError("Super Admin cannot deactivate their own account.")

        success = self.user_repo.update_user_status(target_user_id, is_active)
        status_str = "Activated" if is_active else "Deactivated"

        self.audit_repo.log_action(
            user_id=super_admin_id,
            action="USER_STATUS_CHANGE",
            details=f"Super Admin ID {super_admin_id} set user {target_user_id} status to {status_str}."
        )
        return success

    def assign_user_role(self, super_admin_id: int, target_user_id: int, new_role_name: str) -> bool:
        """Assign role (Pet Owner, Admin, Super Admin) to targeted user."""
        allowed_roles = ["Pet Owner", "Admin", "Super Admin"]
        if new_role_name not in allowed_roles:
            raise ValidationError(f"Invalid role name. Must be one of {allowed_roles}")

        success = self.user_repo.update_user_role(target_user_id, new_role_name)
        self.audit_repo.log_action(
            user_id=super_admin_id,
            action="USER_ROLE_ASSIGN",
            details=f"Super Admin ID {super_admin_id} updated user {target_user_id} role to {new_role_name}."
        )
        return success
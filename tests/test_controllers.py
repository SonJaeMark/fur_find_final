import pytest
from unittest.mock import MagicMock
from datetime import datetime
from controllers.auth_controller import AuthController
from controllers.report_controller import ReportController
from controllers.match_controller import MatchController
from controllers.user_controller import UserController
from models.user import PetOwner
from core.exceptions import ValidationError, AuthenticationError


def test_auth_controller_login_success():
    mock_user_repo = MagicMock()
    mock_audit_repo = MagicMock()

    user = PetOwner(user_id=1, full_name="Jane Doe", email="jane@test.com", contact_no="09170000000")
    user.set_password("CorrectPassword123")
    mock_user_repo.get_by_email_or_username.return_value = user

    controller = AuthController(user_repo=mock_user_repo, audit_repo=mock_audit_repo)
    logged_in_user = controller.login("jane@test.com", "CorrectPassword123")

    assert logged_in_user.email == "jane@test.com"
    assert controller.current_user == user
    mock_audit_repo.log_action.assert_called_once()


def test_auth_controller_login_failure():
    mock_user_repo = MagicMock()
    mock_audit_repo = MagicMock()

    user = PetOwner(user_id=1, full_name="Jane Doe", email="jane@test.com", contact_no="09170000000")
    user.set_password("CorrectPassword123")
    mock_user_repo.get_by_email_or_username.return_value = user

    controller = AuthController(user_repo=mock_user_repo, audit_repo=mock_audit_repo)

    with pytest.raises(AuthenticationError):
        controller.login("jane@test.com", "WrongPassword")


def test_submit_report_missing_photo_raises_error():
    controller = ReportController(
        report_repo=MagicMock(),
        match_repo=MagicMock(),
        audit_repo=MagicMock()
    )

    with pytest.raises(ValidationError):
        controller.submit_report(
            user_id=1, category="Lost", pet_name="Buddy", species="Dog",
            breed="Retriever", gender="Male", primary_color="Golden",
            secondary_color="", distinguishing_marks="",
            incident_date=datetime.now(), location="Manila",
            photo_path="non_existent_file.png"
        )


def test_match_controller_approve():
    mock_match_repo = MagicMock()
    mock_report_repo = MagicMock()
    mock_audit_repo = MagicMock()

    mock_match_repo.get_match_by_id.return_value = {
        "match_id": 1, "lost_report_id": 10, "found_report_id": 20
    }

    controller = MatchController(
        match_repo=mock_match_repo,
        report_repo=mock_report_repo,
        audit_repo=mock_audit_repo
    )

    result = controller.approve_match(match_id=1, admin_user_id=99, notes="Verified")
    assert result is True
    mock_match_repo.update_match_status.assert_called_with(1, status="Approved", notes="Verified")
    mock_report_repo.update_report_status.assert_any_call(10, status="Resolved")
    mock_report_repo.update_report_status.assert_any_call(20, status="Resolved")


def test_user_controller_cannot_deactivate_self():
    controller = UserController(user_repo=MagicMock(), audit_repo=MagicMock())
    with pytest.raises(ValidationError):
        controller.set_user_active_status(super_admin_id=1, target_user_id=1, is_active=False)
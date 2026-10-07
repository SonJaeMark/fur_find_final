import unittest
from unittest.mock import MagicMock, patch
from repositories.user_repository import UserRepository
from repositories.report_repository import ReportRepository
from repositories.match_repository import MatchRepository
from repositories.audit_repository import AuditRepository
from models.user import PetOwner
from core.exceptions import DatabaseError


class TestRepositories(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_db.get_cursor.return_value.__enter__.return_value = self.mock_cursor

    # ------------------ UserRepository Tests ------------------
    def test_create_user_success(self):
        user_repo = UserRepository(db_manager=self.mock_db)
        self.mock_cursor.lastrowid = 1
        
        user = PetOwner(user_id=0, full_name="Jane Doe", email="jane@example.com", contact_no="09171234567")
        user.set_password("SecurePass123!")
        
        new_id = user_repo.create_user(user)
        self.assertEqual(new_id, 1)
        self.mock_cursor.execute.assert_called_once()

    def test_get_user_by_email_found(self):
        user_repo = UserRepository(db_manager=self.mock_db)
        self.mock_cursor.fetchone.return_value = {
            "user_id": 1,
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "contact_no": "09171234567",
            "role_id": 1,
            "status": "Active",
            "password_hash": "hash",
            "salt": "salt"
        }
        
        user = user_repo.get_by_email("jane@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "jane@example.com")
        self.assertEqual(user.get_role_name(), "Pet Owner")

    # ------------------ ReportRepository Tests ------------------
    def test_create_report_success(self):
        report_repo = ReportRepository(db_manager=self.mock_db)
        self.mock_cursor.lastrowid = 10

        report_data = {
            "user_id": 1,
            "report_type": "Lost",
            "pet_name": "Buddy",
            "species": "Dog",
            "incident_date": "2026-10-01",
            "location": "Manila",
            "photo_path": "uploads/buddy.jpg"
        }
        report_id = report_repo.create_report(report_data)
        self.assertEqual(report_id, 10)

    def test_repository_database_error_handling(self):
        user_repo = UserRepository(db_manager=self.mock_db)
        self.mock_cursor.execute.side_effect = Exception("Connection lost")

        with self.assertRaises(DatabaseError):
            user_repo.get_by_id(1)

    # ------------------ MatchRepository Tests ------------------
    def test_save_match_and_update_status(self):
        match_repo = MatchRepository(db_manager=self.mock_db)
        self.mock_cursor.lastrowid = 5

        match_id = match_repo.save_match(lost_report_id=1, found_report_id=2, match_score=85.5)
        self.assertEqual(match_id, 5)

        success = match_repo.update_verification_status(match_id=5, status="Approved", admin_notes="Confirmed owner")
        self.assertTrue(success)

    # ------------------ AuditRepository Tests ------------------
    def test_log_activity(self):
        audit_repo = AuditRepository(db_manager=self.mock_db)
        self.mock_cursor.lastrowid = 100

        log_id = audit_repo.log_activity(user_id=1, action="LOGIN", table_affected="tbl_users", details="Successful login")
        self.assertEqual(log_id, 100)


if __name__ == "__main__":
    unittest.main()
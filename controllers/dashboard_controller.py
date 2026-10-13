import csv
from repositories.report_repository import ReportRepository
from repositories.match_repository import MatchRepository
from repositories.user_repository import UserRepository


class DashboardController:
    """Builds role-specific dashboard statistics and exports them."""

    def __init__(self, report_repo=None, match_repo=None, user_repo=None):
        self.report_repo = report_repo or ReportRepository()
        self.match_repo = match_repo or MatchRepository()
        self.user_repo = user_repo or UserRepository()

    def get_stats(self, user) -> dict:
        role = user.get_role_name()
        reports = self.report_repo.search_reports()
        if role == "Pet Owner":
            mine = [r for r in reports if r["user_id"] == user.user_id]
            return {
                "My Reports": len(mine),
                "My Active Cases": sum(r["status"] == "Active" for r in mine),
                "My Resolved Cases": sum(r["status"] == "Resolved" for r in mine),
                "Potential Matches": len(self.match_repo.get_detailed_for_user(user.user_id)),
                "Lost Pets (All)": sum(r["report_type"] == "Lost" and r["status"] == "Active" for r in reports),
                "Found Pets (All)": sum(r["report_type"] == "Found" and r["status"] == "Active" for r in reports),
            }
        stats = {
            "Total Reports": len(reports),
            "Active Lost": sum(r["report_type"] == "Lost" and r["status"] == "Active" for r in reports),
            "Active Found": sum(r["report_type"] == "Found" and r["status"] == "Active" for r in reports),
            "Resolved Cases": sum(r["status"] == "Resolved" for r in reports),
            "Pending Matches": len(self.match_repo.get_matches_by_status("Pending Admin Verification")),
            "Approved Matches": len(self.match_repo.get_matches_by_status("Approved")),
        }
        if role == "Super Admin":
            users = self.user_repo.get_all_users()
            stats["Total Users"] = len(users)
            stats["Locked Accounts"] = sum(u.status != "Active" for u in users)
        return stats

    def export_stats_csv(self, user, file_path: str) -> str:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Metric", "Value"])
            for k, v in self.get_stats(user).items():
                w.writerow([k, v])
        return file_path
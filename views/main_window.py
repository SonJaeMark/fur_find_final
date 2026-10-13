import tkinter as tk
from views.components.navbar import NavBar
from views.dashboard_view import DashboardView
from views.report_form_view import ReportFormView
from views.search_view import SearchView
from views.my_reports_view import MyReportsView
from views.profile_view import ProfileView
from views.match_queue_view import MatchQueueView
from views.pet_mgmt_view import PetMgmtView
from views.audit_logs_view import AuditLogsView
from views.user_mgmt_view import UserManagementView

OWNER, ADMIN, SUPER = "Pet Owner", "Admin", "Super Admin"
# view_key -> roles allowed (defense in depth; the NavBar already hides links per role)
ACCESS = {
    "dashboard": {OWNER, ADMIN, SUPER}, "search": {OWNER, ADMIN, SUPER},
    "report_pet": {OWNER}, "my_reports": {OWNER}, "profile": {OWNER},
    "match_queue": {ADMIN, SUPER}, "pet_mgmt": {ADMIN, SUPER}, "audit_logs": {ADMIN, SUPER},
    "user_mgmt": {SUPER},
}


class MainWindow(tk.Frame):
    """Main Application Shell hosting navigation and body views."""

    def __init__(self, parent, user_session, on_logout):
        super().__init__(parent, bg="#F4F4F5")
        self.pack(fill="both", expand=True)
        self.user = user_session
        self.on_logout_callback = on_logout

        self.navbar = NavBar(self, user_role=self.user.get_role_name(),
                             on_nav_click=self.navigate_to, on_logout=self.on_logout_callback)
        self.navbar.pack(side="top", fill="x")

        self.content_container = tk.Frame(self, bg="#F4F4F5")
        self.content_container.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        self.navigate_to("dashboard")

    def navigate_to(self, view_key: str):
        role = self.user.get_role_name()
        if role not in ACCESS.get(view_key, set()):
            view_key = "dashboard"

        for widget in self.content_container.winfo_children():
            widget.destroy()

        c, u = self.content_container, self.user
        routes = {
            "dashboard": lambda: DashboardView(c, u),
            "search": lambda: SearchView(c, u),
            "report_pet": lambda: ReportFormView(c, u, on_done=lambda: self.navigate_to("my_reports")),
            "my_reports": lambda: MyReportsView(c, u),
            "profile": lambda: ProfileView(c, u),
            "match_queue": lambda: MatchQueueView(c, u),
            "pet_mgmt": lambda: PetMgmtView(c, u),
            "audit_logs": lambda: AuditLogsView(c, u),
            "user_mgmt": lambda: UserManagementView(c, u),
        }
        routes[view_key]()
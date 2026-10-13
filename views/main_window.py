import tkinter as tk
from views.components.navbar import NavBar


class MainWindow(tk.Frame):
    """Main Application Shell hosting navigation and body views."""

    def __init__(self, parent, user_session, on_logout):
        super().__init__(parent, bg="#F4F4F5")
        self.pack(fill="both", expand=True)

        self.user = user_session
        self.on_logout_callback = on_logout

        # Top Dynamic Navigation Bar
        self.navbar = NavBar(
            self,
            user_role=self.user.get_role_name(),
            on_nav_click=self.navigate_to,
            on_logout=self.on_logout_callback
        )
        self.navbar.pack(side="top", fill="x")

        # Main Body Frame
        self.content_container = tk.Frame(self, bg="#F4F4F5")
        self.content_container.pack(side="top", fill="both", expand=True, padx=20, pady=20)

        # Default View Route
        self.navigate_to("dashboard")

    def navigate_to(self, view_key: str):
        """Swaps content views dynamically."""
        for widget in self.content_container.winfo_children():
            widget.destroy()

        if view_key == "dashboard":
            self._render_dashboard()
        elif view_key == "match_queue":
            self._render_placeholder_card("Match Verification Queue", "Admin verification and claim workflows.")
        elif view_key == "user_mgmt":
            self._render_placeholder_card("User Management Interface", "Super Admin role assignment & account status control.")
        elif view_key == "audit_logs":
            self._render_placeholder_card("System Audit Logs", "Full history of user actions and administrative decisions.")
        else:
            self._render_placeholder_card(f"View: {view_key.capitalize()}", f"Workspace for {view_key}")

    def _render_dashboard(self):
        """Renders role-specific summary view."""
        card = tk.Frame(self.content_container, bg="#FFFFFF", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_welcome = tk.Label(
            card,
            text=f"Welcome, {self.user.full_name}!",
            font=("Segoe UI", 16, "bold"),
            fg="#111827",
            bg="#FFFFFF"
        )
        lbl_welcome.pack(anchor="w", padx=24, pady=(24, 4))

        lbl_sub = tk.Label(
            card,
            text=f"Logged in as: {self.user.get_role_name()} ({self.user.email})",
            font=("Segoe UI", 10),
            fg="#A1A1AA",
            bg="#FFFFFF"
        )
        lbl_sub.pack(anchor="w", padx=24, pady=(0, 20))

    def _render_placeholder_card(self, title: str, description: str):
        card = tk.Frame(self.content_container, bg="#FFFFFF", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), fg="#111827", bg="#FFFFFF")
        lbl_title.pack(anchor="w", padx=24, pady=(24, 4))

        lbl_desc = tk.Label(card, text=description, font=("Segoe UI", 10), fg="#A1A1AA", bg="#FFFFFF")
        lbl_desc.pack(anchor="w", padx=24, pady=(0, 20))
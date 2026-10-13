import tkinter as tk


class NavBar(tk.Frame):
    """Dynamic top navigation bar styled according to FurFind design tokens and user role."""
    
    def __init__(self, parent, user_role="Pet Owner", on_nav_click=None, on_logout=None):
        super().__init__(parent, bg="#18181B", height=56)
        self.pack_propagate(False)
        self.user_role = user_role
        self.on_nav_click = on_nav_click
        self.on_logout = on_logout

        self._build_ui()

    def _build_ui(self):
        # 1. Branding / Logo
        logo_frame = tk.Frame(self, bg="#18181B")
        logo_frame.pack(side="left", padx=16)

        lbl_logo = tk.Label(
            logo_frame, 
            text="🐾 FurFind", 
            font=("Segoe UI", 12, "bold"), 
            fg="#FFFFFF", 
            bg="#18181B"
        )
        lbl_logo.pack(side="left")

        # 2. Dynamic Nav Links based on Role
        links_frame = tk.Frame(self, bg="#18181B")
        links_frame.pack(side="left", padx=20)

        nav_items = [("Dashboard", "dashboard"), ("Unified Search", "search")]

        if self.user_role in ["Pet Owner", "Finder"]:
            nav_items.insert(1, ("Report Pet", "report_pet"))
            nav_items.append(("My Reports", "my_reports"))
            nav_items.append(("Profile", "profile"))

        elif self.user_role == "Admin":
            nav_items.append(("Match Verification", "match_queue"))
            nav_items.append(("Pet Management", "pet_mgmt"))
            nav_items.append(("Audit Log", "audit_logs"))

        elif self.user_role == "Super Admin":
            nav_items.append(("Match Verification", "match_queue"))
            nav_items.append(("Pet Management", "pet_mgmt"))
            nav_items.append(("User Management", "user_mgmt"))
            nav_items.append(("Audit Logs", "audit_logs"))

        # Render Navigation Buttons
        for label, view_key in nav_items:
            btn = tk.Button(
                links_frame,
                text=label,
                font=("Segoe UI", 9, "bold"),
                fg="#A1A1AA",
                bg="#18181B",
                activeforeground="#FFFFFF",
                activebackground="#18181B",
                bd=0,
                cursor="hand2",
                command=lambda vk=view_key: self._handle_click(vk)
            )
            btn.pack(side="left", padx=10, pady=14)

        # 3. User Info & Logout Button
        user_frame = tk.Frame(self, bg="#18181B")
        user_frame.pack(side="right", padx=16)

        lbl_role = tk.Label(
            user_frame,
            text=f"Role: {self.user_role}",
            font=("Segoe UI", 8),
            fg="#A1A1AA",
            bg="#18181B"
        )
        lbl_role.pack(side="left", padx=(0, 12))

        btn_logout = tk.Button(
            user_frame,
            text="Logout",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg="#27272A",
            activeforeground="#FFFFFF",
            activebackground="#3F3F46",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.on_logout
        )
        btn_logout.pack(side="left")

    def _handle_click(self, view_key):
        if self.on_nav_click:
            self.on_nav_click(view_key)
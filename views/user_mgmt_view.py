import tkinter as tk
from tkinter import messagebox
from controllers.user_controller import UserController
from views.components.ui_kit import BG, CARD, MUTED, FONT, card, page_header, button, guard, DataTable, FormDialog

ROLES = ["Pet Owner", "Admin", "Super Admin"]


class UserManagementView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.me, self.ctrl, self.users = user, UserController(), {}
        page_header(self, "User Management", "Create and edit accounts, assign roles, and lock or unlock access.")

        box = card(self)
        box.pack(fill="both", expand=True)
        self.table = DataTable(box, [("user_id", "ID", 50), ("full_name", "Name", 170), ("email", "Email", 210),
                                     ("contact_no", "Contact", 110), ("role", "Role", 100), ("state", "Status", 80)],
                               height=12)
        self.table.pack(fill="both", expand=True, padx=16, pady=(12, 8))

        bar = tk.Frame(box, bg=CARD)
        bar.pack(fill="x", padx=16, pady=(0, 14))
        button(bar, "Create Account", self.create).pack(side="left", padx=(0, 6))
        button(bar, "Edit", self.edit, "secondary").pack(side="left", padx=6)
        button(bar, "Change Role", self.change_role, "secondary").pack(side="left", padx=6)
        button(bar, "Lock / Unlock", self.toggle, "danger").pack(side="left", padx=6)
        button(bar, "Refresh", self.refresh, "secondary").pack(side="right")
        self.refresh()

    @guard
    def refresh(self):
        users = self.ctrl.list_users()
        self.users = {u.user_id: u for u in users}
        self.table.load([{"user_id": u.user_id, "full_name": u.full_name, "email": u.email,
                          "contact_no": u.contact_no, "role": u.get_role_name(),
                          "state": "Active" if u.status == "Active" else "Locked"} for u in users], "user_id")

    def _target(self):
        uid = self.table.selected_id()
        if uid is None:
            messagebox.showinfo("FurFind", "Select a user first.")
            return None
        return self.users[uid]

    def create(self):
        fields = [{"key": "full_name", "label": "Full name"}, {"key": "email", "label": "Email"},
                  {"key": "contact_no", "label": "Contact number"},
                  {"key": "password", "label": "Password (min 8 chars)", "type": "password"},
                  {"key": "role", "label": "Role", "type": "combo", "values": ["Admin", "Super Admin", "Pet Owner"]}]

        def submit(d):
            self.ctrl.create_account(self.me.user_id, d["full_name"], d["email"], d["contact_no"],
                                     d["password"], d["role"])
            self.refresh()
        FormDialog(self, "Create Account", fields, submit, submit_text="Create")

    def edit(self):
        t = self._target()
        if not t:
            return
        fields = [{"key": "full_name", "label": "Full name"}, {"key": "contact_no", "label": "Contact number"}]

        def submit(d):
            self.ctrl.update_profile(self.me.user_id, t.user_id, d["full_name"], d["contact_no"])
            self.refresh()
        FormDialog(self, f"Edit {t.email}", fields, submit,
                   initial={"full_name": t.full_name, "contact_no": t.contact_no})

    def change_role(self):
        t = self._target()
        if not t:
            return
        if t.user_id == self.me.user_id:
            messagebox.showwarning("FurFind", "You cannot change your own role.")
            return

        def submit(d):
            self.ctrl.assign_user_role(self.me.user_id, t.user_id, d["role"])
            self.refresh()
        FormDialog(self, f"Change Role: {t.email}",
                   [{"key": "role", "label": "New role", "type": "combo", "values": ROLES}], submit,
                   initial={"role": t.get_role_name()})

    @guard
    def toggle(self):
        t = self._target()
        if not t:
            return
        unlock = t.status != "Active"
        if messagebox.askyesno("Confirm", f"{'Unlock' if unlock else 'Lock'} account {t.email}?"):
            self.ctrl.set_user_active_status(self.me.user_id, t.user_id, unlock)
            self.refresh()
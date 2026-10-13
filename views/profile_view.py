import tkinter as tk
from tkinter import messagebox
from controllers.user_controller import UserController
from views.components.ui_kit import BG, CARD, TEXT, MUTED, FONT, card, page_header, button, guard


class ProfileView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.user, self.ctrl = user, UserController()
        page_header(self, "My Profile", "Update your name and contact number.")

        box = card(self)
        box.pack(fill="x")
        form = tk.Frame(box, bg=CARD)
        form.pack(padx=24, pady=20, anchor="w")

        def row(label, value, editable=True):
            tk.Label(form, text=label, font=(FONT, 9, "bold"), bg=CARD, fg=TEXT).pack(anchor="w", pady=(8, 2))
            e = tk.Entry(form, width=44, font=(FONT, 10), relief="solid", bd=1)
            e.insert(0, value or "")
            if not editable:
                e.config(state="disabled")
            e.pack(ipady=3)
            return e

        self.name = row("Full name", user.full_name)
        self.contact = row("Contact number", user.contact_no)
        row("Email", user.email, False)
        row("Role", user.get_role_name(), False)
        button(form, "Save Changes", self._save).pack(anchor="w", pady=16)

    @guard
    def _save(self):
        uid = self.user.user_id
        self.ctrl.update_profile(uid, uid, self.name.get(), self.contact.get())
        fresh = self.ctrl.user_repo.get_by_id(uid)
        self.user.full_name, self.user.contact_no = fresh.full_name, fresh.contact_no
        messagebox.showinfo("FurFind", "Profile updated.")
import tkinter as tk
from tkinter import messagebox
from controllers.auth_controller import AuthController
from core.exceptions import FurFindException
from views.login_and_register_view import LoginAndRegisterView
from views.main_window import MainWindow
from views.components.ui_kit import apply_styles


class FurFindApp(tk.Tk):
    """Main Application Controller."""

    def __init__(self):
        super().__init__()
        self.title("FurFind - Pet Search & Recovery System")
        self.geometry("1000x720")
        self.minsize(850, 650)
        self.configure(bg="#F4F4F5")
        apply_styles()

        self.auth = AuthController()
        self.auth_view = None
        self.main_window = None
        self.show_login()

    def show_login(self):
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
        self.auth_view = LoginAndRegisterView(self)
        self.auth_view.on_login = self._handle_login
        self.auth_view.on_register = self._handle_register

    def _handle_login(self):
        try:
            user = self.auth.login(self.auth_view.login_user_entry.get(),
                                   self.auth_view.login_pass_entry.get())
        except FurFindException as e:
            messagebox.showerror("Login Failed", e.message)
            return
        self.auth_view.destroy()
        self.auth_view = None
        self.main_window = MainWindow(self, user, on_logout=self._handle_logout)

    def _handle_register(self):
        e = self.auth_view.reg_entries
        try:
            self.auth.register_pet_owner(
                full_name=e["Full Name *"].get(), email=e["Email Address *"].get(),
                contact_no=e["Contact Number *"].get(), password=e["Password *"].get(),
                confirm_pass=e["Confirm Password *"].get())
        except FurFindException as ex:
            messagebox.showerror("Registration Failed", ex.message)
            return
        messagebox.showinfo("FurFind", "Account created. You can now log in.")
        self.auth_view.switch_tab("login")

    def _handle_logout(self):
        self.auth.logout()
        self.show_login()


if __name__ == "__main__":
    FurFindApp().mainloop()
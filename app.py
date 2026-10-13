import tkinter as tk
from views.login_and_register_view import LoginAndRegisterView


class FurFindApp(tk.Tk):
    """Main Application Controller."""

    def __init__(self):
        super().__init__()
        self.title("FurFind - Pet Search & Recovery System")
        self.geometry("1000x720")
        self.minsize(850, 650)
        self.configure(bg="#F4F4F5")

        # Load Auth View
        self.auth_view = LoginAndRegisterView(self)
        
        # Wire action hooks
        self.auth_view.on_login = self._handle_login
        self.auth_view.on_register = self._handle_register

    def _handle_login(self):
        username = self.auth_view.login_user_entry.get()
        password = self.auth_view.login_pass_entry.get()
        print(f"[App Controller] Login Attempt -> Username/Email: '{username}', Password: '{password}'")

    def _handle_register(self):
        data = {k: v.get() for k, v in self.auth_view.reg_entries.items()}
        data["Role"] = self.auth_view.role_var.get()
        print(f"[App Controller] Register Attempt -> Data: {data}")


if __name__ == "__main__":
    app = FurFindApp()
    app.mainloop()
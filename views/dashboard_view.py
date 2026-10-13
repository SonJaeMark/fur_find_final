import tkinter as tk
from tkinter import filedialog, messagebox
from controllers.dashboard_controller import DashboardController
from views.components.ui_kit import BG, page_header, button, stat_card, guard


class DashboardView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.user, self.ctrl = user, DashboardController()
        role = user.get_role_name()
        page_header(self, f"Welcome, {user.full_name}!", f"{role} · {user.email}")

        if role in ("Admin", "Super Admin"):
            bar = tk.Frame(self, bg=BG)
            bar.pack(fill="x", pady=(0, 8))
            button(bar, "Export Statistics (CSV)", self.export).pack(side="left")
            button(bar, "Refresh", self.refresh, "secondary").pack(side="left", padx=8)

        self.grid_frame = tk.Frame(self, bg=BG)
        self.grid_frame.pack(fill="x")
        for c in range(3):
            self.grid_frame.columnconfigure(c, weight=1, uniform="s")
        self.refresh()

    @guard
    def refresh(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        for i, (label, value) in enumerate(self.ctrl.get_stats(self.user).items()):
            stat_card(self.grid_frame, label, value).grid(row=i // 3, column=i % 3, sticky="ew", padx=6, pady=6)

    @guard
    def export(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="dashboard_stats.csv",
                                            filetypes=[("CSV", "*.csv")])
        if path:
            self.ctrl.export_stats_csv(self.user, path)
            messagebox.showinfo("FurFind", "Dashboard statistics exported.")
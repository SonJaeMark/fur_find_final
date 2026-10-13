import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from controllers.audit_controller import AuditController
from utils.pdf_exporter import PDFExporter
from views.components.ui_kit import BG, CARD, FONT, card, page_header, button, guard, DataTable


class AuditLogsView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.ctrl, self.logs = AuditController(), []
        page_header(self, "System Audit Logs", "Full history of user actions and administrative decisions.")

        box = card(self)
        box.pack(fill="both", expand=True)
        bar = tk.Frame(box, bg=CARD)
        bar.pack(fill="x", padx=16, pady=12)
        tk.Label(bar, text="Show last", font=(FONT, 9, "bold"), bg=CARD).pack(side="left")
        self.limit = ttk.Combobox(bar, values=["100", "250", "500", "1000"], state="readonly", width=6)
        self.limit.set("100")
        self.limit.pack(side="left", padx=6)
        self.limit.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        button(bar, "Refresh", self.refresh, "secondary").pack(side="left", padx=4)
        button(bar, "Export CSV", self.export_csv).pack(side="right", padx=4)
        button(bar, "Export PDF", self.export_pdf).pack(side="right", padx=4)

        self.table = DataTable(box, [("log_id", "ID", 55), ("ts", "Timestamp", 140), ("who", "User", 160),
                                     ("action", "Action", 170), ("details", "Details", 420)], height=14)
        self.table.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.refresh()

    @guard
    def refresh(self):
        self.logs = self.ctrl.fetch_logs(limit=int(self.limit.get()))
        self.table.load([{**l, "ts": str(l["timestamp"]),
                          "who": f"{l['full_name']} (#{l['user_id']})" if l.get("user_id") else "System"}
                         for l in self.logs], "log_id")

    @guard
    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="audit_logs.csv",
                                            filetypes=[("CSV", "*.csv")])
        if path:
            self.ctrl.export_logs_to_csv(path)
            messagebox.showinfo("FurFind", "Audit logs exported to CSV.")

    @guard
    def export_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="audit_logs.pdf",
                                            filetypes=[("PDF", "*.pdf")])
        if path:
            PDFExporter.export_audit_logs(self.logs, path)
            messagebox.showinfo("FurFind", "Audit logs exported to PDF.")
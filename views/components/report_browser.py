import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from controllers.report_controller import ReportController
from repositories.report_repository import ReportRepository
from utils.pdf_exporter import PDFExporter
from views.components.ui_kit import (BG, CARD, TEXT, MUTED, FONT, card, page_header, button, guard,
                                     DataTable, FormDialog, load_thumbnail, resolve_path, fmt_date)

SPECIES = ["Dog", "Cat", "Bird", "Other"]
STATUSES = ["Active", "Resolved", "Closed"]


def show_report_details(parent, r):
    win = tk.Toplevel(parent)
    win.title(f"Report #{r['report_id']}")
    win.configure(bg=CARD)
    win.transient(parent.winfo_toplevel())

    left = tk.Frame(win, bg=CARD)
    left.pack(side="left", padx=20, pady=20, anchor="n")
    photo = load_thumbnail(r.get("photo_path"), (260, 260))
    if photo:
        lbl = tk.Label(left, image=photo, bg=CARD)
        lbl.image = photo
        lbl.pack()
    else:
        tk.Label(left, text="No photo available", fg=MUTED, bg=CARD, width=30, height=10).pack()

    right = tk.Frame(win, bg=CARD)
    right.pack(side="left", padx=(0, 20), pady=20, anchor="n")
    rows = [("Type", r["report_type"]), ("Status", r["status"]), ("Pet name", r.get("pet_name")),
            ("Species", r["species"]), ("Breed", r.get("breed")), ("Gender", r.get("gender")),
            ("Primary color", r.get("primary_color")), ("Secondary color", r.get("secondary_color")),
            ("Marks", r.get("distinguishing_marks")), ("Date", fmt_date(r["incident_date"])),
            ("Location", r["location"])]
    for i, (k, v) in enumerate(rows):
        tk.Label(right, text=k + ":", font=(FONT, 9, "bold"), bg=CARD, fg=MUTED).grid(row=i, column=0, sticky="nw", pady=2)
        tk.Label(right, text=str(v or "—"), font=(FONT, 9), bg=CARD, fg=TEXT, wraplength=260,
                 justify="left").grid(row=i, column=1, sticky="w", padx=8)


class ReportBrowser(tk.Frame):
    """Unified search table. manage=True adds Edit / Soft-Delete (Admin & Super Admin)."""

    def __init__(self, parent, user, title, subtitle, manage=False):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.user, self.manage = user, manage
        self.ctrl = ReportController()
        self.rows = {}
        page_header(self, title, subtitle)

        box = card(self)
        box.pack(fill="both", expand=True)
        bar = tk.Frame(box, bg=CARD)
        bar.pack(fill="x", padx=16, pady=12)
        self.kw = tk.StringVar()
        self.species, self.rtype, self.status = (tk.StringVar(value="All") for _ in range(3))

        tk.Label(bar, text="Search:", font=(FONT, 9, "bold"), bg=CARD).pack(side="left", padx=(0, 6))
        entry = tk.Entry(bar, textvariable=self.kw, width=26, relief="solid", bd=1, font=(FONT, 10))
        entry.pack(side="left", padx=(0, 8), ipady=3)
        entry.bind("<Return>", lambda e: self.refresh())
        for var, vals in ((self.species, ["All"] + SPECIES), (self.rtype, ["All", "Lost", "Found"]),
                          (self.status, ["All"] + STATUSES)):
            ttk.Combobox(bar, textvariable=var, values=vals, state="readonly", width=10).pack(side="left", padx=4)
        button(bar, "Search", self.refresh).pack(side="left", padx=4)
        button(bar, "Reset", self.reset, "secondary").pack(side="left")

        self.table = DataTable(box, [
            ("report_id", "ID", 50), ("report_type", "Type", 65), ("pet_name", "Pet", 110),
            ("species", "Species", 70), ("breed", "Breed", 120), ("primary_color", "Color", 80),
            ("location", "Location", 160), ("date", "Date", 90), ("status", "Status", 80)], height=8)
        self.table.pack(fill="both", expand=True, padx=16)
        self.table.on_double_click(self.view_details)

        acts = tk.Frame(box, bg=CARD)
        acts.pack(fill="x", padx=16, pady=12)
        button(acts, "View Details", self.view_details, "secondary").pack(side="left", padx=(0, 6))
        button(acts, "Export PDF", self.export_pdf, "secondary").pack(side="left", padx=6)
        if manage:
            button(acts, "Edit", self.edit).pack(side="left", padx=6)
            button(acts, "Soft-Delete", self.delete, "danger").pack(side="left", padx=6)
        self.count_lbl = tk.Label(acts, text="", font=(FONT, 9), bg=CARD, fg=MUTED)
        self.count_lbl.pack(side="right")
        self.refresh()

    def reset(self):
        self.kw.set("")
        for v in (self.species, self.rtype, self.status):
            v.set("All")
        self.refresh()

    @guard
    def refresh(self):
        filters = {}
        if self.kw.get().strip():
            filters["keyword"] = self.kw.get().strip()
        for key, var in (("species", self.species), ("report_type", self.rtype), ("status", self.status)):
            if var.get() != "All":
                filters[key] = var.get()
        rows = sorted(self.ctrl.search_reports(filters), key=lambda r: r["report_id"], reverse=True)
        self.rows = {r["report_id"]: r for r in rows}
        self.table.load([{**r, "date": fmt_date(r["incident_date"])} for r in rows], "report_id")
        self.count_lbl.config(text=f"{len(rows)} report(s)")

    def _selected(self):
        rid = self.table.selected_id()
        if rid is None:
            messagebox.showinfo("FurFind", "Select a report first.")
            return None
        return self.rows[rid]

    def view_details(self):
        r = self._selected()
        if r:
            show_report_details(self, r)

    @guard
    def export_pdf(self):
        r = self._selected()
        if not r:
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"report_{r['report_id']}.pdf",
                                            filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        rep = ReportRepository.row_to_report(r)
        rep.photo_path = resolve_path(rep.photo_path)
        PDFExporter.export_pet_report(rep, path)
        messagebox.showinfo("FurFind", "PDF exported successfully.")

    def edit(self):
        r = self._selected()
        if not r:
            return
        fields = [
            {"key": "pet_name", "label": "Pet name"},
            {"key": "species", "label": "Species", "type": "combo", "values": SPECIES},
            {"key": "breed", "label": "Breed"},
            {"key": "gender", "label": "Gender", "type": "combo", "values": ["Male", "Female", "Unknown"]},
            {"key": "primary_color", "label": "Primary color"},
            {"key": "secondary_color", "label": "Secondary color"},
            {"key": "distinguishing_marks", "label": "Distinguishing marks", "type": "text"},
            {"key": "location", "label": "Location"},
            {"key": "status", "label": "Status", "type": "combo", "values": STATUSES},
        ]

        def submit(data):
            self.ctrl.update_report(self.user.user_id, r["report_id"], data)
            self.refresh()
        FormDialog(self, f"Edit Report #{r['report_id']}", fields, submit, initial=r)

    @guard
    def delete(self):
        r = self._selected()
        if r and messagebox.askyesno("Confirm", f"Soft-delete report #{r['report_id']}? It will be hidden from all views."):
            self.ctrl.delete_report(self.user.user_id, r["report_id"])
            self.refresh()
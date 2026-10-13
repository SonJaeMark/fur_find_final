import tkinter as tk
from tkinter import messagebox
from controllers.report_controller import ReportController
from controllers.match_controller import MatchController
from controllers.claim_controller import ClaimController
from views.components.ui_kit import (BG, CARD, MUTED, FONT, card, page_header, button, guard,
                                     DataTable, FormDialog, fmt_date)
from views.components.report_browser import show_report_details


class MyReportsView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.user = user
        self.rc, self.mc, self.cc = ReportController(), MatchController(), ClaimController()
        self.my_rows, self.all_matches, self.match_rows = {}, [], {}
        page_header(self, "My Reports", "Your submissions, suggested matches, and claim / dispute requests.")

        box = card(self)
        box.pack(fill="both", expand=True)
        tk.Label(box, text="Your reports", font=(FONT, 10, "bold"), bg=CARD).pack(anchor="w", padx=16, pady=(12, 4))
        self.reports = DataTable(box, [
            ("report_id", "ID", 50), ("report_type", "Type", 70), ("pet_name", "Pet", 120),
            ("species", "Species", 80), ("breed", "Breed", 130), ("location", "Location", 170),
            ("date", "Date", 90), ("status", "Status", 80)], height=5)
        self.reports.pack(fill="x", padx=16)
        self.reports.on_select(self._show_matches)
        self.reports.on_double_click(self._view_report)

        tk.Label(box, text="Potential matches for the selected report", font=(FONT, 10, "bold"),
                 bg=CARD).pack(anchor="w", padx=16, pady=(14, 4))
        self.matches = DataTable(box, [
            ("match_id", "Match", 55), ("score", "Score", 65), ("other_pet", "Other pet", 120),
            ("other_breed", "Breed", 130), ("other_color", "Color", 80),
            ("other_location", "Location", 170), ("status", "Status", 170)], height=5)
        self.matches.pack(fill="x", padx=16)

        acts = tk.Frame(box, bg=CARD)
        acts.pack(fill="x", padx=16, pady=12)
        button(acts, "Submit Claim", lambda: self._open("Claim")).pack(side="left", padx=(0, 6))
        button(acts, "Submit Dispute", lambda: self._open("Dispute"), "secondary").pack(side="left", padx=6)
        tk.Label(acts, text="Matches are only closed after an admin verifies them.",
                 font=(FONT, 9), fg=MUTED, bg=CARD).pack(side="right")
        self.refresh()

    @guard
    def refresh(self):
        rows = self.rc.get_my_reports(self.user.user_id)
        self.my_rows = {r["report_id"]: r for r in rows}
        self.all_matches = self.mc.get_user_matches(self.user.user_id)
        self.reports.load([{**r, "date": fmt_date(r["incident_date"])} for r in rows], "report_id")
        self.matches.load([], "match_id")

    def _view_report(self):
        rid = self.reports.selected_id()
        if rid:
            show_report_details(self, self.my_rows[rid])

    def _show_matches(self):
        rid = self.reports.selected_id()
        rows = []
        for m in self.all_matches:
            if rid not in (m["lost_report_id"], m["found_report_id"]):
                continue
            side = "found" if m["lost_report_id"] == rid else "lost"
            rows.append({"match_id": m["match_id"], "score": f"{float(m['match_score']):.1f}%",
                         "other_pet": m[f"{side}_pet_name"], "other_breed": m[f"{side}_breed"],
                         "other_color": m[f"{side}_color"], "other_location": m[f"{side}_location"],
                         "status": m["status"]})
        self.matches.load(rows, "match_id")

    def _open(self, claim_type):
        mid = self.matches.selected_id()
        if mid is None:
            messagebox.showinfo("FurFind", "Select a match first.")
            return

        def submit(data):
            self.cc.submit_claim(self.user.user_id, mid, claim_type, data["message"])
            messagebox.showinfo("FurFind", f"{claim_type} submitted for admin review.")
        label = ("Why is this your pet / the owner? (ownership proof, details)" if claim_type == "Claim"
                 else "Why do you dispute this match?")
        FormDialog(self, f"Submit {claim_type} for Match #{mid}",
                   [{"key": "message", "label": label, "type": "text"}], submit, submit_text="Submit")
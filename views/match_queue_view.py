import tkinter as tk
from tkinter import messagebox
from controllers.match_controller import MatchController
from controllers.claim_controller import ClaimController
from core.exceptions import ValidationError
from views.components.ui_kit import (BG, CARD, TEXT, MUTED, FONT, card, page_header, button, guard,
                                     DataTable, load_thumbnail, fmt_date)


class MatchQueueView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.user = user
        self.mc, self.cc = MatchController(), ClaimController()
        self.rows = {}
        page_header(self, "Match Verification",
                    "Review auto-detected matches. No case is closed until you explicitly approve it.")

        box = card(self)
        box.pack(fill="both", expand=True)
        self.table = DataTable(box, [
            ("match_id", "Match", 55), ("score", "Score", 65), ("lost_pet_name", "Lost pet", 110),
            ("found_pet_name", "Found pet", 110), ("lost_species", "Species", 70),
            ("lost_location", "Lost at", 150), ("found_location", "Found at", 150), ("claims", "Claims", 55)],
            height=5)
        self.table.pack(fill="x", padx=16, pady=(12, 8))
        self.table.on_select(self._show)

        panels = tk.Frame(box, bg=CARD)
        panels.pack(fill="x", padx=16)
        panels.columnconfigure((0, 1), weight=1, uniform="p")
        self.lost = self._panel(panels, "LOST REPORT", 0)
        self.found = self._panel(panels, "FOUND REPORT", 1)

        tk.Label(box, text="Claims & disputes", font=(FONT, 9, "bold"), bg=CARD).pack(anchor="w", padx=16, pady=(8, 2))
        self.claims_txt = tk.Text(box, height=3, font=(FONT, 9), relief="solid", bd=1, wrap="word", state="disabled")
        self.claims_txt.pack(fill="x", padx=16)

        bar = tk.Frame(box, bg=CARD)
        bar.pack(fill="x", padx=16, pady=10)
        tk.Label(bar, text="Admin notes / reason:", font=(FONT, 9, "bold"), bg=CARD).pack(side="left")
        self.notes = tk.Entry(bar, width=36, font=(FONT, 10), relief="solid", bd=1)
        self.notes.pack(side="left", padx=8, ipady=3)
        button(bar, "Approve", self._approve, "success").pack(side="left", padx=4)
        button(bar, "Reject", self._reject, "danger").pack(side="left", padx=4)
        button(bar, "Refresh", self.refresh, "secondary").pack(side="right")
        self.refresh()

    def _panel(self, parent, title, col):
        f = tk.Frame(parent, bg=CARD, highlightbackground="#E4E4E7", highlightthickness=1)
        f.grid(row=0, column=col, sticky="nsew", padx=4)
        tk.Label(f, text=title, font=(FONT, 8, "bold"), fg=MUTED, bg=CARD).pack(anchor="w", padx=8, pady=(6, 0))
        body = tk.Frame(f, bg=CARD)
        body.pack(fill="x", padx=8, pady=6)
        photo = tk.Label(body, bg=CARD, width=14, height=6)
        photo.pack(side="left")
        info = tk.Label(body, text="Select a match", font=(FONT, 9), bg=CARD, fg=TEXT, justify="left", anchor="nw")
        info.pack(side="left", padx=10, fill="x")
        return {"photo": photo, "info": info}

    def _fill(self, panel, m, side):
        panel["info"].config(text=(
            f"#{m[side + '_report_id']} · {m[side + '_pet_name']}\n"
            f"{m[side + '_species']} / {m[side + '_breed']} / {m[side + '_color']}\n"
            f"{m[side + '_location']} · {fmt_date(m[side + '_date'])}\n"
            f"Reporter: {m[side + '_owner']} ({m[side + '_contact']})"))
        img = load_thumbnail(m[side + "_photo"], (100, 100))
        panel["photo"].image = img
        panel["photo"].config(image=img or "", text="" if img else "No photo")

    @guard
    def refresh(self):
        rows = self.mc.get_pending_details()
        self.rows = {m["match_id"]: m for m in rows}
        self.table.load([{**m, "score": f"{float(m['match_score']):.1f}%",
                          "claims": len(self.cc.get_claims_for_match(m["match_id"]))} for m in rows], "match_id")
        self.notes.delete(0, "end")

    @guard
    def _show(self):
        mid = self.table.selected_id()
        m = self.rows.get(mid)
        if not m:
            return
        self._fill(self.lost, m, "lost")
        self._fill(self.found, m, "found")
        claims = self.cc.get_claims_for_match(mid)
        text = "\n".join(f"[{c['claim_type']}] {c['full_name']} ({c['contact_no']}): {c['message']}"
                         for c in claims) or "No claims or disputes submitted."
        self.claims_txt.config(state="normal")
        self.claims_txt.delete("1.0", "end")
        self.claims_txt.insert("1.0", text)
        self.claims_txt.config(state="disabled")

    def _need_selection(self):
        mid = self.table.selected_id()
        if mid is None:
            messagebox.showinfo("FurFind", "Select a match first.")
        return mid

    @guard
    def _approve(self):
        mid = self._need_selection()
        if mid and messagebox.askyesno("Confirm", f"Approve match #{mid}? Both reports will be marked Resolved."):
            self.mc.approve_match(mid, self.user.user_id, self.notes.get().strip())
            self.refresh()

    @guard
    def _reject(self):
        mid = self._need_selection()
        if not mid:
            return
        reason = self.notes.get().strip()
        if not reason:
            raise ValidationError("Please enter a reason for rejecting this match.")
        self.mc.reject_match(mid, self.user.user_id, reason)
        self.refresh()
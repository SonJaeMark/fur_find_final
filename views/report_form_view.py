import os
import shutil
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk, filedialog, messagebox
from controllers.report_controller import ReportController
from utils.validator import Validator
from core.exceptions import ValidationError
from views.components.ui_kit import (BG, CARD, TEXT, MUTED, FONT, UPLOAD_DIR, card, page_header,
                                     button, guard, load_thumbnail)


class ReportFormView(tk.Frame):
    def __init__(self, parent, user, on_done=None):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self.user, self.on_done, self.ctrl = user, on_done, ReportController()
        self.photo_path, self.w, self._thumb = "", {}, None
        page_header(self, "Report a Pet", "Submit a Lost or Found report. Fields marked * and a photo are required.")

        box = card(self)
        box.pack(fill="both", expand=True)
        self.form = tk.Frame(box, bg=CARD)
        self.form.pack(fill="both", expand=True, padx=24, pady=14)
        self.form.columnconfigure((0, 1), weight=1, uniform="c")

        # Report type
        self.type_var = tk.StringVar(value="Lost")
        tr = tk.Frame(self.form, bg=CARD)
        tr.grid(row=0, column=0, columnspan=2, sticky="w", padx=8)
        tk.Label(tr, text="Report type *", font=(FONT, 9, "bold"), bg=CARD).pack(side="left", padx=(0, 12))
        for t in ("Lost", "Found"):
            tk.Radiobutton(tr, text=f"I {t.lower()} a pet", variable=self.type_var, value=t,
                           bg=CARD, font=(FONT, 10), activebackground=CARD).pack(side="left", padx=6)

        self._add("pet_name", "Pet name (if known)", 1, 0)
        self._add("species", "Species *", 1, 1, "combo", ["Dog", "Cat", "Bird", "Other"])
        self._add("breed", "Breed", 2, 0)
        self._add("gender", "Gender", 2, 1, "combo", ["Unknown", "Male", "Female"])
        self._add("primary_color", "Primary color *", 3, 0)
        self._add("secondary_color", "Secondary color", 3, 1)
        self._add("incident_date", "Date lost/found * (YYYY-MM-DD)", 4, 0, default=datetime.now().strftime("%Y-%m-%d"))
        self._add("location", "Location *", 4, 1)

        mk = tk.Frame(self.form, bg=CARD)
        mk.grid(row=5, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        tk.Label(mk, text="Distinguishing marks", font=(FONT, 9, "bold"), bg=CARD).pack(anchor="w")
        self.marks = tk.Text(mk, height=3, font=(FONT, 10), relief="solid", bd=1, wrap="word")
        self.marks.pack(fill="x")

        ph = tk.Frame(self.form, bg=CARD)
        ph.grid(row=6, column=0, columnspan=2, sticky="ew", padx=8, pady=6)
        button(ph, "Choose Photo *", self._choose_photo, "secondary").pack(side="left")
        self.photo_lbl = tk.Label(ph, text="No file selected", font=(FONT, 9), fg=MUTED, bg=CARD)
        self.photo_lbl.pack(side="left", padx=10)
        self.thumb_lbl = tk.Label(ph, bg=CARD)
        self.thumb_lbl.pack(side="right")

        acts = tk.Frame(self.form, bg=CARD)
        acts.grid(row=7, column=0, columnspan=2, sticky="w", padx=8, pady=8)
        button(acts, "Submit Report", self._submit).pack(side="left", padx=(0, 8))
        button(acts, "Clear", self._clear, "secondary").pack(side="left")

    def _add(self, key, label, row, col, kind="entry", values=None, default=""):
        cell = tk.Frame(self.form, bg=CARD)
        cell.grid(row=row, column=col, sticky="ew", padx=8, pady=4)
        tk.Label(cell, text=label, font=(FONT, 9, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
        if kind == "combo":
            w = ttk.Combobox(cell, values=values, state="readonly")
            w.set(values[0])
        else:
            w = tk.Entry(cell, font=(FONT, 10), relief="solid", bd=1)
            w.insert(0, default)
        w.pack(fill="x", ipady=3)
        self.w[key] = w

    def _choose_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if not path:
            return
        self.photo_path = path
        self.photo_lbl.config(text=os.path.basename(path))
        self._thumb = load_thumbnail(path, (90, 90))
        self.thumb_lbl.config(image=self._thumb or "")

    def _clear(self):
        for k, w in self.w.items():
            if isinstance(w, ttk.Combobox):
                w.current(0)
            else:
                w.delete(0, "end")
        self.w["incident_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.marks.delete("1.0", "end")
        self.photo_path = ""
        self.photo_lbl.config(text="No file selected")
        self.thumb_lbl.config(image="")

    @guard
    def _submit(self):
        g = lambda k: self.w[k].get().strip()
        Validator.validate_non_empty(g("primary_color"), "Primary color")
        Validator.validate_non_empty(g("location"), "Location")
        try:
            incident = datetime.strptime(g("incident_date"), "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Date must use the format YYYY-MM-DD.")
        if incident > datetime.now():
            raise ValidationError("The date cannot be in the future.")
        src = Validator.validate_image_file(self.photo_path)

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        dest = os.path.join(UPLOAD_DIR, f"{int(time.time())}_{os.path.basename(src)}")
        shutil.copy(src, dest)

        self.ctrl.submit_report(
            user_id=self.user.user_id, category=self.type_var.get(), pet_name=g("pet_name"),
            species=g("species"), breed=g("breed") or "Unknown", gender=g("gender"),
            primary_color=g("primary_color"), secondary_color=g("secondary_color"),
            distinguishing_marks=self.marks.get("1.0", "end").strip(), incident_date=incident,
            location=g("location"), photo_path=dest)
        messagebox.showinfo("FurFind", "Report submitted. Any potential matches go to admin verification "
                                       "and will appear under My Reports.")
        if self.on_done:
            self.on_done()
import os
import tkinter as tk
from tkinter import ttk, messagebox
from functools import wraps
from config.init import PROJECT_ROOT
from core.exceptions import FurFindException

BG, CARD, DARK = "#F4F4F5", "#FFFFFF", "#18181B"
TEXT, MUTED, BORDER = "#111827", "#71717A", "#E4E4E7"
GOOD, BAD = "#16A34A", "#DC2626"
FONT = "Segoe UI"
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")


def apply_styles():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("Treeview", rowheight=28, font=(FONT, 9), background=CARD,
                fieldbackground=CARD, foreground=TEXT, borderwidth=0)
    s.configure("Treeview.Heading", font=(FONT, 9, "bold"), background=BORDER, foreground=TEXT, relief="flat")
    s.map("Treeview", background=[("selected", DARK)], foreground=[("selected", "#FFFFFF")])


def guard(fn):
    """Decorator: show backend/validation errors in a message box instead of crashing."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except FurFindException as e:
            messagebox.showerror("FurFind", e.message)
        except ValueError as e:
            messagebox.showerror("FurFind", str(e))
    return wrapper


def resolve_path(p):
    if not p:
        return ""
    return p if os.path.isabs(p) else os.path.join(PROJECT_ROOT, p)


def load_thumbnail(path, size=(150, 150)):
    try:
        from PIL import Image, ImageTk
        path = resolve_path(path)
        if not os.path.exists(path):
            return None
        img = Image.open(path)
        img.thumbnail(size)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def fmt_date(v):
    return v.strftime("%Y-%m-%d") if hasattr(v, "strftime") else ("" if v is None else str(v))


def card(parent):
    return tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)


def page_header(parent, title, subtitle=""):
    f = tk.Frame(parent, bg=BG)
    f.pack(fill="x", pady=(0, 12))
    tk.Label(f, text=title, font=(FONT, 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w")
    if subtitle:
        tk.Label(f, text=subtitle, font=(FONT, 9), bg=BG, fg=MUTED).pack(anchor="w")
    return f


def button(parent, text, command, kind="primary"):
    bg, fg = {"primary": (DARK, "#FFFFFF"), "secondary": (BORDER, TEXT),
              "danger": (BAD, "#FFFFFF"), "success": (GOOD, "#FFFFFF")}[kind]
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg, activebackground=bg,
                     activeforeground=fg, font=(FONT, 9, "bold"), bd=0, padx=14, pady=6, cursor="hand2")


def stat_card(parent, label, value):
    f = card(parent)
    tk.Label(f, text=str(value), font=(FONT, 24, "bold"), bg=CARD, fg=TEXT).pack(anchor="w", padx=20, pady=(16, 0))
    tk.Label(f, text=label, font=(FONT, 9), bg=CARD, fg=MUTED).pack(anchor="w", padx=20, pady=(0, 16))
    return f


class DataTable(tk.Frame):
    """Treeview + scrollbar. columns = [(key, heading, width), ...]"""

    def __init__(self, parent, columns, height=8):
        super().__init__(parent, bg=CARD)
        self.keys = [c[0] for c in columns]
        self.tree = ttk.Treeview(self, columns=self.keys, show="headings", height=height, selectmode="browse")
        for key, head, width in columns:
            self.tree.heading(key, text=head)
            self.tree.column(key, width=width, anchor="w")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def load(self, rows, id_key):
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            vals = ["" if r.get(k) is None else r.get(k) for k in self.keys]
            self.tree.insert("", "end", iid=str(r[id_key]), values=vals)

    def selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def on_select(self, cb):
        self.tree.bind("<<TreeviewSelect>>", lambda e: cb())

    def on_double_click(self, cb):
        self.tree.bind("<Double-1>", lambda e: cb())


class FormDialog(tk.Toplevel):
    """Generic modal form. fields = [{"key","label","type": entry|password|combo|text,"values":[...]}]
    on_submit(dict) may raise FurFindException/ValueError; the message is shown inline."""

    def __init__(self, parent, title, fields, on_submit, initial=None, submit_text="Save"):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=CARD)
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.on_submit, self.widgets = on_submit, {}
        initial = initial or {}

        body = tk.Frame(self, bg=CARD)
        body.pack(padx=24, pady=(18, 8))
        for f in fields:
            kind, key = f.get("type", "entry"), f["key"]
            tk.Label(body, text=f["label"], font=(FONT, 9, "bold"), bg=CARD, fg=TEXT).pack(anchor="w", pady=(8, 2))
            value = initial.get(key) or ""
            if kind == "combo":
                w = ttk.Combobox(body, values=f["values"], state="readonly", width=42)
                w.set(value or f["values"][0])
            elif kind == "text":
                w = tk.Text(body, width=44, height=5, font=(FONT, 10), relief="solid", bd=1, wrap="word")
                w.insert("1.0", value)
            else:
                w = tk.Entry(body, width=44, font=(FONT, 10), relief="solid", bd=1,
                             show="•" if kind == "password" else "")
                w.insert(0, value)
            w.pack(fill="x", ipady=2)
            self.widgets[key] = (kind, w)

        self.err = tk.Label(self, text="", fg=BAD, bg=CARD, font=(FONT, 9), wraplength=360)
        self.err.pack(padx=24)
        row = tk.Frame(self, bg=CARD)
        row.pack(pady=(4, 18))
        button(row, submit_text, self._submit).pack(side="left", padx=4)
        button(row, "Cancel", self.destroy, "secondary").pack(side="left", padx=4)
        self.wait_visibility()
        self.grab_set()

    def _values(self):
        return {k: (w.get("1.0", "end").strip() if kind == "text" else w.get().strip())
                for k, (kind, w) in self.widgets.items()}

    def _submit(self):
        try:
            self.on_submit(self._values())
        except FurFindException as e:
            self.err.config(text=e.message)
            return
        except ValueError as e:
            self.err.config(text=str(e))
            return
        self.destroy()
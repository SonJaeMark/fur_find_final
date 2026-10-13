import tkinter as tk
from tkinter import ttk


class RoundedCanvasFrame(tk.Canvas):
    """Custom Tkinter Canvas to draw smooth rounded background containers."""
    def __init__(self, parent, bg_color, corner_radius=12, border_color=None, border_width=1, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, **kwargs)
        self.bg_color = bg_color
        self.corner_radius = corner_radius
        self.border_color = border_color
        self.border_width = border_width
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return
            
        r = self.corner_radius
        w = self.border_width if self.border_color else 0

        x1, y1 = w / 2, w / 2
        x2, y2 = width - w / 2, height - w / 2

        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r,
            x2, y2, x2 - r, y2,
            x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]

        kw = {"fill": self.bg_color, "smooth": True}
        if self.border_color:
            kw["outline"] = self.border_color
            kw["width"] = self.border_width

        self.create_polygon(points, **kw)


class RoundedEntry(RoundedCanvasFrame):
    """Custom Entry component with rounded border, placeholder, and click focus fix."""
    def __init__(self, parent, placeholder="", show=None, **kwargs):
        super().__init__(
            parent,
            bg_color="#FFFFFF",
            corner_radius=6,
            border_color="#D4D4D8",
            border_width=1,
            height=38,
            **kwargs
        )
        self.placeholder = placeholder
        self.show_char = show
        self.is_placeholder_active = True

        self.entry = tk.Entry(
            self,
            bg="#FFFFFF",
            fg="#A1A1AA",
            font=("Segoe UI", 10),
            bd=0,
            relief="flat",
            highlightthickness=0
        )
        self.entry.insert(0, self.placeholder)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

        self.entry_window = self.create_window(12, 19, window=self.entry, anchor="w")
        
        # 1. Forward Canvas Clicks directly to Entry Focus
        self.bind("<Button-1>", lambda e: self.entry.focus_set())
        
        # 2. Adjust Inner Entry Width on Resize (Without recursive _draw calls)
        self.bind("<Configure>", self._adjust_entry_width)

    def _adjust_entry_width(self, event):
        # Draw rounded border polygon
        self._draw(event)
        # Resize inner Entry box to fit rounded container padding
        if event.width > 24:
            self.itemconfig(self.entry_window, width=event.width - 24)

    def _on_focus_in(self, event):
        if self.is_placeholder_active:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#111827")
            if self.show_char:
                self.entry.config(show=self.show_char)
            self.is_placeholder_active = False

    def _on_focus_out(self, event):
        if not self.entry.get():
            self.is_placeholder_active = True
            self.entry.config(fg="#A1A1AA", show="")
            self.entry.insert(0, self.placeholder)

    def get(self):
        return "" if self.is_placeholder_active else self.entry.get()

class LoginAndRegisterView(tk.Frame):
    """Main Authentication View containing Login and Register tabs."""
    def __init__(self, parent):
        super().__init__(parent, bg="#F4F4F5")
        self.pack(fill="both", expand=True)

        self.on_login = None
        self.on_register = None

        # Center Container
        self.center_frame = tk.Frame(self, bg="#F4F4F5")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # 1. Branding Header
        self._create_header()

        # 2. Main Card Frame
        self.card_canvas = RoundedCanvasFrame(
            self.center_frame,
            bg_color="#FFFFFF",
            corner_radius=12,
            border_color="#E4E4E7",
            border_width=1,
            width=400,
            height=320
        )
        self.card_canvas.pack(padx=20, pady=10)
        self.card_canvas.pack_propagate(False)

        # 3. Tab Navigation Bar (Segmented Tab Style)
        self.tab_container = tk.Frame(self.card_canvas, bg="#FFFFFF")
        self.tab_container.pack(fill="x", padx=24, pady=(20, 0))

        self.btn_login_tab = tk.Button(
            self.tab_container,
            text="Login",
            font=("Segoe UI", 10, "bold"),
            fg="#111827",
            bg="#FFFFFF",
            bd=0,
            activebackground="#FFFFFF",
            cursor="hand2",
            command=lambda: self.switch_tab("login")
        )
        self.btn_login_tab.pack(side="left", expand=True, fill="x")

        self.btn_register_tab = tk.Button(
            self.tab_container,
            text="Register",
            font=("Segoe UI", 10, "bold"),
            fg="#A1A1AA",
            bg="#FFFFFF",
            bd=0,
            activebackground="#FFFFFF",
            cursor="hand2",
            command=lambda: self.switch_tab("register")
        )
        self.btn_register_tab.pack(side="left", expand=True, fill="x")

        # Tab Underline Indicator Bar
        indicator_frame = tk.Frame(self.card_canvas, bg="#E4E4E7", height=2)
        indicator_frame.pack(fill="x", padx=24, pady=(8, 12))

        self.indicator_line = tk.Frame(indicator_frame, bg="#111827", height=2)
        self.indicator_line.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)

        # 4. Active Content Frame Container
        self.view_container = tk.Frame(self.card_canvas, bg="#FFFFFF")
        self.view_container.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.login_frame = tk.Frame(self.view_container, bg="#FFFFFF")
        self.register_frame = tk.Frame(self.view_container, bg="#FFFFFF")

        self._build_login_view()
        self._build_register_view()

        # Initial Tab State
        self.switch_tab("login")

    def _create_header(self):
        header_frame = tk.Frame(self.center_frame, bg="#F4F4F5")
        header_frame.pack(pady=(0, 12))

        icon_canvas = tk.Canvas(header_frame, width=32, height=32, bg="#F4F4F5", highlightthickness=0)
        icon_canvas.pack(side="left", padx=(0, 8))
        
        icon_canvas.create_rectangle(2, 2, 30, 30, outline="#111827", width=2)
        icon_canvas.create_oval(11, 16, 21, 25, fill="#111827", outline="")
        icon_canvas.create_oval(8, 11, 13, 16, fill="#111827", outline="")
        icon_canvas.create_oval(14, 8, 18, 13, fill="#111827", outline="")
        icon_canvas.create_oval(19, 11, 24, 16, fill="#111827", outline="")

        title_label = tk.Label(
            header_frame,
            text="FurFind",
            font=("Segoe UI", 20, "bold"),
            fg="#111827",
            bg="#F4F4F5"
        )
        title_label.pack(side="left")

    def switch_tab(self, tab_name):
        """Swaps active tab and resizes card container smoothly."""
        if tab_name == "login":
            self.register_frame.pack_forget()
            self.login_frame.pack(fill="both", expand=True)
            self.btn_login_tab.config(fg="#111827")
            self.btn_register_tab.config(fg="#A1A1AA")
            self.indicator_line.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)
            self.card_canvas.config(height=320)
        else:
            self.login_frame.pack_forget()
            self.register_frame.pack(fill="both", expand=True)
            self.btn_login_tab.config(fg="#A1A1AA")
            self.btn_register_tab.config(fg="#111827")
            self.indicator_line.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=1.0)
            self.card_canvas.config(height=580)

    def _build_login_view(self):
        lbl_user = tk.Label(self.login_frame, text="Username or Email", font=("Segoe UI", 9, "bold"), fg="#111827", bg="#FFFFFF")
        lbl_user.pack(anchor="w", pady=(0, 4))
        self.login_user_entry = RoundedEntry(self.login_frame, placeholder="Enter your username or email")
        self.login_user_entry.pack(fill="x", pady=(0, 14))

        lbl_pass = tk.Label(self.login_frame, text="Password", font=("Segoe UI", 9, "bold"), fg="#111827", bg="#FFFFFF")
        lbl_pass.pack(anchor="w", pady=(0, 4))
        self.login_pass_entry = RoundedEntry(self.login_frame, placeholder="••••••••", show="•")
        self.login_pass_entry.pack(fill="x", pady=(0, 20))

        # Action Button
        btn_sign_in = RoundedCanvasFrame(self.login_frame, bg_color="#18181B", corner_radius=6, height=38, cursor="hand2")
        btn_sign_in.pack(fill="x")
        btn_lbl = tk.Label(btn_sign_in, text="Sign In", font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg="#18181B", cursor="hand2")
        
        btn_sign_in.bind("<Configure>", lambda e: btn_sign_in.coords(1, e.width / 2, e.height / 2))
        btn_sign_in.create_window(175, 19, window=btn_lbl, anchor="center")
        btn_sign_in.bind("<Button-1>", lambda e: self._trigger_login())
        btn_lbl.bind("<Button-1>", lambda e: self._trigger_login())

    def _build_register_view(self):
        lbl_title = tk.Label(self.register_frame, text="Create Account", font=("Segoe UI", 13, "bold"), fg="#111827", bg="#FFFFFF")
        lbl_title.pack(anchor="center", pady=(0, 2))
        
        fields = [
            ("Full Name *", "John Doe", False),
            ("Email Address *", "john@domain.com", False),
            ("Contact Number *", "+1 (555) 000-0000", False),
            ("Password *", "Minimum 8 characters", True),
            ("Confirm Password *", "Re-enter password", True),
        ]

        self.reg_entries = {}
        for label_text, placeholder, is_pass in fields:
            lbl = tk.Label(self.register_frame, text=label_text, font=("Segoe UI", 8, "bold"), fg="#111827", bg="#FFFFFF")
            lbl.pack(anchor="w", pady=(2, 2))
            entry = RoundedEntry(self.register_frame, placeholder=placeholder, show="•" if is_pass else None)
            entry.pack(fill="x", pady=(0, 4))
            self.reg_entries[label_text] = entry

        lbl_role = tk.Label(self.register_frame, text="Account Role", font=("Segoe UI", 8, "bold"), fg="#111827", bg="#FFFFFF")
        lbl_role.pack(anchor="w", pady=(2, 2))

        role_container = RoundedCanvasFrame(self.register_frame, bg_color="#FFFFFF", corner_radius=6, border_color="#D4D4D8", border_width=1, height=34)
        role_container.pack(fill="x", pady=(0, 14))

        self.role_var = tk.StringVar(value="Pet Owner")
        role_dropdown = ttk.Combobox(role_container, textvariable=self.role_var, values=["Pet Owner"], state="readonly")
        role_dropdown.pack(fill="both", expand=True, padx=6, pady=4)

        btn_reg = RoundedCanvasFrame(self.register_frame, bg_color="#18181B", corner_radius=6, height=38, cursor="hand2")
        btn_reg.pack(fill="x", pady=(0, 10))
        btn_lbl = tk.Label(btn_reg, text="Register", font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg="#18181B", cursor="hand2")
        
        btn_reg.bind("<Configure>", lambda e: btn_reg.coords(1, e.width / 2, e.height / 2))
        btn_reg.create_window(175, 19, window=btn_lbl, anchor="center")
        btn_reg.bind("<Button-1>", lambda e: self._trigger_register())
        btn_lbl.bind("<Button-1>", lambda e: self._trigger_register())

    def _trigger_login(self):
        if callable(self.on_login):
            self.on_login()

    def _trigger_register(self):
        if callable(self.on_register):
            self.on_register()
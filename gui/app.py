import customtkinter as ctk
from auth.auth_manager import AuthManager
from utils.backup import create_backup
from tkinter import messagebox


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("School Uniform Billing System")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._center()
        self._active_frame = None
        self._build()
        self._show_default()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1280) // 2
        y = (self.winfo_screenheight() - 780) // 2
        self.geometry(f"1280x780+{x}+{y}")

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=210, corner_radius=0,
                               fg_color="#1e1e2e")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo / app name
        ctk.CTkLabel(sidebar, text="🎓", font=ctk.CTkFont(size=36)).pack(pady=(24, 4))
        ctk.CTkLabel(sidebar, text="Uniform Billing",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#cdd6f4").pack()
        user = AuthManager.current_user()
        ctk.CTkLabel(sidebar, text=f"{user.full_name or user.username} ({user.role})",
                     font=ctk.CTkFont(size=11), text_color="#6c7086").pack(pady=(2, 20))

        ctk.CTkFrame(sidebar, height=1, fg_color="#313244").pack(fill="x", padx=16, pady=(0, 16))

        # Nav buttons
        self._nav_buttons = {}

        sales_items = [
            ("New Bill", "💳", self._show_billing),
            ("Bill History", "📋", self._show_history),
            ("Reports", "📊", self._show_reports),
        ]
        ctk.CTkLabel(sidebar, text="SALES", font=ctk.CTkFont(size=10),
                     text_color="#6c7086").pack(anchor="w", padx=20)
        for label, icon, cmd in sales_items:
            self._nav_btn(sidebar, f"{icon}  {label}", cmd)

        if AuthManager.is_admin():
            ctk.CTkFrame(sidebar, height=1, fg_color="#313244").pack(fill="x", padx=16, pady=10)
            ctk.CTkLabel(sidebar, text="ADMIN", font=ctk.CTkFont(size=10),
                         text_color="#6c7086").pack(anchor="w", padx=20)
            admin_items = [
                ("Schools", "🏫", self._show_schools),
                ("Classes", "📚", self._show_classes),
                ("Items", "👕", self._show_items),
                ("Users", "👤", self._show_users),
                ("Shop Settings", "⚙️", self._show_settings),
            ]
            for label, icon, cmd in admin_items:
                self._nav_btn(sidebar, f"{icon}  {label}", cmd)

        # Bottom actions
        ctk.CTkFrame(sidebar, height=1, fg_color="#313244").pack(fill="x", padx=16, pady=10)
        ctk.CTkButton(sidebar, text="💾  Backup DB", fg_color="transparent",
                      hover_color="#313244", anchor="w", corner_radius=6,
                      command=self._do_backup).pack(fill="x", padx=12, pady=2)

        appearance_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        appearance_frame.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(appearance_frame, text="🌙  Theme:", text_color="#6c7086",
                     font=ctk.CTkFont(size=11)).pack(side="left")
        self.theme_var = ctk.StringVar(value="dark")
        ctk.CTkSwitch(appearance_frame, text="", variable=self.theme_var,
                      onvalue="light", offvalue="dark",
                      command=self._toggle_theme, width=40).pack(side="right")

        ctk.CTkButton(sidebar, text="🚪  Logout", fg_color="transparent",
                      hover_color="#ea4335", anchor="w", corner_radius=6,
                      command=self._logout).pack(fill="x", padx=12, pady=(4, 20), side="bottom")

        # ── Content area ──────────────────────────────────────────────────────
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=0)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _nav_btn(self, parent, text, cmd):
        btn = ctk.CTkButton(
            parent, text=text, anchor="w", corner_radius=6,
            fg_color="transparent", hover_color="#313244",
            text_color="#cdd6f4", font=ctk.CTkFont(size=13),
            command=lambda c=cmd, b=text: (self._set_active_nav(b), c())
        )
        btn.pack(fill="x", padx=12, pady=2)
        self._nav_buttons[text] = btn

    def _set_active_nav(self, key):
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#1a73e8", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#cdd6f4")

    def _show_frame(self, FrameClass, nav_key=None):
        if self._active_frame:
            self._active_frame.destroy()
        frame = FrameClass(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self._active_frame = frame
        if nav_key:
            self._set_active_nav(nav_key)

    def _show_default(self):
        self._show_billing()

    def _show_billing(self):
        from gui.sales.billing import BillingFrame
        self._show_frame(BillingFrame, "💳  New Bill")

    def _show_history(self):
        from gui.sales.bill_history import BillHistoryFrame
        self._show_frame(BillHistoryFrame, "📋  Bill History")

    def _show_reports(self):
        from gui.sales.reports import ReportsFrame
        self._show_frame(ReportsFrame, "📊  Reports")

    def _show_schools(self):
        from gui.admin.school_manager import SchoolManagerFrame
        self._show_frame(SchoolManagerFrame, "🏫  Schools")

    def _show_classes(self):
        from gui.admin.class_manager import ClassManagerFrame
        self._show_frame(ClassManagerFrame, "📚  Classes")

    def _show_items(self):
        from gui.admin.item_manager import ItemManagerFrame
        self._show_frame(ItemManagerFrame, "👕  Items")

    def _show_users(self):
        from gui.admin.user_manager import UserManagerFrame
        self._show_frame(UserManagerFrame, "👤  Users")

    def _show_settings(self):
        from gui.admin.settings import ShopSettingsFrame
        self._show_frame(ShopSettingsFrame, "⚙️  Shop Settings")

    def _do_backup(self):
        ok, msg = create_backup()
        if ok:
            messagebox.showinfo("Backup", msg)
        else:
            messagebox.showerror("Backup Failed", msg)

    def _toggle_theme(self):
        ctk.set_appearance_mode(self.theme_var.get())

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            AuthManager.logout()
            self.destroy()
            import main
            main.start()

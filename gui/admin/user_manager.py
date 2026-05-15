import customtkinter as ctk
from tkinter import messagebox
from database.database import get_session
from database.models import User
from auth.auth_manager import AuthManager


class UserManagerFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.selected_id = None
        self._build()
        self._load()

    def _build(self):
        ctk.CTkLabel(self, text="User Management",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 16))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)

        left = ctk.CTkFrame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(left, text="Users", font=ctk.CTkFont(weight="bold")).pack(pady=8)
        self.user_list = ctk.CTkScrollableFrame(left)
        self.user_list.pack(fill="both", expand=True, padx=8)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(btn_row, text="Toggle Active", width=110,
                      command=self._toggle_active).pack(side="right")
        ctk.CTkButton(btn_row, text="New", width=80,
                      command=self._new).pack(side="right", padx=(0, 6))

        right = ctk.CTkFrame(content)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="User Details",
                     font=ctk.CTkFont(weight="bold")).pack(pady=8)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(fill="x", padx=16)

        self.entries = {}
        for label, key in [("Username *", "username"), ("Full Name", "full_name"),
                            ("Password *", "password")]:
            ctk.CTkLabel(form, text=label, anchor="w").pack(fill="x", pady=(6, 0))
            e = ctk.CTkEntry(form, show="*" if key == "password" else "")
            e.pack(fill="x", pady=(2, 0))
            self.entries[key] = e

        ctk.CTkLabel(form, text="Role", anchor="w").pack(fill="x", pady=(8, 0))
        self.role_var = ctk.StringVar(value="accountant")
        rf = ctk.CTkFrame(form, fg_color="transparent")
        rf.pack(anchor="w", pady=(2, 0))
        ctk.CTkRadioButton(rf, text="Accountant", variable=self.role_var,
                           value="accountant").pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(rf, text="Admin", variable=self.role_var,
                           value="admin").pack(side="left")

        ctk.CTkLabel(form, text="(Leave password blank to keep existing)",
                     font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(right, text="Save User", height=38,
                      command=self._save).pack(pady=14, padx=16, fill="x")
        self.status_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=11))
        self.status_label.pack()

    def _load(self):
        for w in self.user_list.winfo_children():
            w.destroy()
        db = get_session()
        users = db.query(User).order_by(User.username).all()
        db.close()
        for user in users:
            status = "✓" if user.is_active else "✗"
            color = "#34a853" if user.is_active else "#ea4335"
            row = ctk.CTkFrame(self.user_list, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=status, text_color=color, width=20).pack(side="left")
            ctk.CTkButton(
                row, text=f"{user.username} ({user.role})", anchor="w",
                fg_color="transparent", hover_color="#313244", text_color=("black", "white"),
                command=lambda uid=user.id: self._select(uid)
            ).pack(side="left", fill="x", expand=True)

    def _select(self, user_id):
        self.selected_id = user_id
        db = get_session()
        user = db.query(User).get(user_id)
        if user:
            for key in ("username", "full_name"):
                self.entries[key].delete(0, "end")
                self.entries[key].insert(0, getattr(user, key) or "")
            self.entries["password"].delete(0, "end")
            self.role_var.set(user.role)
        db.close()

    def _new(self):
        self.selected_id = None
        for e in self.entries.values():
            e.delete(0, "end")
        self.role_var.set("accountant")

    def _save(self):
        username = self.entries["username"].get().strip()
        password = self.entries["password"].get().strip()
        if not username:
            self.status_label.configure(text="Username required.", text_color="#ea4335")
            return
        if not self.selected_id and not password:
            self.status_label.configure(text="Password required for new user.", text_color="#ea4335")
            return
        db = get_session()
        try:
            if self.selected_id:
                user = db.query(User).get(self.selected_id)
            else:
                if db.query(User).filter_by(username=username).first():
                    self.status_label.configure(text="Username already exists.", text_color="#ea4335")
                    return
                user = User()
                db.add(user)
            user.username = username
            user.full_name = self.entries["full_name"].get().strip()
            user.role = self.role_var.get()
            if password:
                user.password_hash = AuthManager.hash_password(password)
            db.commit()
            self.status_label.configure(text="Saved.", text_color="#34a853")
            self._load()
        except Exception as e:
            db.rollback()
            self.status_label.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

    def _toggle_active(self):
        if not self.selected_id:
            return
        db = get_session()
        try:
            user = db.query(User).get(self.selected_id)
            if user:
                if user.id == AuthManager.current_user().id:
                    messagebox.showwarning("Warning", "Cannot deactivate yourself.")
                    return
                user.is_active = not user.is_active
                db.commit()
            self._load()
        finally:
            db.close()

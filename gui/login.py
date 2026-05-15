import customtkinter as ctk
from auth.auth_manager import AuthManager


class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("School Uniform Billing - Login")
        self.geometry("440x520")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._center()
        self._build()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 440) // 2
        y = (self.winfo_screenheight() - 520) // 2
        self.geometry(f"440x520+{x}+{y}")

    def _build(self):
        # Card frame
        card = ctk.CTkFrame(self, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88, relheight=0.88)

        ctk.CTkLabel(card, text="", height=20).pack()
        ctk.CTkLabel(card, text="🎓", font=ctk.CTkFont(size=48)).pack()
        ctk.CTkLabel(card, text="School Uniform Billing",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(6, 2))
        ctk.CTkLabel(card, text="Sign in to continue",
                     font=ctk.CTkFont(size=13), text_color="gray").pack(pady=(0, 20))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=30)

        ctk.CTkLabel(form, text="Username", anchor="w").pack(fill="x")
        self.username_entry = ctk.CTkEntry(form, placeholder_text="Enter username",
                                            height=40, corner_radius=8)
        self.username_entry.pack(fill="x", pady=(2, 12))

        ctk.CTkLabel(form, text="Password", anchor="w").pack(fill="x")
        self.password_entry = ctk.CTkEntry(form, placeholder_text="Enter password",
                                            show="*", height=40, corner_radius=8)
        self.password_entry.pack(fill="x", pady=(2, 12))

        ctk.CTkLabel(form, text="Role", anchor="w").pack(fill="x")
        self.role_var = ctk.StringVar(value="accountant")
        role_frame = ctk.CTkFrame(form, fg_color="transparent")
        role_frame.pack(fill="x", pady=(2, 20))
        ctk.CTkRadioButton(role_frame, text="Accountant", variable=self.role_var,
                           value="accountant").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(role_frame, text="Admin", variable=self.role_var,
                           value="admin").pack(side="left")

        self.error_label = ctk.CTkLabel(form, text="", text_color="#ea4335", font=ctk.CTkFont(size=12))
        self.error_label.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(form, text="Sign In", height=42, corner_radius=8,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._login).pack(fill="x")

        self.username_entry.focus()
        self.password_entry.bind("<Return>", lambda e: self._login())

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            self.error_label.configure(text="Username and password are required.")
            return
        success, msg = AuthManager.login(username, password)
        if success:
            user = AuthManager.current_user()
            if user.role != self.role_var.get():
                AuthManager.logout()
                self.error_label.configure(text="Role mismatch. Please select the correct role.")
                return
            self.destroy()
            self.on_success()
        else:
            self.error_label.configure(text=msg)

import customtkinter as ctk
from tkinter import messagebox
from database.database import get_session, get_shop_settings
from database.models import ShopSettings


class ShopSettingsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()
        self._load()

    def _build(self):
        ctk.CTkLabel(self, text="Shop / Report Settings",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self, text="These details appear on every printed bill / PDF.",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", pady=(0, 16))

        # Scrollable card so it works on smaller screens
        card = ctk.CTkScrollableFrame(self)
        card.pack(fill="both", expand=True)

        fields = [
            ("Shop / Business Name",    "shop_name",      False),
            ("Address Line 1",          "address_line1",  False),
            ("Address Line 2",          "address_line2",  False),
            ("Phone",                   "phone",          False),
            ("Email",                   "email",          False),
            ("GST Number",              "gst_number",     False),
            ("Bill Number Prefix\n(e.g. INV, BILL, SV)", "bill_prefix", False),
            ("Footer Note (on bill)",   "footer_note",    True),   # True = multiline
        ]

        self._entries = {}
        for label, key, multiline in fields:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=(0, 12))
            ctk.CTkLabel(row, text=label, anchor="w",
                         font=ctk.CTkFont(size=12, weight="bold"), width=240).pack(side="left", anchor="n", pady=4)
            if multiline:
                w = ctk.CTkTextbox(row, height=64, corner_radius=6)
                w.pack(side="left", fill="x", expand=True)
            else:
                w = ctk.CTkEntry(row, height=38, corner_radius=6)
                w.pack(side="left", fill="x", expand=True)
            self._entries[key] = (w, multiline)

        # Save button
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(8, 16))
        ctk.CTkButton(btn_row, text="Save Settings", height=42,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._save).pack(side="left")
        self.status = ctk.CTkLabel(btn_row, text="", font=ctk.CTkFont(size=12))
        self.status.pack(side="left", padx=16)

    def _set(self, key, value):
        widget, multiline = self._entries[key]
        if multiline:
            widget.delete("0.0", "end")
            widget.insert("0.0", value or "")
        else:
            widget.delete(0, "end")
            widget.insert(0, value or "")

    def _get(self, key) -> str:
        widget, multiline = self._entries[key]
        if multiline:
            return widget.get("0.0", "end").strip()
        return widget.get().strip()

    def _load(self):
        s = get_shop_settings()
        if not s:
            return
        self._set("shop_name",    s.shop_name)
        self._set("address_line1", s.address_line1)
        self._set("address_line2", s.address_line2)
        self._set("phone",        s.phone)
        self._set("email",        s.email)
        self._set("gst_number",   s.gst_number)
        self._set("bill_prefix",  s.bill_prefix)
        self._set("footer_note",  s.footer_note)

    def _save(self):
        db = get_session()
        try:
            s = db.query(ShopSettings).first()
            if not s:
                s = ShopSettings()
                db.add(s)
            s.shop_name    = self._get("shop_name")
            s.address_line1 = self._get("address_line1")
            s.address_line2 = self._get("address_line2")
            s.phone        = self._get("phone")
            s.email        = self._get("email")
            s.gst_number   = self._get("gst_number")
            s.bill_prefix  = self._get("bill_prefix")
            s.footer_note  = self._get("footer_note")
            db.commit()
            self.status.configure(text="Saved successfully.", text_color="#34a853")
        except Exception as e:
            db.rollback()
            self.status.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

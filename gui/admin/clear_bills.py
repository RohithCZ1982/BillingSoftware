import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy import extract, func
from database.database import get_session
from database.models import Bill, BillItem
from utils.backup import create_backup, default_backup_name


class ClearBillsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._backup_taken = False
        self._build()
        self._load_years()

    def _build(self):
        ctk.CTkLabel(self, text="Clear Bills by Year",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self, text="Permanently delete all bills for a selected year.",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", pady=(0, 20))

        card = ctk.CTkFrame(self, corner_radius=12)
        card.pack(fill="x", ipadx=10, ipady=10)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        # ── Year selector ─────────────────────────────────────────────────────
        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(row1, text="Select Year:", font=ctk.CTkFont(size=13),
                     width=120, anchor="w").pack(side="left")
        self.year_var = ctk.StringVar()
        self.year_combo = ctk.CTkComboBox(row1, variable=self.year_var,
                                           width=160, state="readonly")
        self.year_combo.pack(side="left", padx=(0, 16))
        self.count_label = ctk.CTkLabel(row1, text="", font=ctk.CTkFont(size=12),
                                         text_color="gray")
        self.count_label.pack(side="left")
        self.year_combo.configure(command=self._on_year_change)

        # ── Warning box ───────────────────────────────────────────────────────
        warn = ctk.CTkFrame(inner, fg_color="#3a1a1a", corner_radius=8)
        warn.pack(fill="x", pady=(0, 16))
        wp = ctk.CTkFrame(warn, fg_color="transparent")
        wp.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(wp, text="⚠️  Important — Read before clearing",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#fbbc04").pack(anchor="w", pady=(0, 6))
        for line in [
            "• Deleted bills cannot be recovered from the application.",
            "• PDF files in the bills/ folder are NOT deleted.",
            "• Take a database backup before clearing.",
        ]:
            ctk.CTkLabel(wp, text=line, font=ctk.CTkFont(size=11),
                         text_color="#ffcccc", anchor="w").pack(anchor="w")

        # ── Backup strip ──────────────────────────────────────────────────────
        bk_row = ctk.CTkFrame(inner, fg_color="transparent")
        bk_row.pack(fill="x", pady=(0, 20))
        ctk.CTkButton(bk_row, text="💾  Take Backup Now", width=180, height=38,
                      fg_color="#1a73e8", hover_color="#1557b0",
                      command=self._do_backup).pack(side="left", padx=(0, 16))
        self.backup_status = ctk.CTkLabel(bk_row, text="No backup taken yet.",
                                           font=ctk.CTkFont(size=11), text_color="gray")
        self.backup_status.pack(side="left")

        # ── Delete button ─────────────────────────────────────────────────────
        ctk.CTkFrame(inner, height=1, fg_color="#444").pack(fill="x", pady=(0, 16))
        del_row = ctk.CTkFrame(inner, fg_color="transparent")
        del_row.pack(fill="x")
        self.delete_btn = ctk.CTkButton(
            del_row, text="🗑  Clear Bills for Selected Year",
            width=240, height=42,
            fg_color="#ea4335", hover_color="#c62828",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._confirm_delete,
            state="disabled",
        )
        self.delete_btn.pack(side="left")
        ctk.CTkLabel(del_row,
                     text="  Button enabled only after a backup is taken.",
                     font=ctk.CTkFont(size=11), text_color="gray").pack(side="left")

        self.result_label = ctk.CTkLabel(inner, text="",
                                          font=ctk.CTkFont(size=12), wraplength=560)
        self.result_label.pack(anchor="w", pady=(14, 0))

    # ─────────────────────────────────────────────────────────────────────────

    def _load_years(self):
        db = get_session()
        rows = (
            db.query(extract("year", Bill.bill_date).label("yr"), func.count(Bill.id))
            .group_by("yr")
            .order_by("yr")
            .all()
        )
        db.close()
        years = [str(int(r[0])) for r in rows if r[0]]
        if years:
            self.year_combo.configure(values=years)
            self.year_var.set(years[-1])          # default to most recent year
            self._on_year_change(years[-1])
        else:
            self.year_combo.configure(values=["(no bills)"])
            self.year_var.set("(no bills)")
            self.count_label.configure(text="No bills found in the database.")

    def _on_year_change(self, _=None):
        year = self.year_var.get()
        if not year.isdigit():
            return
        db = get_session()
        count = (
            db.query(func.count(Bill.id))
            .filter(extract("year", Bill.bill_date) == int(year))
            .scalar()
        )
        db.close()
        self.count_label.configure(
            text=f"{count} bill(s) found for {year}",
            text_color="#fbbc04" if count else "gray"
        )
        self.result_label.configure(text="")

    def _do_backup(self):
        name = default_backup_name()
        ok, msg = create_backup(name)
        if ok:
            self._backup_taken = True
            self.backup_status.configure(
                text=f"✓  Backup saved: {name}.db", text_color="#34a853"
            )
            self.delete_btn.configure(state="normal")
        else:
            self.backup_status.configure(text=f"Backup failed: {msg}", text_color="#ea4335")

    def _confirm_delete(self):
        year = self.year_var.get()
        if not year.isdigit():
            return

        # Gate 1 — backup check
        if not self._backup_taken:
            messagebox.showwarning("Backup Required",
                                   "Please take a backup before clearing bills.")
            return

        # Gate 2 — first confirmation
        if not messagebox.askyesno(
            "Confirm Clear",
            f"You are about to permanently delete ALL bills for {year}.\n\n"
            f"This action cannot be undone.\n\n"
            f"Are you sure you want to continue?",
        ):
            return

        # Gate 3 — type the year to confirm
        confirm_dlg = ctk.CTkInputDialog(
            text=f"Type  {year}  to confirm deletion:",
            title="Final Confirmation"
        )
        typed = confirm_dlg.get_input()
        if typed is None or typed.strip() != year:
            self.result_label.configure(
                text="Cancelled — year did not match.", text_color="gray"
            )
            return

        # ── Delete ────────────────────────────────────────────────────────────
        db = get_session()
        try:
            bills = (
                db.query(Bill)
                .filter(extract("year", Bill.bill_date) == int(year))
                .all()
            )
            bill_ids = [b.id for b in bills]
            if not bill_ids:
                self.result_label.configure(text="No bills found for that year.",
                                            text_color="gray")
                return

            db.query(BillItem).filter(BillItem.bill_id.in_(bill_ids)).delete(
                synchronize_session=False
            )
            db.query(Bill).filter(Bill.id.in_(bill_ids)).delete(
                synchronize_session=False
            )
            db.commit()

            self.result_label.configure(
                text=f"✓  {len(bill_ids)} bill(s) for {year} deleted successfully.",
                text_color="#34a853"
            )
            # Reset button state and refresh counts
            self._backup_taken = False
            self.delete_btn.configure(state="disabled")
            self.backup_status.configure(text="No backup taken yet.", text_color="gray")
            self._load_years()

        except Exception as e:
            db.rollback()
            self.result_label.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

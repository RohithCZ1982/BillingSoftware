import csv
import os
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, date
from calendar import monthrange
from sqlalchemy import func
from database.database import get_session
from database.models import Bill, School, SchoolClass, User


# ── All available columns ────────────────────────────────────────────────────
ALL_COLUMNS = [
    ("bill_number",   "Bill No",        90),
    ("bill_date",     "Date",           110),
    ("student_name",  "Student",        140),
    ("student_section","Section",        60),
    ("parent_name",   "Parent",         120),
    ("parent_phone",  "Phone",           100),
    ("school_name",   "School",         160),
    ("class_name",    "Class",           70),
    ("item_count",    "Items",           50),
    ("subtotal",      "Subtotal (₹)",   100),
    ("discount_amt",  "Discount (₹)",   100),
    ("grand_total",   "Total (₹)",      100),
    ("created_by",    "Created By",     100),
]

DEFAULT_ON = {"bill_number", "bill_date", "student_name",
              "school_name", "class_name", "grand_total"}


class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._rows = []          # raw dicts for CSV export
        self._build()

    # ─────────────────────────────────────────────────────────────────────────
    #  BUILD UI
    # ─────────────────────────────────────────────────────────────────────────
    def _build(self):
        ctk.CTkLabel(self, text="Sales Reports",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 12))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ── Left sidebar: controls ────────────────────────────────────────────
        left = ctk.CTkScrollableFrame(body, width=210, label_text="Report Options")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Report type
        ctk.CTkLabel(left, text="Report Type", font=ctk.CTkFont(weight="bold"),
                     anchor="w").pack(fill="x", pady=(8, 4))
        self.report_type = ctk.StringVar(value="Daily")
        for t in ("Daily", "Monthly"):
            ctk.CTkRadioButton(left, text=t, variable=self.report_type,
                               value=t, command=self._on_type_change).pack(anchor="w", pady=2)

        ctk.CTkFrame(left, height=1, fg_color="#444").pack(fill="x", pady=10)

        # Date controls
        self.date_label = ctk.CTkLabel(left, text="Date (dd-mm-yyyy)",
                                        font=ctk.CTkFont(weight="bold"), anchor="w")
        self.date_label.pack(fill="x")
        self.date_entry = ctk.CTkEntry(left, placeholder_text="dd-mm-yyyy", height=34)
        self.date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        self.date_entry.pack(fill="x", pady=(2, 4))

        # Month / Year (hidden by default)
        self.month_label = ctk.CTkLabel(left, text="Month & Year",
                                         font=ctk.CTkFont(weight="bold"), anchor="w")
        self.month_var = ctk.StringVar(value=date.today().strftime("%m"))
        self.month_combo = ctk.CTkComboBox(left, variable=self.month_var, width=90,
                                            values=[f"{m:02d}" for m in range(1, 13)])
        self.year_var = ctk.StringVar(value=str(date.today().year))
        self.year_combo = ctk.CTkComboBox(left, variable=self.year_var, width=90,
                                           values=[str(y) for y in range(2020, 2036)])

        # School filter
        ctk.CTkFrame(left, height=1, fg_color="#444").pack(fill="x", pady=10)
        ctk.CTkLabel(left, text="School Filter", font=ctk.CTkFont(weight="bold"),
                     anchor="w").pack(fill="x")
        self.school_var = ctk.StringVar(value="All Schools")
        self.school_combo = ctk.CTkComboBox(left, variable=self.school_var, width=190)
        self.school_combo.pack(fill="x", pady=(2, 0))
        self._load_schools()

        ctk.CTkFrame(left, height=1, fg_color="#444").pack(fill="x", pady=10)

        # Column selector
        ctk.CTkLabel(left, text="Columns", font=ctk.CTkFont(weight="bold"),
                     anchor="w").pack(fill="x", pady=(0, 4))

        sel_row = ctk.CTkFrame(left, fg_color="transparent")
        sel_row.pack(fill="x", pady=(0, 6))
        ctk.CTkButton(sel_row, text="All", width=60, height=26,
                      command=self._select_all_cols).pack(side="left", padx=(0, 4))
        ctk.CTkButton(sel_row, text="None", width=60, height=26,
                      fg_color="gray", command=self._deselect_all_cols).pack(side="left")

        self._col_vars = {}
        for key, label, _ in ALL_COLUMNS:
            var = ctk.BooleanVar(value=(key in DEFAULT_ON))
            cb = ctk.CTkCheckBox(left, text=label, variable=var, height=24)
            cb.pack(anchor="w", pady=1)
            self._col_vars[key] = var

        ctk.CTkFrame(left, height=1, fg_color="#444").pack(fill="x", pady=10)

        # Generate + export
        ctk.CTkButton(left, text="Generate Report", height=38,
                      font=ctk.CTkFont(weight="bold"),
                      command=self._generate).pack(fill="x", pady=(0, 6))
        ctk.CTkButton(left, text="Export CSV", height=34, fg_color="#34a853",
                      hover_color="#2d8a47", command=self._export_csv).pack(fill="x")

        # ── Right: table + summary ────────────────────────────────────────────
        right = ctk.CTkFrame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        # Treeview
        tree_frame = ctk.CTkFrame(right, fg_color="transparent")
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Report.Treeview", background="#2b2b3b",
                        fieldbackground="#2b2b3b", foreground="white", rowheight=26)
        style.configure("Report.Treeview.Heading", background="#1a73e8",
                        foreground="white", font=("Helvetica", 10, "bold"))
        style.map("Report.Treeview", background=[("selected", "#1a73e8")])

        self.tree = ttk.Treeview(tree_frame, show="headings",
                                  selectmode="browse", style="Report.Treeview")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Summary strip
        summary_frame = ctk.CTkFrame(right, fg_color="#1e1e2e", corner_radius=8)
        summary_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)
        summary_inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        summary_inner.pack(fill="x", padx=16, pady=8)

        self._summary_labels = {}
        for i, (key, label) in enumerate([
            ("count",   "Total Bills"),
            ("revenue", "Total Revenue"),
            ("avg",     "Avg Bill Value"),
            ("max",     "Highest Bill"),
            ("min",     "Lowest Bill"),
        ]):
            col = ctk.CTkFrame(summary_inner, fg_color="transparent")
            col.pack(side="left", expand=True)
            ctk.CTkLabel(col, text=label, font=ctk.CTkFont(size=10),
                         text_color="gray").pack()
            lbl = ctk.CTkLabel(col, text="—",
                               font=ctk.CTkFont(size=14, weight="bold"))
            lbl.pack()
            self._summary_labels[key] = lbl

        # Init for monthly mode (hidden initially)
        self._on_type_change()

    # ─────────────────────────────────────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────────────────────────────────────
    def _on_type_change(self):
        if self.report_type.get() == "Daily":
            self.month_label.pack_forget()
            self.month_combo.pack_forget()
            self.year_combo.pack_forget()
            self.date_label.pack(fill="x")
            self.date_entry.pack(fill="x", pady=(2, 4))
        else:
            self.date_label.pack_forget()
            self.date_entry.pack_forget()
            self.month_label.pack(fill="x")
            self.month_combo.pack(fill="x", pady=(2, 2))
            self.year_combo.pack(fill="x", pady=(0, 4))

    def _load_schools(self):
        db = get_session()
        schools = db.query(School).order_by(School.name).all()
        names = ["All Schools"] + [s.name for s in schools]
        self._school_map = {"All Schools": None}
        self._school_map.update({s.name: s.id for s in schools})
        db.close()
        self.school_combo.configure(values=names)

    def _select_all_cols(self):
        for v in self._col_vars.values():
            v.set(True)

    def _deselect_all_cols(self):
        for v in self._col_vars.values():
            v.set(False)

    def _active_columns(self):
        return [(k, lbl, w) for k, lbl, w in ALL_COLUMNS if self._col_vars[k].get()]

    # ─────────────────────────────────────────────────────────────────────────
    #  DATA FETCH
    # ─────────────────────────────────────────────────────────────────────────
    def _fetch_bills(self):
        db = get_session()
        q = db.query(Bill)

        # Date filter
        if self.report_type.get() == "Daily":
            try:
                d = datetime.strptime(self.date_entry.get().strip(), "%d-%m-%Y")
                q = q.filter(
                    Bill.bill_date >= d.replace(hour=0, minute=0, second=0),
                    Bill.bill_date <= d.replace(hour=23, minute=59, second=59)
                )
            except ValueError:
                db.close()
                messagebox.showerror("Error", "Invalid date format. Use dd-mm-yyyy")
                return []
        else:
            try:
                month = int(self.month_var.get())
                year  = int(self.year_var.get())
                _, last_day = monthrange(year, month)
                start = datetime(year, month, 1, 0, 0, 0)
                end   = datetime(year, month, last_day, 23, 59, 59)
                q = q.filter(Bill.bill_date >= start, Bill.bill_date <= end)
            except Exception:
                db.close()
                messagebox.showerror("Error", "Invalid month/year.")
                return []

        # School filter
        school_id = self._school_map.get(self.school_var.get())
        if school_id:
            q = q.filter(Bill.school_id == school_id)

        bills = q.order_by(Bill.bill_date).all()

        rows = []
        for b in bills:
            discount_amt = b.subtotal - b.grand_total
            rows.append({
                "bill_number":     b.bill_number,
                "bill_date":       b.bill_date.strftime("%d-%m-%Y %H:%M") if b.bill_date else "",
                "student_name":    b.student_name,
                "student_section": b.student_section or "",
                "parent_name":     b.parent_name or "",
                "parent_phone":    b.parent_phone or "",
                "school_name":     b.school.name if b.school else "",
                "class_name":      b.school_class.name if b.school_class else "",
                "item_count":      str(len(b.items)),
                "subtotal":        f"{b.subtotal:.2f}",
                "discount_amt":    f"{discount_amt:.2f}",
                "grand_total":     f"{b.grand_total:.2f}",
                "created_by":      (b.created_by_user.username if b.created_by_user else ""),
                # raw for summary
                "_grand_total_raw": b.grand_total,
            })
        db.close()
        return rows

    # ─────────────────────────────────────────────────────────────────────────
    #  GENERATE
    # ─────────────────────────────────────────────────────────────────────────
    def _generate(self):
        active_cols = self._active_columns()
        if not active_cols:
            messagebox.showwarning("Columns", "Select at least one column.")
            return

        rows = self._fetch_bills()
        self._rows = rows

        # Rebuild treeview columns
        col_keys = [k for k, _, _ in active_cols]
        self.tree.configure(columns=col_keys)
        for k, lbl, w in active_cols:
            self.tree.heading(k, text=lbl,
                              command=lambda c=k: self._sort_by(c))
            self.tree.column(k, width=w, anchor="w", stretch=True)

        # Clear and fill rows
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            values = [row[k] for k in col_keys]
            self.tree.insert("", "end", values=values)

        # Alternating row colours
        self.tree.tag_configure("odd",  background="#2b2b3b")
        self.tree.tag_configure("even", background="#25253a")
        for i, iid in enumerate(self.tree.get_children()):
            self.tree.item(iid, tags=("even" if i % 2 == 0 else "odd",))

        # Update summary
        self._update_summary(rows)

    def _update_summary(self, rows):
        totals = [r["_grand_total_raw"] for r in rows]
        count  = len(totals)
        if count == 0:
            for lbl in self._summary_labels.values():
                lbl.configure(text="—")
            self._summary_labels["count"].configure(text="0")
            return
        revenue = sum(totals)
        avg     = revenue / count
        hi      = max(totals)
        lo      = min(totals)
        self._summary_labels["count"].configure(text=str(count))
        self._summary_labels["revenue"].configure(text=f"₹ {revenue:,.2f}")
        self._summary_labels["avg"].configure(text=f"₹ {avg:,.2f}")
        self._summary_labels["max"].configure(text=f"₹ {hi:,.2f}")
        self._summary_labels["min"].configure(text=f"₹ {lo:,.2f}")

    # ─────────────────────────────────────────────────────────────────────────
    #  SORT
    # ─────────────────────────────────────────────────────────────────────────
    def _sort_by(self, col_key):
        items = [(self.tree.set(iid, col_key), iid)
                 for iid in self.tree.get_children()]
        try:
            items.sort(key=lambda x: float(x[0].replace(",", "")) if x[0].replace(",","").replace(".","").isdigit() else x[0].lower())
        except Exception:
            items.sort(key=lambda x: x[0].lower())
        for i, (_, iid) in enumerate(items):
            self.tree.move(iid, "", i)

    # ─────────────────────────────────────────────────────────────────────────
    #  EXPORT CSV
    # ─────────────────────────────────────────────────────────────────────────
    def _export_csv(self):
        if not self._rows:
            messagebox.showinfo("Export", "Generate a report first.")
            return

        active_cols = self._active_columns()
        col_keys    = [k for k, _, _ in active_cols]
        col_labels  = [lbl for _, lbl, _ in active_cols]

        default_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=default_name,
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(col_labels)
                for row in self._rows:
                    writer.writerow([row[k] for k in col_keys])
            messagebox.showinfo("Export", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database.database import get_session
from database.models import Bill, School, SchoolClass, BillItem
from utils.printer import print_pdf, open_pdf


class BillHistoryFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()
        self._load()

    def _build(self):
        ctk.CTkLabel(self, text="Bill History",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 12))

        # Filters
        filters = ctk.CTkFrame(self, fg_color="transparent")
        filters.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(filters, text="Search:").pack(side="left", padx=(0, 4))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        ctk.CTkEntry(filters, textvariable=self.search_var,
                     placeholder_text="Bill no / student / phone...",
                     width=220).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filters, text="From:").pack(side="left", padx=(0, 4))
        self.from_date = ctk.CTkEntry(filters, width=100, placeholder_text="dd-mm-yyyy")
        self.from_date.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(filters, text="To:").pack(side="left", padx=(0, 4))
        self.to_date = ctk.CTkEntry(filters, width=100, placeholder_text="dd-mm-yyyy")
        self.to_date.pack(side="left", padx=(0, 8))

        ctk.CTkButton(filters, text="Filter", width=70, command=self._load).pack(side="left")
        ctk.CTkButton(filters, text="Clear", width=70, fg_color="gray",
                      command=self._clear_filters).pack(side="left", padx=(6, 0))

        # Split view
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True)
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)

        # ── Table ─────────────────────────────────────────────────────────────
        left = ctk.CTkFrame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("History.Treeview", background="#2b2b3b", fieldbackground="#2b2b3b",
                        foreground="white", rowheight=26)
        style.configure("History.Treeview.Heading", background="#1a73e8", foreground="white",
                        font=("Helvetica", 10, "bold"))
        style.map("History.Treeview", background=[("selected", "#1a73e8")])

        cols = ("Bill No", "Date", "Student", "School", "Class", "Total")
        self.tree = ttk.Treeview(left, columns=cols, show="headings",
                                  selectmode="browse", style="History.Treeview")
        widths = [110, 90, 150, 160, 80, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor="w")
        scroll = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scroll.pack(side="right", fill="y", pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        summary = ctk.CTkFrame(left, fg_color="#1e1e2e", corner_radius=6)
        summary.pack(fill="x", padx=8, pady=(0, 8))
        self.summary_label = ctk.CTkLabel(summary, text="",
                                           font=ctk.CTkFont(size=11))
        self.summary_label.pack(pady=4, padx=8)

        # ── Detail panel ──────────────────────────────────────────────────────
        right = ctk.CTkFrame(content)
        right.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(right, text="Bill Details",
                     font=ctk.CTkFont(weight="bold")).pack(pady=(10, 4))

        self.detail_box = ctk.CTkTextbox(right, state="disabled")
        self.detail_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        action_row = ctk.CTkFrame(right, fg_color="transparent")
        action_row.pack(fill="x", padx=8, pady=(0, 10))
        self.open_btn = ctk.CTkButton(action_row, text="Open PDF", state="disabled",
                                       command=self._open_pdf)
        self.open_btn.pack(side="left", padx=(0, 6))
        self.print_btn = ctk.CTkButton(action_row, text="Print", state="disabled",
                                        fg_color="#34a853", hover_color="#2d8a47",
                                        command=self._print)
        self.print_btn.pack(side="left")

        self._bill_map = {}   # tree iid -> bill_id
        self._selected_bill_id = None
        self._sort_col = "Date"
        self._sort_reverse = True

    def _clear_filters(self):
        self.search_var.set("")
        self.from_date.delete(0, "end")
        self.to_date.delete(0, "end")
        self._load()

    def _load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._bill_map.clear()

        db = get_session()
        q = db.query(Bill)

        s = self.search_var.get().strip()
        if s:
            q = q.filter(
                Bill.bill_number.ilike(f"%{s}%") |
                Bill.student_name.ilike(f"%{s}%") |
                Bill.parent_phone.ilike(f"%{s}%")
            )
        try:
            from_str = self.from_date.get().strip()
            if from_str:
                q = q.filter(Bill.bill_date >= datetime.strptime(from_str, "%d-%m-%Y"))
            to_str = self.to_date.get().strip()
            if to_str:
                to_dt = datetime.strptime(to_str, "%d-%m-%Y")
                to_dt = to_dt.replace(hour=23, minute=59, second=59)
                q = q.filter(Bill.bill_date <= to_dt)
        except ValueError:
            pass

        bills = q.order_by(Bill.bill_date.desc()).all()
        total_amount = 0.0
        for bill in bills:
            school_name = bill.school.name if bill.school else ""
            class_name = bill.school_class.name if bill.school_class else ""
            date_str = bill.bill_date.strftime("%d-%m-%Y") if bill.bill_date else ""
            iid = self.tree.insert("", "end", values=(
                bill.bill_number, date_str, bill.student_name,
                school_name, class_name, f"₹{bill.grand_total:.2f}"
            ))
            self._bill_map[iid] = bill.id
            total_amount += bill.grand_total

        self.summary_label.configure(
            text=f"{len(bills)} bill(s)  |  Total Revenue: ₹{total_amount:.2f}"
        )
        db.close()

    def _on_select(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        bill_id = self._bill_map.get(sel[0])
        if not bill_id:
            return
        self._selected_bill_id = bill_id
        self._show_detail(bill_id)
        self.open_btn.configure(state="normal")
        self.print_btn.configure(state="normal")

    def _show_detail(self, bill_id):
        db = get_session()
        bill = db.query(Bill).get(bill_id)
        if not bill:
            db.close()
            return

        lines = []
        lines.append(f"Bill Number : {bill.bill_number}")
        lines.append(f"Date        : {bill.bill_date.strftime('%d-%m-%Y %I:%M %p') if bill.bill_date else ''}")
        lines.append(f"School      : {bill.school.name if bill.school else ''}")
        lines.append(f"Class       : {bill.school_class.name if bill.school_class else ''}")
        lines.append(f"Student     : {bill.student_name}")
        lines.append(f"Section     : {bill.student_section or ''}")
        lines.append(f"Parent      : {bill.parent_name or ''}")
        lines.append(f"Phone       : {bill.parent_phone or ''}")
        lines.append("-" * 50)
        lines.append(f"{'Item':<22} {'Qty':>4} {'Price':>8} {'Total':>9}")
        lines.append("-" * 50)
        for item in bill.items:
            lines.append(
                f"{item.item_name:<22} {item.quantity:>4} {item.unit_price:>8.2f} {item.total_price:>9.2f}"
            )
        lines.append("-" * 50)
        lines.append(f"{'Subtotal':>36} : ₹{bill.subtotal:.2f}")
        if bill.discount_value:
            dtype = f"({bill.discount_value}%)" if bill.discount_type == "percent" else ""
            lines.append(f"{'Discount ' + dtype:>36} : ₹{bill.subtotal - bill.grand_total:.2f}")
        lines.append(f"{'GRAND TOTAL':>36} : ₹{bill.grand_total:.2f}")
        if bill.notes:
            lines.append(f"\nNotes: {bill.notes}")
        self._pdf_path = bill.pdf_path
        db.close()

        self.detail_box.configure(state="normal")
        self.detail_box.delete("0.0", "end")
        self.detail_box.insert("0.0", "\n".join(lines))
        self.detail_box.configure(state="disabled")

    def _sort(self, col):
        self._sort_reverse = not self._sort_reverse if self._sort_col == col else False
        self._sort_col = col
        rows = [(self.tree.set(iid, col), iid) for iid in self.tree.get_children()]
        rows.sort(reverse=self._sort_reverse)
        for i, (_, iid) in enumerate(rows):
            self.tree.move(iid, "", i)

    def _open_pdf(self):
        if hasattr(self, "_pdf_path") and self._pdf_path:
            open_pdf(self._pdf_path)
        else:
            messagebox.showinfo("No PDF", "PDF not found for this bill.")

    def _print(self):
        if hasattr(self, "_pdf_path") and self._pdf_path:
            ok, msg = print_pdf(self._pdf_path)
            messagebox.showinfo("Print", msg)
        else:
            messagebox.showinfo("No PDF", "PDF not found for this bill.")

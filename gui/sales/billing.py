import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from database.database import get_session
from database.models import School, SchoolClass, UniformItem, Bill, BillItem
from auth.auth_manager import AuthManager
from reports.pdf_generator import generate_bill_pdf
from utils.printer import print_pdf, open_pdf
from database.database import get_shop_settings


class BillingFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._schools = {}
        self._classes = {}
        self._bill_rows = []        # list of dicts: {name,size,category,qty_var,price_var,total_var,frame}
        self._last_bill_id = None
        self._build()
        self._load_schools()

    # ─────────────────────────────────────────────────────────────────────────
    #  UI BUILD
    # ─────────────────────────────────────────────────────────────────────────
    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(top, text="New Bill / Sales",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="Clear", width=80, fg_color="gray",
                      command=self._clear_bill).pack(side="right")

        # Main 2-column layout
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)

        # ── Left column ───────────────────────────────────────────────────────
        left = ctk.CTkFrame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # School / Class selectors
        sel_frame = ctk.CTkFrame(left, fg_color="transparent")
        sel_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(sel_frame, text="School:", width=60, anchor="w").grid(row=0, column=0, sticky="w")
        self.school_var = ctk.StringVar()
        self.school_combo = ctk.CTkComboBox(sel_frame, variable=self.school_var, width=250,
                                             command=self._on_school_change)
        self.school_combo.grid(row=0, column=1, padx=(4, 16))

        ctk.CTkLabel(sel_frame, text="Class:", width=50, anchor="w").grid(row=0, column=2, sticky="w")
        self.class_var = ctk.StringVar()
        self.class_combo = ctk.CTkComboBox(sel_frame, variable=self.class_var, width=140,
                                            command=self._on_class_change)
        self.class_combo.grid(row=0, column=3, padx=(4, 16))

        ctk.CTkLabel(sel_frame, text="Gender:", width=55, anchor="w").grid(row=0, column=4, sticky="w")
        self.gender_var = ctk.StringVar(value="Boy")
        gender_seg = ctk.CTkSegmentedButton(
            sel_frame, values=["Boy", "Girl", "Both"],
            variable=self.gender_var, command=self._on_gender_change,
            width=160
        )
        gender_seg.grid(row=0, column=5, padx=(4, 0))

        # Items area header
        item_header = ctk.CTkFrame(left, fg_color="#1a73e8", corner_radius=0)
        item_header.pack(fill="x", padx=10)
        for text, w in [("#", 30), ("Item Name", 160), ("Size", 60), ("Cat", 80),
                        ("Qty", 50), ("Unit Price", 90), ("Total", 90), ("Del", 40)]:
            ctk.CTkLabel(item_header, text=text, width=w, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="white").pack(side="left", padx=2)

        # Scrollable items list
        self.items_frame = ctk.CTkScrollableFrame(left, height=300)
        self.items_frame.pack(fill="both", expand=True, padx=10, pady=(0, 0))

        # Add extra item button
        add_btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        add_btn_frame.pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(add_btn_frame, text="+ Add Item", width=120,
                      command=self._add_blank_row).pack(side="left")

        # Totals strip
        totals = ctk.CTkFrame(left, fg_color="#1e1e2e", corner_radius=8)
        totals.pack(fill="x", padx=10, pady=8)

        tf = ctk.CTkFrame(totals, fg_color="transparent")
        tf.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(tf, text="Subtotal:").grid(row=0, column=0, sticky="w")
        self.subtotal_var = ctk.StringVar(value="₹ 0.00")
        ctk.CTkLabel(tf, textvariable=self.subtotal_var,
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="e", padx=(20, 40))

        ctk.CTkLabel(tf, text="Discount:").grid(row=0, column=2, sticky="w")
        self.discount_type_var = ctk.StringVar(value="flat")
        disc_frame = ctk.CTkFrame(tf, fg_color="transparent")
        disc_frame.grid(row=0, column=3, padx=(4, 0))
        ctk.CTkRadioButton(disc_frame, text="₹", variable=self.discount_type_var,
                           value="flat", command=self._recalc).pack(side="left")
        ctk.CTkRadioButton(disc_frame, text="%", variable=self.discount_type_var,
                           value="percent", command=self._recalc).pack(side="left", padx=(8, 0))
        self.discount_entry = ctk.CTkEntry(disc_frame, width=70, placeholder_text="0")
        self.discount_entry.pack(side="left", padx=(8, 0))
        self.discount_entry.bind("<KeyRelease>", lambda e: self._recalc())

        ctk.CTkLabel(tf, text="GRAND TOTAL:", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#1a73e8").grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.grand_total_var = ctk.StringVar(value="₹ 0.00")
        ctk.CTkLabel(tf, textvariable=self.grand_total_var,
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#1a73e8").grid(row=1, column=2, columnspan=2, sticky="e", pady=(8, 0))

        # ── Right column: student info ─────────────────────────────────────────
        right = ctk.CTkFrame(main)
        right.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(right, text="Student Information",
                     font=ctk.CTkFont(weight="bold")).pack(pady=(10, 6))

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(fill="x", padx=14)

        self.student_entries = {}
        fields = [
            ("Student Full Name *", "student_name"),
            ("Section", "student_section"),
            ("Parent Name", "parent_name"),
            ("Parent Phone", "parent_phone"),
        ]
        for label, key in fields:
            ctk.CTkLabel(form, text=label, anchor="w", font=ctk.CTkFont(size=12)).pack(fill="x", pady=(6, 0))
            e = ctk.CTkEntry(form, height=36)
            e.pack(fill="x", pady=(2, 0))
            self.student_entries[key] = e

        ctk.CTkLabel(form, text="Date", anchor="w", font=ctk.CTkFont(size=12)).pack(fill="x", pady=(6, 0))
        self.date_entry = ctk.CTkEntry(form, height=36)
        self.date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.date_entry.pack(fill="x", pady=(2, 0))

        ctk.CTkLabel(form, text="Notes", anchor="w", font=ctk.CTkFont(size=12)).pack(fill="x", pady=(6, 0))
        self.notes_box = ctk.CTkTextbox(form, height=60)
        self.notes_box.pack(fill="x", pady=(2, 0))

        # Action buttons
        btns = ctk.CTkFrame(right, fg_color="transparent")
        btns.pack(fill="x", padx=14, pady=14)
        ctk.CTkButton(btns, text="Save & Generate PDF", height=42,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._save_bill).pack(fill="x", pady=(0, 8))

        row2 = ctk.CTkFrame(btns, fg_color="transparent")
        row2.pack(fill="x")
        self.print_btn = ctk.CTkButton(row2, text="Print", width=100,
                                        fg_color="#34a853", hover_color="#2d8a47",
                                        command=self._print_bill, state="disabled")
        self.print_btn.pack(side="left", padx=(0, 8))
        self.open_pdf_btn = ctk.CTkButton(row2, text="Open PDF", width=110,
                                           fg_color="gray",
                                           command=self._open_pdf_bill, state="disabled")
        self.open_pdf_btn.pack(side="left")

        self.bill_status = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=11),
                                         wraplength=280)
        self.bill_status.pack(padx=14, pady=(4, 0))

    # ─────────────────────────────────────────────────────────────────────────
    #  DATA LOADING
    # ─────────────────────────────────────────────────────────────────────────
    def _load_schools(self):
        db = get_session()
        schools = db.query(School).order_by(School.name).all()
        self._schools = {s.name: s.id for s in schools}
        db.close()
        names = list(self._schools.keys())
        self.school_combo.configure(values=names or ["(No schools)"])
        if names:
            self.school_var.set(names[0])
            self._on_school_change(names[0])

    def _on_school_change(self, _=None):
        school_id = self._schools.get(self.school_var.get())
        if not school_id:
            return
        db = get_session()
        classes = db.query(SchoolClass).filter_by(school_id=school_id).order_by(SchoolClass.name).all()
        self._classes = {c.name: c.id for c in classes}
        db.close()
        names = list(self._classes.keys())
        self.class_combo.configure(values=names or ["(No classes)"])
        if names:
            self.class_var.set(names[0])
            self._on_class_change(names[0])
        else:
            self.class_var.set("")
            self._clear_item_rows()

    def _on_class_change(self, _=None):
        self._load_template_items()

    def _on_gender_change(self, _=None):
        self._load_template_items()

    def _load_template_items(self):
        self._clear_item_rows()
        school_id = self._schools.get(self.school_var.get())
        class_id = self._classes.get(self.class_var.get())
        if not school_id:
            return
        gender = self.gender_var.get()   # "Boy" / "Girl" / "Both"
        db = get_session()
        q = db.query(UniformItem).filter_by(school_id=school_id, is_active=True)
        if class_id:
            q = q.filter(
                (UniformItem.class_id == class_id) | (UniformItem.class_id == None)
            )
        # Gender filter: always include items tagged "Both"; also include the selected gender
        if gender in ("Boy", "Girl"):
            q = q.filter(
                (UniformItem.gender == gender) | (UniformItem.gender == "Both") | (UniformItem.gender == None)
            )
        items = q.order_by(UniformItem.category, UniformItem.name).all()
        for item in items:
            self._add_item_row(item.name, item.size or "", item.category,
                                item.default_qty, item.unit_price)
        db.close()
        self._recalc()

    # ─────────────────────────────────────────────────────────────────────────
    #  ITEM ROWS
    # ─────────────────────────────────────────────────────────────────────────
    def _clear_item_rows(self):
        for row in self._bill_rows:
            row["frame"].destroy()
        self._bill_rows.clear()
        self._recalc()

    def _add_item_row(self, name="", size="", category="Uniform", qty=1, price=0.0):
        idx = len(self._bill_rows) + 1
        frame = ctk.CTkFrame(self.items_frame, fg_color="transparent")
        frame.pack(fill="x", pady=1)

        ctk.CTkLabel(frame, text=str(idx), width=30, font=ctk.CTkFont(size=11)).pack(side="left", padx=2)

        name_var = ctk.StringVar(value=name)
        ctk.CTkEntry(frame, textvariable=name_var, width=155, height=28).pack(side="left", padx=2)

        size_var = ctk.StringVar(value=size)
        ctk.CTkEntry(frame, textvariable=size_var, width=55, height=28).pack(side="left", padx=2)

        cat_var = ctk.StringVar(value=category)
        ctk.CTkEntry(frame, textvariable=cat_var, width=75, height=28).pack(side="left", padx=2)

        qty_var = ctk.StringVar(value=str(qty))
        qty_entry = ctk.CTkEntry(frame, textvariable=qty_var, width=45, height=28)
        qty_entry.pack(side="left", padx=2)

        price_var = ctk.StringVar(value=f"{price:.2f}")
        price_entry = ctk.CTkEntry(frame, textvariable=price_var, width=85, height=28)
        price_entry.pack(side="left", padx=2)

        total_var = ctk.StringVar(value=f"₹ {qty * price:.2f}")
        ctk.CTkLabel(frame, textvariable=total_var, width=88, anchor="e",
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=2)

        row_data = {
            "frame": frame, "name_var": name_var, "size_var": size_var,
            "cat_var": cat_var, "qty_var": qty_var, "price_var": price_var,
            "total_var": total_var
        }
        self._bill_rows.append(row_data)

        def on_change(*_):
            try:
                q = int(qty_var.get())
                p = float(price_var.get())
                total_var.set(f"₹ {q * p:.2f}")
            except ValueError:
                total_var.set("₹ -")
            self._recalc()

        qty_var.trace_add("write", on_change)
        price_var.trace_add("write", on_change)

        def del_row():
            self._bill_rows.remove(row_data)
            frame.destroy()
            self._recalc()

        ctk.CTkButton(frame, text="✕", width=36, height=28,
                      fg_color="#ea4335", hover_color="#c62828",
                      command=del_row).pack(side="left", padx=2)

    def _add_blank_row(self):
        self._add_item_row()

    # ─────────────────────────────────────────────────────────────────────────
    #  CALCULATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _recalc(self):
        subtotal = 0.0
        for row in self._bill_rows:
            try:
                q = int(row["qty_var"].get())
                p = float(row["price_var"].get())
                subtotal += q * p
            except ValueError:
                pass

        discount = 0.0
        try:
            dv = float(self.discount_entry.get())
            if self.discount_type_var.get() == "percent":
                discount = subtotal * dv / 100
            else:
                discount = dv
        except ValueError:
            pass

        grand = max(0.0, subtotal - discount)
        self.subtotal_var.set(f"₹ {subtotal:.2f}")
        self.grand_total_var.set(f"₹ {grand:.2f}")

    # ─────────────────────────────────────────────────────────────────────────
    #  SAVE BILL
    # ─────────────────────────────────────────────────────────────────────────
    def _save_bill(self):
        student_name = self.student_entries["student_name"].get().strip()
        if not student_name:
            self.bill_status.configure(text="Student name is required.", text_color="#ea4335")
            return
        if not self._bill_rows:
            self.bill_status.configure(text="No items in bill.", text_color="#ea4335")
            return

        school_id = self._schools.get(self.school_var.get())
        class_id = self._classes.get(self.class_var.get())

        # Parse items
        bill_items = []
        subtotal = 0.0
        for row in self._bill_rows:
            name = row["name_var"].get().strip()
            if not name:
                continue
            try:
                qty = int(row["qty_var"].get())
                price = float(row["price_var"].get())
            except ValueError:
                continue
            total = qty * price
            subtotal += total
            bill_items.append({
                "name": name, "size": row["size_var"].get().strip(),
                "category": row["cat_var"].get().strip(),
                "quantity": qty, "unit_price": price, "total_price": total
            })

        if not bill_items:
            self.bill_status.configure(text="No valid items.", text_color="#ea4335")
            return

        discount_type = self.discount_type_var.get()
        try:
            dv = float(self.discount_entry.get() or "0")
        except ValueError:
            dv = 0.0
        discount_amount = subtotal * dv / 100 if discount_type == "percent" else dv
        grand_total = max(0.0, subtotal - discount_amount)

        db = get_session()
        try:
            # Auto bill number using prefix from shop settings
            prefix = get_shop_settings().bill_prefix or "INV"
            count = db.query(Bill).count()
            bill_number = f"{prefix}-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"

            school = db.query(School).get(school_id) if school_id else None
            school_class = db.query(SchoolClass).get(class_id) if class_id else None

            bill = Bill(
                bill_number=bill_number,
                school_id=school_id,
                class_id=class_id,
                student_name=student_name,
                student_section=self.student_entries["student_section"].get().strip(),
                parent_name=self.student_entries["parent_name"].get().strip(),
                parent_phone=self.student_entries["parent_phone"].get().strip(),
                subtotal=subtotal,
                discount_type=discount_type,
                discount_value=dv,
                grand_total=grand_total,
                notes=self.notes_box.get("0.0", "end").strip(),
                created_by=AuthManager.current_user().id,
            )
            # Parse date
            try:
                bill.bill_date = datetime.strptime(self.date_entry.get().strip(), "%d-%m-%Y")
            except ValueError:
                bill.bill_date = datetime.now()

            db.add(bill)
            db.flush()

            for item in bill_items:
                db.add(BillItem(
                    bill_id=bill.id,
                    item_name=item["name"], size=item["size"],
                    category=item["category"], quantity=item["quantity"],
                    unit_price=item["unit_price"], total_price=item["total_price"]
                ))

            # Generate PDF
            bill_data = {
                "bill_number": bill_number,
                "bill_date": bill.bill_date,
                "school_name": school.name if school else "",
                "class_name": school_class.name if school_class else self.class_var.get(),
                "student_name": bill.student_name,
                "student_section": bill.student_section,
                "parent_name": bill.parent_name,
                "parent_phone": bill.parent_phone,
                "items": bill_items,
                "subtotal": subtotal,
                "discount_type": discount_type,
                "discount_value": dv,
                "grand_total": grand_total,
                "notes": bill.notes,
            }
            pdf_path = generate_bill_pdf(bill_data)
            bill.pdf_path = pdf_path

            db.commit()
            self._last_bill_id = bill.id
            self._last_pdf_path = pdf_path

            self.print_btn.configure(state="normal")
            self.open_pdf_btn.configure(state="normal")
            self.bill_status.configure(
                text=f"Bill saved! {bill_number}\nPDF: {pdf_path}",
                text_color="#34a853"
            )
        except Exception as e:
            db.rollback()
            self.bill_status.configure(text=f"Error saving bill: {e}", text_color="#ea4335")
        finally:
            db.close()

    def _print_bill(self):
        if not hasattr(self, "_last_pdf_path"):
            return
        ok, msg = print_pdf(self._last_pdf_path)
        self.bill_status.configure(text=msg, text_color="#34a853" if ok else "#ea4335")

    def _open_pdf_bill(self):
        if not hasattr(self, "_last_pdf_path"):
            return
        open_pdf(self._last_pdf_path)

    def _clear_bill(self):
        self._clear_item_rows()
        for e in self.student_entries.values():
            e.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.notes_box.delete("0.0", "end")
        self.discount_entry.delete(0, "end")
        self.bill_status.configure(text="")
        self.print_btn.configure(state="disabled")
        self.open_pdf_btn.configure(state="disabled")
        self._last_bill_id = None

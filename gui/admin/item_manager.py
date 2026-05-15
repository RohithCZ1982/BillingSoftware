import customtkinter as ctk
from tkinter import messagebox, ttk
from database.database import get_session
from database.models import School, SchoolClass, UniformItem
from config import CATEGORIES


class ItemManagerFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.selected_item_id = None
        self._schools = {}
        self._classes = {}
        self._build()
        self._load_schools()

    def _build(self):
        ctk.CTkLabel(self, text="Manage Uniform Items",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 12))

        # Filters row
        filters = ctk.CTkFrame(self, fg_color="transparent")
        filters.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(filters, text="School:").pack(side="left", padx=(0, 4))
        self.school_var = ctk.StringVar()
        self.school_combo = ctk.CTkComboBox(filters, variable=self.school_var, width=220,
                                             command=self._on_school_change)
        self.school_combo.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filters, text="Class:").pack(side="left", padx=(0, 4))
        self.class_var = ctk.StringVar()
        self.class_combo = ctk.CTkComboBox(filters, variable=self.class_var, width=140,
                                            command=lambda _: self._load_items())
        self.class_combo.pack(side="left")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)

        # ── Left: table ──────────────────────────────────────────────────────
        left = ctk.CTkFrame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b3b", fieldbackground="#2b2b3b",
                        foreground="white", rowheight=26)
        style.configure("Treeview.Heading", background="#1a73e8", foreground="white",
                        font=("Helvetica", 10, "bold"))
        style.map("Treeview", background=[("selected", "#1a73e8")])

        cols = ("Name", "Size", "Category", "Gender", "Qty", "Price")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("Name", width=150)
        self.tree.column("Size", width=55)
        self.tree.column("Category", width=85)
        self.tree.column("Gender", width=55)
        self.tree.column("Qty", width=38)
        self.tree.column("Price", width=70)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkButton(btn_row, text="Delete", fg_color="#ea4335", hover_color="#c62828",
                      width=80, command=self._delete).pack(side="right")
        ctk.CTkButton(btn_row, text="New", width=80, command=self._new).pack(side="right", padx=(0, 6))

        # ── Right: form ──────────────────────────────────────────────────────
        right = ctk.CTkFrame(content)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="Item Details",
                     font=ctk.CTkFont(weight="bold")).pack(pady=8)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(fill="x", padx=12)

        ctk.CTkLabel(form, text="Class (leave blank = all classes)", anchor="w",
                     font=ctk.CTkFont(size=11)).pack(fill="x", pady=(6, 0))
        self.item_class_var = ctk.StringVar()
        self.item_class_combo = ctk.CTkComboBox(form, variable=self.item_class_var, width=180)
        self.item_class_combo.pack(anchor="w", pady=(2, 0))

        self.form_entries = {}
        fields = [("Item Name *", "name"), ("Size", "size")]
        for label, key in fields:
            ctk.CTkLabel(form, text=label, anchor="w").pack(fill="x", pady=(8, 0))
            e = ctk.CTkEntry(form)
            e.pack(fill="x", pady=(2, 0))
            self.form_entries[key] = e

        ctk.CTkLabel(form, text="Category", anchor="w").pack(fill="x", pady=(8, 0))
        self.category_var = ctk.StringVar(value=CATEGORIES[0])
        ctk.CTkComboBox(form, variable=self.category_var, values=CATEGORIES).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(form, text="Gender", anchor="w").pack(fill="x", pady=(8, 0))
        self.gender_var = ctk.StringVar(value="Both")
        gender_frame = ctk.CTkFrame(form, fg_color="transparent")
        gender_frame.pack(anchor="w", pady=(2, 0))
        for g in ("Boy", "Girl", "Both"):
            ctk.CTkRadioButton(gender_frame, text=g, variable=self.gender_var,
                               value=g).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(form, text="Default Qty", anchor="w").pack(fill="x", pady=(8, 0))
        self.qty_var = ctk.StringVar(value="1")
        ctk.CTkEntry(form, textvariable=self.qty_var, width=80).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(form, text="Unit Price (₹)", anchor="w").pack(fill="x", pady=(8, 0))
        self.price_var = ctk.StringVar(value="0.00")
        ctk.CTkEntry(form, textvariable=self.price_var, width=100).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(right, text="Save Item", height=38,
                      command=self._save).pack(pady=14, padx=12, fill="x")
        self.status_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=11))
        self.status_label.pack()

    def _load_schools(self):
        db = get_session()
        schools = db.query(School).order_by(School.name).all()
        self._schools = {s.name: s.id for s in schools}
        db.close()
        names = list(self._schools.keys())
        self.school_combo.configure(values=names)
        if names:
            self.school_var.set(names[0])
            self._on_school_change(names[0])

    def _on_school_change(self, _=None):
        school_id = self._schools.get(self.school_var.get())
        if not school_id:
            return
        db = get_session()
        classes = db.query(SchoolClass).filter_by(school_id=school_id).order_by(SchoolClass.name).all()
        self._classes = {"(All Classes)": None}
        self._classes.update({c.name: c.id for c in classes})
        db.close()
        names = list(self._classes.keys())
        self.class_combo.configure(values=names)
        self.class_var.set(names[0])
        self.item_class_combo.configure(values=names)
        self.item_class_var.set(names[0])
        self._load_items()

    def _load_items(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        school_id = self._schools.get(self.school_var.get())
        if not school_id:
            return
        db = get_session()
        q = db.query(UniformItem).filter_by(school_id=school_id)
        class_id = self._classes.get(self.class_var.get())
        if class_id:
            q = q.filter_by(class_id=class_id)
        items = q.order_by(UniformItem.category, UniformItem.name).all()
        self._item_ids = []
        for item in items:
            iid = self.tree.insert("", "end", values=(
                item.name, item.size or "-", item.category,
                item.gender or "Both", item.default_qty, f"₹{item.unit_price:.2f}"
            ))
            self._item_ids.append((iid, item.id))
        db.close()

    def _on_select(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        item_id = next((aid for (tid, aid) in self._item_ids if tid == iid), None)
        if not item_id:
            return
        self.selected_item_id = item_id
        db = get_session()
        item = db.query(UniformItem).get(item_id)
        if item:
            cls_name = "(All Classes)"
            if item.class_id:
                cls = db.query(SchoolClass).get(item.class_id)
                if cls:
                    cls_name = cls.name
            self.item_class_var.set(cls_name)
            self.form_entries["name"].delete(0, "end")
            self.form_entries["name"].insert(0, item.name)
            self.form_entries["size"].delete(0, "end")
            self.form_entries["size"].insert(0, item.size or "")
            self.category_var.set(item.category or CATEGORIES[0])
            self.gender_var.set(item.gender or "Both")
            self.qty_var.set(str(item.default_qty))
            self.price_var.set(str(item.unit_price))
        db.close()

    def _new(self):
        self.selected_item_id = None
        for e in self.form_entries.values():
            e.delete(0, "end")
        self.qty_var.set("1")
        self.price_var.set("0.00")
        self.category_var.set(CATEGORIES[0])
        self.gender_var.set("Both")

    def _save(self):
        school_id = self._schools.get(self.school_var.get())
        if not school_id:
            self.status_label.configure(text="Select a school.", text_color="#ea4335")
            return
        name = self.form_entries["name"].get().strip()
        if not name:
            self.status_label.configure(text="Item name is required.", text_color="#ea4335")
            return
        try:
            qty = int(self.qty_var.get())
            price = float(self.price_var.get())
        except ValueError:
            self.status_label.configure(text="Invalid qty or price.", text_color="#ea4335")
            return

        class_id = self._classes.get(self.item_class_var.get())
        db = get_session()
        try:
            if self.selected_item_id:
                item = db.query(UniformItem).get(self.selected_item_id)
            else:
                item = UniformItem(school_id=school_id)
                db.add(item)
            item.class_id = class_id
            item.name = name
            item.size = self.form_entries["size"].get().strip() or None
            item.category = self.category_var.get()
            item.gender = self.gender_var.get()
            item.default_qty = qty
            item.unit_price = price
            db.commit()
            self.selected_item_id = item.id
            self.status_label.configure(text="Saved.", text_color="#34a853")
            self._load_items()
        except Exception as e:
            db.rollback()
            self.status_label.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

    def _delete(self):
        if not self.selected_item_id:
            return
        if not messagebox.askyesno("Delete", "Delete this item?"):
            return
        db = get_session()
        try:
            item = db.query(UniformItem).get(self.selected_item_id)
            if item:
                db.delete(item)
                db.commit()
            self.selected_item_id = None
            self._new()
            self._load_items()
            self.status_label.configure(text="Deleted.", text_color="#fbbc04")
        except Exception as e:
            db.rollback()
            self.status_label.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

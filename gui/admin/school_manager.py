import customtkinter as ctk
from tkinter import messagebox
from database.database import get_session
from database.models import School, SchoolClass
from config import CLASSES


class SchoolManagerFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.selected_id = None
        self._build()
        self._load()

    def _build(self):
        # Title
        ctk.CTkLabel(self, text="Manage Schools",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 16))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)

        # ── Left: list ───────────────────────────────────────────────────────
        left = ctk.CTkFrame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(left, text="Schools", font=ctk.CTkFont(weight="bold")).pack(pady=8)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        ctk.CTkEntry(left, textvariable=self.search_var,
                     placeholder_text="Search...").pack(fill="x", padx=8, pady=(0, 8))

        self.listbox = ctk.CTkScrollableFrame(left)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkButton(btn_row, text="Delete", fg_color="#ea4335", hover_color="#c62828",
                      width=80, command=self._delete).pack(side="right")
        ctk.CTkButton(btn_row, text="New", width=80,
                      command=self._new).pack(side="right", padx=(0, 6))

        # ── Right: form ──────────────────────────────────────────────────────
        right = ctk.CTkFrame(content)
        right.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(right, text="School Details",
                     font=ctk.CTkFont(weight="bold")).pack(pady=8)
        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(fill="x", padx=16)

        fields = [("School Name *", "name"), ("Address", "address"),
                  ("Phone", "phone"), ("Email", "email")]
        self.entries = {}
        for label, key in fields:
            ctk.CTkLabel(form, text=label, anchor="w").pack(fill="x", pady=(6, 0))
            if key == "address":
                e = ctk.CTkTextbox(form, height=60)
            else:
                e = ctk.CTkEntry(form)
            e.pack(fill="x", pady=(2, 0))
            self.entries[key] = e

        ctk.CTkButton(right, text="Save", height=38,
                      command=self._save).pack(pady=16, padx=16, fill="x")
        self.status_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=11))
        self.status_label.pack()

    def _load(self):
        for w in self.listbox.winfo_children():
            w.destroy()
        db = get_session()
        q = db.query(School)
        s = self.search_var.get().strip()
        if s:
            q = q.filter(School.name.ilike(f"%{s}%"))
        schools = q.order_by(School.name).all()
        db.close()
        for school in schools:
            btn = ctk.CTkButton(
                self.listbox, text=school.name, anchor="w",
                fg_color="transparent", hover_color="#313244", text_color=("black", "white"),
                command=lambda sid=school.id: self._select(sid)
            )
            btn.pack(fill="x", pady=2)

    def _select(self, school_id):
        self.selected_id = school_id
        db = get_session()
        school = db.query(School).get(school_id)
        if school:
            self._set_field("name", school.name)
            self._set_field("address", school.address or "")
            self._set_field("phone", school.phone or "")
            self._set_field("email", school.email or "")
        db.close()

    def _set_field(self, key, value):
        e = self.entries[key]
        if isinstance(e, ctk.CTkTextbox):
            e.delete("0.0", "end")
            e.insert("0.0", value)
        else:
            e.delete(0, "end")
            e.insert(0, value)

    def _get_field(self, key) -> str:
        e = self.entries[key]
        if isinstance(e, ctk.CTkTextbox):
            return e.get("0.0", "end").strip()
        return e.get().strip()

    def _new(self):
        self.selected_id = None
        for key in self.entries:
            self._set_field(key, "")
        self.entries["name"].focus()

    def _save(self):
        name = self._get_field("name")
        if not name:
            self.status_label.configure(text="School name is required.", text_color="#ea4335")
            return
        db = get_session()
        is_new = False
        try:
            if self.selected_id:
                school = db.query(School).get(self.selected_id)
                if not school:
                    self.status_label.configure(text="School not found.", text_color="#ea4335")
                    return
            else:
                is_new = True
                school = School()
                db.add(school)
                db.flush()  # get school.id before adding classes
                for cls_name in CLASSES:
                    db.add(SchoolClass(school_id=school.id, name=cls_name))
            school.name = name
            school.address = self._get_field("address")
            school.phone = self._get_field("phone")
            school.email = self._get_field("email")
            db.commit()
            self.selected_id = school.id
            msg = f"Saved. {len(CLASSES)} classes loaded — remove unwanted ones in Classes." if is_new else "Saved successfully."
            self.status_label.configure(text=msg, text_color="#34a853")
            self._load()
        except Exception as e:
            db.rollback()
            self.status_label.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

    def _delete(self):
        if not self.selected_id:
            return
        if not messagebox.askyesno("Delete", "Delete this school and all its data?"):
            return
        db = get_session()
        try:
            school = db.query(School).get(self.selected_id)
            if school:
                db.delete(school)
                db.commit()
            self.selected_id = None
            self._new()
            self._load()
            self.status_label.configure(text="Deleted.", text_color="#fbbc04")
        except Exception as e:
            db.rollback()
            self.status_label.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

import customtkinter as ctk
from tkinter import messagebox
from database.database import get_session
from database.models import School, SchoolClass
from config import CLASSES


class ClassManagerFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.selected_class_id = None
        self._build()
        self._load_schools()

    def _build(self):
        ctk.CTkLabel(self, text="Manage Classes",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 16))

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(top, text="Select School:").pack(side="left", padx=(0, 8))
        self.school_var = ctk.StringVar()
        self.school_combo = ctk.CTkComboBox(top, variable=self.school_var, width=260,
                                             command=self._on_school_change)
        self.school_combo.pack(side="left")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)

        # ── Left: classes list ───────────────────────────────────────────────
        left = ctk.CTkFrame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(left, text="Classes", font=ctk.CTkFont(weight="bold")).pack(pady=8)
        self.class_list = ctk.CTkScrollableFrame(left)
        self.class_list.pack(fill="both", expand=True, padx=8)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(btn_row, text="Delete", fg_color="#ea4335", hover_color="#c62828",
                      width=80, command=self._delete).pack(side="right")
        ctk.CTkButton(btn_row, text="New", width=80,
                      command=self._new).pack(side="right", padx=(0, 6))

        # ── Right: form ──────────────────────────────────────────────────────
        right = ctk.CTkFrame(content)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="Class Details",
                     font=ctk.CTkFont(weight="bold")).pack(pady=8)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(fill="x", padx=16)

        ctk.CTkLabel(form, text="Class Name *", anchor="w").pack(fill="x", pady=(6, 0))
        self.class_name_var = ctk.StringVar()
        self.class_combo = ctk.CTkComboBox(form, variable=self.class_name_var,
                                            values=CLASSES, width=200)
        self.class_combo.pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(right, text="Save", height=38,
                      command=self._save).pack(pady=16, padx=16, fill="x")
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
        self.selected_class_id = None
        self._load_classes()

    def _load_classes(self):
        for w in self.class_list.winfo_children():
            w.destroy()
        school_id = self._schools.get(self.school_var.get())
        if not school_id:
            return
        db = get_session()
        classes = db.query(SchoolClass).filter_by(school_id=school_id).order_by(SchoolClass.name).all()
        db.close()
        for cls in classes:
            btn = ctk.CTkButton(
                self.class_list, text=cls.name, anchor="w",
                fg_color="transparent", hover_color="#313244", text_color=("black", "white"),
                command=lambda cid=cls.id, cname=cls.name: self._select(cid, cname)
            )
            btn.pack(fill="x", pady=2)

    def _select(self, class_id, class_name):
        self.selected_class_id = class_id
        self.class_name_var.set(class_name)

    def _new(self):
        self.selected_class_id = None
        self.class_name_var.set("")

    def _save(self):
        school_id = self._schools.get(self.school_var.get())
        if not school_id:
            self.status_label.configure(text="Select a school first.", text_color="#ea4335")
            return
        name = self.class_name_var.get().strip()
        if not name:
            self.status_label.configure(text="Class name is required.", text_color="#ea4335")
            return
        db = get_session()
        try:
            if self.selected_class_id:
                cls = db.query(SchoolClass).get(self.selected_class_id)
            else:
                existing = db.query(SchoolClass).filter_by(school_id=school_id, name=name).first()
                if existing:
                    self.status_label.configure(text="Class already exists.", text_color="#ea4335")
                    return
                cls = SchoolClass(school_id=school_id)
                db.add(cls)
            cls.name = name
            db.commit()
            self.status_label.configure(text="Saved.", text_color="#34a853")
            self._load_classes()
        except Exception as e:
            db.rollback()
            self.status_label.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

    def _delete(self):
        if not self.selected_class_id:
            return
        if not messagebox.askyesno("Delete", "Delete this class?"):
            return
        db = get_session()
        try:
            cls = db.query(SchoolClass).get(self.selected_class_id)
            if cls:
                db.delete(cls)
                db.commit()
            self.selected_class_id = None
            self._new()
            self._load_classes()
            self.status_label.configure(text="Deleted.", text_color="#fbbc04")
        except Exception as e:
            db.rollback()
            self.status_label.configure(text=f"Error: {e}", text_color="#ea4335")
        finally:
            db.close()

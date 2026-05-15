"""
Seed script — Mysore West Lions Sevaniketan School
Rates extracted from the official quotation (April 2026).

Boys  : LKG–10th Std  (5 items each, Sweater type changes from 7th Std)
Girls : LKG–10th Std  (6 items each, includes Cotton Tights)

Run once:
  python database/seed_lions_school.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db, get_session
from database.models import School, SchoolClass, UniformItem

SCHOOL_NAME = "Mysore West Lions Sevaniketan School"
SCHOOL_ADDR = "Gokulam, Mysore"
SCHOOL_PHONE = "0821-2517670"

# ── Boys items per class ─────────────────────────────────────────────────────
# (item_name, unit, default_qty, unit_price, category)
BOYS = {
    "LKG": [
        ("Uniform",              "Set",  2, 600.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 675.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  75.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Full Sleeves Sweater", "Nos",  1, 220.0,  "Uniform"),
    ],
    "UKG": [
        ("Uniform",              "Set",  2, 600.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 675.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  75.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Full Sleeves Sweater", "Nos",  1, 220.0,  "Uniform"),
    ],
    "1st Std": [
        ("Uniform",              "Set",  2, 640.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 725.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  80.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Full Sleeves Sweater", "Nos",  1, 240.0,  "Uniform"),   # rate 240 (total 2605 confirms)
    ],
    "2nd Std": [
        ("Uniform",              "Set",  2, 640.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 725.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  80.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Full Sleeves Sweater", "Nos",  1, 240.0,  "Uniform"),
    ],
    "3rd Std": [
        ("Uniform",              "Set",  2, 690.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 775.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  80.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Full Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "4th Std": [
        ("Uniform",              "Set",  2, 690.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 775.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  80.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Full Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "5th Std": [
        ("Uniform",              "Set",  2, 950.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 800.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Full Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "6th Std": [
        ("Uniform",              "Set",  2, 950.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 800.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Full Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "7th Std": [
        ("Uniform",              "Set",  2, 950.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 800.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Half Sleeves Sweater", "Nos",  1, 220.0,  "Uniform"),
    ],
    "8th Std": [
        ("Uniform",              "Set",  2,1020.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 850.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Half Sleeves Sweater", "Nos",  1, 240.0,  "Uniform"),
    ],
    "9th Std": [
        ("Uniform",              "Set",  2,1020.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 850.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Half Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "10th Std": [
        ("Uniform",              "Set",  2,1020.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 850.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Half Sleeves Sweater", "Nos",  1, 280.0,  "Uniform"),
    ],
}

# ── Girls items per class ─────────────────────────────────────────────────────
GIRLS = {
    "LKG": [
        ("Uniform",              "Set",  2, 600.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 675.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  75.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 130.0,  "Uniform"),
        ("Full Sleeves Sweater", "Nos",  1, 220.0,  "Uniform"),
    ],
    "UKG": [
        ("Uniform",              "Set",  2, 600.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 675.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  75.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 130.0,  "Uniform"),
        ("Full Sleeves Sweater", "Nos",  1, 220.0,  "Uniform"),
    ],
    "1st Std": [
        ("Uniform",              "Set",  2, 640.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 725.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  80.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 150.0,  "Uniform"),
        ("Full Sleeves Sweater", "Nos",  1, 240.0,  "Uniform"),
    ],
    "2nd Std": [
        ("Uniform",              "Set",  2, 640.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 725.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  80.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 150.0,  "Uniform"),
        ("Full Sleeves Sweater", "Nos",  1, 240.0,  "Uniform"),
    ],
    "3rd Std": [
        ("Uniform",              "Set",  2, 690.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 775.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  80.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 150.0,  "Uniform"),
        ("Full Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "4th Std": [
        ("Uniform",              "Set",  2, 690.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 775.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  80.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 150.0,  "Uniform"),
        ("Full Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "5th Std": [
        ("Uniform",              "Set",  2, 900.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 800.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 160.0,  "Uniform"),
        ("Full Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "6th Std": [
        ("Uniform",              "Set",  2, 900.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 800.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 160.0,  "Uniform"),
        ("Full Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "7th Std": [
        ("Uniform",              "Set",  2, 900.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 800.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 160.0,  "Uniform"),
        ("Half Sleeves Sweater", "Nos",  1, 220.0,  "Uniform"),
    ],
    "8th Std": [
        ("Uniform",              "Set",  2,1020.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 850.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 160.0,  "Uniform"),
        ("Half Sleeves Sweater", "Nos",  1, 240.0,  "Uniform"),
    ],
    "9th Std": [
        ("Uniform",              "Set",  2,1020.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 850.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 160.0,  "Uniform"),
        ("Half Sleeves Sweater", "Nos",  1, 260.0,  "Uniform"),
    ],
    "10th Std": [
        ("Uniform",              "Set",  2,1020.0,  "Uniform"),
        ("Track Suit",           "Set",  1, 850.0,  "Uniform"),
        ("Cotton Socks",         "Pair", 3,  90.0,  "Accessory"),
        ("Belt",                 "Nos",  1, 120.0,  "Accessory"),
        ("Cotton Tights",        "Nos",  2, 160.0,  "Uniform"),
        ("Half Sleeves Sweater", "Nos",  1, 280.0,  "Uniform"),
    ],
}

CLASS_ORDER = ["LKG","UKG","1st Std","2nd Std","3rd Std","4th Std","5th Std",
               "6th Std","7th Std","8th Std","9th Std","10th Std"]


def seed():
    init_db()
    db = get_session()
    try:
        # ── School ───────────────────────────────────────────────────────────
        school = db.query(School).filter_by(name=SCHOOL_NAME).first()
        if school:
            print(f"School already exists (id={school.id}). Clearing existing items …")
            db.query(UniformItem).filter_by(school_id=school.id).delete()
            db.flush()
        else:
            school = School(name=SCHOOL_NAME, address=SCHOOL_ADDR, phone=SCHOOL_PHONE)
            db.add(school)
            db.flush()
            print(f"Created school '{SCHOOL_NAME}' (id={school.id})")

        # ── Ensure all classes exist ──────────────────────────────────────────
        class_map = {}
        for cls_name in CLASS_ORDER:
            cls = db.query(SchoolClass).filter_by(school_id=school.id, name=cls_name).first()
            if not cls:
                cls = SchoolClass(school_id=school.id, name=cls_name)
                db.add(cls)
                db.flush()
            class_map[cls_name] = cls.id

        # ── Insert Boys items ─────────────────────────────────────────────────
        boy_count = 0
        for cls_name, items in BOYS.items():
            cls_id = class_map[cls_name]
            for name, size, qty, price, cat in items:
                db.add(UniformItem(
                    school_id=school.id, class_id=cls_id,
                    name=name, size=size, default_qty=qty,
                    unit_price=price, category=cat, gender="Boy"
                ))
                boy_count += 1

        # ── Insert Girls items ────────────────────────────────────────────────
        girl_count = 0
        for cls_name, items in GIRLS.items():
            cls_id = class_map[cls_name]
            for name, size, qty, price, cat in items:
                db.add(UniformItem(
                    school_id=school.id, class_id=cls_id,
                    name=name, size=size, default_qty=qty,
                    unit_price=price, category=cat, gender="Girl"
                ))
                girl_count += 1

        db.commit()
        print(f"\nDone!")
        print(f"  Classes  : {len(class_map)}")
        print(f"  Boy items: {boy_count}  ({boy_count // len(BOYS)} items × {len(BOYS)} classes)")
        print(f"  Girl items: {girl_count}  ({girl_count // len(GIRLS)} items × {len(GIRLS)} classes)")

        # ── Quick verification ────────────────────────────────────────────────
        print("\nVerification (Boys totals from DB):")
        for cls_name in CLASS_ORDER:
            cls_id = class_map[cls_name]
            items = db.query(UniformItem).filter_by(
                school_id=school.id, class_id=cls_id, gender="Boy").all()
            total = sum(i.default_qty * i.unit_price for i in items)
            print(f"  {cls_name:<10} Boys  = Rs.{total:,.2f}")

        print("\nVerification (Girls totals from DB):")
        for cls_name in CLASS_ORDER:
            cls_id = class_map[cls_name]
            items = db.query(UniformItem).filter_by(
                school_id=school.id, class_id=cls_id, gender="Girl").all()
            total = sum(i.default_qty * i.unit_price for i in items)
            print(f"  {cls_name:<10} Girls = Rs.{total:,.2f}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

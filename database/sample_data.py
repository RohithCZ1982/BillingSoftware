"""Run once to populate sample data."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db, get_session
from database.models import User, School, SchoolClass, UniformItem
import bcrypt


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def insert_sample_data():
    init_db()
    db = get_session()
    try:
        # Users
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(username="admin", password_hash=hash_password("admin123"),
                        full_name="Administrator", role="admin"))
        if not db.query(User).filter_by(username="sales1").first():
            db.add(User(username="sales1", password_hash=hash_password("sales123"),
                        full_name="Sales Staff", role="accountant"))
        db.flush()

        # School 1
        if not db.query(School).filter_by(name="St. Mary's School").first():
            school1 = School(
                name="St. Mary's School",
                address="45 Church Road, Chennai - 600005",
                phone="044-12345678"
            )
            db.add(school1)
            db.flush()

            classes_data = ["LKG", "UKG", "1st Std", "2nd Std", "3rd Std",
                            "4th Std", "5th Std", "6th Std"]
            for cls_name in classes_data:
                cls = SchoolClass(school_id=school1.id, name=cls_name)
                db.add(cls)
                db.flush()

                items = [
                    ("Shirt (White)", "M", 2, 320.0, "Uniform"),
                    ("Pant (Grey)", "30", 2, 480.0, "Uniform"),
                    ("Tie", "-", 1, 120.0, "Accessory"),
                    ("Belt", "M", 1, 90.0, "Accessory"),
                    ("School Bag", "-", 1, 850.0, "Accessory"),
                    ("Shoes (Black)", "6", 1, 650.0, "Footwear"),
                    ("White Socks", "M", 2, 80.0, "Footwear"),
                ]
                for name, size, qty, price, cat in items:
                    db.add(UniformItem(
                        school_id=school1.id, class_id=cls.id,
                        name=name, size=size, default_qty=qty,
                        unit_price=price, category=cat
                    ))

        # School 2
        if not db.query(School).filter_by(name="Delhi Public School").first():
            school2 = School(
                name="Delhi Public School",
                address="78 Anna Nagar, Chennai - 600040",
                phone="044-87654321"
            )
            db.add(school2)
            db.flush()

            for cls_name in ["1st Std", "2nd Std", "3rd Std", "4th Std", "5th Std"]:
                cls = SchoolClass(school_id=school2.id, name=cls_name)
                db.add(cls)
                db.flush()
                items = [
                    ("Shirt (Light Blue)", "M", 2, 350.0, "Uniform"),
                    ("Pant (Dark Blue)", "30", 2, 520.0, "Uniform"),
                    ("Blazer", "M", 1, 1200.0, "Uniform"),
                    ("Tie", "-", 1, 150.0, "Accessory"),
                    ("Shoes (Black)", "6", 1, 750.0, "Footwear"),
                    ("Blue Socks", "M", 2, 90.0, "Footwear"),
                ]
                for name, size, qty, price, cat in items:
                    db.add(UniformItem(
                        school_id=school2.id, class_id=cls.id,
                        name=name, size=size, default_qty=qty,
                        unit_price=price, category=cat
                    ))

        db.commit()
        print("Sample data inserted successfully.")
        print("Login credentials:")
        print("  Admin   -> username: admin    | password: admin123")
        print("  Sales   -> username: sales1   | password: sales123")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    insert_sample_data()

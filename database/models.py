from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    admin = "admin"
    accountant = "accountant"


class ShopSettings(Base):
    __tablename__ = "shop_settings"
    id = Column(Integer, primary_key=True)
    shop_name = Column(String(150), default="Sri Vijaya Uniforms")
    address_line1 = Column(String(200), default="123 Main Street")
    address_line2 = Column(String(200), default="Chennai - 600001")
    phone = Column(String(40), default="+91 98765 43210")
    email = Column(String(100), default="")
    gst_number = Column(String(50), default="33ABCDE1234F1Z5")
    bill_prefix = Column(String(20), default="INV")
    footer_note = Column(Text, default="Thank you for your purchase! Goods once sold will not be taken back.")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="accountant")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    bills = relationship("Bill", back_populates="created_by_user")


class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    classes = relationship("SchoolClass", back_populates="school", cascade="all, delete-orphan")
    items = relationship("UniformItem", back_populates="school", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="school")


class SchoolClass(Base):
    __tablename__ = "school_classes"
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    name = Column(String(50), nullable=False)
    school = relationship("School", back_populates="classes")
    items = relationship("UniformItem", back_populates="school_class")
    bills = relationship("Bill", back_populates="school_class")


class UniformItem(Base):
    __tablename__ = "uniform_items"
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("school_classes.id"), nullable=True)
    name = Column(String(100), nullable=False)
    size = Column(String(30))
    default_qty = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    category = Column(String(50), default="Uniform")
    gender = Column(String(10), default="Both")   # Boy / Girl / Both
    is_active = Column(Boolean, default=True)
    school = relationship("School", back_populates="items")
    school_class = relationship("SchoolClass", back_populates="items")


class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True)
    bill_number = Column(String(30), unique=True, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"))
    class_id = Column(Integer, ForeignKey("school_classes.id"), nullable=True)
    student_name = Column(String(150), nullable=False)
    student_section = Column(String(20))
    parent_name = Column(String(150))
    parent_phone = Column(String(20))
    bill_date = Column(DateTime, default=datetime.now)
    subtotal = Column(Float, default=0.0)
    discount_type = Column(String(20), default="flat")  # flat / percent
    discount_value = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    notes = Column(Text)
    payment_mode = Column(String(10), default="Cash")   # Cash / UPI
    upi_transaction_id = Column(String(100))
    pdf_path = Column(String(300))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    school = relationship("School", back_populates="bills")
    school_class = relationship("SchoolClass", back_populates="bills")
    created_by_user = relationship("User", back_populates="bills")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")


class BillItem(Base):
    __tablename__ = "bill_items"
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    item_name = Column(String(100), nullable=False)
    size = Column(String(30))
    category = Column(String(50))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    bill = relationship("Bill", back_populates="items")

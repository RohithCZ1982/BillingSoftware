import os

APP_NAME = "School Uniform Billing"
APP_VERSION = "1.0.0"

SHOP_NAME = "Sri Vijaya Uniforms"
SHOP_ADDRESS = "123 Main Street, Chennai - 600001"
SHOP_PHONE = "+91 98765 43210"
SHOP_EMAIL = "info@srivijayauniforms.com"
SHOP_GST = "33ABCDE1234F1Z5"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "billing.db")
BILLS_PDF_DIR = os.path.join(BASE_DIR, "bills")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

BILL_PREFIX = "INV"

COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "success": "#34a853",
    "danger": "#ea4335",
    "warning": "#fbbc04",
    "sidebar_bg": "#1e1e2e",
    "sidebar_text": "#cdd6f4",
    "sidebar_hover": "#313244",
    "sidebar_active": "#1a73e8",
}

CLASSES = [
    "LKG", "UKG",
    "1st Std", "2nd Std", "3rd Std", "4th Std", "5th Std",
    "6th Std", "7th Std", "8th Std", "9th Std", "10th Std",
    "11th Std", "12th Std"
]

CATEGORIES = ["Uniform", "Accessory", "Footwear", "Stationery", "Other"]

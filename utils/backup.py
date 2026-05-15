import os
import shutil
from datetime import datetime
from config import DB_PATH, BACKUP_DIR


def create_backup() -> tuple[bool, str]:
    """Copy the SQLite database to the backups folder."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        return False, "Database file not found."
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"billing_backup_{timestamp}.db")
    try:
        shutil.copy2(DB_PATH, dest)
        return True, f"Backup saved to:\n{dest}"
    except Exception as e:
        return False, f"Backup failed: {e}"

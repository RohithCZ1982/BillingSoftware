import os
import shutil
from datetime import datetime
from config import DB_PATH, BACKUP_DIR


def list_backups() -> list[dict]:
    """Return all backup files sorted newest-first.
    Each entry: {name, path, size_kb, modified}
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)
    entries = []
    for fname in os.listdir(BACKUP_DIR):
        if not fname.endswith(".db"):
            continue
        path = os.path.join(BACKUP_DIR, fname)
        stat = os.stat(path)
        entries.append({
            "name":     fname,
            "path":     path,
            "size_kb":  round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime),
        })
    entries.sort(key=lambda e: e["modified"], reverse=True)
    return entries


def restore_backup(backup_path: str) -> tuple[bool, str]:
    """Replace the live DB with the chosen backup file.
    The current DB is auto-saved as a safety backup first.
    """
    if not os.path.exists(backup_path):
        return False, "Backup file not found."
    # Safety: snapshot the current live DB before overwriting
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        safety = os.path.join(
            BACKUP_DIR,
            f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        shutil.copy2(DB_PATH, safety)
    try:
        shutil.copy2(backup_path, DB_PATH)
        return True, f"Restored from:\n{os.path.basename(backup_path)}\n\nPlease restart the application."
    except Exception as e:
        return False, f"Restore failed: {e}"


def default_backup_name() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"billing_backup_{timestamp}"


def create_backup(filename: str = "") -> tuple[bool, str]:
    """Copy the SQLite database to the backups folder.
    filename: stem without extension; uses default if empty.
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        return False, "Database file not found."
    stem = filename.strip() or default_backup_name()
    if not stem.endswith(".db"):
        stem += ".db"
    dest = os.path.join(BACKUP_DIR, stem)
    try:
        shutil.copy2(DB_PATH, dest)
        return True, f"Backup saved:\n{dest}"
    except Exception as e:
        return False, f"Backup failed: {e}"

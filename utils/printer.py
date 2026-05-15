import os
import sys
import subprocess


def print_pdf(pdf_path: str) -> tuple[bool, str]:
    """Print a PDF file. Returns (success, message)."""
    if not os.path.exists(pdf_path):
        return False, f"File not found: {pdf_path}"

    try:
        if sys.platform == "win32":
            # Try win32api first, fall back to ShellExecute
            try:
                import win32api
                win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)
                return True, "Print job sent successfully."
            except ImportError:
                os.startfile(pdf_path, "print")
                return True, "Print job sent successfully."
        elif sys.platform == "darwin":
            subprocess.run(["lpr", pdf_path], check=True)
            return True, "Print job sent."
        else:
            subprocess.run(["lpr", pdf_path], check=True)
            return True, "Print job sent."
    except Exception as e:
        return False, f"Print failed: {e}"


def open_pdf(pdf_path: str):
    """Open PDF in the default viewer."""
    if sys.platform == "win32":
        os.startfile(pdf_path)
    elif sys.platform == "darwin":
        subprocess.run(["open", pdf_path])
    else:
        subprocess.run(["xdg-open", pdf_path])

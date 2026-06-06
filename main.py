import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox, QDialog

from styles import DARK_STYLE
from store import PasswordStore
from dialogs import ModernLoginDialog
from main_window import ModernMainWindow

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SecureVault")
    
    # Apply modern style
    app.setStyleSheet(DARK_STYLE)
    
    store_path = Path(__file__).parent / "passwords.enc"
    
    # Modern login
    login = ModernLoginDialog(store_path)
    if login.exec() != QDialog.DialogCode.Accepted:
        return 0
    
    if not login.password:
        QMessageBox.warning(None, "Error", "Password required!")
        return 0
    
    store = PasswordStore(store_path, login.password)
    try:
        store.load()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Cannot open store: {e}")
        return 1
    
    window = ModernMainWindow(store)
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
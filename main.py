"""Main entry point - like index.html"""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from PySide6.QtCore import Qt

from styles import apply_style
from store import PasswordStore
from dialogs import LoginDialog
from main_window import PasswordManagerMainWindow


def main() -> int:
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Password Manager")
    app.setOrganizationName("YourCompany")
    
    # Apply styling (like loading CSS)
    apply_style(app)
    
    # Set application icon (optional - add your own .ico file)
    # app.setWindowIcon(QIcon("icon.png"))
    
    # Path to store encrypted passwords
    store_path = Path(__file__).parent / "passwords.enc"
    
    # Show login dialog
    login = LoginDialog(store_path)
    if login.exec() != QDialog.DialogCode.Accepted:
        return 0  # User cancelled
    
    # Validate master password
    if not login.password:
        QMessageBox.warning(None, "Password Required", "Master password cannot be empty!")
        return 0
    
    # Load password store
    store = PasswordStore(store_path, login.password)
    try:
        store.load()
    except Exception as e:
        QMessageBox.critical(
            None, 
            "Error", 
            f"Failed to open password store.\n\nError: {e}\n\n"
            "This might be because of an incorrect master password or corrupted file."
        )
        return 1
    
    # Show main window
    window = PasswordManagerMainWindow(store)
    window.show()
    
    # Start event loop
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
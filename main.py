import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from styles import DARK_STYLE
from store import PasswordStore
from dialogs import ModernLoginDialog
from main_window import ModernMainWindow


def get_store_path() -> Path:
    """Return a stable path for the encrypted password store."""
    app_data_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    if not app_data_dir or app_data_dir == Path('.'):
        app_data_dir = Path.home() / "AppData" / "Roaming" / "SecureVault"
    else:
        app_data_dir = app_data_dir

    app_data_dir.mkdir(parents=True, exist_ok=True)
    store_path = app_data_dir / "passwords.enc"

    # If a local store exists next to the script, migrate it once to the persistent app data path.
    local_store = Path(__file__).parent / "passwords.enc"
    if local_store.exists() and not store_path.exists():
        try:
            local_store.replace(store_path)
        except Exception:
            pass

    return store_path


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SecureVault")
    # Load SVG app icon from assets
    try:
        svg_path = Path(__file__).parent / "assets" / "lock.svg"
        def load_svg_icon(path, size=64):
            renderer = QSvgRenderer(str(path))
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)

        app.setWindowIcon(load_svg_icon(svg_path, 64))
    except Exception:
        # Fall back silently if SVG cannot be loaded
        pass
    
    # Apply modern style
    app.setStyleSheet(DARK_STYLE)
    
    store_path = get_store_path()
    
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
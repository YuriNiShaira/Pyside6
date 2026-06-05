"""Main window of the application - like main page component"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QMessageBox, QApplication, QDialog
)

from store import PasswordStore
from dialogs import EntryDialog


class PasswordManagerMainWindow(QMainWindow):
    def __init__(self, store: PasswordStore):
        super().__init__()
        self.store = store
        self.setWindowTitle("🔐 Password Manager")
        self.setMinimumSize(800, 500)
        
        self.setup_ui()
        self.create_menu()
        self.refresh_table()
    
    def setup_ui(self):
        """Setup all UI components"""
        # Create table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Service", "Username", "Password", "Notes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        # Create buttons with styling
        add_button = QPushButton("➕ Add")
        add_button.clicked.connect(self.add_entry)
        
        edit_button = QPushButton("✏️ Edit")
        edit_button.clicked.connect(self.edit_entry)
        
        delete_button = QPushButton("🗑️ Delete")
        delete_button.setObjectName("danger")  # For special styling
        delete_button.clicked.connect(self.delete_entry)
        
        copy_button = QPushButton("📋 Copy Password")
        copy_button.clicked.connect(self.copy_password)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(copy_button)
        button_layout.addStretch()
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        
        # Main layout
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.table)
        layout.addWidget(button_widget)
        self.setCentralWidget(central)
    
    def create_menu(self) -> None:
        """Create application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("🔓 File")
        
        lock_action = QAction("🔒 Lock", self)
        lock_action.triggered.connect(self.lock)
        file_menu.addAction(lock_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("🚪 Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def refresh_table(self) -> None:
        """Refresh the table with current data"""
        self.table.setRowCount(0)
        for entry in self.store.entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(entry.name))
            self.table.setItem(row, 1, QTableWidgetItem(entry.username))
            self.table.setItem(row, 2, QTableWidgetItem(entry.display_password()))
            self.table.setItem(row, 3, QTableWidgetItem(entry.notes))
    
    def add_entry(self) -> None:
        """Add a new password entry"""
        dialog = EntryDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entry = dialog.get_entry()
            if not entry.name or not entry.password:
                QMessageBox.warning(self, "Invalid", "Name and password are required!")
                return
            self.store.add_entry(entry)
            self.refresh_table()
            self.statusBar().showMessage(f"Added {entry.name}", 2000)
    
    def edit_entry(self) -> None:
        """Edit selected entry"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "No Selection", "Please select an entry to edit.")
            return
        
        current = self.store.entries[selected]
        dialog = EntryDialog(entry=current, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.get_entry()
            if not updated.name or not updated.password:
                QMessageBox.warning(self, "Invalid", "Name and password are required!")
                return
            self.store.update_entry(selected, updated)
            self.refresh_table()
            self.statusBar().showMessage(f"Updated {updated.name}", 2000)
    
    def delete_entry(self) -> None:
        """Delete selected entry"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "No Selection", "Please select an entry to delete.")
            return
        
        entry_name = self.store.entries[selected].name
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{entry_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.store.remove_entry(selected)
            self.refresh_table()
            self.statusBar().showMessage(f"Deleted {entry_name}", 2000)
    
    def copy_password(self) -> None:
        """Copy password of selected entry to clipboard"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "No Selection", "Please select an entry to copy.")
            return
        
        entry = self.store.entries[selected]
        QApplication.clipboard().setText(entry.password)
        
        # Visual feedback
        self.statusBar().showMessage(f"Copied password for {entry.name}", 2000)
        QMessageBox.information(self, "Copied", f"Password for '{entry.name}' copied to clipboard!")
    
    def lock(self) -> None:
        """Lock the application (quit - will ask for password again)"""
        self.close()
    
    def show_about(self) -> None:
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Password Manager",
            "🔐 Secure Password Manager\n\n"
            "Version: 1.0\n"
            "Built with PySide6\n\n"
            "All passwords are encrypted locally.\n"
            "Never stored in the cloud."
        )
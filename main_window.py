from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QMessageBox, QApplication, QLabel,
    QLineEdit, QStatusBar, QDialog
)


class ModernMainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setWindowTitle("SecureVault - Password Manager")
        self.setMinimumSize(900, 600)
        
        # Simple dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2f;
            }
            QMenuBar {
                background-color: #2a2a3a;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #4a6fa5;
            }
            QStatusBar {
                background-color: #2a2a3a;
                color: #aaa;
            }
        """)
        
        self.setup_ui()
        self.create_menu()
        self.setup_auto_lock()
        self.refresh_table()
    
    def setup_ui(self):
        """Simple UI setup"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔐 SecureVault")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4a6fa5;")
        layout.addWidget(title)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search passwords...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a3a;
                border: 1px solid #3a3a4a;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4a6fa5;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_input)
        
        # Stats bar (simple)
        self.stats_label = QLabel("📊 0 passwords stored")
        self.stats_label.setStyleSheet("color: #aaa; padding: 5px;")
        layout.addWidget(self.stats_label)
        
        # Password table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Website", "Username", "Password", "Notes"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a3a;
                alternate-background-color: #252535;
                color: white;
                gridline-color: #3a3a4a;
                border: none;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #4a6fa5;
            }
            QHeaderView::section {
                background-color: #1e1e2f;
                color: #aaa;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        btn_style = """
            QPushButton {
                background-color: #4a6fa5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5d7fb5;
            }
        """
        
        danger_style = """
            QPushButton {
                background-color: #a54a4a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b55d5d;
            }
        """
        
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setStyleSheet(btn_style)
        self.add_btn.clicked.connect(self.add_entry)
        
        self.edit_btn = QPushButton("✏ Edit")
        self.edit_btn.setStyleSheet(btn_style)
        self.edit_btn.clicked.connect(self.edit_entry)
        
        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.setStyleSheet(danger_style)
        self.delete_btn.clicked.connect(self.delete_entry)
        
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setStyleSheet(btn_style)
        self.copy_btn.clicked.connect(self.copy_password)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("color: #aaa;")
    
    def create_menu(self):
        """Simple menu"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        
        lock_action = QAction("Lock", self)
        lock_action.triggered.connect(self.lock)
        file_menu.addAction(lock_action)
        
        export_action = QAction("Export Backup", self)
        export_action.triggered.connect(self.export_backup)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_auto_lock(self):
        """Auto-lock after 5 minutes"""
        self.lock_timer = QTimer()
        self.lock_timer.setSingleShot(True)
        self.lock_timer.timeout.connect(self.auto_lock)
        self.reset_lock_timer()
        
        # Reset timer on user activity
        self.table.mousePressEvent = self.wrap_event(self.table.mousePressEvent)
        self.search_input.textChanged.connect(lambda: self.reset_lock_timer())
    
    def reset_lock_timer(self):
        self.lock_timer.start(300000)  # 5 minutes
    
    def wrap_event(self, original_event):
        def handler(event):
            self.reset_lock_timer()
            if original_event:
                original_event(event)
        return handler
    
    def auto_lock(self):
        self.close()
        QMessageBox.information(None, "Auto-Lock", "App locked due to inactivity")
    
    def update_stats(self):
        total = len(self.store.entries)
        weak = sum(1 for e in self.store.entries if len(e.password) < 8)
        
        if weak > 0:
            self.stats_label.setText(f"📊 {total} passwords | ⚠️ {weak} weak passwords")
        else:
            self.stats_label.setText(f"📊 {total} passwords | ✅ All passwords are strong")
    
    def refresh_table(self):
        """Refresh the table"""
        self.table.setRowCount(0)
        for entry in self.store.entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(entry.name))
            self.table.setItem(row, 1, QTableWidgetItem(entry.username))
            self.table.setItem(row, 2, QTableWidgetItem("••••••••"))
            self.table.setItem(row, 3, QTableWidgetItem(entry.notes))
        
        self.update_stats()
    
    def filter_table(self):
        """Filter based on search"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            show = item and search_text in item.text().lower()
            self.table.setRowHidden(row, not show)
    
    def export_backup(self):
        """Export to JSON"""
        from datetime import datetime
        import json
        
        backup_data = [entry.to_dict() for entry in self.store.entries]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            QMessageBox.information(self, "Success", f"Backup saved as {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def add_entry(self):
        from dialogs import ModernEntryDialog
        dialog = ModernEntryDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entry = dialog.get_entry()
            if not entry.name or not entry.password:
                QMessageBox.warning(self, "Error", "Name and password required!")
                return
            self.store.add_entry(entry)
            self.refresh_table()
            self.status_bar.showMessage(f"Added {entry.name}", 2000)
    
    def edit_entry(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Error", "Please select an entry")
            return
        
        from dialogs import ModernEntryDialog
        current = self.store.entries[selected]
        dialog = ModernEntryDialog(entry=current, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.get_entry()
            if not updated.name or not updated.password:
                QMessageBox.warning(self, "Error", "Name and password required!")
                return
            self.store.update_entry(selected, updated)
            self.refresh_table()
            self.status_bar.showMessage(f"Updated {updated.name}", 2000)
    
    def delete_entry(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Error", "Please select an entry")
            return
        
        entry_name = self.store.entries[selected].name
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete '{entry_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.store.remove_entry(selected)
            self.refresh_table()
            self.status_bar.showMessage(f"Deleted {entry_name}", 2000)
    
    def copy_password(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Error", "Please select an entry")
            return
        
        entry = self.store.entries[selected]
        QApplication.clipboard().setText(entry.password)
        self.status_bar.showMessage(f"Copied password for {entry.name}", 2000)
    
    def lock(self):
        self.close()
    
    def show_about(self):
        QMessageBox.about(
            self,
            "About SecureVault",
            "🔐 SecureVault Password Manager\n\n"
            "Simple, secure password manager\n"
            "Built with PySide6\n\n"
            "All passwords are encrypted locally."
        )
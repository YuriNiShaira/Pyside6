from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QDialogButtonBox,
    QMessageBox
)
from PySide6.QtCore import Qt

from models import PasswordEntry


class LoginDialog(QDialog):
    """Login dialog for master password"""
    def __init__(self, store_path: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Manager Login")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.store_path = store_path
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter your master password")
        
        # Style the dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #2a2a3a;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Icon/title area
        title = QLabel("🔐 Password Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        form = QFormLayout()
        form.addRow("Master password:", self.password_edit)
        layout.addLayout(form)
        
        # Buttons
        actions = QHBoxLayout()
        self.create_button = QPushButton("Unlock")
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        actions.addStretch(1)
        actions.addWidget(self.create_button)
        actions.addWidget(self.cancel_button)
        layout.addLayout(actions)
        
        self.setLayout(layout)

    @property
    def password(self) -> str:
        return self.password_edit.text().strip()


class EntryDialog(QDialog):
    """Dialog for adding/editing password entries"""
    def __init__(self, entry: PasswordEntry = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Password")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        # Create input fields
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Google, GitHub, Bank")
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("email@example.com or username")
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password")
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional notes")
        
        # Generate password button
        self.generate_btn = QPushButton("🎲 Generate Strong Password")
        self.generate_btn.clicked.connect(self.generate_password)
        
        # Fill if editing
        if entry is not None:
            self.name_edit.setText(entry.name)
            self.username_edit.setText(entry.username)
            self.password_edit.setText(entry.password)
            self.notes_edit.setText(entry.notes)
        
        # Layout
        layout = QFormLayout()
        layout.addRow("Service Name:", self.name_edit)
        layout.addRow("Username/Email:", self.username_edit)
        layout.addRow("Password:", self.password_edit)
        layout.addRow("", self.generate_btn)
        layout.addRow("Notes:", self.notes_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)
    
    def generate_password(self) -> None:
        """Generate a strong random password"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(16))
        self.password_edit.setText(password)
    
    def get_entry(self) -> PasswordEntry:
        """Get the entered data as a PasswordEntry"""
        return PasswordEntry(
            name=self.name_edit.text().strip(),
            username=self.username_edit.text().strip(),
            password=self.password_edit.text().strip(),
            notes=self.notes_edit.text().strip(),
        )
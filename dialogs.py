from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QDialogButtonBox,
    QMessageBox, QFrame
)
from models import PasswordEntry


class ModernLoginDialog(QDialog):
    def __init__(self, store_path: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SecureVault - Login")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        # Set style for the dialog itself
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2f;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #2a2a3a;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4a6fa5;
            }
            QPushButton {
                background-color: #4a6fa5;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5d7fb5;
            }
            QPushButton#cancel {
                background-color: transparent;
                border: 1px solid #3a3a4a;
            }
            QPushButton#cancel:hover {
                background-color: #2a2a3a;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🔐 SecureVault")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4a6fa5; margin-top: 20px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Enter your master password to unlock")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Master password")
        layout.addWidget(self.password_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.unlock_btn = QPushButton("Unlock")
        self.unlock_btn.setDefault(True)
        self.unlock_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.unlock_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Enter key shortcut
        self.password_edit.returnPressed.connect(self.unlock_btn.click)
    
    @property
    def password(self) -> str:
        return self.password_edit.text().strip()


class ModernEntryDialog(QDialog):
    def __init__(self, entry: PasswordEntry = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Password")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2f;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #2a2a3a;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4a6fa5;
            }
            QPushButton {
                background-color: #4a6fa5;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5d7fb5;
            }
            QPushButton#generate {
                background-color: #4a9a5a;
                max-width: 100px;
            }
            QPushButton#generate:hover {
                background-color: #5daa6d;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🔐 Password Details")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a6fa5; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Google, Facebook")
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("email@example.com")
        
        # Password with generate button
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password")
        
        self.generate_btn = QPushButton("🎲 Generate")
        self.generate_btn.setObjectName("generate")
        self.generate_btn.clicked.connect(self.generate_password)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_edit)
        password_layout.addWidget(self.generate_btn)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional notes")
        
        form_layout.addRow("Service:", self.name_edit)
        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Password:", password_layout)
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        # OK/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Fill if editing
        if entry is not None:
            self.name_edit.setText(entry.name)
            self.username_edit.setText(entry.username)
            self.password_edit.setText(entry.password)
            self.notes_edit.setText(entry.notes)
    
    def generate_password(self):
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(16))
        self.password_edit.setText(password)
    
    def get_entry(self) -> PasswordEntry:
        return PasswordEntry(
            name=self.name_edit.text().strip(),
            username=self.username_edit.text().strip(),
            password=self.password_edit.text().strip(),
            notes=self.notes_edit.text().strip(),
        )


# Keep compatibility
class LoginDialog(ModernLoginDialog):
    pass

class EntryDialog(ModernEntryDialog):
    pass
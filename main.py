from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass
class PasswordEntry:
    name: str
    username: str
    password: str
    notes: str = ""


class PasswordStore:
    SALT_SIZE = 16
    NONCE_SIZE = 12
    ITERATIONS = 200_000

    def __init__(self, path: Path, master_password: str):
        self.path = path
        self.master_password = master_password.encode("utf-8")
        self._data: List[PasswordEntry] = []

    def _derive_key(self, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        return kdf.derive(self.master_password)

    def load(self) -> None:
        if not self.path.exists():
            self._data = []
            return

        raw = self.path.read_bytes()
        if len(raw) < self.SALT_SIZE + self.NONCE_SIZE:
            raise ValueError("Store file is corrupted or too short.")

        salt = raw[: self.SALT_SIZE]
        nonce = raw[self.SALT_SIZE : self.SALT_SIZE + self.NONCE_SIZE]
        ciphertext = raw[self.SALT_SIZE + self.NONCE_SIZE :]

        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        data = json.loads(decrypted.decode("utf-8"))
        self._data = [PasswordEntry(**entry) for entry in data]

    def save(self) -> None:
        salt = os.urandom(self.SALT_SIZE)
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(self.NONCE_SIZE)
        payload = json.dumps([asdict(entry) for entry in self._data], indent=2).encode("utf-8")
        ciphertext = aesgcm.encrypt(nonce, payload, None)
        self.path.write_bytes(salt + nonce + ciphertext)

    @property
    def entries(self) -> List[PasswordEntry]:
        return self._data

    def add_entry(self, entry: PasswordEntry) -> None:
        self._data.append(entry)
        self.save()

    def update_entry(self, index: int, entry: PasswordEntry) -> None:
        self._data[index] = entry
        self.save()

    def remove_entry(self, index: int) -> None:
        del self._data[index]
        self.save()


class LoginDialog(QDialog):
    def __init__(self, store_path: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Manager Login")
        self.store_path = store_path
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Master password")

        self.create_button = QPushButton("Open")
        self.create_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter your master password."))
        form = QFormLayout()
        form.addRow("Master password:", self.password_edit)
        layout.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(self.create_button)
        actions.addWidget(self.cancel_button)
        layout.addLayout(actions)
        self.setLayout(layout)

    @property
    def password(self) -> str:
        return self.password_edit.text().strip()


class EntryDialog(QDialog):
    def __init__(self, entry: PasswordEntry = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Entry")

        self.name_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.notes_edit = QLineEdit()

        if entry is not None:
            self.name_edit.setText(entry.name)
            self.username_edit.setText(entry.username)
            self.password_edit.setText(entry.password)
            self.notes_edit.setText(entry.notes)

        layout = QFormLayout()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Username:", self.username_edit)
        layout.addRow("Password:", self.password_edit)
        layout.addRow("Notes:", self.notes_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def get_entry(self) -> PasswordEntry:
        return PasswordEntry(
            name=self.name_edit.text().strip(),
            username=self.username_edit.text().strip(),
            password=self.password_edit.text().strip(),
            notes=self.notes_edit.text().strip(),
        )


class PasswordManagerMainWindow(QMainWindow):
    def __init__(self, store: PasswordStore):
        super().__init__()
        self.store = store
        self.setWindowTitle("Password Manager")
        self.resize(700, 450)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Username", "Password", "Notes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_entry)
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_entry)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_entry)
        copy_button = QPushButton("Copy Password")
        copy_button.clicked.connect(self.copy_password)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(copy_button)
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.table)
        layout.addWidget(button_widget)
        self.setCentralWidget(central)

        self.create_menu()
        self.refresh_table()

    def create_menu(self) -> None:
        menu = self.menuBar().addMenu("File")
        lock_action = QAction("Lock", self)
        lock_action.triggered.connect(self.lock)
        menu.addAction(lock_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

    def refresh_table(self) -> None:
        self.table.setRowCount(0)
        for entry in self.store.entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(entry.name))
            self.table.setItem(row, 1, QTableWidgetItem(entry.username))
            self.table.setItem(row, 2, QTableWidgetItem("•" * len(entry.password)))
            self.table.setItem(row, 3, QTableWidgetItem(entry.notes))

    def add_entry(self) -> None:
        dialog = EntryDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            entry = dialog.get_entry()
            if not entry.name or not entry.password:
                QMessageBox.warning(self, "Invalid entry", "Name and password are required.")
                return
            self.store.add_entry(entry)
            self.refresh_table()

    def edit_entry(self) -> None:
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Select row", "Please select an entry to edit.")
            return
        current = self.store.entries[selected]
        dialog = EntryDialog(entry=current, parent=self)
        if dialog.exec() == QDialog.Accepted:
            updated = dialog.get_entry()
            if not updated.name or not updated.password:
                QMessageBox.warning(self, "Invalid entry", "Name and password are required.")
                return
            self.store.update_entry(selected, updated)
            self.refresh_table()

    def delete_entry(self) -> None:
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Select row", "Please select an entry to delete.")
            return
        if QMessageBox.question(
            self,
            "Delete entry",
            "Are you sure you want to delete this entry?",
            QMessageBox.Yes | QMessageBox.No,
        ) == QMessageBox.Yes:
            self.store.remove_entry(selected)
            self.refresh_table()

    def copy_password(self) -> None:
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Select row", "Please select an entry to copy.")
            return
        entry = self.store.entries[selected]
        QApplication.clipboard().setText(entry.password)
        QMessageBox.information(self, "Copied", "Password copied to clipboard.")

    def lock(self) -> None:
        QApplication.quit()


def main() -> int:
    app = QApplication(sys.argv)
    store_path = Path(__file__).resolve().parent / "passwords.enc"
    login = LoginDialog(store_path)
    if login.exec() != QDialog.Accepted:
        return 0

    if not login.password:
        QMessageBox.warning(None, "Master password required", "Enter a non-empty master password.")
        return 0

    store = PasswordStore(store_path, login.password)
    try:
        store.load()
    except Exception as exc:
        QMessageBox.critical(None, "Unable to load store", f"Could not open password store: {exc}")
        return 1

    window = PasswordManagerMainWindow(store)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

"""Handles encryption and file storage - like backend API"""
import json
import os
from pathlib import Path
from typing import List

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from models import PasswordEntry


class PasswordStore:
    """Manages encrypted storage of passwords"""
    SALT_SIZE = 16
    NONCE_SIZE = 12
    ITERATIONS = 200_000

    def __init__(self, path: Path, master_password: str):
        self.path = path
        self.master_password = master_password.encode("utf-8")
        self._data: List[PasswordEntry] = []

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from master password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        return kdf.derive(self.master_password)

    def load(self) -> None:
        """Load and decrypt the password store"""
        if not self.path.exists():
            self._data = []
            return

        raw = self.path.read_bytes()
        if len(raw) < self.SALT_SIZE + self.NONCE_SIZE:
            raise ValueError("Store file is corrupted or too short.")

        salt = raw[:self.SALT_SIZE]
        nonce = raw[self.SALT_SIZE:self.SALT_SIZE + self.NONCE_SIZE]
        ciphertext = raw[self.SALT_SIZE + self.NONCE_SIZE:]

        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        data = json.loads(decrypted.decode("utf-8"))
        self._data = [PasswordEntry.from_dict(entry) for entry in data]

    def save(self) -> None:
        """Encrypt and save the password store"""
        salt = os.urandom(self.SALT_SIZE)
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(self.NONCE_SIZE)
        
        # Convert entries to serializable format
        entries_data = [entry.to_dict() for entry in self._data]
        payload = json.dumps(entries_data, indent=2).encode("utf-8")
        ciphertext = aesgcm.encrypt(nonce, payload, None)
        self.path.write_bytes(salt + nonce + ciphertext)

    @property
    def entries(self) -> List[PasswordEntry]:
        """Get all entries"""
        return self._data

    def add_entry(self, entry: PasswordEntry) -> None:
        """Add a new entry"""
        self._data.append(entry)
        self.save()

    def update_entry(self, index: int, entry: PasswordEntry) -> None:
        """Update an existing entry"""
        self._data[index] = entry
        self.save()

    def remove_entry(self, index: int) -> None:
        """Remove an entry"""
        del self._data[index]
        self.save()
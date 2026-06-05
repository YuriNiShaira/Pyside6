"""Data models - like database schema"""
from dataclasses import dataclass
from typing import List

@dataclass
class PasswordEntry:
    """Represents a single password entry"""
    name: str
    username: str
    password: str
    notes: str = ""
    
    def display_password(self) -> str:
        """Return masked password for display"""
        return "•" * len(self.password)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage"""
        return {
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PasswordEntry':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            username=data['username'],
            password=data['password'],
            notes=data.get('notes', '')
        )
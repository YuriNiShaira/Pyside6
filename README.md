# PySide6 Password Manager

A simple desktop password manager built with PySide6 and encrypted storage using `cryptography`.

## Features

- Master password protected store
- Add / edit / delete password entries
- Copy password to clipboard
- Encrypted local store file: `passwords.enc`

## Setup

1. Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python main.py
```

## Notes

- The first run creates a new encrypted store file at `passwords.enc`.
- Keep your master password safe: losing it means the store cannot be decrypted.

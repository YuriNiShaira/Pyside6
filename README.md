# SecureVault — Build & Distribution

This document explains how to build a Windows executable, create an installer, and sign releases for distribution.

**Prerequisites**
- Windows development machine
- Python 3.10+ and `pip`
- `git` (optional)

Install runtime dependencies:
```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller cairosvg pillow
```

1) Build a Windows EXE (PyInstaller)
- A prepared helper script is included: `build_windows.ps1` — it installs deps, generates `assets/lock.ico`, and runs PyInstaller.

Run from the repo root (PowerShell):
```powershell
.\\build_windows.ps1
# Output will be under the `dist` folder (e.g. `dist\SecureVault.exe`).
```

Notes:
- The script uses `--onefile` by default. To produce a folder build, run PyInstaller manually with `--onedir`.
- Ensure `assets/` is bundled (`--add-data "assets;assets"` is used in the script).
- When running the packaged EXE, the encrypted store is saved in a stable app data folder, not the temporary extracted path. On Windows this location is typically:
  `C:\Users\<your-user>\AppData\Roaming\SecureVault\passwords.enc`
- If an older local `passwords.enc` exists beside the script, the next run will migrate it automatically to the app data folder.

2) Create a Windows installer (Inno Setup)
- Install Inno Setup from: https://jrsoftware.org/
- Example minimal script (`securevault.iss`):
```
[Setup]
AppName=SecureVault
AppVersion=1.0
DefaultDirName={pf}\SecureVault
DefaultGroupName=SecureVault
OutputBaseFilename=SecureVaultInstaller
Compression=lzma
SolidCompression=yes

[Files]
; Include the single EXE or the whole dist folder
Source: "dist\SecureVault.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SecureVault"; Filename: "{app}\SecureVault.exe"
```

Build the installer from the Inno Setup Compiler (ISCC):
```powershell
# Example path — adjust to your installation
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" securevault.iss
```

3) Code signing (Windows)
- Code signing improves trust and prevents SmartScreen warnings. Recommended: an EV code signing certificate from a trusted CA (DigiCert, Sectigo, etc.).
- Basic `signtool` example (requires Windows SDK):
```powershell
# Using a PFX file
signtool sign /fd SHA256 /f "C:\path\to\cert.pfx" /p "pfx-password" /tr http://timestamp.digicert.com /td SHA256 "dist\SecureVault.exe"

# Using default certificate store (auto select)
signtool sign /fd SHA256 /a /tr http://timestamp.digicert.com /td SHA256 "dist\SecureVault.exe"
```

Recommendations:
- Use SHA-256 timestamping (`/tr` + `/td SHA256`).
- Prefer EV certificates (hardware-backed or HSM) for faster reputation buildup.
- For CI/CD, consider secure secrets storage for PFX passwords or use Azure Key Vault / SignService.

4) Testing & distribution
- Test the installer on a clean VM to ensure no missing runtime files and to verify antivirus behaviour.
- If distributing broadly, consider notarization and submission to the Microsoft Store (requires MSIX packaging and publisher validation).

5) Sharing with friends
- The simplest share method is to send the packaged EXE from `dist\SecureVault.exe`.
- Your friend can run the EXE directly on Windows; they do not need Python installed.
- For a more polished experience, build an installer with Inno Setup and share the installer file.
- The app stores each user’s data locally in:
  `C:\Users\<user>\AppData\Roaming\SecureVault\passwords.enc`
- Each friend will have their own independent store file; your store remains separate.
- Make sure they keep their master password safe, since it cannot be recovered.

6) macOS and Linux (notes)
- macOS: use PyInstaller or `py2app` and create a signed `.app` bundle and notarize with Apple (requires Apple Developer account). Create a `.dmg` or `.pkg` for distribution.
- Linux: build with PyInstaller and optionally create an AppImage, Snap, or Flatpak for user-friendly distribution.

6) Mobile distribution (recommendation)
- Converting this exact Python+Qt desktop app to mobile is difficult. The recommended path for phone installs is to build a web frontend (PWA) and/or a native mobile UI using a mobile-capable framework.

Where to go next
- Create an Inno Setup script and I can add it to the repo.
- Add CI steps (GitHub Actions) to build, sign, and publish releases automatically.

File references:
- Build script: `build_windows.ps1`
- Icon generator: `tools/make_icons.py`
- Entry point: `main.py`
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

# Build script for Windows: creates .ico from SVG and builds exe with PyInstaller
Set-StrictMode -Version Latest

Write-Host "Installing build dependencies..."
python -m pip install --upgrade pip
python -m pip install pyinstaller cairosvg pillow

Write-Host "Generating icon (assets/lock.ico) from assets/lock.svg..."
python tools\make_icons.py

Write-Host "Running PyInstaller..."
# Use onefile build and include assets folder. Adjust --onefile/--onedir as desired.
pyinstaller --noconfirm --onefile --windowed --name SecureVault --icon assets\lock.ico --add-data "assets;assets" main.py

Write-Host "Build complete. See dist\SecureVault.exe or dist\SecureVault\ depending on --onefile/--onedir choice."
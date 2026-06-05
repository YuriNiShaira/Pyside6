"""All the styling for the app - like CSS file"""

# Modern dark theme
DARK_STYLE = """
QMainWindow {
    background-color: #1e1e2f;
}

QTableWidget {
    background-color: #2a2a3a;
    alternate-background-color: #2f2f3f;
    color: #ffffff;
    gridline-color: #3a3a4a;
    selection-background-color: #4a6fa5;
    border: none;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #4a6fa5;
}

QHeaderView::section {
    background-color: #3a3a4a;
    color: #ffffff;
    padding: 8px;
    border: none;
    font-weight: bold;
}

QPushButton {
    background-color: #4a6fa5;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #5d7fb5;
}

QPushButton:pressed {
    background-color: #3a5a8a;
}

QPushButton#danger {
    background-color: #a54a4a;
}

QPushButton#danger:hover {
    background-color: #b55d5d;
}

QLineEdit, QTextEdit {
    background-color: #2a2a3a;
    color: #ffffff;
    border: 1px solid #4a4a5a;
    border-radius: 4px;
    padding: 6px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #4a6fa5;
}

QLabel {
    color: #e0e0e0;
}

QDialog {
    background-color: #2a2a3a;
}

QMenuBar {
    background-color: #2a2a3a;
    color: #ffffff;
}

QMenuBar::item:selected {
    background-color: #4a6fa5;
}

QMessageBox {
    background-color: #2a2a3a;
}
"""

# Light theme alternative (uncomment to use)
LIGHT_STYLE = """
QMainWindow {
    background-color: #f5f5f5;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f9f9f9;
    color: #333333;
    gridline-color: #e0e0e0;
    selection-background-color: #4a6fa5;
    selection-color: white;
}

QPushButton {
    background-color: #4a6fa5;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #5d7fb5;
}

QLineEdit {
    background-color: white;
    color: #333;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px;
}
"""

def apply_style(app):
    """Apply the style to the application"""
    app.setStyleSheet(DARK_STYLE)  # Use DARK_STYLE or LIGHT_STYLE
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QIcon
import hashlib
import os
import json

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Email Automation Bot - Login")
        self.setFixedSize(1200, 800)
        self.setModal(True)
        
        # Set window icon
        self.setWindowIcon(self.create_login_icon())
        
        # Initialize UI
        self.init_ui()
        
        # Load saved credentials
        self.load_saved_credentials()
        
        # Apply styles
        self.apply_styles()
    
    def create_login_icon(self):
        """Create login dialog icon"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(52, 152, 219))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, '🔐')
        painter.end()
        
        return QIcon(pixmap)
    
    def init_ui(self):
        """Initialize the login UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Email Automation Bot")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Please enter your credentials to continue")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Login form
        form_group = QGroupBox("Login Credentials")
        form_layout = QVBoxLayout(form_group)
        
        # Username
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.setVisible(True)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_edit)
        
        # Password
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setVisible(True)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_edit)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        form_layout.addWidget(self.remember_checkbox)
        
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.login)
        
        self.register_button = QPushButton("Register")
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.register)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Set default button
        self.login_button.setDefault(True)
        
        # Connect Enter key to login
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.login)
    
    def apply_styles(self):
        """Apply modern theme styles to the login dialog"""
        style = """
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #023047, stop:1 #219ebc);
            border-radius: 12px;
        }
        
        #titleLabel {
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        #subtitleLabel {
            font-size: 16px;
            color: #8ecae6;
            margin-bottom: 20px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #8ecae6;
            border-radius: 8px;
            margin: 10px;
            padding: 20px;
            background-color: #023047;
            color: #ffffff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #ffffff;
            font-size: 14px;
        }
        
        QLabel {
            color: #ffffff;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        QLineEdit {
            border: 2px solid #8ecae6;
            border-radius: 8px;
            padding: 14px 16px;
            font-size: 15px;
            margin-bottom: 15px;
            background-color: #219ebc;
            color: #ffffff;
            selection-background-color: #ffb703;
            min-height: 20px;
            max-height: 50px;
        }
        
        QLineEdit:focus {
            border-color: #ffb703;
            background-color: #8ecae6;
            color: #023047;
        }
        
        QLineEdit::placeholder {
            color: #8ecae6;
        }
        
        QCheckBox {
            color: #ffffff;
            font-weight: normal;
            spacing: 10px;
            font-size: 14px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #8ecae6;
            background-color: #023047;
        }
        
        QCheckBox::indicator:checked {
            background-color: #ffb703;
            border-color: #ffb703;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }
        
        #loginButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #ffb703, stop:1 #fb8500);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 15px;
            min-width: 100px;
        }
        
        #loginButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #fb8500, stop:1 #ffb703);
            transform: translateY(-1px);
        }
        
        #loginButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #219ebc, stop:1 #8ecae6);
        }
        
        #registerButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #219ebc, stop:1 #8ecae6);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 15px;
            min-width: 100px;
        }
        
        #registerButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #8ecae6, stop:1 #219ebc);
            transform: translateY(-1px);
        }
        
        #registerButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #023047, stop:1 #219ebc);
        }
        
        #cancelButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #8ecae6, stop:1 #219ebc);
            color: #023047;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 15px;
            min-width: 100px;
        }
        
        #cancelButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #219ebc, stop:1 #023047);
            color: white;
            transform: translateY(-1px);
        }
        
        #cancelButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #023047, stop:1 #219ebc);
        }
        
        QPushButton {
            transition: all 0.2s ease;
        }
        """
        
        self.setStyleSheet(style)
    
    def get_credentials_file(self):
        """Get path to credentials file"""
        return "user_credentials.json"
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_saved_credentials(self):
        """Load saved credentials if remember me was checked"""
        try:
            credentials_file = self.get_credentials_file()
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as f:
                    data = json.load(f)
                    if data.get('remember', False):
                        self.username_edit.setText(data.get('username', ''))
                        self.remember_checkbox.setChecked(True)
        except Exception:
            pass  # Ignore errors loading credentials
    
    def save_credentials(self, username, password_hash, remember):
        """Save credentials to file"""
        try:
            credentials_file = self.get_credentials_file()
            data = {
                'username': username,
                'password_hash': password_hash,
                'remember': remember
            }
            with open(credentials_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not save credentials: {str(e)}")
    
    def load_user_credentials(self):
        """Load user credentials from file"""
        try:
            credentials_file = self.get_credentials_file()
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def verify_credentials(self, username, password):
        """Verify user credentials"""
        credentials = self.load_user_credentials()
        if not credentials:
            return False
        
        return (credentials.get('username') == username and 
                credentials.get('password_hash') == self.hash_password(password))
    
    def login(self):
        """Handle login attempt"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return
        
        # Check if user exists
        if not self.load_user_credentials():
            QMessageBox.information(
                self, "No Account", 
                "No user account found. Please register first."
            )
            return
        
        # Verify credentials
        if self.verify_credentials(username, password):
            # Save credentials if remember me is checked
            if self.remember_checkbox.isChecked():
                self.save_credentials(username, self.hash_password(password), True)
            else:
                # Clear remember flag
                credentials = self.load_user_credentials()
                if credentials:
                    credentials['remember'] = False
                    with open(self.get_credentials_file(), 'w') as f:
                        json.dump(credentials, f)
            
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def register(self):
        """Handle user registration"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters long.")
            return
        
        # Check if user already exists
        if self.load_user_credentials():
            reply = QMessageBox.question(
                self, "User Exists", 
                "A user account already exists. Do you want to update the password?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Save new credentials
        password_hash = self.hash_password(password)
        self.save_credentials(username, password_hash, self.remember_checkbox.isChecked())
        
        QMessageBox.information(
            self, "Success", 
            "User account created/updated successfully! You can now login."
        )
        
        # Clear password field
        self.password_edit.clear()
        self.username_edit.setFocus()
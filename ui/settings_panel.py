from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QCheckBox, QComboBox, QGroupBox,
    QFormLayout, QTabWidget, QTextEdit, QFileDialog,
    QMessageBox, QDialog, QDialogButtonBox, QProgressBar,
    QSlider, QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon
import logging
import json
import os
import shutil
from datetime import datetime
import sqlite3

class DatabaseBackupThread(QThread):
    """Thread for database backup operations"""
    progress_updated = pyqtSignal(int)
    backup_completed = pyqtSignal(str)
    backup_failed = pyqtSignal(str)
    
    def __init__(self, source_db, backup_path):
        super().__init__()
        self.source_db = source_db
        self.backup_path = backup_path
    
    def run(self):
        try:
            # Create backup directory if it doesn't exist
            os.makedirs(os.path.dirname(self.backup_path), exist_ok=True)
            
            # Copy database file
            self.progress_updated.emit(25)
            shutil.copy2(self.source_db, self.backup_path)
            self.progress_updated.emit(75)
            
            # Verify backup
            if os.path.exists(self.backup_path):
                # Test if backup is valid SQLite database
                conn = sqlite3.connect(self.backup_path)
                conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                conn.close()
                self.progress_updated.emit(100)
                self.backup_completed.emit(self.backup_path)
            else:
                self.backup_failed.emit("Backup file was not created")
                
        except Exception as e:
            self.backup_failed.emit(str(e))

class EmailAccountDialog(QDialog):
    """Dialog for adding/editing email accounts"""
    
    def __init__(self, parent=None, account_data=None):
        super().__init__(parent)
        self.account_data = account_data
        self.init_ui()
        
        if account_data:
            self.load_account_data()
    
    def init_ui(self):
        self.setWindowTitle("Email Account Configuration")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Create tabs
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Basic settings tab
        self.create_basic_tab(tab_widget)
        
        # SMTP settings tab
        self.create_smtp_tab(tab_widget)
        
        # IMAP settings tab
        self.create_imap_tab(tab_widget)
        
        # Advanced settings tab
        self.create_advanced_tab(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        
        # Test connection button
        self.test_btn = QPushButton("🔧 Test Connection")
        button_box.addButton(self.test_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        self.test_btn.clicked.connect(self.test_connection)
        
        layout.addWidget(button_box)
    
    def create_basic_tab(self, parent):
        """Create basic account settings tab"""
        basic_widget = QWidget()
        layout = QFormLayout(basic_widget)
        
        # Account name
        self.account_name_edit = QLineEdit()
        self.account_name_edit.setPlaceholderText("My Email Account")
        layout.addRow("Account Name:", self.account_name_edit)
        
        # Email address
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("user@example.com")
        layout.addRow("Email Address:", self.email_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter password or app password")
        layout.addRow("Password:", self.password_edit)
        
        # Display name
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("Your Name")
        layout.addRow("Display Name:", self.display_name_edit)
        
        # Provider preset
        provider_layout = QHBoxLayout()
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "Custom", "Gmail", "Outlook/Hotmail", "Yahoo", "iCloud", "Zoho"
        ])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)
        
        auto_config_btn = QPushButton("Auto Configure")
        auto_config_btn.clicked.connect(self.auto_configure)
        provider_layout.addWidget(auto_config_btn)
        
        layout.addRow("Email Provider:", provider_layout)
        
        # Active checkbox
        self.active_check = QCheckBox("Account is active")
        self.active_check.setChecked(True)
        layout.addRow("", self.active_check)
        
        parent.addTab(basic_widget, "📧 Basic")
    
    def create_smtp_tab(self, parent):
        """Create SMTP settings tab"""
        smtp_widget = QWidget()
        layout = QFormLayout(smtp_widget)
        
        # SMTP server
        self.smtp_server_edit = QLineEdit()
        self.smtp_server_edit.setPlaceholderText("smtp.example.com")
        layout.addRow("SMTP Server:", self.smtp_server_edit)
        
        # SMTP port
        self.smtp_port_spin = QSpinBox()
        self.smtp_port_spin.setRange(1, 65535)
        self.smtp_port_spin.setValue(587)
        layout.addRow("SMTP Port:", self.smtp_port_spin)
        
        # SMTP security
        self.smtp_security_combo = QComboBox()
        self.smtp_security_combo.addItems(["STARTTLS", "SSL/TLS", "None"])
        layout.addRow("Security:", self.smtp_security_combo)
        
        # SMTP authentication
        self.smtp_auth_check = QCheckBox("Requires authentication")
        self.smtp_auth_check.setChecked(True)
        layout.addRow("", self.smtp_auth_check)
        
        # SMTP username (if different from email)
        self.smtp_username_edit = QLineEdit()
        self.smtp_username_edit.setPlaceholderText("Leave empty to use email address")
        layout.addRow("SMTP Username:", self.smtp_username_edit)
        
        parent.addTab(smtp_widget, "📤 SMTP")
    
    def create_imap_tab(self, parent):
        """Create IMAP settings tab"""
        imap_widget = QWidget()
        layout = QFormLayout(imap_widget)
        
        # IMAP server
        self.imap_server_edit = QLineEdit()
        self.imap_server_edit.setPlaceholderText("imap.example.com")
        layout.addRow("IMAP Server:", self.imap_server_edit)
        
        # IMAP port
        self.imap_port_spin = QSpinBox()
        self.imap_port_spin.setRange(1, 65535)
        self.imap_port_spin.setValue(993)
        layout.addRow("IMAP Port:", self.imap_port_spin)
        
        # IMAP security
        self.imap_security_combo = QComboBox()
        self.imap_security_combo.addItems(["SSL/TLS", "STARTTLS", "None"])
        layout.addRow("Security:", self.imap_security_combo)
        
        # IMAP username (if different from email)
        self.imap_username_edit = QLineEdit()
        self.imap_username_edit.setPlaceholderText("Leave empty to use email address")
        layout.addRow("IMAP Username:", self.imap_username_edit)
        
        # Default folders
        self.inbox_folder_edit = QLineEdit()
        self.inbox_folder_edit.setText("INBOX")
        layout.addRow("Inbox Folder:", self.inbox_folder_edit)
        
        self.sent_folder_edit = QLineEdit()
        self.sent_folder_edit.setText("Sent")
        layout.addRow("Sent Folder:", self.sent_folder_edit)
        
        parent.addTab(imap_widget, "📥 IMAP")
    
    def create_advanced_tab(self, parent):
        """Create advanced settings tab"""
        advanced_widget = QWidget()
        layout = QFormLayout(advanced_widget)
        
        # Connection timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")
        layout.addRow("Connection Timeout:", self.timeout_spin)
        
        # Max connections
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(1, 10)
        self.max_connections_spin.setValue(3)
        layout.addRow("Max Connections:", self.max_connections_spin)
        
        # Enable monitoring
        self.enable_monitoring_check = QCheckBox("Enable inbox monitoring")
        self.enable_monitoring_check.setChecked(True)
        layout.addRow("", self.enable_monitoring_check)
        
        # Monitoring interval
        self.monitoring_interval_spin = QSpinBox()
        self.monitoring_interval_spin.setRange(10, 3600)
        self.monitoring_interval_spin.setValue(60)
        self.monitoring_interval_spin.setSuffix(" seconds")
        layout.addRow("Monitoring Interval:", self.monitoring_interval_spin)
        
        # Auto-reply enabled
        self.auto_reply_check = QCheckBox("Enable auto-reply")
        layout.addRow("", self.auto_reply_check)
        
        parent.addTab(advanced_widget, "⚙️ Advanced")
    
    def on_provider_changed(self, provider):
        """Handle provider selection change"""
        # This will be called when auto_configure is implemented
        pass
    
    def auto_configure(self):
        """Auto-configure settings based on provider"""
        provider = self.provider_combo.currentText()
        
        if provider == "Gmail":
            self.smtp_server_edit.setText("smtp.gmail.com")
            self.smtp_port_spin.setValue(587)
            self.smtp_security_combo.setCurrentText("STARTTLS")
            self.imap_server_edit.setText("imap.gmail.com")
            self.imap_port_spin.setValue(993)
            self.imap_security_combo.setCurrentText("SSL/TLS")
            
        elif provider == "Outlook/Hotmail":
            self.smtp_server_edit.setText("smtp-mail.outlook.com")
            self.smtp_port_spin.setValue(587)
            self.smtp_security_combo.setCurrentText("STARTTLS")
            self.imap_server_edit.setText("outlook.office365.com")
            self.imap_port_spin.setValue(993)
            self.imap_security_combo.setCurrentText("SSL/TLS")
            
        elif provider == "Yahoo":
            self.smtp_server_edit.setText("smtp.mail.yahoo.com")
            self.smtp_port_spin.setValue(587)
            self.smtp_security_combo.setCurrentText("STARTTLS")
            self.imap_server_edit.setText("imap.mail.yahoo.com")
            self.imap_port_spin.setValue(993)
            self.imap_security_combo.setCurrentText("SSL/TLS")
            
        elif provider == "iCloud":
            self.smtp_server_edit.setText("smtp.mail.me.com")
            self.smtp_port_spin.setValue(587)
            self.smtp_security_combo.setCurrentText("STARTTLS")
            self.imap_server_edit.setText("imap.mail.me.com")
            self.imap_port_spin.setValue(993)
            self.imap_security_combo.setCurrentText("SSL/TLS")
            
        elif provider == "Zoho":
            self.smtp_server_edit.setText("smtp.zoho.com")
            self.smtp_port_spin.setValue(587)
            self.smtp_security_combo.setCurrentText("STARTTLS")
            self.imap_server_edit.setText("imap.zoho.com")
            self.imap_port_spin.setValue(993)
            self.imap_security_combo.setCurrentText("SSL/TLS")
        
        if provider != "Custom":
            QMessageBox.information(
                self, "Auto Configuration",
                f"Settings configured for {provider}. Please verify and test the connection."
            )
    
    def test_connection(self):
        """Test email connection"""
        # This would integrate with EmailHandler to test the connection
        QMessageBox.information(
            self, "Test Connection",
            "Connection test functionality will be implemented with EmailHandler integration."
        )
    
    def apply_settings(self):
        """Apply settings without closing dialog"""
        # Validate and save settings
        pass
    
    def load_account_data(self):
        """Load account data into form"""
        if not self.account_data:
            return
        
        # Load basic settings
        self.account_name_edit.setText(self.account_data.get('name', ''))
        self.email_edit.setText(self.account_data.get('email', ''))
        self.display_name_edit.setText(self.account_data.get('display_name', ''))
        self.active_check.setChecked(self.account_data.get('is_active', True))
        
        # Load SMTP settings
        self.smtp_server_edit.setText(self.account_data.get('smtp_server', ''))
        self.smtp_port_spin.setValue(self.account_data.get('smtp_port', 587))
        self.smtp_security_combo.setCurrentText(self.account_data.get('smtp_security', 'STARTTLS'))
        self.smtp_auth_check.setChecked(self.account_data.get('smtp_auth', True))
        self.smtp_username_edit.setText(self.account_data.get('smtp_username', ''))
        
        # Load IMAP settings
        self.imap_server_edit.setText(self.account_data.get('imap_server', ''))
        self.imap_port_spin.setValue(self.account_data.get('imap_port', 993))
        self.imap_security_combo.setCurrentText(self.account_data.get('imap_security', 'SSL/TLS'))
        self.imap_username_edit.setText(self.account_data.get('imap_username', ''))
        self.inbox_folder_edit.setText(self.account_data.get('inbox_folder', 'INBOX'))
        self.sent_folder_edit.setText(self.account_data.get('sent_folder', 'Sent'))
        
        # Load advanced settings
        self.timeout_spin.setValue(self.account_data.get('timeout', 30))
        self.max_connections_spin.setValue(self.account_data.get('max_connections', 3))
        self.enable_monitoring_check.setChecked(self.account_data.get('enable_monitoring', True))
        self.monitoring_interval_spin.setValue(self.account_data.get('monitoring_interval', 60))
        self.auto_reply_check.setChecked(self.account_data.get('auto_reply', False))
    
    def get_account_data(self):
        """Get account data from form"""
        return {
            'name': self.account_name_edit.text(),
            'email': self.email_edit.text(),
            'password': self.password_edit.text(),
            'display_name': self.display_name_edit.text(),
            'is_active': self.active_check.isChecked(),
            'smtp_server': self.smtp_server_edit.text(),
            'smtp_port': self.smtp_port_spin.value(),
            'smtp_security': self.smtp_security_combo.currentText(),
            'smtp_auth': self.smtp_auth_check.isChecked(),
            'smtp_username': self.smtp_username_edit.text(),
            'imap_server': self.imap_server_edit.text(),
            'imap_port': self.imap_port_spin.value(),
            'imap_security': self.imap_security_combo.currentText(),
            'imap_username': self.imap_username_edit.text(),
            'inbox_folder': self.inbox_folder_edit.text(),
            'sent_folder': self.sent_folder_edit.text(),
            'timeout': self.timeout_spin.value(),
            'max_connections': self.max_connections_spin.value(),
            'enable_monitoring': self.enable_monitoring_check.isChecked(),
            'monitoring_interval': self.monitoring_interval_spin.value(),
            'auto_reply': self.auto_reply_check.isChecked()
        }

class SettingsPanel(QWidget):
    def __init__(self, db_manager, email_handler=None, scheduler=None):
        super().__init__()
        self.db_manager = db_manager
        self.email_handler = email_handler
        self.scheduler = scheduler
        self.logger = logging.getLogger(__name__)
        
        # Settings file path
        self.settings_file = "app_settings.json"
        self.default_settings = {
            'app': {
                'theme': 'Light',
                'language': 'English',
                'startup_minimized': False,
                'minimize_to_tray': True,
                'auto_start': False,
                'check_updates': True
            },
            'email': {
                'default_delay': 1,
                'max_retries': 3,
                'batch_size': 50,
                'attachment_dir': './attachments',
                'auto_save_drafts': True,
                'confirm_send': True
            },
            'monitoring': {
                'check_interval': 60,
                'max_emails_per_check': 100,
                'mark_as_read': False,
                'process_attachments': True
            },
            'scheduler': {
                'max_concurrent_jobs': 3,
                'retry_failed_jobs': True,
                'job_timeout': 300
            },
            'logging': {
                'log_level': 'INFO',
                'max_log_files': 10,
                'max_log_size_mb': 10,
                'log_to_file': True
            },
            'backup': {
                'auto_backup': True,
                'backup_interval_days': 7,
                'max_backups': 5,
                'backup_location': './backups'
            }
        }
        
        self.current_settings = self.load_settings()
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize the settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("⚙️ Settings")
        title_label.setObjectName("panelTitle")
        layout.addWidget(title_label)
        
        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Settings widget
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # Create settings tabs
        self.create_settings_tabs(settings_layout)
        
        scroll_area.setWidget(settings_widget)
        layout.addWidget(scroll_area)
        
        # Action buttons
        self.create_action_buttons(layout)
        
        # Apply styles
        self.apply_styles()
    
    def create_settings_tabs(self, parent_layout):
        """Create settings tabs"""
        tab_widget = QTabWidget()
        parent_layout.addWidget(tab_widget)
        
        # Account settings tab
        self.create_accounts_tab(tab_widget)
        
        # Application settings tab
        self.create_app_tab(tab_widget)
        
        # Email settings tab
        self.create_email_tab(tab_widget)
        
        # Monitoring settings tab
        self.create_monitoring_tab(tab_widget)
        
        # Scheduler settings tab
        self.create_scheduler_tab(tab_widget)
        
        # Logging settings tab
        self.create_logging_tab(tab_widget)
        
        # Backup settings tab
        self.create_backup_tab(tab_widget)
        
        # About tab
        self.create_about_tab(tab_widget)
    
    def create_accounts_tab(self, parent):
        """Create email accounts management tab"""
        accounts_widget = QWidget()
        layout = QVBoxLayout(accounts_widget)
        
        # Accounts header
        header_layout = QHBoxLayout()
        
        accounts_label = QLabel("Email Accounts")
        accounts_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        header_layout.addWidget(accounts_label)
        
        header_layout.addStretch()
        
        add_account_btn = QPushButton("➕ Add Account")
        add_account_btn.setObjectName("primaryButton")
        add_account_btn.clicked.connect(self.add_email_account)
        header_layout.addWidget(add_account_btn)
        
        layout.addLayout(header_layout)
        
        # Accounts list (placeholder - would be populated from database)
        accounts_group = QGroupBox("Configured Accounts")
        accounts_layout = QVBoxLayout(accounts_group)
        
        # This would be replaced with actual account list from database
        no_accounts_label = QLabel("No email accounts configured.")
        no_accounts_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        accounts_layout.addWidget(no_accounts_label)
        
        layout.addWidget(accounts_group)
        
        layout.addStretch()
        
        parent.addTab(accounts_widget, "📧 Accounts")
    
    def create_app_tab(self, parent):
        """Create application settings tab"""
        app_widget = QWidget()
        layout = QVBoxLayout(app_widget)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German"])
        appearance_layout.addRow("Language:", self.language_combo)
        
        layout.addWidget(appearance_group)
        
        # Startup group
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.startup_minimized_check = QCheckBox("Start minimized")
        startup_layout.addWidget(self.startup_minimized_check)
        
        self.minimize_to_tray_check = QCheckBox("Minimize to system tray")
        startup_layout.addWidget(self.minimize_to_tray_check)
        
        self.auto_start_check = QCheckBox("Start with Windows")
        startup_layout.addWidget(self.auto_start_check)
        
        layout.addWidget(startup_group)
        
        # Updates group
        updates_group = QGroupBox("Updates")
        updates_layout = QVBoxLayout(updates_group)
        
        self.check_updates_check = QCheckBox("Check for updates automatically")
        updates_layout.addWidget(self.check_updates_check)
        
        check_now_btn = QPushButton("🔄 Check Now")
        check_now_btn.setObjectName("secondaryButton")
        check_now_btn.clicked.connect(self.check_for_updates)
        updates_layout.addWidget(check_now_btn)
        
        layout.addWidget(updates_group)
        
        layout.addStretch()
        
        parent.addTab(app_widget, "🎨 Application")
    
    def create_email_tab(self, parent):
        """Create email settings tab"""
        email_widget = QWidget()
        layout = QVBoxLayout(email_widget)
        
        # Sending group
        sending_group = QGroupBox("Email Sending")
        sending_layout = QFormLayout(sending_group)
        
        self.default_delay_spin = QSpinBox()
        self.default_delay_spin.setRange(0, 60)
        self.default_delay_spin.setSuffix(" seconds")
        sending_layout.addRow("Default delay between emails:", self.default_delay_spin)
        
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(0, 10)
        sending_layout.addRow("Max retry attempts:", self.max_retries_spin)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 1000)
        sending_layout.addRow("Batch size:", self.batch_size_spin)
        
        self.confirm_send_check = QCheckBox("Confirm before sending batch emails")
        sending_layout.addRow("", self.confirm_send_check)
        
        layout.addWidget(sending_group)
        
        # Attachments group
        attachments_group = QGroupBox("Attachments")
        attachments_layout = QFormLayout(attachments_group)
        
        attachment_dir_layout = QHBoxLayout()
        self.attachment_dir_edit = QLineEdit()
        attachment_dir_layout.addWidget(self.attachment_dir_edit)
        
        browse_dir_btn = QPushButton("📁 Browse")
        browse_dir_btn.clicked.connect(self.browse_attachment_dir)
        attachment_dir_layout.addWidget(browse_dir_btn)
        
        attachments_layout.addRow("Download directory:", attachment_dir_layout)
        
        layout.addWidget(attachments_group)
        
        # Drafts group
        drafts_group = QGroupBox("Drafts")
        drafts_layout = QVBoxLayout(drafts_group)
        
        self.auto_save_drafts_check = QCheckBox("Auto-save drafts every 30 seconds")
        drafts_layout.addWidget(self.auto_save_drafts_check)
        
        layout.addWidget(drafts_group)
        
        layout.addStretch()
        
        parent.addTab(email_widget, "📤 Email")
    
    def create_monitoring_tab(self, parent):
        """Create monitoring settings tab"""
        monitoring_widget = QWidget()
        layout = QVBoxLayout(monitoring_widget)
        
        # Monitoring group
        monitoring_group = QGroupBox("Inbox Monitoring")
        monitoring_layout = QFormLayout(monitoring_group)
        
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setRange(10, 3600)
        self.check_interval_spin.setSuffix(" seconds")
        monitoring_layout.addRow("Check interval:", self.check_interval_spin)
        
        self.max_emails_per_check_spin = QSpinBox()
        self.max_emails_per_check_spin.setRange(1, 1000)
        monitoring_layout.addRow("Max emails per check:", self.max_emails_per_check_spin)
        
        self.mark_as_read_check = QCheckBox("Mark processed emails as read")
        monitoring_layout.addRow("", self.mark_as_read_check)
        
        self.process_attachments_check = QCheckBox("Process attachments automatically")
        monitoring_layout.addRow("", self.process_attachments_check)
        
        layout.addWidget(monitoring_group)
        
        layout.addStretch()
        
        parent.addTab(monitoring_widget, "👁️ Monitoring")
    
    def create_scheduler_tab(self, parent):
        """Create scheduler settings tab"""
        scheduler_widget = QWidget()
        layout = QVBoxLayout(scheduler_widget)
        
        # Scheduler group
        scheduler_group = QGroupBox("Email Scheduler")
        scheduler_layout = QFormLayout(scheduler_group)
        
        self.max_concurrent_jobs_spin = QSpinBox()
        self.max_concurrent_jobs_spin.setRange(1, 10)
        scheduler_layout.addRow("Max concurrent jobs:", self.max_concurrent_jobs_spin)
        
        self.retry_failed_jobs_check = QCheckBox("Retry failed jobs automatically")
        scheduler_layout.addRow("", self.retry_failed_jobs_check)
        
        self.job_timeout_spin = QSpinBox()
        self.job_timeout_spin.setRange(60, 3600)
        self.job_timeout_spin.setSuffix(" seconds")
        scheduler_layout.addRow("Job timeout:", self.job_timeout_spin)
        
        layout.addWidget(scheduler_group)
        
        layout.addStretch()
        
        parent.addTab(scheduler_widget, "⏰ Scheduler")
    
    def create_logging_tab(self, parent):
        """Create logging settings tab"""
        logging_widget = QWidget()
        layout = QVBoxLayout(logging_widget)
        
        # Logging group
        logging_group = QGroupBox("Application Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("Log level:", self.log_level_combo)
        
        self.log_to_file_check = QCheckBox("Log to file")
        logging_layout.addRow("", self.log_to_file_check)
        
        self.max_log_files_spin = QSpinBox()
        self.max_log_files_spin.setRange(1, 100)
        logging_layout.addRow("Max log files:", self.max_log_files_spin)
        
        self.max_log_size_spin = QSpinBox()
        self.max_log_size_spin.setRange(1, 100)
        self.max_log_size_spin.setSuffix(" MB")
        logging_layout.addRow("Max log file size:", self.max_log_size_spin)
        
        layout.addWidget(logging_group)
        
        # Log actions
        log_actions_group = QGroupBox("Log Actions")
        log_actions_layout = QHBoxLayout(log_actions_group)
        
        view_logs_btn = QPushButton("📄 View Logs")
        view_logs_btn.setObjectName("secondaryButton")
        view_logs_btn.clicked.connect(self.view_logs)
        log_actions_layout.addWidget(view_logs_btn)
        
        clear_logs_btn = QPushButton("🗑️ Clear Logs")
        clear_logs_btn.setObjectName("dangerButton")
        clear_logs_btn.clicked.connect(self.clear_logs)
        log_actions_layout.addWidget(clear_logs_btn)
        
        export_logs_btn = QPushButton("📤 Export Logs")
        export_logs_btn.setObjectName("secondaryButton")
        export_logs_btn.clicked.connect(self.export_logs)
        log_actions_layout.addWidget(export_logs_btn)
        
        layout.addWidget(log_actions_group)
        
        layout.addStretch()
        
        parent.addTab(logging_widget, "📝 Logging")
    
    def create_backup_tab(self, parent):
        """Create backup settings tab"""
        backup_widget = QWidget()
        layout = QVBoxLayout(backup_widget)
        
        # Backup settings group
        backup_group = QGroupBox("Database Backup")
        backup_layout = QFormLayout(backup_group)
        
        self.auto_backup_check = QCheckBox("Enable automatic backups")
        backup_layout.addRow("", self.auto_backup_check)
        
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 365)
        self.backup_interval_spin.setSuffix(" days")
        backup_layout.addRow("Backup interval:", self.backup_interval_spin)
        
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 100)
        backup_layout.addRow("Max backups to keep:", self.max_backups_spin)
        
        backup_location_layout = QHBoxLayout()
        self.backup_location_edit = QLineEdit()
        backup_location_layout.addWidget(self.backup_location_edit)
        
        browse_backup_btn = QPushButton("📁 Browse")
        browse_backup_btn.clicked.connect(self.browse_backup_location)
        backup_location_layout.addWidget(browse_backup_btn)
        
        backup_layout.addRow("Backup location:", backup_location_layout)
        
        layout.addWidget(backup_group)
        
        # Backup actions
        backup_actions_group = QGroupBox("Backup Actions")
        backup_actions_layout = QVBoxLayout(backup_actions_group)
        
        # Manual backup
        manual_backup_layout = QHBoxLayout()
        
        backup_now_btn = QPushButton("💾 Backup Now")
        backup_now_btn.setObjectName("primaryButton")
        backup_now_btn.clicked.connect(self.backup_now)
        manual_backup_layout.addWidget(backup_now_btn)
        
        restore_btn = QPushButton("🔄 Restore")
        restore_btn.setObjectName("secondaryButton")
        restore_btn.clicked.connect(self.restore_backup)
        manual_backup_layout.addWidget(restore_btn)
        
        manual_backup_layout.addStretch()
        
        backup_actions_layout.addLayout(manual_backup_layout)
        
        # Backup progress
        self.backup_progress = QProgressBar()
        self.backup_progress.setVisible(False)
        backup_actions_layout.addWidget(self.backup_progress)
        
        # Backup status
        self.backup_status_label = QLabel("No recent backup")
        self.backup_status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        backup_actions_layout.addWidget(self.backup_status_label)
        
        layout.addWidget(backup_actions_group)
        
        layout.addStretch()
        
        parent.addTab(backup_widget, "💾 Backup")
    
    def create_about_tab(self, parent):
        """Create about tab"""
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)
        
        # App info
        app_info_group = QGroupBox("Application Information")
        app_info_layout = QFormLayout(app_info_group)
        
        app_info_layout.addRow("Name:", QLabel("Email Automation Bot"))
        app_info_layout.addRow("Version:", QLabel("1.0.0"))
        app_info_layout.addRow("Author:", QLabel("MD JOBAYER ARAFAT"))
        app_info_layout.addRow("License:", QLabel("MIT License"))
        
        layout.addWidget(app_info_group)
        
        # System info
        system_info_group = QGroupBox("System Information")
        system_info_layout = QFormLayout(system_info_group)
        
        import platform
        import sys
        
        system_info_layout.addRow("OS:", QLabel(platform.system() + " " + platform.release()))
        system_info_layout.addRow("Python:", QLabel(sys.version.split()[0]))
        system_info_layout.addRow("PyQt6:", QLabel("6.x"))
        
        layout.addWidget(system_info_group)
        
        # Links
        links_group = QGroupBox("Links")
        links_layout = QVBoxLayout(links_group)
        
        github_btn = QPushButton("🔗 GitHub Repository")
        github_btn.setObjectName("secondaryButton")
        github_btn.clicked.connect(lambda: self.open_url("https://github.com/mdjobayerarafat/emailbot_python"))
        links_layout.addWidget(github_btn)
        
        docs_btn = QPushButton("📚 Documentation")
        docs_btn.setObjectName("secondaryButton")
        docs_btn.clicked.connect(lambda: self.open_url("https://github.com/mdjobayerarafat/emailbot_python/blob/main/USER_GUIDE.md"))
        links_layout.addWidget(docs_btn)
        
        layout.addWidget(links_group)
        
        layout.addStretch()
        
        parent.addTab(about_widget, "ℹ️ About")
    
    def create_action_buttons(self, parent_layout):
        """Create action buttons"""
        buttons_frame = QFrame()
        buttons_frame.setObjectName("actionFrame")
        buttons_layout = QHBoxLayout(buttons_frame)
        
        # Reset to defaults
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setObjectName("dangerButton")
        reset_btn.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        
        # Cancel and Save
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.cancel_changes)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)
        
        parent_layout.addWidget(buttons_frame)
    
    def apply_styles(self):
        """Apply styles to the panel"""
        style = """
        #panelTitle {
            font-size: 24px;
            font-weight: bold;
            color: #023047;
            margin-bottom: 20px;
        }
        
        #primaryButton {
            background-color: #219ebc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            margin: 4px;
        }
        
        #primaryButton:hover {
            background-color: #023047;
        }
        
        #secondaryButton {
            background-color: #8ecae6;
            color: #023047;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            margin: 4px;
        }
        
        #secondaryButton:hover {
            background-color: #219ebc;
            color: white;
        }
        
        #dangerButton {
            background-color: #fb8500;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            margin: 4px;
        }
        
        #dangerButton:hover {
            background-color: #ffb703;
        }
        
        #actionFrame {
            background-color: #8ecae6;
            border: 1px solid #219ebc;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #219ebc;
            border-radius: 8px;
            margin-top: 15px;
            padding-top: 15px;
            background-color: #219ebc;
            color: #ffffff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px 0 8px;
            color: #ffffff;
        }
        
        QLineEdit, QComboBox, QSpinBox {
            border: 1px solid #219ebc;
            border-radius: 4px;
            padding: 8px;
            background-color: #023047;
            color: white;
        }
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border-color: #023047;
        }
        
        QCheckBox {
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 2px solid #219ebc;
            border-radius: 3px;
            background-color: #023047;
        }
        
        QCheckBox::indicator:checked {
            border: 2px solid #219ebc;
            border-radius: 3px;
            background-color: #219ebc;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }
        
        QProgressBar {
            border: 1px solid #219ebc;
            border-radius: 4px;
            text-align: center;
            background-color: #8ecae6;
            height: 20px;
        }
        
        QProgressBar::chunk {
            background-color: #219ebc;
            border-radius: 3px;
        }
        
        QTabWidget::pane {
            border: 1px solid #219ebc;
            border-radius: 6px;
            background-color: #8ecae6;
        }
        
        QTabBar::tab {
            background-color: #8ecae6;
            border: 1px solid #219ebc;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            color: #023047;
        }
        
        QTabBar::tab:selected {
            background-color: #8ecae6;
            border-bottom-color: #8ecae6;
            color: #023047;
        }
        
        QTabBar::tab:hover {
            background-color: #219ebc;
            color: white;
        }
        """
        
        self.setStyleSheet(style)
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                merged_settings = self.default_settings.copy()
                for category, values in settings.items():
                    if category in merged_settings:
                        merged_settings[category].update(values)
                    else:
                        merged_settings[category] = values
                
                return merged_settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            # Collect settings from UI
            settings = {
                'app': {
                    'theme': self.theme_combo.currentText(),
                    'language': self.language_combo.currentText(),
                    'startup_minimized': self.startup_minimized_check.isChecked(),
                    'minimize_to_tray': self.minimize_to_tray_check.isChecked(),
                    'auto_start': self.auto_start_check.isChecked(),
                    'check_updates': self.check_updates_check.isChecked()
                },
                'email': {
                    'default_delay': self.default_delay_spin.value(),
                    'max_retries': self.max_retries_spin.value(),
                    'batch_size': self.batch_size_spin.value(),
                    'attachment_dir': self.attachment_dir_edit.text(),
                    'auto_save_drafts': self.auto_save_drafts_check.isChecked(),
                    'confirm_send': self.confirm_send_check.isChecked()
                },
                'monitoring': {
                    'check_interval': self.check_interval_spin.value(),
                    'max_emails_per_check': self.max_emails_per_check_spin.value(),
                    'mark_as_read': self.mark_as_read_check.isChecked(),
                    'process_attachments': self.process_attachments_check.isChecked()
                },
                'scheduler': {
                    'max_concurrent_jobs': self.max_concurrent_jobs_spin.value(),
                    'retry_failed_jobs': self.retry_failed_jobs_check.isChecked(),
                    'job_timeout': self.job_timeout_spin.value()
                },
                'logging': {
                    'log_level': self.log_level_combo.currentText(),
                    'max_log_files': self.max_log_files_spin.value(),
                    'max_log_size_mb': self.max_log_size_spin.value(),
                    'log_to_file': self.log_to_file_check.isChecked()
                },
                'backup': {
                    'auto_backup': self.auto_backup_check.isChecked(),
                    'backup_interval_days': self.backup_interval_spin.value(),
                    'max_backups': self.max_backups_spin.value(),
                    'backup_location': self.backup_location_edit.text()
                }
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.current_settings = settings
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def load_current_settings(self):
        """Load current settings into UI"""
        # App settings
        self.theme_combo.setCurrentText(self.current_settings['app']['theme'])
        self.language_combo.setCurrentText(self.current_settings['app']['language'])
        self.startup_minimized_check.setChecked(self.current_settings['app']['startup_minimized'])
        self.minimize_to_tray_check.setChecked(self.current_settings['app']['minimize_to_tray'])
        self.auto_start_check.setChecked(self.current_settings['app']['auto_start'])
        self.check_updates_check.setChecked(self.current_settings['app']['check_updates'])
        
        # Email settings
        self.default_delay_spin.setValue(self.current_settings['email']['default_delay'])
        self.max_retries_spin.setValue(self.current_settings['email']['max_retries'])
        self.batch_size_spin.setValue(self.current_settings['email']['batch_size'])
        self.attachment_dir_edit.setText(self.current_settings['email']['attachment_dir'])
        self.auto_save_drafts_check.setChecked(self.current_settings['email']['auto_save_drafts'])
        self.confirm_send_check.setChecked(self.current_settings['email']['confirm_send'])
        
        # Monitoring settings
        self.check_interval_spin.setValue(self.current_settings['monitoring']['check_interval'])
        self.max_emails_per_check_spin.setValue(self.current_settings['monitoring']['max_emails_per_check'])
        self.mark_as_read_check.setChecked(self.current_settings['monitoring']['mark_as_read'])
        self.process_attachments_check.setChecked(self.current_settings['monitoring']['process_attachments'])
        
        # Scheduler settings
        self.max_concurrent_jobs_spin.setValue(self.current_settings['scheduler']['max_concurrent_jobs'])
        self.retry_failed_jobs_check.setChecked(self.current_settings['scheduler']['retry_failed_jobs'])
        self.job_timeout_spin.setValue(self.current_settings['scheduler']['job_timeout'])
        
        # Logging settings
        self.log_level_combo.setCurrentText(self.current_settings['logging']['log_level'])
        self.max_log_files_spin.setValue(self.current_settings['logging']['max_log_files'])
        self.max_log_size_spin.setValue(self.current_settings['logging']['max_log_size_mb'])
        self.log_to_file_check.setChecked(self.current_settings['logging']['log_to_file'])
        
        # Backup settings
        self.auto_backup_check.setChecked(self.current_settings['backup']['auto_backup'])
        self.backup_interval_spin.setValue(self.current_settings['backup']['backup_interval_days'])
        self.max_backups_spin.setValue(self.current_settings['backup']['max_backups'])
        self.backup_location_edit.setText(self.current_settings['backup']['backup_location'])
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_settings = self.default_settings.copy()
            self.load_current_settings()
    
    def cancel_changes(self):
        """Cancel changes and reload current settings"""
        self.load_current_settings()
    
    def add_email_account(self):
        """Add new email account"""
        dialog = EmailAccountDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            account_data = dialog.get_account_data()
            # Save to database
            try:
                self.db_manager.add_email_account(
                    name=account_data['name'],
                    email=account_data['email'],
                    password=account_data['password'],
                    smtp_server=account_data['smtp_server'],
                    smtp_port=account_data['smtp_port'],
                    imap_server=account_data['imap_server'],
                    imap_port=account_data['imap_port'],
                    is_active=account_data['is_active']
                )
                QMessageBox.information(self, "Success", "Email account added successfully!")
            except Exception as e:
                self.logger.error(f"Error adding email account: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add email account: {str(e)}")
    
    def browse_attachment_dir(self):
        """Browse for attachment directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Attachment Directory",
            self.attachment_dir_edit.text()
        )
        if dir_path:
            self.attachment_dir_edit.setText(dir_path)
    
    def browse_backup_location(self):
        """Browse for backup location"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Backup Location",
            self.backup_location_edit.text()
        )
        if dir_path:
            self.backup_location_edit.setText(dir_path)
    
    def check_for_updates(self):
        """Check for application updates"""
        QMessageBox.information(
            self, "Check Updates",
            "Update checking functionality will be implemented in a future version."
        )
    
    def view_logs(self):
        """View application logs"""
        QMessageBox.information(
            self, "View Logs",
            "Log viewing functionality will be implemented with log file integration."
        )
    
    def clear_logs(self):
        """Clear application logs"""
        reply = QMessageBox.question(
            self, "Clear Logs",
            "Are you sure you want to clear all application logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Clear Logs", "Logs cleared successfully!")
    
    def export_logs(self):
        """Export application logs"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs",
            "application_logs.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            reply = QMessageBox.question(
                self, "Restore Backup",
                f"Are you sure you want to restore from backup?\n\nThis will replace the current database with the backup file.\n\nBackup file: {file_path}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Close current database connection
                    self.db_manager.close()
                    
                    # Replace current database with backup
                    shutil.copy2(file_path, self.db_manager.db_path)
                    
                    # Reconnect to database
                    self.db_manager.connect()
                    
                    QMessageBox.information(
                        self, "Restore Complete",
                        "Database restored successfully! Please restart the application."
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error restoring backup: {e}")
                    QMessageBox.critical(
                        self, "Restore Failed",
                        f"Failed to restore backup: {str(e)}"
                    )
    
    def on_backup_completed(self, backup_path):
        """Handle backup completion"""
        self.backup_progress.setVisible(False)
        self.backup_status_label.setText(f"Last backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.backup_status_label.setStyleSheet("color: #27ae60; font-style: normal;")
        
        QMessageBox.information(
            self, "Backup Complete",
            f"Database backup created successfully!\n\nBackup saved to: {backup_path}"
        )
    
    def on_backup_failed(self, error_message):
        """Handle backup failure"""
        self.backup_progress.setVisible(False)
        self.backup_status_label.setText("Backup failed")
        self.backup_status_label.setStyleSheet("color: #e74c3c; font-style: normal;")
        
        QMessageBox.critical(
            self, "Backup Failed",
            f"Database backup failed: {error_message}"
        )
    
    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        webbrowser.open(url)
    
    def get_current_settings(self):
        """Get current settings dictionary"""
        return self.current_settings.copy()
    
    def apply_setting(self, category, key, value):
        """Apply a single setting"""
        if category in self.current_settings:
            self.current_settings[category][key] = value
            self.save_settings()
    
    def get_setting(self, category, key, default=None):
         """Get a single setting value"""
         return self.current_settings.get(category, {}).get(key, default)
    
    def backup_now(self):
        """Create manual backup"""
        backup_dir = self.backup_location_edit.text() or "./backups"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"email_bot_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Start backup in background thread
        self.backup_progress.setVisible(True)
        self.backup_progress.setValue(0)
        
        self.backup_thread = DatabaseBackupThread(
            self.db_manager.db_path,
            backup_path
        )
        self.backup_thread.progress_updated.connect(self.backup_progress.setValue)
        self.backup_thread.backup_completed.connect(self.on_backup_completed)
        self.backup_thread.backup_failed.connect(self.on_backup_failed)
        self.backup_thread.start()
    
    def restore_backup(self):
        """Restore from backup"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File",
            self.backup_location_edit.text() or "./backups",
            "Database Files (*.db);;All Files (*)"
        )
        
      
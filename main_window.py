import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QFrame, QSplitter, QMessageBox, QSystemTrayIcon, QMenu, QMenuBar,
    QDialog, QTextEdit, QScrollArea, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor
import logging
from database import DatabaseManager
from email_handler import EmailHandler
from scheduler import EmailScheduler

# Import UI panels
from ui.dashboard_panel import DashboardPanel
from ui.inbox_monitor_panel import InboxMonitorPanel
from ui.email_sender_panel import EmailSenderPanel
from ui.scheduler_panel import SchedulerPanel
from ui.templates_panel import TemplatesPanel
from ui.logs_panel import LogsPanel
from ui.settings_panel import SettingsPanel
from ui.login_dialog import LoginDialog

class EmailBotMainWindow(QMainWindow):
    def __init__(self, db_manager=None):
        super().__init__()
        self.db_manager = db_manager
        self.email_handler = None
        self.email_scheduler = None
        self.current_user = None
        self.is_logged_in = False
        
        # Setup logging
        self.setup_logging()
        
        # Initialize UI
        self.init_ui()
        
        # Create initial panels (dashboard and settings that don't require login)
        self.create_initial_panels()
        
        # Set initial navigation access
        self.update_navigation_access()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle("Email Automation Bot")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Set application icon
        self.setWindowIcon(self.create_app_icon())
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create sidebar
        self.create_sidebar(splitter)
        
        # Create main content area
        self.create_content_area(splitter)
        
        # Set splitter proportions
        splitter.setSizes([250, 950])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        # Apply modern theme styles with new color palette
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #023047, stop:1 #219ebc);
                color: #ffffff;
            }
            
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
                color: #ffffff;
            }
            
            QSplitter::handle {
                background-color: #8ecae6;
                width: 3px;
                border-radius: 1px;
            }
            
            QSplitter::handle:hover {
                background-color: #ffb703;
            }
            
            /* Group box styling with colored backgrounds */
            QGroupBox {
                background-color: #219ebc;
                border: 2px solid #8ecae6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: 600;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                background-color: #219ebc;
            }
            
            /* Sidebar styling */
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #023047, stop:1 #219ebc);
                border: none;
                border-radius: 8px;
                padding: 8px;
                outline: none;
            }
            
            QListWidget::item {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 12px 16px;
                margin: 2px 0;
                color: #ffffff;
                font-weight: 500;
                font-size: 14px;
            }
            
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #8ecae6, stop:1 #219ebc);
                color: #023047;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #ffb703, stop:1 #fb8500);
                color: #ffffff;
                font-weight: 600;
            }
            
            QListWidget::item:disabled {
                color: #8ecae6;
                background-color: transparent;
            }
            
            /* Status bar styling */
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #023047, stop:1 #219ebc);
                border-top: 1px solid #8ecae6;
                color: #ffffff;
                padding: 4px;
            }
            
            QLabel {
                color: #ffffff;
            }
            
            /* Menu bar styling */
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #023047, stop:1 #219ebc);
                border-bottom: 1px solid #8ecae6;
                color: #ffffff;
                padding: 4px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #8ecae6;
                color: #023047;
            }
            
            QMenu {
                background-color: #023047;
                border: 1px solid #8ecae6;
                border-radius: 6px;
                padding: 4px;
                color: #ffffff;
            }
            
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #ffb703;
                color: #ffffff;
            }
            
            /* Scroll bar styling */
            QScrollBar:vertical {
                background-color: #023047;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #8ecae6;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #ffb703;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            /* Button styling */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffb703, stop:1 #fb8500);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #fb8500, stop:1 #ffb703);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #219ebc, stop:1 #8ecae6);
            }
            
            QPushButton:disabled {
                background-color: #8ecae6;
                color: #023047;
            }
        """)
        
        # Setup system tray
        self.setup_system_tray()
        
        # Setup status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(30000)  # Update every 30 seconds
    
    def create_app_icon(self):
        """Create application icon"""
        # Try to load icon.png from the application directory
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            # Fallback to programmatic icon if icon.png doesn't exist
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(0, 123, 255))
            
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont('Arial', 16, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, 'E')
            painter.end()
            
            return QIcon(pixmap)
    
    def create_sidebar(self, parent):
        """Create sidebar with navigation"""
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(250)
        
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # App title
        title_label = QLabel("Email Automation Bot")
        title_label.setObjectName("appTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        sidebar_layout.addWidget(title_label)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        sidebar_layout.addWidget(self.nav_list)
        
        # Add navigation items
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("📧 Inbox Monitor", "inbox"),
            ("📤 Email Sender", "sender"),
            ("⏰ Scheduler", "scheduler"),
            ("📝 Templates", "templates"),
            ("📋 Logs", "logs"),
            ("⚙️ Settings", "settings")
        ]
        
        for text, data in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.nav_list.addItem(item)
        
        # Connect navigation
        self.nav_list.currentRowChanged.connect(self.change_panel)
        self.nav_list.setCurrentRow(0)
        
        # Add user info at bottom
        user_frame = QFrame()
        user_frame.setObjectName("userFrame")
        user_layout = QVBoxLayout(user_frame)
        
        self.user_label = QLabel("Not logged in")
        self.user_label.setObjectName("userLabel")
        user_layout.addWidget(self.user_label)
        
        # Login/Logout button (changes based on login status)
        self.auth_btn = QPushButton("Login")
        self.auth_btn.setObjectName("authBtn")
        self.auth_btn.clicked.connect(self.toggle_login)
        user_layout.addWidget(self.auth_btn)
        
        sidebar_layout.addWidget(user_frame)
        
        parent.addWidget(sidebar_frame)
    
    def create_content_area(self, parent):
        """Create main content area"""
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create stacked widget for panels
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        parent.addWidget(content_frame)
    

    
    def setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.create_app_icon())
            
            # Create tray menu
            tray_menu = QMenu()
            
            show_action = tray_menu.addAction("Show")
            show_action.triggered.connect(self.show)
            
            hide_action = tray_menu.addAction("Hide")
            hide_action.triggered.connect(self.hide)
            
            tray_menu.addSeparator()
            
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(self.quit_application)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def show_login(self):
        """Show login dialog"""
        login_dialog = LoginDialog(self)
        if login_dialog.exec() == login_dialog.DialogCode.Accepted:
            self.initialize_application()
            # Update login status
            self.is_logged_in = True
            self.current_user = "User"  # You can get actual username from login dialog if needed
            self.user_label.setText(f"Logged in as: {self.current_user}")
            self.auth_btn.setText("Logout")
            self.auth_btn.setObjectName("logoutBtn")
            # Enable navigation items
            self.update_navigation_access()
    
    def initialize_application(self):
        """Initialize application after successful login"""
        try:
            # Use existing database manager if available, otherwise create new one
            if not self.db_manager:
                self.db_manager = DatabaseManager()
            
            # Initialize email handler
            self.email_handler = EmailHandler(self.db_manager)
            
            # Initialize scheduler
            self.email_scheduler = EmailScheduler(self.db_manager, self.email_handler)
            
            # Create panels
            self.create_panels()
            
            self.logger.info("Application initialized successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize application: {str(e)}")
            self.is_logged_in = False
    
    def create_panels(self):
        """Create all UI panels after login"""
        try:
            # Update dashboard panel with actual data
            self.stacked_widget.removeWidget(self.dashboard_panel)
            self.dashboard_panel.deleteLater()
            self.dashboard_panel = DashboardPanel(self.db_manager, self.email_handler, self.email_scheduler)
            self.stacked_widget.insertWidget(0, self.dashboard_panel)
            
            # Replace placeholder widgets with actual panels (indices 1-5)
            # Remove inbox placeholder and add actual inbox panel
            placeholder = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(placeholder)
            placeholder.deleteLater()
            self.inbox_panel = InboxMonitorPanel(self.db_manager, self.email_handler)
            self.stacked_widget.insertWidget(1, self.inbox_panel)
            
            # Remove sender placeholder and add actual sender panel
            placeholder = self.stacked_widget.widget(2)
            self.stacked_widget.removeWidget(placeholder)
            placeholder.deleteLater()
            self.sender_panel = EmailSenderPanel(self.db_manager, self.email_handler)
            self.stacked_widget.insertWidget(2, self.sender_panel)
            
            # Remove scheduler placeholder and add actual scheduler panel
            placeholder = self.stacked_widget.widget(3)
            self.stacked_widget.removeWidget(placeholder)
            placeholder.deleteLater()
            self.scheduler_panel = SchedulerPanel(self.db_manager, self.email_scheduler)
            self.stacked_widget.insertWidget(3, self.scheduler_panel)
            
            # Remove templates placeholder and add actual templates panel
            placeholder = self.stacked_widget.widget(4)
            self.stacked_widget.removeWidget(placeholder)
            placeholder.deleteLater()
            self.templates_panel = TemplatesPanel(self.db_manager)
            self.stacked_widget.insertWidget(4, self.templates_panel)
            
            # Remove logs placeholder and add actual logs panel
            placeholder = self.stacked_widget.widget(5)
            self.stacked_widget.removeWidget(placeholder)
            placeholder.deleteLater()
            self.logs_panel = LogsPanel(self.db_manager)
            self.stacked_widget.insertWidget(5, self.logs_panel)
            
            # Update settings panel with actual data
            self.stacked_widget.removeWidget(self.settings_panel)
            self.settings_panel.deleteLater()
            self.settings_panel = SettingsPanel(self.db_manager, self.email_handler)
            self.stacked_widget.insertWidget(6, self.settings_panel)
            
        except Exception as e:
            self.logger.error(f"Error creating panels: {e}")
            raise
    
    def create_initial_panels(self):
        """Create panels that don't require login (dashboard and settings)"""
        try:
            # Clear existing panels
            while self.stacked_widget.count() > 0:
                widget = self.stacked_widget.widget(0)
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()
            
            # Create dashboard panel (index 0)
            self.dashboard_panel = DashboardPanel(None, None, None)
            self.stacked_widget.addWidget(self.dashboard_panel)
            
            # Add placeholder widgets for protected panels (1-5)
            for i in range(5):
                placeholder = QLabel("Please login to access this feature")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                placeholder.setStyleSheet("color: #666; font-size: 16px;")
                self.stacked_widget.addWidget(placeholder)
            
            # Create settings panel (index 6)
            self.settings_panel = SettingsPanel(None, None)
            self.stacked_widget.addWidget(self.settings_panel)
            
        except Exception as e:
            self.logger.error(f"Error creating initial panels: {e}")
            raise
    
    def change_panel(self, index):
        """Change active panel"""
        if index >= 0 and hasattr(self, 'stacked_widget') and self.stacked_widget:
            # Check if user is trying to access protected content without login
            protected_items = [1, 2, 3, 4, 5]  # inbox, sender, scheduler, templates, logs
            if index in protected_items and not self.is_logged_in:
                QMessageBox.information(self, "Login Required", "Please login to access this feature.")
                self.nav_list.setCurrentRow(0)  # Switch back to dashboard
                return
                
            self.stacked_widget.setCurrentIndex(index)
            
            # Refresh panel data if needed
            current_widget = self.stacked_widget.currentWidget()
            if hasattr(current_widget, 'refresh_data'):
                current_widget.refresh_data()
    
    def update_status(self):
        """Update application status"""
        try:
            if hasattr(self, 'dashboard_panel'):
                self.dashboard_panel.refresh_data()
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def toggle_login(self):
        """Toggle between login and logout"""
        if self.is_logged_in:
            self.logout()
        else:
            self.show_login()
    
    def logout(self):
        """Logout user"""
        try:
            # Stop monitoring and scheduler
            if self.email_handler:
                self.email_handler.stop_inbox_monitoring()
            
            if self.email_scheduler:
                self.email_scheduler.shutdown()
            
            # Clear panels
            while self.stacked_widget.count() > 0:
                widget = self.stacked_widget.widget(0)
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()
            
            # Reset variables
            self.email_handler = None
            self.email_scheduler = None
            self.current_user = None
            self.is_logged_in = False
            
            # Update UI
            self.user_label.setText("Not logged in")
            self.auth_btn.setText("Login")
            self.auth_btn.setObjectName("authBtn")
            
            # Disable navigation items that require login
            self.update_navigation_access()
            
            self.logger.info("User logged out successfully")
            
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")
    
    def update_navigation_access(self):
        """Update navigation access based on login status"""
        try:
            # Items that require login (all except dashboard and settings)
            protected_items = [1, 2, 3, 4, 5]  # inbox, sender, scheduler, templates, logs
            
            for i in range(self.nav_list.count()):
                item = self.nav_list.item(i)
                if i in protected_items:
                    # Enable/disable based on login status
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled if self.is_logged_in 
                                else item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    # Change text color to indicate disabled state
                    if not self.is_logged_in:
                        item.setData(Qt.ItemDataRole.ForegroundRole, QColor(150, 150, 150))
                    else:
                        item.setData(Qt.ItemDataRole.ForegroundRole, None)
            
            # If user logs out and is on a protected panel, switch to dashboard
            if not self.is_logged_in and self.nav_list.currentRow() in protected_items:
                self.nav_list.setCurrentRow(0)  # Switch to dashboard
                
        except Exception as e:
            self.logger.error(f"Error updating navigation access: {e}")
    
    def quit_application(self):
        """Quit application"""
        try:
            # Stop services
            if self.email_handler:
                self.email_handler.stop_inbox_monitoring()
            
            if self.email_scheduler:
                self.email_scheduler.shutdown()
            
            # Hide tray icon
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            
            # Quit application
            QApplication.quit()
            
        except Exception as e:
            self.logger.error(f"Error quitting application: {e}")
            QApplication.quit()
    def create_menu_bar(self):
        """Create menu bar with Help menu"""
        menubar = self.menuBar()
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # User Guide action
        user_guide_action = help_menu.addAction('📖 User Guide')
        user_guide_action.triggered.connect(self.show_user_guide)
        
        # Quick Help action
        quick_help_action = help_menu.addAction('❓ Quick Help')
        quick_help_action.triggered.connect(self.show_quick_help)
        
        help_menu.addSeparator()
        
        # About action
        about_action = help_menu.addAction('ℹ️ About')
        about_action.triggered.connect(self.show_about)
    
    def show_user_guide(self):
        """Show comprehensive user guide"""
        dialog = DocumentationDialog(self, "user_guide")
        dialog.exec()
    
    def show_quick_help(self):
        """Show quick help for current panel"""
        dialog = DocumentationDialog(self, "quick_help")
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        dialog = DocumentationDialog(self, "about")
        dialog.exec()
    
    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            # Hide to system tray instead of closing
            self.hide()
            event.ignore()
        else:
            self.quit_application()
            event.accept()

class DocumentationDialog(QDialog):
    """Dialog for displaying documentation and help content"""
    
    def __init__(self, parent=None, doc_type="user_guide"):
        super().__init__(parent)
        self.doc_type = doc_type
        self.init_ui()
        
    def init_ui(self):
        """Initialize the documentation dialog UI"""
        self.setWindowTitle("Email Automation Bot - Documentation")
        self.setModal(True)
        self.resize(900, 700)
        
        layout = QVBoxLayout(self)
        
        if self.doc_type == "user_guide":
            self.create_user_guide_content(layout)
        elif self.doc_type == "quick_help":
            self.create_quick_help_content(layout)
        elif self.doc_type == "about":
            self.create_about_content(layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #023047;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #219ebc;
                border: 2px solid #8ecae6;
                border-radius: 8px;
                padding: 15px;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
            QTabWidget::pane {
                border: 2px solid #8ecae6;
                border-radius: 8px;
                background-color: #219ebc;
            }
            QTabBar::tab {
                background-color: #023047;
                color: #ffffff;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #8ecae6;
                color: #023047;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffb703, stop:1 #fb8500);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #fb8500, stop:1 #ffb703);
            }
        """)
    
    def create_user_guide_content(self, layout):
        """Create comprehensive user guide content"""
        # Try to read the USER_GUIDE.md file
        user_guide_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'USER_GUIDE.md')
        
        if os.path.exists(user_guide_path):
            try:
                with open(user_guide_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create tabbed interface for different sections
                tab_widget = QTabWidget()
                layout.addWidget(tab_widget)
                
                # Split content into sections based on ## headers
                sections = self.parse_markdown_sections(content)
                
                for section_title, section_content in sections.items():
                    text_edit = QTextEdit()
                    text_edit.setPlainText(section_content)
                    text_edit.setReadOnly(True)
                    tab_widget.addTab(text_edit, section_title)
                    
            except Exception as e:
                self.create_fallback_user_guide(layout)
        else:
            self.create_fallback_user_guide(layout)
    
    def create_quick_help_content(self, layout):
        """Create quick help content for current panel"""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        help_content = """
# Quick Help - Email Automation Bot

## Getting Started
1. **Login**: Use the Login button in the sidebar to access all features
2. **Configure Email**: Go to Settings → Account to set up your email account
3. **Test Connection**: Use the Test buttons in Settings to verify your setup

## Main Features

### 📊 Dashboard
- View system status and recent activity
- Start/stop monitoring and scheduler services
- Quick access to important functions

### 👁️ Inbox Monitor
- Set up auto-reply rules based on keywords
- Monitor incoming emails in real-time
- Create custom responses using templates

### 📤 Email Sender
- Send individual emails or bulk campaigns
- Use templates for consistent messaging
- Schedule emails for future delivery

### ⏰ Scheduler
- Create one-time or recurring email schedules
- Support for daily, weekly, monthly patterns
- Manage recipient lists and templates

### 📧 Templates
- Create reusable email templates
- Use variables like {name}, {email}, {date}
- Support for both plain text and HTML

### 📋 Logs
- View all email activities and system events
- Filter logs by date, type, and severity
- Export logs for external analysis

### ⚙️ Settings
- Configure email accounts (SMTP/IMAP)
- Adjust application preferences
- Backup and restore settings

## Common Email Providers

**Gmail:**
- SMTP: smtp.gmail.com:587 (TLS)
- IMAP: imap.gmail.com:993 (SSL)
- Use App Passwords, not regular password

**Outlook:**
- SMTP: smtp-mail.outlook.com:587 (TLS)
- IMAP: outlook.office365.com:993 (SSL)

**Yahoo:**
- SMTP: smtp.mail.yahoo.com:587 (TLS)
- IMAP: imap.mail.yahoo.com:993 (SSL)

## Troubleshooting
- Check the Logs panel for error messages
- Verify email settings in Settings → Account
- Ensure internet connection is stable
- Use app-specific passwords for Gmail/Outlook

## Need More Help?
Access the full User Guide from Help → User Guide for detailed instructions.
        """
        
        text_edit.setPlainText(help_content)
        layout.addWidget(text_edit)
    
    def create_about_content(self, layout):
        """Create about dialog content"""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        about_content = """
 # About Email Automation Bot
 
 ## Application Information
 **Name:** Email Automation Bot
 **Version:** 1.0.0
 **Author:** MD JOBAYER ARAFAT
 **License:** MIT License
 
 ## Description
 A comprehensive desktop application for automating email management tasks, including inbox monitoring, automated responses, email scheduling, and template management.

## Key Features
- 📊 Real-time dashboard with system status
- 👁️ Intelligent inbox monitoring with auto-reply
- 📤 Bulk email sending and campaigns
- ⏰ Flexible email scheduling system
- 📧 Advanced template management
- 📋 Comprehensive activity logging
- ⚙️ Easy configuration and settings

## Technology Stack
- **Framework:** PyQt6
- **Language:** Python 3.8+
- **Database:** SQLite
- **Email Protocols:** SMTP, IMAP

## System Requirements
- Windows 10 or later
- Python 3.8 or higher
- 512 MB RAM minimum
- 100 MB free disk space
- Internet connection for email operations

## Security Features
- Encrypted credential storage
- App password support
- Secure session management
- Safe backup and restore

## Repository
 **GitHub**: https://github.com/mdjobayerarafat/emailbot_python.git
 **Documentation**: https://github.com/mdjobayerarafat/emailbot_python/blob/main/USER_GUIDE.md
 
 ## Support
 For support and documentation:
 - Use Help → User Guide for detailed instructions
 - Check the Logs panel for troubleshooting
 - Verify email provider settings
 
 ## Copyright
  © 2024 MD JOBAYER ARAFAT. All rights reserved.
  Built with ❤️ for email automation enthusiasts.
        """
        
        text_edit.setPlainText(about_content)
        layout.addWidget(text_edit)
    
    def create_fallback_user_guide(self, layout):
        """Create fallback user guide when file is not available"""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        fallback_content = """
# Email Automation Bot - User Guide

## Welcome to Email Automation Bot!

This application helps you automate your email management tasks with powerful features for monitoring, sending, and scheduling emails.

## Getting Started

### 1. Initial Setup
- Click the "Login" button in the sidebar
- Create a new account or login with existing credentials
- Navigate to Settings → Account to configure your email

### 2. Email Configuration
- Add your SMTP settings for sending emails
- Add your IMAP settings for receiving emails
- Test the connection to ensure everything works

### 3. Basic Usage
- **Dashboard**: Monitor system status and activity
- **Inbox Monitor**: Set up auto-reply rules
- **Email Sender**: Send individual or bulk emails
- **Scheduler**: Schedule emails for future delivery
- **Templates**: Create reusable email templates
- **Logs**: View all email activities
- **Settings**: Configure application preferences

## Email Provider Settings

### Gmail
- SMTP: smtp.gmail.com:587 (TLS)
- IMAP: imap.gmail.com:993 (SSL)
- **Important**: Use App Passwords, not your regular password

### Outlook/Hotmail
- SMTP: smtp-mail.outlook.com:587 (TLS)
- IMAP: outlook.office365.com:993 (SSL)

### Yahoo Mail
- SMTP: smtp.mail.yahoo.com:587 (TLS)
- IMAP: imap.mail.yahoo.com:993 (SSL)

## Key Features Explained

### Auto-Reply Rules
1. Go to Inbox Monitor panel
2. Click "Add Rule"
3. Set keywords that trigger the rule
4. Choose a template for the response
5. Set priority and enable the rule

### Email Templates
1. Go to Templates panel
2. Click "New Template"
3. Add subject and body content
4. Use variables like {name}, {email}, {date}
5. Save and use in emails or auto-replies

### Email Scheduling
1. Go to Scheduler panel
2. Click "New Schedule"
3. Choose template and recipients
4. Set timing (one-time or recurring)
5. Enable the schedule

## Troubleshooting

### Common Issues
- **Connection Errors**: Check email settings and internet
- **Authentication Failed**: Use app passwords for Gmail/Outlook
- **Auto-reply Not Working**: Verify IMAP settings and rules
- **Scheduler Issues**: Check system time and schedule settings

### Getting Help
1. Check the Logs panel for error messages
2. Verify all settings in the Settings panel
3. Ensure your email provider allows third-party apps
4. Use app-specific passwords when required

## Tips for Success
- Test email settings before setting up automation
- Start with simple auto-reply rules
- Use descriptive names for templates and schedules
- Regularly check logs for any issues
- Keep recipient lists updated and clean

For more detailed information, please refer to the complete documentation files included with the application.
        """
        
        text_edit.setPlainText(fallback_content)
        layout.addWidget(text_edit)
    
    def parse_markdown_sections(self, content):
        """Parse markdown content into sections based on ## headers"""
        sections = {}
        current_section = "Introduction"
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('## ') and not line.startswith('### '):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line[3:].strip()  # Remove '## '
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Set application properties
    app.setApplicationName("Email Automation Bot")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Email Bot Inc.")
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show main window
    window = EmailBotMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Email Automation Bot - Main Application Entry Point

A cross-platform desktop application for email automation tasks.
Built with Python and PyQt6.

Author: Md Jobayer Arafat
Version: 1.0.0
License: MIT
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor

# Import application modules
from main_window import EmailBotMainWindow
from database import DatabaseManager
from ui.login_dialog import LoginDialog

class ApplicationInitializer(QThread):
    """Thread for initializing application components"""
    progress_updated = pyqtSignal(int, str)
    initialization_completed = pyqtSignal()
    initialization_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.db_manager = None
    
    def run(self):
        try:
            # Initialize database
            self.progress_updated.emit(20, "Initializing database...")
            self.db_manager = DatabaseManager()
            
            # Create tables if they don't exist
            self.progress_updated.emit(40, "Setting up database tables...")
            # Database tables are created automatically in DatabaseManager.__init__
            
            # Check database integrity
            self.progress_updated.emit(60, "Verifying database integrity...")
            # Add any database integrity checks here
            
            # Initialize logging
            self.progress_updated.emit(80, "Setting up logging...")
            self.setup_logging()
            
            # Complete initialization
            self.progress_updated.emit(100, "Initialization complete!")
            self.initialization_completed.emit()
            
        except Exception as e:
            self.initialization_failed.emit(str(e))
    
    def setup_logging(self):
        """Setup application logging"""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # File handler
        file_handler = logging.FileHandler(
            logs_dir / "email_automation_bot.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log startup
        logger = logging.getLogger(__name__)
        logger.info("Email Automation Bot starting up...")

class EmailAutomationBot:
    """Main application class"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.splash_screen = None
        self.db_manager = None
        self.logger = None
        
    def create_splash_screen(self):
        """Create and show splash screen"""
        # Create a simple splash screen
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(QColor(52, 73, 94))  # Dark blue background
        
        painter = QPainter(splash_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw application name
        painter.setPen(QColor(255, 255, 255))
        title_font = QFont('Arial', 24, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(splash_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, 
                        "Email Automation Bot")
        
        # Draw version
        painter.setPen(QColor(189, 195, 199))
        version_font = QFont('Arial', 12)
        painter.setFont(version_font)
        version_rect = splash_pixmap.rect()
        version_rect.setTop(version_rect.center().y() + 30)
        painter.drawText(version_rect, Qt.AlignmentFlag.AlignCenter, "Version 1.0.0")
        
        # Draw loading text
        loading_rect = splash_pixmap.rect()
        loading_rect.setTop(loading_rect.bottom() - 50)
        painter.drawText(loading_rect, Qt.AlignmentFlag.AlignCenter, "Loading...")
        
        painter.end()
        
        self.splash_screen = QSplashScreen(splash_pixmap)
        self.splash_screen.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint
        )
        self.splash_screen.show()
        
        return self.splash_screen
    
    def update_splash_message(self, progress, message):
        """Update splash screen message"""
        if self.splash_screen:
            self.splash_screen.showMessage(
                f"{message} ({progress}%)",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                QColor(255, 255, 255)
            )
    
    def on_initialization_completed(self):
        """Handle successful initialization"""
        try:
            # Get database manager from initializer thread
            self.db_manager = self.initializer.db_manager
            
            # Setup logger
            self.logger = logging.getLogger(__name__)
            self.logger.info("Application initialization completed")
            
            # Hide splash screen
            if self.splash_screen:
                self.splash_screen.close()
            
            # Show main window directly (skip login)
            self.show_main_window()
            
        except Exception as e:
            self.handle_critical_error(f"Error completing initialization: {str(e)}")
    
    def on_initialization_failed(self, error_message):
        """Handle initialization failure"""
        if self.splash_screen:
            self.splash_screen.close()
        
        self.handle_critical_error(f"Application initialization failed: {error_message}")
    
    def show_login_dialog(self):
        """Show login dialog"""
        try:
            login_dialog = LoginDialog()
            
            if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
                # Login successful, show main window
                self.show_main_window()
            else:
                # Login cancelled, exit application
                self.logger.info("User cancelled login, exiting application")
                self.app.quit()
                
        except Exception as e:
            self.handle_critical_error(f"Error showing login dialog: {str(e)}")
    
    def show_main_window(self):
        """Show main application window"""
        try:
            self.main_window = EmailBotMainWindow(self.db_manager)
            self.main_window.show()
            
            self.logger.info("Main window displayed successfully")
            
        except Exception as e:
            self.handle_critical_error(f"Error showing main window: {str(e)}")
    
    def handle_critical_error(self, error_message):
        """Handle critical application errors"""
        print(f"Critical Error: {error_message}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Try to log the error if logger is available
        if self.logger:
            self.logger.critical(f"Critical error: {error_message}")
            self.logger.critical(f"Traceback: {traceback.format_exc()}")
        
        # Show error dialog
        if self.app:
            QMessageBox.critical(
                None, "Critical Error",
                f"A critical error occurred:\n\n{error_message}\n\n"
                f"The application will now exit. Please check the logs for more details."
            )
        
        # Exit application
        if self.app:
            self.app.quit()
        sys.exit(1)
    
    def setup_exception_handling(self):
        """Setup global exception handling"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # Handle Ctrl+C gracefully
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            error_message = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
            self.handle_critical_error(error_message)
        
        sys.excepthook = handle_exception
    
    def run(self):
        """Run the application"""
        try:
            # Create QApplication
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Email Automation Bot")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("Your Organization")
            
            # Setup exception handling
            self.setup_exception_handling()
            
            # Create and show splash screen
            self.create_splash_screen()
            
            # Process events to show splash screen
            self.app.processEvents()
            
            # Initialize application in background thread
            self.initializer = ApplicationInitializer()
            self.initializer.progress_updated.connect(self.update_splash_message)
            self.initializer.initialization_completed.connect(self.on_initialization_completed)
            self.initializer.initialization_failed.connect(self.on_initialization_failed)
            self.initializer.start()
            
            # Start event loop
            return self.app.exec()
            
        except Exception as e:
            self.handle_critical_error(f"Error starting application: {str(e)}")
            return 1
    
    def cleanup(self):
        """Cleanup application resources"""
        try:
            if self.logger:
                self.logger.info("Application shutting down...")
            
            # Close database connection
            if self.db_manager:
                self.db_manager.close()
            
            # Close main window
            if self.main_window:
                self.main_window.close()
            
            if self.logger:
                self.logger.info("Application shutdown complete")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
    
    try:
        import cryptography
    except ImportError:
        missing_deps.append("cryptography")
    
    try:
        import apscheduler
    except ImportError:
        missing_deps.append("APScheduler")
    
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install missing dependencies using:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    return True

def main():
    """Main entry point"""
    print("Email Automation Bot v1.0.0")
    print("============================\n")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Create and run application
    app = EmailAutomationBot()
    
    try:
        exit_code = app.run()
        return exit_code
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    finally:
        app.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
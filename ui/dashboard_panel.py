from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from datetime import datetime, timedelta
import logging

class DashboardPanel(QWidget):
    def __init__(self, db_manager, email_handler, email_scheduler):
        super().__init__()
        self.db_manager = db_manager
        self.email_handler = email_handler
        self.email_scheduler = email_scheduler
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        self.refresh_data()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the dashboard UI"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Main content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        
        # Content layout
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("📊 Dashboard")
        title_label.setObjectName("panelTitle")
        layout.addWidget(title_label)
        
        # Statistics cards
        self.create_stats_cards(layout)
        
        # Quick actions
        self.create_quick_actions(layout)
        
        # Recent activity
        self.create_recent_activity(layout)
        
        # Upcoming schedules
        self.create_upcoming_schedules(layout)
        
        # System status
        self.create_system_status(layout)
        
        # Apply styles
        self.apply_styles()
    
    def create_stats_cards(self, parent_layout):
        """Create statistics cards"""
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout(stats_group)
        
        # Create stat cards
        self.total_emails_card = self.create_stat_card("📧", "Total Emails", "0", "#3498db")
        self.sent_today_card = self.create_stat_card("📤", "Sent Today", "0", "#27ae60")
        self.failed_today_card = self.create_stat_card("❌", "Failed Today", "0", "#e74c3c")
        self.templates_card = self.create_stat_card("📝", "Templates", "0", "#9b59b6")
        self.schedules_card = self.create_stat_card("⏰", "Active Schedules", "0", "#f39c12")
        self.contacts_card = self.create_stat_card("👥", "Contacts", "0", "#1abc9c")
        
        # Add cards to grid
        stats_layout.addWidget(self.total_emails_card, 0, 0)
        stats_layout.addWidget(self.sent_today_card, 0, 1)
        stats_layout.addWidget(self.failed_today_card, 0, 2)
        stats_layout.addWidget(self.templates_card, 1, 0)
        stats_layout.addWidget(self.schedules_card, 1, 1)
        stats_layout.addWidget(self.contacts_card, 1, 2)
        
        parent_layout.addWidget(stats_group)
    
    def create_stat_card(self, icon, title, value, color):
        """Create a statistics card"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            #statCard {{
                background-color: #8ecae6;
                border: 1px solid #219ebc;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                color: #023047;
            }}
            #statCard:hover {{
                border-color: {color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont('Arial', 20))
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        layout.addWidget(value_label)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def create_quick_actions(self, parent_layout):
        """Create quick action buttons"""
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        # Action buttons
        send_email_btn = QPushButton("📤 Send Email")
        send_email_btn.setObjectName("actionButton")
        send_email_btn.clicked.connect(self.quick_send_email)
        
        create_template_btn = QPushButton("📝 Create Template")
        create_template_btn.setObjectName("actionButton")
        create_template_btn.clicked.connect(self.quick_create_template)
        
        schedule_email_btn = QPushButton("⏰ Schedule Email")
        schedule_email_btn.setObjectName("actionButton")
        schedule_email_btn.clicked.connect(self.quick_schedule_email)
        
        view_logs_btn = QPushButton("📋 View Logs")
        view_logs_btn.setObjectName("actionButton")
        view_logs_btn.clicked.connect(self.quick_view_logs)
        
        actions_layout.addWidget(send_email_btn)
        actions_layout.addWidget(create_template_btn)
        actions_layout.addWidget(schedule_email_btn)
        actions_layout.addWidget(view_logs_btn)
        actions_layout.addStretch()
        
        parent_layout.addWidget(actions_group)
    
    def create_recent_activity(self, parent_layout):
        """Create recent activity table"""
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Action", "Details", "Status"])
        
        # Configure table
        header = self.activity_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.activity_table.setMaximumHeight(200)
        
        activity_layout.addWidget(self.activity_table)
        parent_layout.addWidget(activity_group)
    
    def create_upcoming_schedules(self, parent_layout):
        """Create upcoming schedules table"""
        schedules_group = QGroupBox("Upcoming Schedules")
        schedules_layout = QVBoxLayout(schedules_group)
        
        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(4)
        self.schedules_table.setHorizontalHeaderLabels(["Name", "Template", "Next Run", "Recipients"])
        
        # Configure table
        header = self.schedules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.schedules_table.setAlternatingRowColors(True)
        self.schedules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.schedules_table.setMaximumHeight(200)
        
        schedules_layout.addWidget(self.schedules_table)
        parent_layout.addWidget(schedules_group)
    
    def create_system_status(self, parent_layout):
        """Create system status indicators"""
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        # Status indicators
        indicators_layout = QGridLayout()
        
        # Email account status
        self.email_status_label = QLabel("📧 Email Account: Checking...")
        self.email_status_indicator = QLabel("🔴")
        indicators_layout.addWidget(self.email_status_label, 0, 0)
        indicators_layout.addWidget(self.email_status_indicator, 0, 1)
        
        # Inbox monitoring status
        self.monitor_status_label = QLabel("👁️ Inbox Monitor: Stopped")
        self.monitor_status_indicator = QLabel("🔴")
        indicators_layout.addWidget(self.monitor_status_label, 1, 0)
        indicators_layout.addWidget(self.monitor_status_indicator, 1, 1)
        
        # Scheduler status
        self.scheduler_status_label = QLabel("⏰ Scheduler: Running")
        self.scheduler_status_indicator = QLabel("🟢")
        indicators_layout.addWidget(self.scheduler_status_label, 2, 0)
        indicators_layout.addWidget(self.scheduler_status_indicator, 2, 1)
        
        # Database status
        self.db_status_label = QLabel("💾 Database: Connected")
        self.db_status_indicator = QLabel("🟢")
        indicators_layout.addWidget(self.db_status_label, 3, 0)
        indicators_layout.addWidget(self.db_status_indicator, 3, 1)
        
        status_layout.addLayout(indicators_layout)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.start_monitor_btn = QPushButton("Start Monitoring")
        self.start_monitor_btn.clicked.connect(self.toggle_monitoring)
        
        self.test_connection_btn = QPushButton("Test Connection")
        self.test_connection_btn.clicked.connect(self.test_email_connection)
        
        controls_layout.addWidget(self.start_monitor_btn)
        controls_layout.addWidget(self.test_connection_btn)
        controls_layout.addStretch()
        
        status_layout.addLayout(controls_layout)
        parent_layout.addWidget(status_group)
    
    def apply_styles(self):
        """Apply styles to the dashboard"""
        style = """
        #panelTitle {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 20px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #8ecae6;
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
            font-size: 16px;
        }
        
        #actionButton {
            background-color: #ffb703;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            margin: 5px;
        }
        
        #actionButton:hover {
            background-color: #fb8500;
        }
        
        QTableWidget {
            border: 1px solid #8ecae6;
            border-radius: 6px;
            background-color: #219ebc;
            gridline-color: #8ecae6;
            color: #ffffff;
        }
        
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #8ecae6;
            color: #023047;
        }
        
        QTableWidget::item:selected {
            background-color: #ffb703;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #023047;
            border: 1px solid #8ecae6;
            padding: 8px;
            font-weight: bold;
            color: #ffffff;
        }
        """
        
        self.setStyleSheet(style)
    
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            self.update_statistics()
            self.update_recent_activity()
            self.update_upcoming_schedules()
            self.update_system_status()
        except Exception as e:
            self.logger.error(f"Error refreshing dashboard data: {e}")
    
    def update_statistics(self):
        """Update statistics cards"""
        try:
            # Check if db_manager is available
            if not self.db_manager:
                return
                
            # Get email logs
            logs = self.db_manager.get_email_logs(1000)
            
            # Total emails
            total_emails = len(logs)
            self.total_emails_card.value_label.setText(str(total_emails))
            
            # Today's stats
            today = datetime.now().date()
            sent_today = sum(1 for log in logs if 
                           datetime.fromisoformat(log['sent_at']).date() == today and 
                           log['status'] == 'sent')
            failed_today = sum(1 for log in logs if 
                             datetime.fromisoformat(log['sent_at']).date() == today and 
                             log['status'] == 'failed')
            
            self.sent_today_card.value_label.setText(str(sent_today))
            self.failed_today_card.value_label.setText(str(failed_today))
            
            # Templates
            templates = self.db_manager.get_email_templates()
            self.templates_card.value_label.setText(str(len(templates)))
            
            # Active schedules
            schedules = self.db_manager.get_scheduled_emails()
            active_schedules = sum(1 for s in schedules if s['is_active'])
            self.schedules_card.value_label.setText(str(active_schedules))
            
            # Contacts
            contacts = self.db_manager.get_contacts()
            self.contacts_card.value_label.setText(str(len(contacts)))
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def update_recent_activity(self):
        """Update recent activity table"""
        try:
            # Check if db_manager is available
            if not self.db_manager:
                return
                
            logs = self.db_manager.get_email_logs(10)  # Last 10 activities
            
            self.activity_table.setRowCount(len(logs))
            
            for row, log in enumerate(logs):
                # Time
                sent_time = datetime.fromisoformat(log['sent_at'])
                time_str = sent_time.strftime("%H:%M:%S")
                self.activity_table.setItem(row, 0, QTableWidgetItem(time_str))
                
                # Action
                action = "Email Sent" if log['status'] == 'sent' else "Email Failed"
                self.activity_table.setItem(row, 1, QTableWidgetItem(action))
                
                # Details
                details = f"To: {log['recipient_email'][:30]}..."
                if len(log['recipient_email']) <= 30:
                    details = f"To: {log['recipient_email']}"
                self.activity_table.setItem(row, 2, QTableWidgetItem(details))
                
                # Status
                status_item = QTableWidgetItem(log['status'].title())
                if log['status'] == 'sent':
                    status_item.setBackground(QColor(39, 174, 96, 50))
                else:
                    status_item.setBackground(QColor(231, 76, 60, 50))
                self.activity_table.setItem(row, 3, status_item)
            
        except Exception as e:
            self.logger.error(f"Error updating recent activity: {e}")
    
    def update_upcoming_schedules(self):
        """Update upcoming schedules table"""
        try:
            # Check if db_manager is available
            if not self.db_manager:
                return
                
            schedules = self.db_manager.get_scheduled_emails()
            active_schedules = [s for s in schedules if s['is_active']]
            
            # Sort by next run time
            active_schedules.sort(key=lambda x: x['next_run'])
            
            self.schedules_table.setRowCount(len(active_schedules[:5]))  # Show top 5
            
            for row, schedule in enumerate(active_schedules[:5]):
                # Name
                self.schedules_table.setItem(row, 0, QTableWidgetItem(schedule['name']))
                
                # Template
                template_name = schedule.get('template_name', 'Unknown')
                self.schedules_table.setItem(row, 1, QTableWidgetItem(template_name))
                
                # Next run
                next_run = datetime.fromisoformat(schedule['next_run'])
                next_run_str = next_run.strftime("%Y-%m-%d %H:%M")
                self.schedules_table.setItem(row, 2, QTableWidgetItem(next_run_str))
                
                # Recipients count
                recipients_count = len(schedule['recipients'])
                self.schedules_table.setItem(row, 3, QTableWidgetItem(str(recipients_count)))
            
        except Exception as e:
            self.logger.error(f"Error updating upcoming schedules: {e}")
    
    def update_system_status(self):
        """Update system status indicators"""
        try:
            # Check if db_manager is available
            if not self.db_manager:
                self.email_status_label.setText("📧 Email Account: Not configured")
                self.email_status_indicator.setText("🔴")
                self.monitor_status_label.setText("👁️ Inbox Monitor: Stopped")
                self.monitor_status_indicator.setText("🔴")
                self.start_monitor_btn.setText("Start Monitoring")
                return
                
            # Check email account
            account = self.db_manager.get_active_email_account()
            if account:
                self.email_status_label.setText(f"📧 Email Account: {account['email']}")
                self.email_status_indicator.setText("🟢")
            else:
                self.email_status_label.setText("📧 Email Account: Not configured")
                self.email_status_indicator.setText("🔴")
            
            # Check monitoring status
            if hasattr(self.email_handler, 'monitoring') and self.email_handler.monitoring:
                self.monitor_status_label.setText("👁️ Inbox Monitor: Running")
                self.monitor_status_indicator.setText("🟢")
                self.start_monitor_btn.setText("Stop Monitoring")
            else:
                self.monitor_status_label.setText("👁️ Inbox Monitor: Stopped")
                self.monitor_status_indicator.setText("🔴")
                self.start_monitor_btn.setText("Start Monitoring")
            
        except Exception as e:
            self.logger.error(f"Error updating system status: {e}")
    
    def quick_send_email(self):
        """Quick action: Send email"""
        # Switch to sender panel
        parent = self.parent()
        while parent and not hasattr(parent, 'nav_list'):
            parent = parent.parent()
        if parent:
            parent.nav_list.setCurrentRow(2)  # Email Sender panel
    
    def quick_create_template(self):
        """Quick action: Create template"""
        # Switch to templates panel
        parent = self.parent()
        while parent and not hasattr(parent, 'nav_list'):
            parent = parent.parent()
        if parent:
            parent.nav_list.setCurrentRow(4)  # Templates panel
    
    def quick_schedule_email(self):
        """Quick action: Schedule email"""
        # Switch to scheduler panel
        parent = self.parent()
        while parent and not hasattr(parent, 'nav_list'):
            parent = parent.parent()
        if parent:
            parent.nav_list.setCurrentRow(3)  # Scheduler panel
    
    def quick_view_logs(self):
        """Quick action: View logs"""
        # Switch to logs panel
        parent = self.parent()
        while parent and not hasattr(parent, 'nav_list'):
            parent = parent.parent()
        if parent:
            parent.nav_list.setCurrentRow(5)  # Logs panel
    
    def toggle_monitoring(self):
        """Toggle inbox monitoring"""
        try:
            account = self.db_manager.get_active_email_account()
            if not account:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", "No email account configured.")
                return
            
            if hasattr(self.email_handler, 'monitoring') and self.email_handler.monitoring:
                self.email_handler.stop_inbox_monitoring()
            else:
                self.email_handler.start_inbox_monitoring(account)
            
            self.update_system_status()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to toggle monitoring: {str(e)}")
    
    def test_email_connection(self):
        """Test email connection"""
        try:
            account = self.db_manager.get_active_email_account()
            if not account:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", "No email account configured.")
                return
            
            success, message = self.email_handler.test_connection(account)
            
            from PyQt6.QtWidgets import QMessageBox
            if success:
                QMessageBox.information(self, "Success", "Email connection test successful!")
            else:
                QMessageBox.warning(self, "Error", f"Connection test failed: {message}")
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to test connection: {str(e)}")
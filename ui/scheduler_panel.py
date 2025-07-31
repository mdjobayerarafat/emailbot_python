from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QMessageBox,
    QDateTimeEdit, QCalendarWidget, QTimeEdit, QSplitter,
    QFrame, QTabWidget, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDateTime, QDate, QTime
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta
import logging
import json

class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None):
        super().__init__(parent)
        self.schedule = schedule
        self.db_manager = parent.db_manager
        self.init_ui()
        
        if schedule:
            self.load_schedule_data()
    
    def init_ui(self):
        self.setWindowTitle("Schedule Email")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Basic info tab
        self.create_basic_tab(tab_widget)
        
        # Schedule tab
        self.create_schedule_tab(tab_widget)
        
        # Recipients tab
        self.create_recipients_tab(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_basic_tab(self, parent):
        """Create basic information tab"""
        basic_widget = QWidget()
        layout = QFormLayout(basic_widget)
        
        # Schedule name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter schedule name")
        layout.addRow("Schedule Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter description (optional)")
        self.description_edit.setMaximumHeight(80)
        layout.addRow("Description:", self.description_edit)
        
        # Template selection
        self.template_combo = QComboBox()
        self.load_templates()
        layout.addRow("Email Template:", self.template_combo)
        
        # Template preview
        preview_group = QGroupBox("Template Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(100)
        preview_layout.addWidget(self.preview_text)
        
        layout.addRow(preview_group)
        
        # Active status
        self.active_check = QCheckBox("Schedule is active")
        self.active_check.setChecked(True)
        layout.addRow("", self.active_check)
        
        # Connect signals
        self.template_combo.currentTextChanged.connect(self.update_preview)
        
        parent.addTab(basic_widget, "📝 Basic Info")
    
    def create_schedule_tab(self, parent):
        """Create schedule configuration tab"""
        schedule_widget = QWidget()
        layout = QVBoxLayout(schedule_widget)
        
        # Schedule type
        type_group = QGroupBox("Schedule Type")
        type_layout = QFormLayout(type_group)
        
        self.schedule_type_combo = QComboBox()
        self.schedule_type_combo.addItems([
            "Once", "Daily", "Weekly", "Monthly", "Custom Interval"
        ])
        self.schedule_type_combo.currentTextChanged.connect(self.update_schedule_options)
        type_layout.addRow("Type:", self.schedule_type_combo)
        
        layout.addWidget(type_group)
        
        # Schedule options (dynamic based on type)
        self.options_group = QGroupBox("Schedule Options")
        self.options_layout = QFormLayout(self.options_group)
        layout.addWidget(self.options_group)
        
        # Start date/time
        datetime_group = QGroupBox("Start Date & Time")
        datetime_layout = QFormLayout(datetime_group)
        
        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # 1 hour from now
        self.start_datetime.setCalendarPopup(True)
        datetime_layout.addRow("Start Date/Time:", self.start_datetime)
        
        layout.addWidget(datetime_group)
        
        # End conditions
        end_group = QGroupBox("End Conditions")
        end_layout = QFormLayout(end_group)
        
        self.end_type_combo = QComboBox()
        self.end_type_combo.addItems(["Never", "After date", "After count"])
        self.end_type_combo.currentTextChanged.connect(self.update_end_options)
        end_layout.addRow("End Type:", self.end_type_combo)
        
        # End date
        self.end_datetime = QDateTimeEdit()
        self.end_datetime.setDateTime(QDateTime.currentDateTime().addDays(30))
        self.end_datetime.setCalendarPopup(True)
        self.end_datetime.setVisible(False)
        end_layout.addRow("End Date:", self.end_datetime)
        
        # Max count
        self.max_count_spin = QSpinBox()
        self.max_count_spin.setRange(1, 1000)
        self.max_count_spin.setValue(10)
        self.max_count_spin.setVisible(False)
        end_layout.addRow("Max Executions:", self.max_count_spin)
        
        layout.addWidget(end_group)
        
        # Initialize with default type
        self.update_schedule_options()
        
        parent.addTab(schedule_widget, "⏰ Schedule")
    
    def create_recipients_tab(self, parent):
        """Create recipients tab"""
        recipients_widget = QWidget()
        layout = QVBoxLayout(recipients_widget)
        
        # Recipient source
        source_group = QGroupBox("Recipient Source")
        source_layout = QFormLayout(source_group)
        
        self.recipient_source_combo = QComboBox()
        self.recipient_source_combo.addItems(["All contacts", "Select contacts", "Custom list"])
        self.recipient_source_combo.currentTextChanged.connect(self.update_recipient_options)
        source_layout.addRow("Source:", self.recipient_source_combo)
        
        layout.addWidget(source_group)
        
        # Recipient options (dynamic)
        self.recipient_options_group = QGroupBox("Recipients")
        self.recipient_options_layout = QVBoxLayout(self.recipient_options_group)
        layout.addWidget(self.recipient_options_group)
        
        # Initialize with default source
        self.update_recipient_options()
        
        parent.addTab(recipients_widget, "👥 Recipients")
    
    def load_templates(self):
        """Load email templates"""
        try:
            templates = self.db_manager.get_email_templates()
            
            self.template_combo.clear()
            self.template_combo.addItem("Select template...", None)
            
            for template in templates:
                self.template_combo.addItem(template['name'], template['id'])
                
        except Exception as e:
            logging.error(f"Error loading templates: {e}")
    
    def update_preview(self):
        """Update template preview"""
        try:
            template_id = self.template_combo.currentData()
            if not template_id:
                self.preview_text.clear()
                return
            
            template = self.db_manager.get_email_template(template_id)
            
            if template:
                preview = f"Subject: {template['subject']}\n\n{template['body'][:200]}..."
                self.preview_text.setPlainText(preview)
            
        except Exception as e:
            logging.error(f"Error updating preview: {e}")
    
    def update_schedule_options(self):
        """Update schedule options based on type"""
        # Clear existing options
        for i in reversed(range(self.options_layout.count())):
            child = self.options_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        schedule_type = self.schedule_type_combo.currentText()
        
        if schedule_type == "Daily":
            # Time of day
            self.daily_time = QTimeEdit()
            self.daily_time.setTime(QTime(9, 0))  # 9:00 AM
            self.options_layout.addRow("Time:", self.daily_time)
            
        elif schedule_type == "Weekly":
            # Day of week and time
            self.weekly_day = QComboBox()
            self.weekly_day.addItems([
                "Monday", "Tuesday", "Wednesday", "Thursday", 
                "Friday", "Saturday", "Sunday"
            ])
            self.options_layout.addRow("Day of Week:", self.weekly_day)
            
            self.weekly_time = QTimeEdit()
            self.weekly_time.setTime(QTime(9, 0))
            self.options_layout.addRow("Time:", self.weekly_time)
            
        elif schedule_type == "Monthly":
            # Day of month and time
            self.monthly_day = QSpinBox()
            self.monthly_day.setRange(1, 31)
            self.monthly_day.setValue(1)
            self.options_layout.addRow("Day of Month:", self.monthly_day)
            
            self.monthly_time = QTimeEdit()
            self.monthly_time.setTime(QTime(9, 0))
            self.options_layout.addRow("Time:", self.monthly_time)
            
        elif schedule_type == "Custom Interval":
            # Interval value and unit
            self.interval_value = QSpinBox()
            self.interval_value.setRange(1, 999)
            self.interval_value.setValue(1)
            self.options_layout.addRow("Interval:", self.interval_value)
            
            self.interval_unit = QComboBox()
            self.interval_unit.addItems(["Minutes", "Hours", "Days", "Weeks"])
            self.interval_unit.setCurrentText("Hours")
            self.options_layout.addRow("Unit:", self.interval_unit)
    
    def update_end_options(self):
        """Update end condition options"""
        end_type = self.end_type_combo.currentText()
        
        self.end_datetime.setVisible(end_type == "After date")
        self.max_count_spin.setVisible(end_type == "After count")
    
    def update_recipient_options(self):
        """Update recipient options based on source"""
        # Clear existing options
        for i in reversed(range(self.recipient_options_layout.count())):
            child = self.recipient_options_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        source = self.recipient_source_combo.currentText()
        
        if source == "All contacts":
            # Show contact count
            try:
                contacts = self.db_manager.get_contacts()
                count_label = QLabel(f"Will send to all {len(contacts)} contacts in database")
                count_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                self.recipient_options_layout.addWidget(count_label)
            except:
                pass
                
        elif source == "Select contacts":
            # Show contact list with checkboxes
            try:
                contacts = self.db_manager.get_contacts()
                
                self.contact_list = QListWidget()
                self.contact_list.setMaximumHeight(200)
                
                for contact in contacts:
                    item = QListWidgetItem(f"{contact['name']} ({contact['email']})")
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    item.setData(Qt.ItemDataRole.UserRole, contact['id'])
                    self.contact_list.addItem(item)
                
                self.recipient_options_layout.addWidget(QLabel("Select contacts:"))
                self.recipient_options_layout.addWidget(self.contact_list)
                
            except Exception as e:
                error_label = QLabel(f"Error loading contacts: {str(e)}")
                error_label.setStyleSheet("color: #e74c3c;")
                self.recipient_options_layout.addWidget(error_label)
                
        elif source == "Custom list":
            # Text area for email list
            self.custom_emails = QTextEdit()
            self.custom_emails.setPlaceholderText(
                "Enter email addresses, one per line:\n"
                "user1@example.com\n"
                "user2@example.com\n"
                "..."
            )
            self.custom_emails.setMaximumHeight(150)
            
            self.recipient_options_layout.addWidget(QLabel("Email addresses:"))
            self.recipient_options_layout.addWidget(self.custom_emails)
    
    def load_schedule_data(self):
        """Load existing schedule data"""
        if not self.schedule:
            return
        
        # Basic info
        self.name_edit.setText(self.schedule['name'])
        self.description_edit.setPlainText(self.schedule.get('description', ''))
        self.active_check.setChecked(self.schedule.get('is_active', True))
        
        # Template
        template_id = self.schedule.get('template_id')
        if template_id:
            for i in range(self.template_combo.count()):
                if self.template_combo.itemData(i) == template_id:
                    self.template_combo.setCurrentIndex(i)
                    break
        
        # Schedule settings
        schedule_config = json.loads(self.schedule.get('schedule_config', '{}'))
        
        # Set schedule type
        schedule_type = schedule_config.get('type', 'once')
        type_map = {
            'once': 'Once',
            'daily': 'Daily',
            'weekly': 'Weekly',
            'monthly': 'Monthly',
            'interval': 'Custom Interval'
        }
        
        if schedule_type in type_map:
            self.schedule_type_combo.setCurrentText(type_map[schedule_type])
        
        # Start time
        if self.schedule.get('next_run'):
            next_run = datetime.fromisoformat(self.schedule['next_run'])
            self.start_datetime.setDateTime(QDateTime.fromSecsSinceEpoch(int(next_run.timestamp())))
    
    def get_schedule_data(self):
        """Get schedule data from form"""
        # Basic data
        data = {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'template_id': self.template_combo.currentData(),
            'is_active': self.active_check.isChecked(),
            'next_run': self.start_datetime.dateTime().toString(Qt.DateFormat.ISODate)
        }
        
        # Schedule configuration
        schedule_type = self.schedule_type_combo.currentText()
        config = {'type': schedule_type.lower().replace(' ', '_')}
        
        if schedule_type == "Daily":
            config['time'] = self.daily_time.time().toString("HH:mm")
        elif schedule_type == "Weekly":
            config['day_of_week'] = self.weekly_day.currentIndex()
            config['time'] = self.weekly_time.time().toString("HH:mm")
        elif schedule_type == "Monthly":
            config['day_of_month'] = self.monthly_day.value()
            config['time'] = self.monthly_time.time().toString("HH:mm")
        elif schedule_type == "Custom Interval":
            config['interval_value'] = self.interval_value.value()
            config['interval_unit'] = self.interval_unit.currentText().lower()
        
        # End conditions
        end_type = self.end_type_combo.currentText()
        if end_type == "After date":
            config['end_date'] = self.end_datetime.dateTime().toString(Qt.DateFormat.ISODate)
        elif end_type == "After count":
            config['max_count'] = self.max_count_spin.value()
        
        data['schedule_config'] = json.dumps(config)
        
        # Recipients
        recipients = []
        source = self.recipient_source_combo.currentText()
        
        if source == "All contacts":
            try:
                contacts = self.db_manager.get_contacts()
                recipients = [contact['email'] for contact in contacts]
            except:
                pass
        elif source == "Select contacts" and hasattr(self, 'contact_list'):
            try:
                contacts = self.db_manager.get_contacts()
                contact_map = {contact['id']: contact['email'] for contact in contacts}
                
                for i in range(self.contact_list.count()):
                    item = self.contact_list.item(i)
                    if item.checkState() == Qt.CheckState.Checked:
                        contact_id = item.data(Qt.ItemDataRole.UserRole)
                        if contact_id in contact_map:
                            recipients.append(contact_map[contact_id])
            except:
                pass
        elif source == "Custom list" and hasattr(self, 'custom_emails'):
            email_text = self.custom_emails.toPlainText().strip()
            if email_text:
                recipients = [email.strip() for email in email_text.split('\n') if email.strip()]
        
        data['recipients'] = recipients
        
        return data
    
    def validate_data(self):
        """Validate form data"""
        data = self.get_schedule_data()
        
        if not data['name']:
            QMessageBox.warning(self, "Validation Error", "Please enter a schedule name.")
            return False
        
        if not data['template_id']:
            QMessageBox.warning(self, "Validation Error", "Please select an email template.")
            return False
        
        if not data['recipients']:
            QMessageBox.warning(self, "Validation Error", "Please configure recipients.")
            return False
        
        # Check start time is in the future
        start_time = datetime.fromisoformat(data['next_run'])
        if start_time <= datetime.now():
            QMessageBox.warning(self, "Validation Error", "Start time must be in the future.")
            return False
        
        return True
    
    def accept(self):
        if self.validate_data():
            super().accept()

class SchedulerPanel(QWidget):
    def __init__(self, db_manager, email_scheduler):
        super().__init__()
        self.db_manager = db_manager
        self.email_scheduler = email_scheduler
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        self.load_schedules()
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the scheduler UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("⏰ Email Scheduler")
        title_label.setObjectName("panelTitle")
        layout.addWidget(title_label)
        
        # Create splitter for two-panel layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Schedule list
        self.create_schedules_panel(splitter)
        
        # Right panel - Schedule details
        self.create_details_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([600, 400])
        
        # Apply styles
        self.apply_styles()
    
    def create_schedules_panel(self, parent):
        """Create schedules list panel"""
        schedules_widget = QWidget()
        schedules_layout = QVBoxLayout(schedules_widget)
        
        # Schedules header
        schedules_header = QHBoxLayout()
        
        schedules_title = QLabel("Scheduled Emails")
        schedules_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        schedules_header.addWidget(schedules_title)
        
        schedules_header.addStretch()
        
        # Control buttons
        add_schedule_btn = QPushButton("➕ New Schedule")
        add_schedule_btn.setObjectName("primaryButton")
        add_schedule_btn.clicked.connect(self.add_schedule)
        schedules_header.addWidget(add_schedule_btn)
        
        edit_schedule_btn = QPushButton("✏️ Edit")
        edit_schedule_btn.setObjectName("secondaryButton")
        edit_schedule_btn.clicked.connect(self.edit_schedule)
        schedules_header.addWidget(edit_schedule_btn)
        
        delete_schedule_btn = QPushButton("🗑️ Delete")
        delete_schedule_btn.setObjectName("dangerButton")
        delete_schedule_btn.clicked.connect(self.delete_schedule)
        schedules_header.addWidget(delete_schedule_btn)
        
        schedules_layout.addLayout(schedules_header)
        
        # Schedules table
        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(6)
        self.schedules_table.setHorizontalHeaderLabels([
            "Name", "Template", "Next Run", "Recipients", "Status", "Actions"
        ])
        
        # Configure table
        header = self.schedules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.schedules_table.setAlternatingRowColors(True)
        self.schedules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.schedules_table.itemSelectionChanged.connect(self.show_schedule_details)
        self.schedules_table.doubleClicked.connect(self.edit_schedule)
        
        schedules_layout.addWidget(self.schedules_table)
        
        # Scheduler status
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(status_frame)
        
        self.scheduler_status_label = QLabel("🟢 Scheduler: Running")
        self.scheduler_status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.scheduler_status_label)
        
        status_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.refresh_data)
        status_layout.addWidget(refresh_btn)
        
        schedules_layout.addWidget(status_frame)
        
        parent.addWidget(schedules_widget)
    
    def create_details_panel(self, parent):
        """Create schedule details panel"""
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # Details header
        details_title = QLabel("Schedule Details")
        details_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        details_layout.addWidget(details_title)
        
        # Details content
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.details_content = QWidget()
        self.details_layout = QVBoxLayout(self.details_content)
        self.details_scroll.setWidget(self.details_content)
        
        details_layout.addWidget(self.details_scroll)
        
        # Show empty state initially
        self.show_empty_details()
        
        parent.addWidget(details_widget)
    
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
            background-color: #ffb703;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin: 2px;
        }
        
        #primaryButton:hover {
            background-color: #fb8500;
        }
        
        #secondaryButton {
            background-color: #219ebc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin: 2px;
        }
        
        #secondaryButton:hover {
            background-color: #8ecae6;
        }
        
        #dangerButton {
            background-color: #fb8500;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin: 2px;
        }
        
        #dangerButton:hover {
            background-color: #ffb703;
        }
        
        #statusFrame {
            background-color: #8ecae6;
            border: 1px solid #219ebc;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
        }
        
        #statusLabel {
            font-weight: bold;
            font-size: 14px;
        }
        
        QTableWidget {
            border: 1px solid #219ebc;
            border-radius: 6px;
            background-color: #8ecae6;
            gridline-color: #219ebc;
        }
        
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #8ecae6;
            color: #023047;
        }
        
        QTableWidget::item:selected {
            background-color: #219ebc;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #8ecae6;
            border: 1px solid #219ebc;
            padding: 8px;
            font-weight: bold;
            color: #023047;
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
            color: #023047;
        }
        """
        
        self.setStyleSheet(style)
    
    def load_schedules(self):
        """Load scheduled emails"""
        try:
            schedules = self.db_manager.get_scheduled_emails()
            
            self.schedules_table.setRowCount(len(schedules))
            
            for row, schedule in enumerate(schedules):
                # Name
                self.schedules_table.setItem(row, 0, QTableWidgetItem(schedule['name']))
                
                # Template
                template_name = schedule.get('template_name', 'Unknown')
                self.schedules_table.setItem(row, 1, QTableWidgetItem(template_name))
                
                # Next run
                next_run = datetime.fromisoformat(schedule['next_run'])
                next_run_str = next_run.strftime("%Y-%m-%d %H:%M")
                next_run_item = QTableWidgetItem(next_run_str)
                
                # Color code based on time
                now = datetime.now()
                if next_run < now:
                    next_run_item.setBackground(QColor(231, 76, 60, 50))  # Red for overdue
                elif next_run < now + timedelta(hours=1):
                    next_run_item.setBackground(QColor(241, 196, 15, 50))  # Yellow for soon
                else:
                    next_run_item.setBackground(QColor(39, 174, 96, 50))  # Green for future
                
                self.schedules_table.setItem(row, 2, next_run_item)
                
                # Recipients count
                recipients_count = len(schedule['recipients'])
                self.schedules_table.setItem(row, 3, QTableWidgetItem(str(recipients_count)))
                
                # Status
                status = "Active" if schedule['is_active'] else "Inactive"
                status_item = QTableWidgetItem(status)
                if schedule['is_active']:
                    status_item.setBackground(QColor(39, 174, 96, 50))
                else:
                    status_item.setBackground(QColor(149, 165, 166, 50))
                self.schedules_table.setItem(row, 4, status_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                
                # Toggle button
                toggle_btn = QPushButton("⏸️" if schedule['is_active'] else "▶️")
                toggle_btn.setObjectName("actionButton")
                toggle_btn.setToolTip("Pause" if schedule['is_active'] else "Resume")
                toggle_btn.clicked.connect(lambda checked, s_id=schedule['id']: self.toggle_schedule(s_id))
                actions_layout.addWidget(toggle_btn)
                
                # Run now button
                run_btn = QPushButton("🚀")
                run_btn.setObjectName("actionButton")
                run_btn.setToolTip("Run now")
                run_btn.clicked.connect(lambda checked, s_id=schedule['id']: self.run_schedule_now(s_id))
                actions_layout.addWidget(run_btn)
                
                self.schedules_table.setCellWidget(row, 5, actions_widget)
                
                # Store schedule ID in first column
                self.schedules_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, schedule['id'])
            
        except Exception as e:
            self.logger.error(f"Error loading schedules: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load schedules: {str(e)}")
    
    def show_schedule_details(self):
        """Show details of selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row < 0:
            self.show_empty_details()
            return
        
        try:
            schedule_id = self.schedules_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            schedule = self.db_manager.get_scheduled_email(schedule_id)
            
            if not schedule:
                self.show_empty_details()
                return
            
            # Clear existing content
            for i in reversed(range(self.details_layout.count())):
                child = self.details_layout.takeAt(i)
                if child.widget():
                    child.widget().deleteLater()
            
            # Basic info
            basic_group = QGroupBox("Basic Information")
            basic_layout = QFormLayout(basic_group)
            
            basic_layout.addRow("Name:", QLabel(schedule['name']))
            basic_layout.addRow("Description:", QLabel(schedule.get('description', 'No description')))
            
            template_name = schedule.get('template_name', 'Unknown')
            basic_layout.addRow("Template:", QLabel(template_name))
            
            status = "Active" if schedule['is_active'] else "Inactive"
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {'#27ae60' if schedule['is_active'] else '#95a5a6'}; font-weight: bold;")
            basic_layout.addRow("Status:", status_label)
            
            self.details_layout.addWidget(basic_group)
            
            # Schedule info
            schedule_group = QGroupBox("Schedule Information")
            schedule_layout = QFormLayout(schedule_group)
            
            next_run = datetime.fromisoformat(schedule['next_run'])
            schedule_layout.addRow("Next Run:", QLabel(next_run.strftime("%Y-%m-%d %H:%M:%S")))
            
            # Parse schedule config
            try:
                config = json.loads(schedule.get('schedule_config', '{}'))
                schedule_type = config.get('type', 'unknown').replace('_', ' ').title()
                schedule_layout.addRow("Type:", QLabel(schedule_type))
                
                if 'time' in config:
                    schedule_layout.addRow("Time:", QLabel(config['time']))
                if 'day_of_week' in config:
                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    day_name = days[config['day_of_week']] if config['day_of_week'] < len(days) else "Unknown"
                    schedule_layout.addRow("Day of Week:", QLabel(day_name))
                if 'day_of_month' in config:
                    schedule_layout.addRow("Day of Month:", QLabel(str(config['day_of_month'])))
                if 'interval_value' in config and 'interval_unit' in config:
                    interval_text = f"{config['interval_value']} {config['interval_unit']}"
                    schedule_layout.addRow("Interval:", QLabel(interval_text))
                
            except:
                pass
            
            self.details_layout.addWidget(schedule_group)
            
            # Recipients info
            recipients_group = QGroupBox("Recipients")
            recipients_layout = QVBoxLayout(recipients_group)
            
            recipients_count = len(schedule['recipients'])
            count_label = QLabel(f"Total Recipients: {recipients_count}")
            count_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
            recipients_layout.addWidget(count_label)
            
            if recipients_count > 0:
                recipients_list = QListWidget()
                recipients_list.setMaximumHeight(150)
                
                for email in schedule['recipients'][:20]:  # Show first 20
                    recipients_list.addItem(email)
                
                if recipients_count > 20:
                    recipients_list.addItem(f"... and {recipients_count - 20} more")
                
                recipients_layout.addWidget(recipients_list)
            
            self.details_layout.addWidget(recipients_group)
            
            # Execution history
            history_group = QGroupBox("Recent Executions")
            history_layout = QVBoxLayout(history_group)
            
            # Get recent logs for this schedule
            logs = self.db_manager.get_email_logs(50)
            schedule_logs = [log for log in logs if log.get('schedule_id') == schedule_id]
            
            if schedule_logs:
                history_table = QTableWidget()
                history_table.setColumnCount(3)
                history_table.setHorizontalHeaderLabels(["Date", "Recipients", "Status"])
                history_table.setMaximumHeight(120)
                
                # Group logs by execution time (approximate)
                executions = {}
                for log in schedule_logs[:10]:  # Last 10 executions
                    date_key = log['sent_at'][:16]  # Group by minute
                    if date_key not in executions:
                        executions[date_key] = {'sent': 0, 'failed': 0}
                    
                    if log['status'] == 'sent':
                        executions[date_key]['sent'] += 1
                    else:
                        executions[date_key]['failed'] += 1
                
                history_table.setRowCount(len(executions))
                
                for row, (date_key, stats) in enumerate(executions.items()):
                    # Date
                    date_obj = datetime.fromisoformat(date_key)
                    date_str = date_obj.strftime("%m/%d %H:%M")
                    history_table.setItem(row, 0, QTableWidgetItem(date_str))
                    
                    # Recipients
                    total = stats['sent'] + stats['failed']
                    recipients_text = f"{stats['sent']}/{total}"
                    history_table.setItem(row, 1, QTableWidgetItem(recipients_text))
                    
                    # Status
                    if stats['failed'] == 0:
                        status_text = "Success"
                        status_color = QColor(39, 174, 96, 50)
                    elif stats['sent'] == 0:
                        status_text = "Failed"
                        status_color = QColor(231, 76, 60, 50)
                    else:
                        status_text = "Partial"
                        status_color = QColor(241, 196, 15, 50)
                    
                    status_item = QTableWidgetItem(status_text)
                    status_item.setBackground(status_color)
                    history_table.setItem(row, 2, status_item)
                
                # Configure table
                header = history_table.horizontalHeader()
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
                
                history_layout.addWidget(history_table)
            else:
                no_history_label = QLabel("No execution history available")
                no_history_label.setStyleSheet("color: #95a5a6; font-style: italic;")
                history_layout.addWidget(no_history_label)
            
            self.details_layout.addWidget(history_group)
            
            # Add stretch to push content to top
            self.details_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"Error showing schedule details: {e}")
            self.show_empty_details()
    
    def show_empty_details(self):
        """Show empty state in details panel"""
        # Clear existing content
        for i in reversed(range(self.details_layout.count())):
            child = self.details_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        empty_label = QLabel("Select a schedule to view details")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet(
            "color: #95a5a6; font-size: 16px; font-style: italic; padding: 50px;"
        )
        
        self.details_layout.addWidget(empty_label)
    
    def add_schedule(self):
        """Add new schedule"""
        dialog = ScheduleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                schedule_data = dialog.get_schedule_data()
                
                schedule_id = self.db_manager.add_scheduled_email(
                    schedule_data['name'],
                    schedule_data['template_id'],
                    schedule_data['recipients'],
                    schedule_data['next_run'],
                    schedule_data['schedule_config'],
                    schedule_data['is_active']
                )
                
                # Add to scheduler
                self.email_scheduler.load_schedules()
                
                self.load_schedules()
                QMessageBox.information(self, "Success", "Schedule created successfully!")
                
            except Exception as e:
                self.logger.error(f"Error adding schedule: {e}")
                QMessageBox.critical(self, "Error", f"Failed to create schedule: {str(e)}")
    
    def edit_schedule(self):
        """Edit selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a schedule to edit.")
            return
        
        try:
            schedule_id = self.schedules_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            schedule = self.db_manager.get_scheduled_email(schedule_id)
            
            if not schedule:
                QMessageBox.warning(self, "Error", "Schedule not found.")
                return
            
            dialog = ScheduleDialog(self, schedule)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                schedule_data = dialog.get_schedule_data()
                
                self.db_manager.update_scheduled_email(
                    schedule_id,
                    schedule_data['name'],
                    schedule_data['template_id'],
                    schedule_data['recipients'],
                    schedule_data['next_run'],
                    schedule_data['schedule_config'],
                    schedule_data['is_active']
                )
                
                # Reload scheduler
                self.email_scheduler.load_schedules()
                
                self.load_schedules()
                self.show_schedule_details()  # Refresh details
                QMessageBox.information(self, "Success", "Schedule updated successfully!")
                
        except Exception as e:
            self.logger.error(f"Error editing schedule: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit schedule: {str(e)}")
    
    def delete_schedule(self):
        """Delete selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a schedule to delete.")
            return
        
        schedule_name = self.schedules_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the schedule '{schedule_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                schedule_id = self.schedules_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
                
                # Remove from scheduler first
                self.email_scheduler.remove_schedule(schedule_id)
                
                # Delete from database
                self.db_manager.delete_scheduled_email(schedule_id)
                
                self.load_schedules()
                self.show_empty_details()
                QMessageBox.information(self, "Success", "Schedule deleted successfully!")
                
            except Exception as e:
                self.logger.error(f"Error deleting schedule: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete schedule: {str(e)}")
    
    def toggle_schedule(self, schedule_id):
        """Toggle schedule active status"""
        try:
            schedule = self.db_manager.get_scheduled_email(schedule_id)
            if not schedule:
                return
            
            new_status = not schedule['is_active']
            
            self.db_manager.update_scheduled_email(
                schedule_id,
                schedule['name'],
                schedule['template_id'],
                schedule['recipients'],
                schedule['next_run'],
                schedule['schedule_config'],
                new_status
            )
            
            # Update scheduler
            if new_status:
                self.email_scheduler.resume_schedule(schedule_id)
            else:
                self.email_scheduler.pause_schedule(schedule_id)
            
            self.load_schedules()
            self.show_schedule_details()
            
        except Exception as e:
            self.logger.error(f"Error toggling schedule: {e}")
            QMessageBox.critical(self, "Error", f"Failed to toggle schedule: {str(e)}")
    
    def run_schedule_now(self, schedule_id):
        """Run schedule immediately"""
        try:
            schedule = self.db_manager.get_scheduled_email(schedule_id)
            if not schedule:
                return
            
            reply = QMessageBox.question(
                self, "Confirm Run",
                f"Run schedule '{schedule['name']}' now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Execute schedule
                self.email_scheduler.execute_schedule(schedule_id)
                
                QMessageBox.information(self, "Success", "Schedule executed successfully!")
                
                # Refresh data
                self.refresh_data()
                
        except Exception as e:
            self.logger.error(f"Error running schedule: {e}")
            QMessageBox.critical(self, "Error", f"Failed to run schedule: {str(e)}")
    
    def refresh_data(self):
        """Refresh all data"""
        self.load_schedules()
        self.show_schedule_details()
        
        # Update scheduler status
        if self.email_scheduler.scheduler.running:
            self.scheduler_status_label.setText("🟢 Scheduler: Running")
        else:
            self.scheduler_status_label.setText("🔴 Scheduler: Stopped")
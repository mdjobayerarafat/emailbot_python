from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QLineEdit, QComboBox, QDateEdit, QCheckBox, QSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QMessageBox,
    QSplitter, QFrame, QTabWidget, QTextEdit, QProgressBar,
    QFileDialog, QApplication
)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon
import logging
import json
import csv
import os
from datetime import datetime, timedelta

class ExportThread(QThread):
    """Thread for exporting logs to avoid UI blocking"""
    progress_updated = pyqtSignal(int)
    export_completed = pyqtSignal(str)
    export_failed = pyqtSignal(str)
    
    def __init__(self, logs, file_path, export_format):
        super().__init__()
        self.logs = logs
        self.file_path = file_path
        self.export_format = export_format
    
    def run(self):
        try:
            total_logs = len(self.logs)
            
            if self.export_format.lower() == 'csv':
                self.export_to_csv()
            elif self.export_format.lower() == 'json':
                self.export_to_json()
            else:
                self.export_failed.emit(f"Unsupported format: {self.export_format}")
                return
            
            self.export_completed.emit(self.file_path)
            
        except Exception as e:
            self.export_failed.emit(str(e))
    
    def export_to_csv(self):
        """Export logs to CSV format"""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
            if not self.logs:
                return
            
            # Get all unique keys from logs
            fieldnames = set()
            for log in self.logs:
                fieldnames.update(log.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, log in enumerate(self.logs):
                writer.writerow(log)
                progress = int((i + 1) / len(self.logs) * 100)
                self.progress_updated.emit(progress)
    
    def export_to_json(self):
        """Export logs to JSON format"""
        with open(self.file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.logs, jsonfile, indent=2, default=str, ensure_ascii=False)
            self.progress_updated.emit(100)

class LogDetailDialog(QDialog):
    """Dialog to show detailed log information"""
    
    def __init__(self, parent=None, log_data=None):
        super().__init__(parent)
        self.log_data = log_data
        self.init_ui()
        
        if log_data:
            self.load_log_data()
    
    def init_ui(self):
        self.setWindowTitle("Email Log Details")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Basic info tab
        self.create_basic_tab(tab_widget)
        
        # Content tab
        self.create_content_tab(tab_widget)
        
        # Technical tab
        self.create_technical_tab(tab_widget)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_basic_tab(self, parent):
        """Create basic information tab"""
        basic_widget = QWidget()
        layout = QFormLayout(basic_widget)
        
        # Basic fields
        self.timestamp_label = QLabel()
        layout.addRow("Timestamp:", self.timestamp_label)
        
        self.recipient_label = QLabel()
        layout.addRow("Recipient:", self.recipient_label)
        
        self.subject_label = QLabel()
        self.subject_label.setWordWrap(True)
        layout.addRow("Subject:", self.subject_label)
        
        self.status_label = QLabel()
        layout.addRow("Status:", self.status_label)
        
        self.template_label = QLabel()
        layout.addRow("Template:", self.template_label)
        
        self.attachments_label = QLabel()
        layout.addRow("Attachments:", self.attachments_label)
        
        parent.addTab(basic_widget, "📋 Basic Info")
    
    def create_content_tab(self, parent):
        """Create content tab"""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Email body
        body_label = QLabel("Email Body:")
        body_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(body_label)
        
        self.body_text = QTextEdit()
        self.body_text.setReadOnly(True)
        layout.addWidget(self.body_text)
        
        parent.addTab(content_widget, "📄 Content")
    
    def create_technical_tab(self, parent):
        """Create technical details tab"""
        technical_widget = QWidget()
        layout = QFormLayout(technical_widget)
        
        # Technical fields
        self.message_id_label = QLabel()
        layout.addRow("Message ID:", self.message_id_label)
        
        self.sender_label = QLabel()
        layout.addRow("Sender:", self.sender_label)
        
        self.reply_to_label = QLabel()
        layout.addRow("Reply To:", self.reply_to_label)
        
        self.error_message_label = QLabel()
        self.error_message_label.setWordWrap(True)
        layout.addRow("Error Message:", self.error_message_label)
        
        self.retry_count_label = QLabel()
        layout.addRow("Retry Count:", self.retry_count_label)
        
        parent.addTab(technical_widget, "🔧 Technical")
    
    def load_log_data(self):
        """Load log data into the dialog"""
        if not self.log_data:
            return
        
        # Basic info
        self.timestamp_label.setText(str(self.log_data.get('timestamp', 'N/A')))
        self.recipient_label.setText(self.log_data.get('recipient', 'N/A'))
        self.subject_label.setText(self.log_data.get('subject', 'N/A'))
        
        # Status with color
        status = self.log_data.get('status', 'Unknown')
        self.status_label.setText(status)
        if status.lower() == 'sent':
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        elif status.lower() == 'failed':
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        self.template_label.setText(self.log_data.get('template_name', 'N/A'))
        
        # Attachments
        attachments = self.log_data.get('attachments', '')
        if attachments:
            self.attachments_label.setText(attachments)
        else:
            self.attachments_label.setText("None")
        
        # Content
        body = self.log_data.get('body', '')
        if body:
            self.body_text.setPlainText(body)
        else:
            self.body_text.setPlainText("No content available")
        
        # Technical
        self.message_id_label.setText(self.log_data.get('message_id', 'N/A'))
        self.sender_label.setText(self.log_data.get('sender', 'N/A'))
        self.reply_to_label.setText(self.log_data.get('reply_to', 'N/A'))
        
        error_message = self.log_data.get('error_message', '')
        if error_message:
            self.error_message_label.setText(error_message)
            self.error_message_label.setStyleSheet("color: #e74c3c;")
        else:
            self.error_message_label.setText("None")
            self.error_message_label.setStyleSheet("color: #27ae60;")
        
        self.retry_count_label.setText(str(self.log_data.get('retry_count', 0)))

class LogsPanel(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Store all logs for filtering
        self.all_logs = []
        self.filtered_logs = []
        
        self.init_ui()
        self.load_logs()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the logs UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("📊 Email Logs")
        title_label.setObjectName("panelTitle")
        layout.addWidget(title_label)
        
        # Create splitter for two-panel layout
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Top panel - Filters and controls
        self.create_filters_panel(splitter)
        
        # Bottom panel - Logs table
        self.create_logs_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([200, 600])
        
        # Apply styles
        self.apply_styles()
    
    def create_filters_panel(self, parent):
        """Create filters and controls panel"""
        filters_widget = QWidget()
        filters_layout = QVBoxLayout(filters_widget)
        
        # Filters header
        filters_title = QLabel("Filters & Controls")
        filters_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        filters_layout.addWidget(filters_title)
        
        # Create filter tabs
        filter_tabs = QTabWidget()
        filters_layout.addWidget(filter_tabs)
        
        # Basic filters tab
        self.create_basic_filters_tab(filter_tabs)
        
        # Advanced filters tab
        self.create_advanced_filters_tab(filter_tabs)
        
        # Export tab
        self.create_export_tab(filter_tabs)
        
        parent.addWidget(filters_widget)
    
    def create_basic_filters_tab(self, parent):
        """Create basic filters tab"""
        basic_widget = QWidget()
        layout = QHBoxLayout(basic_widget)
        
        # Search
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search logs (recipient, subject, content...)")
        self.search_edit.textChanged.connect(self.filter_logs)
        search_layout.addWidget(self.search_edit)
        
        layout.addWidget(search_group)
        
        # Status filter
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Sent", "Failed", "Pending"])
        self.status_filter.currentTextChanged.connect(self.filter_logs)
        status_layout.addWidget(self.status_filter)
        
        layout.addWidget(status_group)
        
        # Date range
        date_group = QGroupBox("Date Range")
        date_layout = QVBoxLayout(date_group)
        
        date_range_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.dateChanged.connect(self.filter_logs)
        date_range_layout.addWidget(QLabel("From:"))
        date_range_layout.addWidget(self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.dateChanged.connect(self.filter_logs)
        date_range_layout.addWidget(QLabel("To:"))
        date_range_layout.addWidget(self.end_date)
        
        date_layout.addLayout(date_range_layout)
        
        # Quick date buttons
        quick_date_layout = QHBoxLayout()
        
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(lambda: self.set_date_range(0))
        quick_date_layout.addWidget(today_btn)
        
        week_btn = QPushButton("Last 7 days")
        week_btn.clicked.connect(lambda: self.set_date_range(7))
        quick_date_layout.addWidget(week_btn)
        
        month_btn = QPushButton("Last 30 days")
        month_btn.clicked.connect(lambda: self.set_date_range(30))
        quick_date_layout.addWidget(month_btn)
        
        date_layout.addLayout(quick_date_layout)
        
        layout.addWidget(date_group)
        
        # Control buttons
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.load_logs)
        controls_layout.addWidget(refresh_btn)
        
        clear_filters_btn = QPushButton("🗑️ Clear Filters")
        clear_filters_btn.setObjectName("secondaryButton")
        clear_filters_btn.clicked.connect(self.clear_filters)
        controls_layout.addWidget(clear_filters_btn)
        
        layout.addWidget(controls_group)
        
        parent.addTab(basic_widget, "🔍 Basic Filters")
    
    def create_advanced_filters_tab(self, parent):
        """Create advanced filters tab"""
        advanced_widget = QWidget()
        layout = QHBoxLayout(advanced_widget)
        
        # Template filter
        template_group = QGroupBox("Template")
        template_layout = QVBoxLayout(template_group)
        
        self.template_filter = QComboBox()
        self.template_filter.currentTextChanged.connect(self.filter_logs)
        template_layout.addWidget(self.template_filter)
        
        layout.addWidget(template_group)
        
        # Sender filter
        sender_group = QGroupBox("Sender")
        sender_layout = QVBoxLayout(sender_group)
        
        self.sender_filter = QComboBox()
        self.sender_filter.setEditable(True)
        self.sender_filter.currentTextChanged.connect(self.filter_logs)
        sender_layout.addWidget(self.sender_filter)
        
        layout.addWidget(sender_group)
        
        # Attachments filter
        attachments_group = QGroupBox("Attachments")
        attachments_layout = QVBoxLayout(attachments_group)
        
        self.has_attachments_check = QCheckBox("Has attachments")
        self.has_attachments_check.stateChanged.connect(self.filter_logs)
        attachments_layout.addWidget(self.has_attachments_check)
        
        self.no_attachments_check = QCheckBox("No attachments")
        self.no_attachments_check.stateChanged.connect(self.filter_logs)
        attachments_layout.addWidget(self.no_attachments_check)
        
        layout.addWidget(attachments_group)
        
        # Retry filter
        retry_group = QGroupBox("Retry Count")
        retry_layout = QVBoxLayout(retry_group)
        
        retry_range_layout = QHBoxLayout()
        retry_range_layout.addWidget(QLabel("Min:"))
        
        self.min_retry_spin = QSpinBox()
        self.min_retry_spin.setMinimum(0)
        self.min_retry_spin.setMaximum(10)
        self.min_retry_spin.valueChanged.connect(self.filter_logs)
        retry_range_layout.addWidget(self.min_retry_spin)
        
        retry_range_layout.addWidget(QLabel("Max:"))
        
        self.max_retry_spin = QSpinBox()
        self.max_retry_spin.setMinimum(0)
        self.max_retry_spin.setMaximum(10)
        self.max_retry_spin.setValue(10)
        self.max_retry_spin.valueChanged.connect(self.filter_logs)
        retry_range_layout.addWidget(self.max_retry_spin)
        
        retry_layout.addLayout(retry_range_layout)
        
        layout.addWidget(retry_group)
        
        parent.addTab(advanced_widget, "⚙️ Advanced")
    
    def create_export_tab(self, parent):
        """Create export tab"""
        export_widget = QWidget()
        layout = QVBoxLayout(export_widget)
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QFormLayout(export_group)
        
        # Export format
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "JSON"])
        export_layout.addRow("Format:", self.export_format)
        
        # Include filters
        self.export_filtered_check = QCheckBox("Export only filtered results")
        self.export_filtered_check.setChecked(True)
        export_layout.addRow("", self.export_filtered_check)
        
        layout.addWidget(export_group)
        
        # Export buttons
        export_buttons_layout = QHBoxLayout()
        
        export_all_btn = QPushButton("📤 Export All Logs")
        export_all_btn.setObjectName("primaryButton")
        export_all_btn.clicked.connect(lambda: self.export_logs(False))
        export_buttons_layout.addWidget(export_all_btn)
        
        export_filtered_btn = QPushButton("📤 Export Filtered")
        export_filtered_btn.setObjectName("secondaryButton")
        export_filtered_btn.clicked.connect(lambda: self.export_logs(True))
        export_buttons_layout.addWidget(export_filtered_btn)
        
        layout.addLayout(export_buttons_layout)
        
        # Export progress
        self.export_progress = QProgressBar()
        self.export_progress.setVisible(False)
        layout.addWidget(self.export_progress)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.total_logs_label = QLabel("0")
        stats_layout.addRow("Total Logs:", self.total_logs_label)
        
        self.filtered_logs_label = QLabel("0")
        stats_layout.addRow("Filtered Logs:", self.filtered_logs_label)
        
        self.sent_logs_label = QLabel("0")
        stats_layout.addRow("Sent:", self.sent_logs_label)
        
        self.failed_logs_label = QLabel("0")
        stats_layout.addRow("Failed:", self.failed_logs_label)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        parent.addTab(export_widget, "📤 Export")
    
    def create_logs_panel(self, parent):
        """Create logs table panel"""
        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        
        # Logs header
        logs_header = QHBoxLayout()
        
        logs_title = QLabel("Email Logs")
        logs_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        logs_header.addWidget(logs_title)
        
        logs_header.addStretch()
        
        # Auto-refresh toggle
        self.auto_refresh_check = QCheckBox("Auto-refresh (30s)")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        logs_header.addWidget(self.auto_refresh_check)
        
        # Results per page
        logs_header.addWidget(QLabel("Show:"))
        
        self.results_per_page = QComboBox()
        self.results_per_page.addItems(["50", "100", "200", "500", "All"])
        self.results_per_page.setCurrentText("100")
        self.results_per_page.currentTextChanged.connect(self.filter_logs)
        logs_header.addWidget(self.results_per_page)
        
        logs_layout.addLayout(logs_header)
        
        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(7)
        self.logs_table.setHorizontalHeaderLabels([
            "Timestamp", "Recipient", "Subject", "Status", "Template", "Attachments", "Retries"
        ])
        
        # Configure table
        header = self.logs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logs_table.doubleClicked.connect(self.show_log_details)
        
        # Context menu
        self.logs_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.logs_table.customContextMenuRequested.connect(self.show_context_menu)
        
        logs_layout.addWidget(self.logs_table)
        
        # Status bar
        status_frame = QFrame()
        status_frame.setObjectName("statsFrame")
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("📊 0 logs displayed")
        self.status_label.setObjectName("statsLabel")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Action buttons
        view_details_btn = QPushButton("👁️ View Details")
        view_details_btn.setObjectName("secondaryButton")
        view_details_btn.clicked.connect(self.show_log_details)
        status_layout.addWidget(view_details_btn)
        
        delete_log_btn = QPushButton("🗑️ Delete")
        delete_log_btn.setObjectName("dangerButton")
        delete_log_btn.clicked.connect(self.delete_selected_logs)
        status_layout.addWidget(delete_log_btn)
        
        logs_layout.addWidget(status_frame)
        
        parent.addWidget(logs_widget)
    
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
        
        #statsFrame {
            background-color: #8ecae6;
            border: 1px solid #219ebc;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
        }
        
        #statsLabel {
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
            color: #ffffff;
        }
        
        QLineEdit, QComboBox, QDateEdit, QSpinBox {
            border: 1px solid #219ebc;
            border-radius: 4px;
            padding: 6px;
            background-color: #023047;
            color: white;
        }
        
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
            border-color: #ffb703;
        }
        
        QProgressBar {
            border: 1px solid #219ebc;
            border-radius: 4px;
            text-align: center;
            background-color: #8ecae6;
        }
        
        QProgressBar::chunk {
            background-color: #ffb703;
            border-radius: 3px;
        }
        """
        
        self.setStyleSheet(style)
    
    def load_logs(self):
        """Load email logs from database"""
        try:
            self.all_logs = self.db_manager.get_email_logs()
            
            # Update filter dropdowns
            self.update_filter_dropdowns()
            
            # Apply current filters
            self.filter_logs()
            
            # Update statistics
            self.update_statistics()
            
        except Exception as e:
            self.logger.error(f"Error loading logs: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load logs: {str(e)}")
    
    def update_filter_dropdowns(self):
        """Update filter dropdown options based on available data"""
        # Update template filter
        current_template = self.template_filter.currentText()
        templates = set()
        
        for log in self.all_logs:
            template_name = log.get('template_name', '').strip()
            if template_name:
                templates.add(template_name)
        
        self.template_filter.clear()
        self.template_filter.addItem("All Templates")
        for template in sorted(templates):
            self.template_filter.addItem(template)
        
        # Restore selection
        if current_template:
            index = self.template_filter.findText(current_template)
            if index >= 0:
                self.template_filter.setCurrentIndex(index)
        
        # Update sender filter
        current_sender = self.sender_filter.currentText()
        senders = set()
        
        for log in self.all_logs:
            sender = log.get('sender', '').strip()
            if sender:
                senders.add(sender)
        
        self.sender_filter.clear()
        self.sender_filter.addItem("All Senders")
        for sender in sorted(senders):
            self.sender_filter.addItem(sender)
        
        # Restore selection
        if current_sender:
            index = self.sender_filter.findText(current_sender)
            if index >= 0:
                self.sender_filter.setCurrentIndex(index)
    
    def filter_logs(self):
        """Apply filters to logs"""
        if not hasattr(self, 'all_logs'):
            return
        
        filtered_logs = []
        
        # Get filter values
        search_text = self.search_edit.text().lower()
        status_filter = self.status_filter.currentText()
        template_filter = self.template_filter.currentText()
        sender_filter = self.sender_filter.currentText()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        has_attachments = self.has_attachments_check.isChecked()
        no_attachments = self.no_attachments_check.isChecked()
        min_retry = self.min_retry_spin.value()
        max_retry = self.max_retry_spin.value()
        
        for log in self.all_logs:
            # Search filter
            if search_text:
                searchable_text = (
                    log.get('recipient', '').lower() + " " +
                    log.get('subject', '').lower() + " " +
                    log.get('body', '').lower() + " " +
                    log.get('template_name', '').lower()
                )
                
                if search_text not in searchable_text:
                    continue
            
            # Status filter
            if status_filter != "All Status":
                if log.get('status', '').lower() != status_filter.lower():
                    continue
            
            # Template filter
            if template_filter != "All Templates":
                if log.get('template_name', '') != template_filter:
                    continue
            
            # Sender filter
            if sender_filter != "All Senders":
                if log.get('sender', '') != sender_filter:
                    continue
            
            # Date filter
            try:
                log_date = datetime.strptime(log.get('timestamp', ''), '%Y-%m-%d %H:%M:%S').date()
                if log_date < start_date or log_date > end_date:
                    continue
            except (ValueError, TypeError):
                # Skip logs with invalid dates
                continue
            
            # Attachments filter
            log_has_attachments = bool(log.get('attachments', '').strip())
            if has_attachments and not log_has_attachments:
                continue
            if no_attachments and log_has_attachments:
                continue
            
            # Retry filter
            retry_count = log.get('retry_count', 0)
            if retry_count < min_retry or retry_count > max_retry:
                continue
            
            filtered_logs.append(log)
        
        # Store filtered logs
        self.filtered_logs = filtered_logs
        
        # Apply pagination
        self.display_logs(filtered_logs)
        
        # Update statistics
        self.update_statistics()
    
    def display_logs(self, logs):
        """Display logs in table with pagination"""
        # Apply pagination
        results_per_page = self.results_per_page.currentText()
        if results_per_page != "All":
            max_results = int(results_per_page)
            logs = logs[:max_results]
        
        self.logs_table.setRowCount(len(logs))
        
        for row, log in enumerate(logs):
            # Timestamp
            timestamp = log.get('timestamp', '')[:19]  # Remove microseconds
            self.logs_table.setItem(row, 0, QTableWidgetItem(timestamp))
            
            # Recipient
            recipient = log.get('recipient', '')
            self.logs_table.setItem(row, 1, QTableWidgetItem(recipient))
            
            # Subject (truncated)
            subject = log.get('subject', '')
            if len(subject) > 50:
                subject = subject[:47] + "..."
            self.logs_table.setItem(row, 2, QTableWidgetItem(subject))
            
            # Status with color
            status = log.get('status', 'Unknown')
            status_item = QTableWidgetItem(status)
            if status.lower() == 'sent':
                status_item.setBackground(QColor(39, 174, 96, 50))
                status_item.setForeground(QColor(39, 174, 96))
            elif status.lower() == 'failed':
                status_item.setBackground(QColor(231, 76, 60, 50))
                status_item.setForeground(QColor(231, 76, 60))
            else:
                status_item.setBackground(QColor(243, 156, 18, 50))
                status_item.setForeground(QColor(243, 156, 18))
            
            status_item.setFont(QFont('Arial', 9, QFont.Weight.Bold))
            self.logs_table.setItem(row, 3, status_item)
            
            # Template
            template_name = log.get('template_name', 'N/A')
            self.logs_table.setItem(row, 4, QTableWidgetItem(template_name))
            
            # Attachments
            attachments = log.get('attachments', '')
            if attachments:
                attachment_count = len(attachments.split(','))
                attachments_text = f"📎 {attachment_count}"
            else:
                attachments_text = "-"
            self.logs_table.setItem(row, 5, QTableWidgetItem(attachments_text))
            
            # Retry count
            retry_count = str(log.get('retry_count', 0))
            retry_item = QTableWidgetItem(retry_count)
            if int(retry_count) > 0:
                retry_item.setBackground(QColor(243, 156, 18, 50))
            self.logs_table.setItem(row, 6, retry_item)
            
            # Store log ID in first column
            self.logs_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, log.get('id'))
        
        # Update status
        total_filtered = len(self.filtered_logs)
        displayed = len(logs)
        
        if displayed < total_filtered:
            status_text = f"📊 Showing {displayed} of {total_filtered} logs"
        else:
            status_text = f"📊 {displayed} logs displayed"
        
        self.status_label.setText(status_text)
    
    def update_statistics(self):
        """Update statistics in export tab"""
        total_logs = len(self.all_logs)
        filtered_logs = len(self.filtered_logs)
        
        sent_count = sum(1 for log in self.filtered_logs if log.get('status', '').lower() == 'sent')
        failed_count = sum(1 for log in self.filtered_logs if log.get('status', '').lower() == 'failed')
        
        self.total_logs_label.setText(str(total_logs))
        self.filtered_logs_label.setText(str(filtered_logs))
        self.sent_logs_label.setText(str(sent_count))
        self.failed_logs_label.setText(str(failed_count))
        
        # Update label colors
        self.sent_logs_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.failed_logs_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def set_date_range(self, days):
        """Set date range for quick filters"""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-days)
        
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_edit.clear()
        self.status_filter.setCurrentIndex(0)
        self.template_filter.setCurrentIndex(0)
        self.sender_filter.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
        self.has_attachments_check.setChecked(False)
        self.no_attachments_check.setChecked(False)
        self.min_retry_spin.setValue(0)
        self.max_retry_spin.setValue(10)
        self.results_per_page.setCurrentText("100")
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh timer"""
        if self.auto_refresh_check.isChecked():
            self.refresh_timer.start(30000)
        else:
            self.refresh_timer.stop()
    
    def auto_refresh(self):
        """Auto-refresh logs"""
        if self.auto_refresh_check.isChecked():
            self.load_logs()
    
    def show_log_details(self):
        """Show detailed log information"""
        current_row = self.logs_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a log entry to view details.")
            return
        
        try:
            log_id = self.logs_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            
            # Find the log in filtered logs
            log_data = None
            for log in self.filtered_logs:
                if log.get('id') == log_id:
                    log_data = log
                    break
            
            if not log_data:
                QMessageBox.warning(self, "Error", "Log entry not found.")
                return
            
            dialog = LogDetailDialog(self, log_data)
            dialog.exec()
            
        except Exception as e:
            self.logger.error(f"Error showing log details: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show log details: {str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for logs table"""
        # This could be implemented to show additional options
        pass
    
    def delete_selected_logs(self):
        """Delete selected log entries"""
        selected_rows = set()
        for item in self.logs_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select log entries to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {len(selected_rows)} log entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                log_ids = []
                for row in selected_rows:
                    log_id = self.logs_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                    if log_id:
                        log_ids.append(log_id)
                
                # Delete from database
                for log_id in log_ids:
                    self.db_manager.delete_email_log(log_id)
                
                self.load_logs()
                QMessageBox.information(self, "Success", f"Deleted {len(log_ids)} log entries.")
                
            except Exception as e:
                self.logger.error(f"Error deleting logs: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete logs: {str(e)}")
    
    def export_logs(self, filtered_only=True):
        """Export logs to file"""
        # Determine which logs to export
        if filtered_only:
            logs_to_export = self.filtered_logs
            default_name = "filtered_email_logs"
        else:
            logs_to_export = self.all_logs
            default_name = "all_email_logs"
        
        if not logs_to_export:
            QMessageBox.warning(self, "Warning", "No logs to export.")
            return
        
        # Get export format
        export_format = self.export_format.currentText().lower()
        
        # Get file path
        file_filter = f"{export_format.upper()} Files (*.{export_format})"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs",
            f"{default_name}.{export_format}",
            file_filter
        )
        
        if not file_path:
            return
        
        # Start export in background thread
        self.export_progress.setVisible(True)
        self.export_progress.setValue(0)
        
        self.export_thread = ExportThread(logs_to_export, file_path, export_format)
        self.export_thread.progress_updated.connect(self.export_progress.setValue)
        self.export_thread.export_completed.connect(self.on_export_completed)
        self.export_thread.export_failed.connect(self.on_export_failed)
        self.export_thread.start()
    
    def on_export_completed(self, file_path):
        """Handle export completion"""
        self.export_progress.setVisible(False)
        QMessageBox.information(
            self, "Export Complete",
            f"Logs exported successfully to:\n{file_path}"
        )
    
    def on_export_failed(self, error_message):
        """Handle export failure"""
        self.export_progress.setVisible(False)
        QMessageBox.critical(
            self, "Export Failed",
            f"Failed to export logs:\n{error_message}"
        )
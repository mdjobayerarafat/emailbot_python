from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QMessageBox,
    QSplitter, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
import logging
import json

class AutoReplyRuleDialog(QDialog):
    def __init__(self, parent=None, rule=None):
        super().__init__(parent)
        self.rule = rule
        self.init_ui()
        
        if rule:
            self.load_rule_data()
    
    def init_ui(self):
        self.setWindowTitle("Auto-Reply Rule")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Rule name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter rule name")
        form_layout.addRow("Rule Name:", self.name_edit)
        
        # Keywords
        self.keywords_edit = QLineEdit()
        self.keywords_edit.setPlaceholderText("Enter keywords separated by commas")
        form_layout.addRow("Keywords:", self.keywords_edit)
        
        # Match type
        self.match_type_combo = QComboBox()
        self.match_type_combo.addItems(["Any keyword", "All keywords", "Exact phrase"])
        form_layout.addRow("Match Type:", self.match_type_combo)
        
        # Case sensitive
        self.case_sensitive_check = QCheckBox("Case sensitive matching")
        form_layout.addRow("", self.case_sensitive_check)
        
        # Template selection
        self.template_combo = QComboBox()
        self.load_templates()
        form_layout.addRow("Reply Template:", self.template_combo)
        
        # Priority
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 10)
        self.priority_spin.setValue(5)
        form_layout.addRow("Priority (1-10):", self.priority_spin)
        
        # Active
        self.active_check = QCheckBox("Rule is active")
        self.active_check.setChecked(True)
        form_layout.addRow("", self.active_check)
        
        layout.addLayout(form_layout)
        
        # Preview section
        preview_group = QGroupBox("Template Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(100)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.template_combo.currentTextChanged.connect(self.update_preview)
    
    def load_templates(self):
        """Load email templates"""
        try:
            db_manager = self.parent().db_manager
            templates = db_manager.get_email_templates()
            
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
            
            db_manager = self.parent().db_manager
            template = db_manager.get_email_template(template_id)
            
            if template:
                preview = f"Subject: {template['subject']}\n\n{template['body'][:200]}..."
                self.preview_text.setPlainText(preview)
            
        except Exception as e:
            logging.error(f"Error updating preview: {e}")
    
    def load_rule_data(self):
        """Load existing rule data"""
        if not self.rule:
            return
        
        self.name_edit.setText(self.rule['name'])
        self.keywords_edit.setText(self.rule['keywords'])
        
        # Set match type
        match_type = self.rule.get('match_type', 'any')
        if match_type == 'any':
            self.match_type_combo.setCurrentIndex(0)
        elif match_type == 'all':
            self.match_type_combo.setCurrentIndex(1)
        else:
            self.match_type_combo.setCurrentIndex(2)
        
        self.case_sensitive_check.setChecked(self.rule.get('case_sensitive', False))
        
        # Set template
        template_id = self.rule.get('template_id')
        if template_id:
            for i in range(self.template_combo.count()):
                if self.template_combo.itemData(i) == template_id:
                    self.template_combo.setCurrentIndex(i)
                    break
        
        self.priority_spin.setValue(self.rule.get('priority', 5))
        self.active_check.setChecked(self.rule.get('is_active', True))
    
    def get_rule_data(self):
        """Get rule data from form"""
        match_types = ['any', 'all', 'exact']
        
        return {
            'name': self.name_edit.text().strip(),
            'keywords': self.keywords_edit.text().strip(),
            'match_type': match_types[self.match_type_combo.currentIndex()],
            'case_sensitive': self.case_sensitive_check.isChecked(),
            'template_id': self.template_combo.currentData(),
            'priority': self.priority_spin.value(),
            'is_active': self.active_check.isChecked()
        }
    
    def validate_data(self):
        """Validate form data"""
        data = self.get_rule_data()
        
        if not data['name']:
            QMessageBox.warning(self, "Validation Error", "Please enter a rule name.")
            return False
        
        if not data['keywords']:
            QMessageBox.warning(self, "Validation Error", "Please enter keywords.")
            return False
        
        if not data['template_id']:
            QMessageBox.warning(self, "Validation Error", "Please select a template.")
            return False
        
        return True
    
    def accept(self):
        if self.validate_data():
            super().accept()

class InboxMonitorPanel(QWidget):
    rule_updated = pyqtSignal()
    
    def __init__(self, db_manager, email_handler):
        super().__init__()
        self.db_manager = db_manager
        self.email_handler = email_handler
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        self.load_rules()
        self.load_recent_emails()
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_recent_emails)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the inbox monitor UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("👁️ Inbox Monitor")
        title_label.setObjectName("panelTitle")
        layout.addWidget(title_label)
        
        # Create splitter for two-panel layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Auto-reply rules
        self.create_rules_panel(splitter)
        
        # Right panel - Recent emails
        self.create_emails_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
        
        # Apply styles
        self.apply_styles()
    
    def create_rules_panel(self, parent):
        """Create auto-reply rules panel"""
        rules_widget = QWidget()
        rules_layout = QVBoxLayout(rules_widget)
        
        # Rules header
        rules_header = QHBoxLayout()
        
        rules_title = QLabel("Auto-Reply Rules")
        rules_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        rules_header.addWidget(rules_title)
        
        rules_header.addStretch()
        
        # Control buttons
        add_rule_btn = QPushButton("➕ Add Rule")
        add_rule_btn.setObjectName("primaryButton")
        add_rule_btn.clicked.connect(self.add_rule)
        rules_header.addWidget(add_rule_btn)
        
        edit_rule_btn = QPushButton("✏️ Edit")
        edit_rule_btn.setObjectName("secondaryButton")
        edit_rule_btn.clicked.connect(self.edit_rule)
        rules_header.addWidget(edit_rule_btn)
        
        delete_rule_btn = QPushButton("🗑️ Delete")
        delete_rule_btn.setObjectName("dangerButton")
        delete_rule_btn.clicked.connect(self.delete_rule)
        rules_header.addWidget(delete_rule_btn)
        
        rules_layout.addLayout(rules_header)
        
        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels([
            "Name", "Keywords", "Template", "Priority", "Active"
        ])
        
        # Configure table
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.rules_table.setAlternatingRowColors(True)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.doubleClicked.connect(self.edit_rule)
        
        rules_layout.addWidget(self.rules_table)
        
        # Monitoring status
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("📴 Monitoring: Stopped")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.toggle_monitor_btn = QPushButton("▶️ Start Monitoring")
        self.toggle_monitor_btn.setObjectName("primaryButton")
        self.toggle_monitor_btn.clicked.connect(self.toggle_monitoring)
        status_layout.addWidget(self.toggle_monitor_btn)
        
        rules_layout.addWidget(status_frame)
        
        parent.addWidget(rules_widget)
    
    def create_emails_panel(self, parent):
        """Create recent emails panel"""
        emails_widget = QWidget()
        emails_layout = QVBoxLayout(emails_widget)
        
        # Emails header
        emails_header = QHBoxLayout()
        
        emails_title = QLabel("Recent Emails")
        emails_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        emails_header.addWidget(emails_title)
        
        emails_header.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.load_recent_emails)
        emails_header.addWidget(refresh_btn)
        
        emails_layout.addLayout(emails_header)
        
        # Emails table
        self.emails_table = QTableWidget()
        self.emails_table.setColumnCount(5)
        self.emails_table.setHorizontalHeaderLabels([
            "Time", "From", "Subject", "Auto-Reply", "Status"
        ])
        
        # Configure table
        header = self.emails_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.emails_table.setAlternatingRowColors(True)
        self.emails_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        emails_layout.addWidget(self.emails_table)
        
        # Email preview
        preview_group = QGroupBox("Email Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.email_preview = QTextEdit()
        self.email_preview.setReadOnly(True)
        self.email_preview.setMaximumHeight(150)
        preview_layout.addWidget(self.email_preview)
        
        emails_layout.addWidget(preview_group)
        
        # Connect selection change
        self.emails_table.itemSelectionChanged.connect(self.show_email_preview)
        
        parent.addWidget(emails_widget)
    
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
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin: 2px;
        }
        
        #primaryButton:hover {
            background-color: #023047;
        }
        
        #secondaryButton {
            background-color: #8ecae6;
            color: #023047;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin: 2px;
        }
        
        #secondaryButton:hover {
            background-color: #219ebc;
            color: white;
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
            color: #023047;
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
        """
        
        self.setStyleSheet(style)
    
    def load_rules(self):
        """Load auto-reply rules"""
        try:
            rules = self.db_manager.get_auto_reply_rules()
            
            self.rules_table.setRowCount(len(rules))
            
            for row, rule in enumerate(rules):
                # Name
                self.rules_table.setItem(row, 0, QTableWidgetItem(rule['name']))
                
                # Keywords
                keywords = rule['keywords'][:50] + "..." if len(rule['keywords']) > 50 else rule['keywords']
                self.rules_table.setItem(row, 1, QTableWidgetItem(keywords))
                
                # Template
                template_name = rule.get('template_name', 'Unknown')
                self.rules_table.setItem(row, 2, QTableWidgetItem(template_name))
                
                # Priority
                priority_item = QTableWidgetItem(str(rule['priority']))
                priority_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.rules_table.setItem(row, 3, priority_item)
                
                # Active status
                active_item = QTableWidgetItem("✅" if rule['is_active'] else "❌")
                active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if rule['is_active']:
                    active_item.setBackground(QColor(39, 174, 96, 50))
                else:
                    active_item.setBackground(QColor(231, 76, 60, 50))
                self.rules_table.setItem(row, 4, active_item)
                
                # Store rule ID in first column
                self.rules_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, rule['id'])
            
        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load rules: {str(e)}")
    
    def load_recent_emails(self):
        """Load recent emails"""
        try:
            # Get recent emails from email handler
            account = self.db_manager.get_active_email_account()
            if not account:
                return
            
            emails = self.email_handler.get_recent_emails(account, limit=50)
            
            self.emails_table.setRowCount(len(emails))
            
            for row, email in enumerate(emails):
                # Time
                time_str = email.get('date', 'Unknown')
                if isinstance(time_str, str) and time_str != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        time_str = dt.strftime("%m/%d %H:%M")
                    except:
                        pass
                self.emails_table.setItem(row, 0, QTableWidgetItem(time_str))
                
                # From
                from_addr = email.get('from', 'Unknown')[:50]
                self.emails_table.setItem(row, 1, QTableWidgetItem(from_addr))
                
                # Subject
                subject = email.get('subject', 'No Subject')[:60]
                self.emails_table.setItem(row, 2, QTableWidgetItem(subject))
                
                # Auto-reply status
                auto_reply = email.get('auto_reply_sent', False)
                reply_item = QTableWidgetItem("✅" if auto_reply else "❌")
                reply_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.emails_table.setItem(row, 3, reply_item)
                
                # Status
                status = email.get('status', 'received')
                status_item = QTableWidgetItem(status.title())
                if status == 'processed':
                    status_item.setBackground(QColor(39, 174, 96, 50))
                elif status == 'error':
                    status_item.setBackground(QColor(231, 76, 60, 50))
                self.emails_table.setItem(row, 4, status_item)
                
                # Store email data
                self.emails_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, email)
            
        except Exception as e:
            self.logger.error(f"Error loading recent emails: {e}")
    
    def show_email_preview(self):
        """Show preview of selected email"""
        try:
            current_row = self.emails_table.currentRow()
            if current_row < 0:
                self.email_preview.clear()
                return
            
            email_data = self.emails_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            if not email_data:
                return
            
            preview_text = f"From: {email_data.get('from', 'Unknown')}\n"
            preview_text += f"Subject: {email_data.get('subject', 'No Subject')}\n"
            preview_text += f"Date: {email_data.get('date', 'Unknown')}\n\n"
            preview_text += email_data.get('body', 'No content')[:500]
            
            if len(email_data.get('body', '')) > 500:
                preview_text += "\n\n[Content truncated...]"
            
            self.email_preview.setPlainText(preview_text)
            
        except Exception as e:
            self.logger.error(f"Error showing email preview: {e}")
    
    def add_rule(self):
        """Add new auto-reply rule"""
        dialog = AutoReplyRuleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                rule_data = dialog.get_rule_data()
                self.db_manager.add_auto_reply_rule(
                    rule_data['name'],
                    rule_data['keywords'],
                    rule_data['template_id'],
                    rule_data['priority'],
                    rule_data['is_active'],
                    json.dumps({
                        'match_type': rule_data['match_type'],
                        'case_sensitive': rule_data['case_sensitive']
                    })
                )
                
                self.load_rules()
                self.rule_updated.emit()
                QMessageBox.information(self, "Success", "Auto-reply rule added successfully!")
                
            except Exception as e:
                self.logger.error(f"Error adding rule: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add rule: {str(e)}")
    
    def edit_rule(self):
        """Edit selected auto-reply rule"""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a rule to edit.")
            return
        
        try:
            rule_id = self.rules_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            rule = self.db_manager.get_auto_reply_rule(rule_id)
            
            if not rule:
                QMessageBox.warning(self, "Error", "Rule not found.")
                return
            
            dialog = AutoReplyRuleDialog(self, rule)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                rule_data = dialog.get_rule_data()
                self.db_manager.update_auto_reply_rule(
                    rule_id,
                    rule_data['name'],
                    rule_data['keywords'],
                    rule_data['template_id'],
                    rule_data['priority'],
                    rule_data['is_active'],
                    json.dumps({
                        'match_type': rule_data['match_type'],
                        'case_sensitive': rule_data['case_sensitive']
                    })
                )
                
                self.load_rules()
                self.rule_updated.emit()
                QMessageBox.information(self, "Success", "Auto-reply rule updated successfully!")
                
        except Exception as e:
            self.logger.error(f"Error editing rule: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit rule: {str(e)}")
    
    def delete_rule(self):
        """Delete selected auto-reply rule"""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a rule to delete.")
            return
        
        rule_name = self.rules_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the rule '{rule_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                rule_id = self.rules_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
                self.db_manager.delete_auto_reply_rule(rule_id)
                
                self.load_rules()
                self.rule_updated.emit()
                QMessageBox.information(self, "Success", "Auto-reply rule deleted successfully!")
                
            except Exception as e:
                self.logger.error(f"Error deleting rule: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete rule: {str(e)}")
    
    def toggle_monitoring(self):
        """Toggle inbox monitoring"""
        try:
            account = self.db_manager.get_active_email_account()
            if not account:
                QMessageBox.warning(self, "Error", "No email account configured.")
                return
            
            if hasattr(self.email_handler, 'monitoring') and self.email_handler.monitoring:
                self.email_handler.stop_inbox_monitoring()
                self.status_label.setText("📴 Monitoring: Stopped")
                self.toggle_monitor_btn.setText("▶️ Start Monitoring")
            else:
                self.email_handler.start_inbox_monitoring(account)
                self.status_label.setText("📡 Monitoring: Running")
                self.toggle_monitor_btn.setText("⏸️ Stop Monitoring")
            
        except Exception as e:
            self.logger.error(f"Error toggling monitoring: {e}")
            QMessageBox.critical(self, "Error", f"Failed to toggle monitoring: {str(e)}")
    
    def refresh_data(self):
        """Refresh all data"""
        self.load_rules()
        self.load_recent_emails()
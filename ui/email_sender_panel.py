from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QFileDialog, QMessageBox, QProgressBar, QSplitter,
    QFormLayout, QFrame, QTabWidget, QScrollArea, QDialog,
    QDialogButtonBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from datetime import datetime
import logging
import csv
import os
import json
import re

class ContactImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contacts = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Import Contacts")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Import contacts from CSV file. The file should contain columns for:\n"
            "• Email (required)\n"
            "• Name (optional)\n"
            "• Any additional fields for personalization"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #e8f4fd; padding: 10px; border-radius: 4px;")
        layout.addWidget(instructions)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select CSV file...")
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        
        # Preview table
        preview_label = QLabel("Preview:")
        preview_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        layout.addWidget(preview_label)
        
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(200)
        layout.addWidget(self.preview_table)
        
        # Column mapping
        mapping_group = QGroupBox("Column Mapping")
        mapping_layout = QFormLayout(mapping_group)
        
        self.email_column_combo = QComboBox()
        mapping_layout.addRow("Email Column:", self.email_column_combo)
        
        self.name_column_combo = QComboBox()
        mapping_layout.addRow("Name Column:", self.name_column_combo)
        
        layout.addWidget(mapping_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.import_contacts)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def browse_file(self):
        """Browse for CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self.load_preview(file_path)
    
    def load_preview(self, file_path):
        """Load CSV preview"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                rows = list(reader)
                
                if not rows:
                    QMessageBox.warning(self, "Error", "CSV file is empty.")
                    return
                
                # Setup preview table
                headers = rows[0]
                self.preview_table.setColumnCount(len(headers))
                self.preview_table.setHorizontalHeaderLabels(headers)
                
                # Show first 5 rows
                preview_rows = rows[1:6] if len(rows) > 1 else []
                self.preview_table.setRowCount(len(preview_rows))
                
                for row_idx, row in enumerate(preview_rows):
                    for col_idx, cell in enumerate(row):
                        if col_idx < len(headers):
                            self.preview_table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell)))
                
                # Update column combos
                self.email_column_combo.clear()
                self.name_column_combo.clear()
                
                self.email_column_combo.addItem("Select column...", -1)
                self.name_column_combo.addItem("Select column...", -1)
                
                for idx, header in enumerate(headers):
                    self.email_column_combo.addItem(header, idx)
                    self.name_column_combo.addItem(header, idx)
                
                # Auto-detect email column
                for idx, header in enumerate(headers):
                    if 'email' in header.lower() or 'mail' in header.lower():
                        self.email_column_combo.setCurrentIndex(idx + 1)
                        break
                
                # Auto-detect name column
                for idx, header in enumerate(headers):
                    if 'name' in header.lower() or 'first' in header.lower():
                        self.name_column_combo.setCurrentIndex(idx + 1)
                        break
                
                # Store data for import
                self.csv_data = rows
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")
    
    def import_contacts(self):
        """Import contacts from CSV"""
        try:
            if not hasattr(self, 'csv_data'):
                QMessageBox.warning(self, "Error", "Please select a CSV file first.")
                return
            
            email_col = self.email_column_combo.currentData()
            name_col = self.name_column_combo.currentData()
            
            if email_col == -1:
                QMessageBox.warning(self, "Error", "Please select the email column.")
                return
            
            headers = self.csv_data[0]
            data_rows = self.csv_data[1:]
            
            self.contacts = []
            
            for row in data_rows:
                if len(row) > email_col and row[email_col].strip():
                    contact = {
                        'email': row[email_col].strip(),
                        'name': row[name_col].strip() if name_col != -1 and len(row) > name_col else '',
                    }
                    
                    # Add all columns as custom fields
                    for idx, header in enumerate(headers):
                        if idx < len(row) and row[idx].strip():
                            contact[header.lower().replace(' ', '_')] = row[idx].strip()
                    
                    self.contacts.append(contact)
            
            if not self.contacts:
                QMessageBox.warning(self, "Error", "No valid contacts found in the CSV file.")
                return
            
            QMessageBox.information(
                self, "Success", 
                f"Successfully imported {len(self.contacts)} contacts."
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import contacts: {str(e)}")

class EmailSendThread(QThread):
    progress_updated = pyqtSignal(int, int, str)  # current, total, status
    email_sent = pyqtSignal(dict)  # email info
    finished_sending = pyqtSignal(int, int)  # sent, failed
    
    def __init__(self, email_handler, db_manager, email_data, contacts):
        super().__init__()
        self.email_handler = email_handler
        self.db_manager = db_manager
        self.email_data = email_data
        self.contacts = contacts
        self.should_stop = False
    
    def stop(self):
        self.should_stop = True
    
    def run(self):
        sent_count = 0
        failed_count = 0
        total = len(self.contacts)
        
        account = self.db_manager.get_active_email_account()
        if not account:
            self.progress_updated.emit(0, total, "No email account configured")
            return
        
        for i, contact in enumerate(self.contacts):
            if self.should_stop:
                break
            
            try:
                # Personalize email
                subject = self.personalize_text(self.email_data['subject'], contact)
                body = self.personalize_text(self.email_data['body'], contact)
                
                # Send email
                success, message = self.email_handler.send_email(
                    account,
                    contact['email'],
                    subject,
                    body,
                    self.email_data.get('attachments', []),
                    self.email_data.get('is_html', False)
                )
                
                if success:
                    sent_count += 1
                    status = "Sent"
                else:
                    failed_count += 1
                    status = f"Failed: {message}"
                
                # Emit progress
                self.progress_updated.emit(i + 1, total, f"Processing {contact['email']}...")
                
                # Emit email info
                self.email_sent.emit({
                    'email': contact['email'],
                    'name': contact.get('name', ''),
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Small delay to prevent overwhelming the server
                self.msleep(100)
                
            except Exception as e:
                failed_count += 1
                self.email_sent.emit({
                    'email': contact['email'],
                    'name': contact.get('name', ''),
                    'status': f"Error: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                })
        
        self.finished_sending.emit(sent_count, failed_count)
    
    def personalize_text(self, text, contact):
        """Replace placeholders with contact data"""
        if not text:
            return text
        
        # Replace common placeholders
        for key, value in contact.items():
            placeholder = f"{{{key}}}"
            text = text.replace(placeholder, str(value))
        
        return text

class EmailSenderPanel(QWidget):
    def __init__(self, db_manager, email_handler):
        super().__init__()
        self.db_manager = db_manager
        self.email_handler = email_handler
        self.logger = logging.getLogger(__name__)
        
        self.contacts = []
        self.send_thread = None
        
        self.init_ui()
        self.load_templates()
    
    def init_ui(self):
        """Initialize the email sender UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("📤 Email Sender")
        title_label.setObjectName("panelTitle")
        layout.addWidget(title_label)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Compose tab
        self.create_compose_tab(tab_widget)
        
        # Recipients tab
        self.create_recipients_tab(tab_widget)
        
        # Send tab
        self.create_send_tab(tab_widget)
        
        # Apply styles
        self.apply_styles()
    
    def create_compose_tab(self, parent):
        """Create email composition tab"""
        compose_widget = QWidget()
        layout = QVBoxLayout(compose_widget)
        
        # Template selection
        template_group = QGroupBox("Template")
        template_layout = QHBoxLayout(template_group)
        
        template_layout.addWidget(QLabel("Use Template:"))
        
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self.load_template)
        template_layout.addWidget(self.template_combo)
        
        template_layout.addStretch()
        
        new_template_btn = QPushButton("📝 New Template")
        new_template_btn.setObjectName("secondaryButton")
        new_template_btn.clicked.connect(self.create_new_template)
        template_layout.addWidget(new_template_btn)
        
        layout.addWidget(template_group)
        
        # Email composition
        compose_group = QGroupBox("Compose Email")
        compose_layout = QFormLayout(compose_group)
        
        # Subject
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Enter email subject...")
        compose_layout.addRow("Subject:", self.subject_edit)
        
        # Body
        body_layout = QVBoxLayout()
        
        # Format options
        format_layout = QHBoxLayout()
        
        self.html_checkbox = QCheckBox("HTML Format")
        self.html_checkbox.toggled.connect(self.toggle_html_format)
        format_layout.addWidget(self.html_checkbox)
        
        format_layout.addStretch()
        
        # Personalization help
        help_btn = QPushButton("❓ Personalization Help")
        help_btn.setObjectName("helpButton")
        help_btn.clicked.connect(self.show_personalization_help)
        format_layout.addWidget(help_btn)
        
        body_layout.addLayout(format_layout)
        
        self.body_edit = QTextEdit()
        self.body_edit.setPlaceholderText(
            "Enter email body...\n\n"
            "Use placeholders for personalization:\n"
            "{name} - Recipient's name\n"
            "{email} - Recipient's email\n"
            "{custom_field} - Any custom field from CSV"
        )
        self.body_edit.setMinimumHeight(200)
        body_layout.addWidget(self.body_edit)
        
        compose_layout.addRow("Body:", body_layout)
        
        # Attachments
        attachments_layout = QHBoxLayout()
        
        self.attachments_list = QListWidget()
        self.attachments_list.setMaximumHeight(80)
        attachments_layout.addWidget(self.attachments_list)
        
        attachments_buttons = QVBoxLayout()
        
        add_attachment_btn = QPushButton("📎 Add")
        add_attachment_btn.setObjectName("secondaryButton")
        add_attachment_btn.clicked.connect(self.add_attachment)
        attachments_buttons.addWidget(add_attachment_btn)
        
        remove_attachment_btn = QPushButton("🗑️ Remove")
        remove_attachment_btn.setObjectName("dangerButton")
        remove_attachment_btn.clicked.connect(self.remove_attachment)
        attachments_buttons.addWidget(remove_attachment_btn)
        
        attachments_buttons.addStretch()
        attachments_layout.addLayout(attachments_buttons)
        
        compose_layout.addRow("Attachments:", attachments_layout)
        
        layout.addWidget(compose_group)
        
        parent.addTab(compose_widget, "📝 Compose")
    
    def create_recipients_tab(self, parent):
        """Create recipients management tab"""
        recipients_widget = QWidget()
        layout = QVBoxLayout(recipients_widget)
        
        # Import options
        import_group = QGroupBox("Import Recipients")
        import_layout = QHBoxLayout(import_group)
        
        import_csv_btn = QPushButton("📁 Import from CSV")
        import_csv_btn.setObjectName("primaryButton")
        import_csv_btn.clicked.connect(self.import_contacts)
        import_layout.addWidget(import_csv_btn)
        
        import_db_btn = QPushButton("💾 Load from Database")
        import_db_btn.setObjectName("secondaryButton")
        import_db_btn.clicked.connect(self.load_contacts_from_db)
        import_layout.addWidget(import_db_btn)
        
        import_layout.addStretch()
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setObjectName("dangerButton")
        clear_btn.clicked.connect(self.clear_contacts)
        import_layout.addWidget(clear_btn)
        
        layout.addWidget(import_group)
        
        # Recipients table
        recipients_group = QGroupBox("Recipients")
        recipients_layout = QVBoxLayout(recipients_group)
        
        # Table header with count
        table_header = QHBoxLayout()
        
        self.recipients_count_label = QLabel("Recipients: 0")
        self.recipients_count_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        table_header.addWidget(self.recipients_count_label)
        
        table_header.addStretch()
        
        add_manual_btn = QPushButton("➕ Add Manually")
        add_manual_btn.setObjectName("secondaryButton")
        add_manual_btn.clicked.connect(self.add_manual_contact)
        table_header.addWidget(add_manual_btn)
        
        recipients_layout.addLayout(table_header)
        
        # Recipients table
        self.recipients_table = QTableWidget()
        self.recipients_table.setColumnCount(3)
        self.recipients_table.setHorizontalHeaderLabels(["Email", "Name", "Custom Fields"])
        
        # Configure table
        header = self.recipients_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.recipients_table.setAlternatingRowColors(True)
        self.recipients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        recipients_layout.addWidget(self.recipients_table)
        
        layout.addWidget(recipients_group)
        
        parent.addTab(recipients_widget, "👥 Recipients")
    
    def create_send_tab(self, parent):
        """Create email sending tab"""
        send_widget = QWidget()
        layout = QVBoxLayout(send_widget)
        
        # Send options
        options_group = QGroupBox("Send Options")
        options_layout = QFormLayout(options_group)
        
        # Delay between emails
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(1)
        self.delay_spin.setSuffix(" seconds")
        options_layout.addRow("Delay between emails:", self.delay_spin)
        
        # Test mode
        self.test_mode_check = QCheckBox("Test mode (send to yourself only)")
        options_layout.addRow("", self.test_mode_check)
        
        layout.addWidget(options_group)
        
        # Send controls
        controls_group = QGroupBox("Send Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Send button
        send_layout = QHBoxLayout()
        
        self.send_btn = QPushButton("🚀 Send Emails")
        self.send_btn.setObjectName("primaryButton")
        self.send_btn.clicked.connect(self.send_emails)
        send_layout.addWidget(self.send_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.clicked.connect(self.stop_sending)
        self.stop_btn.setEnabled(False)
        send_layout.addWidget(self.stop_btn)
        
        send_layout.addStretch()
        
        controls_layout.addLayout(send_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        controls_layout.addWidget(self.progress_label)
        
        layout.addWidget(controls_group)
        
        # Send results
        results_group = QGroupBox("Send Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Email", "Name", "Status", "Time"])
        
        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.results_table.setAlternatingRowColors(True)
        
        results_layout.addWidget(self.results_table)
        
        layout.addWidget(results_group)
        
        parent.addTab(send_widget, "🚀 Send")
    
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
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            margin: 2px;
        }
        
        #primaryButton:hover {
            background-color: #fb8500;
        }
        
        #primaryButton:disabled {
            background-color: #8ecae6;
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
        
        #helpButton {
            background-color: #ffb703;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        #helpButton:hover {
            background-color: #fb8500;
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
        }
        
        QTabBar::tab:selected {
            background-color: #8ecae6;
            border-bottom-color: #8ecae6;
            color: #023047;
        }
        
        QTabBar::tab:hover {
            background-color: #219ebc;
        }
        """
        
        self.setStyleSheet(style)
    
    def load_templates(self):
        """Load email templates"""
        try:
            templates = self.db_manager.get_email_templates()
            
            self.template_combo.clear()
            self.template_combo.addItem("Select template...", None)
            
            for template in templates:
                self.template_combo.addItem(template['name'], template['id'])
                
        except Exception as e:
            self.logger.error(f"Error loading templates: {e}")
    
    def load_template(self):
        """Load selected template"""
        try:
            template_id = self.template_combo.currentData()
            if not template_id:
                return
            
            template = self.db_manager.get_email_template(template_id)
            if template:
                self.subject_edit.setText(template['subject'])
                self.body_edit.setPlainText(template['body'])
                self.html_checkbox.setChecked(template.get('is_html', False))
                
        except Exception as e:
            self.logger.error(f"Error loading template: {e}")
    
    def create_new_template(self):
        """Create new template from current content"""
        # Switch to templates panel
        parent = self.parent()
        while parent and not hasattr(parent, 'nav_list'):
            parent = parent.parent()
        if parent:
            parent.nav_list.setCurrentRow(4)  # Templates panel
    
    def toggle_html_format(self, checked):
        """Toggle HTML format"""
        if checked:
            # Convert plain text to HTML if needed
            current_text = self.body_edit.toPlainText()
            if current_text and not current_text.strip().startswith('<'):
                html_text = current_text.replace('\n', '<br>\n')
                self.body_edit.setHtml(html_text)
        else:
            # Convert to plain text
            self.body_edit.setPlainText(self.body_edit.toPlainText())
    
    def show_personalization_help(self):
        """Show personalization help dialog"""
        help_text = """
        <h3>Email Personalization</h3>
        <p>Use placeholders in your email subject and body to personalize emails for each recipient:</p>
        
        <h4>Common Placeholders:</h4>
        <ul>
        <li><b>{name}</b> - Recipient's name</li>
        <li><b>{email}</b> - Recipient's email address</li>
        <li><b>{first_name}</b> - First name (if available)</li>
        <li><b>{last_name}</b> - Last name (if available)</li>
        </ul>
        
        <h4>Custom Fields:</h4>
        <p>Any column from your CSV file can be used as a placeholder:</p>
        <ul>
        <li><b>{company}</b> - Company name</li>
        <li><b>{position}</b> - Job position</li>
        <li><b>{phone}</b> - Phone number</li>
        <li><b>{custom_field}</b> - Any custom field</li>
        </ul>
        
        <h4>Example:</h4>
        <p><i>Subject:</i> Hello {name}, special offer for {company}</p>
        <p><i>Body:</i> Dear {name},<br><br>
        We have a special offer for {company}. As a {position}, you might be interested...
        </p>
        
        <p><b>Note:</b> Placeholders are case-sensitive and must match your CSV column headers exactly.</p>
        """
        
        QMessageBox.information(self, "Personalization Help", help_text)
    
    def add_attachment(self):
        """Add email attachment"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Attachments", "", "All Files (*)"
        )
        
        for file_path in file_paths:
            if file_path:
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.attachments_list.addItem(item)
    
    def remove_attachment(self):
        """Remove selected attachment"""
        current_item = self.attachments_list.currentItem()
        if current_item:
            row = self.attachments_list.row(current_item)
            self.attachments_list.takeItem(row)
    
    def import_contacts(self):
        """Import contacts from CSV"""
        dialog = ContactImportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.contacts.extend(dialog.contacts)
            self.update_recipients_table()
            
            # Save contacts to database
            try:
                for contact in dialog.contacts:
                    self.db_manager.add_contact(
                        contact['email'],
                        contact.get('name', ''),
                        json.dumps({k: v for k, v in contact.items() if k not in ['email', 'name']})
                    )
            except Exception as e:
                self.logger.error(f"Error saving contacts: {e}")
    
    def load_contacts_from_db(self):
        """Load contacts from database"""
        try:
            db_contacts = self.db_manager.get_contacts()
            
            for contact in db_contacts:
                contact_data = {
                    'email': contact['email'],
                    'name': contact['name']
                }
                
                # Add custom fields
                if contact['custom_fields']:
                    try:
                        custom_fields = json.loads(contact['custom_fields'])
                        contact_data.update(custom_fields)
                    except:
                        pass
                
                self.contacts.append(contact_data)
            
            self.update_recipients_table()
            
            QMessageBox.information(
                self, "Success", 
                f"Loaded {len(db_contacts)} contacts from database."
            )
            
        except Exception as e:
            self.logger.error(f"Error loading contacts from database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load contacts: {str(e)}")
    
    def add_manual_contact(self):
        """Add contact manually"""
        from PyQt6.QtWidgets import QInputDialog
        
        email, ok = QInputDialog.getText(self, "Add Contact", "Email address:")
        if ok and email.strip():
            name, ok = QInputDialog.getText(self, "Add Contact", "Name (optional):")
            if ok:
                contact = {
                    'email': email.strip(),
                    'name': name.strip() if name else ''
                }
                
                self.contacts.append(contact)
                self.update_recipients_table()
    
    def clear_contacts(self):
        """Clear all contacts"""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear all recipients?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.contacts.clear()
            self.update_recipients_table()
    
    def update_recipients_table(self):
        """Update recipients table"""
        self.recipients_table.setRowCount(len(self.contacts))
        self.recipients_count_label.setText(f"Recipients: {len(self.contacts)}")
        
        for row, contact in enumerate(self.contacts):
            # Email
            self.recipients_table.setItem(row, 0, QTableWidgetItem(contact['email']))
            
            # Name
            self.recipients_table.setItem(row, 1, QTableWidgetItem(contact.get('name', '')))
            
            # Custom fields
            custom_fields = [f"{k}: {v}" for k, v in contact.items() 
                           if k not in ['email', 'name'] and v]
            custom_text = ", ".join(custom_fields[:3])  # Show first 3 fields
            if len(custom_fields) > 3:
                custom_text += "..."
            self.recipients_table.setItem(row, 2, QTableWidgetItem(custom_text))
    
    def send_emails(self):
        """Send emails to all recipients"""
        if not self.contacts:
            QMessageBox.warning(self, "Warning", "No recipients added.")
            return
        
        if not self.subject_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter email subject.")
            return
        
        if not self.body_edit.toPlainText().strip():
            QMessageBox.warning(self, "Warning", "Please enter email body.")
            return
        
        # Prepare email data
        email_data = {
            'subject': self.subject_edit.text().strip(),
            'body': self.body_edit.toHtml() if self.html_checkbox.isChecked() else self.body_edit.toPlainText(),
            'is_html': self.html_checkbox.isChecked(),
            'attachments': []
        }
        
        # Get attachments
        for i in range(self.attachments_list.count()):
            item = self.attachments_list.item(i)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            email_data['attachments'].append(file_path)
        
        # Test mode check
        contacts = self.contacts.copy()
        if self.test_mode_check.isChecked():
            account = self.db_manager.get_active_email_account()
            if account:
                contacts = [{'email': account['email'], 'name': 'Test User'}]
            else:
                QMessageBox.warning(self, "Error", "No email account configured for test mode.")
                return
        
        # Confirm sending
        reply = QMessageBox.question(
            self, "Confirm Send",
            f"Send email to {len(contacts)} recipient(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.start_sending(email_data, contacts)
    
    def start_sending(self, email_data, contacts):
        """Start email sending thread"""
        # Setup UI for sending
        self.send_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setMaximum(len(contacts))
        self.progress_bar.setValue(0)
        
        # Clear results table
        self.results_table.setRowCount(0)
        
        # Start sending thread
        self.send_thread = EmailSendThread(
            self.email_handler, self.db_manager, email_data, contacts
        )
        
        self.send_thread.progress_updated.connect(self.update_progress)
        self.send_thread.email_sent.connect(self.add_result)
        self.send_thread.finished_sending.connect(self.sending_finished)
        
        self.send_thread.start()
    
    def stop_sending(self):
        """Stop email sending"""
        if self.send_thread:
            self.send_thread.stop()
            self.stop_btn.setEnabled(False)
    
    def update_progress(self, current, total, status):
        """Update sending progress"""
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"{status} ({current}/{total})")
    
    def add_result(self, email_info):
        """Add email result to table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Email
        self.results_table.setItem(row, 0, QTableWidgetItem(email_info['email']))
        
        # Name
        self.results_table.setItem(row, 1, QTableWidgetItem(email_info['name']))
        
        # Status
        status_item = QTableWidgetItem(email_info['status'])
        if 'Sent' in email_info['status']:
            status_item.setBackground(QColor(39, 174, 96, 50))
        else:
            status_item.setBackground(QColor(231, 76, 60, 50))
        self.results_table.setItem(row, 2, status_item)
        
        # Time
        timestamp = datetime.fromisoformat(email_info['timestamp'])
        time_str = timestamp.strftime("%H:%M:%S")
        self.results_table.setItem(row, 3, QTableWidgetItem(time_str))
        
        # Scroll to bottom
        self.results_table.scrollToBottom()
    
    def sending_finished(self, sent_count, failed_count):
        """Handle sending completion"""
        # Reset UI
        self.send_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Show summary
        QMessageBox.information(
            self, "Sending Complete",
            f"Email sending completed!\n\n"
            f"Sent: {sent_count}\n"
            f"Failed: {failed_count}\n"
            f"Total: {sent_count + failed_count}"
        )
        
        self.send_thread = None
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QMessageBox,
    QSplitter, QFrame, QTabWidget, QScrollArea, QListWidget,
    QListWidgetItem, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextDocument
from PyQt6.QtWebEngineWidgets import QWebEngineView
import logging
import html
import re

class TemplateDialog(QDialog):
    def __init__(self, parent=None, template=None):
        super().__init__(parent)
        self.template = template
        self.db_manager = parent.db_manager
        self.init_ui()
        
        if template:
            self.load_template_data()
    
    def init_ui(self):
        self.setWindowTitle("Email Template")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Basic info tab
        self.create_basic_tab(tab_widget)
        
        # Content tab
        self.create_content_tab(tab_widget)
        
        # Preview tab
        self.create_preview_tab(tab_widget)
        
        # Variables tab
        self.create_variables_tab(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals for live preview
        self.subject_edit.textChanged.connect(self.update_preview)
        self.body_edit.textChanged.connect(self.update_preview)
        self.html_check.toggled.connect(self.toggle_html_mode)
        self.html_check.toggled.connect(self.update_preview)
    
    def create_basic_tab(self, parent):
        """Create basic information tab"""
        basic_widget = QWidget()
        layout = QFormLayout(basic_widget)
        
        # Template name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter template name")
        layout.addRow("Template Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter description (optional)")
        self.description_edit.setMaximumHeight(80)
        layout.addRow("Description:", self.description_edit)
        
        # Category
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("e.g., Marketing, Newsletter, Auto-reply")
        layout.addRow("Category:", self.category_edit)
        
        # Subject
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Enter email subject")
        layout.addRow("Subject:", self.subject_edit)
        
        # HTML mode
        self.html_check = QCheckBox("HTML Template")
        self.html_check.setToolTip("Enable HTML formatting for rich content")
        layout.addRow("", self.html_check)
        
        parent.addTab(basic_widget, "📝 Basic Info")
    
    def create_content_tab(self, parent):
        """Create content editing tab"""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Content header
        header_layout = QHBoxLayout()
        
        content_label = QLabel("Email Body:")
        content_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        header_layout.addWidget(content_label)
        
        header_layout.addStretch()
        
        # HTML tools (shown when HTML mode is enabled)
        self.html_tools_widget = QWidget()
        html_tools_layout = QHBoxLayout(self.html_tools_widget)
        html_tools_layout.setContentsMargins(0, 0, 0, 0)
        
        bold_btn = QPushButton("B")
        bold_btn.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        bold_btn.setMaximumWidth(30)
        bold_btn.clicked.connect(lambda: self.insert_html_tag('b'))
        html_tools_layout.addWidget(bold_btn)
        
        italic_btn = QPushButton("I")
        italic_btn.setFont(QFont('Arial', 10, QFont.Weight.Normal))
        italic_btn.setStyleSheet("font-style: italic;")
        italic_btn.setMaximumWidth(30)
        italic_btn.clicked.connect(lambda: self.insert_html_tag('i'))
        html_tools_layout.addWidget(italic_btn)
        
        link_btn = QPushButton("🔗")
        link_btn.setMaximumWidth(30)
        link_btn.clicked.connect(self.insert_link)
        html_tools_layout.addWidget(link_btn)
        
        header_layout.addWidget(self.html_tools_widget)
        self.html_tools_widget.setVisible(False)
        
        layout.addLayout(header_layout)
        
        # Body editor
        self.body_edit = QPlainTextEdit()
        self.body_edit.setPlaceholderText(
            "Enter your email content here...\n\n"
            "You can use variables like:\n"
            "{name} - Recipient's name\n"
            "{email} - Recipient's email\n"
            "{company} - Company name\n"
            "\nFor HTML templates, you can use HTML tags for formatting."
        )
        layout.addWidget(self.body_edit)
        
        # Quick insert buttons
        quick_insert_layout = QHBoxLayout()
        
        quick_insert_label = QLabel("Quick Insert:")
        quick_insert_layout.addWidget(quick_insert_label)
        
        variables = [
            ("{name}", "Name"),
            ("{email}", "Email"),
            ("{company}", "Company"),
            ("{date}", "Date"),
            ("{time}", "Time")
        ]
        
        for var_code, var_name in variables:
            var_btn = QPushButton(var_name)
            var_btn.setObjectName("variableButton")
            var_btn.clicked.connect(lambda checked, code=var_code: self.insert_variable(code))
            quick_insert_layout.addWidget(var_btn)
        
        quick_insert_layout.addStretch()
        layout.addLayout(quick_insert_layout)
        
        parent.addTab(content_widget, "✏️ Content")
    
    def create_preview_tab(self, parent):
        """Create preview tab"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)
        
        # Preview header
        preview_header = QHBoxLayout()
        
        preview_label = QLabel("Template Preview:")
        preview_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        preview_header.addWidget(preview_label)
        
        preview_header.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.update_preview)
        preview_header.addWidget(refresh_btn)
        
        layout.addLayout(preview_header)
        
        # Preview content
        preview_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Subject preview
        subject_group = QGroupBox("Subject")
        subject_layout = QVBoxLayout(subject_group)
        
        self.subject_preview = QLabel()
        self.subject_preview.setWordWrap(True)
        self.subject_preview.setStyleSheet(
            "background-color: #f8f9fa; border: 1px solid #dee2e6; "
            "padding: 10px; border-radius: 4px; font-weight: bold;"
        )
        subject_layout.addWidget(self.subject_preview)
        
        preview_splitter.addWidget(subject_group)
        
        # Body preview
        body_group = QGroupBox("Body")
        body_layout = QVBoxLayout(body_group)
        
        # Create both plain text and HTML preview widgets
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setStyleSheet(
            "background-color: #f8f9fa; border: 1px solid #dee2e6; "
            "padding: 10px; border-radius: 4px;"
        )
        
        try:
            self.html_preview = QWebEngineView()
        except ImportError:
            # Fallback if QWebEngineView is not available
            self.html_preview = QTextEdit()
            self.html_preview.setReadOnly(True)
            self.html_preview.setStyleSheet(
                "background-color: #f8f9fa; border: 1px solid #dee2e6; "
                "padding: 10px; border-radius: 4px;"
            )
        
        body_layout.addWidget(self.text_preview)
        body_layout.addWidget(self.html_preview)
        
        preview_splitter.addWidget(body_group)
        
        layout.addWidget(preview_splitter)
        
        # Set initial visibility
        self.html_preview.setVisible(False)
        
        parent.addTab(preview_widget, "👁️ Preview")
    
    def create_variables_tab(self, parent):
        """Create variables reference tab"""
        variables_widget = QWidget()
        layout = QVBoxLayout(variables_widget)
        
        # Variables info
        info_label = QLabel(
            "Available Variables:\n\n"
            "You can use these variables in your templates. They will be replaced "
            "with actual values when sending emails."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #6c757d; margin-bottom: 15px;")
        layout.addWidget(info_label)
        
        # Variables table
        variables_table = QTableWidget()
        variables_table.setColumnCount(3)
        variables_table.setHorizontalHeaderLabels(["Variable", "Description", "Example"])
        
        # Define available variables
        variables_data = [
            ("{name}", "Recipient's full name", "John Doe"),
            ("{first_name}", "Recipient's first name", "John"),
            ("{last_name}", "Recipient's last name", "Doe"),
            ("{email}", "Recipient's email address", "john@example.com"),
            ("{company}", "Recipient's company", "Acme Corp"),
            ("{date}", "Current date", "2024-01-15"),
            ("{time}", "Current time", "14:30"),
            ("{datetime}", "Current date and time", "2024-01-15 14:30"),
            ("{sender_name}", "Sender's name", "Your Name"),
            ("{sender_email}", "Sender's email", "you@company.com")
        ]
        
        variables_table.setRowCount(len(variables_data))
        
        for row, (variable, description, example) in enumerate(variables_data):
            # Variable
            var_item = QTableWidgetItem(variable)
            var_item.setFont(QFont('Courier', 10, QFont.Weight.Bold))
            var_item.setBackground(QColor(248, 249, 250))
            variables_table.setItem(row, 0, var_item)
            
            # Description
            variables_table.setItem(row, 1, QTableWidgetItem(description))
            
            # Example
            example_item = QTableWidgetItem(example)
            example_item.setFont(QFont('Arial', 9))
            example_item.setForeground(QColor(108, 117, 125))
            variables_table.setItem(row, 2, example_item)
        
        # Configure table
        header = variables_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        variables_table.setAlternatingRowColors(True)
        variables_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        variables_table.verticalHeader().setVisible(False)
        
        layout.addWidget(variables_table)
        
        # HTML tips
        html_tips_group = QGroupBox("HTML Tips")
        html_tips_layout = QVBoxLayout(html_tips_group)
        
        html_tips = QLabel(
            "For HTML templates, you can use:\n\n"
            "• <b>Bold text</b> or <strong>Strong text</strong>\n"
            "• <i>Italic text</i> or <em>Emphasized text</em>\n"
            "• <a href='https://example.com'>Links</a>\n"
            "• <br> for line breaks\n"
            "• <p>Paragraphs</p>\n"
            "• <ul><li>Bullet lists</li></ul>\n"
            "• <h1>, <h2>, <h3> for headings\n"
            "• <img src='url' alt='description'> for images"
        )
        html_tips.setWordWrap(True)
        html_tips.setStyleSheet(
            "background-color: #e7f3ff; border: 1px solid #b3d9ff; "
            "padding: 15px; border-radius: 6px; font-family: monospace;"
        )
        html_tips_layout.addWidget(html_tips)
        
        layout.addWidget(html_tips_group)
        
        parent.addTab(variables_widget, "📋 Variables")
    
    def toggle_html_mode(self):
        """Toggle between HTML and plain text mode"""
        is_html = self.html_check.isChecked()
        
        # Show/hide HTML tools
        self.html_tools_widget.setVisible(is_html)
        
        # Update preview visibility
        self.text_preview.setVisible(not is_html)
        self.html_preview.setVisible(is_html)
        
        # Update placeholder text
        if is_html:
            self.body_edit.setPlaceholderText(
                "Enter your HTML email content here...\n\n"
                "You can use HTML tags for formatting:\n"
                "<b>Bold</b>, <i>Italic</i>, <a href='url'>Links</a>\n\n"
                "Variables like {name}, {email}, {company} are also supported."
            )
        else:
            self.body_edit.setPlaceholderText(
                "Enter your plain text email content here...\n\n"
                "You can use variables like:\n"
                "{name} - Recipient's name\n"
                "{email} - Recipient's email\n"
                "{company} - Company name"
            )
    
    def insert_html_tag(self, tag):
        """Insert HTML tag at cursor position"""
        cursor = self.body_edit.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            # Wrap selected text
            new_text = f"<{tag}>{selected_text}</{tag}>"
        else:
            # Insert empty tag
            new_text = f"<{tag}></{tag}>"
        
        cursor.insertText(new_text)
        
        # Position cursor between tags if no text was selected
        if not selected_text:
            position = cursor.position() - len(f"</{tag}>")
            cursor.setPosition(position)
            self.body_edit.setTextCursor(cursor)
    
    def insert_link(self):
        """Insert HTML link"""
        cursor = self.body_edit.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            link_text = f'<a href="https://example.com">{selected_text}</a>'
        else:
            link_text = '<a href="https://example.com">Link text</a>'
        
        cursor.insertText(link_text)
    
    def insert_variable(self, variable):
        """Insert variable at cursor position"""
        cursor = self.body_edit.textCursor()
        cursor.insertText(variable)
    
    def update_preview(self):
        """Update template preview"""
        # Update subject preview
        subject = self.subject_edit.text() or "(No subject)"
        # Replace variables with sample data for preview
        preview_subject = self.replace_variables_for_preview(subject)
        self.subject_preview.setText(preview_subject)
        
        # Update body preview
        body = self.body_edit.toPlainText() or "(No content)"
        preview_body = self.replace_variables_for_preview(body)
        
        if self.html_check.isChecked():
            # HTML preview
            try:
                if hasattr(self.html_preview, 'setHtml'):
                    # QWebEngineView
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                        </style>
                    </head>
                    <body>
                        {preview_body}
                    </body>
                    </html>
                    """
                    self.html_preview.setHtml(html_content)
                else:
                    # QTextEdit fallback
                    self.html_preview.setHtml(preview_body)
            except Exception as e:
                # Fallback to plain text if HTML rendering fails
                self.html_preview.setPlainText(preview_body)
        else:
            # Plain text preview
            self.text_preview.setPlainText(preview_body)
    
    def replace_variables_for_preview(self, text):
        """Replace variables with sample data for preview"""
        replacements = {
            '{name}': 'John Doe',
            '{first_name}': 'John',
            '{last_name}': 'Doe',
            '{email}': 'john.doe@example.com',
            '{company}': 'Acme Corporation',
            '{date}': '2024-01-15',
            '{time}': '14:30',
            '{datetime}': '2024-01-15 14:30',
            '{sender_name}': 'Your Name',
            '{sender_email}': 'you@company.com'
        }
        
        for variable, value in replacements.items():
            text = text.replace(variable, value)
        
        return text
    
    def load_template_data(self):
        """Load existing template data"""
        if not self.template:
            return
        
        self.name_edit.setText(self.template['name'])
        self.description_edit.setPlainText(self.template.get('description', ''))
        self.category_edit.setText(self.template.get('category', ''))
        self.subject_edit.setText(self.template['subject'])
        self.body_edit.setPlainText(self.template['body'])
        self.html_check.setChecked(self.template.get('is_html', False))
        
        # Update preview
        self.update_preview()
    
    def get_template_data(self):
        """Get template data from form"""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'category': self.category_edit.text().strip(),
            'subject': self.subject_edit.text().strip(),
            'body': self.body_edit.toPlainText(),
            'is_html': self.html_check.isChecked()
        }
    
    def validate_data(self):
        """Validate form data"""
        data = self.get_template_data()
        
        if not data['name']:
            QMessageBox.warning(self, "Validation Error", "Please enter a template name.")
            return False
        
        if not data['subject']:
            QMessageBox.warning(self, "Validation Error", "Please enter a subject.")
            return False
        
        if not data['body']:
            QMessageBox.warning(self, "Validation Error", "Please enter email body content.")
            return False
        
        return True
    
    def accept(self):
        if self.validate_data():
            super().accept()

class TemplatesPanel(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        self.load_templates()
    
    def init_ui(self):
        """Initialize the templates UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("📧 Email Templates")
        title_label.setObjectName("panelTitle")
        layout.addWidget(title_label)
        
        # Create splitter for two-panel layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Templates list
        self.create_templates_panel(splitter)
        
        # Right panel - Template preview
        self.create_preview_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([600, 400])
        
        # Apply styles
        self.apply_styles()
    
    def create_templates_panel(self, parent):
        """Create templates list panel"""
        templates_widget = QWidget()
        templates_layout = QVBoxLayout(templates_widget)
        
        # Templates header
        templates_header = QHBoxLayout()
        
        templates_title = QLabel("Email Templates")
        templates_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        templates_header.addWidget(templates_title)
        
        templates_header.addStretch()
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search templates...")
        self.search_edit.setMaximumWidth(200)
        self.search_edit.textChanged.connect(self.filter_templates)
        templates_header.addWidget(self.search_edit)
        
        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.setMaximumWidth(150)
        self.category_filter.currentTextChanged.connect(self.filter_templates)
        templates_header.addWidget(self.category_filter)
        
        templates_layout.addLayout(templates_header)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        add_template_btn = QPushButton("➕ New Template")
        add_template_btn.setObjectName("primaryButton")
        add_template_btn.clicked.connect(self.add_template)
        buttons_layout.addWidget(add_template_btn)
        
        edit_template_btn = QPushButton("✏️ Edit")
        edit_template_btn.setObjectName("secondaryButton")
        edit_template_btn.clicked.connect(self.edit_template)
        buttons_layout.addWidget(edit_template_btn)
        
        duplicate_template_btn = QPushButton("📋 Duplicate")
        duplicate_template_btn.setObjectName("secondaryButton")
        duplicate_template_btn.clicked.connect(self.duplicate_template)
        buttons_layout.addWidget(duplicate_template_btn)
        
        delete_template_btn = QPushButton("🗑️ Delete")
        delete_template_btn.setObjectName("dangerButton")
        delete_template_btn.clicked.connect(self.delete_template)
        buttons_layout.addWidget(delete_template_btn)
        
        buttons_layout.addStretch()
        templates_layout.addLayout(buttons_layout)
        
        # Templates table
        self.templates_table = QTableWidget()
        self.templates_table.setColumnCount(5)
        self.templates_table.setHorizontalHeaderLabels([
            "Name", "Category", "Subject", "Type", "Modified"
        ])
        
        # Configure table
        header = self.templates_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.templates_table.setAlternatingRowColors(True)
        self.templates_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.templates_table.itemSelectionChanged.connect(self.show_template_preview)
        self.templates_table.doubleClicked.connect(self.edit_template)
        
        templates_layout.addWidget(self.templates_table)
        
        # Templates stats
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QHBoxLayout(stats_frame)
        
        self.stats_label = QLabel("📊 0 templates")
        self.stats_label.setObjectName("statsLabel")
        stats_layout.addWidget(self.stats_label)
        
        stats_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.load_templates)
        stats_layout.addWidget(refresh_btn)
        
        templates_layout.addWidget(stats_frame)
        
        parent.addWidget(templates_widget)
    
    def create_preview_panel(self, parent):
        """Create template preview panel"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # Preview header
        preview_title = QLabel("Template Preview")
        preview_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        preview_layout.addWidget(preview_title)
        
        # Preview content
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.preview_content = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_content)
        self.preview_scroll.setWidget(self.preview_content)
        
        preview_layout.addWidget(self.preview_scroll)
        
        # Show empty state initially
        self.show_empty_preview()
        
        parent.addWidget(preview_widget)
    
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
        
        #variableButton {
            background-color: #ffb703;
            color: #023047;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 11px;
            margin: 1px;
        }
        
        #variableButton:hover {
            background-color: #fb8500;
            color: white;
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
        
        QLineEdit {
            border: 1px solid #219ebc;
            border-radius: 4px;
            padding: 8px;
            background-color: #023047;
            color: white;
        }
        
        QLineEdit:focus {
            border-color: #023047;
        }
        
        QComboBox {
            border: 1px solid #219ebc;
            border-radius: 4px;
            padding: 8px;
            background-color: #023047;
            color: white;
        }
        """
        
        self.setStyleSheet(style)
    
    def load_templates(self):
        """Load email templates"""
        try:
            templates = self.db_manager.get_email_templates()
            
            # Update category filter
            self.update_category_filter(templates)
            
            # Store all templates for filtering
            self.all_templates = templates
            
            # Display templates
            self.display_templates(templates)
            
            # Update stats
            self.update_stats(templates)
            
        except Exception as e:
            self.logger.error(f"Error loading templates: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load templates: {str(e)}")
    
    def update_category_filter(self, templates):
        """Update category filter dropdown"""
        current_category = self.category_filter.currentText()
        
        # Get unique categories
        categories = set()
        for template in templates:
            category = template.get('category', '').strip()
            if category:
                categories.add(category)
        
        # Update combo box
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        
        for category in sorted(categories):
            self.category_filter.addItem(category)
        
        # Restore selection if possible
        if current_category:
            index = self.category_filter.findText(current_category)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)
    
    def display_templates(self, templates):
        """Display templates in table"""
        self.templates_table.setRowCount(len(templates))
        
        for row, template in enumerate(templates):
            # Name
            self.templates_table.setItem(row, 0, QTableWidgetItem(template['name']))
            
            # Category
            category = template.get('category', '')
            self.templates_table.setItem(row, 1, QTableWidgetItem(category))
            
            # Subject
            subject = template['subject'][:50] + "..." if len(template['subject']) > 50 else template['subject']
            self.templates_table.setItem(row, 2, QTableWidgetItem(subject))
            
            # Type
            template_type = "HTML" if template.get('is_html', False) else "Text"
            type_item = QTableWidgetItem(template_type)
            if template.get('is_html', False):
                type_item.setBackground(QColor(52, 152, 219, 50))
            else:
                type_item.setBackground(QColor(149, 165, 166, 50))
            self.templates_table.setItem(row, 3, type_item)
            
            # Modified date
            modified = template.get('created_at', '')[:10]  # Just the date part
            self.templates_table.setItem(row, 4, QTableWidgetItem(modified))
            
            # Store template ID in first column
            self.templates_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, template['id'])
    
    def filter_templates(self):
        """Filter templates based on search and category"""
        if not hasattr(self, 'all_templates'):
            return
        
        search_text = self.search_edit.text().lower()
        selected_category = self.category_filter.currentText()
        
        filtered_templates = []
        
        for template in self.all_templates:
            # Category filter
            if selected_category != "All Categories":
                template_category = template.get('category', '').strip()
                if template_category != selected_category:
                    continue
            
            # Search filter
            if search_text:
                searchable_text = (
                    template['name'].lower() + " " +
                    template['subject'].lower() + " " +
                    template.get('category', '').lower() + " " +
                    template['body'].lower()
                )
                
                if search_text not in searchable_text:
                    continue
            
            filtered_templates.append(template)
        
        self.display_templates(filtered_templates)
        self.update_stats(filtered_templates)
    
    def update_stats(self, templates):
        """Update templates statistics"""
        total_count = len(templates)
        html_count = sum(1 for t in templates if t.get('is_html', False))
        text_count = total_count - html_count
        
        stats_text = f"📊 {total_count} templates ({html_count} HTML, {text_count} Text)"
        self.stats_label.setText(stats_text)
    
    def show_template_preview(self):
        """Show preview of selected template"""
        current_row = self.templates_table.currentRow()
        if current_row < 0:
            self.show_empty_preview()
            return
        
        try:
            template_id = self.templates_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            template = self.db_manager.get_email_template(template_id)
            
            if not template:
                self.show_empty_preview()
                return
            
            # Clear existing content
            for i in reversed(range(self.preview_layout.count())):
                child = self.preview_layout.takeAt(i)
                if child.widget():
                    child.widget().deleteLater()
            
            # Template info
            info_group = QGroupBox("Template Information")
            info_layout = QFormLayout(info_group)
            
            info_layout.addRow("Name:", QLabel(template['name']))
            info_layout.addRow("Category:", QLabel(template.get('category', 'No category')))
            info_layout.addRow("Description:", QLabel(template.get('description', 'No description')))
            
            template_type = "HTML" if template.get('is_html', False) else "Plain Text"
            type_label = QLabel(template_type)
            type_label.setStyleSheet(f"color: {'#3498db' if template.get('is_html', False) else '#95a5a6'}; font-weight: bold;")
            info_layout.addRow("Type:", type_label)
            
            self.preview_layout.addWidget(info_group)
            
            # Subject preview
            subject_group = QGroupBox("Subject")
            subject_layout = QVBoxLayout(subject_group)
            
            subject_preview = QLabel(template['subject'])
            subject_preview.setWordWrap(True)
            subject_preview.setStyleSheet(
                "background-color: #f8f9fa; border: 1px solid #dee2e6; "
                "padding: 10px; border-radius: 4px; font-weight: bold;"
            )
            subject_layout.addWidget(subject_preview)
            
            self.preview_layout.addWidget(subject_group)
            
            # Body preview
            body_group = QGroupBox("Body Preview")
            body_layout = QVBoxLayout(body_group)
            
            # Replace variables with sample data for preview
            preview_body = self.replace_variables_for_preview(template['body'])
            
            if template.get('is_html', False):
                # HTML preview
                try:
                    html_preview = QWebEngineView()
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                        </style>
                    </head>
                    <body>
                        {preview_body}
                    </body>
                    </html>
                    """
                    html_preview.setHtml(html_content)
                    html_preview.setMaximumHeight(300)
                    body_layout.addWidget(html_preview)
                except ImportError:
                    # Fallback to QTextEdit
                    html_preview = QTextEdit()
                    html_preview.setHtml(preview_body)
                    html_preview.setReadOnly(True)
                    html_preview.setMaximumHeight(300)
                    body_layout.addWidget(html_preview)
            else:
                # Plain text preview
                text_preview = QTextEdit()
                text_preview.setPlainText(preview_body)
                text_preview.setReadOnly(True)
                text_preview.setMaximumHeight(300)
                text_preview.setStyleSheet(
                    "background-color: #f8f9fa; border: 1px solid #dee2e6; "
                    "padding: 10px; border-radius: 4px;"
                )
                body_layout.addWidget(text_preview)
            
            self.preview_layout.addWidget(body_group)
            
            # Variables used
            variables_used = self.extract_variables(template['body'] + " " + template['subject'])
            if variables_used:
                variables_group = QGroupBox("Variables Used")
                variables_layout = QVBoxLayout(variables_group)
                
                variables_text = ", ".join(sorted(variables_used))
                variables_label = QLabel(variables_text)
                variables_label.setWordWrap(True)
                variables_label.setStyleSheet(
                    "background-color: #fff3cd; border: 1px solid #ffeaa7; "
                    "padding: 10px; border-radius: 4px; font-family: monospace;"
                )
                variables_layout.addWidget(variables_label)
                
                self.preview_layout.addWidget(variables_group)
            
            # Add stretch to push content to top
            self.preview_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"Error showing template preview: {e}")
            self.show_empty_preview()
    
    def show_empty_preview(self):
        """Show empty state in preview panel"""
        # Clear existing content
        for i in reversed(range(self.preview_layout.count())):
            child = self.preview_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        empty_label = QLabel("Select a template to view preview")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet(
            "color: #95a5a6; font-size: 16px; font-style: italic; padding: 50px;"
        )
        
        self.preview_layout.addWidget(empty_label)
    
    def replace_variables_for_preview(self, text):
        """Replace variables with sample data for preview"""
        replacements = {
            '{name}': 'John Doe',
            '{first_name}': 'John',
            '{last_name}': 'Doe',
            '{email}': 'john.doe@example.com',
            '{company}': 'Acme Corporation',
            '{date}': '2024-01-15',
            '{time}': '14:30',
            '{datetime}': '2024-01-15 14:30',
            '{sender_name}': 'Your Name',
            '{sender_email}': 'you@company.com'
        }
        
        for variable, value in replacements.items():
            text = text.replace(variable, value)
        
        return text
    
    def extract_variables(self, text):
        """Extract variables from text"""
        # Find all {variable} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, text)
        return [f"{{{match}}}" for match in matches]
    
    def add_template(self):
        """Add new template"""
        dialog = TemplateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                template_data = dialog.get_template_data()
                
                template_id = self.db_manager.add_email_template(
                    template_data['name'],
                    template_data['subject'],
                    template_data['body'],
                    template_data['is_html']
                )
                
                # Update template with additional fields
                if template_data['description'] or template_data['category']:
                    # Note: You might need to add these fields to the database schema
                    pass
                
                self.load_templates()
                QMessageBox.information(self, "Success", "Template created successfully!")
                
            except Exception as e:
                self.logger.error(f"Error adding template: {e}")
                QMessageBox.critical(self, "Error", f"Failed to create template: {str(e)}")
    
    def edit_template(self):
        """Edit selected template"""
        current_row = self.templates_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a template to edit.")
            return
        
        try:
            template_id = self.templates_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            template = self.db_manager.get_email_template(template_id)
            
            if not template:
                QMessageBox.warning(self, "Error", "Template not found.")
                return
            
            dialog = TemplateDialog(self, template)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                template_data = dialog.get_template_data()
                
                self.db_manager.update_email_template(
                    template_id,
                    template_data['name'],
                    template_data['subject'],
                    template_data['body'],
                    template_data['is_html']
                )
                
                self.load_templates()
                self.show_template_preview()  # Refresh preview
                QMessageBox.information(self, "Success", "Template updated successfully!")
                
        except Exception as e:
            self.logger.error(f"Error editing template: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit template: {str(e)}")
    
    def duplicate_template(self):
        """Duplicate selected template"""
        current_row = self.templates_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a template to duplicate.")
            return
        
        try:
            template_id = self.templates_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            template = self.db_manager.get_email_template(template_id)
            
            if not template:
                QMessageBox.warning(self, "Error", "Template not found.")
                return
            
            # Create copy with modified name
            template['name'] = f"{template['name']} (Copy)"
            
            dialog = TemplateDialog(self, template)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                template_data = dialog.get_template_data()
                
                new_template_id = self.db_manager.add_email_template(
                    template_data['name'],
                    template_data['subject'],
                    template_data['body'],
                    template_data['is_html']
                )
                
                self.load_templates()
                QMessageBox.information(self, "Success", "Template duplicated successfully!")
                
        except Exception as e:
            self.logger.error(f"Error duplicating template: {e}")
            QMessageBox.critical(self, "Error", f"Failed to duplicate template: {str(e)}")
    
    def delete_template(self):
        """Delete selected template"""
        current_row = self.templates_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a template to delete.")
            return
        
        template_name = self.templates_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the template '{template_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                template_id = self.templates_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
                
                self.db_manager.delete_email_template(template_id)
                
                self.load_templates()
                self.show_empty_preview()
                QMessageBox.information(self, "Success", "Template deleted successfully!")
                
            except Exception as e:
                self.logger.error(f"Error deleting template: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete template: {str(e)}")
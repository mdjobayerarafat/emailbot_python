# Email Automation Bot

A comprehensive desktop application for automating email management tasks, including inbox monitoring, automated responses, email scheduling, and template management.

![Email Automation Bot](icon.png)

## Features

- 📊 **Dashboard**: Real-time overview of system status and activities
- 👁️ **Inbox Monitor**: Automatic email monitoring with custom auto-reply rules
- 📤 **Email Sender**: Send individual emails or bulk campaigns
- ⏰ **Scheduler**: Schedule emails for future delivery with flexible timing options
- 📧 **Templates**: Create and manage reusable email templates with variables
- 📋 **Logs**: Comprehensive logging and activity tracking
- ⚙️ **Settings**: Easy configuration of email accounts and application preferences

## Quick Start

### Prerequisites

- Windows 10 or later
- Python 3.8 or higher
- Internet connection for email operations

### Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

### First-Time Setup

1. **Launch the application** by running `python main.py`
2. **Configure your email account** in the Settings panel:
   - Add your SMTP settings for sending emails
   - Add your IMAP settings for receiving emails
   - Test the connection to ensure everything works
3. **Start using the features**:
   - Create email templates in the Templates panel
   - Set up auto-reply rules in the Inbox Monitor
   - Schedule emails in the Scheduler panel

## Email Provider Configuration

### Gmail
- **SMTP**: smtp.gmail.com:587 (TLS)
- **IMAP**: imap.gmail.com:993 (SSL)
- **Note**: Use App Passwords instead of your regular password

### Outlook/Hotmail
- **SMTP**: smtp-mail.outlook.com:587 (TLS)
- **IMAP**: outlook.office365.com:993 (SSL)

### Yahoo Mail
- **SMTP**: smtp.mail.yahoo.com:587 (TLS)
- **IMAP**: imap.mail.yahoo.com:993 (SSL)

## Documentation

For detailed usage instructions, please refer to the [User Guide](USER_GUIDE.md) which covers:

- Complete setup instructions
- Detailed feature explanations
- Step-by-step tutorials
- Troubleshooting guide
- Best practices and tips

## Project Structure

```
email_automation_bot/
├── main.py                 # Application entry point
├── main_window.py          # Main application window
├── ui/                     # UI panels and components
│   ├── dashboard_panel.py
│   ├── inbox_monitor_panel.py
│   ├── email_sender_panel.py
│   ├── scheduler_panel.py
│   ├── templates_panel.py
│   ├── logs_panel.py
│   └── settings_panel.py
├── core/                   # Core functionality
│   ├── email_manager.py
│   ├── scheduler.py
│   ├── template_manager.py
│   └── logger.py
├── data/                   # Data storage
├── requirements.txt        # Python dependencies
├── USER_GUIDE.md          # Comprehensive user documentation
└── README.md              # This file
```

## Key Features Explained

### Inbox Monitor
- Monitor incoming emails in real-time
- Create custom auto-reply rules based on keywords
- Automatic response generation using templates
- Priority-based rule processing

### Email Scheduler
- Schedule one-time or recurring emails
- Support for daily, weekly, and monthly schedules
- Bulk email campaigns with recipient management
- Template integration for consistent messaging

### Template System
- Create reusable email templates
- Support for variables like {name}, {company}, {date}
- HTML and plain text templates
- Template categories for organization

### Comprehensive Logging
- Track all email activities
- System event logging
- Error tracking and debugging
- Exportable log files

## Security Features

- Encrypted storage of email credentials
- App password support for major email providers
- Session management and timeout
- Secure backup and restore functionality

## System Requirements

- **Operating System**: Windows 10 or later
- **Python**: 3.8 or higher
- **Memory**: 512 MB RAM minimum
- **Storage**: 100 MB free space
- **Network**: Internet connection for email operations

## Dependencies

The application uses the following main libraries:
- PyQt5 - GUI framework
- imaplib - Email receiving
- smtplib - Email sending
- schedule - Task scheduling
- cryptography - Secure credential storage

See `requirements.txt` for the complete list of dependencies.

## Troubleshooting

### Common Issues

1. **Email connection errors**: Check your email provider settings and ensure app passwords are used
2. **Scheduler not working**: Verify system time and ensure the scheduler service is started
3. **Auto-reply not triggering**: Check IMAP settings and ensure monitoring is active

For detailed troubleshooting, see the [User Guide](USER_GUIDE.md#troubleshooting).

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
1. Check the [User Guide](USER_GUIDE.md) for detailed instructions
2. Review the Logs panel in the application for error messages
3. Ensure your email provider settings are correct

---

**Version**: 1.0.0  
**Last Updated**: December 2024

Built with ❤️ for email automation enthusiasts

## 🚀 Features

### Core Functionality
- **📧 Email Account Management**: Secure storage of multiple email accounts with encryption
- **📤 Batch Email Sending**: Send personalized emails to multiple recipients with CSV import
- **👁️ Inbox Monitoring**: Automatic monitoring with keyword-based auto-replies
- **⏰ Email Scheduling**: Schedule recurring email campaigns (daily, weekly, monthly, custom)
- **📝 Template Management**: Create and manage HTML/plain text email templates
- **📎 Attachment Handling**: Automatic download and categorization of attachments
- **📊 Comprehensive Logging**: Track all email activities with export capabilities

### User Interface
- **Modern GUI**: Clean, intuitive interface built with PyQt6
- **Dashboard**: Overview of email statistics and recent activities
- **System Tray**: Minimize to system tray for background operation
- **Multi-tab Interface**: Organized workflow with dedicated panels for each feature
- **Real-time Updates**: Live status indicators and progress tracking

### Security & Data
- **Encrypted Storage**: Secure credential storage using AES encryption
- **SQLite Database**: Local data storage for all application data
- **Backup & Restore**: Automatic and manual database backup functionality
- **User Authentication**: Login system with password protection

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.10 or higher
- **Memory**: 512 MB RAM minimum, 1 GB recommended
- **Storage**: 100 MB free disk space

### Python Dependencies
- PyQt6 >= 6.0.0
- cryptography >= 3.4.8
- APScheduler >= 3.9.0
- Standard library modules (included with Python)

## 🛠️ Installation

### Option 1: Clone from Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/email-automation-bot.git
cd email-automation-bot

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Direct Download

1. Download the project files
2. Extract to your desired directory
3. Open terminal/command prompt in the project directory
4. Install dependencies: `pip install -r requirements.txt`

## 🚀 Quick Start

### 1. Run the Application

#### Option A: Using the batch file (Windows)
```bash
run_app.bat
```

#### Option B: Manual activation
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/macOS

# Run the application
python main.py
```

### 2. First-Time Setup

1. **Login/Register**: Create a new user account or login with existing credentials
2. **Add Email Account**: Go to Settings → Accounts → Add Account
   - Enter your email credentials
   - Configure SMTP/IMAP settings (auto-configuration available for popular providers)
   - Test the connection
3. **Configure Settings**: Adjust application preferences in the Settings panel

### 3. Basic Usage

#### Send Batch Emails
1. Navigate to **Email Sender** panel
2. Import contacts from CSV or add manually
3. Compose your email or select a template
4. Configure sending options (delay, test mode)
5. Click **Send Emails**

#### Set Up Auto-Replies
1. Go to **Inbox Monitor** panel
2. Add auto-reply rules with keywords
3. Select reply templates
4. Start monitoring

#### Schedule Email Campaigns
1. Open **Scheduler** panel
2. Create new schedule
3. Configure timing (once, daily, weekly, etc.)
4. Select recipients and template
5. Activate the schedule

## 📁 Project Structure

```
email-automation-bot/
├── main.py                 # Application entry point
├── main_window.py          # Main application window
├── database.py             # Database management
├── email_handler.py        # Email operations (SMTP/IMAP)
├── scheduler.py            # Email scheduling
├── requirements.txt        # Python dependencies
├── run_app.bat            # Windows batch file to run app
├── README.md              # This file
├── venv/                  # Virtual environment (created after setup)
├── ui/                    # User interface modules
│   ├── __init__.py
│   ├── login_dialog.py    # Login/registration dialog
│   ├── dashboard_panel.py # Dashboard overview
│   ├── inbox_monitor_panel.py # Inbox monitoring
│   ├── email_sender_panel.py  # Batch email sender
│   ├── scheduler_panel.py     # Email scheduler
│   ├── templates_panel.py     # Template management
│   ├── logs_panel.py          # Logs and export
│   └── settings_panel.py      # Application settings
├── logs/                  # Application logs (created at runtime)
├── backups/              # Database backups (created at runtime)
└── attachments/          # Downloaded attachments (created at runtime)
```

## ⚙️ Configuration

### Email Provider Settings

The application includes auto-configuration for popular email providers:

#### Gmail
- **SMTP**: smtp.gmail.com:587 (STARTTLS)
- **IMAP**: imap.gmail.com:993 (SSL/TLS)
- **Note**: Use App Passwords for 2FA-enabled accounts

#### Outlook/Hotmail
- **SMTP**: smtp-mail.outlook.com:587 (STARTTLS)
- **IMAP**: outlook.office365.com:993 (SSL/TLS)

#### Yahoo Mail
- **SMTP**: smtp.mail.yahoo.com:587 (STARTTLS)
- **IMAP**: imap.mail.yahoo.com:993 (SSL/TLS)

### Custom SMTP/IMAP Settings

For other email providers, configure manually:
1. Go to Settings → Accounts → Add Account
2. Select "Custom" provider
3. Enter server details, ports, and security settings
4. Test connection before saving

## 📊 Features Guide

### Dashboard
- **Statistics**: Email counts, success rates, template usage
- **Recent Activity**: Latest sent emails and system events
- **Quick Actions**: Fast access to common tasks
- **System Status**: Real-time status of email accounts and services

### Email Templates
- **Rich Text Editor**: Format emails with HTML styling
- **Variable Support**: Use placeholders like `{name}`, `{email}`, `{company}`
- **Preview**: Live preview of templates before sending
- **Categories**: Organize templates by type or purpose

### Batch Email Sending
- **CSV Import**: Import contacts with column mapping
- **Personalization**: Automatic variable replacement
- **Progress Tracking**: Real-time sending progress and results
- **Test Mode**: Send test emails before full batch
- **Retry Logic**: Automatic retry for failed emails

### Inbox Monitoring
- **Keyword Rules**: Define auto-reply triggers
- **Priority System**: Set rule priorities for multiple matches
- **Template Responses**: Use templates for consistent replies
- **Real-time Processing**: Immediate response to incoming emails

### Email Scheduling
- **Flexible Timing**: Once, daily, weekly, monthly, or custom intervals
- **Recipient Management**: Schedule for all contacts or specific groups
- **Template Integration**: Use existing templates for scheduled emails
- **Status Tracking**: Monitor scheduled email execution

### Logging & Export
- **Comprehensive Logs**: Track all email activities
- **Filter & Search**: Find specific log entries quickly
- **Export Options**: Export logs to CSV or JSON
- **Statistics**: View sending statistics and success rates

## 🔧 Troubleshooting

### Common Issues

#### Connection Errors
- **Check credentials**: Verify email address and password
- **App Passwords**: Use app-specific passwords for 2FA accounts
- **Firewall**: Ensure SMTP/IMAP ports are not blocked
- **Server Settings**: Verify SMTP/IMAP server addresses and ports

#### Email Sending Issues
- **Rate Limits**: Reduce sending speed if hitting provider limits
- **Authentication**: Check if email provider requires specific authentication
- **Content Filters**: Avoid spam-like content in emails

#### Database Issues
- **Backup**: Use the backup feature before making changes
- **Permissions**: Ensure write permissions in application directory
- **Corruption**: Restore from backup if database becomes corrupted

### Log Files

Check log files for detailed error information:
- **Location**: `logs/email_automation_bot.log`
- **Levels**: INFO, WARNING, ERROR, CRITICAL
- **Rotation**: Logs are automatically rotated to prevent large files

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/email-automation-bot.git
cd email-automation-bot

# Create development environment
python -m venv dev-env
source dev-env/bin/activate  # or dev-env\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt6**: For the excellent GUI framework
- **APScheduler**: For robust job scheduling
- **Cryptography**: For secure credential storage
- **Python Community**: For the amazing ecosystem

## 📞 Support

If you encounter any issues or have questions:

1. **Check Documentation**: Review this README and inline code comments
2. **Search Issues**: Look through existing GitHub issues
3. **Create Issue**: Open a new issue with detailed information
4. **Email**: Contact [your-email@example.com](mailto:your-email@example.com)

## 🗺️ Roadmap

### Planned Features
- [ ] **Email Analytics**: Advanced statistics and reporting
- [ ] **Plugin System**: Support for custom extensions
- [ ] **Cloud Sync**: Synchronize data across devices
- [ ] **Mobile App**: Companion mobile application
- [ ] **API Integration**: REST API for external integrations
- [ ] **Advanced Filtering**: More sophisticated email filtering options
- [ ] **Multi-language Support**: Internationalization
- [ ] **Dark Theme**: Alternative UI theme

### Version History
- **v1.0.0** (Current): Initial release with core features

---

**Made with ❤️ using Python and PyQt6**
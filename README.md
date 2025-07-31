<div align="center">

# 📧 Email Automation Bot

<img src="icon.png" alt="Email Automation Bot" width="120" height="120">

**A powerful cross-platform desktop application for automated email management**

*Built with Python, PyQt6, and SQLite*

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

## ✨ Features

- **📊 Dashboard** - Real-time overview of system status and activities
- **👁️ Inbox Monitor** - Automatic email monitoring with custom auto-reply rules
- **📤 Email Sender** - Send individual emails or bulk campaigns with CSV import
- **⏰ Scheduler** - Schedule emails for future delivery with flexible timing options
- **📧 Templates** - Create and manage reusable email templates with variables
- **📋 Logs** - Comprehensive logging and activity tracking
- **⚙️ Settings** - Easy configuration of email accounts and application preferences
- **🔒 Security** - Encrypted storage of email credentials with app password support

## 🚀 Quick Start

### Prerequisites
- Windows 10+ / Linux / macOS
- Python 3.8 or higher
- Internet connection for email operations

### Installation

```bash
# Clone the repository
git clone https://github.com/mdjobayerarafat/emailbot_python.git
cd emailbot_python

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### First-Time Setup

1. **Launch** the application by running `python main.py`
2. **Configure** your email account in the Settings panel
3. **Test** the connection to ensure everything works
4. **Start** using the features - create templates, set up auto-replies, schedule emails

## 📧 Email Provider Configuration

| Provider | SMTP Server | IMAP Server | Port | Security |
|----------|-------------|-------------|------|----------|
| **Gmail** | smtp.gmail.com | imap.gmail.com | 587/993 | TLS/SSL |
| **Outlook** | smtp-mail.outlook.com | outlook.office365.com | 587/993 | TLS/SSL |
| **Yahoo** | smtp.mail.yahoo.com | imap.mail.yahoo.com | 587/993 | TLS/SSL |

> **Note**: Use App Passwords for accounts with 2FA enabled

## 📁 Project Structure

```
emailbot_python/
├── main.py                 # Application entry point
├── main_window.py          # Main application window
├── database.py             # Database management
├── email_handler.py        # Email operations (SMTP/IMAP)
├── scheduler.py            # Email scheduling
├── requirements.txt        # Python dependencies
├── run_app.bat            # Windows batch file
├── ui/                    # User interface modules
│   ├── dashboard_panel.py
│   ├── inbox_monitor_panel.py
│   ├── email_sender_panel.py
│   ├── scheduler_panel.py
│   ├── templates_panel.py
│   ├── logs_panel.py
│   └── settings_panel.py
└── USER_GUIDE.md          # Comprehensive documentation
```

## 🛠️ System Requirements

- **OS**: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.8 or higher
- **Memory**: 512 MB RAM minimum
- **Storage**: 100 MB free space
- **Network**: Internet connection for email operations

## 📚 Documentation

For detailed usage instructions, please refer to the [**User Guide**](USER_GUIDE.md) which covers:

- Complete setup instructions
- Detailed feature explanations
- Step-by-step tutorials
- Troubleshooting guide
- Best practices and tips

## 🔧 Troubleshooting

### Common Issues

- **Connection errors**: Check email provider settings and use app passwords
- **Scheduler not working**: Verify system time and scheduler service status
- **Auto-reply not triggering**: Check IMAP settings and monitoring status

For detailed troubleshooting, see the [User Guide](USER_GUIDE.md#troubleshooting).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **GitHub Repository**: https://github.com/mdjobayerarafat/emailbot_python.git
- **Documentation**: https://github.com/mdjobayerarafat/emailbot_python/blob/main/USER_GUIDE.md

## 💬 Support

For support and questions:
- Check the [User Guide](USER_GUIDE.md) for detailed instructions
- Review the Logs panel in the application for error messages
- Ensure your email provider settings are correct

---

<div align="center">

**Version 1.0.0** | **Last Updated: December 2024**

Built with ❤️ by **MD JOBAYER ARAFAT** for email automation enthusiasts

</div>
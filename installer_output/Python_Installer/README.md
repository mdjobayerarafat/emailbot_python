# Python Self-Extracting Installer

This folder contains a Python-based self-extracting installer for Email Automation Bot.

## Files Included

- **EmailAutomationBot_Installer.py** (577.7 MB) - Python self-extracting installer script

## Features

- ✅ Cross-platform compatibility (Windows, macOS, Linux)
- ✅ Self-contained installer (no external dependencies)
- ✅ GUI installation interface using tkinter
- ✅ Installation path selection
- ✅ Progress indicators and status updates
- ✅ Automatic shortcut creation (Windows)
- ✅ Error handling and validation
- ✅ Embedded application files
- ✅ Custom installation options

## Prerequisites

- **Python 3.7+** installed on the target system
- **tkinter** (usually included with Python)
- **Administrator privileges** (recommended for system-wide installation)

## Installation Instructions

### Method 1: Direct Python Execution
```bash
# Run the installer
python EmailAutomationBot_Installer.py
```

### Method 2: Double-click (Windows)
1. **Double-click** `EmailAutomationBot_Installer.py`
2. **Select Python**: Choose Python interpreter if prompted
3. **Follow GUI**: Use the graphical installation wizard

### Method 3: Command Line with Options
```bash
# Silent installation to default location
python EmailAutomationBot_Installer.py --silent

# Install to custom directory
python EmailAutomationBot_Installer.py --path "C:\Custom\Path"

# Show help
python EmailAutomationBot_Installer.py --help
```

## Installation Process

1. **Welcome Screen**: Introduction and system check
2. **License Agreement**: Review and accept terms
3. **Installation Path**: Choose destination folder
4. **Component Selection**: Select features to install
5. **Installation**: Extract and copy files with progress
6. **Shortcuts**: Create desktop and menu shortcuts
7. **Completion**: Installation summary and launch option

## Command Line Arguments

| Argument | Description | Example |
|----------|-------------|----------|
| `--silent` | Silent installation (no GUI) | `--silent` |
| `--path <dir>` | Custom installation directory | `--path "C:\Apps"` |
| `--no-shortcuts` | Skip shortcut creation | `--no-shortcuts` |
| `--help` | Show help message | `--help` |
| `--version` | Show installer version | `--version` |

## What Gets Installed

```
Installation Directory/
├── EmailAutomationBot.exe          # Main application
├── email_bot.db                    # Database file
├── encryption.key                  # Security key
├── logs/                           # Log directory
│   └── email_automation_bot.log    # Application logs
├── README.md                       # Documentation
├── USER_GUIDE.md                   # User guide
├── INSTALLATION.md                 # Installation guide
├── requirements.txt                # Dependencies
└── uninstall.py                    # Uninstaller script
```

## Shortcuts Created (Windows)

- **Desktop**: `Email Automation Bot.lnk`
- **Start Menu**: `Programs\Email Automation Bot\Email Automation Bot.lnk`
- **Start Menu**: `Programs\Email Automation Bot\Uninstall.lnk`

## Uninstallation

### Method 1: Use Uninstaller
```bash
# Run the uninstaller
python "<installation_path>\uninstall.py"
```

### Method 2: Manual Removal
1. Delete the installation directory
2. Remove shortcuts from Desktop and Start Menu
3. Clean up any configuration files (if applicable)

## Advanced Features

### Custom Installation Scripts
The installer supports custom pre/post installation scripts:

```python
# Add to installer before running
def pre_install_hook():
    # Custom setup before installation
    pass

def post_install_hook():
    # Custom setup after installation
    pass
```

### Configuration Options
Modify installer behavior by editing the script:

```python
# Installation configuration
CONFIG = {
    'app_name': 'Email Automation Bot',
    'version': '1.0.0',
    'default_path': 'C:\\Program Files\\EmailAutomationBot',
    'create_shortcuts': True,
    'require_admin': False,
    'check_dependencies': True
}
```

## Troubleshooting

### Common Issues

1. **"Python not found"**
   - Install Python 3.7+ from python.org
   - Ensure Python is in system PATH
   - Try: `py EmailAutomationBot_Installer.py`

2. **"tkinter not available"**
   - Install tkinter: `pip install tk`
   - Or use command line: `python EmailAutomationBot_Installer.py --silent`

3. **"Permission denied"**
   - Run as Administrator
   - Choose a user-writable installation path
   - Check antivirus software settings

4. **"Installation failed"**
   - Check available disk space
   - Verify Python version compatibility
   - Review error messages in console

5. **"Shortcuts not created"**
   - Run with administrator privileges
   - Check if `--no-shortcuts` was used
   - Manually create shortcuts if needed

### Debug Mode
Run with debug output:
```bash
python EmailAutomationBot_Installer.py --debug
```

## Advantages

- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Customizable**: Easy to modify and extend
- **Self-Contained**: No external installer tools required
- **Scriptable**: Can be automated and integrated into deployment scripts
- **Transparent**: Source code is visible and auditable
- **Flexible**: Supports various installation scenarios

## Disadvantages

- **Requires Python**: Target system must have Python installed
- **Large File Size**: Contains embedded application files
- **Less Professional**: Not a native installer format
- **Platform Specific**: Some features only work on Windows

## Best For

- Development and testing environments
- Cross-platform deployment
- Automated installation scripts
- Custom installation requirements
- Systems with Python already installed
- Scenarios requiring installation customization

## Security Considerations

- The installer contains embedded application files
- Verify the source and integrity before running
- Consider code signing for production distribution
- Review the Python script for any security concerns
- Use in trusted environments only

## Customization Guide

To modify the installer:

1. **Edit Configuration**: Modify the CONFIG dictionary
2. **Add Custom Logic**: Insert pre/post installation hooks
3. **Change UI**: Modify tkinter interface elements
4. **Add Features**: Extend functionality as needed
5. **Test Thoroughly**: Verify changes on target systems

## Support

For issues with the Python installer:
1. Check Python version compatibility
2. Review console output for error messages
3. Try running with `--debug` flag
4. Verify system requirements are met
5. Contact support with detailed error information
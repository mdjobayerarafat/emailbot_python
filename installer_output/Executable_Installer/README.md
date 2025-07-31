# Executable Installer Package

This folder contains ready-to-run executable installers for Email Automation Bot.

## Files Included

- **EmailAutomationBot_Setup.exe** (211.4 MB) - Professional executable installer
- **Quick_Install.bat** (1.7 KB) - Simple batch file installer

## EmailAutomationBot_Setup.exe

### Features
- ✅ Professional GUI installer interface
- ✅ Custom installation wizard
- ✅ Installation path selection
- ✅ Desktop and Start Menu shortcuts
- ✅ Add/Remove Programs registration
- ✅ Built-in uninstaller
- ✅ Progress indicators and status updates
- ✅ Error handling and rollback

### Installation Instructions
1. **Double-click** `EmailAutomationBot_Setup.exe`
2. **Follow the wizard**: Choose installation options
3. **Select path**: Choose installation directory (default: Program Files)
4. **Create shortcuts**: Select shortcut preferences
5. **Complete**: Click Finish to complete installation

### System Requirements
- Windows 10/11 (64-bit)
- Administrator privileges (recommended)
- 500MB free disk space
- 4GB RAM (recommended)

## Quick_Install.bat

### Features
- ✅ Simple command-line installation
- ✅ Automatic file copying
- ✅ Basic shortcut creation
- ✅ Minimal user interaction
- ✅ Fast deployment

### Installation Instructions
1. **Right-click** `Quick_Install.bat` and select "Run as administrator"
2. **Follow prompts**: The script will guide you through basic setup
3. **Automatic setup**: Files are copied and shortcuts created

### What Quick Install Does
- Copies application files to Program Files
- Creates desktop shortcut
- Sets up basic file associations
- Configures initial application settings

## Comparison

| Feature | Setup.exe | Quick_Install.bat |
|---------|-----------|-------------------|
| GUI Interface | ✅ Professional | ❌ Command-line only |
| Installation Options | ✅ Full customization | ❌ Basic options |
| Progress Indicators | ✅ Visual progress | ✅ Text progress |
| Error Handling | ✅ Advanced | ✅ Basic |
| Uninstaller | ✅ Built-in | ❌ Manual removal |
| File Size | 211.4 MB | 1.7 KB |
| Dependencies | ✅ Self-contained | ❌ Requires release files |
| User Experience | ✅ Professional | ✅ Simple |

## Installation Locations

Both installers will install to:
- **Default Path**: `C:\Program Files\EmailAutomationBot\`
- **Desktop Shortcut**: `Email Automation Bot.lnk`
- **Start Menu**: `Programs\Email Automation Bot`

## Uninstallation

### For Setup.exe Installation
- Use Windows "Add or Remove Programs"
- Or run uninstaller from installation directory

### For Quick_Install.bat Installation
- Manually delete installation folder
- Remove shortcuts from Desktop and Start Menu
- Clean up any registry entries (if applicable)

## Troubleshooting

### Common Issues

1. **"Access Denied" Error**
   - Run installer as Administrator
   - Check antivirus software isn't blocking

2. **Installation Fails**
   - Ensure sufficient disk space
   - Close any running instances of the application
   - Temporarily disable antivirus during installation

3. **Shortcuts Not Created**
   - Check user permissions
   - Manually create shortcuts if needed

4. **Application Won't Start**
   - Verify all files were copied correctly
   - Check Windows Event Viewer for error details
   - Ensure .NET Framework is installed

## Best For

### EmailAutomationBot_Setup.exe
- End-user distribution
- Professional deployment
- Users who prefer GUI installers
- Complete installation experience
- Systems requiring proper uninstall support

### Quick_Install.bat
- Quick testing and development
- Automated deployment scripts
- Minimal installation footprint
- Systems where GUI installers are not preferred
- Batch deployment scenarios

## Security Notes

- Both installers are digitally signed (if applicable)
- Antivirus software may flag executable installers
- Always download from trusted sources
- Verify file integrity before installation

## Support

For installation issues:
1. Check this README for troubleshooting steps
2. Review installation logs (if available)
3. Contact support with specific error messages
4. Include system information and installation method used
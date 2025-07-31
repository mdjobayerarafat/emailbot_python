# WiX Toolset Source Files

This folder contains WiX (Windows Installer XML) source files for creating a professional MSI installer.

## Files Included

- **EmailBot.wxs** (4.6 KB) - WiX source file defining the installer structure
- **compile_msi.bat** (1.2 KB) - Batch script to compile the MSI installer

## Prerequisites

To compile the MSI installer, you need:

1. **WiX Toolset v3.11+** - Download from: https://wixtoolset.org/
2. **Visual Studio Build Tools** or **Visual Studio** (for MSBuild)
3. **Windows SDK** (usually included with Visual Studio)

## Installation Instructions

### Step 1: Install WiX Toolset
```bash
# Download and install WiX Toolset from:
# https://github.com/wixtoolset/wix3/releases
```

### Step 2: Compile the MSI
```bash
# Run the compilation script
compile_msi.bat
```

### Manual Compilation
If the batch script doesn't work, compile manually:
```bash
# Navigate to this directory
cd installer_output\WiX_Source

# Compile the WiX source
candle.exe EmailBot.wxs

# Link to create MSI
light.exe EmailBot.wixobj -out EmailAutomationBot.msi
```

## WiX Source Features

The `EmailBot.wxs` file defines:

- ✅ Product information and versioning
- ✅ Installation directory structure
- ✅ File components and registry entries
- ✅ Desktop and Start Menu shortcuts
- ✅ Add/Remove Programs integration
- ✅ Upgrade and uninstall logic
- ✅ Custom actions and dialogs

## Generated MSI Features

- **Professional Windows Installer**: Native MSI format
- **Group Policy Support**: Can be deployed via Active Directory
- **Rollback Support**: Automatic rollback on installation failure
- **Repair Functionality**: Built-in repair option
- **Upgrade Logic**: Handles version upgrades properly
- **Silent Installation**: Supports `/quiet` parameter

## Command Line Options

Once compiled, the MSI supports standard Windows Installer options:

```bash
# Silent installation
msiexec /i EmailAutomationBot.msi /quiet

# Installation with logging
msiexec /i EmailAutomationBot.msi /l*v install.log

# Uninstall
msiexec /x EmailAutomationBot.msi /quiet

# Repair
msiexec /fa EmailAutomationBot.msi
```

## Customization

To customize the installer:

1. Edit `EmailBot.wxs` with your preferred XML editor
2. Modify product information, features, or UI
3. Recompile using the batch script or manual commands

## Troubleshooting

### Common Issues

1. **"candle.exe not found"**
   - Ensure WiX Toolset is installed and in PATH
   - Try full path: `"C:\Program Files (x86)\WiX Toolset v3.11\bin\candle.exe"`

2. **"light.exe failed"**
   - Check for missing files in the source directory
   - Verify all referenced files exist

3. **MSI validation errors**
   - Use `light.exe -sval` to skip validation
   - Check WiX documentation for specific error codes

## Best For

- Enterprise deployment via Group Policy
- Professional software distribution
- Systems requiring native MSI format
- Advanced installation customization
- Corporate environments with strict installer requirements

## Documentation

- WiX Toolset Documentation: https://wixtoolset.org/documentation/
- WiX Tutorial: https://www.firegiant.com/wix/tutorial/
- MSI Reference: https://docs.microsoft.com/en-us/windows/win32/msi/
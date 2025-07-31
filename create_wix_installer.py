#!/usr/bin/env python3
"""
WiX-based MSI Installer Creator for Email Automation Bot
Creates MSI installer using WiX Toolset (if available) or generates WiX source files
"""

import os
import sys
import uuid
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

class WiXInstaller:
    def __init__(self):
        self.app_name = "Email Automation Bot"
        self.app_version = "1.0.0"
        self.manufacturer = "MD JOBAYER ARAFAT"
        self.product_id = str(uuid.uuid4()).upper()
        self.upgrade_code = str(uuid.uuid4()).upper()
        
        # Paths
        self.source_dir = "release"
        self.output_dir = "installer_output"
        self.wxs_file = os.path.join(self.output_dir, "EmailBot.wxs")
        self.msi_name = f"EmailAutomationBot_v{self.app_version}.msi"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_component_id(self, file_path):
        """Generate a unique component ID for a file"""
        # Create a deterministic ID based on file path
        import hashlib
        hash_obj = hashlib.md5(file_path.encode())
        return f"comp_{hash_obj.hexdigest()[:8]}"
    
    def create_wxs_file(self):
        """Create WiX source file (.wxs)"""
        print(f"📝 Creating WiX source file: {self.wxs_file}")
        
        # Create root element
        wix = ET.Element("Wix", xmlns="http://schemas.microsoft.com/wix/2006/wi")
        
        # Product element
        product = ET.SubElement(wix, "Product", {
            "Id": self.product_id,
            "Name": self.app_name,
            "Language": "1033",
            "Version": self.app_version,
            "Manufacturer": self.manufacturer,
            "UpgradeCode": self.upgrade_code
        })
        
        # Package element
        ET.SubElement(product, "Package", {
            "InstallerVersion": "200",
            "Compressed": "yes",
            "InstallScope": "perMachine",
            "Description": f"{self.app_name} v{self.app_version}",
            "Comments": "Professional Email Automation Tool",
            "Manufacturer": self.manufacturer
        })
        
        # Media element
        ET.SubElement(product, "Media", {
            "Id": "1",
            "Cabinet": "EmailBot.cab",
            "EmbedCab": "yes"
        })
        
        # Directory structure
        target_dir = ET.SubElement(product, "Directory", {"Id": "TARGETDIR", "Name": "SourceDir"})
        program_files = ET.SubElement(target_dir, "Directory", {"Id": "ProgramFilesFolder"})
        install_dir = ET.SubElement(program_files, "Directory", {
            "Id": "INSTALLFOLDER",
            "Name": self.app_name
        })
        
        # Program Menu Directory
        program_menu = ET.SubElement(target_dir, "Directory", {"Id": "ProgramMenuFolder"})
        app_menu = ET.SubElement(program_menu, "Directory", {
            "Id": "ApplicationProgramsFolder",
            "Name": self.app_name
        })
        
        # Desktop Directory
        ET.SubElement(target_dir, "Directory", {"Id": "DesktopFolder", "Name": "Desktop"})
        
        # Components and files
        component_group = ET.SubElement(product, "ComponentGroup", {"Id": "ProductComponents", "Directory": "INSTALLFOLDER"})
        
        if not os.path.exists(self.source_dir):
            print(f"❌ Source directory not found: {self.source_dir}")
            return False
        
        file_count = 0
        main_exe_component = None
        
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.source_dir)
                
                # Create component
                component_id = self.generate_component_id(rel_path)
                component = ET.SubElement(component_group, "Component", {
                    "Id": component_id,
                    "Guid": str(uuid.uuid4()).upper()
                })
                
                # Add file
                file_element = ET.SubElement(component, "File", {
                    "Id": f"file_{file_count}",
                    "Source": file_path,
                    "KeyPath": "yes"
                })
                
                # Remember main executable component for shortcuts
                if file.lower() == "emailautomationbot.exe":
                    main_exe_component = component_id
                    file_element.set("Id", "MainExecutable")
                
                file_count += 1
        
        # Features
        feature = ET.SubElement(product, "Feature", {
            "Id": "ProductFeature",
            "Title": self.app_name,
            "Level": "1"
        })
        ET.SubElement(feature, "ComponentGroupRef", {"Id": "ProductComponents"})
        
        # Shortcuts feature
        shortcuts_feature = ET.SubElement(product, "Feature", {
            "Id": "ShortcutsFeature",
            "Title": "Shortcuts",
            "Level": "1"
        })
        
        # Desktop shortcut component
        if main_exe_component:
            desktop_component = ET.SubElement(product, "Component", {
                "Id": "DesktopShortcutComponent",
                "Guid": str(uuid.uuid4()).upper(),
                "Directory": "DesktopFolder"
            })
            
            ET.SubElement(desktop_component, "Shortcut", {
                "Id": "DesktopShortcut",
                "Name": self.app_name,
                "Target": "[INSTALLFOLDER]EmailAutomationBot.exe",
                "WorkingDirectory": "INSTALLFOLDER",
                "Icon": "EmailBot.exe",
                "IconIndex": "0"
            })
            
            ET.SubElement(desktop_component, "RegistryValue", {
                "Root": "HKCU",
                "Key": f"Software\\{self.manufacturer}\\{self.app_name}",
                "Name": "installed",
                "Type": "integer",
                "Value": "1",
                "KeyPath": "yes"
            })
            
            ET.SubElement(shortcuts_feature, "ComponentRef", {"Id": "DesktopShortcutComponent"})
            
            # Start Menu shortcut component
            startmenu_component = ET.SubElement(product, "Component", {
                "Id": "StartMenuShortcutComponent",
                "Guid": str(uuid.uuid4()).upper(),
                "Directory": "ApplicationProgramsFolder"
            })
            
            ET.SubElement(startmenu_component, "Shortcut", {
                "Id": "StartMenuShortcut",
                "Name": self.app_name,
                "Target": "[INSTALLFOLDER]EmailAutomationBot.exe",
                "WorkingDirectory": "INSTALLFOLDER",
                "Icon": "EmailBot.exe",
                "IconIndex": "0"
            })
            
            # Uninstall shortcut
            ET.SubElement(startmenu_component, "Shortcut", {
                "Id": "UninstallShortcut",
                "Name": f"Uninstall {self.app_name}",
                "Target": "[System64Folder]msiexec.exe",
                "Arguments": f"/x [ProductCode]"
            })
            
            ET.SubElement(startmenu_component, "RemoveFolder", {
                "Id": "ApplicationProgramsFolder",
                "On": "uninstall"
            })
            
            ET.SubElement(startmenu_component, "RegistryValue", {
                "Root": "HKCU",
                "Key": f"Software\\{self.manufacturer}\\{self.app_name}",
                "Name": "startmenu",
                "Type": "integer",
                "Value": "1",
                "KeyPath": "yes"
            })
            
            ET.SubElement(shortcuts_feature, "ComponentRef", {"Id": "StartMenuShortcutComponent"})
        
        # Icon
        if os.path.exists(os.path.join(self.source_dir, "EmailAutomationBot.exe")):
            ET.SubElement(product, "Icon", {
                "Id": "EmailBot.exe",
                "SourceFile": os.path.join(self.source_dir, "EmailAutomationBot.exe")
            })
        
        # Property for Add/Remove Programs icon
        ET.SubElement(product, "Property", {
            "Id": "ARPPRODUCTICON",
            "Value": "EmailBot.exe"
        })
        
        # Upgrade logic
        upgrade = ET.SubElement(product, "Upgrade", {"Id": self.upgrade_code})
        ET.SubElement(upgrade, "UpgradeVersion", {
            "OnlyDetect": "no",
            "Property": "PREVIOUSFOUND",
            "Minimum": "1.0.0",
            "IncludeMinimum": "yes",
            "Maximum": "1.0.0",
            "IncludeMaximum": "no"
        })
        
        # Install execute sequence
        install_sequence = ET.SubElement(product, "InstallExecuteSequence")
        ET.SubElement(install_sequence, "RemoveExistingProducts", {"After": "InstallValidate"})
        
        # Write XML file
        rough_string = ET.tostring(wix, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Remove empty lines
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
        
        with open(self.wxs_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"✅ WiX source file created: {self.wxs_file}")
        return True
    
    def compile_msi(self):
        """Compile MSI using WiX toolset if available"""
        print("🔨 Attempting to compile MSI using WiX toolset...")
        
        # Check if WiX is available
        wix_paths = [
            r"C:\Program Files (x86)\WiX Toolset v3.11\bin",
            r"C:\Program Files\WiX Toolset v3.11\bin",
            r"C:\Program Files (x86)\Windows Installer XML v3.5\bin",
            r"C:\Program Files\Windows Installer XML v3.5\bin",
        ]
        
        candle_exe = None
        light_exe = None
        
        for wix_path in wix_paths:
            candle_path = os.path.join(wix_path, "candle.exe")
            light_path = os.path.join(wix_path, "light.exe")
            if os.path.exists(candle_path) and os.path.exists(light_path):
                candle_exe = candle_path
                light_exe = light_path
                break
        
        if not candle_exe:
            print("⚠️  WiX Toolset not found. Please install WiX Toolset to compile MSI.")
            print("   Download from: https://wixtoolset.org/releases/")
            print(f"   WiX source file created: {self.wxs_file}")
            return False
        
        try:
            # Compile .wxs to .wixobj
            wixobj_file = self.wxs_file.replace('.wxs', '.wixobj')
            candle_cmd = [candle_exe, self.wxs_file, "-out", wixobj_file]
            
            print(f"Running: {' '.join(candle_cmd)}")
            result = subprocess.run(candle_cmd, capture_output=True, text=True, cwd=self.output_dir)
            
            if result.returncode != 0:
                print(f"❌ Candle compilation failed:")
                print(result.stderr)
                return False
            
            # Link .wixobj to .msi
            msi_file = os.path.join(self.output_dir, self.msi_name)
            light_cmd = [light_exe, wixobj_file, "-out", msi_file]
            
            print(f"Running: {' '.join(light_cmd)}")
            result = subprocess.run(light_cmd, capture_output=True, text=True, cwd=self.output_dir)
            
            if result.returncode != 0:
                print(f"❌ Light linking failed:")
                print(result.stderr)
                return False
            
            print(f"✅ MSI compiled successfully: {msi_file}")
            
            # Get file size
            file_size = os.path.getsize(msi_file) / (1024 * 1024)
            print(f"📊 File size: {file_size:.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error compiling MSI: {str(e)}")
            return False
    
    def create_batch_compiler(self):
        """Create a batch file to compile the MSI"""
        batch_content = f'''
@echo off
echo ========================================
echo   Email Automation Bot - MSI Compiler
echo ========================================
echo.

REM Check for WiX Toolset
set "WIX_PATH="
if exist "C:\\Program Files (x86)\\WiX Toolset v3.11\\bin\\candle.exe" (
    set "WIX_PATH=C:\\Program Files (x86)\\WiX Toolset v3.11\\bin"
) else if exist "C:\\Program Files\\WiX Toolset v3.11\\bin\\candle.exe" (
    set "WIX_PATH=C:\\Program Files\\WiX Toolset v3.11\\bin"
) else (
    echo ERROR: WiX Toolset not found!
    echo Please install WiX Toolset from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)

echo Found WiX Toolset at: %WIX_PATH%
echo.

echo Compiling WiX source file...
"%WIX_PATH%\\candle.exe" EmailBot.wxs
if errorlevel 1 (
    echo ERROR: Compilation failed!
    pause
    exit /b 1
)

echo Linking MSI package...
"%WIX_PATH%\\light.exe" EmailBot.wixobj -out "{self.msi_name}"
if errorlevel 1 (
    echo ERROR: Linking failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo MSI package created successfully!
echo ========================================
echo.
echo File: {self.msi_name}
echo.
pause
'''
        
        batch_file = os.path.join(self.output_dir, "compile_msi.bat")
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"✅ MSI compiler batch file created: {batch_file}")
        return True

def main():
    print("🚀 Email Automation Bot - WiX MSI Installer Creator")
    print("=" * 55)
    
    # Check if source directory exists
    if not os.path.exists("release"):
        print("❌ Release directory not found. Please build the application first.")
        print("   Run: python build_windows.py")
        return False
    
    try:
        # Create WiX installer
        installer = WiXInstaller()
        
        # Generate WiX source file
        if not installer.create_wxs_file():
            return False
        
        # Create batch compiler
        installer.create_batch_compiler()
        
        # Try to compile MSI
        msi_compiled = installer.compile_msi()
        
        print("\n" + "=" * 55)
        if msi_compiled:
            print("✅ MSI installer created successfully!")
        else:
            print("⚠️  WiX source files created. Manual compilation required.")
        
        print(f"\n📁 Files created in '{installer.output_dir}':")
        for item in os.listdir(installer.output_dir):
            item_path = os.path.join(installer.output_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path) / 1024
                if size > 1024:
                    print(f"   - {item} ({size/1024:.1f} MB)")
                else:
                    print(f"   - {item} ({size:.1f} KB)")
        
        if not msi_compiled:
            print("\n📝 To compile MSI manually:")
            print(f"   1. Install WiX Toolset from: https://wixtoolset.org/releases/")
            print(f"   2. Run: {os.path.join(installer.output_dir, 'compile_msi.bat')}")
        
        print("\n🎉 WiX installer package is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating WiX installer: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
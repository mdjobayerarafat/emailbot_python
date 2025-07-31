#!/usr/bin/env python3
"""
MSI Installer Creator for Email Automation Bot
Creates a professional Windows MSI installer package
"""

import os
import sys
import uuid
import shutil
from pathlib import Path
try:
    import msilib
except ImportError:
    print("❌ msilib module not available. This script requires Windows.")
    sys.exit(1)

class MSIInstaller:
    def __init__(self):
        self.app_name = "Email Automation Bot"
        self.app_version = "1.0.0"
        self.manufacturer = "MD JOBAYER ARAFAT"
        self.product_code = str(uuid.uuid4()).upper()
        self.upgrade_code = str(uuid.uuid4()).upper()
        self.package_code = str(uuid.uuid4()).upper()
        
        # Paths
        self.source_dir = "release"
        self.output_dir = "installer_output"
        self.msi_name = f"EmailAutomationBot_v{self.app_version}.msi"
        self.msi_path = os.path.join(self.output_dir, self.msi_name)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_msi(self):
        """Create the MSI installer"""
        print(f"🔨 Creating MSI installer: {self.msi_name}")
        
        # Remove existing MSI if it exists
        if os.path.exists(self.msi_path):
            os.remove(self.msi_path)
        
        # Create MSI database
        db = msilib.init_database(
            self.msi_path,
            msilib.schema,
            self.app_name,
            self.package_code,
            self.app_version,
            self.manufacturer
        )
        
        # Set product properties
        msilib.add_data(db, "Property", [
            ("ProductCode", self.product_code),
            ("ProductName", self.app_name),
            ("ProductVersion", self.app_version),
            ("Manufacturer", self.manufacturer),
            ("UpgradeCode", self.upgrade_code),
            ("ALLUSERS", "1"),
            ("ARPPRODUCTICON", "EmailBot.exe"),
            ("ARPURLINFOABOUT", "https://github.com/mdjobayerarafat"),
            ("ARPCONTACT", "MD JOBAYER ARAFAT"),
            ("ARPCOMMENTS", "Professional Email Automation Tool"),
            ("ARPSIZE", "220000"),  # Size in KB
            ("REINSTALLMODE", "amus"),
            ("REINSTALL", "ALL"),
        ])
        
        # Create directory structure
        installdir = msilib.add_data(db, "Directory", [
            ("TARGETDIR", None, "SourceDir"),
            ("ProgramFilesFolder", "TARGETDIR", "."),
            ("INSTALLDIR", "ProgramFilesFolder", self.app_name),
            ("ProgramMenuFolder", "TARGETDIR", "."),
            ("MenuDir", "ProgramMenuFolder", self.app_name),
            ("DesktopFolder", "TARGETDIR", "."),
        ])
        
        # Create features
        msilib.add_data(db, "Feature", [
            ("Complete", None, "Complete Installation", "Complete installation of " + self.app_name, 1, 1, None, 0),
            ("MainApplication", "Complete", "Main Application", "Core application files", 1, 1, "INSTALLDIR", 0),
            ("Documentation", "Complete", "Documentation", "User guides and documentation", 1, 1, "INSTALLDIR", 0),
            ("Shortcuts", "Complete", "Shortcuts", "Desktop and Start Menu shortcuts", 1, 1, None, 0),
        ])
        
        # Add files
        self.add_files(db)
        
        # Add shortcuts
        self.add_shortcuts(db)
        
        # Add registry entries
        self.add_registry_entries(db)
        
        # Create install/uninstall sequences
        self.create_sequences(db)
        
        # Commit the database
        db.Commit()
        db.Close()
        
        print(f"✅ MSI installer created successfully: {self.msi_path}")
        
        # Get file size
        file_size = os.path.getsize(self.msi_path) / (1024 * 1024)
        print(f"📊 File size: {file_size:.1f} MB")
        
        return True
    
    def add_files(self, db):
        """Add application files to the MSI"""
        print("📁 Adding application files...")
        
        if not os.path.exists(self.source_dir):
            print(f"❌ Source directory not found: {self.source_dir}")
            return False
        
        files_data = []
        components_data = []
        feature_components_data = []
        
        file_id = 1
        
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.source_dir)
                
                # Generate unique IDs
                file_key = f"File{file_id}"
                component_key = f"Component{file_id}"
                component_guid = str(uuid.uuid4()).upper()
                
                # Determine target directory
                target_dir = "INSTALLDIR"
                if os.path.dirname(rel_path):
                    # Handle subdirectories if needed
                    pass
                
                # Add file entry
                files_data.append((
                    file_key,           # File key
                    component_key,      # Component
                    file,              # FileName
                    os.path.getsize(file_path),  # FileSize
                    None,              # Version
                    None,              # Language
                    None,              # Attributes
                    None               # Sequence
                ))
                
                # Add component entry
                components_data.append((
                    component_key,      # Component
                    component_guid,     # ComponentId
                    target_dir,         # Directory_
                    0,                 # Attributes
                    None,              # Condition
                    file_key           # KeyPath
                ))
                
                # Link component to feature
                if file.endswith('.exe'):
                    feature = "MainApplication"
                elif file.endswith(('.md', '.txt')):
                    feature = "Documentation"
                else:
                    feature = "MainApplication"
                
                feature_components_data.append((feature, component_key))
                
                file_id += 1
        
        # Add data to MSI
        msilib.add_data(db, "File", files_data)
        msilib.add_data(db, "Component", components_data)
        msilib.add_data(db, "FeatureComponents", feature_components_data)
        
        # Add media and cabinet
        msilib.add_data(db, "Media", [(1, 1, None, "#EmailBot.cab", None, None)])
        
        # Create cabinet file
        cab = msilib.CAB("EmailBot")
        
        file_id = 1
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_key = f"File{file_id}"
                cab.append(file_key, file_path)
                file_id += 1
        
        cab.commit(db)
        
        return True
    
    def add_shortcuts(self, db):
        """Add desktop and start menu shortcuts"""
        print("🔗 Adding shortcuts...")
        
        shortcuts_data = [
            # Desktop shortcut
            (
                "DesktopShortcut",          # Shortcut
                "DesktopFolder",            # Directory_
                self.app_name,              # Name
                "Component1",               # Component_
                "[INSTALLDIR]EmailAutomationBot.exe",  # Target
                None,                       # Arguments
                None,                       # Description
                None,                       # Hotkey
                "[INSTALLDIR]EmailAutomationBot.exe",  # Icon
                0,                          # IconIndex
                None,                       # ShowCmd
                "INSTALLDIR"                # WkDir
            ),
            # Start Menu shortcut
            (
                "StartMenuShortcut",        # Shortcut
                "MenuDir",                  # Directory_
                self.app_name,              # Name
                "Component1",               # Component_
                "[INSTALLDIR]EmailAutomationBot.exe",  # Target
                None,                       # Arguments
                None,                       # Description
                None,                       # Hotkey
                "[INSTALLDIR]EmailAutomationBot.exe",  # Icon
                0,                          # IconIndex
                None,                       # ShowCmd
                "INSTALLDIR"                # WkDir
            ),
            # User Guide shortcut
            (
                "UserGuideShortcut",        # Shortcut
                "MenuDir",                  # Directory_
                "User Guide",               # Name
                "Component2",               # Component_ (assuming USER_GUIDE.md is Component2)
                "[INSTALLDIR]USER_GUIDE.md", # Target
                None,                       # Arguments
                None,                       # Description
                None,                       # Hotkey
                None,                       # Icon
                0,                          # IconIndex
                None,                       # ShowCmd
                "INSTALLDIR"                # WkDir
            )
        ]
        
        msilib.add_data(db, "Shortcut", shortcuts_data)
        
        # Add shortcut components to feature
        msilib.add_data(db, "FeatureComponents", [
            ("Shortcuts", "Component1"),
            ("Shortcuts", "Component2"),
        ])
        
        return True
    
    def add_registry_entries(self, db):
        """Add registry entries for Add/Remove Programs"""
        print("📝 Adding registry entries...")
        
        registry_data = [
            # Uninstall information
            (
                "UninstallReg",
                -1,  # HKEY_LOCAL_MACHINE
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.product_code}",
                "DisplayName",
                self.app_name,
                "Component1"
            ),
            (
                "UninstallReg2",
                -1,
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.product_code}",
                "DisplayVersion",
                self.app_version,
                "Component1"
            ),
            (
                "UninstallReg3",
                -1,
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.product_code}",
                "Publisher",
                self.manufacturer,
                "Component1"
            ),
            (
                "UninstallReg4",
                -1,
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.product_code}",
                "InstallLocation",
                "[INSTALLDIR]",
                "Component1"
            ),
            (
                "UninstallReg5",
                -1,
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.product_code}",
                "UninstallString",
                f"MsiExec.exe /X{self.product_code}",
                "Component1"
            ),
            (
                "UninstallReg6",
                -1,
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.product_code}",
                "NoModify",
                "1",
                "Component1"
            ),
            (
                "UninstallReg7",
                -1,
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.product_code}",
                "NoRepair",
                "1",
                "Component1"
            ),
        ]
        
        msilib.add_data(db, "Registry", registry_data)
        return True
    
    def create_sequences(self, db):
        """Create installation and UI sequences"""
        print("⚙️ Creating installation sequences...")
        
        # Install Execute Sequence
        install_sequence = [
            ("ValidateProductID", None, 700),
            ("CostInitialize", None, 800),
            ("FileCost", None, 900),
            ("CostFinalize", None, 1000),
            ("InstallValidate", None, 1400),
            ("InstallInitialize", None, 1500),
            ("ProcessComponents", None, 1600),
            ("UnpublishFeatures", None, 1800),
            ("RemoveFiles", None, 3500),
            ("InstallFiles", None, 4000),
            ("CreateShortcuts", None, 4500),
            ("WriteRegistryValues", None, 5000),
            ("RegisterProduct", None, 6100),
            ("PublishFeatures", None, 6300),
            ("PublishProduct", None, 6400),
            ("InstallFinalize", None, 6600),
        ]
        
        msilib.add_data(db, "InstallExecuteSequence", install_sequence)
        
        # Admin Execute Sequence
        admin_sequence = [
            ("CostInitialize", None, 800),
            ("FileCost", None, 900),
            ("CostFinalize", None, 1000),
            ("InstallValidate", None, 1400),
            ("InstallInitialize", None, 1500),
            ("ProcessComponents", None, 1600),
            ("InstallAdminPackage", None, 3900),
            ("InstallFiles", None, 4000),
            ("InstallFinalize", None, 6600),
        ]
        
        msilib.add_data(db, "AdminExecuteSequence", admin_sequence)
        
        return True

def main():
    print("🚀 Email Automation Bot - MSI Installer Creator")
    print("=" * 50)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("❌ MSI installers can only be created on Windows.")
        return False
    
    # Check if source directory exists
    if not os.path.exists("release"):
        print("❌ Release directory not found. Please build the application first.")
        print("   Run: python build_windows.py")
        return False
    
    try:
        # Create MSI installer
        installer = MSIInstaller()
        success = installer.create_msi()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ MSI installer created successfully!")
            print(f"\n📁 Installer location: {installer.msi_path}")
            print(f"📊 Product Code: {installer.product_code}")
            print(f"🔄 Upgrade Code: {installer.upgrade_code}")
            print("\n🎉 MSI installer is ready for distribution!")
            
            # Show all available installers
            print("\n📦 All available installers:")
            for item in os.listdir(installer.output_dir):
                item_path = os.path.join(installer.output_dir, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path) / (1024 * 1024)
                    print(f"   - {item} ({size:.1f} MB)")
            
            return True
        else:
            print("❌ Failed to create MSI installer")
            return False
            
    except Exception as e:
        print(f"❌ Error creating MSI installer: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
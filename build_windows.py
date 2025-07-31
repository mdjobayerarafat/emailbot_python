#!/usr/bin/env python3
"""
Windows Build Script for Email Automation Bot
This script creates a standalone Windows executable using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("🔨 Building Email Automation Bot for Windows...")
    
    # Get the current directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Removed {folder}/")
    
    # Remove .spec files
    for spec_file in project_dir.glob('*.spec'):
        spec_file.unlink()
        print(f"   Removed {spec_file.name}")
    
    # Install PyInstaller if not already installed
    print("📦 Installing PyInstaller...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller>=5.13.0'], 
                      check=True, capture_output=True)
        print("   PyInstaller installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   Error installing PyInstaller: {e}")
        return False
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Create a single executable file
        '--windowed',                   # Hide console window (GUI app)
        '--name=EmailAutomationBot',    # Name of the executable
        '--icon=icon.png',              # Application icon
        '--add-data=icon.png;.',        # Include icon in the bundle
        '--add-data=ui;ui',             # Include UI modules
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=cryptography',
        '--hidden-import=APScheduler',
        '--hidden-import=sqlite3',
        '--collect-all=PyQt6',
        '--noconfirm',                  # Overwrite output directory without confirmation
        'main.py'                       # Main script
    ]
    
    print("🚀 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if the executable was created
        exe_path = project_dir / 'dist' / 'EmailAutomationBot.exe'
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"📁 Executable created: {exe_path}")
            print(f"📊 File size: {file_size:.1f} MB")
            
            # Create a release folder
            release_dir = project_dir / 'release'
            release_dir.mkdir(exist_ok=True)
            
            # Copy executable to release folder
            release_exe = release_dir / 'EmailAutomationBot.exe'
            shutil.copy2(exe_path, release_exe)
            
            # Copy additional files
            additional_files = ['README.md', 'USER_GUIDE.md', 'requirements.txt']
            for file_name in additional_files:
                src_file = project_dir / file_name
                if src_file.exists():
                    shutil.copy2(src_file, release_dir / file_name)
            
            print(f"📦 Release package created in: {release_dir}")
            print("\n🎉 Build process completed successfully!")
            print(f"\n📋 Release contents:")
            for item in release_dir.iterdir():
                if item.is_file():
                    size = item.stat().st_size / (1024 * 1024) if item.suffix == '.exe' else item.stat().st_size / 1024
                    unit = 'MB' if item.suffix == '.exe' else 'KB'
                    print(f"   - {item.name} ({size:.1f} {unit})")
            
            return True
        else:
            print("❌ Executable not found in dist folder")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n✨ You can now distribute the EmailAutomationBot.exe file!")
        print("💡 The executable is self-contained and doesn't require Python to be installed.")
    else:
        print("\n💥 Build failed. Please check the error messages above.")
        sys.exit(1)
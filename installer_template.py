
#!/usr/bin/env python3
"""
Email Automation Bot - Windows Installer
Self-extracting installer for Email Automation Bot
"""

import os
import sys
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from pathlib import Path
import subprocess
import winreg

class EmailBotInstaller:
    def __init__(self):
        self.app_name = "Email Automation Bot"
        self.app_version = "1.0.0"
        self.publisher = "MD JOBAYER ARAFAT"
        self.default_path = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), self.app_name)
        self.install_path = self.default_path
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title(f"{self.app_name} Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=self.app_name, 
                              font=("Arial", 16, "bold"), fg="white", bg="#2c3e50")
        title_label.pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Welcome message
        welcome_text = f"Welcome to the {self.app_name} Setup Wizard.\n\nThis will install {self.app_name} v{self.app_version} on your computer."
        welcome_label = tk.Label(main_frame, text=welcome_text, justify="left", wraplength=450)
        welcome_label.pack(pady=(0, 20))
        
        # Installation path
        path_frame = tk.Frame(main_frame)
        path_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(path_frame, text="Installation Directory:").pack(anchor="w")
        
        path_entry_frame = tk.Frame(path_frame)
        path_entry_frame.pack(fill="x", pady=(5, 0))
        
        self.path_var = tk.StringVar(value=self.install_path)
        self.path_entry = tk.Entry(path_entry_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(path_entry_frame, text="Browse...", command=self.browse_path)
        browse_btn.pack(side="right", padx=(5, 0))
        
        # Options
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill="x", pady=(0, 20))
        
        self.desktop_shortcut = tk.BooleanVar(value=True)
        self.start_menu = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="Create desktop shortcut", 
                      variable=self.desktop_shortcut).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Create Start Menu shortcuts", 
                      variable=self.start_menu).pack(anchor="w")
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill="x", pady=(0, 10))
        
        self.status_label = tk.Label(main_frame, text="Ready to install", fg="blue")
        self.status_label.pack()
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        self.install_btn = tk.Button(button_frame, text="Install", command=self.install, 
                                   bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
        self.install_btn.pack(side="right", padx=(5, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.root.quit)
        cancel_btn.pack(side="right")
    
    def browse_path(self):
        path = filedialog.askdirectory(initialdir=os.path.dirname(self.install_path))
        if path:
            self.install_path = os.path.join(path, self.app_name)
            self.path_var.set(self.install_path)
    
    def update_progress(self, value, status):
        self.progress['value'] = value
        self.status_label.config(text=status)
        self.root.update()
    
    def install(self):
        try:
            self.install_path = self.path_var.get()
            
            # Disable install button
            self.install_btn.config(state="disabled")
            
            # Create installation directory
            self.update_progress(10, "Creating installation directory...")
            os.makedirs(self.install_path, exist_ok=True)
            
            # Extract files
            self.update_progress(20, "Extracting application files...")
            
            # Get the embedded ZIP data (this will be replaced during build)
            zip_data = get_embedded_data()
            
            # Extract ZIP to installation directory
            import io
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                total_files = len(zf.namelist())
                for i, file in enumerate(zf.namelist()):
                    zf.extract(file, self.install_path)
                    progress = 20 + (60 * (i + 1) // total_files)
                    self.update_progress(progress, f"Extracting: {os.path.basename(file)}")
            
            # Create shortcuts
            if self.desktop_shortcut.get():
                self.update_progress(85, "Creating desktop shortcut...")
                self.create_desktop_shortcut()
            
            if self.start_menu.get():
                self.update_progress(90, "Creating Start Menu shortcuts...")
                self.create_start_menu_shortcuts()
            
            # Register in Add/Remove Programs
            self.update_progress(95, "Registering application...")
            self.register_application()
            
            self.update_progress(100, "Installation completed successfully!")
            
            # Show completion message
            result = messagebox.askyesno("Installation Complete", 
                                       f"{self.app_name} has been installed successfully!\n\n" +
                                       "Would you like to launch the application now?")
            
            if result:
                exe_path = os.path.join(self.install_path, "EmailAutomationBot.exe")
                subprocess.Popen([exe_path])
            
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Installation Error", f"Installation failed: {str(e)}")
            self.install_btn.config(state="normal")
    
    def create_desktop_shortcut(self):
        try:
            import win32com.client
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, f"{self.app_name}.lnk")
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = os.path.join(self.install_path, "EmailAutomationBot.exe")
            shortcut.WorkingDirectory = self.install_path
            shortcut.IconLocation = os.path.join(self.install_path, "EmailAutomationBot.exe")
            shortcut.save()
        except:
            pass  # Ignore if win32com is not available
    
    def create_start_menu_shortcuts(self):
        try:
            import win32com.client
            start_menu = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
            app_folder = os.path.join(start_menu, self.app_name)
            os.makedirs(app_folder, exist_ok=True)
            
            shell = win32com.client.Dispatch("WScript.Shell")
            
            # Main application shortcut
            shortcut = shell.CreateShortCut(os.path.join(app_folder, f"{self.app_name}.lnk"))
            shortcut.Targetpath = os.path.join(self.install_path, "EmailAutomationBot.exe")
            shortcut.WorkingDirectory = self.install_path
            shortcut.save()
            
            # User Guide shortcut
            guide_path = os.path.join(self.install_path, "USER_GUIDE.md")
            if os.path.exists(guide_path):
                shortcut = shell.CreateShortCut(os.path.join(app_folder, "User Guide.lnk"))
                shortcut.Targetpath = guide_path
                shortcut.save()
        except:
            pass  # Ignore if win32com is not available
    
    def register_application(self):
        try:
            # Register in Windows Add/Remove Programs
            key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}"
            
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, self.app_name)
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, self.app_version)
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, self.publisher)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, self.install_path)
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, 
                                os.path.join(self.install_path, "EmailAutomationBot.exe"))
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, 
                                f'python "{os.path.join(self.install_path, "uninstall.py")}"')
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, 220000)  # Size in KB
        except:
            pass  # Ignore registry errors (may need admin rights)
    
    def run(self):
        self.root.mainloop()

def get_embedded_data():
    # This function will be replaced with actual ZIP data during build
    return b""  # Placeholder

if __name__ == "__main__":
    try:
        installer = EmailBotInstaller()
        installer.run()
    except Exception as e:
        import tkinter.messagebox as mb
        mb.showerror("Installer Error", f"Failed to start installer: {str(e)}")
        sys.exit(1)

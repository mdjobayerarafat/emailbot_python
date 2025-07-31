import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from cryptography.fernet import Fernet
import base64
import os

class DatabaseManager:
    def __init__(self, db_path: str = "email_bot.db"):
        self.db_path = db_path
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.init_database()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Email accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER NOT NULL,
                imap_server TEXT NOT NULL,
                imap_port INTEGER NOT NULL,
                password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Email templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                is_html BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Email logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_email TEXT NOT NULL,
                recipient_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                template_id INTEGER,
                FOREIGN KEY (template_id) REFERENCES email_templates (id)
            )
        ''')
        
        # Scheduled emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template_id INTEGER NOT NULL,
                recipients TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_data TEXT NOT NULL,
                next_run TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES email_templates (id)
            )
        ''')
        
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                additional_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Attachments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                sender_email TEXT NOT NULL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                mime_type TEXT
            )
        ''')
        
        # Auto-reply rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auto_reply_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                keywords TEXT NOT NULL,
                template_id INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES email_templates (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Email Accounts Methods
    def add_email_account(self, name: str, email: str, smtp_server: str, smtp_port: int,
                         imap_server: str, imap_port: int, password: str) -> int:
        """Add new email account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        encrypted_password = self.encrypt_data(password)
        
        cursor.execute('''
            INSERT INTO email_accounts (name, email, smtp_server, smtp_port, imap_server, imap_port, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, smtp_server, smtp_port, imap_server, imap_port, encrypted_password))
        
        account_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return account_id
    
    def get_email_accounts(self) -> List[Dict]:
        """Get all email accounts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_accounts WHERE is_active = 1')
        accounts = []
        for row in cursor.fetchall():
            account = dict(row)
            account['password'] = self.decrypt_data(account['password'])
            accounts.append(account)
        
        conn.close()
        return accounts
    
    def get_active_email_account(self) -> Optional[Dict]:
        """Get the first active email account"""
        accounts = self.get_email_accounts()
        return accounts[0] if accounts else None
    
    # Email Templates Methods
    def add_email_template(self, name: str, subject: str, body: str, is_html: bool = False) -> int:
        """Add new email template"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO email_templates (name, subject, body, is_html)
            VALUES (?, ?, ?, ?)
        ''', (name, subject, body, is_html))
        
        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return template_id
    
    def get_email_templates(self) -> List[Dict]:
        """Get all email templates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_templates ORDER BY name')
        templates = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return templates
    
    def get_email_template(self, template_id: int) -> Optional[Dict]:
        """Get specific email template"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_templates WHERE id = ?', (template_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def update_email_template(self, template_id: int, name: str, subject: str, body: str, is_html: bool = False):
        """Update email template"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE email_templates 
            SET name = ?, subject = ?, body = ?, is_html = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, subject, body, is_html, template_id))
        
        conn.commit()
        conn.close()
    
    def delete_email_template(self, template_id: int):
        """Delete email template"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM email_templates WHERE id = ?', (template_id,))
        
        conn.commit()
        conn.close()
    
    # Email Logs Methods
    def add_email_log(self, sender_email: str, recipient_email: str, subject: str, 
                     body: str, status: str, error_message: str = None, template_id: int = None) -> int:
        """Add email log entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO email_logs (sender_email, recipient_email, subject, body, status, error_message, template_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sender_email, recipient_email, subject, body, status, error_message, template_id))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id
    
    def get_email_logs(self, limit: int = 100) -> List[Dict]:
        """Get email logs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT el.*, et.name as template_name 
            FROM email_logs el
            LEFT JOIN email_templates et ON el.template_id = et.id
            ORDER BY el.sent_at DESC
            LIMIT ?
        ''', (limit,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return logs
    
    # Contacts Methods
    def add_contact(self, name: str, email: str, additional_data: Dict = None) -> int:
        """Add new contact"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        additional_json = json.dumps(additional_data) if additional_data else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO contacts (name, email, additional_data)
            VALUES (?, ?, ?)
        ''', (name, email, additional_json))
        
        contact_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return contact_id
    
    def get_contacts(self) -> List[Dict]:
        """Get all contacts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM contacts ORDER BY name')
        contacts = []
        for row in cursor.fetchall():
            contact = dict(row)
            if contact['additional_data']:
                contact['additional_data'] = json.loads(contact['additional_data'])
            contacts.append(contact)
        
        conn.close()
        return contacts
    
    # Scheduled Emails Methods
    def add_scheduled_email(self, name: str, template_id: int, recipients: List[str], 
                           schedule_type: str, schedule_data: Dict, next_run: datetime) -> int:
        """Add scheduled email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        recipients_json = json.dumps(recipients)
        schedule_data_json = json.dumps(schedule_data)
        
        cursor.execute('''
            INSERT INTO scheduled_emails (name, template_id, recipients, schedule_type, schedule_data, next_run)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, template_id, recipients_json, schedule_type, schedule_data_json, next_run))
        
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return schedule_id
    
    def get_scheduled_emails(self) -> List[Dict]:
        """Get all scheduled emails"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT se.*, et.name as template_name, et.subject as template_subject
            FROM scheduled_emails se
            JOIN email_templates et ON se.template_id = et.id
            WHERE se.is_active = 1
            ORDER BY se.next_run
        ''')
        
        schedules = []
        for row in cursor.fetchall():
            schedule = dict(row)
            schedule['recipients'] = json.loads(schedule['recipients'])
            schedule['schedule_data'] = json.loads(schedule['schedule_data'])
            schedules.append(schedule)
        
        conn.close()
        return schedules
    
    # Auto-reply Rules Methods
    def add_auto_reply_rule(self, name: str, keywords: List[str], template_id: int) -> int:
        """Add auto-reply rule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        keywords_json = json.dumps(keywords)
        
        cursor.execute('''
            INSERT INTO auto_reply_rules (name, keywords, template_id)
            VALUES (?, ?, ?)
        ''', (name, keywords_json, template_id))
        
        rule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return rule_id
    
    def get_auto_reply_rules(self) -> List[Dict]:
        """Get all active auto-reply rules"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT arr.*, et.name as template_name, et.subject as template_subject
            FROM auto_reply_rules arr
            JOIN email_templates et ON arr.template_id = et.id
            WHERE arr.is_active = 1
        ''')
        
        rules = []
        for row in cursor.fetchall():
            rule = dict(row)
            rule['keywords'] = json.loads(rule['keywords'])
            rules.append(rule)
        
        conn.close()
        return rules
    
    # Attachments Methods
    def add_attachment(self, filename: str, file_path: str, sender_email: str, 
                      file_size: int, mime_type: str) -> int:
        """Add attachment record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO attachments (filename, file_path, sender_email, file_size, mime_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, file_path, sender_email, file_size, mime_type))
        
        attachment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return attachment_id
    
    def get_attachments(self, limit: int = 100) -> List[Dict]:
        """Get attachment records"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM attachments 
            ORDER BY received_at DESC 
            LIMIT ?
        ''', (limit,))
        
        attachments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return attachments
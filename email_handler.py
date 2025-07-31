import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
import os
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from database import DatabaseManager
import threading
import time

class EmailHandler:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        
    def test_connection(self, email_config: Dict) -> Tuple[bool, str]:
        """Test SMTP and IMAP connections"""
        try:
            # Test SMTP
            smtp_server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            smtp_server.starttls()
            smtp_server.login(email_config['email'], email_config['password'])
            smtp_server.quit()
            
            # Test IMAP
            imap_server = imaplib.IMAP4_SSL(email_config['imap_server'], email_config['imap_port'])
            imap_server.login(email_config['email'], email_config['password'])
            imap_server.logout()
            
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
    
    def send_email(self, sender_config: Dict, recipient: str, subject: str, 
                   body: str, is_html: bool = False, attachments: List[str] = None,
                   template_id: int = None) -> Tuple[bool, str]:
        """Send email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_config['email']
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(sender_config['smtp_server'], sender_config['smtp_port'])
            server.starttls()
            server.login(sender_config['email'], sender_config['password'])
            text = msg.as_string()
            server.sendmail(sender_config['email'], recipient, text)
            server.quit()
            
            # Log success
            self.db_manager.add_email_log(
                sender_email=sender_config['email'],
                recipient_email=recipient,
                subject=subject,
                body=body,
                status='sent',
                template_id=template_id
            )
            
            return True, "Email sent successfully"
            
        except Exception as e:
            error_msg = str(e)
            # Log failure
            self.db_manager.add_email_log(
                sender_email=sender_config['email'],
                recipient_email=recipient,
                subject=subject,
                body=body,
                status='failed',
                error_message=error_msg,
                template_id=template_id
            )
            
            return False, error_msg
    
    def send_batch_emails(self, sender_config: Dict, recipients: List[Dict], 
                         template: Dict, attachments: List[str] = None) -> Dict:
        """Send batch emails with personalization"""
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        for recipient in recipients:
            try:
                # Personalize subject and body
                personalized_subject = self._personalize_text(template['subject'], recipient)
                personalized_body = self._personalize_text(template['body'], recipient)
                
                success, message = self.send_email(
                    sender_config=sender_config,
                    recipient=recipient['email'],
                    subject=personalized_subject,
                    body=personalized_body,
                    is_html=template['is_html'],
                    attachments=attachments,
                    template_id=template['id']
                )
                
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{recipient['email']}: {message}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"{recipient['email']}: {str(e)}")
        
        return results
    
    def _personalize_text(self, text: str, recipient: Dict) -> str:
        """Replace placeholders with recipient data"""
        personalized = text
        
        # Replace common placeholders
        for key, value in recipient.items():
            placeholder = f"{{{key}}}"
            personalized = personalized.replace(placeholder, str(value))
        
        return personalized
    
    def start_inbox_monitoring(self, email_config: Dict, check_interval: int = 60):
        """Start monitoring inbox for new emails"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_inbox,
            args=(email_config, check_interval),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Inbox monitoring started")
    
    def stop_inbox_monitoring(self):
        """Stop monitoring inbox"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Inbox monitoring stopped")
    
    def _monitor_inbox(self, email_config: Dict, check_interval: int):
        """Monitor inbox for new emails and auto-reply"""
        last_check = datetime.now()
        
        while self.monitoring:
            try:
                # Connect to IMAP
                imap = imaplib.IMAP4_SSL(email_config['imap_server'], email_config['imap_port'])
                imap.login(email_config['email'], email_config['password'])
                imap.select('INBOX')
                
                # Search for unread emails since last check
                search_criteria = f'(UNSEEN SINCE "{last_check.strftime("%d-%b-%Y")}")'
                status, messages = imap.search(None, search_criteria)
                
                if status == 'OK' and messages[0]:
                    email_ids = messages[0].split()
                    
                    for email_id in email_ids:
                        try:
                            # Fetch email
                            status, msg_data = imap.fetch(email_id, '(RFC822)')
                            if status == 'OK':
                                email_message = email.message_from_bytes(msg_data[0][1])
                                
                                # Process email
                                self._process_incoming_email(email_message, email_config)
                                
                        except Exception as e:
                            self.logger.error(f"Error processing email {email_id}: {e}")
                
                imap.logout()
                last_check = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Error monitoring inbox: {e}")
            
            # Wait before next check
            time.sleep(check_interval)
    
    def _process_incoming_email(self, email_message, sender_config: Dict):
        """Process incoming email for auto-reply and attachments"""
        try:
            # Extract email details
            sender = email_message.get('From', '')
            subject = email_message.get('Subject', '')
            
            # Get email body
            body = self._extract_email_body(email_message)
            
            # Check for auto-reply rules
            auto_reply_rules = self.db_manager.get_auto_reply_rules()
            
            for rule in auto_reply_rules:
                if self._check_keywords(body + ' ' + subject, rule['keywords']):
                    # Get template
                    template = self.db_manager.get_email_template(rule['template_id'])
                    if template:
                        # Send auto-reply
                        reply_subject = f"Re: {subject}"
                        self.send_email(
                            sender_config=sender_config,
                            recipient=sender,
                            subject=reply_subject,
                            body=template['body'],
                            is_html=template['is_html'],
                            template_id=template['id']
                        )
                        self.logger.info(f"Auto-reply sent to {sender} using rule '{rule['name']}'")
                        break
            
            # Process attachments
            self._process_attachments(email_message, sender)
            
        except Exception as e:
            self.logger.error(f"Error processing incoming email: {e}")
    
    def _extract_email_body(self, email_message) -> str:
        """Extract text body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return body
    
    def _check_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if any keywords are present in text"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    def _process_attachments(self, email_message, sender: str):
        """Process and save email attachments"""
        attachments_dir = "attachments"
        os.makedirs(attachments_dir, exist_ok=True)
        
        for part in email_message.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    # Clean filename
                    filename = re.sub(r'[^\w\s.-]', '', filename)
                    
                    # Create unique filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(attachments_dir, unique_filename)
                    
                    # Save attachment
                    with open(file_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    
                    # Get file info
                    file_size = os.path.getsize(file_path)
                    mime_type = part.get_content_type()
                    
                    # Save to database
                    self.db_manager.add_attachment(
                        filename=filename,
                        file_path=file_path,
                        sender_email=sender,
                        file_size=file_size,
                        mime_type=mime_type
                    )
                    
                    self.logger.info(f"Attachment saved: {filename} from {sender}")
    
    def get_inbox_emails(self, email_config: Dict, limit: int = 50) -> List[Dict]:
        """Get recent emails from inbox"""
        emails = []
        
        try:
            # Connect to IMAP
            imap = imaplib.IMAP4_SSL(email_config['imap_server'], email_config['imap_port'])
            imap.login(email_config['email'], email_config['password'])
            imap.select('INBOX')
            
            # Search for recent emails
            status, messages = imap.search(None, 'ALL')
            
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()[-limit:]  # Get last N emails
                
                for email_id in reversed(email_ids):  # Newest first
                    try:
                        status, msg_data = imap.fetch(email_id, '(RFC822)')
                        if status == 'OK':
                            email_message = email.message_from_bytes(msg_data[0][1])
                            
                            emails.append({
                                'id': email_id.decode(),
                                'from': email_message.get('From', ''),
                                'subject': email_message.get('Subject', ''),
                                'date': email_message.get('Date', ''),
                                'body': self._extract_email_body(email_message)[:200] + '...'  # Preview
                            })
                            
                    except Exception as e:
                        self.logger.error(f"Error fetching email {email_id}: {e}")
            
            imap.logout()
            
        except Exception as e:
            self.logger.error(f"Error getting inbox emails: {e}")
        
        return emails
    
    def import_contacts_from_csv(self, csv_file_path: str) -> Tuple[int, List[str]]:
        """Import contacts from CSV file"""
        import csv
        
        imported_count = 0
        errors = []
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Required fields
                        name = row.get('name', '').strip()
                        email = row.get('email', '').strip()
                        
                        if not name or not email:
                            errors.append(f"Row {row_num}: Missing name or email")
                            continue
                        
                        # Validate email format
                        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                            errors.append(f"Row {row_num}: Invalid email format: {email}")
                            continue
                        
                        # Additional data
                        additional_data = {k: v for k, v in row.items() if k not in ['name', 'email']}
                        
                        # Add to database
                        self.db_manager.add_contact(name, email, additional_data)
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
        
        except Exception as e:
            errors.append(f"File error: {str(e)}")
        
        return imported_count, errors
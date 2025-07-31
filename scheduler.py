from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional
from database import DatabaseManager
from email_handler import EmailHandler

class EmailScheduler:
    def __init__(self, db_manager: DatabaseManager, email_handler: EmailHandler):
        self.db_manager = db_manager
        self.email_handler = email_handler
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)
        self.scheduler.start()
        self._load_scheduled_emails()
    
    def _load_scheduled_emails(self):
        """Load scheduled emails from database and add to scheduler"""
        try:
            scheduled_emails = self.db_manager.get_scheduled_emails()
            
            for schedule in scheduled_emails:
                self._add_job_to_scheduler(schedule)
                
            self.logger.info(f"Loaded {len(scheduled_emails)} scheduled emails")
            
        except Exception as e:
            self.logger.error(f"Error loading scheduled emails: {e}")
    
    def add_scheduled_email(self, name: str, template_id: int, recipients: List[str],
                           schedule_type: str, schedule_data: Dict) -> int:
        """Add new scheduled email"""
        try:
            # Calculate next run time
            next_run = self._calculate_next_run(schedule_type, schedule_data)
            
            # Save to database
            schedule_id = self.db_manager.add_scheduled_email(
                name=name,
                template_id=template_id,
                recipients=recipients,
                schedule_type=schedule_type,
                schedule_data=schedule_data,
                next_run=next_run
            )
            
            # Add to scheduler
            schedule = {
                'id': schedule_id,
                'name': name,
                'template_id': template_id,
                'recipients': recipients,
                'schedule_type': schedule_type,
                'schedule_data': schedule_data,
                'next_run': next_run
            }
            
            self._add_job_to_scheduler(schedule)
            
            self.logger.info(f"Scheduled email '{name}' added with ID {schedule_id}")
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"Error adding scheduled email: {e}")
            raise
    
    def _calculate_next_run(self, schedule_type: str, schedule_data: Dict) -> datetime:
        """Calculate next run time based on schedule type and data"""
        now = datetime.now()
        
        if schedule_type == 'once':
            return datetime.fromisoformat(schedule_data['datetime'])
        
        elif schedule_type == 'daily':
            time_str = schedule_data['time']  # Format: "HH:MM"
            hour, minute = map(int, time_str.split(':'))
            
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            
            return next_run
        
        elif schedule_type == 'weekly':
            time_str = schedule_data['time']  # Format: "HH:MM"
            weekday = schedule_data['weekday']  # 0=Monday, 6=Sunday
            hour, minute = map(int, time_str.split(':'))
            
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            return next_run
        
        elif schedule_type == 'monthly':
            time_str = schedule_data['time']  # Format: "HH:MM"
            day = schedule_data['day']  # Day of month (1-31)
            hour, minute = map(int, time_str.split(':'))
            
            # Try current month first
            try:
                next_run = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    # Move to next month
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
            except ValueError:
                # Day doesn't exist in current month, move to next month
                if now.month == 12:
                    next_run = datetime(now.year + 1, 1, day, hour, minute)
                else:
                    next_run = datetime(now.year, now.month + 1, day, hour, minute)
            
            return next_run
        
        elif schedule_type == 'interval':
            interval_type = schedule_data['interval_type']  # 'minutes', 'hours', 'days'
            interval_value = schedule_data['interval_value']
            
            if interval_type == 'minutes':
                return now + timedelta(minutes=interval_value)
            elif interval_type == 'hours':
                return now + timedelta(hours=interval_value)
            elif interval_type == 'days':
                return now + timedelta(days=interval_value)
        
        raise ValueError(f"Unknown schedule type: {schedule_type}")
    
    def _add_job_to_scheduler(self, schedule: Dict):
        """Add job to APScheduler"""
        try:
            job_id = f"email_schedule_{schedule['id']}"
            
            # Remove existing job if it exists
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Create trigger based on schedule type
            trigger = self._create_trigger(schedule['schedule_type'], schedule['schedule_data'])
            
            # Add job
            self.scheduler.add_job(
                func=self._execute_scheduled_email,
                trigger=trigger,
                id=job_id,
                args=[schedule['id']],
                replace_existing=True
            )
            
            self.logger.info(f"Job added to scheduler: {job_id}")
            
        except Exception as e:
            self.logger.error(f"Error adding job to scheduler: {e}")
    
    def _create_trigger(self, schedule_type: str, schedule_data: Dict):
        """Create APScheduler trigger based on schedule type"""
        if schedule_type == 'once':
            run_date = datetime.fromisoformat(schedule_data['datetime'])
            return DateTrigger(run_date=run_date)
        
        elif schedule_type == 'daily':
            time_str = schedule_data['time']
            hour, minute = map(int, time_str.split(':'))
            return CronTrigger(hour=hour, minute=minute)
        
        elif schedule_type == 'weekly':
            time_str = schedule_data['time']
            weekday = schedule_data['weekday']
            hour, minute = map(int, time_str.split(':'))
            return CronTrigger(day_of_week=weekday, hour=hour, minute=minute)
        
        elif schedule_type == 'monthly':
            time_str = schedule_data['time']
            day = schedule_data['day']
            hour, minute = map(int, time_str.split(':'))
            return CronTrigger(day=day, hour=hour, minute=minute)
        
        elif schedule_type == 'interval':
            interval_type = schedule_data['interval_type']
            interval_value = schedule_data['interval_value']
            
            if interval_type == 'minutes':
                return IntervalTrigger(minutes=interval_value)
            elif interval_type == 'hours':
                return IntervalTrigger(hours=interval_value)
            elif interval_type == 'days':
                return IntervalTrigger(days=interval_value)
        
        raise ValueError(f"Unknown schedule type: {schedule_type}")
    
    def _execute_scheduled_email(self, schedule_id: int):
        """Execute scheduled email"""
        try:
            # Get schedule details from database
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT se.*, et.subject, et.body, et.is_html
                FROM scheduled_emails se
                JOIN email_templates et ON se.template_id = et.id
                WHERE se.id = ? AND se.is_active = 1
            ''', (schedule_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                self.logger.warning(f"Scheduled email {schedule_id} not found or inactive")
                return
            
            schedule = dict(row)
            recipients = json.loads(schedule['recipients'])
            schedule_data = json.loads(schedule['schedule_data'])
            
            # Get sender configuration
            sender_config = self.db_manager.get_active_email_account()
            if not sender_config:
                self.logger.error("No active email account found")
                return
            
            # Prepare template
            template = {
                'id': schedule['template_id'],
                'subject': schedule['subject'],
                'body': schedule['body'],
                'is_html': schedule['is_html']
            }
            
            # Convert recipients to required format
            recipient_list = []
            for recipient in recipients:
                if isinstance(recipient, str):
                    # Simple email string
                    recipient_list.append({'email': recipient, 'name': recipient})
                else:
                    # Dictionary with email and other data
                    recipient_list.append(recipient)
            
            # Send batch emails
            results = self.email_handler.send_batch_emails(
                sender_config=sender_config,
                recipients=recipient_list,
                template=template
            )
            
            self.logger.info(
                f"Scheduled email '{schedule['name']}' executed: "
                f"{results['sent']} sent, {results['failed']} failed"
            )
            
            # Update next run time for recurring schedules
            if schedule['schedule_type'] != 'once':
                next_run = self._calculate_next_run(schedule['schedule_type'], schedule_data)
                
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE scheduled_emails SET next_run = ? WHERE id = ?',
                    (next_run, schedule_id)
                )
                conn.commit()
                conn.close()
            else:
                # Deactivate one-time schedules
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE scheduled_emails SET is_active = 0 WHERE id = ?',
                    (schedule_id,)
                )
                conn.commit()
                conn.close()
                
                # Remove from scheduler
                job_id = f"email_schedule_{schedule_id}"
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)
            
        except Exception as e:
            self.logger.error(f"Error executing scheduled email {schedule_id}: {e}")
    
    def remove_scheduled_email(self, schedule_id: int):
        """Remove scheduled email"""
        try:
            # Remove from scheduler
            job_id = f"email_schedule_{schedule_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Deactivate in database
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE scheduled_emails SET is_active = 0 WHERE id = ?',
                (schedule_id,)
            )
            conn.commit()
            conn.close()
            
            self.logger.info(f"Scheduled email {schedule_id} removed")
            
        except Exception as e:
            self.logger.error(f"Error removing scheduled email {schedule_id}: {e}")
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Get list of scheduled jobs with next run times"""
        jobs = []
        
        try:
            scheduled_emails = self.db_manager.get_scheduled_emails()
            
            for schedule in scheduled_emails:
                job_id = f"email_schedule_{schedule['id']}"
                job = self.scheduler.get_job(job_id)
                
                job_info = {
                    'id': schedule['id'],
                    'name': schedule['name'],
                    'template_name': schedule['template_name'],
                    'template_subject': schedule['template_subject'],
                    'schedule_type': schedule['schedule_type'],
                    'recipients_count': len(schedule['recipients']),
                    'next_run': schedule['next_run'],
                    'is_active': schedule['is_active'],
                    'scheduler_status': 'scheduled' if job else 'not_scheduled'
                }
                
                if job:
                    job_info['next_run_scheduler'] = job.next_run_time
                
                jobs.append(job_info)
        
        except Exception as e:
            self.logger.error(f"Error getting scheduled jobs: {e}")
        
        return jobs
    
    def pause_scheduled_email(self, schedule_id: int):
        """Pause scheduled email"""
        try:
            job_id = f"email_schedule_{schedule_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.pause_job(job_id)
                self.logger.info(f"Scheduled email {schedule_id} paused")
        except Exception as e:
            self.logger.error(f"Error pausing scheduled email {schedule_id}: {e}")
    
    def resume_scheduled_email(self, schedule_id: int):
        """Resume scheduled email"""
        try:
            job_id = f"email_schedule_{schedule_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.resume_job(job_id)
                self.logger.info(f"Scheduled email {schedule_id} resumed")
        except Exception as e:
            self.logger.error(f"Error resuming scheduled email {schedule_id}: {e}")
    
    def shutdown(self):
        """Shutdown scheduler"""
        try:
            self.scheduler.shutdown(wait=False)
            self.logger.info("Email scheduler shutdown")
        except Exception as e:
            self.logger.error(f"Error shutting down scheduler: {e}")
    
    def get_schedule_types(self) -> Dict[str, Dict]:
        """Get available schedule types and their configurations"""
        return {
            'once': {
                'name': 'One Time',
                'description': 'Send email once at specified date and time',
                'fields': ['datetime']
            },
            'daily': {
                'name': 'Daily',
                'description': 'Send email daily at specified time',
                'fields': ['time']
            },
            'weekly': {
                'name': 'Weekly',
                'description': 'Send email weekly on specified day and time',
                'fields': ['weekday', 'time']
            },
            'monthly': {
                'name': 'Monthly',
                'description': 'Send email monthly on specified day and time',
                'fields': ['day', 'time']
            },
            'interval': {
                'name': 'Interval',
                'description': 'Send email at regular intervals',
                'fields': ['interval_type', 'interval_value']
            }
        }
# Email Automation Bot - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Application Overview](#application-overview)
4. [Dashboard Panel](#dashboard-panel)
5. [Inbox Monitor Panel](#inbox-monitor-panel)
6. [Email Sender Panel](#email-sender-panel)
7. [Scheduler Panel](#scheduler-panel)
8. [Templates Panel](#templates-panel)
9. [Logs Panel](#logs-panel)
10. [Settings Panel](#settings-panel)
11. [Troubleshooting](#troubleshooting)
12. [Tips and Best Practices](#tips-and-best-practices)

## Introduction

The Email Automation Bot is a comprehensive desktop application designed to automate email management tasks. It provides features for monitoring incoming emails, sending automated responses, scheduling email campaigns, managing email templates, and tracking all activities through detailed logging.

### Key Features
- **Automated Email Monitoring**: Monitor your inbox and automatically respond to emails based on custom rules
- **Email Scheduling**: Schedule emails to be sent at specific times or intervals
- **Template Management**: Create and manage reusable email templates with variables
- **Comprehensive Logging**: Track all email activities and system events
- **User-Friendly Interface**: Intuitive design with organized panels for different functions

## Getting Started

### System Requirements
- Windows 10 or later
- Python 3.8 or higher
- Internet connection for email operations

### Installation
1. Download and extract the application files
2. Install required dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

### First-Time Setup
1. **Launch the Application**: Double-click `main.py` or run `python main.py`
2. **Login/Registration**: Create a new account or login with existing credentials
3. **Email Configuration**: Configure your email account in the Settings panel
4. **Test Connection**: Verify your email settings work correctly

## Application Overview

The application features a sidebar navigation with the following panels:

- **📊 Dashboard**: Overview of system status and quick actions
- **👁️ Inbox Monitor**: Monitor incoming emails and set up auto-reply rules
- **📤 Email Sender**: Send individual emails or bulk campaigns
- **⏰ Scheduler**: Schedule emails for future delivery
- **📧 Templates**: Create and manage email templates
- **📋 Logs**: View application logs and email activity
- **⚙️ Settings**: Configure application and email settings

## Dashboard Panel

The Dashboard provides an overview of your email automation system.

### Features
- **System Status Indicators**: Shows the status of email connection, monitoring, and scheduler
- **Quick Statistics**: Displays counts of recent emails, active schedules, and templates
- **Control Buttons**: Start/stop monitoring and scheduler services
- **Recent Activity**: Shows the latest email activities

### How to Use
1. **Check System Status**: Green indicators show everything is working properly
2. **Start Services**: Click "Start Monitoring" to begin inbox monitoring
3. **View Statistics**: Monitor your email automation metrics
4. **Quick Actions**: Access frequently used functions directly from the dashboard

## Inbox Monitor Panel

Monitor your inbox and automatically respond to incoming emails based on custom rules.

### Setting Up Auto-Reply Rules

1. **Create a New Rule**:
   - Click "Add Rule" button
   - Enter a descriptive name for the rule
   - Set keywords to trigger the rule (e.g., "support", "help")
   - Choose or create a template for the auto-reply
   - Set priority (High, Medium, Low)
   - Enable/disable the rule as needed

2. **Rule Configuration Options**:
   - **Keywords**: Words that trigger the rule when found in incoming emails
   - **Template**: Pre-written response template to send
   - **Priority**: Determines which rule applies when multiple rules match
   - **Active Status**: Enable or disable rules without deleting them

3. **Managing Rules**:
   - **Edit**: Double-click any rule to modify its settings
   - **Delete**: Select a rule and click "Delete" to remove it
   - **Toggle**: Use the status column to quickly enable/disable rules

### Monitoring Status
- **Green Status**: Monitoring is active and working
- **Red Status**: Monitoring is stopped or has issues
- **Email Count**: Shows number of recent emails processed

### Recent Emails View
- View incoming emails in real-time
- See which rules were triggered
- Check auto-reply status for each email
- Click on emails to view full content

## Email Sender Panel

Send individual emails or bulk email campaigns.

### Sending Individual Emails

1. **Compose Email**:
   - Enter recipient email address
   - Add subject line
   - Write your message in the body field
   - Optionally select a template to pre-fill content

2. **Using Templates**:
   - Select a template from the dropdown
   - Template content will populate the subject and body
   - Customize the content as needed
   - Variables in templates (like {name}) will be replaced

3. **Send Options**:
   - **Send Now**: Immediately send the email
   - **Schedule**: Set a future date/time for delivery
   - **Save as Draft**: Save for later editing

### Bulk Email Campaigns

1. **Recipient Management**:
   - Import recipients from CSV file
   - Manually add recipients one by one
   - Manage recipient lists for different campaigns

2. **Campaign Setup**:
   - Choose email template
   - Set campaign name and description
   - Configure sending schedule
   - Review recipient list

3. **Sending**:
   - Preview emails before sending
   - Monitor sending progress
   - View delivery reports

## Scheduler Panel

Schedule emails to be sent automatically at specific times or intervals.

### Creating Scheduled Emails

1. **Basic Information**:
   - **Name**: Descriptive name for the schedule
   - **Template**: Choose which email template to use
   - **Recipients**: Add email addresses or import from file

2. **Schedule Configuration**:
   - **One-time**: Send once at a specific date and time
   - **Recurring**: Send repeatedly at set intervals
   - **Daily**: Send every day at specified time
   - **Weekly**: Send on specific days of the week
   - **Monthly**: Send on specific dates each month

3. **Advanced Options**:
   - **End Date**: Set when recurring schedules should stop
   - **Maximum Sends**: Limit total number of emails sent
   - **Time Zone**: Configure for different time zones

### Managing Schedules

- **View All Schedules**: See list of all created schedules
- **Schedule Status**: Active schedules show green, inactive show red
- **Edit Schedules**: Double-click to modify schedule settings
- **Run Now**: Manually trigger a schedule immediately
- **Enable/Disable**: Toggle schedules on/off without deleting

### Schedule Details
- **Next Run Time**: When the schedule will next execute
- **Last Run**: When it was last executed
- **Success Rate**: Percentage of successful email deliveries
- **Recipient Count**: Number of people receiving emails

## Templates Panel

Create and manage reusable email templates with dynamic content.

### Creating Templates

1. **Basic Information**:
   - **Name**: Unique name for the template
   - **Category**: Organize templates by type (e.g., "Marketing", "Support")
   - **Description**: Brief description of template purpose

2. **Content Creation**:
   - **Subject Line**: Email subject with optional variables
   - **Body Content**: Main email content
   - **HTML Support**: Enable rich formatting and HTML content
   - **Variables**: Use placeholders like {name}, {company}, {date}

3. **Template Variables**:
   - **{name}**: Recipient's name
   - **{email}**: Recipient's email address
   - **{company}**: Recipient's company
   - **{date}**: Current date
   - **{time}**: Current time
   - **Custom Variables**: Define your own variables

### Template Management

- **Search and Filter**: Find templates by name, category, or content
- **Preview**: See how templates look with sample data
- **Duplicate**: Copy existing templates to create variations
- **Export/Import**: Share templates between installations
- **Usage Statistics**: See how often templates are used

### HTML Templates

1. **Enable HTML Mode**: Check the "HTML Content" option
2. **HTML Editor**: Use built-in tools for formatting
3. **Insert Elements**: Add links, images, and formatting
4. **Preview**: See rendered HTML output
5. **Variables in HTML**: Use variables within HTML tags

## Logs Panel

Monitor application activity and troubleshoot issues.

### Log Categories

- **Email Activity**: All sent and received emails
- **System Events**: Application startup, shutdown, errors
- **Scheduler Activity**: Scheduled email executions
- **Auto-Reply Activity**: Automatic responses triggered
- **Error Logs**: Issues and error messages

### Using the Logs

1. **Filter Logs**:
   - **Date Range**: View logs from specific time periods
   - **Log Level**: Filter by Info, Warning, Error
   - **Category**: Show only specific types of activities
   - **Search**: Find specific log entries

2. **Log Details**:
   - **Timestamp**: Exact time of each event
   - **Level**: Severity of the log entry
   - **Message**: Detailed description of the event
   - **Context**: Additional information about the event

3. **Export Logs**:
   - Save logs to file for external analysis
   - Choose date ranges and categories to export
   - Multiple export formats available

## Settings Panel

Configure application behavior and email account settings.

### Email Account Configuration

1. **SMTP Settings** (for sending emails):
   - **Server**: SMTP server address (e.g., smtp.gmail.com)
   - **Port**: Usually 587 for TLS or 465 for SSL
   - **Security**: Choose TLS, SSL, or None
   - **Username**: Your email address
   - **Password**: Your email password or app password

2. **IMAP Settings** (for receiving emails):
   - **Server**: IMAP server address (e.g., imap.gmail.com)
   - **Port**: Usually 993 for SSL or 143 for non-SSL
   - **Security**: Choose SSL/TLS or None
   - **Username**: Your email address
   - **Password**: Your email password or app password

3. **Common Email Providers**:
   - **Gmail**: smtp.gmail.com:587 (SMTP), imap.gmail.com:993 (IMAP)
   - **Outlook**: smtp-mail.outlook.com:587 (SMTP), outlook.office365.com:993 (IMAP)
   - **Yahoo**: smtp.mail.yahoo.com:587 (SMTP), imap.mail.yahoo.com:993 (IMAP)

### Application Settings

1. **General Settings**:
   - **Auto-start**: Launch application when Windows starts
   - **Minimize to Tray**: Hide application in system tray
   - **Check Interval**: How often to check for new emails
   - **Language**: Application interface language

2. **Notification Settings**:
   - **Email Notifications**: Get notified of new emails
   - **Error Notifications**: Alert on system errors
   - **Sound Alerts**: Audio notifications for events
   - **Desktop Notifications**: Windows toast notifications

3. **Security Settings**:
   - **Password Protection**: Require password to access application
   - **Session Timeout**: Auto-logout after inactivity
   - **Encryption**: Encrypt stored email credentials
   - **Backup Settings**: Automatic backup of configuration

### Backup and Restore

1. **Create Backup**:
   - Export all settings, templates, and schedules
   - Save to secure location
   - Include or exclude email credentials

2. **Restore from Backup**:
   - Import previously saved configuration
   - Selective restore of specific components
   - Merge with existing settings or replace completely

## Troubleshooting

### Common Issues

#### Email Connection Problems
- **Symptoms**: Cannot send or receive emails
- **Solutions**:
  - Verify SMTP/IMAP settings are correct
  - Check internet connection
  - Ensure email provider allows third-party apps
  - Use app-specific passwords for Gmail/Outlook
  - Check firewall and antivirus settings

#### Authentication Errors
- **Symptoms**: "Login failed" or "Authentication error"
- **Solutions**:
  - Verify username and password
  - Enable "Less secure app access" (Gmail)
  - Use app passwords instead of regular passwords
  - Check two-factor authentication settings

#### Scheduler Not Working
- **Symptoms**: Scheduled emails not sending
- **Solutions**:
  - Ensure scheduler is started in Dashboard
  - Check schedule configuration
  - Verify email templates exist
  - Check system time and time zone
  - Review logs for error messages

#### Auto-Reply Not Triggering
- **Symptoms**: Incoming emails not generating automatic responses
- **Solutions**:
  - Verify inbox monitoring is active
  - Check auto-reply rule keywords
  - Ensure rules are enabled
  - Verify email templates are valid
  - Check IMAP connection status

### Getting Help

1. **Check Logs**: Always review the Logs panel for error messages
2. **Test Connections**: Use the "Test" buttons in Settings to verify email configuration
3. **Review Configuration**: Double-check all settings match your email provider's requirements
4. **Restart Application**: Sometimes a restart resolves temporary issues

## Tips and Best Practices

### Email Security
- Use app-specific passwords instead of your main email password
- Enable two-factor authentication on your email account
- Regularly update your email passwords
- Keep the application updated to the latest version

### Template Best Practices
- Use clear, descriptive names for templates
- Test templates with sample data before using
- Keep templates organized with categories
- Include unsubscribe links in marketing emails
- Use variables to personalize content

### Scheduling Best Practices
- Test schedules with small recipient lists first
- Avoid sending emails during off-hours unless necessary
- Monitor delivery rates and adjust timing as needed
- Use appropriate intervals to avoid being marked as spam
- Keep recipient lists updated and clean

### Performance Optimization
- Regularly clean up old logs to save disk space
- Limit the number of active auto-reply rules
- Use efficient keywords in auto-reply rules
- Monitor system resources during bulk email campaigns
- Schedule large campaigns during low-usage periods

### Compliance and Ethics
- Always obtain consent before adding people to email lists
- Include clear unsubscribe options in all marketing emails
- Respect email frequency preferences
- Follow local laws regarding email marketing (CAN-SPAM, GDPR, etc.)
- Maintain accurate and up-to-date recipient information

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Support**: Check the Logs panel for troubleshooting information

For additional help or feature requests, please refer to the application's built-in help system or contact support through the Settings panel.
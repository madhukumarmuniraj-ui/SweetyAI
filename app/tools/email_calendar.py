"""
SweetyAI Email & Calendar Integration
SMTP/IMAP, Google Calendar, Outlook, meeting scheduling
"""

import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

# Google Calendar API
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    print("[Email/Calendar] Google Calendar API not available. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


# =============================================================================
# EMAIL SENDING (SMTP)
# =============================================================================

class EmailClient:
    """Email client for sending emails via SMTP."""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        cc_addresses: List[str] = None,
        bcc_addresses: List[str] = None,
        attachments: List[str] = None,
        html: bool = False
    ) -> str:
        """Send an email with optional attachments."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = subject

            if cc_addresses:
                msg['Cc'] = ', '.join(cc_addresses)

            # Attach body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))

            # Attach files
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={os.path.basename(filepath)}'
                            )
                            msg.attach(part)

            # Send email
            all_recipients = to_addresses + (cc_addresses or []) + (bcc_addresses or [])

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return f"Email sent to {len(all_recipients)} recipient(s)"

        except Exception as e:
            return f"Error sending email: {e}"


# =============================================================================
# EMAIL READING (IMAP)
# =============================================================================

class IMAPClient:
    """Email client for reading emails via IMAP."""

    def __init__(self, imap_server: str, username: str, password: str):
        self.imap_server = imap_server
        self.username = username
        self.password = password

    def fetch_emails(
        self,
        mailbox: str = 'INBOX',
        limit: int = 10,
        unread_only: bool = False,
        since_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch emails from mailbox."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select(mailbox)

            # Build search criteria
            search_criteria = []
            if unread_only:
                search_criteria.append('UNSEEN')
            if since_date:
                date_str = since_date.strftime('%d-%b-%Y')
                search_criteria.append(f'SINCE {date_str}')

            search_query = ' '.join(search_criteria) if search_criteria else 'ALL'

            # Search for emails
            _, message_numbers = mail.search(None, search_query)

            emails = []
            for num in message_numbers[0].split()[-limit:]:
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                # Extract email data
                emails.append({
                    'id': num.decode(),
                    'from': email_message.get('From'),
                    'to': email_message.get('To'),
                    'subject': email_message.get('Subject'),
                    'date': email_message.get('Date'),
                    'body': self._get_email_body(email_message)
                })

            mail.close()
            mail.logout()

            return emails

        except Exception as e:
            return [{'error': str(e)}]

    def _get_email_body(self, email_message) -> str:
        """Extract email body from message."""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
        return body

    def mark_as_read(self, email_id: str, mailbox: str = 'INBOX') -> str:
        """Mark email as read."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select(mailbox)
            mail.store(email_id, '+FLAGS', '\\Seen')
            mail.close()
            mail.logout()
            return f"Email {email_id} marked as read"
        except Exception as e:
            return f"Error marking email as read: {e}"

    def delete_email(self, email_id: str, mailbox: str = 'INBOX') -> str:
        """Delete email."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            mail.select(mailbox)
            mail.store(email_id, '+FLAGS', '\\Deleted')
            mail.expunge()
            mail.close()
            mail.logout()
            return f"Email {email_id} deleted"
        except Exception as e:
            return f"Error deleting email: {e}"


# =============================================================================
# GOOGLE CALENDAR INTEGRATION
# =============================================================================

class GoogleCalendarClient:
    """Google Calendar integration."""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None

    def authenticate(self) -> str:
        """Authenticate with Google Calendar API."""
        if not GOOGLE_CALENDAR_AVAILABLE:
            return "Error: Google Calendar API not available"

        try:
            creds = None
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        return "Error: credentials.json not found. Download from Google Cloud Console."
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())

            self.service = build('calendar', 'v3', credentials=creds)
            return "Authenticated with Google Calendar"

        except Exception as e:
            return f"Error authenticating: {e}"

    def list_events(
        self,
        max_results: int = 10,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """List calendar events."""
        if not self.service:
            return [{'error': 'Not authenticated. Call authenticate() first.'}]

        try:
            time_min = time_min or datetime.utcnow()
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z' if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            return [
                {
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                }
                for event in events
            ]

        except Exception as e:
            return [{'error': str(e)}]

    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str = '',
        location: str = '',
        attendees: List[str] = None
    ) -> str:
        """Create a calendar event."""
        if not self.service:
            return "Error: Not authenticated"

        try:
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return f"Event created: {created_event.get('htmlLink')}"

        except Exception as e:
            return f"Error creating event: {e}"

    def delete_event(self, event_id: str) -> str:
        """Delete a calendar event."""
        if not self.service:
            return "Error: Not authenticated"

        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return f"Event {event_id} deleted"
        except Exception as e:
            return f"Error deleting event: {e}"

    def find_free_slots(
        self,
        duration_minutes: int = 60,
        days_ahead: int = 7,
        working_hours: tuple = (9, 17)
    ) -> List[Dict[str, datetime]]:
        """Find free time slots in calendar."""
        if not self.service:
            return [{'error': 'Not authenticated'}]

        try:
            time_min = datetime.utcnow()
            time_max = time_min + timedelta(days=days_ahead)

            events = self.list_events(max_results=100, time_min=time_min, time_max=time_max)

            # Simple free slot finder (can be enhanced)
            free_slots = []
            current_time = time_min

            while current_time < time_max:
                # Check if within working hours
                if working_hours[0] <= current_time.hour < working_hours[1]:
                    slot_end = current_time + timedelta(minutes=duration_minutes)

                    # Check if slot conflicts with any event
                    is_free = True
                    for event in events:
                        if 'error' not in event:
                            event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                            event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))

                            if not (slot_end <= event_start or current_time >= event_end):
                                is_free = False
                                break

                    if is_free:
                        free_slots.append({
                            'start': current_time,
                            'end': slot_end
                        })

                current_time += timedelta(minutes=30)

            return free_slots[:10]  # Return first 10 free slots

        except Exception as e:
            return [{'error': str(e)}]


# =============================================================================
# EMAIL UTILITIES
# =============================================================================

def summarize_email(email_content: str, max_length: int = 200) -> str:
    """Create a brief summary of email content."""
    sentences = email_content.split('.')
    summary = '. '.join(sentences[:3]) + '.'
    if len(summary) > max_length:
        summary = summary[:max_length] + '...'
    return summary


def parse_email_addresses(address_string: str) -> List[str]:
    """Parse comma-separated email addresses."""
    return [addr.strip() for addr in address_string.split(',') if addr.strip()]


def validate_email(email_address: str) -> bool:
    """Simple email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email_address) is not None


# =============================================================================
# MEETING SCHEDULER
# =============================================================================

class MeetingScheduler:
    """Automated meeting scheduling assistant."""

    def __init__(self, calendar_client: GoogleCalendarClient, email_client: EmailClient):
        self.calendar = calendar_client
        self.email = email_client

    def schedule_meeting(
        self,
        attendees: List[str],
        duration_minutes: int,
        subject: str,
        description: str = '',
        preferred_days: int = 7
    ) -> str:
        """Find free slot and schedule meeting."""
        try:
            # Find free slots
            free_slots = self.calendar.find_free_slots(
                duration_minutes=duration_minutes,
                days_ahead=preferred_days
            )

            if not free_slots or 'error' in free_slots[0]:
                return "No free slots found"

            # Use first available slot
            slot = free_slots[0]

            # Create calendar event
            result = self.calendar.create_event(
                summary=subject,
                start_time=slot['start'],
                end_time=slot['end'],
                description=description,
                attendees=attendees
            )

            # Send invitation emails
            meeting_details = f"""
Meeting Scheduled: {subject}

Time: {slot['start'].strftime('%Y-%m-%d %H:%M')} - {slot['end'].strftime('%H:%M')}
Duration: {duration_minutes} minutes

Description: {description}

This meeting has been added to your calendar.
"""

            self.email.send_email(
                to_addresses=attendees,
                subject=f"Meeting Invitation: {subject}",
                body=meeting_details
            )

            return f"Meeting scheduled for {slot['start'].strftime('%Y-%m-%d %H:%M')}"

        except Exception as e:
            return f"Error scheduling meeting: {e}"


__all__ = [
    'EmailClient',
    'IMAPClient',
    'GoogleCalendarClient',
    'MeetingScheduler',
    'summarize_email',
    'parse_email_addresses',
    'validate_email'
]

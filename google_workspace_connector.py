"""
SweetyAI Google Workspace & YouTube Live Integration Hub
Handles OAuth 2.0 authentication and live API requests for Calendar, Tasks, and YouTube.
"""

import os
import json
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format="[SweetyAI Google Hub] %(levelname)s: %(message)s")

# Required scopes for Calendar, Tasks, and YouTube
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/youtube.readonly'
]

class GoogleWorkspaceConnector:
    def __init__(self):
        self.creds_path = "social_config/google_credentials.json"
        self.token_path = "social_config/token.json"
        self.creds = None
        self.authenticate()

    def authenticate(self):
        """Handles OAuth 2.0 flow for Google APIs."""
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logging.warning(f"Token refresh failed: {e}. Re-authenticating...")
                    self.creds = None

            if not self.creds:
                if not os.path.exists(self.creds_path):
                    logging.error(f"Google credentials file missing at {self.creds_path}!")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
                # Local server flow for terminal/desktop environment
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for future runs
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
                logging.info("Saved fresh OAuth token to %s", self.token_path)

    def create_calendar_event(self, summary: str, start_time: str, end_time: str, description: str = ""):
        """Creates an event in live Google Calendar (ISO format: YYYY-MM-DDTHH:MM:SS)."""
        if not self.creds:
            return {"status": "error", "message": "Not authenticated"}
        
        service = build('calendar', 'v3', credentials=self.creds)
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        logging.info(f"[Google Calendar] Created live event: {summary}")
        return {"status": "success", "event_id": created_event.get('id'), "link": created_event.get('htmlLink')}

    def add_to_do_task(self, task_title: str, due_date: str, notes: str = ""):
        """Adds a task to Google Tasks (due_date format: YYYY-MM-DDT00:00:00.000Z)."""
        if not self.creds:
            return {"status": "error", "message": "Not authenticated"}
        
        service = build('tasks', 'v1', credentials=self.creds)
        task = {
            'title': task_title,
            'notes': notes,
            'due': due_date if 'T' in due_date else f"{due_date}T00:00:00.000Z"
        }
        result = service.tasks().insert(tasklist='@default', body=task).execute()
        logging.info(f"[Google Tasks] Added live task: {task_title}")
        return {"status": "success", "task_id": result.get('id'), "title": result.get('title')}

    def fetch_youtube_channel_stats(self):
        """Fetches channel statistics for the authenticated user."""
        if not self.creds:
            return {"status": "error", "message": "Not authenticated"}
        
        service = build('youtube', 'v3', credentials=self.creds)
        request = service.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()
        logging.info("[YouTube API] Fetched channel analytics successfully.")
        return {"status": "success", "data": response}

if __name__ == "__main__":
    hub = GoogleWorkspaceConnector()
    print("Google Workspace Integration Hub initialized and authenticated successfully!")

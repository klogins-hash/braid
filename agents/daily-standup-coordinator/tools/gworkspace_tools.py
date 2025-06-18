"""
Public, LLM-callable tools for interacting with Google Workspace (Calendar, Gmail, GSheets).
"""
import os
import base64
from typing import List, Optional

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError(
        "Google Workspace tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install ".[gworkspace]"'
    )

# --- Authentication Helper ---
# If modifying these scopes, delete the token.json file.
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets",
]

def _get_gworkspace_credentials():
    """Gets valid user credentials from storage or initiates authentication."""
    creds = None
    if os.path.exists("credentials/gworkspace_token.json"):
        creds = Credentials.from_authorized_user_file("credentials/gworkspace_token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials/gworkspace_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("credentials/gworkspace_token.json", "w") as token:
            token.write(creds.to_json())
    return creds

# --- Input Schemas ---

class GoogleCalendarCreateEventInput(BaseModel):
    summary: str = Field(description="The summary or title of the event.")
    start_time: str = Field(description="The start time of the event in ISO 8601 format (e.g., '2024-05-10T10:00:00-07:00').")
    end_time: str = Field(description="The end time of the event in ISO 8601 format (e.g., '2024-05-10T11:00:00-07:00').")
    attendees: List[str] = Field(description="A list of attendee email addresses.")
    location: Optional[str] = Field(default=None, description="The location of the event.")
    description: Optional[str] = Field(default=None, description="A description for the event.")

class GmailSendEmailInput(BaseModel):
    to: List[str] = Field(description="A list of recipient email addresses.")
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The plain text body of the email.")

class GSheetsAppendRowInput(BaseModel):
    spreadsheet_id: str = Field(description="The ID of the Google Sheet.")
    range_name: str = Field(description="The A1 notation of a range to search for a logical table of data. Values are appended after the last row of the table.")
    values: List[str] = Field(description="A list of string values to append in the new row, in order.")

# --- Input Schemas for Calendar Read Operations ---

class GoogleCalendarListEventsInput(BaseModel):
    max_results: int = Field(default=10, description="Maximum number of events to return (1-250).")
    time_min: Optional[str] = Field(default=None, description="Lower bound (exclusive) for an event's end time to filter by in ISO 8601 format. Optional - defaults to now.")
    time_max: Optional[str] = Field(default=None, description="Upper bound (exclusive) for an event's start time to filter by in ISO 8601 format. Optional.")
    single_events: bool = Field(default=True, description="Whether to expand recurring events into instances.")

# --- Google Calendar Tools ---

@tool("google_calendar_list_events", args_schema=GoogleCalendarListEventsInput)
def list_google_calendar_events(max_results: int = 10, time_min: Optional[str] = None, time_max: Optional[str] = None, single_events: bool = True) -> str:
    """
    Lists events from the user's primary Google Calendar.
    Returns a formatted string with event details including title, time, attendees, and description.
    """
    try:
        creds = _get_gworkspace_credentials()
        service = build("calendar", "v3", credentials=creds)
        
        # If no time_min specified, default to current time
        if time_min is None:
            from datetime import datetime
            time_min = datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=single_events,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
        
        event_list = []
        for event in events:
            summary = event.get('summary', 'No title')
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Get attendees if available
            attendees = event.get('attendees', [])
            attendee_emails = [attendee.get('email', '') for attendee in attendees if attendee.get('email')]
            
            description = event.get('description', '')
            location = event.get('location', '')
            
            event_info = f"• {summary}\n  Time: {start} to {end}"
            if attendee_emails:
                event_info += f"\n  Attendees: {', '.join(attendee_emails)}"
            if location:
                event_info += f"\n  Location: {location}"
            if description:
                event_info += f"\n  Description: {description[:100]}{'...' if len(description) > 100 else ''}"
            
            event_list.append(event_info)
        
        return "\n\n".join(event_list)
        
    except HttpError as error:
        return f"An error occurred with Google Calendar API: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("google_calendar_create_event", args_schema=GoogleCalendarCreateEventInput)
def create_google_calendar_event(summary: str, start_time: str, end_time: str, attendees: List[str], location: Optional[str] = None, description: Optional[str] = None) -> str:
    """
    Creates a new event on Google Calendar.
    """
    try:
        creds = _get_gworkspace_credentials()
        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "America/Los_Angeles"},
            "end": {"dateTime": end_time, "timeZone": "America/Los_Angeles"},
            "attendees": [{"email": email} for email in attendees],
        }
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return f"Event created successfully. View it here: {created_event.get('htmlLink')}"
    except HttpError as error:
        return f"An error occurred with Google Calendar API: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Gmail Tools ---

@tool("gmail_send_email", args_schema=GmailSendEmailInput)
def gmail_send_email(to: List[str], subject: str, body: str) -> str:
    """
    Sends an email using Gmail.
    """
    try:
        creds = _get_gworkspace_credentials()
        service = build("gmail", "v1", credentials=creds)
        message = f"From: me\nTo: {', '.join(to)}\nSubject: {subject}\n\n{body}"
        raw_message = base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return "Email sent successfully."
    except HttpError as error:
        return f"An error occurred with Gmail API: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Google Sheets Tools ---

@tool("gsheets_append_row", args_schema=GSheetsAppendRowInput)
def gsheets_append_row(spreadsheet_id: str, range_name: str, values: List[str]) -> str:
    """
    Appends a new row of values to a Google Sheet.
    """
    try:
        creds = _get_gworkspace_credentials()
        service = build("sheets", "v4", credentials=creds)
        body = {"values": [values]}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        return f"{result.get('updates').get('updatedCells')} cells appended."
    except HttpError as error:
        return f"An error occurred with Google Sheets API: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Tool Aggregator ---

def get_google_calendar_tools():
    return [list_google_calendar_events, create_google_calendar_event]

def get_gmail_tools():
    return [gmail_send_email]

def get_gsheets_tools():
    return [gsheets_append_row]

def get_gworkspace_tools():
    """Returns a list of all Google Workspace tools."""
    return get_google_calendar_tools() + get_gmail_tools() + get_gsheets_tools() 
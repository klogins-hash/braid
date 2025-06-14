"""
Google Calendar Tools for LangGraph Agents

This module provides robust tools for interacting with Google Calendar API.
These tools are designed to work consistently across different agent implementations
and handle common pitfalls like date parsing, timezone issues, and validation.

SETUP REQUIREMENTS:
1. Install dependencies: pip install ".[gworkspace]"
2. Set up Google Cloud project and enable Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app type)
4. Save credentials as `credentials/google_credentials.json`
5. First run will open browser for authorization

COMMON USAGE PATTERNS:
- When using with LLMs, always provide current date context in your system prompt
- Use ISO 8601 format for all datetime inputs: YYYY-MM-DDTHH:MM:SS±HH:MM
- Consider timezone implications when scheduling across different regions

TROUBLESHOOTING:
- If events appear in wrong year: Ensure LLM has current date context
- If timezone issues: Verify correct timezone offsets (PST=-08:00, PDT=-07:00)
- If authentication fails: Check redirect URIs in Google Cloud Console
"""

try:
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError(
        "Google Calendar tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install ".[gworkspace]"'
    )

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field, validator
from .google_auth import get_google_service
import re
from datetime import datetime, timedelta
import pytz
from typing import Optional, Tuple
import logging

# Set up logging for debugging
logger = logging.getLogger(__name__)

# Define the scopes required for the Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Combined scopes for all Google Workspace tools to prevent auth conflicts
COMBINED_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events"
]

# Common timezone mappings for better user experience
TIMEZONE_MAPPINGS = {
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles", 
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "UTC": "UTC",
    "GMT": "UTC"
}

def validate_iso_datetime(dt_string: str) -> Tuple[bool, str]:
    """
    Validate if a string is in proper ISO 8601 format and return helpful error message.
    
    Args:
        dt_string: The datetime string to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not dt_string:
        return False, "DateTime string cannot be empty"
    
    # Enhanced pattern to catch more ISO 8601 variants
    iso_patterns = [
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$',  # Standard: 2025-06-14T14:00:00-07:00
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$',                # UTC: 2025-06-14T21:00:00Z
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2}$',  # With milliseconds
    ]
    
    for pattern in iso_patterns:
        if re.match(pattern, dt_string):
            try:
                # Additional validation: ensure it can be parsed
                datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
                return True, ""
            except ValueError as e:
                return False, f"Invalid datetime format: {str(e)}"
    
    return False, (
        f"Invalid ISO 8601 format: '{dt_string}'. "
        "Expected formats: 'YYYY-MM-DDTHH:MM:SS±HH:MM' or 'YYYY-MM-DDTHH:MM:SSZ'"
    )

def validate_datetime_logic(start_time: str, end_time: str) -> Tuple[bool, str]:
    """
    Validate datetime logic (end after start, reasonable duration, not too far in past).
    
    Args:
        start_time: ISO 8601 start time string
        end_time: ISO 8601 end time string
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    try:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        now = datetime.now(pytz.UTC)
        
        # Check if end is after start
        if end_dt <= start_dt:
            return False, f"End time ({end_time}) must be after start time ({start_time})"
        
        # Check for reasonable duration (not longer than 24 hours)
        duration = end_dt - start_dt
        if duration > timedelta(hours=24):
            return False, f"Event duration too long: {duration}. Maximum 24 hours allowed."
        
        # Check if event is too far in the past (more than 1 year)
        if start_dt < now - timedelta(days=365):
            return False, (
                f"Event start time ({start_time}) is more than 1 year in the past. "
                "This might indicate a date parsing error. Please verify the year is correct."
            )
        
        # Warn if event is in distant future (more than 2 years)
        if start_dt > now + timedelta(days=730):
            logger.warning(f"Event scheduled far in future: {start_time}")
        
        return True, ""
        
    except ValueError as e:
        return False, f"Error parsing datetime: {str(e)}"

def extract_timezone_from_datetime(dt_string: str) -> str:
    """
    Extract timezone information from ISO datetime string.
    
    Args:
        dt_string: ISO 8601 datetime string
        
    Returns:
        Timezone identifier (e.g., "America/Los_Angeles") or "UTC" if Z format
    """
    if dt_string.endswith('Z'):
        return "UTC"
    
    # Extract timezone offset
    if '+' in dt_string:
        offset = dt_string.split('+')[1]
    elif dt_string.count('-') >= 3:  # Has timezone offset
        offset = dt_string.split('-')[-1]
    else:
        return "UTC"  # Default fallback
    
    # Map common offsets to timezones (this is simplified)
    offset_mappings = {
        "08:00": "America/Los_Angeles",  # PST
        "07:00": "America/Los_Angeles",  # PDT
        "05:00": "America/New_York",     # EST
        "04:00": "America/New_York",     # EDT
        "00:00": "UTC"
    }
    
    return offset_mappings.get(offset, "UTC")

class CreateEventInput(BaseModel):
    """
    Input schema for creating Google Calendar events.
    
    IMPORTANT FOR LLM USAGE:
    - Always use current year in datetime strings
    - Use proper timezone offsets: PST=-08:00, PDT=-07:00, EST=-05:00, EDT=-04:00
    - Ensure end_time is after start_time
    - Use meaningful summary and description
    """
    summary: str = Field(
        description="A clear, descriptive title for the event (e.g., 'Project Kickoff Meeting with Acme Corp')"
    )
    start_time: str = Field(
        description=(
            "Event start time in ISO 8601 format. "
            "CRITICAL: Use current year and proper timezone offset. "
            "Examples: '2025-06-14T14:00:00-07:00' (PDT), '2025-12-15T10:00:00-08:00' (PST)"
        )
    )
    end_time: str = Field(
        description=(
            "Event end time in ISO 8601 format. Must be after start_time. "
            "Examples: '2025-06-14T15:00:00-07:00' (1 hour after start)"
        )
    )
    location: str = Field(
        default="",
        description="Event location (e.g., 'Conference Room A', 'https://zoom.us/j/123456789', or 'Virtual')"
    )
    description: str = Field(
        default="",
        description="Detailed event description including agenda, participants, or meeting purpose"
    )
    timezone: Optional[str] = Field(
        default=None,
        description="Optional timezone override (e.g., 'America/Los_Angeles'). If not provided, extracted from datetime."
    )

    @validator('start_time', 'end_time')
    def validate_datetime_format(cls, v):
        """Validate datetime format during input parsing."""
        is_valid, error_msg = validate_iso_datetime(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

@tool("create_google_calendar_event", args_schema=CreateEventInput)
def create_google_calendar_event(
    summary: str, 
    start_time: str, 
    end_time: str, 
    location: str = "", 
    description: str = "",
    timezone: Optional[str] = None
) -> str:
    """
    Creates a new event on the user's primary Google Calendar with comprehensive validation.
    
    This tool includes multiple layers of validation to prevent common issues:
    - ISO 8601 format validation
    - Logical datetime validation (end after start, reasonable duration)
    - Timezone handling and extraction
    - Year verification to prevent past-year errors
    
    Args:
        summary: Event title/summary
        start_time: ISO 8601 start datetime with timezone
        end_time: ISO 8601 end datetime with timezone  
        location: Event location (optional)
        description: Event description (optional)
        timezone: Timezone override (optional)
        
    Returns:
        Success message with calendar link or detailed error message
    """
    try:
        logger.info(f"Creating calendar event: {summary} from {start_time} to {end_time}")
        
        # Step 1: Validate datetime formats
        start_valid, start_error = validate_iso_datetime(start_time)
        if not start_valid:
            return f"❌ Start time error: {start_error}"
        
        end_valid, end_error = validate_iso_datetime(end_time)
        if not end_valid:
            return f"❌ End time error: {end_error}"
        
        # Step 2: Validate datetime logic
        logic_valid, logic_error = validate_datetime_logic(start_time, end_time)
        if not logic_valid:
            return f"❌ DateTime logic error: {logic_error}"
        
        # Step 3: Extract or use provided timezone
        if not timezone:
            timezone = extract_timezone_from_datetime(start_time)
        
        # Step 4: Create the calendar service
        service = get_google_service("calendar", "v3", SCOPES, COMBINED_SCOPES)
        
        # Step 5: Prepare event data
        event_data = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": timezone
            },
            "end": {
                "dateTime": end_time,
                "timeZone": timezone
            },
            # Add some useful defaults
            "reminders": {
                "useDefault": True
            },
            "visibility": "default",
            "status": "confirmed"
        }
        
        # Step 6: Create the event
        logger.info(f"Sending event data to Google Calendar API")
        created_event = service.events().insert(calendarId="primary", body=event_data).execute()
        
        # Step 7: Return success with link
        event_id = created_event.get('id')
        event_link = created_event.get('htmlLink', f"https://calendar.google.com/calendar/event?eid={event_id}")
        
        logger.info(f"Event created successfully with ID: {event_id}")
        
        return (
            f"✅ Calendar event created successfully!\n"
            f"📅 Event: {summary}\n"
            f"🕐 Time: {start_time} to {end_time}\n"
            f"📍 Location: {location or 'Not specified'}\n"
            f"🔗 View event: {event_link}"
        )
        
    except HttpError as error:
        error_details = error.content.decode('utf-8') if error.content else str(error)
        logger.error(f"Google Calendar API error: {error.resp.status} - {error_details}")
        
        return (
            f"❌ Google Calendar API error (HTTP {error.resp.status}):\n"
            f"Details: {error_details}\n"
            f"Event: {summary} ({start_time} to {end_time})\n"
            f"Suggestion: Check your calendar permissions and try again."
        )
        
    except Exception as e:
        logger.error(f"Unexpected error creating calendar event: {str(e)}", exc_info=True)
        
        return (
            f"❌ Failed to create calendar event: {str(e)}\n"
            f"Event details: {summary} from {start_time} to {end_time}\n"
            f"Location: {location}\n"
            f"Please check the datetime format and try again."
        )

@tool("list_upcoming_events")
def list_upcoming_events(max_results: int = 10) -> str:
    """
    List upcoming events from the user's primary Google Calendar.
    
    Args:
        max_results: Maximum number of events to return (default: 10)
        
    Returns:
        Formatted list of upcoming events or error message
    """
    try:
        service = get_google_service("calendar", "v3", SCOPES, COMBINED_SCOPES)
        
        # Get events starting from now
        now = datetime.now(pytz.UTC).isoformat().replace('+00:00', 'Z')
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "📅 No upcoming events found."
        
        event_list = ["📅 Upcoming Calendar Events:\n"]
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'Untitled Event')
            location = event.get('location', '')
            
            # Format the datetime
            try:
                if 'T' in start:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%A, %B %d at %I:%M %p")
                else:
                    formatted_time = f"All day on {start}"
            except:
                formatted_time = start
            
            event_info = f"• {summary} - {formatted_time}"
            if location:
                event_info += f" ({location})"
            
            event_list.append(event_info)
        
        return "\n".join(event_list)
        
    except HttpError as error:
        return f"❌ Error fetching events: {error}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def get_google_calendar_tools():
    """
    Returns a list of all Google Calendar tools available in this module.
    
    Available tools:
    - create_google_calendar_event: Create new calendar events with robust validation
    - list_upcoming_events: List upcoming events from the calendar
    
    Returns:
        List of LangChain tools
    """
    return [create_google_calendar_event, list_upcoming_events]

# Additional utility functions for agent developers

def get_current_date_context() -> str:
    """
    Get current date context formatted for LLM system prompts.
    
    This is a utility function that agent developers can use to provide
    proper date context to LLMs to prevent date parsing errors.
    
    Returns:
        Formatted string with current date information
    """
    now = datetime.now(pytz.timezone('America/Los_Angeles'))
    tomorrow = now + timedelta(days=1)
    
    return f"""
CURRENT DATE CONTEXT:
- Today: {now.strftime("%A, %B %d, %Y")}
- Current time: {now.strftime("%I:%M %p %Z")}
- Tomorrow: {tomorrow.strftime("%A, %B %d, %Y")}
- Current year: {now.year}

TIMEZONE REFERENCE:
- PST (Pacific Standard Time): UTC-8 = -08:00
- PDT (Pacific Daylight Time): UTC-7 = -07:00
- Current Pacific timezone: {now.strftime("%Z")} = {now.strftime("%z")[:3]}:{now.strftime("%z")[3:]}

DATETIME FORMAT EXAMPLES:
- Tomorrow 2 PM PST: {tomorrow.replace(hour=14, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%S%z")[:22]}
- Next week same time: {(now + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S%z")[:22]}
"""

def validate_agent_datetime_input(dt_string: str, context: str = "") -> str:
    """
    Validate datetime input with agent-friendly error messages.
    
    Args:
        dt_string: The datetime string to validate
        context: Additional context about where this validation is happening
        
    Returns:
        Empty string if valid, or detailed error message with suggestions
    """
    is_valid, error_msg = validate_iso_datetime(dt_string)
    
    if is_valid:
        logic_valid, logic_error = validate_datetime_logic(dt_string, dt_string)
        if logic_valid:
            return ""  # All good
        else:
            return f"{context}: {logic_error}"
    
    current_year = datetime.now().year
    suggestions = f"""
{context}: {error_msg}

💡 SUGGESTIONS:
1. Use current year ({current_year}) in your datetime
2. Include proper timezone offset (e.g., -07:00 for PDT, -08:00 for PST)
3. Format: YYYY-MM-DDTHH:MM:SS±HH:MM
4. Example: {datetime.now().strftime('%Y-%m-%dT14:00:00-07:00')}

{get_current_date_context()}
"""
    
    return suggestions
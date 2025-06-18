"""
Google Workspace Utility Functions.
"""
from datetime import datetime
import pytz

def get_current_date_context() -> str:
    """Returns the current date and time in a user-friendly format for system prompts."""
    pst = pytz.timezone('America/Los_Angeles')
    now = datetime.now(pst)
    return f"Today is {now.strftime('%A, %B %d, %Y')}. The current time is {now.strftime('%I:%M %p %Z')}." 
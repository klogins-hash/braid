"""
Tools for interacting with Gmail.
This tool uses the "gworkspace" optional dependency.
Install it with: pip install ".[gworkspace]"
"""
import base64
from email.mime.text import MIMEText

try:
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError(
        "Gmail tools are not available. Please install the necessary dependencies with: "
        'pip install ".[gworkspace]"'
    )

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from .google_auth import get_google_service

# Define the scopes required for the Gmail API
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
# Combined scopes for all Google Workspace tools
COMBINED_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events"
]

class SendEmailInput(BaseModel):
    to: str = Field(description="The email address of the recipient.")
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body content of the email.")

@tool("gmail_send_email", args_schema=SendEmailInput)
def gmail_send_email(to: str, subject: str, body: str) -> str:
    """
    Sends an email from the user's Gmail account.
    """
    try:
        service = get_google_service("gmail", "v1", SCOPES, COMBINED_SCOPES)
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        
        # The 'me' keyword refers to the authenticated user's email address
        create_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
        
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return f"Email sent successfully! Message ID: {send_message['id']}"
    except HttpError as error:
        return f"An error occurred with Gmail API: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def get_gmail_tools():
    """Returns a list of all tools in this module."""
    return [gmail_send_email] 
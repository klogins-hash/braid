"""
Tools for interacting with Microsoft 365 services.
This toolset uses the "ms365" optional dependency.
Install it with: pip install ".[ms365]"

To use these tools, you must first register an application in the
Microsoft Entra admin center.

1.  Go to the Microsoft Entra admin center -> Identity -> Applications -> App registrations.
2.  Create a new registration.
3.  For "Supported account types," select "Accounts in any organizational
    directory (Any Microsoft Entra ID tenant - Multitenant) and personal
    Microsoft accounts (e.g. Skype, Xbox)."
4.  Add a "Web" platform and set the Redirect URI to "http://localhost:8000".
5.  Go to "API permissions" and add the following delegated permissions
    from Microsoft Graph:
    - `User.Read`
    - `Mail.Send`
    - `ChannelMessage.Send`
    - `Team.ReadBasic.All`
6.  Go to "Certificates & secrets" and create a new client secret. Copy this
    secret value.
7.  Create a file at `credentials/ms365_credentials.json` with the following format:
    {
        "client_id": "YOUR_APP_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET"
    }
"""
import os
import json

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    from O365 import Account
except ImportError:
    raise ImportError(
        "Microsoft 365 tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install ".[ms365]"'
    )

CREDS_PATH = "credentials/ms365_credentials.json"
TOKEN_PATH = "credentials/ms365_token.json"

# Global account instance to avoid multiple authentications
_ms365_account = None

def get_ms365_account():
    """Authenticates with Microsoft 365 and returns an Account object."""
    global _ms365_account
    
    # Return existing account if already created and authenticated
    if _ms365_account is not None and _ms365_account.is_authenticated:
        return _ms365_account
        
    if not os.path.exists(CREDS_PATH):
        raise FileNotFoundError(f"Microsoft 365 credentials not found at {CREDS_PATH}")

    with open(CREDS_PATH) as f:
        creds = json.load(f)
    
    from O365.connection import FileSystemTokenBackend
    token_backend = FileSystemTokenBackend(token_path=TOKEN_PATH)
    _ms365_account = Account((creds["client_id"], creds["client_secret"]), 
                            tenant_id="e76a482b-c060-4a49-affc-87c454bd1976",
                            token_backend=token_backend)

    if not _ms365_account.is_authenticated:
        # This will open a browser for the user to authenticate and consent
        # The token will be saved automatically to TOKEN_PATH
        _ms365_account.authenticate(scopes=["User.Read", "Mail.Send", "ChannelMessage.Send", "Team.ReadBasic.All"])
    
    return _ms365_account

# --- Tool Definitions ---

class SendOutlookEmailInput(BaseModel):
    to_recipient: str = Field(description="The email address of the recipient.")
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body content of the email.")

@tool("outlook_send_email", args_schema=SendOutlookEmailInput)
def outlook_send_email(to_recipient: str, subject: str, body: str) -> str:
    """Sends an email from the user's Outlook account."""
    try:
        account = get_ms365_account()
        mailbox = account.mailbox()
        message = mailbox.new_message()
        message.to.add(to_recipient)
        message.subject = subject
        message.body = body
        message.send()
        return "Email sent successfully via Outlook."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

class PostTeamsMessageInput(BaseModel):
    team_name: str = Field(description="The name of the Team.")
    channel_name: str = Field(description="The name of the channel to post the message in.")
    message: str = Field(description="The text of the message to post.")

@tool("teams_post_message", args_schema=PostTeamsMessageInput)
def teams_post_message(team_name: str, channel_name: str, message: str) -> str:
    """Sends a message to a specific channel in Microsoft Teams."""
    try:
        account = get_ms365_account()
        teams = account.teams()
        team = teams.get_team(team_name)
        if not team:
            return f"Error: Team '{team_name}' not found."
        channel = team.get_channel(channel_name)
        if not channel:
            return f"Error: Channel '{channel_name}' not found in team '{team_name}'."
        
        channel.send_message(message)
        return "Message posted successfully to Teams."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("graph_get_user")
def graph_get_user() -> str:
    """Fetches and returns the display name and email of the authenticated Microsoft 365 user."""
    try:
        account = get_ms365_account()
        # The user's info is implicitly available via the authenticated account
        user_info = {
            "display_name": account.get_current_user().get('displayName'),
            "email": account.get_current_user().get('mail')
        }
        return json.dumps(user_info)
    except Exception as e:
        return f"An unexpected error occurred: {e}" 
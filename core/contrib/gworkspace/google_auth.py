"""
Shared authentication logic for all Google Workspace tools.
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TOKEN_DIR = "credentials"
TOKEN_PATH = os.path.join(TOKEN_DIR, "google_token.json")
CREDS_PATH = os.path.join(TOKEN_DIR, "google_credentials.json")

def get_google_service(api_name: str, api_version: str, scopes: list[str], combined_scopes: list[str] = None):
    """
    A generic function to authenticate with a Google API and return a service object.
    Handles the OAuth2 flow and token management.
    """
    # Use combined scopes if provided, otherwise use individual scopes
    auth_scopes = combined_scopes if combined_scopes else scopes
    
    # Ensure the credentials directory exists
    os.makedirs(TOKEN_DIR, exist_ok=True)
    
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, auth_scopes)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_PATH):
                raise FileNotFoundError(
                    "Google credentials not found. Please place your "
                    f"`credentials.json` file at `{CREDS_PATH}`"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, auth_scopes)
            creds = flow.run_local_server(port=8080)
        
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build(api_name, api_version, credentials=creds) 
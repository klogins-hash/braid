# authenticate_gworkspace.py
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# These scopes must match the ones in your gworkspace tools
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets",
]

CREDENTIALS_DIR = 'credentials'
TOKEN_PATH = os.path.join(CREDENTIALS_DIR, 'gworkspace_token.json')
CLIENT_SECRETS_PATH = os.path.join(CREDENTIALS_DIR, 'gworkspace_credentials.json')

def authenticate():
    """
    Runs the Google OAuth2 flow to get a token and saves it.
    This should be run once, locally, before running any agent that uses GWorkspace tools.
    """
    creds = None

    if not os.path.exists(CLIENT_SECRETS_PATH):
        print(f"---")
        print(f"🚨 Error: Client secrets file not found at '{CLIENT_SECRETS_PATH}'")
        print(f"Please download your OAuth 2.0 Client ID credentials from the Google Cloud Console and save the file there.")
        print(f"---")
        return

    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("   Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("   No valid credentials found. Starting authentication flow...")
            print("   Your browser will open to complete the authentication.")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        if not os.path.exists(CREDENTIALS_DIR):
            os.makedirs(CREDENTIALS_DIR)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Credentials saved successfully to '{TOKEN_PATH}'")
    else:
        print("✅ Google Workspace credentials are valid and ready.")

if __name__ == '__main__':
    authenticate() 
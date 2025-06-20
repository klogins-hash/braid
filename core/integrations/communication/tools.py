"""
Twilio Direct API Integration Tools

Provides direct API access to Twilio's communication services without MCP server dependencies.
Includes SMS, voice, WhatsApp, email, verification, and serverless capabilities.
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        "Twilio tools require additional dependencies. "
        "Install with: pip install requests python-dotenv"
    )

# Load environment variables
load_dotenv(override=True)

# --- Input Schemas ---

class SMSInput(BaseModel):
    to: str = Field(description="Recipient phone number in E.164 format (e.g., +1234567890)")
    from_: str = Field(alias="from", description="Sender phone number (Twilio number)")
    body: str = Field(description="Text message content (up to 1600 characters)")
    media_url: Optional[List[str]] = Field(default=None, description="URLs of media attachments for MMS")

class CallInput(BaseModel):
    to: str = Field(description="Phone number to call in E.164 format")
    from_: str = Field(alias="from", description="Caller ID (Twilio number)")
    twiml: Optional[str] = Field(default=None, description="TwiML instructions for the call")
    url: Optional[str] = Field(default=None, description="Webhook URL for dynamic TwiML")

class EmailInput(BaseModel):
    to: str = Field(description="Recipient email address")
    from_: str = Field(alias="from", description="Sender email address")
    subject: str = Field(description="Email subject line")
    text_content: Optional[str] = Field(default=None, description="Plain text email content")
    html_content: Optional[str] = Field(default=None, description="HTML email content")

class VerifyInput(BaseModel):
    phone_number: str = Field(description="Phone number to verify in E.164 format")
    channel: str = Field(default="sms", description="Verification channel: sms, call, or email")
    locale: Optional[str] = Field(default="en", description="Language locale for verification message")

class LookupInput(BaseModel):
    phone_number: str = Field(description="Phone number to lookup in E.164 format")
    type: Optional[List[str]] = Field(default=["carrier"], description="Lookup types: carrier, caller-name")

class FunctionInput(BaseModel):
    service_sid: str = Field(description="Twilio Service SID for the function")
    function_path: str = Field(description="Function path (e.g., /hello-world)")
    code: str = Field(description="JavaScript code for the function")
    visibility: str = Field(default="protected", description="Function visibility: public, protected, private")

class AssetInput(BaseModel):
    service_sid: str = Field(description="Twilio Service SID for the asset")
    asset_path: str = Field(description="Asset path (e.g., /style.css)")
    content: str = Field(description="Asset content")
    content_type: str = Field(description="MIME type (e.g., text/css, image/png)")

# --- Helper Functions ---

def _get_twilio_auth() -> tuple[str, str]:
    """Get Twilio authentication credentials."""
    # Force reload environment variables
    load_dotenv(override=True)
    
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    
    # Prefer API Key authentication over Auth Token
    api_key = os.getenv("TWILIO_API_KEY", "").strip()
    api_secret = os.getenv("TWILIO_API_SECRET", "").strip()
    
    if api_key and api_secret:
        return api_key, api_secret
    
    # Fallback to Auth Token
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    if account_sid and auth_token:
        return account_sid, auth_token
    
    raise ValueError(
        "Missing Twilio credentials. Set either:\n"
        "- TWILIO_API_KEY + TWILIO_API_SECRET (recommended)\n"
        "- TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN"
    )

def _get_account_sid() -> str:
    """Get Twilio Account SID."""
    load_dotenv(override=True)
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    if not account_sid:
        raise ValueError("TWILIO_ACCOUNT_SID environment variable not set")
    return account_sid

def _make_twilio_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """Make authenticated request to Twilio API."""
    
    try:
        username, password = _get_twilio_auth()
        account_sid = _get_account_sid()
        
        if not base_url:
            base_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}"
        
        url = f"{base_url}/{endpoint.lstrip('/')}"
        
        auth = (username, password)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        print(f"🔄 Making Twilio API call: {method} {endpoint}")
        
        if method.upper() == "POST":
            response = requests.post(url, auth=auth, headers=headers, data=data, timeout=30)
        elif method.upper() == "GET":
            response = requests.get(url, auth=auth, params=data, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        print(f"📊 Twilio API Response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS! Twilio API call completed")
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            return {
                "error": True,
                "status_code": response.status_code,
                "message": error_data.get("message", f"Twilio API error: {response.status_code}"),
                "code": error_data.get("code"),
                "more_info": error_data.get("more_info")
            }
            
    except Exception as e:
        print(f"❌ Twilio API Error: {e}")
        return {
            "error": True,
            "message": f"Request failed: {str(e)}"
        }

# --- Core Messaging Tools ---

@tool("send_sms", args_schema=SMSInput)
def send_sms(to: str, body: str, from_: str = None) -> str:
    """
    Send SMS text message using Twilio.
    
    Args:
        to: Recipient phone number in E.164 format (e.g., +1234567890)
        body: Message content (up to 1600 characters)
        from_: Sender phone number (uses default if not provided)
    
    Returns:
        JSON string with message SID and status
    """
    
    if not from_:
        from_ = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
        if not from_:
            return json.dumps({
                "error": True,
                "message": "No sender phone number provided. Set TWILIO_PHONE_NUMBER or provide from_ parameter"
            })
    
    data = {
        "To": to,
        "From": from_,
        "Body": body
    }
    
    result = _make_twilio_request("POST", "Messages.json", data)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "status": "failed"
        })
    
    return json.dumps({
        "sid": result.get("sid"),
        "status": result.get("status"),
        "to": result.get("to"),
        "from": result.get("from"),
        "body": result.get("body"),
        "direction": result.get("direction"),
        "date_created": result.get("date_created"),
        "uri": result.get("uri")
    })

@tool("send_mms", args_schema=SMSInput)
def send_mms(to: str, body: str, media_url: List[str], from_: str = None) -> str:
    """
    Send MMS multimedia message using Twilio.
    
    Args:
        to: Recipient phone number in E.164 format
        body: Message content
        media_url: List of URLs for media attachments
        from_: Sender phone number (uses default if not provided)
    
    Returns:
        JSON string with message SID and status
    """
    
    if not from_:
        from_ = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
        if not from_:
            return json.dumps({
                "error": True,
                "message": "No sender phone number provided"
            })
    
    data = {
        "To": to,
        "From": from_,
        "Body": body
    }
    
    # Add media URLs
    for i, url in enumerate(media_url):
        data[f"MediaUrl"] = url  # Twilio accepts multiple MediaUrl parameters
    
    result = _make_twilio_request("POST", "Messages.json", data)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "status": "failed"
        })
    
    return json.dumps({
        "sid": result.get("sid"),
        "status": result.get("status"),
        "to": result.get("to"),
        "from": result.get("from"),
        "body": result.get("body"),
        "num_media": result.get("num_media"),
        "date_created": result.get("date_created")
    })

@tool("send_whatsapp", args_schema=SMSInput)
def send_whatsapp(to: str, body: str, from_: str = None) -> str:
    """
    Send WhatsApp message using Twilio WhatsApp Business API.
    
    Args:
        to: Recipient WhatsApp number (e.g., whatsapp:+1234567890)
        body: Message content
        from_: Sender WhatsApp number (e.g., whatsapp:+1987654321)
    
    Returns:
        JSON string with message SID and status
    """
    
    # Ensure WhatsApp prefix
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"
    
    if not from_:
        from_ = os.getenv("TWILIO_WHATSAPP_NUMBER", "").strip()
        if not from_:
            return json.dumps({
                "error": True,
                "message": "No WhatsApp sender number provided. Set TWILIO_WHATSAPP_NUMBER or provide from_ parameter"
            })
    
    if not from_.startswith("whatsapp:"):
        from_ = f"whatsapp:{from_}"
    
    data = {
        "To": to,
        "From": from_,
        "Body": body
    }
    
    result = _make_twilio_request("POST", "Messages.json", data)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "status": "failed"
        })
    
    return json.dumps({
        "sid": result.get("sid"),
        "status": result.get("status"),
        "to": result.get("to"),
        "from": result.get("from"),
        "body": result.get("body"),
        "date_created": result.get("date_created")
    })

# --- Voice Tools ---

@tool("make_call", args_schema=CallInput)
def make_call(to: str, from_: str = None, twiml: str = None, url: str = None) -> str:
    """
    Initiate voice call using Twilio.
    
    Args:
        to: Phone number to call in E.164 format
        from_: Caller ID (uses default if not provided)
        twiml: TwiML instructions for the call
        url: Webhook URL for dynamic TwiML (alternative to twiml)
    
    Returns:
        JSON string with call SID and status
    """
    
    if not from_:
        from_ = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
        if not from_:
            return json.dumps({
                "error": True,
                "message": "No caller phone number provided"
            })
    
    if not twiml and not url:
        twiml = '<Response><Say>Hello from Twilio!</Say></Response>'
    
    data = {
        "To": to,
        "From": from_
    }
    
    if twiml:
        data["Twiml"] = twiml
    elif url:
        data["Url"] = url
    
    result = _make_twilio_request("POST", "Calls.json", data)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "status": "failed"
        })
    
    return json.dumps({
        "sid": result.get("sid"),
        "status": result.get("status"),
        "to": result.get("to"),
        "from": result.get("from"),
        "direction": result.get("direction"),
        "date_created": result.get("date_created")
    })

# --- Email Tools (SendGrid) ---

@tool("send_email", args_schema=EmailInput)
def send_email(
    to: str,
    subject: str,
    from_: str = None,
    text_content: str = None,
    html_content: str = None
) -> str:
    """
    Send email using Twilio SendGrid.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        from_: Sender email address (uses default if not provided)
        text_content: Plain text email content
        html_content: HTML email content
    
    Returns:
        JSON string with email status
    """
    
    if not from_:
        from_ = os.getenv("SENDGRID_FROM_EMAIL", "").strip()
        if not from_:
            return json.dumps({
                "error": True,
                "message": "No sender email provided. Set SENDGRID_FROM_EMAIL or provide from_ parameter"
            })
    
    # SendGrid API requires different authentication
    api_key = os.getenv("SENDGRID_API_KEY", "").strip()
    if not api_key:
        return json.dumps({
            "error": True,
            "message": "SENDGRID_API_KEY environment variable not set"
        })
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    email_data = {
        "personalizations": [{
            "to": [{"email": to}],
            "subject": subject
        }],
        "from": {"email": from_},
        "content": []
    }
    
    if text_content:
        email_data["content"].append({
            "type": "text/plain",
            "value": text_content
        })
    
    if html_content:
        email_data["content"].append({
            "type": "text/html", 
            "value": html_content
        })
    
    if not email_data["content"]:
        return json.dumps({
            "error": True,
            "message": "Either text_content or html_content must be provided"
        })
    
    try:
        print(f"🔄 Sending email via SendGrid...")
        response = requests.post(url, headers=headers, json=email_data, timeout=30)
        
        print(f"📊 SendGrid Response: {response.status_code}")
        
        if response.status_code == 202:
            print("✅ SUCCESS! Email sent via SendGrid")
            return json.dumps({
                "status": "sent",
                "message_id": response.headers.get("X-Message-Id"),
                "to": to,
                "from": from_,
                "subject": subject
            })
        else:
            return json.dumps({
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            })
            
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"SendGrid request failed: {str(e)}"
        })

# --- Verification and Lookup Tools ---

@tool("verify_phone", args_schema=VerifyInput)
def verify_phone(phone_number: str, channel: str = "sms", locale: str = "en") -> str:
    """
    Send phone verification code using Twilio Verify.
    
    Args:
        phone_number: Phone number to verify in E.164 format
        channel: Verification channel (sms, call, email)
        locale: Language locale for verification message
    
    Returns:
        JSON string with verification SID and status
    """
    
    verify_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID", "").strip()
    if not verify_sid:
        return json.dumps({
            "error": True,
            "message": "TWILIO_VERIFY_SERVICE_SID environment variable not set"
        })
    
    base_url = f"https://verify.twilio.com/v2/Services/{verify_sid}"
    data = {
        "To": phone_number,
        "Channel": channel,
        "Locale": locale
    }
    
    result = _make_twilio_request("POST", "Verifications", data, base_url)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "status": "failed"
        })
    
    return json.dumps({
        "sid": result.get("sid"),
        "status": result.get("status"),
        "to": result.get("to"),
        "channel": result.get("channel"),
        "date_created": result.get("date_created")
    })

@tool("lookup_phone", args_schema=LookupInput)
def lookup_phone(phone_number: str, lookup_type: List[str] = ["carrier"]) -> str:
    """
    Lookup phone number information using Twilio Lookup.
    
    Args:
        phone_number: Phone number to lookup in E.164 format
        lookup_type: Types of information to retrieve (carrier, caller-name)
    
    Returns:
        JSON string with phone number information
    """
    
    # URL encode the phone number
    import urllib.parse
    encoded_number = urllib.parse.quote(phone_number)
    
    base_url = "https://lookups.twilio.com/v1/PhoneNumbers"
    params = {
        "Type": ",".join(lookup_type)
    }
    
    result = _make_twilio_request("GET", encoded_number, params, base_url)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    return json.dumps({
        "phone_number": result.get("phone_number"),
        "national_format": result.get("national_format"),
        "country_code": result.get("country_code"),
        "carrier": result.get("carrier", {}),
        "caller_name": result.get("caller_name", {}),
        "url": result.get("url")
    })

# --- Serverless Tools ---

@tool("upload_function", args_schema=FunctionInput)
def upload_function(
    service_sid: str,
    function_path: str,
    code: str,
    visibility: str = "protected"
) -> str:
    """
    Upload serverless function to Twilio Functions.
    
    Args:
        service_sid: Twilio Service SID for the function
        function_path: Function path (e.g., /hello-world)
        code: JavaScript code for the function
        visibility: Function visibility (public, protected, private)
    
    Returns:
        JSON string with function SID and status
    """
    
    base_url = f"https://serverless.twilio.com/v1/Services/{service_sid}"
    
    # First, create or update the function
    function_data = {
        "FriendlyName": function_path.strip("/"),
        "Visibility": visibility
    }
    
    result = _make_twilio_request("POST", "Functions", function_data, base_url)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    function_sid = result.get("sid")
    
    # Upload the function code
    version_data = {
        "Path": function_path,
        "Content": code,
        "Visibility": visibility
    }
    
    version_result = _make_twilio_request(
        "POST", 
        f"Functions/{function_sid}/Versions",
        version_data,
        base_url
    )
    
    if version_result.get("error"):
        return json.dumps({
            "error": True,
            "message": version_result.get("message")
        })
    
    return json.dumps({
        "function_sid": function_sid,
        "version_sid": version_result.get("sid"),
        "path": function_path,
        "visibility": visibility,
        "status": "uploaded"
    })

@tool("upload_asset", args_schema=AssetInput)
def upload_asset(
    service_sid: str,
    asset_path: str,
    content: str,
    content_type: str
) -> str:
    """
    Upload static asset to Twilio Functions.
    
    Args:
        service_sid: Twilio Service SID for the asset
        asset_path: Asset path (e.g., /style.css)
        content: Asset content
        content_type: MIME type (e.g., text/css, image/png)
    
    Returns:
        JSON string with asset SID and status
    """
    
    base_url = f"https://serverless.twilio.com/v1/Services/{service_sid}"
    
    # Create the asset
    asset_data = {
        "FriendlyName": asset_path.strip("/"),
        "Visibility": "public"  # Assets are typically public
    }
    
    result = _make_twilio_request("POST", "Assets", asset_data, base_url)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    asset_sid = result.get("sid")
    
    # Upload the asset content
    version_data = {
        "Path": asset_path,
        "Content": content,
        "ContentType": content_type
    }
    
    version_result = _make_twilio_request(
        "POST",
        f"Assets/{asset_sid}/Versions", 
        version_data,
        base_url
    )
    
    if version_result.get("error"):
        return json.dumps({
            "error": True,
            "message": version_result.get("message")
        })
    
    return json.dumps({
        "asset_sid": asset_sid,
        "version_sid": version_result.get("sid"),
        "path": asset_path,
        "content_type": content_type,
        "status": "uploaded"
    })

# --- Advanced Communication Tools ---

@tool("create_conversation")
def create_conversation(unique_name: str, friendly_name: str = None) -> str:
    """
    Create conversation channel for multi-party messaging.
    
    Args:
        unique_name: Unique identifier for the conversation
        friendly_name: Human-readable name for the conversation
    
    Returns:
        JSON string with conversation SID and details
    """
    
    base_url = "https://conversations.twilio.com/v1"
    
    data = {
        "UniqueName": unique_name
    }
    
    if friendly_name:
        data["FriendlyName"] = friendly_name
    
    result = _make_twilio_request("POST", "Conversations", data, base_url)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    return json.dumps({
        "sid": result.get("sid"),
        "unique_name": result.get("unique_name"),
        "friendly_name": result.get("friendly_name"),
        "state": result.get("state"),
        "date_created": result.get("date_created")
    })

@tool("start_video_room")
def start_video_room(
    unique_name: str,
    room_type: str = "group",
    record_participants: bool = False
) -> str:
    """
    Create video room for video conferencing.
    
    Args:
        unique_name: Unique identifier for the video room
        room_type: Type of room (group, peer-to-peer, go)
        record_participants: Whether to record participants
    
    Returns:
        JSON string with room SID and connection details
    """
    
    base_url = "https://video.twilio.com/v1"
    
    data = {
        "UniqueName": unique_name,
        "Type": room_type,
        "RecordParticipantsOnConnect": record_participants
    }
    
    result = _make_twilio_request("POST", "Rooms", data, base_url)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    return json.dumps({
        "sid": result.get("sid"),
        "unique_name": result.get("unique_name"),
        "status": result.get("status"),
        "type": result.get("type"),
        "record_participants": result.get("record_participants_on_connect"),
        "date_created": result.get("date_created")
    })

@tool("sync_data")
def sync_data(service_sid: str, document_unique_name: str, data: Dict[str, Any]) -> str:
    """
    Manage real-time data synchronization using Twilio Sync.
    
    Args:
        service_sid: Twilio Sync Service SID
        document_unique_name: Unique name for the sync document
        data: Data to synchronize
    
    Returns:
        JSON string with sync document SID and status
    """
    
    base_url = f"https://sync.twilio.com/v1/Services/{service_sid}"
    
    sync_data = {
        "UniqueName": document_unique_name,
        "Data": json.dumps(data)
    }
    
    result = _make_twilio_request("POST", "Documents", sync_data, base_url)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    return json.dumps({
        "sid": result.get("sid"),
        "unique_name": result.get("unique_name"),
        "data": result.get("data"),
        "revision": result.get("revision"),
        "date_created": result.get("date_created")
    })

# --- Tool Collections ---

def get_twilio_tools():
    """Get all Twilio tools."""
    return [
        send_sms,
        send_mms,
        send_whatsapp,
        make_call,
        send_email,
        verify_phone,
        lookup_phone,
        upload_function,
        upload_asset,
        create_conversation,
        start_video_room,
        sync_data
    ]

def get_messaging_tools():
    """Get messaging-specific tools."""
    return [
        send_sms,
        send_mms,
        send_whatsapp
    ]

def get_voice_tools():
    """Get voice-specific tools."""
    return [
        make_call
    ]

def get_verification_tools():
    """Get verification and lookup tools."""
    return [
        verify_phone,
        lookup_phone
    ]
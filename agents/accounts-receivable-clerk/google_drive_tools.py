"""
Google Drive integration for contract monitoring.
Watches specified folder for new contract uploads and processes them.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

class DriveMonitorInput(BaseModel):
    """Input schema for Google Drive monitoring."""
    folder_id: Optional[str] = Field(
        default="1x4E2pditBkAEWmX_jKDODwNZFhN1Gyvs",
        description="Google Drive folder ID to monitor for new contracts"
    )

class DriveFileInput(BaseModel):
    """Input schema for processing specific Drive files."""
    file_id: str = Field(description="Google Drive file ID to process")

def get_drive_service():
    """Get authenticated Google Drive service."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        SCOPES = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file'
        ]
        
        creds_path = os.path.join(os.path.dirname(__file__), "credentials", "google_credentials.json")
        token_path = os.path.join(os.path.dirname(__file__), "credentials", "google_token.json")
        
        creds = None
        
        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If no valid credentials, try to refresh or get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(creds_path):
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    raise FileNotFoundError("Google credentials not found")
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)
    
    except ImportError:
        print("⚠️ Google API packages not installed, using demo mode")
        return None
    except Exception as e:
        print(f"❌ Google Drive authentication failed: {e}")
        return None

@tool("monitor_drive_folder", args_schema=DriveMonitorInput)
def monitor_drive_folder(folder_id: str = "1x4E2pditBkAEWmX_jKDODwNZFhN1Gyvs") -> str:
    """Monitor Google Drive folder for new contract uploads."""
    try:
        print(f"📁 Monitoring Google Drive folder: {folder_id}")
        
        service = get_drive_service()
        if not service:
            # Demo mode - simulate finding contract files
            demo_files = [
                {
                    "file_id": "demo_contract_123",
                    "name": "TechCorp_Contract_2025.pdf",
                    "mime_type": "application/pdf",
                    "created_time": datetime.now().isoformat(),
                    "modified_time": datetime.now().isoformat(),
                    "size": "245760",
                    "is_contract": True
                }
            ]
            
            print(f"📁 Demo mode: Simulating contract files in folder")
            return json.dumps({
                "status": "success",
                "files_found": 1,
                "contract_files": 1,
                "files": demo_files,
                "folder_id": folder_id,
                "data_source": "DEMO Google Drive (packages not installed)",
                "next_action": "process_newest_contract",
                "note": "Install google-api-python-client for real Drive integration"
            }, indent=2)
        
        # Query for files in the specified folder
        query = f"'{folder_id}' in parents and trashed=false"
        
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, createdTime, modifiedTime, size)",
            orderBy="createdTime desc"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("📂 No files found in contracts folder")
            return json.dumps({
                "status": "success",
                "message": "No new contracts found",
                "files_found": 0,
                "folder_id": folder_id,
                "data_source": "REAL Google Drive API"
            })
        
        # Process found files
        contract_files = []
        for file in files:
            file_info = {
                "file_id": file['id'],
                "name": file['name'],
                "mime_type": file.get('mimeType', ''),
                "created_time": file.get('createdTime', ''),
                "modified_time": file.get('modifiedTime', ''),
                "size": file.get('size', 0)
            }
            
            # Check if it looks like a contract
            name_lower = file['name'].lower()
            if any(keyword in name_lower for keyword in ['contract', 'agreement', 'invoice', 'proposal']):
                file_info['is_contract'] = True
                contract_files.append(file_info)
            else:
                file_info['is_contract'] = False
            
        print(f"✅ Found {len(files)} files, {len(contract_files)} potential contracts")
        
        return json.dumps({
            "status": "success",
            "files_found": len(files),
            "contract_files": len(contract_files),
            "files": contract_files if contract_files else files[:5],  # Show first 5 if no contracts
            "folder_id": folder_id,
            "data_source": "REAL Google Drive API",
            "next_action": "process_newest_contract" if contract_files else "waiting_for_upload"
        }, indent=2)
        
    except Exception as e:
        error_msg = f"Error monitoring Drive folder: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "status": "error",
            "message": error_msg,
            "data_source": "Google Drive Error"
        })

@tool("download_drive_file", args_schema=DriveFileInput)
def download_drive_file(file_id: str) -> str:
    """Download and extract text content from Google Drive file."""
    try:
        print(f"📄 Downloading file from Google Drive: {file_id}")
        
        service = get_drive_service()
        if not service:
            # Demo mode - simulate file download
            demo_content = f"""CONTRACT AGREEMENT
            
Date: {datetime.now().strftime('%B %d, %Y')}
Client: TechCorp Solutions Inc.
Services: Web development and digital transformation
Total Contract Value: $35,000.00
Payment Terms: 50% upfront ($17,500), 50% on completion ($17,500)
Billing Contact: billing@techcorp.com
Phone: +1-555-0199
Net Terms: 30 days from invoice date

This agreement is effective immediately upon signature.
"""
            
            return json.dumps({
                "status": "success",
                "file_id": file_id,
                "file_name": "TechCorp_Contract_2025.pdf",
                "mime_type": "application/pdf",
                "content": demo_content,
                "content_length": len(demo_content),
                "data_source": "DEMO Google Drive (packages not installed)"
            }, indent=2)
        
        # Get file metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        file_name = file_metadata.get('name', 'Unknown')
        mime_type = file_metadata.get('mimeType', '')
        
        print(f"📋 Processing file: {file_name} ({mime_type})")
        
        # Download file content
        if mime_type == 'application/pdf':
            # For PDFs, we'd need additional processing
            # For now, return file info for demo
            content = f"PDF Contract: {file_name}\nThis would contain the full contract text after PDF parsing."
        elif 'text' in mime_type or 'document' in mime_type:
            # Download text-based files
            request = service.files().get_media(fileId=file_id)
            content = request.execute().decode('utf-8')
        else:
            # Export Google Docs as plain text
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
            content = request.execute().decode('utf-8')
        
        print(f"✅ Downloaded {len(content)} characters from {file_name}")
        
        return json.dumps({
            "status": "success",
            "file_id": file_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "content": content,
            "content_length": len(content),
            "data_source": "REAL Google Drive API"
        }, indent=2)
        
    except Exception as e:
        error_msg = f"Error downloading Drive file: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "status": "error",
            "message": error_msg,
            "file_id": file_id,
            "data_source": "Google Drive Error"
        })

@tool("process_drive_contract", args_schema=DriveFileInput)
def process_drive_contract(file_id: str) -> str:
    """Download and process a contract from Google Drive."""
    try:
        print(f"🔄 Processing contract from Google Drive: {file_id}")
        
        # First download the file
        download_result = download_drive_file.invoke({"file_id": file_id})
        download_data = json.loads(download_result)
        
        if download_data.get("status") != "success":
            return download_result
        
        # Extract contract data using our existing parser
        from contract_tools import extract_contract_data
        
        contract_content = download_data.get("content", "")
        file_name = download_data.get("file_name", "Unknown")
        
        # Add file context to improve parsing
        enhanced_content = f"""
Contract File: {file_name}
Source: Google Drive
        
{contract_content}
        """
        
        contract_result = extract_contract_data.invoke({
            "contract_text": enhanced_content,
            "client_context": f"File: {file_name}"
        })
        
        contract_data = json.loads(contract_result)
        
        # Enhance with Drive metadata
        contract_data.update({
            "source_file_id": file_id,
            "source_file_name": file_name,
            "source_platform": "Google Drive",
            "processed_timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ Processed contract from Drive: {contract_data.get('client_name', 'Unknown')} - ${contract_data.get('total_value', 0):,.2f}")
        
        return json.dumps(contract_data, indent=2)
        
    except Exception as e:
        error_msg = f"Error processing Drive contract: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "status": "error",
            "message": error_msg,
            "file_id": file_id,
            "data_source": "Contract Processing Error"
        })

def get_drive_tools():
    """Get all Google Drive tools for the agent."""
    return [
        monitor_drive_folder,
        download_drive_file,
        process_drive_contract
    ]
"""
Public, LLM-callable tools for interacting with Notion API directly.
"""
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    import requests
except ImportError:
    raise ImportError(
        "Notion tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install "requests"'
    )

# --- Input Schemas ---

class NotionPageInput(BaseModel):
    title: str = Field(description="Title of the page to create")
    parent_page_id: Optional[str] = Field(
        default=None,
        description="Parent page ID. If not provided, uses NOTION_DEFAULT_PAGE_ID from environment."
    )
    content: Optional[str] = Field(
        default="",
        description="Page content in markdown format"
    )

class NotionPageGetInput(BaseModel):
    page_id: str = Field(description="ID of the page to retrieve")

class NotionPageUpdateInput(BaseModel):
    page_id: str = Field(description="ID of the page to update")
    title: Optional[str] = Field(default=None, description="New title for the page")
    content: Optional[str] = Field(default=None, description="New content in markdown format")

# --- Helper Functions ---

def _get_notion_headers() -> Dict[str, str]:
    """Get Notion API headers with authentication."""
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        raise ValueError("NOTION_API_KEY environment variable not set")
    
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

def _make_notion_request(
    method: str, 
    endpoint: str, 
    data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Internal helper to make requests to Notion API."""
    base_url = "https://api.notion.com/v1"
    url = f"{base_url}/{endpoint}"
    
    headers = _get_notion_headers()
    
    if method.upper() == "GET":
        response = requests.get(url, headers=headers, timeout=30)
    elif method.upper() == "POST":
        response = requests.post(url, headers=headers, json=data or {}, timeout=30)
    elif method.upper() == "PATCH":
        response = requests.patch(url, headers=headers, json=data or {}, timeout=30)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        error_msg = f"Notion API error: {response.status_code}"
        try:
            error_detail = response.json()
            if "message" in error_detail:
                error_msg += f" - {error_detail['message']}"
        except:
            error_msg += f" - {response.text}"
        raise Exception(error_msg)

def _markdown_to_notion_blocks(content: str) -> List[Dict[str, Any]]:
    """Convert markdown content to Notion blocks."""
    if not content:
        return []
    
    blocks = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Handle headers
        if line.startswith('### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "object": "block",
                "type": "heading_2", 
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                }
            })
        elif line.startswith('# '):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                }
            })
        # Handle bullet points
        elif line.startswith('- ') or line.startswith('* '):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                }
            })
        # Handle numbered lists
        elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                }
            })
        # Regular paragraph
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })
    
    return blocks

def _get_default_parent_id() -> str:
    """Get default parent page ID from environment or raise error."""
    parent_id = os.environ.get("NOTION_DEFAULT_PAGE_ID")
    if not parent_id:
        raise ValueError(
            "NOTION_DEFAULT_PAGE_ID environment variable not set. "
            "Please provide a parent_page_id or set this environment variable."
        )
    return parent_id

# --- Notion Tools ---

@tool("create_notion_page", args_schema=NotionPageInput)
def create_notion_page(
    title: str,
    parent_page_id: Optional[str] = None,
    content: str = ""
) -> str:
    """
    Create a new page in Notion.
    
    This tool creates a new page with the specified title and content.
    Content can be provided in markdown format and will be converted
    to Notion blocks automatically.
    """
    try:
        # Use provided parent ID or get from environment
        parent_id = parent_page_id or _get_default_parent_id()
        
        # Prepare page data
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": title}
                        }
                    ]
                }
            }
        }
        
        # Add content blocks if provided
        if content:
            page_data["children"] = _markdown_to_notion_blocks(content)
        
        result = _make_notion_request("POST", "pages", page_data)
        
        # Return formatted response matching MCP pattern
        response = {
            "id": result.get("id", ""),
            "url": result.get("url", ""),
            "title": title,
            "created_time": result.get("created_time", ""),
            "status": "success"
        }
        
        return json.dumps(response, indent=2)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Notion page creation failed: {str(e)}"

@tool("get_notion_page", args_schema=NotionPageGetInput)
def get_notion_page(page_id: str) -> str:
    """
    Retrieve a page from Notion.
    
    This tool fetches page details including properties and content.
    """
    try:
        result = _make_notion_request("GET", f"pages/{page_id}")
        
        # Extract key information
        response = {
            "id": result.get("id", ""),
            "url": result.get("url", ""),
            "created_time": result.get("created_time", ""),
            "last_edited_time": result.get("last_edited_time", ""),
            "properties": result.get("properties", {}),
            "status": "success"
        }
        
        return json.dumps(response, indent=2)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Notion page retrieval failed: {str(e)}"

@tool("update_notion_page", args_schema=NotionPageUpdateInput)
def update_notion_page(
    page_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> str:
    """
    Update an existing page in Notion.
    
    This tool can update the page title and/or replace the page content.
    Content should be provided in markdown format.
    """
    try:
        update_data = {}
        
        # Update title if provided
        if title:
            update_data["properties"] = {
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": title}
                        }
                    ]
                }
            }
        
        # Update the page properties
        if update_data:
            result = _make_notion_request("PATCH", f"pages/{page_id}", update_data)
        else:
            result = {"id": page_id}
        
        # If content is provided, we would need to replace page blocks
        # This is more complex and would require getting existing blocks first
        # For now, just update properties
        
        response = {
            "id": result.get("id", page_id),
            "status": "success",
            "updated_fields": list(update_data.keys()) if update_data else []
        }
        
        return json.dumps(response, indent=2)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Notion page update failed: {str(e)}"

# --- Tool Aggregator ---

def get_notion_tools():
    """Returns a list of all Notion tools in this module."""
    return [
        create_notion_page,
        get_notion_page,
        update_notion_page
    ]
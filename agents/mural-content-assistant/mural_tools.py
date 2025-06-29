"""
Mural API Integration Tools for Braid
Direct API integration following Braid patterns
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Mural API Configuration
MURAL_BASE_URL = "https://app.mural.co/api/public/v1"
MURAL_ACCESS_TOKEN = os.environ.get("MURAL_ACCESS_TOKEN")
MURAL_DEFAULT_WORKSPACE_ID = os.environ.get("MURAL_DEFAULT_WORKSPACE_ID")
MURAL_DEFAULT_ROOM_ID = os.environ.get("MURAL_DEFAULT_ROOM_ID")

def get_mural_headers() -> Dict[str, str]:
    """Get headers for Mural API requests."""
    if not MURAL_ACCESS_TOKEN:
        return {}
    return {
        "Authorization": f"Bearer {MURAL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def handle_mural_response(response: requests.Response, operation: str) -> Dict[str, Any]:
    """Handle Mural API response with proper error handling."""
    try:
        if response.status_code == 200:
            data = response.json()
            # Handle different response formats
            if "value" in data:
                result_data = data["value"]
            else:
                result_data = data
            
            return {
                "value": result_data,
                "data_source": "REAL Mural API - Direct Integration",
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        elif response.status_code == 201:
            data = response.json()
            return {
                **data.get("value", data),
                "data_source": "REAL Mural API - Direct Integration", 
                "timestamp": datetime.now().isoformat(),
                "status": "created"
            }
        else:
            error_data = response.json() if response.text else {}
            return {
                "error": True,
                "status_code": response.status_code,
                "message": error_data.get("message", f"Mural API error: {response.status_code}"),
                "operation": operation,
                "data_source": "Mural API Error",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "error": True,
            "message": f"Failed to process Mural API response for {operation}: {str(e)}",
            "data_source": "Mural API Failed - Processing Error",
            "timestamp": datetime.now().isoformat(),
            "fallback_available": True
        }

# Pydantic schemas for tool inputs
class CreateMuralInput(BaseModel):
    title: str = Field(description="Title of the mural to create")
    room_id: Optional[str] = Field(default=None, description="Room ID where mural should be created (optional)")
    workspace_id: Optional[str] = Field(default=None, description="Workspace ID (optional)")
    template_id: Optional[str] = Field(default=None, description="Template ID to create mural from (optional - if not provided, creates blank mural)")

class CreateStickyNoteInput(BaseModel):
    mural_id: str = Field(description="ID of the mural to add sticky note to")
    text: str = Field(description="Text content of the sticky note")
    x: Optional[int] = Field(default=None, description="X position on mural (optional - if not provided, will auto-place intelligently)")
    y: Optional[int] = Field(default=None, description="Y position on mural (optional - if not provided, will auto-place intelligently)")
    color: Optional[str] = Field(default="yellow", description="Color of the sticky note. Options: yellow, blue, green, red, orange, purple, pink, or hex code like #FF5733")
    placement_context: Optional[str] = Field(default=None, description="Placement strategy hint: 'list', 'grid', 'horizontal', or 'general' (optional - auto-detected if not provided)")

class CreateTextboxInput(BaseModel):
    mural_id: str = Field(description="ID of the mural to add text box to")
    text: str = Field(description="Text content of the text box")
    x: Optional[int] = Field(default=100, description="X position on mural (optional)")
    y: Optional[int] = Field(default=200, description="Y position on mural (optional)")

class CreateTitleInput(BaseModel):
    mural_id: str = Field(description="ID of the mural to add title to")
    text: str = Field(description="Title text")
    x: Optional[int] = Field(default=100, description="X position on mural (optional)")
    y: Optional[int] = Field(default=50, description="Y position on mural (optional)")

class SearchMuralsInput(BaseModel):
    query: str = Field(description="Search query for finding murals")
    workspace_id: Optional[str] = Field(default=None, description="Workspace ID to search within (optional)")

class InviteUsersInput(BaseModel):
    mural_id: str = Field(description="ID of the mural to invite users to")
    emails: List[str] = Field(description="List of email addresses to invite")
    role: Optional[str] = Field(default="member", description="Role for invited users (member, guest)")

class CreateFromTemplateUrlInput(BaseModel):
    title: str = Field(description="Title of the mural to create")
    template_url: str = Field(description="Full URL of the template to use")
    room_id: Optional[str] = Field(default=None, description="Room ID where mural should be created (optional)")

def extract_template_id_from_url(template_url: str) -> Optional[str]:
    """Extract template ID from a Mural template URL."""
    try:
        # Template URLs typically look like:
        # https://app.mural.co/template/8abe326c-4f8e-4c14-b480-837a7d5d868f/39d667d7-0b42-4205-a3fe-92e29527e13f
        if "/template/" in template_url:
            parts = template_url.split("/template/")
            if len(parts) > 1:
                # Get the part after /template/ and extract the first ID (before the next /)
                template_part = parts[1].split("/")[0]
                return template_part
        return None
    except Exception:
        return None

def get_sticky_note_color(color: str) -> str:
    """Convert color name to hex code for sticky notes."""
    color_map = {
        "yellow": "#FFFF88FF",
        "blue": "#87CEEBFF", 
        "green": "#90EE90FF",
        "red": "#FFB6C1FF",
        "orange": "#FFA07AFF",
        "purple": "#DDA0DDFF",
        "pink": "#FFB6C1FF",
        "white": "#FFFFFFFF",
        "gray": "#D3D3D3FF",
        "black": "#000000FF"
    }
    
    # If it's already a hex code, return as is (add FF for alpha if 6 chars)
    if color.startswith("#"):
        if len(color) == 7:  # #RRGGBB format
            return color + "FF"  # Add alpha channel
        return color
    
    # Convert color name to lowercase and return hex code
    return color_map.get(color.lower(), "#FFFF88FF")  # Default to yellow

def calculate_smart_position(mural_id: str, placement_context: str = "general") -> tuple:
    """
    Calculate intelligent positioning for new sticky notes based on existing content.
    Returns (x, y) coordinates for optimal placement.
    """
    try:
        # Get existing widgets and mural dimensions
        widgets_result = get_mural_widgets.invoke({"mural_id": mural_id})
        widgets_data = json.loads(widgets_result)
        
        details_result = get_mural_details.invoke({"mural_id": mural_id})
        details_data = json.loads(details_result)
        
        if "error" in widgets_data or "error" in details_data:
            # Fallback to safe default position
            return 100, 100
        
        # Extract mural info and existing widgets
        mural_info = details_data.get("value", {})
        canvas_width = mural_info.get("width", 9216)
        canvas_height = mural_info.get("height", 6237)
        existing_widgets = widgets_data.get("value", [])
        
        # Default widget dimensions and spacing
        margin = 50
        widget_width = 150
        widget_height = 150
        spacing = 20
        
        # Build occupied positions list
        occupied_positions = []
        for widget in existing_widgets:
            x = widget.get("x", 0)
            y = widget.get("y", 0)
            w = widget.get("width", widget_width)
            h = widget.get("height", widget_height)
            occupied_positions.append({
                "x1": x, "y1": y,
                "x2": x + w, "y2": y + h
            })
        
        # Different placement strategies based on context
        if placement_context in ["list", "column", "vertical"]:
            # Vertical list placement - find next position in left column
            start_x = margin
            start_y = margin
            
            # Find the bottom-most widget in the left third of canvas
            for pos in occupied_positions:
                if pos["x1"] < canvas_width // 3:
                    start_y = max(start_y, pos["y2"] + spacing)
            
            return start_x, start_y
            
        elif placement_context in ["grid", "matrix", "organized"]:
            # Grid placement - find next free grid position
            cols = min(6, (canvas_width - 2 * margin) // (widget_width + spacing))
            
            for row in range(20):  # Try up to 20 rows
                for col in range(cols):
                    x = margin + col * (widget_width + spacing)
                    y = margin + row * (widget_height + spacing)
                    
                    # Check if position is free
                    is_free = True
                    for pos in occupied_positions:
                        if not (x + widget_width < pos["x1"] or x > pos["x2"] or 
                               y + widget_height < pos["y1"] or y > pos["y2"]):
                            is_free = False
                            break
                    
                    if is_free and y + widget_height < canvas_height:
                        return x, y
        
        elif placement_context in ["horizontal", "row"]:
            # Horizontal row placement
            start_x = margin
            start_y = margin
            
            # Find rightmost widget in top area
            for pos in occupied_positions:
                if pos["y1"] < canvas_height // 3:
                    start_x = max(start_x, pos["x2"] + spacing)
            
            return start_x, start_y
        
        else:  # general placement - find first available space
            # Try to place in reading order (top-left to bottom-right)
            for y in range(margin, canvas_height - widget_height, widget_height + spacing):
                for x in range(margin, canvas_width - widget_width, widget_width + spacing):
                    # Check if position is free
                    is_free = True
                    for pos in occupied_positions:
                        if not (x + widget_width < pos["x1"] or x > pos["x2"] or 
                               y + widget_height < pos["y1"] or y > pos["y2"]):
                            is_free = False
                            break
                    
                    if is_free:
                        return x, y
        
        # Fallback: place at bottom of existing content
        max_y = max([pos["y2"] for pos in occupied_positions] + [margin])
        return margin, max_y + spacing
        
    except Exception as e:
        # Ultimate fallback
        return 100, 100

def detect_placement_context(text: str, mural_context: dict = None) -> str:
    """
    Detect the appropriate placement context based on sticky note content and mural context.
    """
    text_lower = text.lower()
    
    # Context keywords for different placement strategies
    list_keywords = ["todo", "task", "action", "step", "item", "priority", "checklist"]
    grid_keywords = ["category", "matrix", "framework", "quadrant", "grid", "organize"]
    horizontal_keywords = ["timeline", "sequence", "flow", "process", "stage", "phase"]
    
    # Check for list context
    if any(keyword in text_lower for keyword in list_keywords):
        return "list"
    
    # Check for grid context  
    if any(keyword in text_lower for keyword in grid_keywords):
        return "grid"
    
    # Check for horizontal context
    if any(keyword in text_lower for keyword in horizontal_keywords):
        return "horizontal"
    
    # Default to general placement
    return "general"

# MURAL MANAGEMENT TOOLS

@tool("create_mural", args_schema=CreateMuralInput)
def create_mural(title: str, room_id: Optional[str] = None, workspace_id: Optional[str] = None, template_id: Optional[str] = None) -> str:
    """Create a new mural in Mural workspace. Can create from template or blank. Returns mural details including URL."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured. Please set MURAL_ACCESS_TOKEN environment variable.",
                "data_source": "Configuration Error"
            })

        # Use default room if not specified
        target_room_id = room_id or MURAL_DEFAULT_ROOM_ID
        if not target_room_id:
            return json.dumps({
                "error": True,
                "message": "No room ID specified and no default room configured. Please provide a room_id or set MURAL_DEFAULT_ROOM_ID.",
                "data_source": "Configuration Error"
            })

        # Determine if creating from template or blank mural
        if template_id:
            # Create mural from template using template endpoint
            payload = {
                "title": title,
                "roomId": int(target_room_id)
            }
            
            response = requests.post(
                f"{MURAL_BASE_URL}/templates/{template_id}/murals",
                headers=get_mural_headers(),
                json=payload
            )
        else:
            # Create blank mural using standard endpoint
            payload = {
                "title": title,
                "roomId": int(target_room_id)  # Convert to integer as required by API
            }

            response = requests.post(
                f"{MURAL_BASE_URL}/murals",
                headers=get_mural_headers(),
                json=payload
            )

        # Handle specific error cases before general processing
        if response.status_code == 403:
            try:
                error_data = response.json()
                if error_data.get("code") == "MURAL_CREATE_FORBIDDEN":
                    return json.dumps({
                        "error": True,
                        "message": "Your Mural workspace has reached the maximum number of murals allowed by your plan. You can delete an existing mural to create a new one, or upgrade your plan.",
                        "data_source": "Mural API - Plan Limit",
                        "suggestion": "Try deleting an unused mural first, or contact your Mural administrator about upgrading the workspace plan.",
                        "plan_limit_reached": True
                    })
            except:
                pass
        
        result = handle_mural_response(response, "create_mural")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to create mural: {str(e)}",
            "data_source": "Mural API Failed",
            "fallback": {
                "title": title,
                "id": "demo-mural-123",
                "url": "https://app.mural.co/t/demo/m/demo/demo123",
                "data_source": "Demo Data - API Error"
            }
        })

@tool("create_mural_from_template_url", args_schema=CreateFromTemplateUrlInput)
def create_mural_from_template_url(title: str, template_url: str, room_id: Optional[str] = None) -> str:
    """Create a new mural from a template URL. Extracts template ID from URL and creates mural."""
    try:
        # Extract template ID from the URL
        template_id = extract_template_id_from_url(template_url)
        if not template_id:
            return json.dumps({
                "error": True,
                "message": f"Could not extract template ID from URL: {template_url}",
                "data_source": "URL Parsing Error"
            })
        
        # Use the existing create_mural function with the extracted template ID
        result = create_mural.invoke({"title": title, "room_id": room_id, "template_id": template_id})
        return result
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to create mural from template URL: {str(e)}",
            "data_source": "Template URL Creation Failed",
            "fallback": {
                "title": title,
                "template_url": template_url,
                "data_source": "Demo Data - API Error"
            }
        })

@tool("get_mural_details", args_schema=None)
def get_mural_details(mural_id: str) -> str:
    """Get detailed information about a specific mural."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        response = requests.get(
            f"{MURAL_BASE_URL}/murals/{mural_id}",
            headers=get_mural_headers()
        )

        result = handle_mural_response(response, "get_mural_details")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to get mural details: {str(e)}",
            "data_source": "Mural API Failed",
            "fallback": {
                "id": mural_id,
                "title": "Sample Mural",
                "url": f"https://app.mural.co/t/demo/m/demo/{mural_id}",
                "data_source": "Demo Data - API Error"
            }
        })

@tool("search_murals", args_schema=SearchMuralsInput)
def search_murals(query: str, workspace_id: Optional[str] = None) -> str:
    """Search for murals by keywords in workspace murals (fallback to get workspace murals and filter)."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        # Use workspace_id or default
        target_workspace = workspace_id or MURAL_DEFAULT_WORKSPACE_ID
        if not target_workspace:
            return json.dumps({
                "error": True,
                "message": "No workspace ID specified and no default configured.",
                "data_source": "Configuration Error"
            })

        # Get all murals in workspace and filter by query
        response = requests.get(
            f"{MURAL_BASE_URL}/workspaces/{target_workspace}/murals",
            headers=get_mural_headers()
        )

        result = handle_mural_response(response, "search_murals")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to search murals: {str(e)}",
            "data_source": "Mural API Failed",
            "fallback": {
                "murals": [
                    {
                        "id": "demo-1",
                        "title": f"Sample mural matching '{query}'",
                        "url": "https://app.mural.co/t/demo/m/demo/demo1"
                    }
                ],
                "data_source": "Demo Data - API Error"
            }
        })

@tool("get_workspace_murals", args_schema=None)
def get_workspace_murals(workspace_id: Optional[str] = None) -> str:
    """Get all murals in a workspace."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        target_workspace = workspace_id or MURAL_DEFAULT_WORKSPACE_ID
        if not target_workspace:
            return json.dumps({
                "error": True,
                "message": "No workspace ID specified and no default configured.",
                "data_source": "Configuration Error"
            })

        response = requests.get(
            f"{MURAL_BASE_URL}/workspaces/{target_workspace}/murals",
            headers=get_mural_headers()
        )

        result = handle_mural_response(response, "get_workspace_murals")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to get workspace murals: {str(e)}",
            "data_source": "Mural API Failed"
        })

# CONTENT CREATION TOOLS

@tool("create_sticky_note", args_schema=CreateStickyNoteInput)
def create_sticky_note(mural_id: str, text: str, x: Optional[int] = None, y: Optional[int] = None, color: str = "yellow", placement_context: Optional[str] = None) -> str:
    """Create a sticky note widget in a mural with intelligent auto-placement and customizable color."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        # Handle intelligent auto-placement
        if x is None or y is None:
            # Detect placement context if not provided
            if placement_context is None:
                placement_context = detect_placement_context(text)
            
            # Calculate smart position
            auto_x, auto_y = calculate_smart_position(mural_id, placement_context)
            final_x = x if x is not None else auto_x
            final_y = y if y is not None else auto_y
            placement_info = {
                "auto_placed": True,
                "strategy": placement_context,
                "position": f"({final_x}, {final_y})"
            }
        else:
            final_x, final_y = x, y
            placement_info = {
                "auto_placed": False,
                "strategy": "manual",
                "position": f"({final_x}, {final_y})"
            }
        
        # Get hex color code
        background_color = get_sticky_note_color(color)
        
        payload = {
            "text": text,
            "x": final_x,
            "y": final_y,
            "width": 150,
            "height": 150,
            "shape": "rectangle",
            "style": {
                "backgroundColor": background_color,
                "bold": False,
                "font": "proxima-nova",
                "fontSize": 23,
                "italic": False,
                "strike": False,
                "textAlign": "center",
                "underline": False,
                "border": False
            }
        }

        response = requests.post(
            f"{MURAL_BASE_URL}/murals/{mural_id}/widgets/sticky-note",
            headers=get_mural_headers(),
            json=payload
        )

        result = handle_mural_response(response, "create_sticky_note")
        
        # Add placement information to the result
        if isinstance(result, dict) and "error" not in result:
            result["placement_info"] = placement_info
        
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to create sticky note: {str(e)}",
            "data_source": "Mural API Failed",
            "fallback": {
                "id": "demo-sticky-123",
                "text": text,
                "data_source": "Demo Data - API Error"
            }
        })

@tool("create_textbox", args_schema=CreateTextboxInput)
def create_textbox(mural_id: str, text: str, x: int = 100, y: int = 200) -> str:
    """Create a text box widget in a mural."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        payload = {
            "text": text,
            "x": x,
            "y": y,
            "width": 300,
            "height": 100
        }

        response = requests.post(
            f"{MURAL_BASE_URL}/murals/{mural_id}/widgets/textbox",
            headers=get_mural_headers(),
            json=payload
        )

        result = handle_mural_response(response, "create_textbox")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to create text box: {str(e)}",
            "data_source": "Mural API Failed",
            "fallback": {
                "id": "demo-textbox-123",
                "text": text,
                "data_source": "Demo Data - API Error"
            }
        })

@tool("create_title", args_schema=CreateTitleInput)
def create_title(mural_id: str, text: str, x: int = 100, y: int = 50) -> str:
    """Create a title widget in a mural."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        payload = {
            "text": text,
            "x": x,
            "y": y,
            "width": 400,
            "height": 60
        }

        response = requests.post(
            f"{MURAL_BASE_URL}/murals/{mural_id}/widgets/title",
            headers=get_mural_headers(),
            json=payload
        )

        result = handle_mural_response(response, "create_title")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to create title: {str(e)}",
            "data_source": "Mural API Failed",
            "fallback": {
                "id": "demo-title-123",
                "text": text,
                "data_source": "Demo Data - API Error"
            }
        })

@tool("get_mural_widgets", args_schema=None)
def get_mural_widgets(mural_id: str) -> str:
    """Get all widgets (content) in a mural."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        response = requests.get(
            f"{MURAL_BASE_URL}/murals/{mural_id}/widgets",
            headers=get_mural_headers()
        )

        result = handle_mural_response(response, "get_mural_widgets")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to get mural widgets: {str(e)}",
            "data_source": "Mural API Failed"
        })

# USER & COLLABORATION TOOLS

@tool("get_mural_users", args_schema=None)
def get_mural_users(mural_id: str) -> str:
    """Get all users who have access to a mural."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        response = requests.get(
            f"{MURAL_BASE_URL}/murals/{mural_id}/users",
            headers=get_mural_headers()
        )

        result = handle_mural_response(response, "get_mural_users")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to get mural users: {str(e)}",
            "data_source": "Mural API Failed"
        })

@tool("invite_users_to_mural", args_schema=InviteUsersInput)
def invite_users_to_mural(mural_id: str, emails: List[str], role: str = "member") -> str:
    """Invite users to collaborate on a mural."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        payload = {
            "emails": emails,
            "role": role
        }

        response = requests.post(
            f"{MURAL_BASE_URL}/murals/{mural_id}/users/invite",
            headers=get_mural_headers(),
            json=payload
        )

        result = handle_mural_response(response, "invite_users_to_mural")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to invite users: {str(e)}",
            "data_source": "Mural API Failed",
            "fallback": {
                "invited_emails": emails,
                "status": "pending",
                "data_source": "Demo Data - API Error"
            }
        })

@tool("get_workspaces", args_schema=None)
def get_workspaces() -> str:
    """Get all available workspaces for the authenticated user."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        response = requests.get(
            f"{MURAL_BASE_URL}/workspaces",
            headers=get_mural_headers()
        )

        result = handle_mural_response(response, "get_workspaces")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to get workspaces: {str(e)}",
            "data_source": "Mural API Failed"
        })

@tool("search_templates", args_schema=None)
def search_templates(query: str = "") -> str:
    """Search for mural templates in the default workspace."""
    try:
        if not MURAL_ACCESS_TOKEN:
            return json.dumps({
                "error": True,
                "message": "Mural API token not configured.",
                "data_source": "Configuration Error"
            })

        # Use default workspace for templates
        workspace_id = MURAL_DEFAULT_WORKSPACE_ID
        if not workspace_id:
            return json.dumps({
                "error": True,
                "message": "No default workspace configured for template search.",
                "data_source": "Configuration Error"
            })

        response = requests.get(
            f"{MURAL_BASE_URL}/workspaces/{workspace_id}/templates",
            headers=get_mural_headers()
        )

        result = handle_mural_response(response, "search_templates")
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to search templates: {str(e)}",
            "data_source": "Mural API Failed",
            "fallback": {
                "templates": [
                    {
                        "id": "demo-template-1",
                        "title": "Retrospective Template",
                        "description": "Standard sprint retrospective template"
                    }
                ],
                "data_source": "Demo Data - API Error"
            }
        })

# Utility function to get all Mural tools
def get_mural_tools():
    """Return all Mural API tools for agent integration."""
    return [
        # Mural Management
        create_mural,
        create_mural_from_template_url,
        get_mural_details,
        search_murals,
        get_workspace_murals,
        
        # Content Creation
        create_sticky_note,
        create_textbox,
        create_title,
        get_mural_widgets,
        
        # User & Collaboration
        get_mural_users,
        invite_users_to_mural,
        get_workspaces,
        search_templates
    ]
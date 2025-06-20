"""
Notion API integration for direct tool access without MCP.
"""

from .tools import (
    create_notion_page,
    get_notion_page,
    update_notion_page,
    get_notion_tools
)

__all__ = [
    "create_notion_page",
    "get_notion_page",
    "update_notion_page", 
    "get_notion_tools"
]
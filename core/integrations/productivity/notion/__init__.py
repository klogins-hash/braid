"""
Notion Direct API Integration for Braid

Provides direct access to Notion API for documentation, 
note-taking, and knowledge management.
"""

from .tools import (
    create_notion_page,
    get_notion_page,
    update_notion_page
)

__all__ = [
    'create_notion_page',
    'get_notion_page',
    'update_notion_page'
]

__version__ = "1.0.0"
__author__ = "Braid"
__description__ = "Direct Notion API integration for documentation"
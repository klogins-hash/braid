"""
Model Context Protocol (MCP) integration for Braid agents.

This module provides discovery, integration, and management of MCP servers
that extend agent capabilities beyond core tools.
"""

from .discovery import MCPDiscovery
from .integration import MCPIntegrator
from .registry import MCPRegistry

__all__ = ['MCPDiscovery', 'MCPIntegrator', 'MCPRegistry']
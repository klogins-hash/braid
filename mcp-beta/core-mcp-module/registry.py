"""
MCP Registry for loading and querying available MCP servers.
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class MCPRegistry:
    """Registry for managing and querying available MCP servers."""
    
    def __init__(self, registry_path: Optional[str] = None):
        """Initialize the MCP registry.
        
        Args:
            registry_path: Path to registry.json file. If None, uses default location.
        """
        if registry_path is None:
            # Default to registry.json in the mcp directory
            braid_root = Path(__file__).parent.parent.parent
            registry_path = braid_root / "mcp" / "registry.json"
        
        self.registry_path = Path(registry_path)
        self.registry_data = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load the MCP registry from file."""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"MCP registry not found at {self.registry_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in MCP registry: {e}")
    
    def get_all_mcps(self) -> Dict[str, Dict[str, Any]]:
        """Get all available MCP servers."""
        return self.registry_data.get("mcp_servers", {})
    
    def get_mcp_by_id(self, mcp_id: str) -> Optional[Dict[str, Any]]:
        """Get MCP server by ID."""
        return self.registry_data.get("mcp_servers", {}).get(mcp_id)
    
    def get_mcps_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get all MCP servers in a specific category."""
        all_mcps = self.get_all_mcps()
        return {
            mcp_id: mcp_data 
            for mcp_id, mcp_data in all_mcps.items()
            if mcp_data.get("category") == category
        }
    
    def search_mcps(self, query: str) -> List[Dict[str, Any]]:
        """Search MCP servers by keywords, use cases, or capabilities.
        
        Args:
            query: Search terms (space-separated)
            
        Returns:
            List of matching MCP servers with relevance scores
        """
        query_terms = [term.lower().strip() for term in query.split()]
        if not query_terms:
            return []
        
        results = []
        all_mcps = self.get_all_mcps()
        
        for mcp_id, mcp_data in all_mcps.items():
            score = self._calculate_relevance_score(mcp_data, query_terms)
            if score > 0:
                result = {
                    "mcp_id": mcp_id,
                    "mcp_data": mcp_data,
                    "relevance_score": score
                }
                results.append(result)
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results
    
    def _calculate_relevance_score(self, mcp_data: Dict[str, Any], query_terms: List[str]) -> float:
        """Calculate relevance score for an MCP against query terms."""
        score = 0.0
        
        # Search fields with different weights
        search_fields = [
            (mcp_data.get("name", ""), 3.0),
            (mcp_data.get("description", ""), 2.0),
            (" ".join(mcp_data.get("keywords", [])), 2.5),
            (" ".join(mcp_data.get("use_cases", [])), 2.0),
            (" ".join(mcp_data.get("capabilities", [])), 1.5),
        ]
        
        for field_text, weight in search_fields:
            field_text_lower = field_text.lower()
            for term in query_terms:
                if term in field_text_lower:
                    # Boost score for exact matches
                    if term == field_text_lower:
                        score += weight * 2
                    # Word boundary matches
                    elif f" {term} " in f" {field_text_lower} ":
                        score += weight * 1.5
                    # Partial matches
                    else:
                        score += weight
        
        return score
    
    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all available categories."""
        return self.registry_data.get("categories", {})
    
    def suggest_mcps_for_task(self, task_description: str) -> List[Dict[str, Any]]:
        """Suggest relevant MCPs for a given task description.
        
        Args:
            task_description: Description of what the user wants to accomplish
            
        Returns:
            List of suggested MCPs with relevance scores
        """
        # Extract key terms from task description
        task_lower = task_description.lower()
        
        # Look for specific service mentions
        service_keywords = {
            "notion": ["notion", "workspace", "wiki", "knowledge base"],
            "airtable": ["airtable", "database", "spreadsheet"],
            "slack": ["slack", "message", "team chat"],
            "github": ["github", "git", "repository", "code"],
            "stripe": ["stripe", "payment", "billing"],
        }
        
        direct_matches = []
        for mcp_id, keywords in service_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                mcp_data = self.get_mcp_by_id(mcp_id)
                if mcp_data:
                    direct_matches.append({
                        "mcp_id": mcp_id,
                        "mcp_data": mcp_data,
                        "relevance_score": 5.0,  # High score for direct matches
                        "match_type": "direct_service"
                    })
        
        if direct_matches:
            return direct_matches
        
        # Fallback to general search
        search_results = self.search_mcps(task_description)
        
        # Add match type for general searches
        for result in search_results:
            result["match_type"] = "keyword_match"
        
        return search_results[:5]  # Return top 5 suggestions
    
    def validate_mcp_metadata(self, mcp_id: str) -> List[str]:
        """Validate MCP metadata for completeness and correctness.
        
        Returns:
            List of validation issues (empty if valid)
        """
        mcp_data = self.get_mcp_by_id(mcp_id)
        if not mcp_data:
            return [f"MCP '{mcp_id}' not found in registry"]
        
        issues = []
        required_fields = ["name", "category", "description", "capabilities", "authentication"]
        
        for field in required_fields:
            if field not in mcp_data:
                issues.append(f"Missing required field: {field}")
        
        # Validate authentication
        auth = mcp_data.get("authentication", {})
        if auth.get("type") == "api_key" and not auth.get("required_env_vars"):
            issues.append("API key authentication requires 'required_env_vars'")
        
        # Check if metadata file exists
        braid_root = Path(__file__).parent.parent.parent
        category = mcp_data.get("category", "")
        metadata_path = braid_root / "mcp" / category / mcp_id / "metadata.json"
        
        if not metadata_path.exists():
            issues.append(f"Metadata file not found: {metadata_path}")
        
        return issues
"""
MCP Discovery system for intelligent MCP recommendation and user interaction.
"""

import re
from typing import Dict, List, Optional, Any
from .registry import MCPRegistry


class MCPDiscovery:
    """Intelligent MCP discovery and recommendation system."""
    
    def __init__(self, registry: Optional[MCPRegistry] = None):
        """Initialize MCP discovery system.
        
        Args:
            registry: MCPRegistry instance. If None, creates default registry.
        """
        self.registry = registry or MCPRegistry()
        
        # Task patterns for automatic MCP detection
        self.task_patterns = {
            "notion": [
                r"notion\s+(workspace|page|database)",
                r"(knowledge\s+base|wiki)\s+(search|update|create)",
                r"(meeting\s+notes|documentation)\s+in\s+notion",
                r"notion\s+(integration|api|sync)"
            ],
            "github": [
                r"github\s+(repository|repo|issues|pr)",
                r"(git|version\s+control)\s+(operations|management)",
                r"(code\s+review|pull\s+request)\s+automation"
            ],
            "slack": [
                r"slack\s+(message|notification|channel)",
                r"(team\s+communication|chat)\s+integration",
                r"slack\s+(bot|automation)"
            ],
            "agentql": [
                r"web\s+(scraping|automation|data\s+extraction)",
                r"(competitive\s+intelligence|market\s+research)",
                r"(website\s+analysis|scraping)",
                r"(data\s+extraction|web\s+automation)"
            ],
            "alphavantage": [
                r"(stock|financial|market)\s+(data|analysis|price)",
                r"(portfolio|investment)\s+(tracking|management|analysis)",
                r"(trading|forex|cryptocurrency)\s+(data|bot|analysis)",
                r"(technical\s+analysis|financial\s+dashboard)",
                r"(real.time|historical)\s+(stock|financial|market)",
                r"(market\s+research|stock\s+screening)"
            ],
            "perplexity": [
                r"(real.time|live)\s+(search|research|information)",
                r"(current|latest|breaking)\s+(news|events|developments)",
                r"(fact.checking|verify|validation)",
                r"(web\s+research|information\s+retrieval)",
                r"(research\s+assistant|current\s+data)",
                r"(trending|recent)\s+(topics|news|information)"
            ],
            "mongodb": [
                r"mongodb\s+(database|operations|atlas)",
                r"(nosql|document)\s+(database|storage)",
                r"(crud|database)\s+(operations|queries)",
                r"(data\s+storage|database\s+management)",
                r"(aggregation|collection)\s+(queries|operations)",
                r"(atlas|cluster)\s+(management|administration)"
            ],
            "twilio": [
                r"(sms|text)\s+(message|messaging|notification)",
                r"(voice|phone)\s+(call|calling|dialing)",
                r"whatsapp\s+(message|messaging|business)",
                r"(email|sendgrid)\s+(sending|notification)",
                r"(phone|number)\s+(verification|2fa|authenticate)",
                r"(communication|messaging)\s+(platform|api|service)",
                r"(twilio|telephony)\s+(integration|api|service)",
                r"(customer\s+support|contact\s+center)\s+(automation|system)",
                r"(notification|alert)\s+(system|service|automation)"
            ]
        }
    
    def analyze_task_description(self, task_description: str) -> Dict[str, Any]:
        """Analyze a task description to identify potential MCP needs.
        
        Args:
            task_description: User's description of what they want to accomplish
            
        Returns:
            Analysis result with suggested MCPs and confidence scores
        """
        task_lower = task_description.lower()
        
        # Check for direct service mentions
        direct_matches = self._find_direct_service_matches(task_lower)
        
        # Check for pattern matches
        pattern_matches = self._find_pattern_matches(task_lower)
        
        # Get general keyword suggestions
        keyword_suggestions = self.registry.suggest_mcps_for_task(task_description)
        
        # Combine and rank all suggestions
        all_suggestions = self._combine_suggestions(
            direct_matches, pattern_matches, keyword_suggestions
        )
        
        return {
            "task": task_description,
            "suggested_mcps": all_suggestions[:3],  # Top 3 suggestions
            "requires_mcp": len(all_suggestions) > 0,
            "confidence": self._calculate_overall_confidence(all_suggestions),
            "analysis": {
                "direct_matches": len(direct_matches),
                "pattern_matches": len(pattern_matches),
                "keyword_matches": len(keyword_suggestions)
            }
        }
    
    def _find_direct_service_matches(self, task_lower: str) -> List[Dict[str, Any]]:
        """Find direct mentions of services that have MCPs."""
        matches = []
        
        # Get all available MCPs
        all_mcps = self.registry.get_all_mcps()
        
        for mcp_id, mcp_data in all_mcps.items():
            # Check if service name is mentioned directly
            service_name = mcp_id.lower()
            keywords = [kw.lower() for kw in mcp_data.get("keywords", [])]
            
            # Direct service name match
            if service_name in task_lower:
                matches.append({
                    "mcp_id": mcp_id,
                    "mcp_data": mcp_data,
                    "relevance_score": 5.0,
                    "match_type": "direct_service",
                    "confidence": 0.95
                })
            # Keyword matches
            elif any(keyword in task_lower for keyword in keywords):
                matches.append({
                    "mcp_id": mcp_id,
                    "mcp_data": mcp_data,
                    "relevance_score": 3.0,
                    "match_type": "keyword",
                    "confidence": 0.75
                })
        
        return matches
    
    def _find_pattern_matches(self, task_lower: str) -> List[Dict[str, Any]]:
        """Find pattern-based matches using regex patterns."""
        matches = []
        
        for mcp_id, patterns in self.task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, task_lower):
                    mcp_data = self.registry.get_mcp_by_id(mcp_id)
                    if mcp_data:
                        matches.append({
                            "mcp_id": mcp_id,
                            "mcp_data": mcp_data,
                            "relevance_score": 4.0,
                            "match_type": "pattern",
                            "confidence": 0.80,
                            "matched_pattern": pattern
                        })
                        break  # Only one match per MCP
        
        return matches
    
    def _combine_suggestions(self, *suggestion_lists) -> List[Dict[str, Any]]:
        """Combine and deduplicate suggestions from multiple sources."""
        combined = {}
        
        for suggestions in suggestion_lists:
            for suggestion in suggestions:
                mcp_id = suggestion["mcp_id"]
                if mcp_id not in combined:
                    combined[mcp_id] = suggestion
                else:
                    # Keep the suggestion with higher relevance score
                    if suggestion["relevance_score"] > combined[mcp_id]["relevance_score"]:
                        combined[mcp_id] = suggestion
        
        # Sort by relevance score
        sorted_suggestions = sorted(
            combined.values(),
            key=lambda x: x["relevance_score"],
            reverse=True
        )
        
        return sorted_suggestions
    
    def _calculate_overall_confidence(self, suggestions: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in MCP recommendations."""
        if not suggestions:
            return 0.0
        
        # Weight by relevance scores
        total_weighted_confidence = sum(
            s["relevance_score"] * s.get("confidence", 0.5)
            for s in suggestions
        )
        total_weight = sum(s["relevance_score"] for s in suggestions)
        
        if total_weight == 0:
            return 0.0
        
        return min(total_weighted_confidence / total_weight, 1.0)
    
    def should_suggest_mcp(self, task_description: str, threshold: float = 0.4) -> bool:
        """Determine if an MCP should be suggested for the given task.
        
        Args:
            task_description: User's task description
            threshold: Confidence threshold for suggestions (0.0-1.0)
            
        Returns:
            True if MCP should be suggested
        """
        analysis = self.analyze_task_description(task_description)
        return analysis["confidence"] >= threshold and analysis["requires_mcp"]
    
    def format_mcp_suggestion(self, mcp_suggestion: Dict[str, Any]) -> str:
        """Format an MCP suggestion for user display.
        
        Args:
            mcp_suggestion: MCP suggestion from analyze_task_description
            
        Returns:
            Formatted string for user display
        """
        mcp_data = mcp_suggestion["mcp_data"]
        mcp_id = mcp_suggestion["mcp_id"]
        
        name = mcp_data.get("name", mcp_id)
        description = mcp_data.get("description", "No description available")
        category = mcp_data.get("category", "unknown")
        
        # Get key capabilities
        capabilities = mcp_data.get("capabilities", [])
        key_caps = capabilities[:3] if len(capabilities) > 3 else capabilities
        caps_text = ", ".join(key_caps) if key_caps else "Various capabilities"
        
        return f"""
**{name}** ({category})
{description}

Key capabilities: {caps_text}
Match confidence: {mcp_suggestion.get('confidence', 0.5):.0%}
        """.strip()
    
    def get_setup_requirements(self, mcp_id: str) -> Dict[str, Any]:
        """Get setup requirements for a specific MCP.
        
        Args:
            mcp_id: MCP identifier
            
        Returns:
            Setup requirements and instructions
        """
        mcp_data = self.registry.get_mcp_by_id(mcp_id)
        if not mcp_data:
            return {"error": f"MCP '{mcp_id}' not found"}
        
        auth = mcp_data.get("authentication", {})
        
        return {
            "mcp_id": mcp_id,
            "name": mcp_data.get("name", mcp_id),
            "authentication": {
                "type": auth.get("type", "unknown"),
                "required_env_vars": auth.get("required_env_vars", []),
                "setup_instructions": auth.get("setup_instructions", [])
            },
            "docker_required": mcp_data.get("docker_required", False),
            "complexity": mcp_data.get("installation_complexity", "unknown"),
            "documentation": mcp_data.get("repository", "")
        }
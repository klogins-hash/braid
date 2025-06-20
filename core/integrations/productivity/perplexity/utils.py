"""
Utility functions for Perplexity AI integration.

These are non-tool helper functions for direct Python use.
"""
import os
import json
from typing import Dict, Any, Optional, List
import requests


def get_perplexity_client_info() -> Dict[str, Any]:
    """
    Get information about the Perplexity API client configuration.
    
    Returns:
        Dict containing client configuration info
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    
    return {
        "api_key_configured": bool(api_key),
        "api_base_url": "https://api.perplexity.ai/chat/completions",
        "available_models": [
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online", 
            "llama-3.1-sonar-huge-128k-online",
            "sonar-pro",
            "sonar-deep-research",
            "sonar-reasoning-pro"
        ],
        "default_model": "llama-3.1-sonar-large-128k-online"
    }


def validate_perplexity_config() -> tuple[bool, str]:
    """
    Validate that Perplexity is properly configured.
    
    Returns:
        Tuple of (is_valid, message)
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    
    if not api_key:
        return False, "PERPLEXITY_API_KEY environment variable not set"
    
    if not api_key.startswith("pplx-"):
        return False, "PERPLEXITY_API_KEY appears to be invalid (should start with 'pplx-')"
    
    return True, "Perplexity configuration is valid"


def test_perplexity_connection() -> tuple[bool, str]:
    """
    Test the connection to Perplexity API.
    
    Returns:
        Tuple of (is_connected, message)
    """
    try:
        is_valid, config_message = validate_perplexity_config()
        if not is_valid:
            return False, config_message
        
        # Simple test query
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-sonar-small-128k-online",  # Use smallest model for test
            "messages": [{"role": "user", "content": "Hello, can you respond with just 'OK'?"}],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return True, "Perplexity API connection successful"
        else:
            return False, f"API connection failed: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def format_research_results(raw_response: str, include_metadata: bool = False) -> Dict[str, Any]:
    """
    Format raw Perplexity research results into structured data.
    
    Args:
        raw_response: Raw response text from Perplexity
        include_metadata: Whether to include additional metadata
        
    Returns:
        Formatted research results
    """
    # Basic formatting - extract key sections if present
    formatted = {
        "content": raw_response,
        "word_count": len(raw_response.split()),
        "character_count": len(raw_response)
    }
    
    if include_metadata:
        formatted.update({
            "sections": _extract_sections(raw_response),
            "key_points": _extract_key_points(raw_response),
            "has_statistics": _contains_statistics(raw_response)
        })
    
    return formatted


def _extract_sections(text: str) -> List[str]:
    """Extract section headers from text."""
    import re
    # Look for numbered lists or headers
    sections = re.findall(r'^\d+\.\s*([^\n]+)', text, re.MULTILINE)
    return sections


def _extract_key_points(text: str) -> List[str]:
    """Extract key bullet points from text."""
    import re
    # Look for bullet points or dashes
    points = re.findall(r'^[\-•*]\s*([^\n]+)', text, re.MULTILINE)
    return points[:5]  # Return first 5 key points


def _contains_statistics(text: str) -> bool:
    """Check if text contains statistical information."""
    import re
    # Look for percentages, numbers with units, growth indicators
    stats_patterns = [
        r'\d+%',  # Percentages
        r'\$\d+',  # Dollar amounts
        r'\d+\s*(billion|million|thousand)',  # Large numbers
        r'grew?\s+by\s+\d+',  # Growth indicators
        r'increased?\s+\d+',  # Increase indicators
    ]
    
    for pattern in stats_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def create_market_research_prompt(
    industry: str,
    location: Optional[str] = None,
    focus_areas: Optional[List[str]] = None,
    timeframe: str = "5 years"
) -> str:
    """
    Create a structured market research prompt.
    
    Args:
        industry: Industry to research
        location: Geographic focus
        focus_areas: Specific areas to focus on
        timeframe: Research timeframe
        
    Returns:
        Formatted research prompt
    """
    location_clause = f" in {location}" if location else ""
    focus_clause = ""
    
    if focus_areas:
        focus_clause = f"\n\nPay special attention to: {', '.join(focus_areas)}"
    
    prompt = f"""Conduct comprehensive market research for the {industry} industry{location_clause}.

Please provide analysis covering:

1. **Market Size & Growth**: Current market size and projected growth over {timeframe}
2. **Key Trends**: Major trends shaping the industry
3. **Competitive Landscape**: Leading companies and competitive dynamics  
4. **Revenue Drivers**: Primary sources of revenue and growth
5. **Challenges & Risks**: Key challenges and risk factors
6. **Future Outlook**: Opportunities and predictions for the next {timeframe}

Please include specific statistics, percentages, and data points where available.{focus_clause}"""

    return prompt
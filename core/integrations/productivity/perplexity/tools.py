"""
Public, LLM-callable tools for interacting with Perplexity AI.
"""
import os
import json
from typing import Optional, Dict, Any

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    import requests
except ImportError:
    raise ImportError(
        "Perplexity tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install "requests"'
    )

# --- Input Schemas ---

class PerplexitySearchInput(BaseModel):
    query: str = Field(description="The search query to send to Perplexity")
    model: Optional[str] = Field(
        default="llama-3.1-sonar-large-128k-online", 
        description="Perplexity model to use (default: llama-3.1-sonar-large-128k-online)"
    )
    temperature: Optional[float] = Field(
        default=0.1, 
        description="Temperature for response generation (0.0-1.0, default: 0.1)"
    )

class PerplexityResearchInput(BaseModel):
    topic: str = Field(description="The research topic or question")
    focus_areas: Optional[str] = Field(
        default=None, 
        description="Specific areas to focus the research on (comma-separated)"
    )
    depth: Optional[str] = Field(
        default="comprehensive", 
        description="Research depth: 'quick', 'standard', or 'comprehensive'"
    )

class PerplexityMarketResearchInput(BaseModel):
    industry: str = Field(description="Industry to research")
    location: Optional[str] = Field(
        default=None, 
        description="Geographic location for market analysis"
    )
    timeframe: Optional[str] = Field(
        default="5 years", 
        description="Forecast timeframe for analysis"
    )

class PerplexityNewsSearchInput(BaseModel):
    topic: str = Field(description="News topic to search for")
    days_back: Optional[int] = Field(
        default=7, 
        description="Number of days back to search (default: 7)"
    )
    sources: Optional[str] = Field(
        default=None, 
        description="Preferred news sources (comma-separated)"
    )

# --- Helper Functions ---

def _make_perplexity_request(
    prompt: str, 
    model: str = "llama-3.1-sonar-large-128k-online",
    temperature: float = 0.1
) -> Dict[str, Any]:
    """Internal helper to make requests to Perplexity API."""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set")
    
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")

# --- Perplexity Tools ---

@tool("perplexity_search", args_schema=PerplexitySearchInput)
def perplexity_search(
    query: str, 
    model: str = "llama-3.1-sonar-large-128k-online",
    temperature: float = 0.1
) -> str:
    """
    Perform a general web search using Perplexity AI.
    
    This tool provides real-time web search capabilities with AI-powered 
    summarization and analysis of results.
    """
    try:
        result = _make_perplexity_request(query, model, temperature)
        return result['choices'][0]['message']['content']
    except ValueError:
        return "Error: PERPLEXITY_API_KEY environment variable not set."
    except Exception as e:
        return f"Perplexity search failed: {str(e)}"

@tool("perplexity_research", args_schema=PerplexityResearchInput)
def perplexity_research(
    topic: str,
    focus_areas: Optional[str] = None,
    depth: str = "comprehensive"
) -> str:
    """
    Conduct detailed research on a specific topic using Perplexity AI.
    
    This tool is optimized for in-depth research and analysis, providing
    comprehensive insights with citations and sources.
    """
    try:
        # Build research prompt based on depth and focus areas
        if depth == "quick":
            detail_instruction = "Provide a concise 2-3 sentence summary."
        elif depth == "standard":
            detail_instruction = "Provide a comprehensive 1-2 paragraph analysis."
        else:  # comprehensive
            detail_instruction = "Provide a detailed analysis with key insights, trends, and supporting data."
        
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f" Focus specifically on: {focus_areas}."
        
        prompt = f"""Research the topic: {topic}
        
{detail_instruction}{focus_instruction}

Include relevant statistics, recent developments, and credible sources where available."""
        
        result = _make_perplexity_request(prompt, "sonar-pro", 0.1)
        return result['choices'][0]['message']['content']
    except ValueError:
        return "Error: PERPLEXITY_API_KEY environment variable not set."
    except Exception as e:
        return f"Perplexity research failed: {str(e)}"

@tool("perplexity_market_research", args_schema=PerplexityMarketResearchInput)
def perplexity_market_research(
    industry: str,
    location: Optional[str] = None,
    timeframe: str = "5 years"
) -> str:
    """
    Conduct market research and analysis for a specific industry using Perplexity AI.
    
    This tool provides market insights, growth projections, trends, and
    competitive analysis for business planning and forecasting.
    """
    try:
        location_clause = f" in {location}" if location else ""
        
        prompt = f"""Provide market analysis for the {industry} industry{location_clause}. Include:

1. Industry growth outlook for the next {timeframe}
2. Key market trends and drivers
3. Revenue growth expectations and projections
4. Major competitive dynamics
5. Risk factors and challenges
6. Opportunities for growth

Focus on actionable insights with supporting data and statistics where available. Keep the analysis comprehensive but well-structured."""

        result = _make_perplexity_request(prompt, "llama-3.1-sonar-large-128k-online", 0.1)
        return result['choices'][0]['message']['content']
    except ValueError:
        return "Error: PERPLEXITY_API_KEY environment variable not set."
    except Exception as e:
        return f"Market research failed: {str(e)}"

@tool("perplexity_news_search", args_schema=PerplexityNewsSearchInput)
def perplexity_news_search(
    topic: str,
    days_back: int = 7,
    sources: Optional[str] = None
) -> str:
    """
    Search for recent news and updates on a specific topic using Perplexity AI.
    
    This tool focuses on recent news, developments, and current events
    related to the specified topic.
    """
    try:
        time_constraint = f"from the last {days_back} days" if days_back > 0 else "recent"
        source_constraint = f" Focus on sources like: {sources}." if sources else ""
        
        prompt = f"""Find recent news and developments about {topic} {time_constraint}.

Provide:
1. Key recent developments and news
2. Important updates or changes
3. Relevant statistics or data points
4. Source citations where possible

{source_constraint}

Focus on the most significant and credible news items."""

        result = _make_perplexity_request(prompt, "llama-3.1-sonar-large-128k-online", 0.1)
        return result['choices'][0]['message']['content']
    except ValueError:
        return "Error: PERPLEXITY_API_KEY environment variable not set."
    except Exception as e:
        return f"News search failed: {str(e)}"

@tool("perplexity_ask", args_schema=PerplexitySearchInput)
def perplexity_ask(
    query: str,
    model: str = "llama-3.1-sonar-large-128k-online",
    temperature: float = 0.1
) -> str:
    """
    Ask a conversational question to Perplexity AI with real-time web knowledge.
    
    This tool is ideal for getting direct answers to questions that require
    current information and web-based knowledge.
    """
    try:
        result = _make_perplexity_request(query, model, temperature)
        return result['choices'][0]['message']['content']
    except ValueError:
        return "Error: PERPLEXITY_API_KEY environment variable not set."
    except Exception as e:
        return f"Perplexity query failed: {str(e)}"

# --- Tool Aggregator ---

def get_perplexity_tools():
    """Returns a list of all Perplexity tools in this module."""
    return [
        perplexity_search,
        perplexity_research, 
        perplexity_market_research,
        perplexity_news_search,
        perplexity_ask
    ]
"""
Web tools for HTTP requests, API integration, and web scraping.
"""
import json
import os
from typing import Dict, List, Optional, Any

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    raise ImportError(
        "Web tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install requests>=2.28.0'
    )

# --- Input Schemas ---

class HttpRequestInput(BaseModel):
    url: str = Field(description="The URL to make the request to")
    method: str = Field(default="GET", description="HTTP method: GET, POST, PUT, DELETE, PATCH")
    headers: Optional[Dict[str, str]] = Field(default=None, description="HTTP headers as key-value pairs")
    params: Optional[Dict[str, str]] = Field(default=None, description="Query parameters as key-value pairs")
    body: Optional[str] = Field(default=None, description="Request body content (for POST/PUT requests)")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    follow_redirects: bool = Field(default=True, description="Whether to follow redirects")

class WebScrapeInput(BaseModel):
    url: str = Field(description="The URL to scrape content from")
    css_selector: Optional[str] = Field(default=None, description="CSS selector to extract specific elements")
    extract_links: bool = Field(default=False, description="Whether to extract all links from the page")
    timeout: int = Field(default=30, description="Request timeout in seconds")

# --- Helper Functions ---

def _create_session_with_retries():
    """Create a requests session with retry strategy."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def _safe_json_parse(text: str) -> Any:
    """Safely parse JSON, return original text if parsing fails."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text

# --- Web Tools ---

@tool("http_request", args_schema=HttpRequestInput)
def http_request(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None,
                params: Optional[Dict[str, str]] = None, body: Optional[str] = None,
                timeout: int = 30, follow_redirects: bool = True) -> str:
    """
    Make HTTP requests to APIs and websites.
    
    Supports all standard HTTP methods (GET, POST, PUT, DELETE, PATCH) with:
    - Custom headers and query parameters
    - Request body for POST/PUT operations
    - Automatic retries for failed requests
    - JSON response parsing
    - Error handling and detailed status reporting
    
    Returns a JSON string with response details including status, headers, and content.
    """
    try:
        session = _create_session_with_retries()
        
        # Set default headers
        request_headers = {
            'User-Agent': 'Braid-Agent/1.0',
            'Accept': 'application/json, text/plain, */*'
        }
        if headers:
            request_headers.update(headers)
        
        # Make the request
        response = session.request(
            method=method.upper(),
            url=url,
            headers=request_headers,
            params=params or {},
            data=body,
            timeout=timeout,
            allow_redirects=follow_redirects
        )
        
        # Parse response content
        content = response.text
        content_type = response.headers.get('content-type', '').lower()
        
        # Try to parse JSON responses
        parsed_content = content
        if 'application/json' in content_type:
            parsed_content = _safe_json_parse(content)
        
        # Build result
        result = {
            "success": True,
            "status_code": response.status_code,
            "status_text": response.reason,
            "url": response.url,
            "method": method.upper(),
            "headers": dict(response.headers),
            "content": parsed_content,
            "content_length": len(content),
            "encoding": response.encoding,
            "elapsed_seconds": response.elapsed.total_seconds()
        }
        
        # Add error info for non-2xx status codes
        if not response.ok:
            result["error"] = f"HTTP {response.status_code}: {response.reason}"
        
        return json.dumps(result, indent=2, default=str)
        
    except requests.exceptions.Timeout:
        return json.dumps({
            "success": False,
            "error": f"Request timed out after {timeout} seconds",
            "url": url,
            "method": method.upper()
        }, indent=2)
    
    except requests.exceptions.ConnectionError as e:
        return json.dumps({
            "success": False,
            "error": f"Connection error: {str(e)}",
            "url": url,
            "method": method.upper()
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "url": url,
            "method": method.upper()
        }, indent=2)

@tool("web_scrape", args_schema=WebScrapeInput)
def web_scrape(url: str, css_selector: Optional[str] = None, 
               extract_links: bool = False, timeout: int = 30) -> str:
    """
    Scrape content from web pages with optional CSS selector filtering.
    
    Can extract:
    - Full page text content
    - Specific elements using CSS selectors
    - All links from the page
    - Page metadata (title, description)
    
    Returns extracted content as JSON with metadata.
    """
    try:
        # Import BeautifulSoup here to make it optional
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return json.dumps({
                "success": False,
                "error": "BeautifulSoup not available. Install with: pip install beautifulsoup4"
            })
        
        session = _create_session_with_retries()
        
        # Get the page
        response = session.get(url, timeout=timeout, headers={
            'User-Agent': 'Braid-Agent/1.0 (Web Scraper)'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic page info
        result = {
            "success": True,
            "url": response.url,
            "title": soup.title.string.strip() if soup.title else None,
            "status_code": response.status_code
        }
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            result["description"] = meta_desc.get('content', '').strip()
        
        # Extract specific content based on selector
        if css_selector:
            elements = soup.select(css_selector)
            result["selected_content"] = [elem.get_text().strip() for elem in elements]
            result["selected_count"] = len(elements)
        else:
            # Extract main text content (remove script and style elements)
            for script in soup(["script", "style"]):
                script.decompose()
            result["text_content"] = soup.get_text()
        
        # Extract links if requested
        if extract_links:
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().strip()
                if href and text:
                    links.append({
                        "url": href,
                        "text": text
                    })
            result["links"] = links
            result["link_count"] = len(links)
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Scraping failed: {str(e)}",
            "url": url
        }, indent=2)

# --- Tool Aggregator ---

def get_web_tools():
    """Returns a list of all web tools."""
    return [http_request, web_scrape]
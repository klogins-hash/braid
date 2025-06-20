"""
AgentQL Direct API Integration Tools

Provides direct access to AgentQL web extraction capabilities
without MCP server dependencies.
"""

import os
import json
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        "AgentQL tools require additional dependencies. "
        "Install with: pip install requests python-dotenv"
    )

# Load environment variables
load_dotenv(override=True)

# --- Input Schemas ---

class WebExtractionInput(BaseModel):
    url: str = Field(description="URL to extract data from")
    data_schema: Dict[str, Any] = Field(description="JSON schema defining the data structure to extract")
    prompt: str = Field(description="Natural language description of what data to extract")
    timeout: Optional[int] = Field(default=30, description="Request timeout in seconds")

class ProductExtractionInput(BaseModel):
    url: str = Field(description="Product page URL")
    extract_reviews: bool = Field(default=True, description="Whether to extract review information")
    extract_images: bool = Field(default=False, description="Whether to extract image URLs")

class ContactExtractionInput(BaseModel):
    url: str = Field(description="Website URL to extract contact information from")
    include_social: bool = Field(default=True, description="Whether to include social media links")

class PricingExtractionInput(BaseModel):
    url: str = Field(description="Pricing page URL")
    include_features: bool = Field(default=True, description="Whether to extract feature lists")

class NewsExtractionInput(BaseModel):
    url: str = Field(description="News article or blog post URL")
    include_metadata: bool = Field(default=True, description="Whether to extract publication metadata")

# --- Helper Functions ---

def _get_agentql_auth() -> str:
    """Get AgentQL API key."""
    load_dotenv(override=True)
    
    api_key = os.getenv("AGENTQL_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "AGENTQL_API_KEY environment variable not set. "
            "Get your API key from https://dev.agentql.com"
        )
    
    return api_key

def _make_agentql_request(
    url: str,
    data_schema: Dict[str, Any],
    prompt: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """Make request to AgentQL API for web data extraction."""
    
    try:
        api_key = _get_agentql_auth()
        
        # AgentQL API endpoint
        api_url = "https://api.agentql.com/v1/extract"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "schema": data_schema,
            "prompt": prompt,
            "timeout": timeout
        }
        
        print(f"🔄 Making AgentQL extraction request for: {url}")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=timeout + 10  # Add buffer for API processing
        )
        
        print(f"📊 AgentQL API Response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! AgentQL data extraction completed")
            result = response.json()
            
            return {
                "success": True,
                "url": url,
                "extracted_data": result.get("data", {}),
                "extraction_time": result.get("extraction_time"),
                "page_title": result.get("page_title"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            error_data = response.json() if response.content else {}
            return {
                "error": True,
                "status_code": response.status_code,
                "message": error_data.get("error", f"AgentQL API error: {response.status_code}"),
                "details": error_data.get("details")
            }
            
    except Exception as e:
        print(f"❌ AgentQL API Error: {e}")
        return {
            "error": True,
            "message": f"Request failed: {str(e)}"
        }

# --- Core Extraction Tools ---

@tool("extract_web_data", args_schema=WebExtractionInput)
def extract_web_data(
    url: str,
    data_schema: Dict[str, Any],
    prompt: str,
    timeout: int = 30
) -> str:
    """
    Extract structured data from any URL using natural language descriptions.
    
    Args:
        url: URL to extract data from
        data_schema: JSON schema defining the data structure to extract
        prompt: Natural language description of what data to extract
        timeout: Request timeout in seconds
    
    Returns:
        JSON string with extracted structured data
    """
    
    result = _make_agentql_request(url, data_schema, prompt, timeout)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "url": url
        })
    
    return json.dumps(result, indent=2)

@tool("extract_product_info", args_schema=ProductExtractionInput)
def extract_product_info(
    url: str,
    extract_reviews: bool = True,
    extract_images: bool = False
) -> str:
    """
    Extract product information from e-commerce product pages.
    
    Args:
        url: Product page URL
        extract_reviews: Whether to extract review information
        extract_images: Whether to extract image URLs
    
    Returns:
        JSON string with product details
    """
    
    # Define comprehensive product schema
    schema = {
        "product_name": "string",
        "price": "number",
        "original_price": "number",
        "currency": "string",
        "availability": "string",
        "brand": "string",
        "description": "string",
        "key_features": ["string"],
        "specifications": {
            "category": "string",
            "model": "string",
            "dimensions": "string",
            "weight": "string"
        }
    }
    
    if extract_reviews:
        schema.update({
            "rating": "number",
            "review_count": "number",
            "top_reviews": [{"rating": "number", "text": "string", "author": "string"}]
        })
    
    if extract_images:
        schema.update({
            "main_image": "string",
            "additional_images": ["string"]
        })
    
    prompt = "Extract comprehensive product information including name, pricing, availability, brand, description, and key specifications"
    if extract_reviews:
        prompt += ". Also include customer ratings and review highlights"
    if extract_images:
        prompt += ". Include product image URLs"
    
    result = _make_agentql_request(url, schema, prompt)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "url": url
        })
    
    return json.dumps(result, indent=2)

@tool("extract_contact_info", args_schema=ContactExtractionInput)
def extract_contact_info(
    url: str,
    include_social: bool = True
) -> str:
    """
    Extract contact information from company websites.
    
    Args:
        url: Website URL to extract contact information from
        include_social: Whether to include social media links
    
    Returns:
        JSON string with contact details
    """
    
    schema = {
        "company_name": "string",
        "email": "string",
        "phone": "string",
        "address": {
            "street": "string",
            "city": "string",
            "state": "string",
            "zip_code": "string",
            "country": "string"
        },
        "business_hours": "string",
        "contact_form_url": "string"
    }
    
    if include_social:
        schema.update({
            "social_media": {
                "facebook": "string",
                "twitter": "string",
                "linkedin": "string",
                "instagram": "string"
            }
        })
    
    prompt = "Extract all contact information including company name, email, phone, physical address, and business hours"
    if include_social:
        prompt += ". Also find social media profiles and links"
    
    result = _make_agentql_request(url, schema, prompt)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "url": url
        })
    
    return json.dumps(result, indent=2)

@tool("extract_pricing_data", args_schema=PricingExtractionInput)
def extract_pricing_data(
    url: str,
    include_features: bool = True
) -> str:
    """
    Extract pricing information and plan details from pricing pages.
    
    Args:
        url: Pricing page URL
        include_features: Whether to extract feature lists for each plan
    
    Returns:
        JSON string with pricing plans and details
    """
    
    schema = {
        "company_name": "string",
        "pricing_model": "string",
        "currency": "string",
        "billing_cycles": ["string"],
        "plans": [
            {
                "name": "string",
                "price": "number",
                "billing_cycle": "string",
                "description": "string",
                "popular": "boolean",
                "cta_text": "string"
            }
        ]
    }
    
    if include_features:
        schema["plans"][0].update({
            "features": ["string"],
            "feature_limits": {
                "users": "string",
                "storage": "string",
                "api_calls": "string"
            }
        })
    
    prompt = "Extract all pricing plans with names, costs, billing cycles, and descriptions"
    if include_features:
        prompt += ". Include detailed feature lists and usage limits for each plan"
    
    result = _make_agentql_request(url, schema, prompt)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "url": url
        })
    
    return json.dumps(result, indent=2)

@tool("extract_news_articles", args_schema=NewsExtractionInput)
def extract_news_articles(
    url: str,
    include_metadata: bool = True
) -> str:
    """
    Extract news article content and metadata from news websites.
    
    Args:
        url: News article or blog post URL
        include_metadata: Whether to extract publication metadata
    
    Returns:
        JSON string with article content and metadata
    """
    
    schema = {
        "title": "string",
        "content": "string",
        "summary": "string",
        "main_image": "string",
        "category": "string",
        "tags": ["string"]
    }
    
    if include_metadata:
        schema.update({
            "author": "string",
            "publication_date": "string",
            "publisher": "string",
            "word_count": "number",
            "reading_time": "string",
            "related_articles": [
                {
                    "title": "string",
                    "url": "string"
                }
            ]
        })
    
    prompt = "Extract the full article content including title, main text, and summary"
    if include_metadata:
        prompt += ". Also extract author information, publication details, and related articles"
    
    result = _make_agentql_request(url, schema, prompt)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "url": url
        })
    
    return json.dumps(result, indent=2)

# --- Advanced Extraction Tools ---

@tool("extract_competitor_analysis")
def extract_competitor_analysis(competitor_urls: List[str]) -> str:
    """
    Extract and compare data from multiple competitor websites.
    
    Args:
        competitor_urls: List of competitor website URLs
    
    Returns:
        JSON string with comparative analysis
    """
    
    results = []
    
    schema = {
        "company_name": "string",
        "tagline": "string",
        "key_products": ["string"],
        "pricing_strategy": "string",
        "target_audience": "string",
        "unique_selling_points": ["string"]
    }
    
    prompt = "Extract company overview, main products/services, pricing approach, and key differentiators"
    
    for url in competitor_urls[:5]:  # Limit to 5 competitors
        result = _make_agentql_request(url, schema, prompt)
        if not result.get("error"):
            results.append({
                "url": url,
                "data": result.get("extracted_data", {})
            })
    
    return json.dumps({
        "competitor_count": len(results),
        "analysis_date": datetime.now().isoformat(),
        "competitors": results
    }, indent=2)

@tool("extract_job_listings")
def extract_job_listings(job_board_url: str, search_query: str = None) -> str:
    """
    Extract job listings from job board websites.
    
    Args:
        job_board_url: Job board or company careers page URL
        search_query: Optional search terms to focus extraction
    
    Returns:
        JSON string with job listings
    """
    
    schema = {
        "company_name": "string",
        "total_openings": "number",
        "job_listings": [
            {
                "title": "string",
                "department": "string",
                "location": "string",
                "employment_type": "string",
                "salary_range": "string",
                "posted_date": "string",
                "description": "string",
                "requirements": ["string"],
                "benefits": ["string"],
                "apply_url": "string"
            }
        ]
    }
    
    prompt = f"Extract all job listings with titles, locations, requirements, and application details"
    if search_query:
        prompt += f". Focus on positions related to: {search_query}"
    
    result = _make_agentql_request(job_board_url, schema, prompt)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message"),
            "url": job_board_url
        })
    
    return json.dumps(result, indent=2)

# --- Tool Collections ---

def get_agentql_tools():
    """Get all AgentQL tools."""
    return [
        extract_web_data,
        extract_product_info,
        extract_contact_info,
        extract_pricing_data,
        extract_news_articles,
        extract_competitor_analysis,
        extract_job_listings
    ]

def get_extraction_tools():
    """Get core extraction tools only."""
    return [
        extract_web_data,
        extract_product_info,
        extract_contact_info,
        extract_pricing_data,
        extract_news_articles
    ]
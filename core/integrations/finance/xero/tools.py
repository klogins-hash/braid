"""
Public, LLM-callable tools for interacting with Xero API directly.

Quick Setup:
1. Run: python -m core.integrations.xero.setup
2. Follow the OAuth2 flow in your browser
3. Credentials are automatically saved to .env file
4. Start using Xero tools in your agent!

Alternative setup:
from core.integrations.xero.setup import setup_xero_integration
setup_xero_integration()
"""
import os
import json
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    import requests
except ImportError:
    raise ImportError(
        "Xero tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install "requests"'
    )

# --- Input Schemas ---

class XeroReportInput(BaseModel):
    fromDate: Optional[str] = Field(
        default=None,
        description="Start date for report (YYYY-MM-DD format). Defaults to 1 year ago."
    )
    toDate: Optional[str] = Field(
        default=None,
        description="End date for report (YYYY-MM-DD format). Defaults to today."
    )
    periods: Optional[int] = Field(
        default=1,
        description="Number of periods to compare (1-12)"
    )
    timeframe: Optional[str] = Field(
        default="MONTH",
        description="Timeframe for comparison: MONTH, QUARTER, or YEAR"
    )

class XeroBalanceSheetInput(BaseModel):
    date: Optional[str] = Field(
        default=None,
        description="Date for balance sheet (YYYY-MM-DD format). Defaults to today."
    )
    periods: Optional[int] = Field(
        default=1,
        description="Number of periods to compare (1-12)"
    )
    timeframe: Optional[str] = Field(
        default="MONTH",
        description="Timeframe for comparison: MONTH, QUARTER, or YEAR"
    )

# --- Helper Functions ---

def _get_xero_headers(accept_xml: bool = False) -> Dict[str, str]:
    """Get Xero API headers with authentication."""
    # FORCE reload environment to get fresh tokens (critical for avoiding cache issues)
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    access_token = os.environ.get("XERO_ACCESS_TOKEN", "").strip()
    tenant_id = os.environ.get("XERO_TENANT_ID", "").strip()
    
    # Return headers even if credentials missing - let calling function handle fallback
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Xero-tenant-id": tenant_id
    }
    
    # Use XML for reports as it's more reliable
    if accept_xml:
        headers["Accept"] = "application/xml"
    else:
        headers["Accept"] = "application/json"
    
    return headers

def _make_xero_request(endpoint: str, params: Dict[str, Any] = None, use_xml: bool = False) -> Dict[str, Any]:
    """Internal helper to make requests to Xero API."""
    # FORCE reload environment variables to avoid caching issues
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Check credentials first
    access_token = os.environ.get("XERO_ACCESS_TOKEN", "").strip()
    tenant_id = os.environ.get("XERO_TENANT_ID", "").strip()
    
    # Debug output for troubleshooting
    print(f"🔍 Token check: {access_token[:50] if access_token else 'MISSING'}...")
    print(f"🔍 Tenant: {tenant_id}")
    
    if not access_token or not tenant_id:
        return {
            "error": True,
            "message": "Missing XERO_ACCESS_TOKEN or XERO_TENANT_ID",
            "data_source": "Mock Data - No Credentials"
        }
    
    base_url = "https://api.xero.com/api.xro/2.0"
    url = f"{base_url}/{endpoint}"
    
    headers = _get_xero_headers(accept_xml=use_xml)
    
    try:
        print(f"🔄 Making API call to Xero: {endpoint}")
        response = requests.get(url, headers=headers, params=params or {}, timeout=30)
        
        print(f"📊 API Response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Got real Xero data")
            if use_xml:
                return {"xml_content": response.text, "data_source": "REAL Xero API - Core Integration"}
            else:
                data = response.json()
                data["data_source"] = "REAL Xero API - Core Integration"
                return data
        else:
            print(f"❌ API Error: {response.text[:200]}")
            # Return error info instead of raising exception
            return {
                "error": True,
                "status_code": response.status_code,
                "message": f"Xero API error: {response.status_code}",
                "details": response.text[:200],
                "data_source": f"Mock Data - API Error {response.status_code}"
            }
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return {
            "error": True,
            "message": f"Connection error: {str(e)}",
            "data_source": "Mock Data - Request Failed"
        }

def _get_default_dates() -> tuple[str, str]:
    """Get default from/to dates (1 year period ending today)."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    return one_year_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

def _parse_xml_report(xml_content: str) -> Dict[str, Any]:
    """Parse Xero XML report response into structured data using proven working approach."""
    try:
        root = ET.fromstring(xml_content)
        
        financial_data = {
            "total_revenue": 0.0,
            "total_cogs": 0.0,
            "gross_profit": 0.0,
            "total_expenses": 0.0,
            "net_income": 0.0
        }
        
        rows_data = []
        
        # Parse XML rows using the proven working method
        for row in root.findall('.//Row'):
            cells = row.findall('.//Cell')
            
            if len(cells) >= 2:
                account_cell = cells[0].find('Value')
                value_cell = cells[1].find('Value')
                
                if account_cell is not None and value_cell is not None:
                    account_name = account_cell.text or ''
                    value_text = value_cell.text or ''
                    
                    # Store row
                    rows_data.append({
                        "account": account_name,
                        "value": value_text
                    })
                    
                    # Extract key metrics using the proven working logic
                    if value_text and value_text not in ['0', '0.00', '']:
                        try:
                            value_float = float(value_text)
                            account_lower = account_name.lower()
                            
                            if 'total revenue' in account_lower:
                                financial_data['total_revenue'] = value_float
                            elif 'total cost of sales' in account_lower:
                                financial_data['total_cogs'] = value_float
                            elif 'gross profit' in account_lower:
                                financial_data['gross_profit'] = value_float
                            elif 'total operating expenses' in account_lower:
                                financial_data['total_expenses'] = value_float
                            elif any(term in account_lower for term in ['net income', 'net profit', 'net loss']):
                                if 'before tax' not in account_lower:
                                    financial_data['net_income'] = value_float
                                    
                        except (ValueError, TypeError):
                            pass
        
        return {
            "reportName": "Profit and Loss",
            "reportDate": "Current Period",
            "financial_data": financial_data,
            "rows": rows_data,
            "data_source": "REAL Xero API - Core Integration"
        }
        
    except Exception as e:
        return {
            "data_source": "Mock Data - XML Parse Error", 
            "financial_data": {"total_revenue": 666666, "net_income": 666666},
            "error": f"XML parse failed: {e}"
        }

def _format_report_response(report_data: Dict[str, Any]) -> str:
    """Format Xero report response to match MCP server output format."""
    try:
        # Handle XML response
        if "xml_content" in report_data:
            parsed_data = _parse_xml_report(report_data["xml_content"])
            return json.dumps(parsed_data, indent=2)
        
        # Handle JSON response
        reports = report_data.get("Reports", [])
        if not reports:
            return json.dumps({"error": "No report data found"}, indent=2)
        
        report = reports[0]
        formatted_report = {
            "reportName": report.get("ReportName", ""),
            "reportDate": report.get("ReportDate", ""),
            "updatedDateUTC": report.get("UpdatedDateUTC", ""),
            "rows": []
        }
        
        # Process report rows
        for row in report.get("Rows", []):
            formatted_row = {
                "rowType": row.get("RowType", ""),
                "cells": []
            }
            
            for cell in row.get("Cells", []):
                formatted_cell = {
                    "value": cell.get("Value", "")
                }
                # Include attributes if they exist
                if "Attributes" in cell:
                    formatted_cell["attributes"] = cell["Attributes"]
                formatted_row["cells"].append(formatted_cell)
            
            formatted_report["rows"].append(formatted_row)
        
        return json.dumps(formatted_report, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to format report: {str(e)}"}, indent=2)

# --- Xero Tools ---

@tool("get_xero_profit_and_loss", args_schema=XeroReportInput)
def get_xero_profit_and_loss(
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    periods: int = 1,
    timeframe: str = "MONTH"
) -> str:
    """
    Retrieve Profit and Loss report from Xero.
    
    This tool fetches P&L data showing revenue, expenses, and net income
    for the specified period. Essential for financial forecasting.
    
    Returns structured data including:
    - reportName: Name of the report
    - reportDate: Date range covered
    - financial_data: Key metrics (total_revenue, gross_profit, net_income, etc.)
    - rows: Detailed line items
    """
    # Set default dates if not provided (YTD if not specified)
    if not fromDate or not toDate:
        current_year = datetime.now().year
        fromDate = f"{current_year}-01-01"
        toDate = datetime.now().strftime("%Y-%m-%d")
    
    # Reload environment and check credentials
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    access_token = os.environ.get("XERO_ACCESS_TOKEN", "").strip()
    tenant_id = os.environ.get("XERO_TENANT_ID", "").strip()
    
    if not access_token or not tenant_id:
        return json.dumps({
            "data_source": "Mock Data - Xero not configured",
            "reportName": "Profit and Loss",
            "reportDate": f"{fromDate} to {toDate}",
            "financial_data": {
                "total_revenue": 150000,
                "total_cogs": 60000,
                "gross_profit": 90000,
                "total_expenses": 45000,
                "net_income": 45000
            },
            "note": "Configure XERO_ACCESS_TOKEN and XERO_TENANT_ID for real data"
        }, indent=2)
    
    # Try to get real Xero data
    params = {
        "fromDate": fromDate,
        "toDate": toDate
    }
    
    result = _make_xero_request("Reports/ProfitAndLoss", params, use_xml=True)
    
    # Check if we got an error
    if result.get("error"):
        return json.dumps({
            "data_source": "Mock Data - Xero API Error",
            "reportName": "Profit and Loss", 
            "reportDate": f"{fromDate} to {toDate}",
            "financial_data": {
                "total_revenue": 175000,
                "total_cogs": 70000,
                "gross_profit": 105000,
                "total_expenses": 52000,
                "net_income": 53000
            },
            "error_details": result.get("message", "API connection failed"),
            "note": "Using mock data due to API issues. Check Xero authentication."
        }, indent=2)
    
    # Parse real Xero data
    return _format_report_response(result)

@tool("get_xero_balance_sheet", args_schema=XeroBalanceSheetInput)
def get_xero_balance_sheet(
    date: Optional[str] = None,
    periods: int = 1,
    timeframe: str = "MONTH"
) -> str:
    """
    Retrieve Balance Sheet report from Xero.
    
    This tool fetches balance sheet data showing assets, liabilities,
    and equity at a specific point in time.
    """
    # Set default date if not provided
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Reload environment and check credentials
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    access_token = os.environ.get("XERO_ACCESS_TOKEN", "").strip()
    tenant_id = os.environ.get("XERO_TENANT_ID", "").strip()
    
    if not access_token or not tenant_id:
        return json.dumps({
            "data_source": "Mock Data - Xero not configured",
            "reportName": "Balance Sheet",
            "reportDate": date,
            "note": "Configure XERO_ACCESS_TOKEN and XERO_TENANT_ID for real data"
        }, indent=2)
    
    # Try to get real Xero data
    params = {
        "date": date
    }
    
    result = _make_xero_request("Reports/BalanceSheet", params)
    
    # Check if we got an error
    if result.get("error"):
        return json.dumps({
            "data_source": "Mock Data - Xero API Error",
            "reportName": "Balance Sheet",
            "reportDate": date,
            "error_details": result.get("message", "API connection failed"),
            "note": "Using mock data due to API issues. Check Xero authentication."
        }, indent=2)
    
    # Parse real Xero data
    return _format_report_response(result)

@tool("get_xero_trial_balance", args_schema=XeroReportInput)
def get_xero_trial_balance(
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    periods: int = 1,
    timeframe: str = "MONTH"
) -> str:
    """
    Retrieve Trial Balance report from Xero.
    
    This tool fetches trial balance data showing all account balances
    to ensure debits equal credits.
    """
    try:
        # Set default dates if not provided
        if not fromDate or not toDate:
            default_from, default_to = _get_default_dates()
            fromDate = fromDate or default_from
            toDate = toDate or default_to
        
        params = {
            "fromDate": fromDate,
            "toDate": toDate,
            "periods": periods,
            "timeframe": timeframe
        }
        
        result = _make_xero_request("Reports/TrialBalance", params)
        return _format_report_response(result)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Xero Trial Balance retrieval failed: {str(e)}"

# --- Tool Aggregator ---

def get_xero_tools():
    """Returns a list of all Xero tools in this module."""
    return [
        get_xero_profit_and_loss,
        get_xero_balance_sheet,
        get_xero_trial_balance
    ]
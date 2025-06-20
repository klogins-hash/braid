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
    access_token = os.environ.get("XERO_ACCESS_TOKEN")
    if not access_token:
        # Provide helpful setup instructions
        setup_msg = (
            "XERO_ACCESS_TOKEN environment variable not set. "
            "Run: python -m core.integrations.xero.setup"
        )
        raise ValueError(setup_msg)
    
    tenant_id = os.environ.get("XERO_TENANT_ID")
    if not tenant_id:
        setup_msg = (
            "XERO_TENANT_ID environment variable not set. "
            "Run: python -m core.integrations.xero.setup"
        )
        raise ValueError(setup_msg)
    
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
    base_url = "https://api.xero.com/api.xro/2.0"
    url = f"{base_url}/{endpoint}"
    
    headers = _get_xero_headers(accept_xml=use_xml)
    
    response = requests.get(url, headers=headers, params=params or {}, timeout=30)
    
    if response.status_code == 200:
        if use_xml:
            return {"xml_content": response.text}
        else:
            return response.json()
    else:
        # Enhanced error handling
        error_msg = f"Xero API error: {response.status_code}"
        
        if response.status_code == 401:
            error_msg += " - Authentication failed. Tokens may have expired. Run: python -m core.integrations.xero.setup"
        elif response.status_code == 403:
            error_msg += " - Access denied. Check your Xero app permissions."
        elif response.status_code == 404:
            error_msg += f" - Endpoint not found: {endpoint}"
        else:
            try:
                if "application/json" in response.headers.get("content-type", ""):
                    error_detail = response.json()
                    if "Message" in error_detail:
                        error_msg += f" - {error_detail['Message']}"
                else:
                    error_msg += f" - {response.text[:200]}"
            except:
                error_msg += f" - {response.text[:200]}"
        
        raise Exception(error_msg)

def _get_default_dates() -> tuple[str, str]:
    """Get default from/to dates (1 year period ending today)."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    return one_year_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

def _parse_xml_report(xml_content: str) -> Dict[str, Any]:
    """Parse Xero XML report response into structured data."""
    try:
        root = ET.fromstring(xml_content)
        
        # Find the report
        reports = root.findall('.//Report')
        if not reports:
            return {"error": "No reports found in XML"}
        
        report = reports[0]
        
        # Extract report metadata
        report_name = report.find('ReportName')
        report_date = report.find('ReportDate')
        
        parsed_report = {
            "reportName": report_name.text if report_name is not None else "",
            "reportDate": report_date.text if report_date is not None else "",
            "financial_data": {},
            "rows": []
        }
        
        # Parse rows to extract financial data
        rows = report.findall('.//Row')
        
        for row in rows:
            cells = row.findall('.//Cell')
            
            if len(cells) >= 2:
                account_cell = cells[0].find('Value')
                value_cell = cells[1].find('Value')
                
                if account_cell is not None and value_cell is not None:
                    account_name = account_cell.text or ''
                    value_text = value_cell.text or ''
                    
                    # Store raw row data
                    parsed_report["rows"].append({
                        "account": account_name,
                        "value": value_text
                    })
                    
                    # Extract key financial metrics
                    if value_text and value_text not in ['0', '0.00', '']:
                        try:
                            value_float = float(value_text)
                            account_lower = account_name.lower()
                            
                            if 'total revenue' in account_lower:
                                parsed_report["financial_data"]['total_revenue'] = value_float
                            elif 'total cost of sales' in account_lower or 'cost of goods sold' in account_lower:
                                parsed_report["financial_data"]['total_cogs'] = value_float
                            elif 'gross profit' in account_lower:
                                parsed_report["financial_data"]['gross_profit'] = value_float
                            elif 'total operating expenses' in account_lower:
                                parsed_report["financial_data"]['total_expenses'] = value_float
                            elif any(term in account_lower for term in ['net income', 'net profit', 'net loss']):
                                if 'before tax' not in account_lower:
                                    parsed_report["financial_data"]['net_income'] = value_float
                                    
                        except (ValueError, TypeError):
                            pass
        
        return parsed_report
        
    except ET.ParseError as e:
        return {"error": f"XML parsing error: {e}"}
    except Exception as e:
        return {"error": f"Failed to parse XML report: {e}"}

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
    try:
        # Set default dates if not provided (YTD if not specified)
        if not fromDate or not toDate:
            if not fromDate and not toDate:
                # Default to Year-to-Date
                current_year = datetime.now().year
                fromDate = f"{current_year}-01-01"
                toDate = datetime.now().strftime("%Y-%m-%d")
            else:
                default_from, default_to = _get_default_dates()
                fromDate = fromDate or default_from
                toDate = toDate or default_to
        
        params = {
            "fromDate": fromDate,
            "toDate": toDate,
            "periods": periods,
            "timeframe": timeframe
        }
        
        # Use XML for more reliable parsing
        result = _make_xero_request("Reports/ProfitAndLoss", params, use_xml=True)
        return _format_report_response(result)
        
    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Xero P&L retrieval failed: {str(e)}"}, indent=2)

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
    try:
        # Set default date if not provided
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "date": date,
            "periods": periods,
            "timeframe": timeframe
        }
        
        result = _make_xero_request("Reports/BalanceSheet", params)
        return _format_report_response(result)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Xero Balance Sheet retrieval failed: {str(e)}"

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
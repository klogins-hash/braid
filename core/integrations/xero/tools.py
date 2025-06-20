"""
Public, LLM-callable tools for interacting with Xero API directly.
"""
import os
import json
from typing import Optional, Dict, Any
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

def _get_xero_headers() -> Dict[str, str]:
    """Get Xero API headers with authentication."""
    access_token = os.environ.get("XERO_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("XERO_ACCESS_TOKEN environment variable not set")
    
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Xero-tenant-id": os.environ.get("XERO_TENANT_ID", "")
    }

def _make_xero_request(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Internal helper to make requests to Xero API."""
    base_url = "https://api.xero.com/api.xro/2.0"
    url = f"{base_url}/{endpoint}"
    
    headers = _get_xero_headers()
    
    response = requests.get(url, headers=headers, params=params or {}, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    else:
        error_msg = f"Xero API error: {response.status_code}"
        try:
            error_detail = response.json()
            if "Message" in error_detail:
                error_msg += f" - {error_detail['Message']}"
        except:
            error_msg += f" - {response.text}"
        raise Exception(error_msg)

def _get_default_dates() -> tuple[str, str]:
    """Get default from/to dates (1 year period ending today)."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    return one_year_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

def _format_report_response(report_data: Dict[str, Any]) -> str:
    """Format Xero report response to match MCP server output format."""
    try:
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
        
        result = _make_xero_request("Reports/ProfitAndLoss", params)
        return _format_report_response(result)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Xero P&L retrieval failed: {str(e)}"

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
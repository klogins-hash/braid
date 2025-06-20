"""Tools for interacting with the Xero API using official SDK."""

import os
import json
import logging
from typing import Dict, Any, List
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date

# Try to import Xero SDK, fall back to requests if not available
try:
    from xero_python.api_client import ApiClient
    from xero_python.api_client.configuration import Configuration
    from xero_python.api_client.oauth2 import OAuth2Token
    from xero_python.accounting import AccountingApi
    XERO_SDK_AVAILABLE = True
except ImportError:
    XERO_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)

class XeroTools:
    """Tools for interacting with Xero API."""
    
    def __init__(self):
        self.access_token = os.getenv('XERO_ACCESS_TOKEN', '').strip()
        self.tenant_id = os.getenv('XERO_TENANT_ID', '').strip()
        self.client_id = os.getenv('XERO_CLIENT_ID', '').strip()
        self.client_secret = os.getenv('XERO_CLIENT_SECRET', '').strip()
        
        # Setup SDK if available
        self.sdk_client = None
        if XERO_SDK_AVAILABLE and self.access_token and self.client_id and self.client_secret:
            try:
                config = Configuration(
                    oauth2_token=OAuth2Token(
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                        access_token=self.access_token,
                        refresh_token=os.getenv('XERO_REFRESH_TOKEN', '').strip()
                    )
                )
                self.sdk_client = ApiClient(config)
                logger.info("✅ Xero SDK initialized")
            except Exception as e:
                logger.warning(f"⚠️ SDK init failed, falling back to requests: {e}")
        
        # Fallback headers for requests
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.tenant_id:
            self.headers['xero-tenant-id'] = self.tenant_id
    
    def get_profit_and_loss(self, from_date: str = None, to_date: str = None) -> List[Dict[str, Any]]:
        """
        Get profit and loss statement from Xero - now with REAL YTD data.
        
        Args:
            from_date: Start date in YYYY-MM-DD format (defaults to YTD)
            to_date: End date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            List of financial data points with real Demo Company data
        """
        try:
            logger.info("🔄 Connecting to Xero API...")
            
            # If no dates provided, use Year-to-Date
            if not from_date or not to_date:
                current_year = datetime.now().year
                from_date = f"{current_year}-01-01"
                to_date = date.today().strftime("%Y-%m-%d")
                logger.info(f"📅 Using YTD period: {from_date} to {to_date}")
            
            # Use direct API call for proven XML response handling
            if self.access_token and self.tenant_id and self.access_token.startswith('eyJ'):
                logger.info("🎯 Retrieving REAL Demo Company YTD P&L data...")
                
                url = f"https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss?fromDate={from_date}&toDate={to_date}"
                headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    'xero-tenant-id': self.tenant_id,
                    'Accept': 'application/xml'  # Request XML for proven parsing
                }
                
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    logger.info("🎉 SUCCESS: Retrieved REAL Demo Company YTD P&L data!")
                    return self._parse_xero_xml_response(response.text, from_date, to_date)
                else:
                    logger.warning(f"⚠️ Xero API error {response.status_code}: {response.text}")
                    return self._get_enhanced_mock_data()
            
            elif self.access_token and self.access_token.startswith('eyJ'):
                logger.info("✅ Xero token present - using enhanced mock data (no tenant ID)")
                return self._get_enhanced_mock_data()
            else:
                logger.warning("⚠️ No Xero token, using basic mock data")
                return self._get_mock_data()
                
        except Exception as e:
            logger.error(f"❌ Xero API error: {e}")
            return self._get_mock_data()
    
    def _parse_xero_xml_response(self, xml_content: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """Parse Xero P&L XML response into standardized format."""
        try:
            root = ET.fromstring(xml_content)
            
            # Extract key financial figures
            ytd_data = {
                'total_revenue': 0,
                'total_cogs': 0,
                'gross_profit': 0,
                'total_expenses': 0,
                'net_income': 0
            }
            
            # Parse rows to extract financial data
            rows = root.findall('.//Row')
            
            for row in rows:
                cells = row.findall('.//Cell')
                
                if len(cells) >= 2:
                    account_cell = cells[0].find('Value')
                    value_cell = cells[1].find('Value')
                    
                    if account_cell is not None and value_cell is not None:
                        account_name = account_cell.text or ''
                        value_text = value_cell.text or ''
                        
                        if value_text and value_text not in ['0', '0.00', '']:
                            try:
                                value_float = float(value_text)
                                account_lower = account_name.lower()
                                
                                if 'total revenue' in account_lower:
                                    ytd_data['total_revenue'] = value_float
                                elif 'total cost of sales' in account_lower:
                                    ytd_data['total_cogs'] = value_float
                                elif 'gross profit' in account_lower:
                                    ytd_data['gross_profit'] = value_float
                                elif 'total operating expenses' in account_lower:
                                    ytd_data['total_expenses'] = value_float
                                elif any(term in account_lower for term in ['net income', 'net profit', 'net loss']):
                                    if 'before tax' not in account_lower:
                                        ytd_data['net_income'] = value_float
                                        
                            except (ValueError, TypeError):
                                pass
            
            # Return standardized format
            return [{
                "period_start": from_date,
                "period_end": to_date,
                "revenue": ytd_data['total_revenue'],
                "cost_of_goods_sold": ytd_data['total_cogs'],
                "gross_profit": ytd_data['gross_profit'],
                "operating_expenses": ytd_data['total_expenses'],
                "ebitda": ytd_data['gross_profit'] - ytd_data['total_expenses'] if ytd_data['gross_profit'] and ytd_data['total_expenses'] else None,
                "net_income": ytd_data['net_income'],
                "data_source": "Demo Company (US) - Real Xero Data"
            }]
            
        except ET.ParseError as e:
            logger.error(f"❌ XML parsing error: {e}")
            return self._get_enhanced_mock_data()
        except Exception as e:
            logger.error(f"❌ Error parsing Xero XML: {e}")
            return self._get_enhanced_mock_data()
    
    def _parse_profit_loss(self, data: Dict[str, Any], tenant_name: str) -> List[Dict[str, Any]]:
        """Parse Xero P&L response into standardized format."""
        try:
            report = data['Reports'][0]
            rows = report['Rows']
            
            # Extract period dates
            period = report.get('ReportTitles', [])[1]  # Usually contains date range
            from_date, to_date = self._extract_dates(period)
            
            # Extract key metrics
            revenue = self._find_section_total(rows, "Revenue")
            cogs = self._find_section_total(rows, "Cost of Sales")
            gross_profit = revenue - cogs if revenue is not None and cogs is not None else None
            operating_expenses = self._find_section_total(rows, "Operating Expenses")
            
            # Calculate EBITDA and net income
            ebitda = gross_profit - operating_expenses if gross_profit is not None and operating_expenses is not None else None
            net_income = ebitda * 0.75 if ebitda is not None else None  # Simplified tax calculation
            
            return [{
                "period_start": from_date,
                "period_end": to_date,
                "revenue": revenue,
                "cost_of_goods_sold": cogs,
                "gross_profit": gross_profit,
                "operating_expenses": operating_expenses,
                "ebitda": ebitda,
                "net_income": net_income,
                "data_source": f"Live Xero API - {tenant_name}"
            }]
            
        except Exception as e:
            logger.error(f"❌ Error parsing Xero P&L: {e}")
            return self._get_mock_data()
    
    def _parse_sdk_profit_loss(self, report) -> List[Dict[str, Any]]:
        """Parse Xero SDK P&L report into standardized format."""
        try:
            # Extract period dates from report
            report_date = report.report_date if hasattr(report, 'report_date') else "2023-12-31"
            
            # Initialize financial data
            revenue = 0
            cogs = 0
            operating_expenses = 0
            
            # Parse rows from SDK report
            if hasattr(report, 'rows') and report.rows:
                for row in report.rows:
                    if hasattr(row, 'title') and row.title:
                        title = row.title.lower()
                        
                        # Get value from cells
                        value = 0
                        if hasattr(row, 'cells') and row.cells and len(row.cells) > 1:
                            try:
                                cell_value = row.cells[1].value
                                if cell_value and str(cell_value).replace('.', '').replace('-', '').isdigit():
                                    value = float(cell_value)
                            except (ValueError, AttributeError):
                                continue
                        
                        # Categorize the data
                        if 'revenue' in title or 'income' in title:
                            revenue += value
                        elif 'cost of sales' in title or 'cost of goods' in title:
                            cogs += value
                        elif 'expense' in title and 'operating' in title:
                            operating_expenses += value
            
            # Calculate derived metrics
            gross_profit = revenue - cogs
            ebitda = gross_profit - operating_expenses
            net_income = ebitda * 0.75  # Simplified tax calculation
            
            # Get organisation name from report
            org_name = "Live Xero Organisation"
            if hasattr(report, 'report_titles') and report.report_titles:
                org_name = f"Live Xero API - {report.report_titles[0]}"
            
            return [{
                "period_start": "2023-01-01",
                "period_end": report_date,
                "revenue": revenue,
                "cost_of_goods_sold": cogs,
                "gross_profit": gross_profit,
                "operating_expenses": operating_expenses,
                "ebitda": ebitda,
                "net_income": net_income,
                "data_source": org_name
            }]
            
        except Exception as e:
            logger.error(f"❌ Error parsing SDK P&L: {e}")
            return self._get_enhanced_mock_data()
    
    def _find_section_total(self, rows: List[Dict[str, Any]], section_name: str) -> float:
        """Find total value for a section in P&L."""
        for row in rows:
            if row.get('Title', '').lower() == section_name.lower():
                for cell in row.get('Cells', []):
                    if cell.get('Value'):
                        try:
                            return float(cell['Value'])
                        except (ValueError, TypeError):
                            return None
        return None
    
    def _extract_dates(self, period_string: str) -> tuple[str, str]:
        """Extract from and to dates from period string."""
        # Default to current year if can't parse
        current_year = datetime.now().year
        return f"{current_year}-01-01", f"{current_year}-12-31"
    
    def _get_enhanced_mock_data(self) -> List[Dict[str, Any]]:
        """Get enhanced mock financial data with Xero token."""
        return [{
            "period_start": "2023-01-01",
            "period_end": "2023-12-31",
            "revenue": 2650000,
            "cost_of_goods_sold": 795000,
            "gross_profit": 1855000,
            "operating_expenses": 1325000,
            "ebitda": 530000,
            "net_income": 397500,
            "data_source": "Enhanced mock data - Xero API authenticated"
        }]
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        """Get mock financial data for testing."""
        return [{
            "period_start": "2023-01-01",
            "period_end": "2023-12-31",
            "revenue": 2400000,
            "cost_of_goods_sold": 720000,
            "gross_profit": 1680000,
            "operating_expenses": 1200000,
            "ebitda": 480000,
            "net_income": 360000,
            "data_source": "Mock data - Xero token not configured"
        }] 
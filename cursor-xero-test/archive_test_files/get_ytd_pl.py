#!/usr/bin/env python3
"""
Get Year-to-Date P&L Data from Demo Company (US)
"""

import os
import requests
import xml.etree.ElementTree as ET
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv(override=True)

class YTDHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! Getting YTD P&L...</h1></body></html>')
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def format_currency(value):
    """Format currency values."""
    if not value:
        return "$0.00"
    try:
        val_float = float(value)
        if val_float < 0:
            return f"-${abs(val_float):,.2f}"
        else:
            return f"${val_float:,.2f}"
    except (ValueError, TypeError):
        return str(value)

def parse_ytd_pl_xml(xml_content):
    """Parse YTD P&L XML response and extract key figures."""
    
    try:
        root = ET.fromstring(xml_content)
        
        print("\n" + "="*80)
        print("📊 DEMO COMPANY (US) - YEAR-TO-DATE P&L STATEMENT")
        print("="*80)
        
        # Find the report
        reports = root.findall('.//Report')
        if not reports:
            print("❌ No reports found in XML")
            return None
        
        report = reports[0]
        
        # Extract report metadata
        report_name = report.find('ReportName')
        print(f"📄 Report: {report_name.text if report_name is not None else 'N/A'}")
        
        # Find report titles/periods
        titles = report.findall('.//ReportTitle')
        if titles:
            print(f"📅 Period: {titles[0].text if titles else 'N/A'}")
        
        # Extract key financial figures
        ytd_data = {
            'total_revenue': 0,
            'total_cogs': 0,
            'gross_profit': 0,
            'total_expenses': 0,
            'net_income': 0,
            'revenue_breakdown': [],
            'expense_breakdown': []
        }
        
        print("\n💰 YEAR-TO-DATE FINANCIAL SUMMARY:")
        print("-"*80)
        
        # Parse rows to extract financial data
        rows = report.findall('.//Row')
        
        current_section = ""
        
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
                            formatted_value = format_currency(value_float)
                            
                            # Categorize the line items
                            account_lower = account_name.lower()
                            
                            if 'total revenue' in account_lower:
                                ytd_data['total_revenue'] = value_float
                                print(f"💵 TOTAL REVENUE (YTD):                {formatted_value}")
                                
                            elif 'total cost of sales' in account_lower or 'cost of goods sold' in account_lower:
                                ytd_data['total_cogs'] = value_float
                                print(f"📦 TOTAL COST OF SALES (YTD):          {formatted_value}")
                                
                            elif 'gross profit' in account_lower:
                                ytd_data['gross_profit'] = value_float
                                print(f"💰 GROSS PROFIT (YTD):                 {formatted_value}")
                                
                            elif 'total operating expenses' in account_lower:
                                ytd_data['total_expenses'] = value_float
                                print(f"💸 TOTAL OPERATING EXPENSES (YTD):     {formatted_value}")
                                
                            elif any(term in account_lower for term in ['net income', 'net profit', 'net loss']):
                                if 'before tax' not in account_lower:  # Get the final net income
                                    ytd_data['net_income'] = value_float
                                    if value_float < 0:
                                        print(f"📉 NET LOSS (YTD):                     {formatted_value}")
                                    else:
                                        print(f"📈 NET INCOME (YTD):                   {formatted_value}")
                            
                            # Track revenue items
                            elif any(term in account_lower for term in ['sales', 'revenue', 'income']) and 'total' not in account_lower and 'net' not in account_lower:
                                ytd_data['revenue_breakdown'].append((account_name, value_float))
                            
                            # Track major expense items
                            elif value_float > 100 and any(term in account_lower for term in ['expense', 'wages', 'rent', 'advertising', 'utilities']):
                                ytd_data['expense_breakdown'].append((account_name, value_float))
                                
                        except (ValueError, TypeError):
                            pass
        
        # Show breakdown of revenue sources
        if ytd_data['revenue_breakdown']:
            print(f"\n📊 REVENUE BREAKDOWN (YTD):")
            print("-" * 50)
            for item, amount in sorted(ytd_data['revenue_breakdown'], key=lambda x: x[1], reverse=True):
                print(f"   {item:<35} {format_currency(amount):>12}")
        
        # Show major expenses
        if ytd_data['expense_breakdown']:
            print(f"\n💸 MAJOR EXPENSES (YTD):")
            print("-" * 50)
            for item, amount in sorted(ytd_data['expense_breakdown'], key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {item:<35} {format_currency(amount):>12}")
        
        # Calculate key ratios
        print(f"\n📈 KEY FINANCIAL RATIOS (YTD):")
        print("-" * 50)
        
        if ytd_data['total_revenue'] > 0:
            gross_margin = (ytd_data['gross_profit'] / ytd_data['total_revenue']) * 100
            net_margin = (ytd_data['net_income'] / ytd_data['total_revenue']) * 100
            print(f"   Gross Profit Margin:            {gross_margin:>8.1f}%")
            print(f"   Net Profit Margin:              {net_margin:>8.1f}%")
            
            if ytd_data['total_expenses'] > 0:
                expense_ratio = (ytd_data['total_expenses'] / ytd_data['total_revenue']) * 100
                print(f"   Operating Expense Ratio:        {expense_ratio:>8.1f}%")
        
        print("\n" + "="*80)
        print("🎉 YEAR-TO-DATE P&L DATA SUCCESSFULLY RETRIEVED!")
        print("✅ Your agent now has access to comprehensive YTD financial data")
        print("="*80)
        
        return ytd_data
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return None

def main():
    """Get Year-to-Date P&L data from Demo Company."""
    
    print("📊 DEMO COMPANY YTD P&L ANALYZER")
    print("="*60)
    print("Retrieving Year-to-Date Profit & Loss data")
    
    # Use NEW Xero app
    client_id = "474346C165654911BFFA8A80C108094D"
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    redirect_uri = 'http://localhost:8080/callback'
    
    print(f"\n🔑 Client ID: {client_id}")
    
    if not client_secret:
        print("❌ Missing XERO_CLIENT_SECRET")
        return
    
    # OAuth2 flow
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'ytd_pl'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print("🌐 Starting OAuth2 flow...")
    
    # Start server
    server = HTTPServer(('localhost', 8080), YTDHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    webbrowser.open(auth_url)
    
    # Wait for auth
    timeout = 90
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Authorization timeout")
        server.shutdown()
        return
    
    print("✅ Authorization successful")
    server.shutdown()
    
    # Get token
    token_response = requests.post(
        'https://identity.xero.com/connect/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': server.auth_code,
            'redirect_uri': redirect_uri
        }
    )
    
    if token_response.status_code != 200:
        print(f"❌ Token failed: {token_response.text}")
        return
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    
    # Get connections
    conn_response = requests.get(
        'https://api.xero.com/connections',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    connections = conn_response.json()
    tenant_id = connections[0]['tenantId']
    tenant_name = connections[0].get('tenantName', 'Unknown')
    
    print(f"✅ Connected to: {tenant_name}")
    
    # Get current date for YTD calculation
    current_year = datetime.now().year
    year_start = f"{current_year}-01-01"
    today = date.today().strftime("%Y-%m-%d")
    
    print(f"\n📅 Requesting YTD data: {year_start} to {today}")
    
    # Get YTD P&L data with date parameters
    print("📊 Retrieving YTD P&L data...")
    
    # Try with date parameters for YTD
    pl_response = requests.get(
        f'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss?fromDate={year_start}&toDate={today}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'xero-tenant-id': tenant_id,
            'Accept': 'application/xml'
        }
    )
    
    print(f"📡 Response Status: {pl_response.status_code}")
    print(f"📄 Response Size: {len(pl_response.text)} characters")
    
    if pl_response.status_code == 200:
        print("✅ YTD P&L data received!")
        ytd_data = parse_ytd_pl_xml(pl_response.text)
        
        if ytd_data:
            print(f"\n📋 SUMMARY FOR YOUR AGENT:")
            print(f"Total Revenue YTD: ${ytd_data['total_revenue']:,.2f}")
            print(f"Gross Profit YTD: ${ytd_data['gross_profit']:,.2f}")
            print(f"Net Income YTD: ${ytd_data['net_income']:,.2f}")
            
    else:
        print(f"❌ API call failed: {pl_response.text}")

if __name__ == "__main__":
    main()
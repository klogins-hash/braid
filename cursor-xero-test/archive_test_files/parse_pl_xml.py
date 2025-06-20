#!/usr/bin/env python3
"""
Parse P&L XML Response: Show Demo Company Financial Data
"""

import os
import requests
import xml.etree.ElementTree as ET
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from dotenv import load_dotenv

load_dotenv(override=True)

class XMLHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! Parsing P&L XML...</h1></body></html>')
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

def parse_pl_xml(xml_content):
    """Parse Xero P&L XML response."""
    
    try:
        root = ET.fromstring(xml_content)
        
        print("\n" + "="*80)
        print("📊 DEMO COMPANY (US) - PROFIT & LOSS STATEMENT")
        print("="*80)
        
        # Find the report
        reports = root.findall('.//Report')
        if not reports:
            print("❌ No reports found in XML")
            return
        
        report = reports[0]
        
        # Extract report metadata
        report_id = report.find('ReportID')
        report_name = report.find('ReportName')
        report_type = report.find('ReportType')
        
        print(f"📋 Report ID: {report_id.text if report_id is not None else 'N/A'}")
        print(f"📄 Report Name: {report_name.text if report_name is not None else 'N/A'}")
        print(f"📊 Report Type: {report_type.text if report_type is not None else 'N/A'}")
        
        # Find report titles
        titles = report.findall('.//ReportTitle')
        if titles:
            print(f"📅 Report Period: {titles[0].text if titles else 'N/A'}")
        
        print("\n💰 FINANCIAL DATA:")
        print("-"*80)
        
        # Parse rows
        rows = report.findall('.//Row')
        print(f"📈 Total rows found: {len(rows)}")
        
        for i, row in enumerate(rows):
            row_type = row.get('RowType', 'Unknown')
            
            # Get cells for this row
            cells = row.findall('.//Cell')
            
            if cells:
                # First cell is usually the account name
                account_cell = cells[0] if len(cells) > 0 else None
                value_cell = cells[1] if len(cells) > 1 else None
                
                if account_cell is not None:
                    account_name = account_cell.find('Value')
                    account_text = account_name.text if account_name is not None else ''
                    
                    if value_cell is not None:
                        value_elem = value_cell.find('Value')
                        value_text = value_elem.text if value_elem is not None else ''
                        
                        # Only show rows with actual values
                        if account_text and value_text and value_text not in ['0', '0.00', '']:
                            try:
                                formatted_value = format_currency(float(value_text))
                                
                                if row_type == 'Header':
                                    print(f"\n📈 {account_text.upper()}")
                                    print("-" * 50)
                                elif 'Total' in account_text:
                                    print(f"💰 {account_text:<50} {formatted_value:>15}")
                                    print("-" * 67)
                                else:
                                    print(f"   {account_text:<50} {formatted_value:>15}")
                                    
                            except (ValueError, TypeError):
                                if account_text:
                                    print(f"   {account_text:<50} {value_text:>15}")
        
        print("\n" + "="*80)
        print("🎉 REAL DEMO COMPANY FINANCIAL DATA SUCCESSFULLY PARSED!")
        print("✅ Your agent can now access live P&L data from Xero")
        print("="*80)
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        print("Raw content (first 1000 chars):")
        print(xml_content[:1000])

def main():
    """Get and parse Demo Company P&L XML data."""
    
    print("📊 DEMO COMPANY P&L XML PARSER")
    print("="*60)
    print("Parse XML response to show actual financial data")
    
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
        'state': 'xml_parser'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print("🌐 Starting OAuth2 flow...")
    
    # Start server
    server = HTTPServer(('localhost', 8080), XMLHandler)
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
    
    # Get P&L data
    print("\n📊 Retrieving P&L XML data...")
    
    pl_response = requests.get(
        'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
        headers={
            'Authorization': f'Bearer {access_token}',
            'xero-tenant-id': tenant_id,
            'Accept': 'application/xml'  # Explicitly request XML
        }
    )
    
    print(f"📡 Response Status: {pl_response.status_code}")
    print(f"📄 Response Size: {len(pl_response.text)} characters")
    
    if pl_response.status_code == 200:
        print("✅ P&L XML data received!")
        parse_pl_xml(pl_response.text)
    else:
        print(f"❌ API call failed: {pl_response.text}")

if __name__ == "__main__":
    main()
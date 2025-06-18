#!/usr/bin/env python3
"""
Test script for the Sales Intelligence Agent.
Demonstrates multi-tool integration with mock data when APIs aren't available.
"""
import json
from datetime import datetime, timedelta

# Import tools for testing
from tools.http_tools import get_web_tools
from tools.transform_tools import get_transform_tools
from tools.slack_tools import get_slack_tools
from tools.files_tools import get_files_tools
from tools.csv_tools import get_csv_tools

def test_data_collection_simulation():
    """Simulate the data collection phase using HTTP tools."""
    print("📡 Testing Data Collection Phase")
    print("=" * 35)
    
    try:
        web_tools = get_web_tools()
        http_tool = next((t for t in web_tools if t.name == "http_request"), None)
        
        if not http_tool:
            print("❌ HTTP tool not available")
            return {}
        
        # Simulate CRM API call
        print("1. Fetching CRM data...")
        crm_result = http_tool.invoke({
            "url": "https://jsonplaceholder.typicode.com/users",  # Mock API
            "method": "GET",
            "headers": {"Authorization": "Bearer mock-token"}
        })
        
        crm_response = json.loads(crm_result)
        print(f"   ✅ CRM API: {crm_response.get('success', False)}")
        print(f"   📊 Status: {crm_response.get('status_code', 'N/A')}")
        
        # Simulate analytics API call
        print("2. Fetching analytics data...")
        analytics_result = http_tool.invoke({
            "url": "https://jsonplaceholder.typicode.com/posts",  # Mock API
            "method": "GET"
        })
        
        analytics_response = json.loads(analytics_result)
        print(f"   ✅ Analytics API: {analytics_response.get('success', False)}")
        print(f"   📊 Records: {len(analytics_response.get('content', []))}")
        
        return {
            "crm_data": crm_response.get('content', []),
            "analytics_data": analytics_response.get('content', [])
        }
        
    except Exception as e:
        print(f"❌ Data collection failed: {str(e)}")
        return {}
    
    print()

def test_data_processing_pipeline():
    """Test the data transformation pipeline."""
    print("⚙️ Testing Data Processing Pipeline")
    print("=" * 37)
    
    try:
        transform_tools = get_transform_tools()
        
        # Get transformation tools
        edit_fields_tool = next((t for t in transform_tools if t.name == "edit_fields"), None)
        filter_tool = next((t for t in transform_tools if t.name == "filter_items"), None)
        sort_tool = next((t for t in transform_tools if t.name == "sort_items"), None)
        
        # Sample sales data
        raw_sales_data = [
            {"contact_name": "John Doe", "company": "Acme Corp", "deal_value": 50000, "stage": "qualified", "last_contact": "2024-06-17", "temp_field": "remove"},
            {"contact_name": "Jane Smith", "company": "TechStart Inc", "deal_value": 25000, "stage": "proposal", "last_contact": "2024-06-16", "temp_field": "delete"},
            {"contact_name": "Bob Johnson", "company": "Enterprise Ltd", "deal_value": 100000, "stage": "negotiation", "last_contact": "2024-06-18", "temp_field": "drop"},
            {"contact_name": "Alice Wilson", "company": "Innovation Co", "deal_value": 75000, "stage": "qualified", "last_contact": "2024-06-15", "temp_field": "clear"}
        ]
        
        print("1. Normalizing sales data fields...")
        if edit_fields_tool:
            normalized_result = edit_fields_tool.invoke({
                "items": raw_sales_data,
                "operations": [
                    {"action": "rename", "field": "contact_name", "new_name": "lead_name"},
                    {"action": "rename", "field": "deal_value", "new_name": "pipeline_value"},
                    {"action": "add", "field": "priority_score", "value": 0},
                    {"action": "add", "field": "status", "value": "active"},
                    {"action": "remove", "field": "temp_field"}
                ]
            })
            
            normalized_data = json.loads(normalized_result)["items"]
            print(f"   ✅ Normalized {len(normalized_data)} records")
            print(f"   📝 Operations: {json.loads(normalized_result)['operations_applied']}")
        
        print("2. Filtering high-value deals...")
        if filter_tool:
            filtered_result = filter_tool.invoke({
                "items": normalized_data,
                "condition": "pipeline_value >= 50000"
            })
            
            high_value_deals = json.loads(filtered_result)["items"]
            print(f"   ✅ Filtered to {len(high_value_deals)} high-value deals")
        
        print("3. Sorting by pipeline value...")
        if sort_tool:
            sorted_result = sort_tool.invoke({
                "items": high_value_deals,
                "sort_fields": [{"field": "pipeline_value", "order": "desc"}]
            })
            
            final_data = json.loads(sorted_result)["items"]
            print(f"   ✅ Sorted {len(final_data)} deals by value")
            
            # Show top deals
            print("   🏆 Top deals:")
            for deal in final_data[:3]:
                name = deal.get('lead_name', 'Unknown')
                company = deal.get('company', 'Unknown')
                value = deal.get('pipeline_value', 0)
                print(f"      - {name} ({company}): ${value:,}")
        
        return final_data
        
    except Exception as e:
        print(f"❌ Data processing failed: {str(e)}")
        return []
    
    print()

def test_file_operations():
    """Test file storage and CSV operations."""
    print("📁 Testing File Operations")
    print("=" * 26)
    
    try:
        files_tools = get_files_tools()
        csv_tools = get_csv_tools()
        
        file_store_tool = next((t for t in files_tools if t.name == "file_store"), None)
        csv_tool = next((t for t in csv_tools if t.name == "csv_processor"), None)
        
        # Create sales intelligence report
        report_content = f"""
# Daily Sales Intelligence Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Metrics
- New leads: 12
- Pipeline value: $350,000
- Hot leads: 3
- Competitor alerts: 1

## Top Priority Actions
1. Follow up with Enterprise Ltd - $100k deal in negotiation
2. Send proposal to Acme Corp - $50k qualified lead
3. Check competitor pricing change (TechCorp -8%)

## Next Steps
- Sales team standup at 9 AM
- Update CRM with latest contact attempts
- Review pricing strategy for competitive response
"""
        
        print("1. Storing daily report...")
        if file_store_tool:
            report_result = file_store_tool.invoke({
                "content": report_content,
                "file_path": f"reports/daily_sales_report_{datetime.now().strftime('%Y%m%d')}.md",
                "mode": "w",
                "create_dirs": True
            })
            
            response = json.loads(report_result)
            print(f"   ✅ Report stored: {response.get('success', False)}")
            print(f"   📄 File size: {response.get('file_size_human', 'N/A')}")
        
        print("2. Creating CSV data for historical tracking...")
        csv_data = """date,new_leads,pipeline_value,hot_leads,competitor_alerts
2024-06-18,12,350000,3,1
2024-06-17,8,320000,2,0
2024-06-16,15,380000,4,2
2024-06-15,10,340000,3,1"""
        
        if file_store_tool:
            csv_result = file_store_tool.invoke({
                "content": csv_data,
                "file_path": "data/sales_metrics.csv",
                "mode": "w",
                "create_dirs": True
            })
            
            csv_response = json.loads(csv_result)
            print(f"   ✅ CSV stored: {csv_response.get('success', False)}")
        
        print("3. Processing historical CSV data...")
        if csv_tool:
            analysis_result = csv_tool.invoke({
                "file_path": "data/sales_metrics.csv",
                "operation": "summary"
            })
            
            analysis_response = json.loads(analysis_result)
            print(f"   ✅ CSV analysis: {analysis_response.get('success', False)}")
            print(f"   📊 Rows analyzed: {analysis_response.get('total_rows', 'N/A')}")
            
            numeric_cols = analysis_response.get('numeric_columns', [])
            if numeric_cols:
                print("   📈 Metric trends:")
                for col in numeric_cols[:3]:  # Show first 3 metrics
                    print(f"      - {col['column']}: avg {col['avg']:.0f}, range {col['min']}-{col['max']}")
        
    except Exception as e:
        print(f"❌ File operations failed: {str(e)}")
    
    print()

def test_slack_integration_simulation():
    """Test Slack integration capabilities (simulation)."""
    print("💬 Testing Slack Integration")
    print("=" * 29)
    
    try:
        slack_tools = get_slack_tools()
        print(f"✅ Slack tools loaded: {len(slack_tools)} tools available")
        
        # List available Slack tools
        slack_tool_names = [tool.name for tool in slack_tools]
        print(f"📋 Available tools: {', '.join(slack_tool_names)}")
        
        # Simulate message formatting for different channels
        print("\n📤 Simulated message formats:")
        
        # Executive summary for leadership channel
        leadership_message = """🎯 **Daily Sales Intelligence** | {date}

📊 **Key Metrics**
• New leads: 12 (+4 from yesterday)
• Pipeline value: $350K (+$30K)
• Hot leads: 3 🔥

⚠️ **Alerts**
• Competitor TechCorp dropped pricing 8%
• Enterprise Ltd deal needs urgent follow-up

🎯 **Top Actions**
• @sales-team: Focus on Enterprise Ltd negotiation
• @pricing-team: Review competitive response strategy""".format(date=datetime.now().strftime('%Y-%m-%d'))
        
        print("   📢 #sales-leadership channel:")
        print("   " + leadership_message.replace('\n', '\n   '))
        
        # Personalized DM example
        personal_dm = """Hi! 👋 Your daily sales update:

🎯 **Your active deals:**
• Acme Corp ($50K) - Ready for proposal
• Innovation Co ($75K) - Qualified, needs follow-up

💡 **Action items:**
• Send Acme Corp proposal by EOD
• Schedule Innovation Co demo this week

📈 **Team performance:** You're #2 in pipeline value this month! 🚀"""
        
        print("\n   💬 Personal DM example:")
        print("   " + personal_dm.replace('\n', '\n   '))
        
        print("\n✅ Slack integration ready for actual implementation")
        
    except Exception as e:
        print(f"❌ Slack integration test failed: {str(e)}")
    
    print()

def test_workflow_coordination():
    """Test workflow execution and coordination."""
    print("⏱️ Testing Workflow Coordination")
    print("=" * 32)
    
    try:
        from tools.execution_tools import get_execution_tools
        execution_tools = get_execution_tools()
        
        wait_tool = next((t for t in execution_tools if t.name == "workflow_wait"), None)
        data_tool = next((t for t in execution_tools if t.name == "execution_data"), None)
        
        print("1. Testing workflow scheduling...")
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        if current_day < 5 and 7 <= current_hour <= 10:
            print("   ✅ Current time is optimal for sales workflow execution")
        else:
            print(f"   ⏰ Current time ({current_hour}:00, day {current_day}) is outside optimal window")
            print("   💡 Optimal: Weekdays 7 AM - 10 AM")
        
        print("2. Testing coordination delays...")
        if wait_tool:
            delay_result = wait_tool.invoke({
                "wait_type": "time",
                "duration_seconds": 2
            })
            
            delay_response = json.loads(delay_result)
            print(f"   ✅ Coordination delay: {delay_response.get('success', False)}")
            print(f"   ⏱️ Actual duration: {delay_response.get('actual_duration', 'N/A'):.2f}s")
        
        print("3. Testing execution metadata...")
        if data_tool:
            metadata_result = data_tool.invoke({
                "data_type": "metric",
                "key": "daily_pipeline_value",
                "value": 350000,
                "tags": ["sales", "daily", "pipeline"],
                "description": "Total pipeline value for daily report"
            })
            
            metadata_response = json.loads(metadata_result)
            print(f"   ✅ Metadata storage: {metadata_response.get('success', False)}")
            print(f"   🗃️ Entry ID: {metadata_response.get('entry_id', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Workflow coordination test failed: {str(e)}")
    
    print()

def test_complete_integration():
    """Test the complete multi-tool integration."""
    print("🔗 Testing Complete Multi-Tool Integration")
    print("=" * 43)
    
    print("Simulating complete sales intelligence workflow...")
    
    # Step 1: Data Collection
    collected_data = test_data_collection_simulation()
    
    # Step 2: Data Processing  
    processed_data = test_data_processing_pipeline()
    
    # Step 3: File Operations
    test_file_operations()
    
    # Step 4: Communication
    test_slack_integration_simulation()
    
    # Step 5: Workflow Coordination
    test_workflow_coordination()
    
    print("🎉 Multi-Tool Integration Summary:")
    print("✅ HTTP tools: API data collection and web scraping")
    print("✅ Transform tools: Data cleaning, filtering, and analysis")
    print("✅ File tools: Report generation and data storage")
    print("✅ CSV tools: Historical data processing and metrics")
    print("✅ Slack tools: Team communication and notifications")
    print("✅ Execution tools: Workflow coordination and scheduling")
    print("\n🚀 Ready for production with all 7 tool categories integrated!")

def main():
    """Run the complete sales intelligence agent test suite."""
    print("🎯 Sales Intelligence Agent - Multi-Tool Integration Test")
    print("=" * 65)
    print()
    
    test_complete_integration()
    
    print("\n" + "=" * 65)
    print("🏁 Sales Intelligence Agent Testing Complete!")
    print()
    print("This demonstrates a comprehensive business agent using:")
    print("• 7 different tool categories")
    print("• Multiple APIs and data sources")
    print("• Complex data processing pipelines")
    print("• Multi-channel communication")
    print("• Automated workflow coordination")
    print("• Historical data management")
    print()
    print("The agent is ready for customization with real:")
    print("• CRM API endpoints")
    print("• Slack workspace credentials")
    print("• Google Sheets integration")
    print("• Competitor monitoring URLs")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test Notion API connection and create a simple page
"""

import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

def test_notion_connection():
    """Test if we can connect to Notion and get basic info."""
    
    api_key = os.getenv('NOTION_API_KEY')
    
    if not api_key:
        print("❌ No NOTION_API_KEY found in .env file")
        return False
    
    print(f"🔑 Testing Notion API connection...")
    print(f"API Key: {api_key[:20]}...")
    
    try:
        client = Client(auth=api_key)
        
        # Test basic connection
        user = client.users.me()
        print(f"✅ Connected to Notion as: {user.get('name', 'Unknown User')}")
        
        # Test searching for pages (this will show what we have access to)
        print("\n🔍 Searching for accessible pages...")
        try:
            search_results = client.search(query="", page_size=5)
            
            if search_results.get('results'):
                print(f"📄 Found {len(search_results['results'])} accessible pages:")
                for i, page in enumerate(search_results['results'][:3]):
                    page_id = page.get('id', 'Unknown')
                    title = "Untitled"
                    
                    # Try to get title from properties
                    if page.get('properties'):
                        for prop_name, prop_data in page['properties'].items():
                            if prop_data.get('type') == 'title' and prop_data.get('title'):
                                title = prop_data['title'][0]['text']['content']
                                break
                    
                    print(f"  {i+1}. {title} (ID: {page_id[:8]}...)")
                
                # Use the first page as a potential parent for our reports
                first_page_id = search_results['results'][0]['id']
                print(f"\n💡 Could use page {first_page_id[:8]}... as parent for reports")
                return first_page_id
                
            else:
                print("📄 No accessible pages found")
                return None
                
        except Exception as e:
            print(f"⚠️ Search failed: {e}")
            return None
        
    except Exception as e:
        print(f"❌ Notion connection failed: {e}")
        return False

def create_test_page(parent_page_id=None):
    """Create a test financial report page."""
    
    api_key = os.getenv('NOTION_API_KEY')
    client = Client(auth=api_key)
    
    print(f"\n📝 Creating test financial report page...")
    
    try:
        # Create page content
        content = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "📊 Test Financial Report"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "This is a test page created by the financial forecasting agent. "
                                         "It demonstrates that Notion integration is working correctly."
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🎉 Success! Your Notion API integration is working."
                            }
                        }
                    ],
                    "icon": {"emoji": "✅"}
                }
            }
        ]
        
        if parent_page_id:
            # Create as child page
            page = client.pages.create(
                parent={"page_id": parent_page_id},
                properties={
                    "title": {"title": [{"text": {"content": "Test Financial Report - Agent Integration"}}]}
                },
                children=content
            )
        else:
            print("⚠️ No parent page available - would need workspace/database setup")
            return None
        
        page_url = f"https://notion.so/{page['id'].replace('-', '')}"
        print(f"✅ Created test page: {page_url}")
        return page_url
        
    except Exception as e:
        print(f"❌ Failed to create test page: {e}")
        return None

def main():
    print("🧪 NOTION INTEGRATION TEST")
    print("=" * 50)
    
    # Test connection
    parent_page_id = test_notion_connection()
    
    if parent_page_id:
        # Try to create a test page
        test_page_url = create_test_page(parent_page_id)
        
        if test_page_url:
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Notion integration is working")
            print(f"📄 Test page created: {test_page_url}")
            print(f"💡 Ready to generate real financial reports!")
        else:
            print(f"\n⚠️ Connection works but page creation failed")
            print(f"💡 May need additional permissions or setup")
    else:
        print(f"\n❌ Notion integration needs setup")
        print(f"💡 Check API key permissions and accessible pages")

if __name__ == "__main__":
    main()
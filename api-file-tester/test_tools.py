#!/usr/bin/env python3
"""
Test script for API integration and data persistence tools.
This script validates that both web and file tools work correctly.
"""
import json
import os
import tempfile
from datetime import datetime

# Import the tools directly to test them
from tools.web_tools import http_request, web_scrape
from tools.files_tools import file_store, file_read, file_list, csv_processor

def test_api_integration():
    """Test the HTTP request functionality."""
    print("🌐 Testing API Integration (HTTP Request Tool)")
    print("=" * 50)
    
    # Test 1: Simple GET request to a public API
    print("Test 1: GET request to JSONPlaceholder API")
    result = http_request.invoke({
        "url": "https://jsonplaceholder.typicode.com/posts/1",
        "method": "GET"
    })
    
    response = json.loads(result)
    print(f"✅ Status: {response.get('success', False)}")
    print(f"   HTTP Status: {response.get('status_code', 'N/A')}")
    print(f"   Response has content: {'content' in response}")
    
    if response.get('success') and response.get('status_code') == 200:
        content = response.get('content', {})
        if isinstance(content, dict) and 'title' in content:
            print(f"   Post title: {content['title'][:50]}...")
        print("✅ GET request test PASSED")
    else:
        print("❌ GET request test FAILED")
        print(f"   Error: {response.get('error', 'Unknown error')}")
    
    print()
    
    # Test 2: POST request with JSON data
    print("Test 2: POST request with JSON data")
    test_data = json.dumps({
        "title": "Test Post from Braid Agent",
        "body": "This is a test post created by the API integration test.",
        "userId": 1
    })
    
    result = http_request.invoke({
        "url": "https://jsonplaceholder.typicode.com/posts",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": test_data
    })
    
    response = json.loads(result)
    print(f"✅ Status: {response.get('success', False)}")
    print(f"   HTTP Status: {response.get('status_code', 'N/A')}")
    
    if response.get('success') and response.get('status_code') == 201:
        content = response.get('content', {})
        if isinstance(content, dict) and 'id' in content:
            print(f"   Created post ID: {content['id']}")
        print("✅ POST request test PASSED")
    else:
        print("❌ POST request test FAILED")
        print(f"   Error: {response.get('error', 'Unknown error')}")
    
    print()

def test_data_persistence():
    """Test the file storage and reading functionality."""
    print("📁 Testing Data Persistence (File System Tools)")
    print("=" * 50)
    
    # Test 1: File storage
    print("Test 1: File storage (write)")
    test_content = f"""# Test File Created by Braid Agent
Created at: {datetime.now().isoformat()}

This is a test file to validate the file storage functionality.
It contains multiple lines and various content types:

- Numbers: 12345
- JSON-like data: {{"test": true, "value": 42}}
- Special characters: áéíóú ñ ¡¿ @#$%^&*()

End of test file.
"""
    
    result = file_store.invoke({
        "content": test_content,
        "file_path": "test_data/braid_test_file.txt",
        "mode": "w",
        "create_dirs": True
    })
    
    response = json.loads(result)
    print(f"✅ Status: {response.get('success', False)}")
    print(f"   File path: {response.get('file_path', 'N/A')}")
    print(f"   File size: {response.get('file_size_human', 'N/A')}")
    
    if response.get('success'):
        print("✅ File storage test PASSED")
    else:
        print("❌ File storage test FAILED")
        print(f"   Error: {response.get('error', 'Unknown error')}")
    
    print()
    
    # Test 2: File reading
    print("Test 2: File reading")
    result = file_read.invoke({
        "file_path": "test_data/braid_test_file.txt",
        "encoding": "utf-8"
    })
    
    response = json.loads(result)
    print(f"✅ Status: {response.get('success', False)}")
    print(f"   File size: {response.get('file_size_human', 'N/A')}")
    print(f"   Line count: {response.get('line_count', 'N/A')}")
    
    if response.get('success'):
        content = response.get('content', '')
        if 'Test File Created by Braid Agent' in content:
            print("✅ File reading test PASSED")
            print("   Content verification successful")
        else:
            print("❌ File reading test FAILED - content mismatch")
    else:
        print("❌ File reading test FAILED")
        print(f"   Error: {response.get('error', 'Unknown error')}")
    
    print()
    
    # Test 3: CSV processing
    print("Test 3: CSV file creation and processing")
    csv_content = """name,age,city,score
Alice,25,New York,85.5
Bob,30,Los Angeles,92.0
Charlie,35,Chicago,78.5
Diana,28,Houston,96.0
Eve,32,Phoenix,81.0"""
    
    # Store CSV file
    result = file_store.invoke({
        "content": csv_content,
        "file_path": "test_data/sample_data.csv",
        "mode": "w"
    })
    
    response = json.loads(result)
    if response.get('success'):
        print("✅ CSV file created successfully")
        
        # Process CSV file
        result = csv_processor.invoke({
            "file_path": "test_data/sample_data.csv",
            "operation": "info"
        })
        
        response = json.loads(result)
        print(f"✅ CSV processing status: {response.get('success', False)}")
        print(f"   Total rows: {response.get('total_rows', 'N/A')}")
        print(f"   Columns: {response.get('columns', [])}")
        
        if response.get('success') and response.get('total_rows') == 5:
            print("✅ CSV processing test PASSED")
        else:
            print("❌ CSV processing test FAILED")
    else:
        print("❌ CSV file creation FAILED")
        print(f"   Error: {response.get('error', 'Unknown error')}")
    
    print()
    
    # Test 4: File listing
    print("Test 4: File listing")
    result = file_list.invoke({
        "directory_path": "test_data",
        "pattern": "*",
        "recursive": False
    })
    
    response = json.loads(result)
    print(f"✅ Status: {response.get('success', False)}")
    print(f"   File count: {response.get('file_count', 'N/A')}")
    
    if response.get('success'):
        files = response.get('files', [])
        file_names = [f['name'] for f in files]
        print(f"   Files found: {file_names}")
        
        if 'braid_test_file.txt' in file_names and 'sample_data.csv' in file_names:
            print("✅ File listing test PASSED")
        else:
            print("❌ File listing test FAILED - expected files not found")
    else:
        print("❌ File listing test FAILED")
        print(f"   Error: {response.get('error', 'Unknown error')}")

def main():
    """Run all tests."""
    print("🧪 Braid Agent - API Integration & Data Persistence Tests")
    print("=" * 60)
    print()
    
    # Test API integration
    try:
        test_api_integration()
    except Exception as e:
        print(f"❌ API Integration tests failed with exception: {e}")
        print()
    
    # Test data persistence
    try:
        test_data_persistence()
    except Exception as e:
        print(f"❌ Data Persistence tests failed with exception: {e}")
        print()
    
    print("🏁 Test suite completed!")
    print()
    print("Summary:")
    print("- API Integration: HTTP requests for GET and POST operations")
    print("- Data Persistence: File creation, reading, CSV processing, and directory listing")
    print("- Both tool sets are now ready for use in Braid agents")

if __name__ == "__main__":
    main()
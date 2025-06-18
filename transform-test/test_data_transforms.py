#!/usr/bin/env python3
"""
Test script for n8n-inspired data transformation tools.
Tests the core ETL-style transformation capabilities.
"""
import json
from tools.transform_tools import get_transform_tools

def test_edit_fields():
    """Test the edit_fields tool for data normalization."""
    print("📝 Testing Edit Fields Tool")
    print("=" * 30)
    
    try:
        transform_tools = get_transform_tools()
        edit_tool = next((t for t in transform_tools if t.name == "edit_fields"), None)
        
        if not edit_tool:
            print("❌ Edit fields tool not found")
            return
            
        # Test data
        test_items = [
            {"first_name": "John", "last_name": "Doe", "age": 30, "temp_field": "remove_me"},
            {"first_name": "Jane", "last_name": "Smith", "age": 25, "temp_field": "also_remove"}
        ]
        
        # Operations to test
        operations = [
            {"action": "add", "field": "status", "value": "active"},
            {"action": "rename", "field": "first_name", "new_name": "given_name"},
            {"action": "rename", "field": "last_name", "new_name": "family_name"},
            {"action": "remove", "field": "temp_field"}
        ]
        
        result = edit_tool.invoke({
            "items": test_items,
            "operations": operations
        })
        
        response = json.loads(result)
        print(f"✅ Success: {response.get('success', False)}")
        print(f"   Operations applied: {response.get('operations_applied', {})}")
        print(f"   Sample result: {response.get('items', [{}])[0] if response.get('items') else 'None'}")
        
    except Exception as e:
        print(f"❌ Edit fields test failed: {str(e)}")
    
    print()

def test_filter_items():
    """Test the filter_items tool for data selection."""
    print("🔍 Testing Filter Items Tool")
    print("=" * 30)
    
    try:
        transform_tools = get_transform_tools()
        filter_tool = next((t for t in transform_tools if t.name == "filter_items"), None)
        
        if not filter_tool:
            print("❌ Filter items tool not found")
            return
            
        # Test data
        test_items = [
            {"name": "Alice", "age": 30, "department": "Engineering", "salary": 75000},
            {"name": "Bob", "age": 35, "department": "Marketing", "salary": 65000},
            {"name": "Charlie", "age": 28, "department": "Engineering", "salary": 80000},
            {"name": "Diana", "age": 42, "department": "Sales", "salary": 70000},
            {"name": "Eve", "age": 26, "department": "Engineering", "salary": 72000}
        ]
        
        # Test different filter conditions
        test_cases = [
            {"condition": "age > 30", "description": "Age greater than 30"},
            {"condition": "department == Engineering", "description": "Engineering department"},
            {"condition": "salary >= 75000", "description": "Salary 75k or more"}
        ]
        
        for test_case in test_cases:
            print(f"Test: {test_case['description']}")
            result = filter_tool.invoke({
                "items": test_items,
                "condition": test_case["condition"],
                "limit": 3
            })
            
            response = json.loads(result)
            print(f"   ✅ Success: {response.get('success', False)}")
            print(f"   Filtered: {response.get('original_count', 0)} → {response.get('filtered_count', 0)} items")
            if response.get('items'):
                names = [item.get('name', 'Unknown') for item in response['items']]
                print(f"   Results: {names}")
            print()
        
    except Exception as e:
        print(f"❌ Filter items test failed: {str(e)}")
    
    print()

def test_date_time():
    """Test the date_time tool for temporal operations."""
    print("📅 Testing Date & Time Tool")
    print("=" * 30)
    
    try:
        transform_tools = get_transform_tools()
        date_tool = next((t for t in transform_tools if t.name == "date_time"), None)
        
        if not date_tool:
            print("❌ Date time tool not found")
            return
            
        # Test different date operations
        test_cases = [
            {
                "operation": "now",
                "description": "Get current timestamp"
            },
            {
                "operation": "add",
                "date_value": "now",
                "amount": 7,
                "unit": "days",
                "description": "Add 7 days to now"
            },
            {
                "operation": "format",
                "date_value": "now",
                "format_string": "%B %d, %Y at %I:%M %p",
                "description": "Format current time"
            }
        ]
        
        for test_case in test_cases:
            print(f"Test: {test_case['description']}")
            
            params = {"operation": test_case["operation"]}
            if "date_value" in test_case:
                params["date_value"] = test_case["date_value"]
            if "amount" in test_case:
                params["amount"] = test_case["amount"]
            if "unit" in test_case:
                params["unit"] = test_case["unit"]
            if "format_string" in test_case:
                params["format_string"] = test_case["format_string"]
            
            result = date_tool.invoke(params)
            response = json.loads(result)
            
            print(f"   ✅ Success: {response.get('success', False)}")
            print(f"   Result: {response.get('result_formatted', 'N/A')}")
            print()
        
    except Exception as e:
        print(f"❌ Date time test failed: {str(e)}")
    
    print()

def test_sort_and_rename():
    """Test sort_items and rename_keys tools."""
    print("🔄 Testing Sort & Rename Tools") 
    print("=" * 33)
    
    try:
        transform_tools = get_transform_tools()
        sort_tool = next((t for t in transform_tools if t.name == "sort_items"), None)
        rename_tool = next((t for t in transform_tools if t.name == "rename_keys"), None)
        
        # Test data
        test_items = [
            {"employee_id": 3, "full_name": "Charlie Brown", "hire_date": "2022-03-15", "score": 85},
            {"employee_id": 1, "full_name": "Alice Johnson", "hire_date": "2021-01-10", "score": 92},
            {"employee_id": 2, "full_name": "Bob Wilson", "hire_date": "2021-11-22", "score": 78}
        ]
        
        # Test sorting
        if sort_tool:
            print("Test: Sort by score (descending)")
            result = sort_tool.invoke({
                "items": test_items,
                "sort_fields": [{"field": "score", "order": "desc"}]
            })
            
            response = json.loads(result)
            print(f"   ✅ Sort success: {response.get('success', False)}")
            if response.get('items'):
                scores = [item.get('score', 0) for item in response['items']]
                print(f"   Sorted scores: {scores}")
            print()
        
        # Test key renaming
        if rename_tool:
            print("Test: Rename keys for standardization")
            key_mapping = {
                "employee_id": "id",
                "full_name": "name", 
                "hire_date": "start_date"
            }
            
            result = rename_tool.invoke({
                "items": test_items,
                "key_mapping": key_mapping
            })
            
            response = json.loads(result)
            print(f"   ✅ Rename success: {response.get('success', False)}")
            print(f"   Rename stats: {response.get('rename_statistics', {})}")
            if response.get('items'):
                sample_keys = list(response['items'][0].keys()) if response['items'] else []
                print(f"   New keys: {sample_keys}")
            print()
        
    except Exception as e:
        print(f"❌ Sort/rename test failed: {str(e)}")
    
    print()

def test_etl_pipeline():
    """Test a complete ETL pipeline using multiple transformation tools."""
    print("🔄 Testing Complete ETL Pipeline")
    print("=" * 35)
    
    try:
        transform_tools = get_transform_tools()
        
        # Get all tools
        tools = {}
        for tool in transform_tools:
            tools[tool.name] = tool
        
        # Sample raw data (messy format)
        raw_data = [
            {"first": "John", "last": "Doe", "birthYear": 1990, "dept": "eng", "temp": "delete"},
            {"first": "Jane", "last": "Smith", "birthYear": 1985, "dept": "marketing", "temp": "remove"},
            {"first": "Bob", "last": "Johnson", "birthYear": 1995, "dept": "eng", "temp": "drop"},
            {"first": "Alice", "last": "Williams", "birthYear": 1988, "dept": "sales", "temp": "clear"}
        ]
        
        print("Step 1: Clean and normalize fields")
        # Step 1: Edit fields - rename, add computed fields, remove temp
        if "edit_fields" in tools:
            result = tools["edit_fields"].invoke({
                "items": raw_data,
                "operations": [
                    {"action": "rename", "field": "first", "new_name": "first_name"},
                    {"action": "rename", "field": "last", "new_name": "last_name"},
                    {"action": "rename", "field": "dept", "new_name": "department"},
                    {"action": "add", "field": "status", "value": "active"},
                    {"action": "remove", "field": "temp"}
                ]
            })
            
            step1_data = json.loads(result)["items"]
            print(f"   ✅ Cleaned {len(step1_data)} records")
        
        print("Step 2: Filter for engineering department")
        # Step 2: Filter for engineering department
        if "filter_items" in tools:
            result = tools["filter_items"].invoke({
                "items": step1_data,
                "condition": "department == eng"
            })
            
            step2_data = json.loads(result)["items"]
            print(f"   ✅ Filtered to {len(step2_data)} engineering records")
        
        print("Step 3: Add computed age field and sort")
        # Step 3: Add age calculation and sort by age
        current_year = 2024
        for item in step2_data:
            item["age"] = current_year - item["birthYear"]
        
        if "sort_items" in tools:
            result = tools["sort_items"].invoke({
                "items": step2_data,
                "sort_fields": [{"field": "age", "order": "asc"}]
            })
            
            final_data = json.loads(result)["items"]
            print(f"   ✅ Sorted {len(final_data)} records by age")
            
            # Show final result
            print("\nFinal ETL Result:")
            for item in final_data:
                name = f"{item.get('first_name', '')} {item.get('last_name', '')}"
                age = item.get('age', 'N/A')
                dept = item.get('department', 'N/A')
                print(f"   - {name}, {age} years old, {dept} department")
        
    except Exception as e:
        print(f"❌ ETL pipeline test failed: {str(e)}")
    
    print()

def main():
    """Run all transformation tool tests."""
    print("🔧 Braid - n8n-Inspired Data Transformation Tools Test")
    print("=" * 60)
    print()
    
    test_edit_fields()
    test_filter_items()
    test_date_time()
    test_sort_and_rename()
    test_etl_pipeline()
    
    print("🎉 Data transformation tools testing complete!")
    print()
    print("Tools Implemented:")
    print("✅ edit_fields: Rename, add, remove fields on data items")
    print("✅ filter_items: Keep only items matching conditions") 
    print("✅ date_time: Manipulate dates/times and calculate intervals")
    print("✅ sort_items: Order items by one or more fields")
    print("✅ rename_keys: Bulk-rename field names via mapping")
    print()
    print("These tools enable powerful ETL-style data processing workflows!")

if __name__ == "__main__":
    main()
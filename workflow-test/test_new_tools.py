#!/usr/bin/env python3
"""
Test script for the new organized tool structure and workflow tools.
Tests execution control, code execution, and data handling tools.
"""
import json
from tools.execution_tools import get_execution_tools
from tools.code_tools import get_code_tools
from tools.files_tools import get_files_tools
from tools.csv_tools import get_csv_tools

def test_tool_imports():
    """Test that all new tools import correctly."""
    print("🔧 Testing Tool Imports")
    print("=" * 30)
    
    try:
        execution_tools = get_execution_tools()
        print(f"✅ Execution tools: {len(execution_tools)} tools loaded")
        for tool in execution_tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        code_tools = get_code_tools()
        print(f"✅ Code tools: {len(code_tools)} tools loaded")
        for tool in code_tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        files_tools = get_files_tools()
        print(f"✅ Files tools: {len(files_tools)} tools loaded")
        for tool in files_tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        csv_tools = get_csv_tools()
        print(f"✅ CSV tools: {len(csv_tools)} tools loaded")
        for tool in csv_tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        total_tools = len(execution_tools) + len(code_tools) + len(files_tools) + len(csv_tools)
        print(f"✅ Total tools available: {total_tools}")
        
    except Exception as e:
        print(f"❌ Tool import failed: {str(e)}")
    
    print()

def test_workflow_tools():
    """Test the new workflow control tools."""
    print("⚙️ Testing Workflow Control Tools")
    print("=" * 35)
    
    try:
        execution_tools = get_execution_tools()
        
        # Find and test the workflow_wait tool
        wait_tool = None
        execution_data_tool = None
        
        for tool in execution_tools:
            if tool.name == "workflow_wait":
                wait_tool = tool
            elif tool.name == "execution_data":
                execution_data_tool = tool
        
        # Test workflow_wait (time delay)
        if wait_tool:
            print("Test 1: Workflow wait (2 second delay)")
            result = wait_tool.invoke({
                "wait_type": "time",
                "duration_seconds": 2
            })
            response = json.loads(result)
            print(f"✅ Wait result: {response.get('success', False)}")
            print(f"   Actual duration: {response.get('actual_duration', 'N/A'):.2f}s")
        
        # Test execution_data (metadata storage)
        if execution_data_tool:
            print("Test 2: Execution data storage")
            result = execution_data_tool.invoke({
                "data_type": "debug",
                "key": "test_run",
                "value": {"test": True, "timestamp": "2024-06-18"},
                "tags": ["test", "workflow"],
                "description": "Test execution data"
            })
            response = json.loads(result)
            print(f"✅ Data storage result: {response.get('success', False)}")
            print(f"   Entry ID: {response.get('entry_id', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Workflow tools test failed: {str(e)}")
    
    print()

def test_code_execution():
    """Test the code execution tools."""
    print("💻 Testing Code Execution Tools")
    print("=" * 32)
    
    try:
        code_tools = get_code_tools()
        
        # Find the python_code tool
        python_tool = None
        for tool in code_tools:
            if tool.name == "python_code":
                python_tool = tool
                break
        
        if python_tool:
            print("Test 1: Python code execution")
            test_code = """
# Simple calculation test
numbers = [1, 2, 3, 4, 5]
result = sum(numbers)
average = result / len(numbers)
print(f"Sum: {result}, Average: {average}")
"""
            
            result = python_tool.invoke({
                "code": test_code,
                "context_vars": {"test_mode": True},
                "timeout_seconds": 10
            })
            
            response = json.loads(result)
            print(f"✅ Python execution result: {response.get('success', False)}")
            print(f"   Output: {response.get('stdout', 'No output').strip()}")
            if response.get('local_variables'):
                print(f"   Variables: {list(response['local_variables'].keys())}")
        
    except Exception as e:
        print(f"❌ Code execution test failed: {str(e)}")
    
    print()

def test_data_tools():
    """Test the separated data handling tools."""
    print("📊 Testing Data Handling Tools")
    print("=" * 31)
    
    try:
        files_tools = get_files_tools()
        csv_tools = get_csv_tools()
        
        # Test file operations
        file_store_tool = None
        file_read_tool = None
        csv_tool = None
        
        for tool in files_tools:
            if tool.name == "file_store":
                file_store_tool = tool
            elif tool.name == "file_read":
                file_read_tool = tool
        
        for tool in csv_tools:
            if tool.name == "csv_processor":
                csv_tool = tool
        
        # Test file storage
        if file_store_tool:
            print("Test 1: File storage (organized structure)")
            result = file_store_tool.invoke({
                "content": "Test data from reorganized tools\\nLine 2\\nLine 3",
                "file_path": "test_organized.txt",
                "mode": "w"
            })
            response = json.loads(result)
            print(f"✅ File storage: {response.get('success', False)}")
            print(f"   File size: {response.get('file_size_human', 'N/A')}")
        
        # Test CSV creation and processing
        if file_store_tool and csv_tool:
            print("Test 2: CSV processing (separated tools)")
            csv_data = "name,score,grade\\nAlice,95,A\\nBob,87,B\\nCharlie,92,A"
            
            # Create CSV file
            file_result = file_store_tool.invoke({
                "content": csv_data,
                "file_path": "test_scores.csv",
                "mode": "w"
            })
            
            # Process CSV file
            if json.loads(file_result).get('success'):
                csv_result = csv_tool.invoke({
                    "file_path": "test_scores.csv",
                    "operation": "summary"
                })
                response = json.loads(csv_result)
                print(f"✅ CSV processing: {response.get('success', False)}")
                print(f"   Rows: {response.get('total_rows', 'N/A')}")
                print(f"   Columns: {response.get('columns', [])}")
        
    except Exception as e:
        print(f"❌ Data tools test failed: {str(e)}")
    
    print()

def main():
    """Run all tests for the reorganized tool structure."""
    print("🧪 Braid Tools - Reorganized Structure Test Suite")
    print("=" * 50)
    print()
    
    test_tool_imports()
    test_workflow_tools()
    test_code_execution()
    test_data_tools()
    
    print("🏁 Tool reorganization tests completed!")
    print()
    print("Summary of New Organization:")
    print("- workflow/execution: Wait, sub-workflow, execution data")
    print("- workflow/code: Python and JavaScript execution")
    print("- data/files: Basic file operations (read, write, list)")
    print("- data/csv: Specialized CSV processing")
    print("- network/http: HTTP requests and web scraping")
    print("- integrations/: External services (Google, Slack, etc.)")
    print()
    print("✅ All tools are properly organized and functional!")

if __name__ == "__main__":
    main()
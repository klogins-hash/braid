"""
Workflow Execution Tools - Control flow and orchestration for complex workflows.

Tools:
- workflow_wait: Pause execution for time delays or external events
- execution_data: Store execution metadata and debugging information
- sub_workflow: Execute sub-workflows for modular agent architectures

For webhook tools, see network/webhooks/tools.py
For code execution, see workflow/code/tools.py
"""
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Input Schemas ---

class WorkflowWaitInput(BaseModel):
    wait_type: str = Field(description="Type of wait: 'time' (time delay) or 'file' (wait for file to exist)")
    duration_seconds: Optional[int] = Field(default=None, description="Seconds to wait (for time wait)")
    file_path: Optional[str] = Field(default=None, description="File path to wait for (for file wait)")
    timeout_seconds: int = Field(default=300, description="Maximum time to wait before timeout")
    check_interval: int = Field(default=5, description="Seconds between checks (for file wait)")

class ExecutionDataInput(BaseModel):
    data_type: str = Field(description="Type of data: 'metadata', 'debug', 'metric', 'checkpoint'")
    key: str = Field(description="Unique key for this data entry")
    value: Any = Field(description="Data value to store (can be any JSON-serializable type)")
    tags: Optional[list] = Field(default=None, description="Optional tags for filtering/searching")
    description: Optional[str] = Field(default=None, description="Human-readable description")

class SubWorkflowInput(BaseModel):
    workflow_type: str = Field(description="Type of sub-workflow: 'file' (Python file) or 'function' (imported function)")
    workflow_path: str = Field(description="Path to workflow file or function name")
    input_data: Dict[str, Any] = Field(description="Input data to pass to the sub-workflow")
    timeout_seconds: int = Field(default=600, description="Maximum execution time before timeout")

# --- Global execution data store ---
_execution_store = {}

# --- Workflow Execution Tools ---

@tool("workflow_wait", args_schema=WorkflowWaitInput)
def workflow_wait(wait_type: str, duration_seconds: Optional[int] = None, 
                 file_path: Optional[str] = None, timeout_seconds: int = 300,
                 check_interval: int = 5) -> str:
    """
    Pause workflow execution until a time delay passes or an external event occurs.
    
    Wait types:
    - 'time': Wait for a specific number of seconds
    - 'file': Wait for a file to exist (useful for coordination with external processes)
    
    Features:
    - Configurable timeout to prevent infinite waits
    - Regular status reporting during long waits
    - File existence monitoring with configurable check intervals
    
    Returns JSON with wait status and timing information.
    """
    start_time = datetime.now()
    
    try:
        if wait_type == "time":
            if duration_seconds is None:
                return json.dumps({
                    "success": False,
                    "error": "duration_seconds is required for time wait",
                    "wait_type": wait_type
                }, indent=2)
            
            if duration_seconds > timeout_seconds:
                return json.dumps({
                    "success": False,
                    "error": f"Duration ({duration_seconds}s) exceeds timeout ({timeout_seconds}s)",
                    "wait_type": wait_type
                }, indent=2)
            
            # Simple time wait
            time.sleep(duration_seconds)
            
            end_time = datetime.now()
            actual_duration = (end_time - start_time).total_seconds()
            
            return json.dumps({
                "success": True,
                "wait_type": wait_type,
                "requested_duration": duration_seconds,
                "actual_duration": actual_duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }, indent=2)
            
        elif wait_type == "file":
            if file_path is None:
                return json.dumps({
                    "success": False,
                    "error": "file_path is required for file wait",
                    "wait_type": wait_type
                }, indent=2)
            
            file_path_obj = Path(file_path)
            elapsed = 0
            checks = 0
            
            while elapsed < timeout_seconds:
                if file_path_obj.exists():
                    end_time = datetime.now()
                    actual_duration = (end_time - start_time).total_seconds()
                    
                    return json.dumps({
                        "success": True,
                        "wait_type": wait_type,
                        "file_path": str(file_path_obj),
                        "file_found": True,
                        "checks_performed": checks,
                        "actual_duration": actual_duration,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat()
                    }, indent=2)
                
                time.sleep(check_interval)
                elapsed += check_interval
                checks += 1
            
            # Timeout reached
            end_time = datetime.now()
            actual_duration = (end_time - start_time).total_seconds()
            
            return json.dumps({
                "success": False,
                "wait_type": wait_type,
                "file_path": str(file_path_obj),
                "file_found": False,
                "timeout_reached": True,
                "checks_performed": checks,
                "actual_duration": actual_duration,
                "error": f"File not found within {timeout_seconds}s timeout"
            }, indent=2)
            
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown wait_type: {wait_type}. Available: 'time', 'file'",
                "wait_type": wait_type
            }, indent=2)
            
    except Exception as e:
        end_time = datetime.now()
        actual_duration = (end_time - start_time).total_seconds()
        
        return json.dumps({
            "success": False,
            "error": f"Wait operation failed: {str(e)}",
            "wait_type": wait_type,
            "actual_duration": actual_duration
        }, indent=2)

@tool("execution_data", args_schema=ExecutionDataInput)
def execution_data(data_type: str, key: str, value: Any, tags: Optional[list] = None,
                  description: Optional[str] = None) -> str:
    """
    Store execution metadata and debugging information for workflow analysis.
    
    Data types:
    - 'metadata': General workflow metadata
    - 'debug': Debugging information and traces
    - 'metric': Performance metrics and measurements  
    - 'checkpoint': Workflow state checkpoints
    
    Features:
    - Persistent storage during workflow execution
    - Tagging system for organization and filtering
    - Timestamped entries for chronological analysis
    - JSON serialization for complex data structures
    
    Returns JSON with storage confirmation and entry details.
    """
    try:
        timestamp = datetime.now().isoformat()
        
        # Create the data entry
        entry = {
            "data_type": data_type,
            "key": key,
            "value": value,
            "tags": tags or [],
            "description": description,
            "timestamp": timestamp,
            "entry_id": f"{data_type}_{key}_{int(time.time())}"
        }
        
        # Store in global execution store
        if data_type not in _execution_store:
            _execution_store[data_type] = {}
        
        _execution_store[data_type][key] = entry
        
        result = {
            "success": True,
            "data_type": data_type,
            "key": key,
            "entry_id": entry["entry_id"],
            "timestamp": timestamp,
            "tags": tags or [],
            "description": description,
            "storage_location": f"_execution_store['{data_type}']['{key}']",
            "total_entries": len(_execution_store.get(data_type, {}))
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to store execution data: {str(e)}",
            "data_type": data_type,
            "key": key
        }, indent=2)

@tool("sub_workflow", args_schema=SubWorkflowInput)
def sub_workflow(workflow_type: str, workflow_path: str, input_data: Dict[str, Any],
                timeout_seconds: int = 600) -> str:
    """
    Execute sub-workflows for modular agent architectures and code reuse.
    
    Workflow types:
    - 'file': Execute a Python file as a subprocess
    - 'function': Import and call a Python function
    
    Features:
    - Isolated execution environment
    - Input/output data marshaling
    - Timeout protection for long-running workflows
    - Error handling and status reporting
    
    Returns JSON with execution results and status information.
    """
    start_time = datetime.now()
    
    try:
        if workflow_type == "file":
            import subprocess
            import tempfile
            
            # Create a temporary file with input data
            input_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(input_data, input_file, default=str)
            input_file.close()
            
            try:
                # Execute the workflow file with input data
                result = subprocess.run([
                    'python', workflow_path, input_file.name
                ], capture_output=True, text=True, timeout=timeout_seconds)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Clean up temp file
                Path(input_file.name).unlink()
                
                if result.returncode == 0:
                    # Try to parse output as JSON
                    try:
                        output_data = json.loads(result.stdout)
                    except json.JSONDecodeError:
                        output_data = result.stdout
                    
                    return json.dumps({
                        "success": True,
                        "workflow_type": workflow_type,
                        "workflow_path": workflow_path,
                        "return_code": result.returncode,
                        "output_data": output_data,
                        "stderr": result.stderr,
                        "duration_seconds": duration,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat()
                    }, indent=2, default=str)
                else:
                    return json.dumps({
                        "success": False,
                        "workflow_type": workflow_type,
                        "workflow_path": workflow_path,
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "duration_seconds": duration,
                        "error": f"Sub-workflow exited with code {result.returncode}"
                    }, indent=2)
                    
            except subprocess.TimeoutExpired:
                # Clean up temp file
                Path(input_file.name).unlink()
                
                return json.dumps({
                    "success": False,
                    "workflow_type": workflow_type,
                    "workflow_path": workflow_path,
                    "error": f"Sub-workflow timed out after {timeout_seconds} seconds",
                    "timeout_seconds": timeout_seconds
                }, indent=2)
                
        elif workflow_type == "function":
            import importlib.util
            import sys
            
            # Parse module and function name
            if '.' in workflow_path:
                module_name, function_name = workflow_path.rsplit('.', 1)
            else:
                return json.dumps({
                    "success": False,
                    "error": "Function path must be in format 'module.function'",
                    "workflow_path": workflow_path
                }, indent=2)
            
            try:
                # Import the module
                module = importlib.import_module(module_name)
                
                # Get the function
                if not hasattr(module, function_name):
                    return json.dumps({
                        "success": False,
                        "error": f"Function '{function_name}' not found in module '{module_name}'",
                        "workflow_path": workflow_path
                    }, indent=2)
                
                func = getattr(module, function_name)
                
                # Execute the function
                output_data = func(input_data)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return json.dumps({
                    "success": True,
                    "workflow_type": workflow_type,
                    "workflow_path": workflow_path,
                    "output_data": output_data,
                    "duration_seconds": duration,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }, indent=2, default=str)
                
            except Exception as func_error:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return json.dumps({
                    "success": False,
                    "workflow_type": workflow_type,
                    "workflow_path": workflow_path,
                    "error": f"Function execution failed: {str(func_error)}",
                    "duration_seconds": duration
                }, indent=2)
                
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown workflow_type: {workflow_type}. Available: 'file', 'function'",
                "workflow_type": workflow_type
            }, indent=2)
            
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return json.dumps({
            "success": False,
            "error": f"Sub-workflow execution failed: {str(e)}",
            "workflow_type": workflow_type,
            "workflow_path": workflow_path,
            "duration_seconds": duration
        }, indent=2)

# --- Tool Aggregator ---

def get_execution_tools():
    """Returns a list of all workflow execution tools."""
    return [workflow_wait, execution_data, sub_workflow]
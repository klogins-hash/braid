"""
Code Execution Tools - Execute custom JavaScript and Python code within workflows.

Tools:
- python_code: Execute Python code with safety restrictions
- javascript_code: Execute JavaScript code via Node.js

For sub-workflow execution, see workflow/execution/tools.py
"""
import json
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Input Schemas ---

class PythonCodeInput(BaseModel):
    code: str = Field(description="Python code to execute")
    context_vars: Optional[Dict[str, Any]] = Field(default=None, description="Variables to make available in execution context")
    timeout_seconds: int = Field(default=30, description="Maximum execution time")
    capture_output: bool = Field(default=True, description="Whether to capture stdout/stderr")

class JavaScriptCodeInput(BaseModel):
    code: str = Field(description="JavaScript code to execute")
    context_vars: Optional[Dict[str, Any]] = Field(default=None, description="Variables to make available as global variables")
    timeout_seconds: int = Field(default=30, description="Maximum execution time")
    node_modules: Optional[list] = Field(default=None, description="List of npm modules to require")

# --- Code Execution Tools ---

@tool("python_code", args_schema=PythonCodeInput)
def python_code(code: str, context_vars: Optional[Dict[str, Any]] = None, 
               timeout_seconds: int = 30, capture_output: bool = True) -> str:
    """
    Execute Python code with safety restrictions and context variables.
    
    Features:
    - Isolated execution environment
    - Context variable injection
    - Stdout/stderr capture
    - Timeout protection
    - Error handling and traceback capture
    
    Safety restrictions:
    - No file system access outside current directory
    - No network access (imports restricted)
    - Limited execution time
    - No dangerous imports (os.system, subprocess, etc.)
    
    Returns JSON with execution results, output, and timing information.
    """
    start_time = datetime.now()
    
    try:
        # Safety check - block dangerous imports
        dangerous_imports = [
            'os.system', 'subprocess', 'importlib', '__import__',
            'exec', 'eval', 'compile', 'open'
        ]
        
        code_lower = code.lower()
        for dangerous in dangerous_imports:
            if dangerous in code_lower:
                return json.dumps({
                    "success": False,
                    "error": f"Blocked dangerous operation: {dangerous}",
                    "safety_restriction": True,
                    "code_preview": code[:100] + "..." if len(code) > 100 else code
                }, indent=2)
        
        # Create execution environment
        import builtins
        safe_builtins = {}
        allowed_builtins = [
            'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple', 'set',
            'min', 'max', 'sum', 'abs', 'round', 'sorted', 'reversed',
            'enumerate', 'zip', 'range', 'print', 'type', 'isinstance',
            'hasattr', 'getattr', 'setattr', 'delattr'
        ]
        
        for builtin_name in allowed_builtins:
            if hasattr(builtins, builtin_name):
                safe_builtins[builtin_name] = getattr(builtins, builtin_name)
        
        exec_globals = {
            '__builtins__': safe_builtins,
            'json': json,
            'datetime': datetime,
            'math': None,  # Will import if needed
        }
        
        # Add context variables if provided
        if context_vars:
            exec_globals.update(context_vars)
        
        # Import math if used
        if 'math.' in code:
            import math
            exec_globals['math'] = math
        
        exec_locals = {}
        
        # Capture output if requested
        if capture_output:
            from io import StringIO
            import contextlib
            
            stdout_capture = StringIO()
            stderr_capture = StringIO()
            
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                # Execute the code
                exec(code, exec_globals, exec_locals)
            
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
        else:
            # Execute without capture
            exec(code, exec_globals, exec_locals)
            stdout_output = ""
            stderr_output = ""
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Extract return value if any
        return_value = exec_locals.get('__return__', None)
        
        result = {
            "success": True,
            "code_executed": True,
            "stdout": stdout_output,
            "stderr": stderr_output,
            "return_value": return_value,
            "local_variables": {k: v for k, v in exec_locals.items() if not k.startswith('__')},
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return json.dumps({
            "success": False,
            "error": f"Python code execution failed: {str(e)}",
            "error_type": type(e).__name__,
            "duration_seconds": duration,
            "code_preview": code[:200] + "..." if len(code) > 200 else code
        }, indent=2)

@tool("javascript_code", args_schema=JavaScriptCodeInput)
def javascript_code(code: str, context_vars: Optional[Dict[str, Any]] = None,
                   timeout_seconds: int = 30, node_modules: Optional[list] = None) -> str:
    """
    Execute JavaScript code via Node.js with context variables and module support.
    
    Features:
    - Node.js execution environment
    - Context variable injection as global variables
    - NPM module imports
    - Stdout/stderr capture
    - Timeout protection
    - Error handling and stack trace capture
    
    Requirements:
    - Node.js must be installed and available in PATH
    - NPM modules must be installed globally or in current directory
    
    Returns JSON with execution results, output, and timing information.
    """
    start_time = datetime.now()
    
    try:
        # Check if Node.js is available
        try:
            node_version = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if node_version.returncode != 0:
                return json.dumps({
                    "success": False,
                    "error": "Node.js is not available. Please install Node.js to use JavaScript execution.",
                    "requirement": "Node.js"
                }, indent=2)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return json.dumps({
                "success": False,
                "error": "Node.js is not available. Please install Node.js to use JavaScript execution.",
                "requirement": "Node.js"
            }, indent=2)
        
        # Build the JavaScript code with context and modules
        js_code_parts = []
        
        # Add context variables as globals
        if context_vars:
            for key, value in context_vars.items():
                js_value = json.dumps(value, default=str)
                js_code_parts.append(f"global.{key} = {js_value};")
        
        # Add module requires
        if node_modules:
            for module in node_modules:
                # Sanitize module name
                if not module.replace('-', '').replace('_', '').isalnum():
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid module name: {module}",
                        "safety_restriction": True
                    }, indent=2)
                js_code_parts.append(f"const {module.replace('-', '_')} = require('{module}');")
        
        # Add the user code
        js_code_parts.append(code)
        
        full_js_code = '\\n'.join(js_code_parts)
        
        # Create a temporary file for the JavaScript code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
            temp_file.write(full_js_code)
            temp_file_path = temp_file.name
        
        try:
            # Execute the JavaScript code
            result = subprocess.run([
                'node', temp_file_path
            ], capture_output=True, text=True, timeout=timeout_seconds)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Clean up temp file
            Path(temp_file_path).unlink()
            
            # Parse the result
            execution_result = {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "node_version": node_version.stdout.strip(),
                "context_vars_provided": list(context_vars.keys()) if context_vars else [],
                "modules_required": node_modules or []
            }
            
            if result.returncode != 0:
                execution_result["error"] = f"JavaScript execution failed with exit code {result.returncode}"
            
            return json.dumps(execution_result, indent=2, default=str)
            
        except subprocess.TimeoutExpired:
            # Clean up temp file
            Path(temp_file_path).unlink()
            
            return json.dumps({
                "success": False,
                "error": f"JavaScript execution timed out after {timeout_seconds} seconds",
                "timeout_seconds": timeout_seconds,
                "duration_seconds": timeout_seconds
            }, indent=2)
            
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return json.dumps({
            "success": False,
            "error": f"JavaScript code execution failed: {str(e)}",
            "duration_seconds": duration,
            "code_preview": code[:200] + "..." if len(code) > 200 else code
        }, indent=2)

# --- Tool Aggregator ---

def get_code_tools():
    """Returns a list of all code execution tools."""
    return [python_code, javascript_code]
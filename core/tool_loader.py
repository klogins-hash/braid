"""
Dynamically discovers and loads tools registered via entry points.
"""
import sys
import pkgutil
from importlib import metadata
from typing import List, Dict, Callable

# A cache to store loaded tool instances
_tool_cache: Dict[str, object] = {}

from core.tool_registry import LlamaIndexTool

def load_tools() -> Dict[str, LlamaIndexTool]:
    """
    Discovers all available tools from the 'braid.tools' entry point.
    It returns a dictionary of tool names to their respective LlamaIndexTool objects.
    This function supports both newer (importlib.metadata) and older (pkg_resources)
    packaging libraries.
    """
    tools = {}
    try:
        # Newer approach using importlib.metadata (Python 3.8+)
        entry_points = metadata.entry_points()
        if "braid.tools" in entry_points:
            tool_entry_points = entry_points["braid.tools"]
            for entry_point in tool_entry_points:
                tool_name = entry_point.name
                tool_func = entry_point.load()
                tools[tool_name] = tool_func
    except (ImportError, Exception):
        # Fallback for older Python versions or other issues
        try:
            import pkg_resources
            tool_entry_points = pkg_resources.iter_entry_points(group="braid.tools")
            for entry_point in tool_entry_points:
                tool_name = entry_point.name
                tool_func = entry_point.load()
                tools[tool_name] = tool_func
        except Exception as e:
            # This makes the tool discoverable but will raise an error if used
            # without the proper extras installed.
            def missing_dependency_func(original_error=e, extra_name=tool_name.split('.')[2]):
                raise ImportError(
                    f"Tool '{tool_name}' is available but its dependencies are not installed. "
                    f"Please install them with: pip install '.[{extra_name}]'\n"
                    f"Original error: {original_error}"
                )
            tools[tool_name] = missing_dependency_func
            
    return tools

def get_tools(names: List[str]) -> List[Callable]:
    """
    Loads and returns a list of specific tools by their registered names.
    """
    all_tools = load_tools()
    
    selected_tools: List[Callable] = []
    missing_tools: List[str] = []

    for name in names:
        if name in all_tools:
            # Check if it's a "missing dependency" placeholder function
            tool_func = all_tools[name]
            if (hasattr(tool_func, "__kwdefaults__") 
                and tool_func.__kwdefaults__ is not None 
                and "original_error" in tool_func.__kwdefaults__):
                 # This will raise the helpful ImportError
                tool_func()
            selected_tools.append(tool_func)
        else:
            missing_tools.append(name)
            
    if missing_tools:
        raise ValueError(f"Tools not found: {', '.join(missing_tools)}. "
                         f"Available tools are: {list(all_tools.keys())}")
                         
    return selected_tools

def get_tool(name: str) -> Callable:
    """
    Loads and returns a single tool by its registered name.
    """
    all_tools = load_tools()
    if name not in all_tools:
        raise ValueError(f"Tool not found: '{name}'. "
                         f"Available tools are: {list(all_tools.keys())}")
    
    tool_func = all_tools[name]
    # Raise the ImportError if dependencies are missing
    if (hasattr(tool_func, "__kwdefaults__") 
        and tool_func.__kwdefaults__ is not None 
        and "original_error" in tool_func.__kwdefaults__):
        tool_func()

    return tool_func 
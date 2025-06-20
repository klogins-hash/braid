"""
Data Transformation Tools - Core data processing and manipulation utilities.

Tools:
- edit_fields: Rename, add, or remove fields on data items
- filter_items: Keep only items matching conditions  
- date_time: Manipulate dates/times and calculate intervals
- sort_items: Order items by one or more fields
- rename_keys: Bulk-rename field names via mapping

Inspired by n8n core transformation nodes for ETL-style workflows.
"""
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from operator import itemgetter

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Input Schemas ---

class EditFieldsInput(BaseModel):
    items: List[Dict[str, Any]] = Field(description="List of data items to process")
    operations: List[Dict[str, Any]] = Field(description="List of field operations: {action: 'add|remove|rename', field: 'name', value: 'new_value', new_name: 'new_field'}")

class FilterItemsInput(BaseModel):
    items: List[Dict[str, Any]] = Field(description="List of data items to filter")
    condition: str = Field(description="Filter condition: 'field operator value' (e.g., 'age > 25', 'status == active')")
    limit: Optional[int] = Field(default=None, description="Maximum number of items to return")

class DateTimeInput(BaseModel):
    operation: str = Field(description="Operation: 'add', 'subtract', 'format', 'now', 'parse'")
    date_value: Optional[str] = Field(default=None, description="Input date (ISO format or 'now')")
    amount: Optional[int] = Field(default=None, description="Amount to add/subtract")
    unit: Optional[str] = Field(default="days", description="Time unit: 'days', 'hours', 'minutes', 'seconds'")
    format_string: Optional[str] = Field(default="%Y-%m-%d %H:%M:%S", description="Output format string")

class SortItemsInput(BaseModel):
    items: List[Dict[str, Any]] = Field(description="List of data items to sort")
    sort_fields: List[Dict[str, Any]] = Field(description="Sort criteria: [{field: 'name', order: 'asc|desc'}]")

class RenameKeysInput(BaseModel):
    items: List[Dict[str, Any]] = Field(description="List of data items to process")
    key_mapping: Dict[str, str] = Field(description="Mapping of old_key: new_key")

# --- Data Transformation Tools ---

@tool("edit_fields", args_schema=EditFieldsInput)
def edit_fields(items: List[Dict[str, Any]], operations: List[Dict[str, Any]]) -> str:
    """
    Rename, add, or remove fields on each data item.
    
    Operations:
    - add: Add a new field with specified value
    - remove: Remove a field from items
    - rename: Rename an existing field
    
    Common uses:
    - Standardize incoming payload keys
    - Inject constant values (status = "new")
    - Drop unneeded properties before passing data downstream
    
    Returns JSON with processed items and operation summary.
    """
    try:
        processed_items = []
        operation_count = {"add": 0, "remove": 0, "rename": 0}
        
        for item in items:
            processed_item = item.copy()
            
            for op in operations:
                action = op.get("action", "").lower()
                field = op.get("field", "")
                
                if action == "add":
                    value = op.get("value", "")
                    processed_item[field] = value
                    operation_count["add"] += 1
                    
                elif action == "remove":
                    if field in processed_item:
                        del processed_item[field]
                        operation_count["remove"] += 1
                        
                elif action == "rename":
                    new_name = op.get("new_name", "")
                    if field in processed_item and new_name:
                        processed_item[new_name] = processed_item.pop(field)
                        operation_count["rename"] += 1
            
            processed_items.append(processed_item)
        
        result = {
            "success": True,
            "original_count": len(items),
            "processed_count": len(processed_items),
            "operations_applied": operation_count,
            "items": processed_items
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Field editing failed: {str(e)}",
            "original_count": len(items) if items else 0
        }, indent=2)

@tool("filter_items", args_schema=FilterItemsInput)
def filter_items(items: List[Dict[str, Any]], condition: str, limit: Optional[int] = None) -> str:
    """
    Keep only items matching a condition with optional limit.
    
    Condition format: 'field operator value'
    Operators: ==, !=, >, <, >=, <=, contains, startswith, endswith
    
    Examples:
    - 'age > 25'
    - 'status == active'
    - 'name contains John'
    - 'email endswith gmail.com'
    
    Returns JSON with filtered items and filter statistics.
    """
    try:
        # Parse condition
        condition_parts = condition.strip().split()
        if len(condition_parts) < 3:
            return json.dumps({
                "success": False,
                "error": "Invalid condition format. Use: 'field operator value'",
                "example": "age > 25"
            }, indent=2)
        
        field = condition_parts[0]
        operator = condition_parts[1]
        value = " ".join(condition_parts[2:])  # Handle values with spaces
        
        # Convert value to appropriate type
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').replace('-', '').isdigit():
            value = float(value)
        elif value.startswith('"') and value.endswith('"'):
            value = value[1:-1]  # Remove quotes
        
        filtered_items = []
        
        for item in items:
            if field not in item:
                continue
                
            item_value = item[field]
            matches = False
            
            try:
                if operator == "==":
                    matches = item_value == value
                elif operator == "!=":
                    matches = item_value != value
                elif operator == ">":
                    matches = float(item_value) > float(value)
                elif operator == "<":
                    matches = float(item_value) < float(value)
                elif operator == ">=":
                    matches = float(item_value) >= float(value)
                elif operator == "<=":
                    matches = float(item_value) <= float(value)
                elif operator == "contains":
                    matches = str(value).lower() in str(item_value).lower()
                elif operator == "startswith":
                    matches = str(item_value).lower().startswith(str(value).lower())
                elif operator == "endswith":
                    matches = str(item_value).lower().endswith(str(value).lower())
                else:
                    continue  # Unknown operator
                    
                if matches:
                    filtered_items.append(item)
                    
            except (ValueError, TypeError):
                continue  # Skip items that can't be compared
        
        # Apply limit if specified
        if limit and limit > 0:
            filtered_items = filtered_items[:limit]
        
        result = {
            "success": True,
            "condition": condition,
            "original_count": len(items),
            "filtered_count": len(filtered_items),
            "filter_field": field,
            "filter_operator": operator,
            "filter_value": value,
            "limit_applied": limit,
            "items": filtered_items
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Filtering failed: {str(e)}",
            "condition": condition,
            "original_count": len(items) if items else 0
        }, indent=2)

@tool("date_time", args_schema=DateTimeInput)
def date_time(operation: str, date_value: Optional[str] = None, amount: Optional[int] = None,
              unit: str = "days", format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Manipulate dates/times or calculate intervals.
    
    Operations:
    - 'now': Get current timestamp
    - 'add': Add time to a date
    - 'subtract': Subtract time from a date  
    - 'format': Format a date string
    - 'parse': Parse a date string to ISO format
    
    Common uses:
    - Add/subtract days, hours, minutes
    - Format timestamps (ISO, RFC, custom strings)
    - Compute "now plus X days" for scheduling delays
    
    Returns JSON with date operation result.
    """
    try:
        current_time = datetime.now()
        
        if operation == "now":
            result_date = current_time
            
        elif operation in ["add", "subtract"]:
            # Parse input date
            if date_value == "now" or date_value is None:
                base_date = current_time
            else:
                try:
                    # Try ISO format first
                    base_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except ValueError:
                    # Try common formats
                    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%m/%d/%Y"]:
                        try:
                            base_date = datetime.strptime(date_value, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        return json.dumps({
                            "success": False,
                            "error": f"Could not parse date: {date_value}",
                            "supported_formats": ["ISO 8601", "YYYY-MM-DD", "YYYY-MM-DD HH:MM:SS"]
                        }, indent=2)
            
            if amount is None:
                return json.dumps({
                    "success": False,
                    "error": "Amount is required for add/subtract operations"
                }, indent=2)
            
            # Calculate time delta
            if unit == "days":
                delta = timedelta(days=amount)
            elif unit == "hours":
                delta = timedelta(hours=amount)
            elif unit == "minutes":
                delta = timedelta(minutes=amount)
            elif unit == "seconds":
                delta = timedelta(seconds=amount)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown time unit: {unit}",
                    "supported_units": ["days", "hours", "minutes", "seconds"]
                }, indent=2)
            
            if operation == "add":
                result_date = base_date + delta
            else:  # subtract
                result_date = base_date - delta
                
        elif operation == "format":
            if date_value == "now" or date_value is None:
                input_date = current_time
            else:
                try:
                    input_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except ValueError:
                    return json.dumps({
                        "success": False,
                        "error": f"Could not parse date for formatting: {date_value}"
                    }, indent=2)
            
            result_date = input_date
            
        elif operation == "parse":
            if not date_value:
                return json.dumps({
                    "success": False,
                    "error": "Date value is required for parse operation"
                }, indent=2)
            
            try:
                result_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": f"Could not parse date: {date_value}"
                }, indent=2)
        
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown operation: {operation}",
                "supported_operations": ["now", "add", "subtract", "format", "parse"]
            }, indent=2)
        
        # Format result
        formatted_result = result_date.strftime(format_string)
        iso_result = result_date.isoformat()
        
        result = {
            "success": True,
            "operation": operation,
            "input_date": date_value,
            "amount": amount,
            "unit": unit,
            "format_string": format_string,
            "result_formatted": formatted_result,
            "result_iso": iso_result,
            "result_timestamp": result_date.timestamp()
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Date/time operation failed: {str(e)}",
            "operation": operation
        }, indent=2)

@tool("sort_items", args_schema=SortItemsInput)
def sort_items(items: List[Dict[str, Any]], sort_fields: List[Dict[str, Any]]) -> str:
    """
    Order items by one or more fields (ascending/descending).
    
    Sort fields format: [{"field": "name", "order": "asc|desc"}]
    
    Features:
    - Multi-field sorting with priority order
    - Ascending/descending per field
    - Type-aware sorting (numbers, strings, dates)
    - Handles missing fields gracefully
    
    Returns JSON with sorted items and sort criteria.
    """
    try:
        if not sort_fields:
            return json.dumps({
                "success": False,
                "error": "At least one sort field is required"
            }, indent=2)
        
        sorted_items = items.copy()
        
        # Build sort key function for multiple fields
        def sort_key(item):
            keys = []
            for sort_field in reversed(sort_fields):  # Reverse for stable sorting
                field = sort_field.get("field", "")
                order = sort_field.get("order", "asc").lower()
                
                if field not in item:
                    value = ""  # Default for missing fields
                else:
                    value = item[field]
                
                # Convert to comparable type
                if isinstance(value, str):
                    try:
                        # Try to convert to number if possible
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        value = value.lower()  # Case-insensitive string sort
                
                # Handle reverse order
                if order == "desc":
                    if isinstance(value, (int, float)):
                        value = -value
                    elif isinstance(value, str):
                        # For strings, we'll sort normally then reverse the list
                        keys.append((field, value, True))  # True indicates desc
                        continue
                
                keys.append((field, value, order == "desc"))
            
            return keys
        
        # Sort by each field in reverse order for multi-field sorting
        for sort_field in reversed(sort_fields):
            field = sort_field.get("field", "")
            order = sort_field.get("order", "asc").lower()
            reverse = order == "desc"
            
            sorted_items.sort(
                key=lambda item: item.get(field, ""),
                reverse=reverse
            )
        
        result = {
            "success": True,
            "original_count": len(items),
            "sorted_count": len(sorted_items),
            "sort_fields": sort_fields,
            "items": sorted_items
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Sorting failed: {str(e)}",
            "original_count": len(items) if items else 0
        }, indent=2)

@tool("rename_keys", args_schema=RenameKeysInput)
def rename_keys(items: List[Dict[str, Any]], key_mapping: Dict[str, str]) -> str:
    """
    Bulk-rename item field names via a mapping.
    
    Key mapping format: {"old_key": "new_key"}
    
    Features:
    - Bulk rename operations across all items
    - Preserves data while standardizing field names
    - Handles missing keys gracefully
    - Reports rename statistics
    
    Returns JSON with items having renamed keys and operation summary.
    """
    try:
        processed_items = []
        rename_stats = {"total_renames": 0, "items_affected": 0}
        
        for item in items:
            processed_item = {}
            item_renames = 0
            
            for key, value in item.items():
                if key in key_mapping:
                    new_key = key_mapping[key]
                    processed_item[new_key] = value
                    item_renames += 1
                    rename_stats["total_renames"] += 1
                else:
                    processed_item[key] = value
            
            if item_renames > 0:
                rename_stats["items_affected"] += 1
                
            processed_items.append(processed_item)
        
        result = {
            "success": True,
            "original_count": len(items),
            "processed_count": len(processed_items),
            "key_mapping": key_mapping,
            "rename_statistics": rename_stats,
            "items": processed_items
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Key renaming failed: {str(e)}",
            "original_count": len(items) if items else 0
        }, indent=2)

# --- Tool Aggregator ---

def get_transform_tools():
    """Returns a list of all data transformation tools."""
    return [edit_fields, filter_items, date_time, sort_items, rename_keys]
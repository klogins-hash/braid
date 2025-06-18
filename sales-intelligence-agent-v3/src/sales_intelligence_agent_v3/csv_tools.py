"""
CSV Processing Tools - Specialized tools for working with CSV files.

Tools:
- csv_processor: Read, analyze, filter, and process CSV files

For basic file operations, see data/files/tools.py
"""
import json
import csv
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Input Schemas ---

class CsvProcessorInput(BaseModel):
    file_path: str = Field(description="Path to the CSV file")
    operation: str = Field(description="Operation: 'read', 'info', 'sample', 'filter', 'summary'")
    filter_column: Optional[str] = Field(default=None, description="Column to filter on (for filter operation)")
    filter_value: Optional[str] = Field(default=None, description="Value to filter for (for filter operation)")
    sample_size: int = Field(default=5, description="Number of rows to sample")

# --- Helper Functions ---

def _safe_path(file_path: str) -> Path:
    """Convert to Path object and validate it's not trying to escape working directory."""
    path = Path(file_path).resolve()
    
    # Basic safety check - prevent directory traversal attacks
    cwd = Path.cwd().resolve()
    try:
        path.relative_to(cwd)
        return path
    except ValueError:
        # If path is outside current working directory, create relative path
        return cwd / Path(file_path).name

# --- CSV Processing Tools ---

@tool("csv_processor", args_schema=CsvProcessorInput)
def csv_processor(file_path: str, operation: str, filter_column: Optional[str] = None,
                 filter_value: Optional[str] = None, sample_size: int = 5) -> str:
    """
    Process CSV files with various operations.
    
    Supported operations:
    - 'read': Read and return CSV content
    - 'info': Get CSV structure information
    - 'sample': Return a sample of rows
    - 'filter': Filter rows by column value
    - 'summary': Get statistical summary
    
    Returns JSON with processed CSV data.
    """
    try:
        # Validate and safe path
        safe_file_path = _safe_path(file_path)
        
        # Check if file exists
        if not safe_file_path.exists():
            return json.dumps({
                "success": False,
                "error": f"CSV file not found: {safe_file_path}",
                "file_path": str(safe_file_path)
            }, indent=2)
        
        # Read CSV file
        with open(safe_file_path, 'r', encoding='utf-8') as f:
            # Detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)
        
        if not rows:
            return json.dumps({
                "success": False,
                "error": "CSV file is empty or has no data rows",
                "file_path": str(safe_file_path)
            }, indent=2)
        
        columns = list(rows[0].keys())
        
        result = {
            "success": True,
            "file_path": str(safe_file_path),
            "operation": operation,
            "total_rows": len(rows),
            "columns": columns,
            "column_count": len(columns)
        }
        
        if operation == "info":
            # Return structure information
            result["delimiter"] = delimiter
            result["sample_data"] = rows[:3]  # First 3 rows as sample
            
        elif operation == "sample":
            # Return sample rows
            import random
            sample_rows = random.sample(rows, min(sample_size, len(rows)))
            result["sample_size"] = len(sample_rows)
            result["data"] = sample_rows
            
        elif operation == "read":
            # Return all data (with reasonable limit)
            if len(rows) > 1000:
                result["warning"] = f"Large CSV file ({len(rows)} rows). Consider using 'sample' operation."
                result["data"] = rows[:1000]
                result["truncated"] = True
            else:
                result["data"] = rows
                result["truncated"] = False
                
        elif operation == "filter":
            # Filter by column value
            if not filter_column or filter_column not in columns:
                result["error"] = f"Filter column '{filter_column}' not found. Available: {columns}"
            elif filter_value is None:
                result["error"] = "Filter value is required for filter operation"
            else:
                filtered_rows = [row for row in rows if row.get(filter_column) == filter_value]
                result["filter_column"] = filter_column
                result["filter_value"] = filter_value
                result["filtered_rows"] = len(filtered_rows)
                result["data"] = filtered_rows
                
        elif operation == "summary":
            # Basic statistical summary
            numeric_cols = []
            for col in columns:
                # Check if column has numeric data
                numeric_values = []
                for row in rows:
                    try:
                        val = float(row[col])
                        numeric_values.append(val)
                    except (ValueError, TypeError):
                        continue
                
                if numeric_values:
                    numeric_cols.append({
                        "column": col,
                        "count": len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "avg": sum(numeric_values) / len(numeric_values)
                    })
            
            result["numeric_columns"] = numeric_cols
            result["text_columns"] = [col for col in columns if col not in [nc["column"] for nc in numeric_cols]]
            
        else:
            result["error"] = f"Unknown operation: {operation}. Available: read, info, sample, filter, summary"
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"CSV processing failed: {str(e)}",
            "file_path": file_path,
            "operation": operation
        }, indent=2)

# --- Tool Aggregator ---

def get_csv_tools():
    """Returns a list of all CSV processing tools."""
    return [csv_processor]
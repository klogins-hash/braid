"""
File system tools for data persistence, file management, and processing.
"""
import json
import os
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Input Schemas ---

class FileStoreInput(BaseModel):
    content: str = Field(description="Content to write to the file")
    file_path: str = Field(description="Path where to store the file")
    mode: str = Field(default="w", description="Write mode: 'w' (write), 'a' (append), 'x' (exclusive create)")
    encoding: str = Field(default="utf-8", description="File encoding")
    create_dirs: bool = Field(default=True, description="Whether to create parent directories if they don't exist")

class FileReadInput(BaseModel):
    file_path: str = Field(description="Path to the file to read")
    encoding: str = Field(default="utf-8", description="File encoding")
    max_size_mb: int = Field(default=10, description="Maximum file size to read in MB (safety limit)")

class FileListInput(BaseModel):
    directory_path: str = Field(description="Directory path to list files from")
    pattern: str = Field(default="*", description="File pattern to match (e.g., '*.txt', '*.json')")
    recursive: bool = Field(default=False, description="Whether to search subdirectories recursively")
    include_dirs: bool = Field(default=False, description="Whether to include directories in the results")

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

def _format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

# --- File System Tools ---

@tool("file_store", args_schema=FileStoreInput)
def file_store(content: str, file_path: str, mode: str = "w", encoding: str = "utf-8", 
               create_dirs: bool = True) -> str:
    """
    Store content to files with automatic directory creation and safety checks.
    
    Supports different modes:
    - 'w': Write (overwrite existing file)
    - 'a': Append to existing file
    - 'x': Exclusive create (fail if file exists)
    
    Features:
    - Automatic parent directory creation
    - Path safety validation
    - File size reporting
    - Error handling with detailed messages
    
    Returns JSON with operation status and file information.
    """
    try:
        # Validate and safe path
        safe_file_path = _safe_path(file_path)
        
        # Create parent directories if needed
        if create_dirs:
            safe_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists for exclusive mode
        if mode == 'x' and safe_file_path.exists():
            return json.dumps({
                "success": False,
                "error": f"File already exists: {safe_file_path}",
                "file_path": str(safe_file_path)
            }, indent=2)
        
        # Write the file
        with open(safe_file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        # Get file info
        file_size = safe_file_path.stat().st_size
        
        result = {
            "success": True,
            "file_path": str(safe_file_path),
            "mode": mode,
            "encoding": encoding,
            "content_length": len(content),
            "file_size_bytes": file_size,
            "file_size_human": _format_file_size(file_size),
            "created_dirs": create_dirs and not safe_file_path.parent.exists()
        }
        
        return json.dumps(result, indent=2)
        
    except PermissionError:
        return json.dumps({
            "success": False,
            "error": f"Permission denied: Cannot write to {file_path}",
            "file_path": file_path
        }, indent=2)
    
    except FileNotFoundError:
        return json.dumps({
            "success": False,
            "error": f"Directory does not exist: {Path(file_path).parent}",
            "file_path": file_path
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"File write failed: {str(e)}",
            "file_path": file_path
        }, indent=2)

@tool("file_read", args_schema=FileReadInput)
def file_read(file_path: str, encoding: str = "utf-8", max_size_mb: int = 10) -> str:
    """
    Read content from files with safety limits and error handling.
    
    Features:
    - File size safety limits (default 10MB)
    - Automatic encoding detection fallback
    - Detailed file metadata
    - Binary file detection
    
    Returns JSON with file content and metadata.
    """
    try:
        # Validate and safe path
        safe_file_path = _safe_path(file_path)
        
        # Check if file exists
        if not safe_file_path.exists():
            return json.dumps({
                "success": False,
                "error": f"File not found: {safe_file_path}",
                "file_path": str(safe_file_path)
            }, indent=2)
        
        # Check file size
        file_size = safe_file_path.stat().st_size
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            return json.dumps({
                "success": False,
                "error": f"File too large: {_format_file_size(file_size)} > {max_size_mb}MB limit",
                "file_path": str(safe_file_path),
                "file_size_bytes": file_size,
                "file_size_human": _format_file_size(file_size)
            }, indent=2)
        
        # Try to read the file
        try:
            with open(safe_file_path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(safe_file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                encoding = 'latin-1'
            except UnicodeDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Unable to decode file - may be binary",
                    "file_path": str(safe_file_path),
                    "file_size_bytes": file_size,
                    "suggested_action": "Use binary file tools if this is not a text file"
                }, indent=2)
        
        # Get file metadata
        stat = safe_file_path.stat()
        
        result = {
            "success": True,
            "file_path": str(safe_file_path),
            "content": content,
            "encoding": encoding,
            "file_size_bytes": file_size,
            "file_size_human": _format_file_size(file_size),
            "content_length": len(content),
            "line_count": content.count('\n') + (1 if content and not content.endswith('\n') else 0),
            "modified_time": stat.st_mtime,
            "created_time": stat.st_ctime
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"File read failed: {str(e)}",
            "file_path": file_path
        }, indent=2)

@tool("file_list", args_schema=FileListInput)
def file_list(directory_path: str, pattern: str = "*", recursive: bool = False, 
              include_dirs: bool = False) -> str:
    """
    List files in directories with pattern matching and filtering.
    
    Features:
    - Glob pattern matching (*.txt, *.json, etc.)
    - Recursive directory traversal
    - File metadata (size, modification time)
    - Directory inclusion option
    
    Returns JSON with file listing and metadata.
    """
    try:
        # Validate and safe path
        safe_dir_path = _safe_path(directory_path)
        
        # Check if directory exists
        if not safe_dir_path.exists():
            return json.dumps({
                "success": False,
                "error": f"Directory not found: {safe_dir_path}",
                "directory_path": str(safe_dir_path)
            }, indent=2)
        
        if not safe_dir_path.is_dir():
            return json.dumps({
                "success": False,
                "error": f"Path is not a directory: {safe_dir_path}",
                "directory_path": str(safe_dir_path)
            }, indent=2)
        
        # List files based on pattern
        if recursive:
            paths = safe_dir_path.rglob(pattern)
        else:
            paths = safe_dir_path.glob(pattern)
        
        files = []
        dirs = []
        
        for path in paths:
            try:
                stat = path.stat()
                
                item_info = {
                    "name": path.name,
                    "path": str(path),
                    "relative_path": str(path.relative_to(safe_dir_path)),
                    "size_bytes": stat.st_size,
                    "size_human": _format_file_size(stat.st_size),
                    "modified_time": stat.st_mtime,
                    "is_file": path.is_file(),
                    "is_dir": path.is_dir()
                }
                
                if path.is_file():
                    files.append(item_info)
                elif path.is_dir() and include_dirs:
                    dirs.append(item_info)
                    
            except (OSError, PermissionError):
                # Skip files we can't access
                continue
        
        # Sort by name
        files.sort(key=lambda x: x['name'])
        dirs.sort(key=lambda x: x['name'])
        
        result = {
            "success": True,
            "directory_path": str(safe_dir_path),
            "pattern": pattern,
            "recursive": recursive,
            "include_dirs": include_dirs,
            "file_count": len(files),
            "dir_count": len(dirs),
            "files": files,
            "directories": dirs if include_dirs else []
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Directory listing failed: {str(e)}",
            "directory_path": directory_path
        }, indent=2)

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

def get_files_tools():
    """Returns a list of all file system tools."""
    return [file_store, file_read, file_list, csv_processor]
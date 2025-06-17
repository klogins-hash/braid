"""
Tools for interacting with Google Sheets.
This tool uses the "gworkspace" optional dependency.
Install it with: pip install ".[gworkspace]"
"""
try:
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError(
        "Google Sheets tools are not available. Please install the necessary dependencies with: "
        'pip install ".[gworkspace]"'
    )

import logging
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from .google_auth import get_google_service

# Set up logging
logger = logging.getLogger(__name__)

# Define the scopes required for the Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class AppendRowInput(BaseModel):
    spreadsheet_id: str = Field(description="The ID of the Google Sheet.")
    range_name: str = Field(description="The A1 notation of the range to append to, e.g., 'Sheet1!A1'.")
    values: list[list] = Field(description="A list of lists, where each inner list represents a row of values to append.")

@tool("gsheets_append_row", args_schema=AppendRowInput)
def gsheets_append_row(spreadsheet_id: str, range_name: str, values: list[list]) -> str:
    """
    Appends one or more rows to a Google Sheet.
    """
    try:
        logger.info(
            f"Attempting to append to sheet. ID: '{spreadsheet_id}', Range: '{range_name}'"
        )
        service = get_google_service("sheets", "v4", SCOPES)
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        return f"Successfully appended {result.get('updates').get('updatedRows')} row(s)."
    except HttpError as error:
        error_details = f"HTTP {error.resp.status} - {error.reason}"
        if error.content:
            error_details += f" | Details: {error.content.decode('utf-8')}"
        logger.error(f"Google Sheets API error: {error_details}")

        # Provide more specific, actionable feedback to the user/LLM
        if "Requested entity was not found" in error_details:
            return f"⚠️ Error: The Google Sheet with ID '{spreadsheet_id}' was not found. Please verify the ID."
        if "Unable to parse range" in error_details:
            return f"⚠️ Error: The sheet name (range) '{range_name}' is invalid. Please check the exact sheet name inside your spreadsheet."
        
        return f"An error occurred with Google Sheets API: {error_details}"
    except Exception as e:
        logger.error(f"Unexpected error in gsheets_append_row: {e}", exc_info=True)
        return f"An unexpected error occurred in gsheets_append_row: {e}"

def get_gsheets_tools():
    """Returns a list of all tools in this module."""
    return [gsheets_append_row] 
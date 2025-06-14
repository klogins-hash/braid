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

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from .google_auth import get_google_service

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
        return f"An error occurred with Google Sheets API: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def get_gsheets_tools():
    """Returns a list of all tools in this module."""
    return [gsheets_append_row] 
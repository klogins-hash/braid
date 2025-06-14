"""
Tools for interacting with Slack.
This tool uses the "slack" optional dependency.
Install it with: pip install ".[slack]"

To use these tools, you must create a Slack App and get a Bot User OAuth Token.
Set this token in your environment as `SLACK_BOT_TOKEN`.
"""
import os
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    raise ImportError(
        "Slack tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install ".[slack]"'
    )

class SlackPostMessageInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel to post the message to (e.g., 'C024BE91L').")
    text: str = Field(description="The text of the message to post.")

@tool("slack_post_message", args_schema=SlackPostMessageInput)
def slack_post_message(channel_id: str, text: str) -> str:
    """
    Sends a message to a Slack channel.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.chat_postMessage(channel=channel_id, text=text)
        return "Message posted successfully to Slack."
    except SlackApiError as e:
        return f"Error posting message to Slack: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

class SlackUploadFileInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel to upload the file to (e.g., 'C024BE91L').")
    file_path: str = Field(description="The local path to the file to upload.")
    initial_comment: str = Field(default="", description="An optional comment to post along with the file.")

@tool("slack_upload_file", args_schema=SlackUploadFileInput)
def slack_upload_file(channel_id: str, file_path: str, initial_comment: str = "") -> str:
    """
    Uploads a file to a Slack channel.
    """
    if not os.path.exists(file_path):
        return f"Error: The file at path '{file_path}' does not exist."
    
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.files_upload_v2(
            channel=channel_id,
            file=file_path,
            initial_comment=initial_comment
        )
        return "File uploaded successfully to Slack."
    except SlackApiError as e:
        return f"Error uploading file to Slack: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def get_slack_tools():
    """Returns a list of all tools in this module."""
    return [slack_post_message, slack_upload_file] 
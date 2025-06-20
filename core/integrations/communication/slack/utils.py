"""
Slack Utility Functions

These are non-tool helper functions that an agent's own Python code can import
and use directly. They are NOT exposed to the LLM as tools.
"""
import os
from typing import Optional

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    raise ImportError(
        "Slack tools are not available. "
        "Please install the necessary dependencies with: "
        'pip install ".[slack]"'
    )

def post_message(channel: str, message: str, thread_ts: Optional[str] = None) -> Optional[str]:
    """
    A non-tool helper function to post a message to Slack.
    Returns the message timestamp (ts) if successful, which can be used as a thread_ts.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.chat_postMessage(
            channel=channel,
            text=message,
            thread_ts=thread_ts
        )
        return response.get("ts")
    except SlackApiError as e:
        print(f"Error posting message to Slack: {e.response['error']}")
        return None
    except KeyError:
        print("SLACK_BOT_TOKEN environment variable not set.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_latest_message_from_thread(channel: str, thread_ts: str) -> Optional[str]:
    """
    A non-tool helper function to get the text of the last message in a thread.
    This is used by human-in-the-loop approval nodes.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.conversations_replies(channel=channel, ts=thread_ts, limit=50)
        
        messages = response.get("messages", [])
        if len(messages) > 1:  # More than just the parent message
            return messages[-1].get("text")
            
        return None # No replies yet
        
    except SlackApiError as e:
        print(f"Error getting latest thread message from Slack: {e.response['error']}")
        return None
    except KeyError:
        print("SLACK_BOT_TOKEN environment variable not set.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None 
"""
Public, LLM-callable tools for interacting with Slack.
"""
import os
import json
from typing import Optional, List

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

# --- Helper Functions ---

def _find_user_id(client: WebClient, name: str) -> Optional[str]:
    """Internal helper to find a user ID from a real or display name."""
    name_lower = name.lower()
    try:
        for page in client.users_list(limit=200):
            for user in page["members"]:
                profile = user.get("profile", {})
                if (profile.get("real_name", "").lower() == name_lower or
                    profile.get("display_name", "").lower() == name_lower):
                    return user["id"]
    except SlackApiError:
        return None
    return None

# --- Input Schemas ---

class SlackPostMessageInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel to post the message to (e.g., 'C024BE91L').")
    text: str = Field(description="The text of the message to post.")

class SlackUploadFileInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel to upload the file to (e.g., 'C024BE91L').")
    file_path: str = Field(description="The local path to the file to upload.")
    initial_comment: str = Field(default="", description="An optional comment to post along with the file.")

class SlackGetMessagesInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel to get messages from (e.g., 'C024BE91L').")
    limit: int = Field(default=10, description="Number of messages to retrieve (default: 10, max: 100).")

class SlackPostThreadReplyInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel containing the thread.")
    thread_ts: str = Field(description="The timestamp of the parent message to reply to.")
    text: str = Field(description="The text of the reply message.")

class SlackGetThreadRepliesInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel containing the thread.")
    thread_ts: str = Field(description="The timestamp of the parent message.")

class SlackGetMentionsInput(BaseModel):
    limit: int = Field(default=10, description="Number of mentions to retrieve (default: 10, max: 100).")

class SlackFindUserInput(BaseModel):
    name: str = Field(description="The real name or display name of the user to find.")

class SlackGetUserProfileInput(BaseModel):
    user_id: str = Field(description="The ID of the user to get profile information for (e.g., 'U024BE91L').")

class SlackGetChannelInfoInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel to get information about (e.g., 'C024BE91L').")

class SlackAddReactionInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel where the message is.")
    timestamp: str = Field(description="The timestamp of the message to react to.")
    emoji_name: str = Field(description="The name of the emoji to add (e.g., 'thumbsup', 'eyes').")

class SlackSendDirectMessageInput(BaseModel):
    user_id: str = Field(description="The ID of the user to send a direct message to (e.g., 'U024BE91L').")
    text: str = Field(description="The text of the message to send.")

class SlackUploadAndNotifyInput(BaseModel):
    channel_id: str = Field(description="The ID of the channel to upload the file to.")
    file_path: str = Field(description="The local path to the file to upload.")
    user_names: List[str] = Field(description="A list of user real names or display names to mention in the comment.")
    comment: str = Field(description="The base text of the comment to post with the file. The mentions will be prepended to this text.")


# --- Communication Tools ---

@tool("slack_post_message", args_schema=SlackPostMessageInput)
def slack_post_message(channel_id: str, text: str) -> str:
    """
    Sends a message to a Slack channel.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        client.chat_postMessage(channel=channel_id, text=text)
        return "Message posted successfully to Slack."
    except SlackApiError as e:
        return f"Error posting message to Slack: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("slack_post_thread_reply", args_schema=SlackPostThreadReplyInput)
def slack_post_thread_reply(channel_id: str, thread_ts: str, text: str) -> str:
    """
    Replies to a message thread in a Slack channel.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )
        return "Thread reply posted successfully to Slack."
    except SlackApiError as e:
        return f"Error posting thread reply to Slack: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("slack_send_direct_message", args_schema=SlackSendDirectMessageInput)
def slack_send_direct_message(user_id: str, text: str) -> str:
    """
    Sends a private direct message to a user. Requires the 'im:write' scope.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.conversations_open(users=user_id)
        dm_channel_id = response["channel"]["id"]
        client.chat_postMessage(channel=dm_channel_id, text=text)
        return "Direct message sent successfully."
    except SlackApiError as e:
        return f"Error sending direct message: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("slack_add_reaction", args_schema=SlackAddReactionInput)
def slack_add_reaction(channel_id: str, timestamp: str, emoji_name: str) -> str:
    """
    Adds an emoji reaction to a specific message. Emoji name should be without colons, e.g., 'thumbsup'.
    Requires the 'reactions:write' scope.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        client.reactions_add(
            channel=channel_id,
            name=emoji_name.replace(":", ""),
            timestamp=timestamp
        )
        return "Reaction added successfully."
    except SlackApiError as e:
        return f"Error adding reaction: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# --- File Management Tools ---

@tool("slack_upload_file", args_schema=SlackUploadFileInput)
def slack_upload_file(channel_id: str, file_path: str, initial_comment: str = "") -> str:
    """
    Uploads a file to a Slack channel. Requires the 'files:write' scope.
    """
    if not os.path.exists(file_path):
        return f"Error: The file at path '{file_path}' does not exist."
    
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        client.files_upload_v2(
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

@tool("slack_upload_and_notify", args_schema=SlackUploadAndNotifyInput)
def slack_upload_and_notify(channel_id: str, file_path: str, user_names: List[str], comment: str) -> str:
    """
    Uploads a file and notifies specific users in the comment.
    Finds users by their real names, then mentions them in the file upload comment.
    """
    if not os.path.exists(file_path):
        return f"Error: The file at path '{file_path}' does not exist."
        
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        
        mentions = []
        not_found = []
        for name in user_names:
            user_id = _find_user_id(client, name)
            if user_id:
                mentions.append(f"<@{user_id}>")
            else:
                not_found.append(name)
        
        mention_string = " ".join(mentions)
        full_comment = f"{mention_string} {comment}".strip()
        
        client.files_upload_v2(
            channel=channel_id,
            file=file_path,
            initial_comment=full_comment
        )
        
        result_message = "File uploaded successfully."
        if not_found:
            result_message += f" The following users could not be found and were not notified: {', '.join(not_found)}."
            
        return result_message
        
    except SlackApiError as e:
        return f"Error during upload and notify: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# --- Information Gathering Tools ---

@tool("slack_get_messages", args_schema=SlackGetMessagesInput)
def slack_get_messages(channel_id: str, limit: int = 10) -> str:
    """
    Retrieves recent messages from a Slack channel. Requires appropriate history scope
    (e.g., 'channels:history', 'groups:history').
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.conversations_history(channel=channel_id, limit=min(limit, 100))
        
        if not response["messages"]:
            return "No messages found in this channel."
        
        messages = []
        for msg in reversed(response["messages"]):
            user_id = msg.get("user", "Unknown")
            text = msg.get("text", "")
            
            try:
                user_info = client.users_info(user=user_id)
                username = user_info["user"]["real_name"] or user_info["user"]["name"]
            except:
                username = user_id
            
            messages.append(f"{username}: {text}")
        
        return "\n".join(messages)
        
    except SlackApiError as e:
        return f"Error getting messages from Slack: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("slack_get_thread_replies", args_schema=SlackGetThreadRepliesInput)
def slack_get_thread_replies(channel_id: str, thread_ts: str) -> str:
    """
    Gets all replies in a message thread.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.conversations_replies(channel=channel_id, ts=thread_ts)
        
        if not response["messages"]:
            return "No replies found in this thread."
        
        messages = []
        for msg in response["messages"]:
            user_id = msg.get("user", "Unknown")
            text = msg.get("text", "")
            
            try:
                user_info = client.users_info(user=user_id)
                username = user_info["user"]["real_name"] or user_info["user"]["name"]
            except:
                username = user_id
            
            messages.append(f"{username}: {text}")
        
        return "\n".join(messages)
        
    except SlackApiError as e:
        return f"Error getting thread replies from Slack: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("slack_get_mentions", args_schema=SlackGetMentionsInput)
def slack_get_mentions(limit: int = 10) -> str:
    """
    Gets recent @mentions of the bot.
    IMPORTANT: This tool requires a User OAuth Token with the 'search:read' scope,
    set as the SLACK_USER_TOKEN environment variable. It cannot use a Bot token for searching.
    """
    try:
        user_token = os.environ["SLACK_USER_TOKEN"]
        client = WebClient(token=user_token)

        bot_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        auth_response = bot_client.auth_test()
        bot_user_id = auth_response["user_id"]

        response = client.search_messages(
            query=f"<@{bot_user_id}>",
            count=min(limit, 100)
        )

        if not response["messages"]["matches"]:
            return "No recent mentions found."

        mentions = []
        for match in response["messages"]["matches"]:
            channel_name = match["channel"]["name"]
            user_id = match["user"]
            text = match["text"]
            
            try:
                user_info = client.users_info(user=user_id)
                username = user_info["user"]["real_name"] or user_info["user"]["name"]
            except:
                username = user_id

            mentions.append(f"#{channel_name} - {username}: {text}")

        return "\n".join(mentions)

    except SlackApiError as e:
        return f"Error getting mentions from Slack: {e.response['error']}"
    except KeyError as e:
        if 'SLACK_USER_TOKEN' in str(e):
            return "SLACK_USER_TOKEN environment variable not set. This tool requires a User OAuth Token with the 'search:read' scope."
        if 'SLACK_BOT_TOKEN' in str(e):
            return "SLACK_BOT_TOKEN environment variable not set."
        return f"A required environment variable is not set: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("slack_find_user_by_name", args_schema=SlackFindUserInput)
def slack_find_user_by_name(name: str) -> str:
    """
    Finds a user's ID by their real name or display name.
    Warning: This can be slow on large workspaces as it iterates through all users.
    Returns the user ID (e.g., 'U12345') or an error message.
    """
    user_id = _find_user_id(WebClient(token=os.environ.get("SLACK_BOT_TOKEN")), name)
    if user_id:
        return user_id
    return f"Error: User '{name}' not found."

@tool("slack_get_user_profile", args_schema=SlackGetUserProfileInput)
def slack_get_user_profile(user_id: str) -> str:
    """
    Retrieves a user's profile information (name, email, status, title) as a JSON string.
    Requires the 'users:read.email' scope.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.users_info(user=user_id)
        profile = response["user"]["profile"]
        useful_profile = {
            "real_name": profile.get("real_name"),
            "display_name": profile.get("display_name"),
            "email": profile.get("email"),
            "title": profile.get("title"),
            "status_text": profile.get("status_text"),
            "status_emoji": profile.get("status_emoji"),
        }
        return json.dumps(useful_profile)
    except SlackApiError as e:
        return f"Error getting user profile: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool("slack_get_channel_info", args_schema=SlackGetChannelInfoInput)
def slack_get_channel_info(channel_id: str) -> str:
    """
    Gets details about a channel (name, topic, purpose, member count) as a JSON string.
    """
    try:
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = client.conversations_info(channel=channel_id)
        channel_info = response["channel"]
        useful_info = {
            "name": channel_info.get("name"),
            "topic": channel_info.get("topic", {}).get("value"),
            "purpose": channel_info.get("purpose", {}).get("value"),
            "num_members": channel_info.get("num_members"),
        }
        return json.dumps(useful_info)
    except SlackApiError as e:
        return f"Error getting channel info: {e.response['error']}"
    except KeyError:
        return "SLACK_BOT_TOKEN environment variable not set."
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# --- Tool Aggregator ---

def get_slack_tools():
    """Returns a list of all tools in this module."""
    return [
        slack_post_message,
        slack_post_thread_reply,
        slack_send_direct_message,
        slack_add_reaction,
        slack_upload_file,
        slack_upload_and_notify,
        slack_get_messages,
        slack_get_thread_replies,
        slack_get_mentions,
        slack_find_user_by_name,
        slack_get_user_profile,
        slack_get_channel_info,
    ] 
import os
from typing import List

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

# Import the Slack tools
from core.contrib.slack.slack_tools import get_slack_tools

from dotenv import load_dotenv

# Get the directory of the current script
script_dir = os.path.dirname(__file__)
# Construct the path to the .env file, which is in the same directory
dotenv_path = os.path.join(script_dir, '.env')
# Load the .env file
load_dotenv(dotenv_path=dotenv_path)

# Verify that the SLACK_BOT_TOKEN is loaded
if os.getenv("SLACK_BOT_TOKEN"):
    print("✓ SLACK_BOT_TOKEN is loaded successfully")
else:
    print("✗ SLACK_BOT_TOKEN is not loaded. Please check your .env file.")
    exit(1)

# Also check for the user token, as it's needed for searching mentions
if not os.getenv("SLACK_USER_TOKEN"):
    print("⚠️  SLACK_USER_TOKEN is not set. The 'get_mentions' tool will be unavailable.")

# --- Tool and Model Definition ---

# Get the Slack tools
tools = get_slack_tools()
tool_node = ToolNode(tools)

# Define the model and bind the tools
# We use a comprehensive system prompt to give the agent detailed instructions.
SYSTEM_PROMPT = """You are an expert Slack assistant. Your purpose is to help users interact with Slack by using a comprehensive suite of tools.

Here are the capabilities you have:
- **Sending Messages:** You can send messages to channels, threads, and directly to users.
- **Reading Information:** You can read messages from channels, get replies from threads, and fetch details about users and channels.
- **File Management:** You can upload files and notify users about them in a single step.
- **Interacting:** You can add emoji reactions to messages.
- **Searching:** You can find recent mentions of yourself and look up users by name.

**Important Guidelines:**
1.  **Be resourceful:** Use your tools to answer questions and perform tasks. For example, if a user asks you to "DM John Doe", you should first use `slack_find_user_by_name` to get his user ID, and then use `slack_send_direct_message`.
2.  **Ask for clarification:** Many tools require a channel ID (e.g., 'C024BE91L') or a message timestamp. If you don't have this information, you MUST ask the user for it. Do not guess.
3.  **Handle failures gracefully:** If a tool returns an error, inform the user about the error and suggest a possible reason or next step (e.g., "I couldn't find that user. Could you please double-check the spelling?").
4.  **Confirm actions:** Before performing an action that might be disruptive (like posting in a busy channel), it's good practice to confirm with the user.
5.  **Use the right tool for the job:** Use `slack_upload_and_notify` for combined file uploads and mentions. Use `slack_get_user_profile` to get more details about a person. Read the tool descriptions carefully to understand their purpose.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_PROMPT,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

def assistant_node(state: MessagesState):
    """
    The 'assistant' node. This is the LLM that decides what to do next.
    """
    result = llm_with_tools.invoke(state["messages"])
    return {"messages": [result]}


# --- Graph Construction ---

def build_graph():
    """Builds the ReAct agent graph."""
    builder = StateGraph(MessagesState)

    # Add the nodes
    builder.add_node("assistant", assistant_node)
    builder.add_node("tools", tool_node)

    # Set the entry point
    builder.add_edge(START, "assistant")

    # Add the conditional edge to route to tools or end
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )

    # Add an edge from the tools node back to the assistant
    builder.add_edge("tools", "assistant")

    # Compile the graph
    return builder.compile()

def main():
    """
    Runs the ReAct agent for testing Slack tools.
    """
    print("Welcome to the Slack Tool Testing Agent.")
    
    graph = build_graph()
    
    # A list to store the conversation
    conversation: List[BaseMessage] = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        conversation.append(HumanMessage(content=user_input))

        # Invoke the graph
        result = graph.invoke({"messages": conversation})
        
        # The final response is the last message in the list
        final_response = result["messages"][-1]
        
        # Add the final response to the conversation history
        conversation.append(final_response)
        
        print("Assistant:", final_response.content)

if __name__ == "__main__":
    # Note: To run this, you must have your OpenAI and Slack API keys set
    # in a .env file located in the same directory as this script.
    # The .env file should contain:
    # OPENAI_API_KEY="sk-..."
    # SLACK_BOT_TOKEN="xoxb-..."
    # SLACK_USER_TOKEN="xoxp-..." # Required for the slack_get_mentions tool
    #
    # Ensure your Slack App has the following Bot Token Scopes:
    # - chat:write
    # - files:write
    # - channels:history, groups:history, im:history
    # - users:read
    # - im:write       (for sending DMs)
    # - reactions:write (for adding reactions)
    # And the following User Token Scope:
    # - search:read    (for getting mentions)
    #
    # You also need to install the slack dependencies:
    # pip install ".[slack]"
    main() 
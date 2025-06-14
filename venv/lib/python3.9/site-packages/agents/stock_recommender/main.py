import uuid
from langchain_core.messages import HumanMessage, AIMessage
from agents.stock_recommender import build_agent
# Import tools directly to check for existing preferences
from core.user_profile import get_user_preferences

def run():
    """The main entry point to run the stock recommender agent."""
    graph = build_agent()
    
    user_id = "user_123" 
    config = {"configurable": {"user_id": user_id}}

    print("Welcome to the Stock Recommender Agent!")
    print(f"Session details: user_id='{user_id}'")
    print("-" * 30)

    # Test the long-term memory: check if user preferences already exist.
    saved_preferences = get_user_preferences.invoke({"user_id": user_id})

    if saved_preferences:
        print("I see you have saved preferences:")
        print(f"  - Sectors: {', '.join(saved_preferences.get('sectors', []))}")
        print(f"  - Risk Tolerance: {saved_preferences.get('risk_tolerance', 'N/A')}")
        
        use_saved = input("Would you like to use them for this session? (y/n): ").lower()
        if use_saved == 'y':
            initial_prompt = f"Please find stocks for me based on my saved preferences: {saved_preferences}."
        else:
            # Fall through to ask for new preferences
            saved_preferences = {}
    
    if not saved_preferences:
        print("Let's start by gathering your preferences.")
        sectors = input("What are your favourite stock sectors? (e.g., tech, energy): ")
        sectors_list = [s.strip() for s in sectors.split(',')]
        risk_tolerance = ""
        while risk_tolerance not in ['low', 'medium', 'high']:
            risk_tolerance = input("What is your risk tolerance? (low / medium / high): ").lower()
        
        user_preferences = {"sectors": sectors_list, "risk_tolerance": risk_tolerance}
        initial_prompt = (
            f"I am a new user. My preferences are: {user_preferences}. "
            f"Please save them and then find stocks for me."
        )

    # Each run is a new conversation thread.
    thread_id = str(uuid.uuid4())
    config["configurable"]["thread_id"] = thread_id
    
    initial_state = { "messages": [HumanMessage(content=initial_prompt)], "user_id": user_id }
    
    print("-" * 30)
    print("Agent is thinking...")

    for event in graph.stream(initial_state, config=config, stream_mode="values"):
        last_message = event["messages"][-1]
        if isinstance(last_message, AIMessage):
            if last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    print(f"Agent is calling tool: {tool_call['name']} with args: {tool_call['args']}")
            else:
                print("\nAgent Response:")
                last_message.pretty_print()

if __name__ == "__main__":
    run() 
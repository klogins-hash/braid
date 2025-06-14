from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env before any other imports that might need it
# Look for .env in the project root (two levels up from this file)
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

from .graph import ProductivityAgent

def main():
    """
    Main function to run the Productivity Assistant agent.
    """
    print("Initializing Productivity Assistant...")
    agent = ProductivityAgent()

    # The test query that requires using both Gmail and Google Calendar
    query = (
        "I just landed a new client, 'Innovate Inc.'. "
        "Please send a welcome email to their main contact, 'chase@business-plans.com', "
        "letting her know we're excited to work with them. Also, please schedule a 30-minute "
        "'Project Kickoff' meeting with her for tomorrow at 2 PM PST."
    )

    print(f"\n--- Sending Query ---\n{query}\n---------------------\n")
    
    # Run the agent
    result = agent.run(query)
    
    # Print the final response from the agent
    print("\n--- Final Response ---")
    final_response = result["messages"][-1].content
    print(final_response)
    print("----------------------\n")

if __name__ == "__main__":
    main()

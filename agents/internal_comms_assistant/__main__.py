from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env before any other imports that might need it
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

from .graph import InternalCommsAgent

def main():
    """
    Main function to run the Internal Comms Assistant agent.
    """
    print("Initializing Internal Comms Assistant...")
    agent = InternalCommsAgent()

    # The test query that requires using both Outlook and Teams
    query = (
        "There's a critical bug in the payment gateway, causing intermittent failures. "
        "Please send an urgent email to the engineering lead at 'lead.engineer@example.com' "
        "with the subject 'Critical Bug: Payment Gateway' and a body explaining the issue. "
        "Also, post a high-priority message in the 'Dev Alerts' channel in the 'Engineering' "
        "team to notify everyone to be on standby."
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

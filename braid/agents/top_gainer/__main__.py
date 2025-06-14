from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env before any other imports that might need it
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

from .graph import TopGainerAgent

def main():
    """
    Main function to run the Top Gainer agent.
    """
    # This should be the entry point when running the module.
    # Ensure your .env file has the necessary API keys.
    print("Initializing Top Gainer Agent...")
    agent = TopGainerAgent()
    
    print("Running agent to find top gainer and reason...")
    result = agent.run()
    
    print("\n--- Final Analyst Rating ---")
    print(result.get("final_rating", "No rating generated."))
    print("--------------------------\n")

if __name__ == "__main__":
    main()

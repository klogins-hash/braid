# main.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """
    This is the main entry point for your agent.
    """
    print("Agent started!")
    
    # Example: Accessing an environment variable
    api_key = os.getenv("YOUR_API_KEY")
    if api_key:
        print("API Key found.")
    else:
        print("API Key not found. Please set it in your .env file.")

    print("Agent finished.")


if __name__ == "__main__":
    main() 
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file at the project root.
# This ensures that any library needing environment variables will have them available.
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Expose the graph builder for easy import.
from .graph import build_agent 
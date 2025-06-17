import sqlite3
import json
from langchain_core.tools import tool

DB_PATH = "langgraph.db"

def get_db_conn():
    """Establishes a connection to the SQLite database."""
    # Using check_same_thread=False is important for use in multi-threaded apps
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Initializes the user_profiles table in the database if it doesn't exist."""
    with get_db_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                preferences TEXT NOT NULL
            )
        """)

@tool
def get_user_preferences(user_id: str) -> dict:
    """
    Retrieves the stored preferences for a given user_id from the SQLite database.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A dictionary containing the user's preferences, or an empty dictionary if not found.
    """
    with get_db_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT preferences FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
    
    if row:
        print(f"CORE: Found preferences for user_id: {user_id}")
        return json.loads(row[0])
    else:
        print(f"CORE: No preferences found for user_id: {user_id}")
        return {}

@tool
def save_user_preferences(user_id: str, preferences: dict) -> str:
    """
    Saves or updates a user's preferences in the SQLite database.

    Args:
        user_id: The unique identifier for the user.
        preferences: A dictionary of the user's preferences to save.

    Returns:
        A confirmation message indicating success.
    """
    with get_db_conn() as conn:
        # Use INSERT OR REPLACE to handle both new and existing users.
        conn.execute(
            "INSERT OR REPLACE INTO user_profiles (user_id, preferences) VALUES (?, ?)",
            (user_id, json.dumps(preferences))
        )
    
    print(f"CORE: Saved preferences for user_id: {user_id}")
    return "User preferences saved successfully."

# Initialize the database when the module is loaded.
init_db() 
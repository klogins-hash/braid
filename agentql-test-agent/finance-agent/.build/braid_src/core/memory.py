import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

def get_checkpointer():
    """
    Returns a production-ready SqliteSaver checkpointer.
    
    This system is configured to be persistent by default, saving all conversational
    checkpoints to a local SQLite database file.
    """
    # Using check_same_thread=False is crucial for LangGraph's checkpointer,
    # which may operate in different threads than the main application.
    conn = sqlite3.connect("langgraph.db", check_same_thread=False)
    
    # The SqliteSaver instance will manage the connection's lifecycle.
    return SqliteSaver(conn=conn) 
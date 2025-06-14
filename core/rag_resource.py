"""
Core component for creating a RAG (Retrieval-Augmented Generation) resource
that can be seamlessly integrated into a LangGraph agent.
"""
from langchain_core.tools import Tool
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

def create_rag_tool_from_directory(directory_path: str, name: str, description: str) -> Tool:
    """
    Creates a LangChain Tool for RAG on a given document directory.

    This function sets up a LlamaIndex VectorStoreIndex from documents
    in the specified directory and wraps its query engine in a LangChain Tool.

    Args:
        directory_path (str): The path to the directory containing documents.
        name (str): The name for the resulting LangChain Tool.
        description (str): The description for the Tool, telling the agent
                           when to use it.

    Returns:
        Tool: A LangChain Tool that can query the documents.
    """
    # Configure LlamaIndex to use OpenAI models
    Settings.llm = OpenAI(model="gpt-4o")
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

    # Load documents from the specified directory
    documents = SimpleDirectoryReader(directory_path).load_data()

    # Create a Vector Store Index from the documents
    index = VectorStoreIndex.from_documents(documents)

    # Create a query engine from the index
    query_engine = index.as_query_engine()

    # Create and return a LangChain Tool from the query engine
    rag_tool = Tool(
        name=name,
        func=lambda q: str(query_engine.query(q)),
        description=description,
    )

    return rag_tool 
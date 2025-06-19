# 13. RAG with User-Uploaded Documents using LlamaIndex

This document outlines how to equip agents with the ability to perform Retrieval-Augmented Generation (RAG) on a directory of documents provided at runtime. This allows an agent to answer questions and perform tasks based on specific, private, or domain-specific knowledge.

We use the LlamaIndex library to handle the complexities of document loading, parsing, and indexing, and expose this capability to our agents as a simple, reusable tool.

---

### How It Works: The RAG Tool Factory

The core of this capability is the `create_rag_tool_from_directory` function located in `core/rag_resource.py`. This function acts as a factory that generates a query tool for any given set of documents.

Here's the workflow it automates:

1.  **Load Documents**: It uses LlamaIndex's `SimpleDirectoryReader` to ingest all files from a specified directory path. This reader can handle various file types, including `.pdf`, `.md`, `.txt`, and more.
2.  **Create Index**: It processes the loaded documents, splits them into text chunks (nodes), creates vector embeddings using OpenAI, and builds an in-memory `VectorStoreIndex`. This index is a searchable representation of the document content.
3.  **Create Query Engine**: It derives a `query_engine` from the index. This engine provides a high-level interface for asking natural language questions about the documents.
4.  **Wrap as a Tool**: Finally, it wraps the query engine in a standard LangChain `Tool`. This makes the entire RAG pipeline available to a LangGraph agent as a single, callable tool.

### How to Use in an Agent

Integrating this RAG capability into an agent is straightforward and follows the standard pattern for adding tools.

> **Note on Dependencies**
> To process PDF files, which is a common use case, you must have the `pypdf` library installed. This is included in the core dependencies, which you can install by running `pip install .` from the project root. The LlamaIndex `SimpleDirectoryReader` will use it automatically.

#### Step 1: Place User Documents

The user must place the documents they want the agent to analyze into a designated directory. For example: `data/my_project_docs/`.

#### Step 2: Create the RAG Tool

In your agent's graph-building file, import the factory function and call it to create the tool.

```python
# In your agent's graph.py
from core.rag_resource import create_rag_tool_from_directory
from .my_other_tools import my_tool

# Define the path to the user's documents
docs_path = "data/my_project_docs/"

# Create the RAG tool
document_search_tool = create_rag_tool_from_directory(
    directory_path=docs_path,
    name="DocumentSearchTool",
    description="Use this tool to answer questions about the user's uploaded documents. It is the only source of information for these files."
)

# Add the new tool to your agent's list of tools
tools = [my_tool, document_search_tool]
```

#### Step 3: Guide the Agent with a System Prompt

The final, critical step is to inform the agent's LLM about its new capability. Modify the agent's system prompt to explicitly mention the tool and when to use it.

```python
# In your agent's primary node
from langchain_core.messages import SystemMessage

system_message = SystemMessage(
    content="You are a helpful assistant. You have access to a special tool called `DocumentSearchTool` "
            "that can find information inside the user's private documents. "
            "When the user's question seems to refer to their uploaded files, you must use this tool."
)
# ... prepend this to your model call ...
```

By following this pattern, you can quickly build agents that combine general knowledge with deep, contextual understanding of user-provided data, making them significantly more powerful and versatile. 
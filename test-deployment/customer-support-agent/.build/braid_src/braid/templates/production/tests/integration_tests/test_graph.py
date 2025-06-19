"""Integration tests for the agent graph."""

import os
from unittest.mock import patch

import pytest

from {AGENT_NAME}.graph import create_agent_graph


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
    reason="No API key available for integration test"
)
def test_graph_creation():
    """Test that the graph can be created successfully."""
    graph = create_agent_graph()
    assert graph is not None


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
    reason="No API key available for integration test"
)  
def test_graph_simple_interaction():
    """Test a simple interaction with the graph."""
    graph = create_agent_graph()
    
    # Test with a simple message
    result = graph.invoke({
        "messages": [{"role": "user", "content": "Hello, can you help me?"}]
    })
    
    assert "messages" in result
    assert len(result["messages"]) > 0
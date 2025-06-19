"""Utility functions for the notion_test_agent agent."""

import os
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


def load_chat_model(model_name: str, temperature: float = 0.1):
    """Load a chat model based on the model name."""
    if model_name.startswith("gpt-") or model_name.startswith("openai/"):
        # OpenAI model
        model = model_name.replace("openai/", "")
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif "claude" in model_name.lower() or model_name.startswith("anthropic/"):
        # Anthropic model
        model = model_name.replace("anthropic/", "")
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        # Default to OpenAI
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )


def validate_api_keys() -> list[str]:
    """Validate that required API keys are present."""
    missing = []
    
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        missing.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    return missing
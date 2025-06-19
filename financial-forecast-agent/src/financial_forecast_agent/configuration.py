"""Configuration for the financial_forecast_agent agent."""

import os
from typing import Optional


class Configuration:
    """Configuration settings for the agent."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.model = os.getenv("AGENT_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.1"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Tool-specific configurations

        
    def validate(self) -> list[str]:
        """Validate configuration and return list of missing requirements."""
        missing = []
        
        if not self.openai_api_key and not self.anthropic_api_key:
            missing.append("OPENAI_API_KEY or ANTHROPIC_API_KEY")
            
        # Tool-specific validation

        
        return missing
    
    @classmethod
    def from_context(cls) -> "Configuration":
        """Create configuration from current context/environment."""
        return cls()
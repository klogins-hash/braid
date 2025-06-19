"""Test configuration module."""

import os
from unittest.mock import patch

import pytest

from sales_intelligence_agent_v3.configuration import Configuration


def test_configuration_default_values():
    """Test configuration with default values."""
    with patch.dict(os.environ, {}, clear=True):
        config = Configuration()
        assert config.model == "gpt-4o"
        assert config.temperature == 0.1


def test_configuration_from_env():
    """Test configuration from environment variables."""
    with patch.dict(os.environ, {
        "AGENT_MODEL": "gpt-3.5-turbo",
        "AGENT_TEMPERATURE": "0.5",
        "OPENAI_API_KEY": "test-key"
    }):
        config = Configuration()
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.openai_api_key == "test-key"


def test_configuration_validation():
    """Test configuration validation."""
    with patch.dict(os.environ, {}, clear=True):
        config = Configuration()
        missing = config.validate()
        assert "OPENAI_API_KEY or ANTHROPIC_API_KEY" in missing


@pytest.fixture
def valid_config():
    """Fixture providing a valid configuration."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return Configuration()
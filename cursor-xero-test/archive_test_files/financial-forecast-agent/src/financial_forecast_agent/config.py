"""Production configuration management for Financial Forecast Agent."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Production configuration settings."""
    
    # Core API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    
    # Xero API Configuration
    XERO_CLIENT_ID: str = os.getenv("XERO_CLIENT_ID", "")
    XERO_CLIENT_SECRET: str = os.getenv("XERO_CLIENT_SECRET", "")
    XERO_ACCESS_TOKEN: str = os.getenv("XERO_ACCESS_TOKEN", "")
    XERO_REDIRECT_URI: str = os.getenv("XERO_REDIRECT_URI", "http://localhost:8080/callback")
    
    # Notion API (Optional)
    NOTION_API_KEY: Optional[str] = os.getenv("NOTION_API_KEY")
    
    # LangSmith Tracing
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "financial-forecast-production")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    
    # Application Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "forecast_data.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Monitoring
    HEALTH_CHECK_PORT: int = int(os.getenv("HEALTH_CHECK_PORT", "8000"))
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Rate Limiting
    API_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "60"))
    XERO_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("XERO_RATE_LIMIT_PER_MINUTE", "300"))
    PERPLEXITY_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("PERPLEXITY_RATE_LIMIT_PER_MINUTE", "20"))
    
    @classmethod
    def validate_required_env_vars(cls) -> list[str]:
        """Validate that all required environment variables are set."""
        missing_vars = []
        
        required_vars = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "XERO_CLIENT_ID": cls.XERO_CLIENT_ID,
            "XERO_CLIENT_SECRET": cls.XERO_CLIENT_SECRET,
            "XERO_ACCESS_TOKEN": cls.XERO_ACCESS_TOKEN,
            "PERPLEXITY_API_KEY": cls.PERPLEXITY_API_KEY,
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value or var_value == "":
                missing_vars.append(var_name)
        
        return missing_vars
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def setup_logging(cls):
        """Setup production logging configuration."""
        log_level = getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('/app/logs/agent.log') if cls.is_production() else logging.StreamHandler()
            ]
        )
        
        # Silence noisy libraries in production
        if cls.is_production():
            logging.getLogger("requests").setLevel(logging.WARNING)
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("httpcore").setLevel(logging.WARNING)

# Global config instance
config = Config()
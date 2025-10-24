# infrastructure/api/config.py
from pydantic import BaseSettings
from typing import List


class APIConfig(BaseSettings):
    """
    API-specific configuration for the Progresser FastAPI application.
    
    This class extends Pydantic's BaseSettings to provide configuration
    management for the API layer. It supports environment variable
    configuration and provides sensible defaults for all settings.
    
    Attributes:
        title (str): Application title displayed in API documentation
        version (str): API version for semantic versioning
        description (str): Detailed description of the API
        api_prefix (str): URL prefix for all API endpoints
        docs_url (str): URL path for interactive API documentation
        cors_origins (List[str]): Allowed origins for CORS requests
        cors_methods (List[str]): Allowed HTTP methods for CORS
        enable_request_logging (bool): Whether to enable request logging middleware
    
    Example:
        >>> config = APIConfig()
        >>> print(config.title)
        'Progresser API'
        
        # Override via environment variables
        >>> import os
        >>> os.environ['API_TITLE'] = 'My Custom API'
        >>> config = APIConfig()
        >>> print(config.title)
        'My Custom API'
    """
    title: str = "Progresser API"
    version: str = "1.0.0"
    description: str = "Task management API"

    # API Routing
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"

    # CORS
    cors_origins: List[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    cors_methods: List[str] = ["*"]

    # Middleware
    enable_request_logging: bool = True

    class Config:
        """
        Pydantic configuration for APIConfig.
        
        This nested class configures how Pydantic handles the settings,
        including environment variable loading and validation.
        """
        env_file = ".env"


# Singleton instance for global access
api_config = APIConfig()
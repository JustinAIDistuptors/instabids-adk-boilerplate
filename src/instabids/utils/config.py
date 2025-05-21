"""
Configuration management utility for InstaBids.
"""
import os
from functools import lru_cache
from typing import Dict, Any, Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Application settings
    environment: str = "development"
    app_name: str = "InstaBids"
    version: str = "0.1.0"
    
    # API settings
    allowed_origins: str = "http://localhost:3000"  # Comma-separated origins for CORS
    
    # Google API settings
    google_api_key: Optional[str] = None
    google_genai_use_vertexai: bool = False
    google_cloud_project: Optional[str] = None
    google_cloud_location: Optional[str] = None
    
    # Database settings
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # Agent settings
    default_homeowner_agent_model: str = "gemini-2.0-pro"
    default_recruiter_agent_model: str = "gemini-2.0-pro"
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings, with caching for efficiency.
    
    Returns:
        Settings object with application configuration.
    """
    return Settings()

def get_cors_origins() -> list:
    """
    Get the list of allowed CORS origins.
    
    Returns:
        List of allowed origins for CORS.
    """
    settings = get_settings()
    return [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
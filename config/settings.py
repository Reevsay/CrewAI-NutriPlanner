"""
Configuration settings for the Smart Recipe & Meal Planning System
"""
import os
from typing import Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    nutritionix_app_id: Optional[str] = Field(None, env="NUTRITIONIX_APP_ID")
    nutritionix_api_key: Optional[str] = Field(None, env="NUTRITIONIX_API_KEY")
    kroger_client_id: Optional[str] = Field(None, env="KROGER_CLIENT_ID")
    kroger_client_secret: Optional[str] = Field(None, env="KROGER_CLIENT_SECRET")
    instacart_api_key: Optional[str] = Field(None, env="INSTACART_API_KEY")
    
    # API Base URLs
    usda_api_base_url: str = Field(
        "https://api.nal.usda.gov/fdc/v1", 
        env="USDA_API_BASE_URL"
    )
    
    # Application Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    cache_duration_hours: int = Field(24, env="CACHE_DURATION_HOURS")
    max_retries: int = Field(3, env="MAX_RETRIES")
    request_timeout: int = Field(30, env="REQUEST_TIMEOUT")
    
    # Development Settings
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("production", env="ENVIRONMENT")
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
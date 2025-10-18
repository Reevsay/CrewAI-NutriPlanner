"""
Google Gemini API configuration and utilities
"""
import os
from typing import Optional
import google.generativeai as genai
from loguru import logger
from config.settings import settings


def configure_gemini() -> bool:
    """
    Configure Google Gemini API with the provided API key
    
    Returns:
        bool: True if configuration successful, False otherwise
    """
    try:
        if not settings.google_api_key:
            logger.error("Google API key not found in settings")
            return False
        
        # Configure the Gemini API
        genai.configure(api_key=settings.google_api_key)
        
        # Test the connection
        model = genai.GenerativeModel('gemini-2.5-flash')
        test_response = model.generate_content("Hello")
        
        if test_response:
            logger.info("Google Gemini API configured successfully")
            return True
        else:
            logger.error("Failed to get response from Gemini API")
            return False
            
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        return False


def get_gemini_model(model_name: str = "gemini-2.5-flash") -> Optional[genai.GenerativeModel]:
    """
    Get a configured Gemini model instance
    
    Args:
        model_name: Name of the Gemini model to use
        
    Returns:
        GenerativeModel instance or None if configuration fails
    """
    try:
        if not settings.google_api_key:
            logger.error("Google API key not configured")
            return None
            
        genai.configure(api_key=settings.google_api_key)
        return genai.GenerativeModel(model_name)
        
    except Exception as e:
        logger.error(f"Failed to get Gemini model: {e}")
        return None


def get_available_models() -> list:
    """
    Get list of available Gemini models
    
    Returns:
        List of available model names
    """
    try:
        if not settings.google_api_key:
            logger.error("Google API key not configured")
            return []
            
        genai.configure(api_key=settings.google_api_key)
        models = []
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                models.append(model.name)
                
        return models
        
    except Exception as e:
        logger.error(f"Failed to list Gemini models: {e}")
        return []


# CrewAI LLM configuration for Gemini
def get_crewai_gemini_config() -> dict:
    """
    Get CrewAI configuration for Google Gemini
    
    Returns:
        Dictionary with CrewAI LLM configuration
    """
    return {
        "llm": {
            "provider": "google",
            "config": {
                "model": "gemini-2.5-flash",
                "api_key": settings.google_api_key,
                "temperature": 0.7,
                "max_tokens": 4096
            }
        }
    }
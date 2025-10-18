"""
Nutrition API integration for the Smart Recipe & Meal Planning System.

This module provides integration with USDA FoodData Central API for nutritional data
lookup with caching mechanism and error handling.
"""

import json
import time
import os
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests
from pathlib import Path
import logging

from ..models.recipe import NutritionalInfo


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class FoodSearchResult:
    """Result from food search API."""
    fdc_id: int
    description: str
    brand_owner: Optional[str] = None
    ingredients: Optional[str] = None
    data_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FoodSearchResult':
        """Create from dictionary for cache loading."""
        return cls(**data)


@dataclass
class NutrientData:
    """Nutrient data from USDA API."""
    nutrient_id: int
    nutrient_name: str
    value: float
    unit: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NutrientData':
        """Create from dictionary for cache loading."""
        return cls(**data)


@dataclass
class CachedNutritionData:
    """Cached nutrition data with timestamp."""
    nutrition_info: NutritionalInfo
    timestamp: datetime
    source: str
    
    def is_expired(self, cache_duration_hours: int = 24) -> bool:
        """Check if cached data is expired."""
        expiry_time = self.timestamp + timedelta(hours=cache_duration_hours)
        return datetime.now() > expiry_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching."""
        return {
            'nutrition_info': asdict(self.nutrition_info),
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CachedNutritionData':
        """Create from dictionary for cache loading."""
        return cls(
            nutrition_info=NutritionalInfo(**data['nutrition_info']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=data['source']
        )


class NutritionAPIError(Exception):
    """Custom exception for nutrition API errors."""
    pass


class NutritionAPI:
    """
    USDA FoodData Central API integration with caching and error handling.
    
    This class provides methods to search for foods and retrieve nutritional
    information with automatic caching and fallback strategies.
    """
    
    # USDA FoodData Central API endpoints
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    SEARCH_ENDPOINT = f"{BASE_URL}/foods/search"
    FOOD_ENDPOINT = f"{BASE_URL}/food"
    
    # Nutrient IDs from USDA database (most common ones)
    NUTRIENT_MAPPING = {
        'calories': 1008,      # Energy (kcal)
        'protein': 1003,       # Protein (g)
        'carbohydrates': 1005, # Carbohydrate, by difference (g)
        'fat': 1004,          # Total lipid (fat) (g)
        'fiber': 1079,        # Fiber, total dietary (g)
        'sugar': 2000,        # Sugars, total including NLEA (g)
        'sodium': 1093,       # Sodium, Na (mg)
        'vitamin_c': 1162,    # Vitamin C, total ascorbic acid (mg)
        'calcium': 1087,      # Calcium, Ca (mg)
        'iron': 1089,         # Iron, Fe (mg)
    }
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 cache_dir: str = "cache",
                 cache_duration_hours: int = 24,
                 max_retries: int = 3,
                 request_timeout: int = 30):
        """
        Initialize the Nutrition API client.
        
        Args:
            api_key: USDA API key (optional for basic usage)
            cache_dir: Directory to store cached data
            cache_duration_hours: How long to cache data (hours)
            max_retries: Maximum number of retry attempts
            request_timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv('USDA_API_KEY')
        self.cache_duration_hours = cache_duration_hours
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        
        # Set up caching
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.nutrition_cache_file = self.cache_dir / "nutrition_cache.json"
        self.search_cache_file = self.cache_dir / "search_cache.json"
        
        # Load existing caches
        self._nutrition_cache = self._load_nutrition_cache()
        self._search_cache = self._load_search_cache()
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Smart-Recipe-Meal-Planner/1.0'
        })
    
    def _load_nutrition_cache(self) -> Dict[str, CachedNutritionData]:
        """Load nutrition cache from file."""
        if not self.nutrition_cache_file.exists():
            return {}
        
        try:
            with open(self.nutrition_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            nutrition_cache = {}
            for key, data in cache_data.items():
                try:
                    nutrition_cache[key] = CachedNutritionData.from_dict(data)
                except Exception as e:
                    logger.warning(f"Failed to load cached nutrition data for {key}: {e}")
            
            return nutrition_cache
        except Exception as e:
            logger.error(f"Failed to load nutrition cache: {e}")
            return {}
    
    def _load_search_cache(self) -> Dict[str, List[FoodSearchResult]]:
        """Load search cache from file."""
        if not self.search_cache_file.exists():
            return {}
        
        try:
            with open(self.search_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            search_cache = {}
            for query, results_data in cache_data.items():
                try:
                    search_cache[query] = [FoodSearchResult.from_dict(result) for result in results_data]
                except Exception as e:
                    logger.warning(f"Failed to load cached search results for {query}: {e}")
            
            return search_cache
        except Exception as e:
            logger.error(f"Failed to load search cache: {e}")
            return {}
    
    def _save_nutrition_cache(self):
        """Save nutrition cache to file."""
        try:
            cache_data = {}
            for key, cached_data in self._nutrition_cache.items():
                if not cached_data.is_expired(self.cache_duration_hours):
                    cache_data[key] = cached_data.to_dict()
            
            with open(self.nutrition_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save nutrition cache: {e}")
    
    def _save_search_cache(self):
        """Save search cache to file."""
        try:
            cache_data = {}
            for query, results in self._search_cache.items():
                cache_data[query] = [result.to_dict() for result in results]
            
            with open(self.search_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save search cache: {e}")
    
    def _generate_cache_key(self, food_name: str, quantity: float = 100.0) -> str:
        """Generate a cache key for food nutrition data."""
        key_string = f"{food_name.lower().strip()}_{quantity}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _make_request(self, url: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            url: Request URL
            params: Query parameters
            data: Request body data
            
        Returns:
            Response JSON data
            
        Raises:
            NutritionAPIError: If request fails after all retries
        """
        if params is None:
            params = {}
        
        # Add API key if available
        if self.api_key:
            params['api_key'] = self.api_key
        
        for attempt in range(self.max_retries):
            try:
                if data:
                    response = self.session.post(
                        url, 
                        params=params, 
                        json=data, 
                        timeout=self.request_timeout
                    )
                else:
                    response = self.session.get(
                        url, 
                        params=params, 
                        timeout=self.request_timeout
                    )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise NutritionAPIError(f"Failed to make request after {self.max_retries} attempts: {e}")
                
                # Exponential backoff
                time.sleep(2 ** attempt)
    
    def search_foods(self, query: str, max_results: int = 10) -> List[FoodSearchResult]:
        """
        Search for foods using USDA FoodData Central API.
        
        Args:
            query: Search query (food name)
            max_results: Maximum number of results to return
            
        Returns:
            List of food search results
        """
        # Check cache first
        cache_key = f"{query.lower().strip()}_{max_results}"
        if cache_key in self._search_cache:
            logger.debug(f"Using cached search results for: {query}")
            return self._search_cache[cache_key]
        
        try:
            # Prepare search parameters
            search_params = {
                'query': query,
                'pageSize': max_results,
                'dataType': ['Foundation', 'SR Legacy', 'Survey (FNDDS)'],
                'sortBy': 'dataType.keyword',
                'sortOrder': 'asc'
            }
            
            logger.info(f"Searching for foods: {query}")
            response_data = self._make_request(self.SEARCH_ENDPOINT, data=search_params)
            
            # Parse results
            results = []
            foods = response_data.get('foods', [])
            
            for food in foods[:max_results]:
                result = FoodSearchResult(
                    fdc_id=food.get('fdcId'),
                    description=food.get('description', ''),
                    brand_owner=food.get('brandOwner'),
                    ingredients=food.get('ingredients'),
                    data_type=food.get('dataType')
                )
                results.append(result)
            
            # Cache results
            self._search_cache[cache_key] = results
            self._save_search_cache()
            
            logger.info(f"Found {len(results)} foods for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search foods for query '{query}': {e}")
            raise NutritionAPIError(f"Food search failed: {e}")
    
    def get_nutrition_data(self, fdc_id: int) -> List[NutrientData]:
        """
        Get detailed nutrition data for a specific food by FDC ID.
        
        Args:
            fdc_id: USDA FoodData Central ID
            
        Returns:
            List of nutrient data
        """
        try:
            url = f"{self.FOOD_ENDPOINT}/{fdc_id}"
            params = {'nutrients': list(self.NUTRIENT_MAPPING.values())}
            
            logger.debug(f"Getting nutrition data for FDC ID: {fdc_id}")
            response_data = self._make_request(url, params=params)
            
            # Parse nutrient data
            nutrients = []
            food_nutrients = response_data.get('foodNutrients', [])
            
            for nutrient in food_nutrients:
                nutrient_data = NutrientData(
                    nutrient_id=nutrient.get('nutrient', {}).get('id'),
                    nutrient_name=nutrient.get('nutrient', {}).get('name', ''),
                    value=nutrient.get('amount', 0.0),
                    unit=nutrient.get('nutrient', {}).get('unitName', '')
                )
                nutrients.append(nutrient_data)
            
            return nutrients
            
        except Exception as e:
            logger.error(f"Failed to get nutrition data for FDC ID {fdc_id}: {e}")
            raise NutritionAPIError(f"Nutrition data retrieval failed: {e}")
    
    def _convert_nutrients_to_nutrition_info(self, nutrients: List[NutrientData]) -> NutritionalInfo:
        """
        Convert USDA nutrient data to our NutritionalInfo model.
        
        Args:
            nutrients: List of nutrient data from USDA API
            
        Returns:
            NutritionalInfo object
        """
        nutrition_info = NutritionalInfo()
        
        # Create reverse mapping for nutrient IDs
        id_to_field = {v: k for k, v in self.NUTRIENT_MAPPING.items()}
        
        for nutrient in nutrients:
            field_name = id_to_field.get(nutrient.nutrient_id)
            if field_name and hasattr(nutrition_info, field_name):
                setattr(nutrition_info, field_name, nutrient.value)
        
        return nutrition_info
    
    def get_food_nutrition(self, food_name: str, quantity: float = 100.0) -> NutritionalInfo:
        """
        Get nutritional information for a food item.
        
        Args:
            food_name: Name of the food
            quantity: Quantity in grams (default: 100g)
            
        Returns:
            NutritionalInfo object with nutritional data
        """
        # Check cache first
        cache_key = self._generate_cache_key(food_name, quantity)
        if cache_key in self._nutrition_cache:
            cached_data = self._nutrition_cache[cache_key]
            if not cached_data.is_expired(self.cache_duration_hours):
                logger.debug(f"Using cached nutrition data for: {food_name}")
                return cached_data.nutrition_info
            else:
                # Remove expired cache entry
                del self._nutrition_cache[cache_key]
        
        try:
            # Search for the food
            search_results = self.search_foods(food_name, max_results=1)
            
            if not search_results:
                raise NutritionAPIError(f"No food found for: {food_name}")
            
            # Get the first (best) result
            best_match = search_results[0]
            logger.info(f"Using food: {best_match.description} (FDC ID: {best_match.fdc_id})")
            
            # Get nutrition data
            nutrients = self.get_nutrition_data(best_match.fdc_id)
            nutrition_info = self._convert_nutrients_to_nutrition_info(nutrients)
            
            # Adjust for quantity (USDA data is per 100g)
            if quantity != 100.0:
                nutrition_info = nutrition_info.multiply(quantity / 100.0)
            
            # Cache the result
            cached_data = CachedNutritionData(
                nutrition_info=nutrition_info,
                timestamp=datetime.now(),
                source=f"USDA FDC ID: {best_match.fdc_id}"
            )
            self._nutrition_cache[cache_key] = cached_data
            self._save_nutrition_cache()
            
            logger.info(f"Retrieved nutrition data for {food_name} ({quantity}g)")
            return nutrition_info
            
        except Exception as e:
            logger.error(f"Failed to get nutrition for {food_name}: {e}")
            # Try fallback strategy
            return self._get_fallback_nutrition(food_name, quantity)
    
    def _get_fallback_nutrition(self, food_name: str, quantity: float) -> NutritionalInfo:
        """
        Fallback strategy for when API fails.
        
        This provides basic estimated nutritional values based on food categories.
        """
        logger.warning(f"Using fallback nutrition data for: {food_name}")
        
        # Basic fallback estimates (per 100g)
        fallback_data = {
            # Proteins
            'chicken': NutritionalInfo(calories=165, protein=31, fat=3.6, carbohydrates=0),
            'beef': NutritionalInfo(calories=250, protein=26, fat=17, carbohydrates=0),
            'fish': NutritionalInfo(calories=206, protein=22, fat=12, carbohydrates=0),
            'egg': NutritionalInfo(calories=155, protein=13, fat=11, carbohydrates=1.1),
            
            # Carbohydrates
            'rice': NutritionalInfo(calories=130, protein=2.7, fat=0.3, carbohydrates=28),
            'bread': NutritionalInfo(calories=265, protein=9, fat=3.2, carbohydrates=49),
            'pasta': NutritionalInfo(calories=131, protein=5, fat=1.1, carbohydrates=25),
            'potato': NutritionalInfo(calories=77, protein=2, fat=0.1, carbohydrates=17),
            
            # Vegetables
            'broccoli': NutritionalInfo(calories=34, protein=2.8, fat=0.4, carbohydrates=7, fiber=2.6),
            'carrot': NutritionalInfo(calories=41, protein=0.9, fat=0.2, carbohydrates=10, fiber=2.8),
            'spinach': NutritionalInfo(calories=23, protein=2.9, fat=0.4, carbohydrates=3.6, fiber=2.2),
            
            # Fruits
            'apple': NutritionalInfo(calories=52, protein=0.3, fat=0.2, carbohydrates=14, fiber=2.4, sugar=10),
            'banana': NutritionalInfo(calories=89, protein=1.1, fat=0.3, carbohydrates=23, fiber=2.6, sugar=12),
            
            # Default fallback
            'default': NutritionalInfo(calories=100, protein=5, fat=3, carbohydrates=15)
        }
        
        # Find best match
        food_lower = food_name.lower()
        for key, nutrition in fallback_data.items():
            if key in food_lower:
                # Adjust for quantity
                if quantity != 100.0:
                    nutrition = nutrition.multiply(quantity / 100.0)
                return nutrition
        
        # Use default if no match found
        nutrition = fallback_data['default']
        if quantity != 100.0:
            nutrition = nutrition.multiply(quantity / 100.0)
        
        return nutrition
    
    def batch_get_nutrition(self, food_items: List[Tuple[str, float]]) -> Dict[str, NutritionalInfo]:
        """
        Get nutrition data for multiple food items efficiently.
        
        Args:
            food_items: List of (food_name, quantity) tuples
            
        Returns:
            Dictionary mapping food names to NutritionalInfo
        """
        results = {}
        
        for food_name, quantity in food_items:
            try:
                nutrition_info = self.get_food_nutrition(food_name, quantity)
                results[food_name] = nutrition_info
            except Exception as e:
                logger.error(f"Failed to get nutrition for {food_name}: {e}")
                # Continue with other items
                continue
        
        return results
    
    def clear_cache(self):
        """Clear all cached data."""
        self._nutrition_cache.clear()
        self._search_cache.clear()
        
        # Remove cache files
        if self.nutrition_cache_file.exists():
            self.nutrition_cache_file.unlink()
        if self.search_cache_file.exists():
            self.search_cache_file.unlink()
        
        logger.info("Nutrition API cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        nutrition_count = len(self._nutrition_cache)
        search_count = len(self._search_cache)
        
        # Count expired entries
        expired_nutrition = sum(
            1 for cached_data in self._nutrition_cache.values()
            if cached_data.is_expired(self.cache_duration_hours)
        )
        
        return {
            'nutrition_cache_entries': nutrition_count,
            'search_cache_entries': search_count,
            'expired_nutrition_entries': expired_nutrition,
            'cache_duration_hours': self.cache_duration_hours
        }
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if hasattr(self, 'session'):
            self.session.close()


# Convenience function for quick nutrition lookup
def get_nutrition(food_name: str, quantity: float = 100.0) -> NutritionalInfo:
    """
    Quick function to get nutrition data for a food item.
    
    Args:
        food_name: Name of the food
        quantity: Quantity in grams (default: 100g)
        
    Returns:
        NutritionalInfo object
    """
    api = NutritionAPI()
    return api.get_food_nutrition(food_name, quantity)
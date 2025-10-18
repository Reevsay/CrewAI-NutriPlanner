"""
Grocery Price API integration for the Smart Recipe & Meal Planning System.

This module provides integration with grocery price APIs for ingredient pricing,
availability checking, and location-based queries with caching and error handling.
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

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class IngredientPrice:
    """Price information for an ingredient."""
    ingredient_name: str
    price: float
    unit: str
    store_name: str
    brand: Optional[str] = None
    size: Optional[str] = None
    availability: bool = True
    location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IngredientPrice':
        """Create from dictionary for cache loading."""
        return cls(**data)


@dataclass
class StoreLocation:
    """Store location information."""
    store_id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoreLocation':
        """Create from dictionary for cache loading."""
        return cls(**data)


@dataclass
class CachedPriceData:
    """Cached price data with timestamp."""
    prices: List[IngredientPrice]
    timestamp: datetime
    location: str
    
    def is_expired(self, cache_duration_hours: int = 24) -> bool:
        """Check if cached data is expired."""
        expiry_time = self.timestamp + timedelta(hours=cache_duration_hours)
        return datetime.now() > expiry_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for caching."""
        return {
            'prices': [price.to_dict() for price in self.prices],
            'timestamp': self.timestamp.isoformat(),
            'location': self.location
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CachedPriceData':
        """Create from dictionary for cache loading."""
        return cls(
            prices=[IngredientPrice.from_dict(price) for price in data['prices']],
            timestamp=datetime.fromisoformat(data['timestamp']),
            location=data['location']
        )


class GroceryPriceAPIError(Exception):
    """Custom exception for grocery price API errors."""
    pass


class GroceryPriceAPI:
    """
    Grocery Price API integration with multiple providers and caching.
    
    This class provides methods to lookup ingredient prices, check availability,
    and perform location-based queries with automatic caching and fallback strategies.
    """
    
    def __init__(self, 
                 kroger_client_id: Optional[str] = None,
                 kroger_client_secret: Optional[str] = None,
                 instacart_api_key: Optional[str] = None,
                 cache_dir: str = "cache",
                 cache_duration_hours: int = 24,
                 max_retries: int = 3,
                 request_timeout: int = 30):
        """
        Initialize the Grocery Price API client.
        
        Args:
            kroger_client_id: Kroger API client ID
            kroger_client_secret: Kroger API client secret
            instacart_api_key: Instacart API key
            cache_dir: Directory to store cached data
            cache_duration_hours: How long to cache data (hours)
            max_retries: Maximum number of retry attempts
            request_timeout: Request timeout in seconds
        """
        # API credentials
        self.kroger_client_id = kroger_client_id or os.getenv('KROGER_CLIENT_ID')
        self.kroger_client_secret = kroger_client_secret or os.getenv('KROGER_CLIENT_SECRET')
        self.instacart_api_key = instacart_api_key or os.getenv('INSTACART_API_KEY')
        
        # Configuration
        self.cache_duration_hours = cache_duration_hours
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        
        # Set up caching
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.price_cache_file = self.cache_dir / "price_cache.json"
        self.store_cache_file = self.cache_dir / "store_cache.json"
        
        # Load existing caches
        self._price_cache = self._load_price_cache()
        self._store_cache = self._load_store_cache()
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Smart-Recipe-Meal-Planner/1.0'
        })
        
        # Kroger API endpoints
        self.kroger_base_url = "https://api.kroger.com/v1"
        self.kroger_token = None
        self.kroger_token_expires = None
        
        # Initialize Kroger authentication if credentials available
        if self.kroger_client_id and self.kroger_client_secret:
            self._authenticate_kroger()
    
    def _load_price_cache(self) -> Dict[str, CachedPriceData]:
        """Load price cache from file."""
        if not self.price_cache_file.exists():
            return {}
        
        try:
            with open(self.price_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            price_cache = {}
            for key, data in cache_data.items():
                try:
                    price_cache[key] = CachedPriceData.from_dict(data)
                except Exception as e:
                    logger.warning(f"Failed to load cached price data for {key}: {e}")
            
            return price_cache
        except Exception as e:
            logger.error(f"Failed to load price cache: {e}")
            return {}
    
    def _load_store_cache(self) -> Dict[str, List[StoreLocation]]:
        """Load store cache from file."""
        if not self.store_cache_file.exists():
            return {}
        
        try:
            with open(self.store_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            store_cache = {}
            for location, stores_data in cache_data.items():
                try:
                    store_cache[location] = [StoreLocation.from_dict(store) for store in stores_data]
                except Exception as e:
                    logger.warning(f"Failed to load cached store data for {location}: {e}")
            
            return store_cache
        except Exception as e:
            logger.error(f"Failed to load store cache: {e}")
            return {}
    
    def _save_price_cache(self):
        """Save price cache to file."""
        try:
            cache_data = {}
            for key, cached_data in self._price_cache.items():
                if not cached_data.is_expired(self.cache_duration_hours):
                    cache_data[key] = cached_data.to_dict()
            
            with open(self.price_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save price cache: {e}")
    
    def _save_store_cache(self):
        """Save store cache to file."""
        try:
            cache_data = {}
            for location, stores in self._store_cache.items():
                cache_data[location] = [store.to_dict() for store in stores]
            
            with open(self.store_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save store cache: {e}")
    
    def _generate_cache_key(self, ingredient_name: str, location: str) -> str:
        """Generate a cache key for price data."""
        key_string = f"{ingredient_name.lower().strip()}_{location.lower().strip()}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _make_request(self, url: str, headers: Dict[str, str] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            url: Request URL
            headers: Additional headers
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            GroceryPriceAPIError: If request fails after all retries
        """
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        
        # Merge headers
        request_headers = self.session.headers.copy()
        request_headers.update(headers)
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url, 
                    headers=request_headers,
                    params=params, 
                    timeout=self.request_timeout
                )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise GroceryPriceAPIError(f"Failed to make request after {self.max_retries} attempts: {e}")
                
                # Exponential backoff
                time.sleep(2 ** attempt)
    
    def _authenticate_kroger(self):
        """Authenticate with Kroger API and get access token."""
        try:
            auth_url = "https://api.kroger.com/v1/connect/oauth2/token"
            
            auth_data = {
                'grant_type': 'client_credentials',
                'scope': 'product.compact'
            }
            
            auth_headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = self.session.post(
                auth_url,
                data=auth_data,
                headers=auth_headers,
                auth=(self.kroger_client_id, self.kroger_client_secret),
                timeout=self.request_timeout
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self.kroger_token = token_data['access_token']
            # Token expires in seconds, convert to datetime
            expires_in = token_data.get('expires_in', 3600)
            self.kroger_token_expires = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Successfully authenticated with Kroger API")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Kroger API: {e}")
            self.kroger_token = None
            self.kroger_token_expires = None
    
    def _is_kroger_token_valid(self) -> bool:
        """Check if Kroger token is valid and not expired."""
        return (self.kroger_token is not None and 
                self.kroger_token_expires is not None and 
                datetime.now() < self.kroger_token_expires)
    
    def _search_kroger_products(self, ingredient_name: str, location_id: str = None) -> List[IngredientPrice]:
        """
        Search for products using Kroger API.
        
        Args:
            ingredient_name: Name of the ingredient to search
            location_id: Kroger location ID for pricing
            
        Returns:
            List of ingredient prices
        """
        if not self._is_kroger_token_valid():
            self._authenticate_kroger()
        
        if not self.kroger_token:
            raise GroceryPriceAPIError("Kroger authentication failed")
        
        try:
            search_url = f"{self.kroger_base_url}/products"
            
            headers = {
                'Authorization': f'Bearer {self.kroger_token}'
            }
            
            params = {
                'filter.term': ingredient_name,
                'filter.limit': 10
            }
            
            if location_id:
                params['filter.locationId'] = location_id
            
            response_data = self._make_request(search_url, headers=headers, params=params)
            
            prices = []
            products = response_data.get('data', [])
            
            for product in products:
                # Extract price information
                price_info = product.get('items', [{}])[0].get('price', {})
                regular_price = price_info.get('regular', 0)
                promo_price = price_info.get('promo', regular_price)
                
                # Use the lower price (promo if available)
                price = promo_price if promo_price < regular_price else regular_price
                
                if price > 0:  # Only include items with valid prices
                    ingredient_price = IngredientPrice(
                        ingredient_name=ingredient_name,
                        price=price,
                        unit=product.get('items', [{}])[0].get('size', 'each'),
                        store_name="Kroger",
                        brand=product.get('brand', {}).get('name'),
                        size=product.get('items', [{}])[0].get('size'),
                        availability=True,
                        location=location_id
                    )
                    prices.append(ingredient_price)
            
            return prices
            
        except Exception as e:
            logger.error(f"Failed to search Kroger products for {ingredient_name}: {e}")
            return []
    
    def _get_fallback_prices(self, ingredient_name: str, location: str) -> List[IngredientPrice]:
        """
        Fallback strategy for when APIs fail.
        
        This provides estimated prices based on common ingredient categories.
        """
        logger.warning(f"Using fallback price data for: {ingredient_name}")
        
        # Basic fallback price estimates (USD per common unit)
        fallback_prices = {
            # Proteins (per lb)
            'chicken': 3.99,
            'beef': 6.99,
            'pork': 4.49,
            'fish': 8.99,
            'salmon': 12.99,
            'eggs': 2.49,  # per dozen
            
            # Dairy (per unit)
            'milk': 3.49,  # per gallon
            'cheese': 4.99,  # per lb
            'butter': 4.29,  # per lb
            'yogurt': 1.29,  # per container
            
            # Grains (per lb)
            'rice': 1.99,
            'pasta': 1.49,
            'bread': 2.99,  # per loaf
            'flour': 2.49,
            
            # Vegetables (per lb)
            'broccoli': 2.49,
            'carrot': 1.29,
            'onion': 1.49,
            'potato': 1.99,
            'tomato': 2.99,
            'spinach': 3.49,
            'lettuce': 1.99,  # per head
            
            # Fruits (per lb)
            'apple': 1.99,
            'banana': 0.79,
            'orange': 1.49,
            'strawberry': 3.99,
            'grape': 2.99,
            
            # Pantry items
            'oil': 3.99,  # per bottle
            'salt': 0.99,  # per container
            'sugar': 2.49,  # per lb
            'pepper': 2.99,  # per container
        }
        
        # Find best match
        ingredient_lower = ingredient_name.lower()
        price = None
        unit = "lb"
        
        for key, base_price in fallback_prices.items():
            if key in ingredient_lower:
                price = base_price
                if key in ['eggs']:
                    unit = "dozen"
                elif key in ['milk']:
                    unit = "gallon"
                elif key in ['bread', 'lettuce']:
                    unit = "each"
                elif key in ['oil', 'salt', 'pepper']:
                    unit = "container"
                break
        
        # Use default if no match found
        if price is None:
            price = 2.99
            unit = "lb"
        
        # Add some variation for different stores
        stores = [
            ("Kroger", 1.0),
            ("Walmart", 0.9),
            ("Safeway", 1.1),
            ("Whole Foods", 1.3),
            ("Target", 0.95)
        ]
        
        prices = []
        for store_name, multiplier in stores:
            adjusted_price = price * multiplier
            ingredient_price = IngredientPrice(
                ingredient_name=ingredient_name,
                price=adjusted_price,
                unit=unit,
                store_name=store_name,
                availability=True,
                location=location
            )
            prices.append(ingredient_price)
        
        return prices
    
    def get_ingredient_prices(self, ingredient_name: str, location: str = "default") -> List[IngredientPrice]:
        """
        Get price information for an ingredient.
        
        Args:
            ingredient_name: Name of the ingredient
            location: Location for price lookup (zip code, city, etc.)
            
        Returns:
            List of ingredient prices from different sources
        """
        # Check cache first
        cache_key = self._generate_cache_key(ingredient_name, location)
        if cache_key in self._price_cache:
            cached_data = self._price_cache[cache_key]
            if not cached_data.is_expired(self.cache_duration_hours):
                logger.debug(f"Using cached price data for: {ingredient_name}")
                return cached_data.prices
            else:
                # Remove expired cache entry
                del self._price_cache[cache_key]
        
        prices = []
        
        try:
            # Try Kroger API if available
            if self.kroger_client_id and self.kroger_client_secret:
                kroger_prices = self._search_kroger_products(ingredient_name, location)
                prices.extend(kroger_prices)
            
            # Try other APIs here (Instacart, etc.)
            # TODO: Implement additional API integrations
            
            # If no prices found, use fallback
            if not prices:
                prices = self._get_fallback_prices(ingredient_name, location)
            
            # Cache the results
            cached_data = CachedPriceData(
                prices=prices,
                timestamp=datetime.now(),
                location=location
            )
            self._price_cache[cache_key] = cached_data
            self._save_price_cache()
            
            logger.info(f"Retrieved {len(prices)} price options for {ingredient_name}")
            return prices
            
        except Exception as e:
            logger.error(f"Failed to get prices for {ingredient_name}: {e}")
            # Return fallback prices
            return self._get_fallback_prices(ingredient_name, location)
    
    def check_ingredient_availability(self, ingredient_name: str, location: str = "default") -> bool:
        """
        Check if an ingredient is available in the specified location.
        
        Args:
            ingredient_name: Name of the ingredient
            location: Location to check availability
            
        Returns:
            True if ingredient is available, False otherwise
        """
        try:
            prices = self.get_ingredient_prices(ingredient_name, location)
            return any(price.availability for price in prices)
        except Exception as e:
            logger.error(f"Failed to check availability for {ingredient_name}: {e}")
            return True  # Assume available if check fails
    
    def get_cheapest_price(self, ingredient_name: str, location: str = "default") -> Optional[IngredientPrice]:
        """
        Get the cheapest price for an ingredient.
        
        Args:
            ingredient_name: Name of the ingredient
            location: Location for price lookup
            
        Returns:
            IngredientPrice with the lowest price, or None if not found
        """
        prices = self.get_ingredient_prices(ingredient_name, location)
        if not prices:
            return None
        
        # Find the cheapest available option
        available_prices = [price for price in prices if price.availability]
        if not available_prices:
            return None
        
        return min(available_prices, key=lambda p: p.price)
    
    def batch_get_prices(self, ingredients: List[str], location: str = "default") -> Dict[str, List[IngredientPrice]]:
        """
        Get prices for multiple ingredients efficiently.
        
        Args:
            ingredients: List of ingredient names
            location: Location for price lookup
            
        Returns:
            Dictionary mapping ingredient names to price lists
        """
        results = {}
        
        for ingredient in ingredients:
            try:
                prices = self.get_ingredient_prices(ingredient, location)
                results[ingredient] = prices
            except Exception as e:
                logger.error(f"Failed to get prices for {ingredient}: {e}")
                # Continue with other ingredients
                continue
        
        return results
    
    def find_ingredient_substitutes(self, ingredient_name: str, location: str = "default") -> List[IngredientPrice]:
        """
        Find substitute ingredients with similar properties.
        
        Args:
            ingredient_name: Original ingredient name
            location: Location for price lookup
            
        Returns:
            List of substitute ingredient prices
        """
        # Common ingredient substitutions
        substitutions = {
            'chicken breast': ['chicken thigh', 'turkey breast', 'pork tenderloin'],
            'ground beef': ['ground turkey', 'ground chicken', 'plant-based ground'],
            'butter': ['margarine', 'coconut oil', 'olive oil'],
            'milk': ['almond milk', 'soy milk', 'oat milk'],
            'eggs': ['egg substitute', 'flax eggs', 'applesauce'],
            'white rice': ['brown rice', 'quinoa', 'cauliflower rice'],
            'pasta': ['zucchini noodles', 'shirataki noodles', 'whole wheat pasta'],
            'sugar': ['honey', 'maple syrup', 'stevia'],
        }
        
        ingredient_lower = ingredient_name.lower()
        substitutes = []
        
        # Find substitutions
        for original, subs in substitutions.items():
            if original in ingredient_lower:
                for substitute in subs:
                    try:
                        sub_prices = self.get_ingredient_prices(substitute, location)
                        substitutes.extend(sub_prices)
                    except Exception as e:
                        logger.warning(f"Failed to get prices for substitute {substitute}: {e}")
                break
        
        return substitutes
    
    def clear_cache(self):
        """Clear all cached data."""
        self._price_cache.clear()
        self._store_cache.clear()
        
        # Remove cache files
        if self.price_cache_file.exists():
            self.price_cache_file.unlink()
        if self.store_cache_file.exists():
            self.store_cache_file.unlink()
        
        logger.info("Grocery price API cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        price_count = len(self._price_cache)
        store_count = len(self._store_cache)
        
        # Count expired entries
        expired_prices = sum(
            1 for cached_data in self._price_cache.values()
            if cached_data.is_expired(self.cache_duration_hours)
        )
        
        return {
            'price_cache_entries': price_count,
            'store_cache_entries': store_count,
            'expired_price_entries': expired_prices,
            'cache_duration_hours': self.cache_duration_hours
        }
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if hasattr(self, 'session'):
            self.session.close()


# Convenience functions for quick price lookup
def get_ingredient_price(ingredient_name: str, location: str = "default") -> Optional[IngredientPrice]:
    """
    Quick function to get the cheapest price for an ingredient.
    
    Args:
        ingredient_name: Name of the ingredient
        location: Location for price lookup
        
    Returns:
        IngredientPrice with the lowest price, or None if not found
    """
    api = GroceryPriceAPI()
    return api.get_cheapest_price(ingredient_name, location)


def check_availability(ingredient_name: str, location: str = "default") -> bool:
    """
    Quick function to check ingredient availability.
    
    Args:
        ingredient_name: Name of the ingredient
        location: Location to check availability
        
    Returns:
        True if ingredient is available, False otherwise
    """
    api = GroceryPriceAPI()
    return api.check_ingredient_availability(ingredient_name, location)
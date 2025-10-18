"""
Error Handling and Recovery System for the Smart Recipe & Meal Planning System.

This module implements comprehensive error handling, fallback strategies, and graceful
degradation for API failures, agent failures, and partial results scenarios.
"""

from typing import Dict, List, Optional, Any, Callable, Union
import logging
import time
import traceback
from functools import wraps
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for classification and handling."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for specific handling strategies."""
    API_FAILURE = "api_failure"
    AGENT_FAILURE = "agent_failure"
    DATA_VALIDATION = "data_validation"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    RESOURCE_ERROR = "resource_error"
    CONFIGURATION_ERROR = "configuration_error"


@dataclass
class ErrorContext:
    """Context information for error handling and recovery."""
    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: datetime
    component: str
    retry_count: int = 0
    max_retries: int = 3
    fallback_available: bool = False
    user_impact: str = ""
    recovery_actions: List[str] = None
    
    def __post_init__(self):
        if self.recovery_actions is None:
            self.recovery_actions = []


class MealPlanningError(Exception):
    """Base exception for meal planning system errors."""
    
    def __init__(self, message: str, context: ErrorContext = None):
        super().__init__(message)
        self.context = context or ErrorContext(
            error_type=self.__class__.__name__,
            error_message=message,
            category=ErrorCategory.AGENT_FAILURE,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            component="unknown"
        )


class APIFailureError(MealPlanningError):
    """Exception for external API failures."""
    
    def __init__(self, api_name: str, message: str, status_code: int = None):
        context = ErrorContext(
            error_type="APIFailureError",
            error_message=f"{api_name}: {message}",
            category=ErrorCategory.API_FAILURE,
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(),
            component=api_name,
            fallback_available=True,
            user_impact="May use cached or default data"
        )
        super().__init__(message, context)
        self.api_name = api_name
        self.status_code = status_code


class AgentExecutionError(MealPlanningError):
    """Exception for agent execution failures."""
    
    def __init__(self, agent_name: str, message: str, task_name: str = None):
        context = ErrorContext(
            error_type="AgentExecutionError",
            error_message=f"{agent_name}: {message}",
            category=ErrorCategory.AGENT_FAILURE,
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(),
            component=agent_name,
            fallback_available=True,
            user_impact="May use simplified or default recommendations"
        )
        super().__init__(message, context)
        self.agent_name = agent_name
        self.task_name = task_name


class DataValidationError(MealPlanningError):
    """Exception for data validation failures."""
    
    def __init__(self, field_name: str, message: str, value: Any = None):
        context = ErrorContext(
            error_type="DataValidationError",
            error_message=f"{field_name}: {message}",
            category=ErrorCategory.DATA_VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            component="data_validation",
            user_impact="May require user input correction"
        )
        super().__init__(message, context)
        self.field_name = field_name
        self.value = value


class ErrorRecoveryManager:
    """Manages error recovery strategies and fallback mechanisms."""
    
    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.fallback_strategies = self._initialize_fallback_strategies()
        self.retry_strategies = self._initialize_retry_strategies()
        
    def _initialize_fallback_strategies(self) -> Dict[ErrorCategory, Callable]:
        """Initialize fallback strategies for different error categories."""
        return {
            ErrorCategory.API_FAILURE: self._handle_api_failure,
            ErrorCategory.AGENT_FAILURE: self._handle_agent_failure,
            ErrorCategory.DATA_VALIDATION: self._handle_data_validation,
            ErrorCategory.NETWORK_ERROR: self._handle_network_error,
            ErrorCategory.TIMEOUT_ERROR: self._handle_timeout_error,
            ErrorCategory.RESOURCE_ERROR: self._handle_resource_error,
            ErrorCategory.CONFIGURATION_ERROR: self._handle_configuration_error
        }
    
    def _initialize_retry_strategies(self) -> Dict[ErrorCategory, Dict[str, Any]]:
        """Initialize retry strategies with exponential backoff."""
        return {
            ErrorCategory.API_FAILURE: {
                'max_retries': 3,
                'base_delay': 1.0,
                'backoff_factor': 2.0,
                'max_delay': 30.0
            },
            ErrorCategory.NETWORK_ERROR: {
                'max_retries': 5,
                'base_delay': 0.5,
                'backoff_factor': 1.5,
                'max_delay': 10.0
            },
            ErrorCategory.TIMEOUT_ERROR: {
                'max_retries': 2,
                'base_delay': 2.0,
                'backoff_factor': 2.0,
                'max_delay': 60.0
            },
            ErrorCategory.AGENT_FAILURE: {
                'max_retries': 2,
                'base_delay': 1.0,
                'backoff_factor': 1.0,
                'max_delay': 5.0
            }
        }
    
    def handle_error(self, error: Exception, context: ErrorContext = None) -> Any:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: The exception that occurred
            context: Additional error context
            
        Returns:
            Recovery result or raises if unrecoverable
        """
        try:
            # Create context if not provided
            if context is None:
                context = self._create_error_context(error)
            
            # Log error
            self._log_error(error, context)
            
            # Add to error history
            self.error_history.append(context)
            
            # Determine if retry is appropriate
            if self._should_retry(context):
                return self._attempt_retry(error, context)
            
            # Apply fallback strategy
            if context.category in self.fallback_strategies:
                fallback_handler = self.fallback_strategies[context.category]
                return fallback_handler(error, context)
            
            # If no specific handler, use generic fallback
            return self._generic_fallback(error, context)
            
        except Exception as recovery_error:
            logger.critical(f"Error recovery failed: {recovery_error}")
            raise error  # Re-raise original error if recovery fails
    
    def _create_error_context(self, error: Exception) -> ErrorContext:
        """Create error context from exception."""
        if isinstance(error, MealPlanningError) and error.context:
            return error.context
        
        # Determine category based on error type
        category = ErrorCategory.AGENT_FAILURE
        severity = ErrorSeverity.MEDIUM
        
        if "api" in str(error).lower() or "request" in str(error).lower():
            category = ErrorCategory.API_FAILURE
            severity = ErrorSeverity.HIGH
        elif "timeout" in str(error).lower():
            category = ErrorCategory.TIMEOUT_ERROR
            severity = ErrorSeverity.MEDIUM
        elif "network" in str(error).lower() or "connection" in str(error).lower():
            category = ErrorCategory.NETWORK_ERROR
            severity = ErrorSeverity.HIGH
        
        return ErrorContext(
            error_type=type(error).__name__,
            error_message=str(error),
            category=category,
            severity=severity,
            timestamp=datetime.now(),
            component="unknown"
        )
    
    def _should_retry(self, context: ErrorContext) -> bool:
        """Determine if error should be retried."""
        if context.retry_count >= context.max_retries:
            return False
        
        # Don't retry validation errors
        if context.category == ErrorCategory.DATA_VALIDATION:
            return False
        
        # Don't retry configuration errors
        if context.category == ErrorCategory.CONFIGURATION_ERROR:
            return False
        
        # Retry network and API errors
        return context.category in [
            ErrorCategory.API_FAILURE,
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.TIMEOUT_ERROR,
            ErrorCategory.AGENT_FAILURE
        ]
    
    def _attempt_retry(self, error: Exception, context: ErrorContext) -> Any:
        """Attempt to retry the failed operation with exponential backoff."""
        retry_config = self.retry_strategies.get(context.category, {})
        
        base_delay = retry_config.get('base_delay', 1.0)
        backoff_factor = retry_config.get('backoff_factor', 2.0)
        max_delay = retry_config.get('max_delay', 30.0)
        
        # Calculate delay with exponential backoff
        delay = min(base_delay * (backoff_factor ** context.retry_count), max_delay)
        
        logger.info(f"Retrying operation after {delay:.1f}s (attempt {context.retry_count + 1})")
        time.sleep(delay)
        
        context.retry_count += 1
        
        # Re-raise error to trigger retry in calling code
        raise error
    
    def _handle_api_failure(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Handle API failure with cached or default data."""
        logger.warning(f"API failure for {context.component}, using fallback data")
        
        # Return fallback data based on component
        if "nutrition" in context.component.lower():
            return self._get_nutrition_fallback()
        elif "grocery" in context.component.lower() or "price" in context.component.lower():
            return self._get_pricing_fallback()
        else:
            return self._get_generic_api_fallback()
    
    def _handle_agent_failure(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Handle agent execution failure with simplified logic."""
        logger.warning(f"Agent failure for {context.component}, using simplified approach")
        
        # Return simplified results based on agent type
        if "nutritionist" in context.component.lower():
            return self._get_nutritionist_fallback()
        elif "recipe" in context.component.lower():
            return self._get_recipe_fallback()
        elif "cost" in context.component.lower():
            return self._get_cost_fallback()
        elif "planner" in context.component.lower():
            return self._get_planner_fallback()
        elif "validator" in context.component.lower():
            return self._get_validator_fallback()
        else:
            return self._get_generic_agent_fallback()
    
    def _handle_data_validation(self, error: Exception, context: ErrorContext) -> None:
        """Handle data validation errors by requesting user correction."""
        logger.error(f"Data validation error: {context.error_message}")
        
        # For data validation errors, we typically need user intervention
        # This would trigger a user prompt in the UI
        raise DataValidationError(
            field_name=getattr(error, 'field_name', 'unknown'),
            message=f"Please correct the following: {context.error_message}"
        )
    
    def _handle_network_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Handle network errors with cached data."""
        logger.warning("Network error detected, using cached data if available")
        return self._get_cached_data_fallback()
    
    def _handle_timeout_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Handle timeout errors with partial results."""
        logger.warning("Timeout error detected, using partial results")
        return self._get_partial_results_fallback()
    
    def _handle_resource_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Handle resource errors with simplified processing."""
        logger.warning("Resource error detected, using simplified processing")
        return self._get_simplified_processing_fallback()
    
    def _handle_configuration_error(self, error: Exception, context: ErrorContext) -> None:
        """Handle configuration errors by alerting for manual intervention."""
        logger.critical(f"Configuration error: {context.error_message}")
        raise error  # Configuration errors require manual intervention
    
    def _generic_fallback(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Generic fallback for unhandled error categories."""
        logger.warning(f"Using generic fallback for {context.category}")
        return {
            'status': 'fallback',
            'message': 'Using default values due to system error',
            'error_context': context.error_message,
            'recommendations': [
                'System encountered an error but continued with default values',
                'Please review results carefully',
                'Consider retrying the operation later'
            ]
        }
    
    # Fallback data providers
    def _get_nutrition_fallback(self) -> Dict[str, Any]:
        """Provide fallback nutrition data."""
        return {
            'daily_targets': {
                'calories': 2000,
                'protein': 150,
                'carbohydrates': 250,
                'fat': 67,
                'fiber': 25,
                'sodium': 2300
            },
            'source': 'fallback_defaults',
            'message': 'Using standard nutritional guidelines'
        }
    
    def _get_pricing_fallback(self) -> Dict[str, Any]:
        """Provide fallback pricing data."""
        return {
            'pricing_data': {
                'average_cost_per_meal': 8.50,
                'price_inflation_factor': 1.1
            },
            'source': 'fallback_estimates',
            'message': 'Using estimated pricing data'
        }
    
    def _get_nutritionist_fallback(self) -> Dict[str, Any]:
        """Provide fallback nutritionist analysis."""
        return {
            'daily_targets': self._get_nutrition_fallback()['daily_targets'],
            'guidelines': [
                'Eat a balanced diet with variety',
                'Include fruits and vegetables daily',
                'Stay hydrated with 8-10 glasses of water',
                'Limit processed foods and added sugars'
            ],
            'source': 'fallback_guidelines'
        }
    
    def _get_recipe_fallback(self) -> Dict[str, Any]:
        """Provide fallback recipe suggestions."""
        return {
            'recipes': [
                {
                    'name': 'Simple Oatmeal Bowl',
                    'meal_type': 'breakfast',
                    'ingredients': ['oats', 'milk', 'banana', 'honey'],
                    'instructions': ['Cook oats', 'Add toppings', 'Serve warm']
                },
                {
                    'name': 'Basic Salad',
                    'meal_type': 'lunch',
                    'ingredients': ['mixed greens', 'tomato', 'cucumber', 'olive oil'],
                    'instructions': ['Wash vegetables', 'Combine in bowl', 'Add dressing']
                },
                {
                    'name': 'Grilled Chicken',
                    'meal_type': 'dinner',
                    'ingredients': ['chicken breast', 'vegetables', 'rice'],
                    'instructions': ['Season chicken', 'Grill until done', 'Serve with sides']
                }
            ],
            'source': 'fallback_recipes'
        }
    
    def _get_cost_fallback(self) -> Dict[str, Any]:
        """Provide fallback cost analysis."""
        return {
            'total_weekly_cost': 60.00,
            'budget_status': 'estimated',
            'cost_per_meal': 8.50,
            'source': 'fallback_estimates'
        }
    
    def _get_planner_fallback(self) -> Dict[str, Any]:
        """Provide fallback meal plan."""
        return {
            'daily_plans': [
                {'day': i, 'breakfast': 'Simple meal', 'lunch': 'Basic meal', 'dinner': 'Standard meal'}
                for i in range(7)
            ],
            'shopping_list': ['basic ingredients'],
            'source': 'fallback_plan'
        }
    
    def _get_validator_fallback(self) -> Dict[str, Any]:
        """Provide fallback health validation."""
        return {
            'overall_score': 75,
            'approval_status': 'approved_with_caution',
            'recommendations': [
                'Review meal plan manually',
                'Consult healthcare provider if needed',
                'Monitor nutritional balance'
            ],
            'source': 'fallback_validation'
        }
    
    def _get_generic_api_fallback(self) -> Dict[str, Any]:
        """Generic API fallback data."""
        return {
            'data': 'unavailable',
            'source': 'fallback',
            'message': 'External service temporarily unavailable'
        }
    
    def _get_cached_data_fallback(self) -> Dict[str, Any]:
        """Cached data fallback."""
        return {
            'source': 'cached_data',
            'message': 'Using previously cached information',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_partial_results_fallback(self) -> Dict[str, Any]:
        """Partial results fallback."""
        return {
            'status': 'partial',
            'message': 'Operation completed with partial results',
            'completeness': 'limited'
        }
    
    def _get_simplified_processing_fallback(self) -> Dict[str, Any]:
        """Simplified processing fallback."""
        return {
            'processing_mode': 'simplified',
            'message': 'Using reduced complexity processing',
            'quality': 'basic'
        }
    
    def _get_generic_agent_fallback(self) -> Dict[str, Any]:
        """Generic agent fallback."""
        return {
            'result': 'basic_output',
            'source': 'fallback_agent',
            'message': 'Agent used simplified processing'
        }
    
    def _log_error(self, error: Exception, context: ErrorContext):
        """Log error with appropriate level based on severity."""
        error_msg = f"{context.component}: {context.error_message}"
        
        if context.severity == ErrorSeverity.CRITICAL:
            logger.critical(error_msg, exc_info=True)
        elif context.severity == ErrorSeverity.HIGH:
            logger.error(error_msg, exc_info=True)
        elif context.severity == ErrorSeverity.MEDIUM:
            logger.warning(error_msg)
        else:
            logger.info(error_msg)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered during execution."""
        if not self.error_history:
            return {'status': 'no_errors', 'total_errors': 0}
        
        error_counts = {}
        for error in self.error_history:
            category = error.category.value
            error_counts[category] = error_counts.get(category, 0) + 1
        
        return {
            'status': 'errors_encountered',
            'total_errors': len(self.error_history),
            'error_breakdown': error_counts,
            'latest_error': self.error_history[-1].error_message if self.error_history else None
        }


# Decorator for automatic error handling
def with_error_handling(
    component: str,
    category: ErrorCategory = ErrorCategory.AGENT_FAILURE,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    fallback_result: Any = None
):
    """
    Decorator to add automatic error handling to functions.
    
    Args:
        component: Component name for error context
        category: Error category for handling strategy
        severity: Error severity level
        fallback_result: Default result to return on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            error_manager = ErrorRecoveryManager()
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    category=category,
                    severity=severity,
                    timestamp=datetime.now(),
                    component=component
                )
                
                try:
                    return error_manager.handle_error(e, context)
                except Exception:
                    # If error handling fails, return fallback
                    if fallback_result is not None:
                        logger.warning(f"Returning fallback result for {component}")
                        return fallback_result
                    raise
        
        return wrapper
    return decorator


# Global error recovery manager instance
global_error_manager = ErrorRecoveryManager()
"""
Workflow orchestration module for the Smart Recipe & Meal Planning System.

This module provides the CrewAI workflow orchestration with task definitions,
crew configuration, and comprehensive error handling for the meal planning system.
"""

from .crew import MealPlanningCrew, execute_meal_planning_workflow
from .tasks import (
    create_nutritional_analysis_task,
    create_ingredient_sourcing_task,
    create_recipe_generation_task,
    create_cost_analysis_task,
    create_meal_planning_task,
    create_health_validation_task,
    get_task_execution_order,
    validate_task_dependencies,
    TASK_DEPENDENCIES
)
from .error_handling import (
    ErrorRecoveryManager,
    MealPlanningError,
    APIFailureError,
    AgentExecutionError,
    DataValidationError,
    ErrorCategory,
    ErrorSeverity,
    with_error_handling,
    global_error_manager
)

__all__ = [
    # Main workflow classes
    'MealPlanningCrew',
    'execute_meal_planning_workflow',
    
    # Task creation functions
    'create_nutritional_analysis_task',
    'create_ingredient_sourcing_task',
    'create_recipe_generation_task',
    'create_cost_analysis_task',
    'create_meal_planning_task',
    'create_health_validation_task',
    
    # Task management utilities
    'get_task_execution_order',
    'validate_task_dependencies',
    'TASK_DEPENDENCIES',
    
    # Error handling
    'ErrorRecoveryManager',
    'MealPlanningError',
    'APIFailureError',
    'AgentExecutionError',
    'DataValidationError',
    'ErrorCategory',
    'ErrorSeverity',
    'with_error_handling',
    'global_error_manager'
]
"""
User interface components for the Smart Recipe & Meal Planning System.

This package contains command-line interface components for user input processing,
validation, meal plan execution workflow, and comprehensive output generation.
"""

from .user_input import UserInputProcessor, InputValidator, UserPrompts
from .execution_workflow import (
    MealPlanExecutionWorkflow, 
    ProgressTracker, 
    UserFeedbackManager,
    ExecutionOptimizer,
    execute_meal_plan_with_monitoring
)
from .output_generator import (
    ComprehensiveReportGenerator,
    EnhancedShoppingListFormatter,
    NutritionalSummaryFormatter,
    CostBreakdownFormatter
)

__all__ = [
    # User Input Processing
    "UserInputProcessor",
    "InputValidator", 
    "UserPrompts",
    
    # Execution Workflow
    "MealPlanExecutionWorkflow",
    "ProgressTracker",
    "UserFeedbackManager", 
    "ExecutionOptimizer",
    "execute_meal_plan_with_monitoring",
    
    # Output Generation
    "ComprehensiveReportGenerator",
    "EnhancedShoppingListFormatter",
    "NutritionalSummaryFormatter",
    "CostBreakdownFormatter"
]
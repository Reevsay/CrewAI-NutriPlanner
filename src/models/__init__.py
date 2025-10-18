"""
Data models for the Smart Recipe & Meal Planning System.

This package contains all data models, validation logic, and formatting utilities
for user profiles, recipes, meal plans, and system outputs.
"""

from .user_profile import (
    UserProfile,
    PersonalInfo,
    DietaryPreferences,
    HealthGoals,
    BudgetConstraints,
    SchedulePreferences,
    MacroPreferences,
    ActivityLevel,
    Gender,
    GoalType,
    CookingSkillLevel,
    PriceSensitivity
)

from .recipe import (
    Recipe,
    Ingredient,
    WeeklyMealPlan,
    DailyMealPlan,
    ShoppingList,
    ShoppingListItem,
    NutritionalInfo,
    WeeklyNutritionalSummary,
    DifficultyLevel,
    MealType,
    Unit
)

from .formatters import (
    MarkdownReportGenerator,
    JSONSerializer,
    AgentDataExchange,
    CustomJSONEncoder
)

__all__ = [
    # User Profile Models
    "UserProfile",
    "PersonalInfo", 
    "DietaryPreferences",
    "HealthGoals",
    "BudgetConstraints",
    "SchedulePreferences",
    "MacroPreferences",
    
    # User Profile Enums
    "ActivityLevel",
    "Gender",
    "GoalType", 
    "CookingSkillLevel",
    "PriceSensitivity",
    
    # Recipe and Meal Plan Models
    "Recipe",
    "Ingredient",
    "WeeklyMealPlan",
    "DailyMealPlan", 
    "ShoppingList",
    "ShoppingListItem",
    "NutritionalInfo",
    "WeeklyNutritionalSummary",
    
    # Recipe Enums
    "DifficultyLevel",
    "MealType",
    "Unit",
    
    # Formatting Utilities
    "MarkdownReportGenerator",
    "JSONSerializer",
    "AgentDataExchange",
    "CustomJSONEncoder"
]
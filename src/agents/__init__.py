# CrewAI Agents Module

from .nutritionist_agent import (
    create_nutritionist_agent,
    create_nutritional_analysis_task,
    analyze_user_nutrition,
    NutritionalAnalysisOutput
)

from .recipe_creator_agent import (
    create_recipe_creator_agent,
    create_recipe_generation_task,
    generate_recipe,
    RecipeOutput
)

from .ingredient_sourcer_agent import (
    create_ingredient_sourcer_agent,
    create_ingredient_sourcing_task,
    research_ingredients,
    IngredientAvailabilityOutput
)

from .cost_calculator_agent import (
    create_cost_calculator_agent,
    create_cost_analysis_task,
    analyze_meal_plan_costs,
    CostAnalysisOutput
)

from .meal_planner_agent import (
    create_meal_planner_agent,
    create_meal_planning_task,
    create_weekly_meal_plan,
    MealPlanningOutput
)

from .health_validator_agent import (
    create_health_validator_agent,
    create_health_validation_task,
    validate_meal_plan_health,
    HealthValidationOutput
)

__all__ = [
    # Nutritionist Agent
    'create_nutritionist_agent',
    'create_nutritional_analysis_task',
    'analyze_user_nutrition',
    'NutritionalAnalysisOutput',
    
    # Recipe Creator Agent
    'create_recipe_creator_agent',
    'create_recipe_generation_task',
    'generate_recipe',
    'RecipeOutput',
    
    # Ingredient Sourcer Agent
    'create_ingredient_sourcer_agent',
    'create_ingredient_sourcing_task',
    'research_ingredients',
    'IngredientAvailabilityOutput',
    
    # Cost Calculator Agent
    'create_cost_calculator_agent',
    'create_cost_analysis_task',
    'analyze_meal_plan_costs',
    'CostAnalysisOutput',
    
    # Meal Planner Agent
    'create_meal_planner_agent',
    'create_meal_planning_task',
    'create_weekly_meal_plan',
    'MealPlanningOutput',
    
    # Health Validator Agent
    'create_health_validator_agent',
    'create_health_validation_task',
    'validate_meal_plan_health',
    'HealthValidationOutput'
]
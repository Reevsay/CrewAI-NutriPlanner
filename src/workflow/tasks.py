"""
CrewAI Task Definitions for the Smart Recipe & Meal Planning System.

This module defines all the CrewAI Task objects with specific goals, expected outputs,
and dependencies for the meal planning workflow orchestration.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import date
from crewai import Task

from ..agents.nutritionist_agent import create_nutritionist_agent
from ..agents.recipe_creator_agent import create_recipe_creator_agent
from ..agents.ingredient_sourcer_agent import create_ingredient_sourcer_agent
from ..agents.cost_calculator_agent import create_cost_calculator_agent
from ..agents.meal_planner_agent import create_meal_planner_agent
from ..agents.health_validator_agent import create_health_validator_agent

# Configure logging
logger = logging.getLogger(__name__)


def create_nutritional_analysis_task(user_profile_data: Dict[str, Any]) -> Task:
    """
    Create task for nutritional analysis by the Nutritionist Agent.
    
    Args:
        user_profile_data: User profile information for analysis
        
    Returns:
        CrewAI Task for nutritional analysis
    """
    task = Task(
        description=f"""
        Analyze the provided user profile to establish comprehensive nutritional requirements and guidelines.
        
        User Profile: {user_profile_data}
        
        Your analysis must include:
        1. Calculate Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE)
        2. Determine daily caloric needs based on health goals
        3. Calculate optimal macronutrient distribution (protein, carbs, fat)
        4. Establish micronutrient requirements (vitamins, minerals)
        5. Identify dietary restrictions and special considerations
        6. Provide specific nutritional guidelines for meal planning
        
        Use your tools to perform accurate calculations based on current nutritional science.
        Consider age, gender, weight, height, activity level, health goals, and dietary restrictions.
        """,
        expected_output="""
        Comprehensive nutritional analysis containing:
        - Daily caloric needs and metabolic calculations (BMR, TDEE)
        - Macronutrient targets (protein, carbohydrates, fat, fiber)
        - Micronutrient requirements with daily targets
        - Dietary guidelines and recommendations
        - Special considerations for restrictions and health goals
        
        Format as structured data that can be used by subsequent agents.
        """,
        agent=create_nutritionist_agent(),
        context=[],  # No dependencies - runs in parallel
        output_file="nutritional_analysis.json"
    )
    
    return task


def create_ingredient_sourcing_task(
    user_profile_data: Dict[str, Any],
    location: Optional[str] = None
) -> Task:
    """
    Create task for ingredient sourcing and availability research.
    
    Args:
        user_profile_data: User profile with budget and preferences
        location: User location for price lookup
        
    Returns:
        CrewAI Task for ingredient sourcing
    """
    budget_constraints = user_profile_data.get('budget_constraints', {})
    dietary_preferences = user_profile_data.get('dietary_preferences', {})
    
    task = Task(
        description=f"""
        Research ingredient availability, pricing, and alternatives based on user preferences and budget.
        
        Budget Constraints: {budget_constraints}
        Dietary Preferences: {dietary_preferences}
        Location: {location or 'General US market'}
        
        Your research must include:
        1. Current market prices for common ingredients
        2. Seasonal availability and pricing patterns
        3. Budget-friendly alternatives for expensive ingredients
        4. Store recommendations and shopping strategies
        5. Ingredient substitutions for dietary restrictions
        6. Cost optimization opportunities
        
        Focus on maintaining nutritional value while optimizing for cost and availability.
        """,
        expected_output="""
        Ingredient sourcing report containing:
        - Current price ranges for ingredient categories
        - Seasonal availability calendar and recommendations
        - Budget optimization strategies and alternatives
        - Shopping recommendations by store type
        - Substitution guide for dietary restrictions
        - Cost-saving tips and bulk buying opportunities
        
        Format as actionable sourcing data for recipe creation and meal planning.
        """,
        agent=create_ingredient_sourcer_agent(),
        context=[],  # No dependencies - runs in parallel
        output_file="ingredient_sourcing.json"
    )
    
    return task


def create_recipe_generation_task(
    nutritional_requirements: Dict[str, float],
    ingredient_availability: Dict[str, Any],
    meal_requirements: Dict[str, Any]
) -> Task:
    """
    Create task for recipe generation based on nutritional needs and ingredient availability.
    
    Args:
        nutritional_requirements: Daily nutritional targets from nutritionist
        ingredient_availability: Ingredient data from sourcing agent
        meal_requirements: Meal type and cooking preferences
        
    Returns:
        CrewAI Task for recipe generation
    """
    task = Task(
        description=f"""
        Generate custom recipes that meet nutritional requirements using available ingredients.
        
        Nutritional Requirements: {nutritional_requirements}
        Available Ingredients: {ingredient_availability.get('available_ingredients', [])}
        Budget Constraints: {ingredient_availability.get('budget_constraints', {})}
        Meal Requirements: {meal_requirements}
        
        Your recipe generation must:
        1. Meet specified nutritional targets for each meal type
        2. Use ingredients within budget and availability constraints
        3. Respect all dietary restrictions and preferences
        4. Match cooking skill level and time constraints
        5. Provide complete recipes with ingredients and instructions
        6. Calculate nutritional information per serving
        
        Create recipes for breakfast, lunch, dinner, and snacks as specified.
        Ensure variety and appeal while maintaining nutritional balance.
        """,
        expected_output="""
        Complete recipe collection containing:
        - Recipes for each required meal type (breakfast, lunch, dinner, snacks)
        - Detailed ingredient lists with quantities and alternatives
        - Step-by-step cooking instructions
        - Nutritional information per serving
        - Preparation and cooking times
        - Difficulty levels and cooking tips
        
        Format as structured recipe data ready for cost analysis and meal planning.
        """,
        agent=create_recipe_creator_agent(),
        context=["nutritional_analysis.json", "ingredient_sourcing.json"],
        output_file="generated_recipes.json"
    )
    
    return task


def create_cost_analysis_task(
    recipes: List[Dict[str, Any]],
    ingredient_pricing: Dict[str, Any],
    budget_constraints: Dict[str, Any]
) -> Task:
    """
    Create task for cost analysis and budget optimization.
    
    Args:
        recipes: Generated recipes from recipe creator
        ingredient_pricing: Pricing data from ingredient sourcer
        budget_constraints: User budget limitations
        
    Returns:
        CrewAI Task for cost analysis
    """
    task = Task(
        description=f"""
        Analyze costs for generated recipes and optimize within budget constraints.
        
        Recipes to Analyze: {len(recipes)} recipes
        Ingredient Pricing: {ingredient_pricing}
        Budget Constraints: {budget_constraints}
        
        Your cost analysis must:
        1. Calculate total cost for each recipe and per serving
        2. Analyze weekly meal plan costs and budget utilization
        3. Identify most expensive ingredients and cost drivers
        4. Provide budget optimization recommendations
        5. Suggest ingredient substitutions for cost savings
        6. Compare cost-effectiveness of different meal options
        
        Focus on maintaining nutritional value while optimizing costs.
        """,
        expected_output="""
        Comprehensive cost analysis containing:
        - Total weekly cost and daily breakdown
        - Cost per serving for each recipe
        - Budget utilization analysis and status
        - Most expensive ingredients and alternatives
        - Cost optimization recommendations
        - Budget allocation suggestions by meal type
        
        Format as actionable cost data for meal planning decisions.
        """,
        agent=create_cost_calculator_agent(),
        context=["generated_recipes.json", "ingredient_sourcing.json"],
        output_file="cost_analysis.json"
    )
    
    return task


def create_meal_planning_task(
    recipes: List[Dict[str, Any]],
    nutritional_targets: Dict[str, float],
    cost_analysis: Dict[str, Any],
    schedule_preferences: Dict[str, Any],
    week_start_date: str
) -> Task:
    """
    Create task for weekly meal planning and schedule organization.
    
    Args:
        recipes: Available recipes with cost analysis
        nutritional_targets: Daily nutritional requirements
        cost_analysis: Cost optimization recommendations
        schedule_preferences: User schedule and timing preferences
        week_start_date: Start date for meal plan
        
    Returns:
        CrewAI Task for meal planning
    """
    task = Task(
        description=f"""
        Create a comprehensive weekly meal plan organizing recipes into balanced schedules.
        
        Available Recipes: {len(recipes)} recipes
        Nutritional Targets: {nutritional_targets}
        Cost Analysis: Budget status and recommendations
        Schedule Preferences: {schedule_preferences}
        Week Starting: {week_start_date}
        
        Your meal planning must:
        1. Organize recipes into balanced weekly schedule
        2. Ensure nutritional targets are met across the week
        3. Generate organized shopping list by store sections
        4. Create meal prep instructions and timeline
        5. Provide food storage and safety recommendations
        6. Optimize for variety, nutrition, and practicality
        
        Consider user schedule, cooking skills, and time constraints.
        """,
        expected_output="""
        Complete weekly meal plan containing:
        - Day-by-day meal schedule with assigned recipes
        - Shopping list organized by store sections
        - Meal prep instructions and preparation timeline
        - Nutritional balance summary across the week
        - Storage recommendations and food safety guidelines
        - Implementation timeline and daily requirements
        
        Format as actionable meal plan ready for health validation.
        """,
        agent=create_meal_planner_agent(),
        context=["generated_recipes.json", "cost_analysis.json", "nutritional_analysis.json"],
        output_file="weekly_meal_plan.json"
    )
    
    return task


def create_health_validation_task(
    meal_plan: Dict[str, Any],
    user_profile: Dict[str, Any],
    nutritional_targets: Dict[str, float]
) -> Task:
    """
    Create task for health validation and final meal plan approval.
    
    Args:
        meal_plan: Complete weekly meal plan to validate
        user_profile: User health profile and restrictions
        nutritional_targets: Target nutritional values
        
    Returns:
        CrewAI Task for health validation
    """
    task = Task(
        description=f"""
        Conduct comprehensive health validation of the weekly meal plan for safety and optimization.
        
        Meal Plan: {len(meal_plan.get('daily_plans', []))} days of planned meals
        User Profile: Health goals, restrictions, and preferences
        Nutritional Targets: Required nutritional standards
        
        Your validation must:
        1. Assess nutritional adequacy against RDAs and user targets
        2. Verify strict compliance with dietary restrictions and allergies
        3. Provide health optimization recommendations
        4. Identify potential risks or nutritional concerns
        5. Recommend meal plan adjustments if needed
        6. Provide final approval status with reasoning
        
        Prioritize user health and safety in all assessments.
        """,
        expected_output="""
        Final health validation report containing:
        - Overall health score and nutritional adequacy assessment
        - Dietary compliance verification and violation alerts
        - Personalized health optimization recommendations
        - Risk assessment and monitoring suggestions
        - Required meal plan adjustments (if any)
        - Final approval status (approved/needs_revision/rejected)
        
        Format as professional nutritional assessment with clear action items.
        """,
        agent=create_health_validator_agent(),
        context=["weekly_meal_plan.json", "nutritional_analysis.json"],
        output_file="health_validation.json"
    )
    
    return task


# Task dependency mapping for workflow orchestration
TASK_DEPENDENCIES = {
    'nutritional_analysis': [],  # No dependencies - parallel execution
    'ingredient_sourcing': [],   # No dependencies - parallel execution
    'recipe_generation': ['nutritional_analysis', 'ingredient_sourcing'],
    'cost_analysis': ['recipe_generation', 'ingredient_sourcing'],
    'meal_planning': ['recipe_generation', 'cost_analysis', 'nutritional_analysis'],
    'health_validation': ['meal_planning', 'nutritional_analysis']
}


def get_task_execution_order() -> List[List[str]]:
    """
    Get the execution order for tasks based on dependencies.
    
    Returns:
        List of task groups that can be executed in parallel
    """
    return [
        ['nutritional_analysis', 'ingredient_sourcing'],  # Parallel phase 1
        ['recipe_generation'],                            # Sequential phase 1
        ['cost_analysis'],                               # Sequential phase 2
        ['meal_planning'],                               # Sequential phase 3
        ['health_validation']                            # Sequential phase 4
    ]


def validate_task_dependencies(tasks: Dict[str, Task]) -> bool:
    """
    Validate that all task dependencies are satisfied.
    
    Args:
        tasks: Dictionary of task name to Task object
        
    Returns:
        True if all dependencies are satisfied
    """
    for task_name, dependencies in TASK_DEPENDENCIES.items():
        if task_name in tasks:
            for dependency in dependencies:
                if dependency not in tasks:
                    logger.error(f"Task '{task_name}' depends on '{dependency}' which is not available")
                    return False
    
    return True
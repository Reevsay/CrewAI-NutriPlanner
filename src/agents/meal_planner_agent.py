"""
Meal Planner Agent for the Smart Recipe & Meal Planning System.

This module implements the Meal Planner Agent that organizes recipes into
balanced weekly schedules, generates shopping lists, and provides meal prep instructions.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import date, timedelta
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.recipe import (
    Recipe, WeeklyMealPlan, DailyMealPlan, ShoppingList, 
    ShoppingListItem, MealType, Unit
)
from ..models.user_profile import SchedulePreferences
from ..tools.calculation_tools import NutritionalCalculator

# Configure logging
logger = logging.getLogger(__name__)


class MealPlanningInput(BaseModel):
    """Input model for meal planning."""
    recipes: List[Dict[str, Any]] = Field(description="Available recipes to organize")
    nutritional_targets: Dict[str, float] = Field(description="Daily nutritional targets")
    schedule_preferences: Dict[str, Any] = Field(description="User schedule and timing preferences")
    week_start_date: str = Field(description="Start date for the meal plan")


class MealPlanningOutput(BaseModel):
    """Output model for meal planning."""
    weekly_schedule: Dict[str, Dict[str, Any]] = Field(description="Weekly meal schedule by day")
    shopping_list: Dict[str, List[Dict[str, Any]]] = Field(description="Shopping list organized by category")
    meal_prep_instructions: List[str] = Field(description="Step-by-step meal prep instructions")
    nutritional_balance_summary: Dict[str, float] = Field(description="Weekly nutritional balance summary")
    preparation_timeline: Dict[str, List[str]] = Field(description="Meal prep timeline by day")
    storage_recommendations: List[str] = Field(description="Food storage and safety recommendations")


class WeeklySchedulerTool(BaseTool):
    """Tool for organizing recipes into weekly schedules."""
    
    name: str = "weekly_scheduler"
    description: str = "Organize recipes into balanced weekly meal schedules"
    
    def _run(self, recipes: List[Dict[str, Any]], nutritional_targets: Dict[str, float], preferences: Dict[str, Any]) -> str:
        """
        Create a weekly meal schedule from available recipes.
        
        Args:
            recipes: List of available recipes
            nutritional_targets: Daily nutritional targets
            preferences: User schedule preferences
            
        Returns:
            Weekly schedule organization
        """
        try:
            meals_per_day = preferences.get('meals_per_day', 3)
            snacks_per_day = preferences.get('snacks_per_day', 1)
            
            # Categorize recipes by meal type
            breakfast_recipes = [r for r in recipes if r.get('meal_type') == 'breakfast']
            lunch_recipes = [r for r in recipes if r.get('meal_type') == 'lunch']
            dinner_recipes = [r for r in recipes if r.get('meal_type') == 'dinner']
            snack_recipes = [r for r in recipes if r.get('meal_type') == 'snack']
            
            # If not enough recipes in categories, use flexible assignment
            if not breakfast_recipes:
                breakfast_recipes = [r for r in recipes if r.get('prep_time', 0) <= 15]
            if not lunch_recipes:
                lunch_recipes = [r for r in recipes if r.get('cook_time', 0) <= 30]
            if not dinner_recipes:
                dinner_recipes = recipes  # Any recipe can be dinner
            
            result = "Weekly Meal Schedule Organization:\n\n"
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for i, day in enumerate(days):
                result += f"**{day}:**\n"
                
                # Assign breakfast
                if breakfast_recipes and meals_per_day >= 1:
                    breakfast = breakfast_recipes[i % len(breakfast_recipes)]
                    result += f"- Breakfast: {breakfast.get('name', 'Unknown')}\n"
                
                # Assign lunch
                if lunch_recipes and meals_per_day >= 2:
                    lunch = lunch_recipes[i % len(lunch_recipes)]
                    result += f"- Lunch: {lunch.get('name', 'Unknown')}\n"
                
                # Assign dinner
                if dinner_recipes and meals_per_day >= 3:
                    dinner = dinner_recipes[i % len(dinner_recipes)]
                    result += f"- Dinner: {dinner.get('name', 'Unknown')}\n"
                
                # Assign snacks
                if snack_recipes and snacks_per_day > 0:
                    for j in range(snacks_per_day):
                        snack = snack_recipes[(i + j) % len(snack_recipes)]
                        result += f"- Snack {j+1}: {snack.get('name', 'Unknown')}\n"
                
                result += "\n"
            
            # Add nutritional balance considerations
            result += "Nutritional Balance Considerations:\n"
            target_calories = nutritional_targets.get('calories', 2000)
            target_protein = nutritional_targets.get('protein', 150)
            
            result += f"- Target daily calories: {target_calories:.0f}\n"
            result += f"- Target daily protein: {target_protein:.0f}g\n"
            result += "- Ensure variety in protein sources throughout the week\n"
            result += "- Balance heavier meals with lighter options\n"
            result += "- Consider prep time distribution across days\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create weekly schedule: {e}")
            return f"Error creating weekly schedule: {str(e)}"


class ShoppingListGeneratorTool(BaseTool):
    """Tool for generating organized shopping lists."""
    
    name: str = "shopping_list_generator"
    description: str = "Generate organized shopping lists from meal plans"
    

    
    def _load_category_mapping(self) -> Dict[str, str]:
        """Load ingredient to category mapping for shopping list organization."""
        return {
            # Proteins
            'chicken': 'Meat & Poultry',
            'beef': 'Meat & Poultry',
            'pork': 'Meat & Poultry',
            'turkey': 'Meat & Poultry',
            'fish': 'Seafood',
            'salmon': 'Seafood',
            'shrimp': 'Seafood',
            'tofu': 'Meat Alternatives',
            'tempeh': 'Meat Alternatives',
            'beans': 'Pantry',
            'lentils': 'Pantry',
            
            # Dairy
            'milk': 'Dairy',
            'cheese': 'Dairy',
            'yogurt': 'Dairy',
            'butter': 'Dairy',
            'eggs': 'Dairy',
            
            # Produce
            'apple': 'Produce',
            'banana': 'Produce',
            'berries': 'Produce',
            'spinach': 'Produce',
            'broccoli': 'Produce',
            'carrots': 'Produce',
            'onions': 'Produce',
            'tomatoes': 'Produce',
            'peppers': 'Produce',
            'lettuce': 'Produce',
            
            # Grains & Bread
            'rice': 'Grains & Bread',
            'quinoa': 'Grains & Bread',
            'oats': 'Grains & Bread',
            'bread': 'Grains & Bread',
            'pasta': 'Grains & Bread',
            'flour': 'Baking',
            
            # Pantry
            'olive_oil': 'Pantry',
            'coconut_oil': 'Pantry',
            'vinegar': 'Pantry',
            'salt': 'Pantry',
            'pepper': 'Pantry',
            'herbs': 'Pantry',
            'spices': 'Pantry',
            
            # Frozen
            'frozen_vegetables': 'Frozen',
            'frozen_fruits': 'Frozen',
            
            # Canned/Jarred
            'canned_beans': 'Canned/Jarred',
            'canned_tomatoes': 'Canned/Jarred',
            'nut_butter': 'Canned/Jarred'
        }
    
    def _run(self, recipes: List[Dict[str, Any]]) -> str:
        """
        Generate a shopping list from recipes.
        
        Args:
            recipes: List of recipes to generate shopping list from
            
        Returns:
            Organized shopping list
        """
        try:
            # Consolidate ingredients
            ingredient_totals = {}
            
            for recipe in recipes:
                ingredients = recipe.get('ingredients', [])
                servings = recipe.get('servings', 1)
                
                for ingredient in ingredients:
                    name = ingredient.get('name', '').lower()
                    quantity = ingredient.get('quantity', 0)
                    unit = ingredient.get('unit', 'pieces')
                    
                    # Create key for consolidation
                    key = (name, unit)
                    
                    if key not in ingredient_totals:
                        ingredient_totals[key] = {
                            'name': ingredient.get('name', ''),
                            'quantity': 0,
                            'unit': unit,
                            'category': self._get_category(name)
                        }
                    
                    ingredient_totals[key]['quantity'] += quantity
            
            # Organize by category
            categorized_items = {}
            for item_data in ingredient_totals.values():
                category = item_data['category']
                if category not in categorized_items:
                    categorized_items[category] = []
                categorized_items[category].append(item_data)
            
            # Format output
            result = "Shopping List (Organized by Store Section):\n\n"
            
            # Define category order for shopping efficiency
            category_order = [
                'Produce', 'Meat & Poultry', 'Seafood', 'Dairy', 
                'Grains & Bread', 'Pantry', 'Canned/Jarred', 
                'Frozen', 'Baking', 'Meat Alternatives', 'Other'
            ]
            
            total_items = 0
            for category in category_order:
                if category in categorized_items:
                    result += f"**{category}:**\n"
                    items = categorized_items[category]
                    
                    # Sort items alphabetically within category
                    items.sort(key=lambda x: x['name'])
                    
                    for item in items:
                        quantity = item['quantity']
                        unit = item['unit']
                        name = item['name']
                        
                        # Format quantity nicely
                        if quantity == int(quantity):
                            quantity_str = str(int(quantity))
                        else:
                            quantity_str = f"{quantity:.1f}"
                        
                        result += f"- {quantity_str} {unit} {name}\n"
                        total_items += 1
                    
                    result += "\n"
            
            result += f"**Total Items: {total_items}**\n\n"
            
            # Add shopping tips
            result += "Shopping Tips:\n"
            result += "- Check pantry items before shopping\n"
            result += "- Buy produce last to maintain freshness\n"
            result += "- Consider seasonal alternatives for better prices\n"
            result += "- Bring reusable bags and shopping list\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate shopping list: {e}")
            return f"Error generating shopping list: {str(e)}"
    
    def _get_category(self, ingredient_name: str) -> str:
        """Get category for an ingredient."""
        ingredient_lower = ingredient_name.lower()
        
        # Load category mapping locally
        category_mapping = self._load_category_mapping()
        
        # Check for direct matches
        for key, category in category_mapping.items():
            if key in ingredient_lower:
                return category
        
        # Check for partial matches
        if any(word in ingredient_lower for word in ['fruit', 'berry', 'apple', 'orange']):
            return 'Produce'
        elif any(word in ingredient_lower for word in ['vegetable', 'green', 'leaf']):
            return 'Produce'
        elif any(word in ingredient_lower for word in ['meat', 'chicken', 'beef']):
            return 'Meat & Poultry'
        elif any(word in ingredient_lower for word in ['milk', 'cheese', 'dairy']):
            return 'Dairy'
        elif any(word in ingredient_lower for word in ['grain', 'rice', 'bread']):
            return 'Grains & Bread'
        elif any(word in ingredient_lower for word in ['oil', 'sauce', 'spice']):
            return 'Pantry'
        elif any(word in ingredient_lower for word in ['frozen']):
            return 'Frozen'
        elif any(word in ingredient_lower for word in ['canned', 'jar']):
            return 'Canned/Jarred'
        else:
            return 'Other'


class MealPrepPlannerTool(BaseTool):
    """Tool for creating meal prep instructions and timelines."""
    
    name: str = "meal_prep_planner"
    description: str = "Create meal prep instructions and preparation timelines"
    
    def _run(self, recipes: List[Dict[str, Any]], prep_preferences: Dict[str, Any]) -> str:
        """
        Create meal prep instructions and timeline.
        
        Args:
            recipes: List of recipes to prep
            prep_preferences: User meal prep preferences
            
        Returns:
            Meal prep instructions and timeline
        """
        try:
            prep_days = prep_preferences.get('meal_prep_days', ['sunday'])
            max_prep_time = prep_preferences.get('prep_time_limit', 120)
            
            result = "Meal Prep Plan:\n\n"
            
            # Categorize recipes by prep requirements
            make_ahead_recipes = []
            fresh_recipes = []
            batch_cookable = []
            
            for recipe in recipes:
                prep_time = recipe.get('prep_time', 0)
                cook_time = recipe.get('cook_time', 0)
                name = recipe.get('name', 'Unknown')
                
                # Determine prep category
                if cook_time > 30 or 'soup' in name.lower() or 'stew' in name.lower():
                    batch_cookable.append(recipe)
                elif prep_time <= 10 and cook_time <= 15:
                    fresh_recipes.append(recipe)
                else:
                    make_ahead_recipes.append(recipe)
            
            # Create prep timeline
            result += f"**Prep Day Schedule ({', '.join(prep_days).title()}):**\n\n"
            
            current_time = 0
            
            # Phase 1: Batch cooking (longest items first)
            if batch_cookable:
                result += "**Phase 1: Batch Cooking (1-2 hours)**\n"
                for recipe in sorted(batch_cookable, key=lambda x: x.get('cook_time', 0), reverse=True):
                    cook_time = recipe.get('cook_time', 0)
                    result += f"- Start {recipe.get('name', 'Unknown')} ({cook_time} min cook time)\n"
                    current_time += cook_time
                result += "\n"
            
            # Phase 2: Make-ahead prep
            if make_ahead_recipes:
                result += "**Phase 2: Make-Ahead Prep (30-60 minutes)**\n"
                for recipe in make_ahead_recipes:
                    prep_time = recipe.get('prep_time', 0)
                    result += f"- Prep {recipe.get('name', 'Unknown')} ({prep_time} min prep)\n"
                    current_time += prep_time
                result += "\n"
            
            # Phase 3: Fresh items (daily)
            if fresh_recipes:
                result += "**Phase 3: Fresh Items (Prepare Daily)**\n"
                for recipe in fresh_recipes:
                    result += f"- {recipe.get('name', 'Unknown')} - prepare fresh each day\n"
                result += "\n"
            
            # Storage instructions
            result += "**Storage Instructions:**\n"
            result += "- Store cooked grains and proteins in airtight containers (3-4 days)\n"
            result += "- Keep cut vegetables in separate containers with paper towels\n"
            result += "- Prepare dressings and sauces separately to maintain freshness\n"
            result += "- Label containers with contents and date\n"
            result += "- Store most items in refrigerator, freeze items for later in week\n\n"
            
            # Prep tips
            result += "**Meal Prep Tips:**\n"
            result += "- Wash and chop all vegetables at once\n"
            result += "- Cook grains and proteins in large batches\n"
            result += "- Use sheet pan cooking for multiple items\n"
            result += "- Prepare grab-and-go portions for busy days\n"
            result += "- Keep some ingredients separate for variety\n\n"
            
            # Time estimate
            result += f"**Total Estimated Prep Time: {current_time} minutes**\n"
            if current_time > max_prep_time:
                result += f"⚠️ Exceeds preferred prep time limit ({max_prep_time} min)\n"
                result += "Consider spreading prep across multiple days or simplifying recipes.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create meal prep plan: {e}")
            return f"Error creating meal prep plan: {str(e)}"


class NutritionalBalanceTool(BaseTool):
    """Tool for ensuring nutritional balance across the week."""
    
    name: str = "nutritional_balance"
    description: str = "Analyze and ensure nutritional balance across weekly meal plans"
    
    def _run(self, daily_meals: List[Dict[str, Any]], nutritional_targets: Dict[str, float]) -> str:
        """
        Analyze nutritional balance across the week.
        
        Args:
            daily_meals: List of daily meal plans
            nutritional_targets: Daily nutritional targets
            
        Returns:
            Nutritional balance analysis
        """
        try:
            target_calories = nutritional_targets.get('calories', 2000)
            target_protein = nutritional_targets.get('protein', 150)
            target_carbs = nutritional_targets.get('carbohydrates', 250)
            target_fat = nutritional_targets.get('fat', 67)
            
            result = "Weekly Nutritional Balance Analysis:\n\n"
            
            # Analyze each day
            daily_totals = []
            for i, day_meals in enumerate(daily_meals):
                day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
                
                # Calculate daily totals (simplified - would use actual nutrition data)
                daily_calories = 0
                daily_protein = 0
                daily_carbs = 0
                daily_fat = 0
                
                # Estimate based on meal types and ingredients
                for meal_type, meal in day_meals.items():
                    if meal and isinstance(meal, dict):
                        # Rough estimation based on meal type
                        if meal_type == 'breakfast':
                            daily_calories += 400
                            daily_protein += 20
                            daily_carbs += 45
                            daily_fat += 15
                        elif meal_type == 'lunch':
                            daily_calories += 500
                            daily_protein += 30
                            daily_carbs += 55
                            daily_fat += 18
                        elif meal_type == 'dinner':
                            daily_calories += 600
                            daily_protein += 35
                            daily_carbs += 60
                            daily_fat += 22
                        elif meal_type == 'snacks':
                            daily_calories += 200
                            daily_protein += 8
                            daily_carbs += 25
                            daily_fat += 8
                
                daily_totals.append({
                    'day': day_name,
                    'calories': daily_calories,
                    'protein': daily_protein,
                    'carbs': daily_carbs,
                    'fat': daily_fat
                })
            
            # Calculate weekly averages
            avg_calories = sum(d['calories'] for d in daily_totals) / len(daily_totals)
            avg_protein = sum(d['protein'] for d in daily_totals) / len(daily_totals)
            avg_carbs = sum(d['carbs'] for d in daily_totals) / len(daily_totals)
            avg_fat = sum(d['fat'] for d in daily_totals) / len(daily_totals)
            
            result += "**Weekly Averages vs Targets:**\n"
            result += f"- Calories: {avg_calories:.0f} / {target_calories:.0f} ({avg_calories/target_calories*100:.1f}%)\n"
            result += f"- Protein: {avg_protein:.1f}g / {target_protein:.1f}g ({avg_protein/target_protein*100:.1f}%)\n"
            result += f"- Carbs: {avg_carbs:.1f}g / {target_carbs:.1f}g ({avg_carbs/target_carbs*100:.1f}%)\n"
            result += f"- Fat: {avg_fat:.1f}g / {target_fat:.1f}g ({avg_fat/target_fat*100:.1f}%)\n\n"
            
            # Identify imbalances
            result += "**Balance Assessment:**\n"
            
            if abs(avg_calories - target_calories) / target_calories > 0.1:
                if avg_calories > target_calories:
                    result += "⚠️ Calories are above target - consider smaller portions or lighter meals\n"
                else:
                    result += "⚠️ Calories are below target - consider adding healthy snacks or larger portions\n"
            else:
                result += "✓ Calorie balance is good\n"
            
            if avg_protein / target_protein < 0.8:
                result += "⚠️ Protein intake is low - add more lean proteins, beans, or dairy\n"
            elif avg_protein / target_protein > 1.3:
                result += "⚠️ Protein intake is high - consider balancing with more carbs and vegetables\n"
            else:
                result += "✓ Protein balance is good\n"
            
            # Recommendations
            result += "\n**Recommendations:**\n"
            result += "- Ensure each meal includes a protein source\n"
            result += "- Include a variety of colorful vegetables throughout the week\n"
            result += "- Balance heavier meals with lighter options\n"
            result += "- Consider nutrient timing around physical activity\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze nutritional balance: {e}")
            return f"Error analyzing nutritional balance: {str(e)}"


def create_meal_planner_agent() -> Agent:
    """
    Create and configure the Meal Planner Agent.
    
    Returns:
        Configured CrewAI Agent for meal planning
    """
    
    # Initialize tools
    weekly_scheduler_tool = WeeklySchedulerTool()
    shopping_list_tool = ShoppingListGeneratorTool()
    meal_prep_tool = MealPrepPlannerTool()
    nutritional_balance_tool = NutritionalBalanceTool()
    
    tools = [
        weekly_scheduler_tool,
        shopping_list_tool,
        meal_prep_tool,
        nutritional_balance_tool
    ]
    
    agent = Agent(
        role="Weekly Schedule Organizer and Meal Planning Coordinator",
        goal="Organize recipes into balanced weekly schedules with shopping lists and meal prep instructions",
        backstory="""You are an experienced meal planning coordinator with over 10 years of experience 
        helping busy individuals and families organize their weekly meals efficiently. Your expertise 
        includes creating balanced meal schedules, optimizing meal prep workflows, and generating 
        practical shopping lists. You understand the challenges of maintaining nutritional balance 
        while managing time constraints, food storage limitations, and varying cooking skills. 
        You have worked with diverse dietary needs and lifestyle requirements, giving you insight 
        into practical meal planning strategies that work in real-world situations.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=True
    )
    
    return agent


def create_meal_planning_task(
    recipes: List[Dict[str, Any]],
    nutritional_targets: Dict[str, float],
    schedule_preferences: Dict[str, Any],
    week_start_date: str
) -> Task:
    """
    Create a task for weekly meal planning.
    
    Args:
        recipes: Available recipes to organize
        nutritional_targets: Daily nutritional targets
        schedule_preferences: User schedule and timing preferences
        week_start_date: Start date for the meal plan
        
    Returns:
        CrewAI Task for meal planning
    """
    
    task = Task(
        description=f"""
        Create a comprehensive weekly meal plan that organizes the provided recipes into a balanced schedule.
        
        Available recipes: {len(recipes)} recipes
        Nutritional targets: {nutritional_targets}
        Schedule preferences: {schedule_preferences}
        Week starting: {week_start_date}
        
        Your meal plan should include:
        
        1. Weekly meal schedule with recipes assigned to specific days and meal types
        2. Nutritional balance analysis ensuring targets are met across the week
        3. Organized shopping list grouped by store sections for efficient shopping
        4. Detailed meal prep instructions and timeline for preparation
        5. Food storage recommendations and safety guidelines
        6. Preparation timeline optimized for the user's available prep time
        
        Use the available tools to:
        - Create a balanced weekly schedule from available recipes
        - Generate an organized shopping list for efficient grocery shopping
        - Develop meal prep instructions that fit the user's time constraints
        - Ensure nutritional balance across all days of the week
        
        Consider the user's schedule preferences, cooking skill level, and time constraints.
        Optimize for variety, nutritional balance, and practical implementation.
        """,
        expected_output="""
        A comprehensive weekly meal plan containing:
        
        1. **Weekly Schedule:**
           - Day-by-day meal assignments (breakfast, lunch, dinner, snacks)
           - Recipe names and basic information for each meal
           - Nutritional balance considerations across the week
        
        2. **Shopping List:**
           - Ingredients organized by store sections (Produce, Dairy, Meat, etc.)
           - Consolidated quantities for efficient shopping
           - Total item count and shopping tips
        
        3. **Meal Prep Instructions:**
           - Step-by-step preparation timeline
           - Batch cooking recommendations
           - Make-ahead vs. fresh preparation guidance
        
        4. **Storage & Safety:**
           - Food storage recommendations for prepped items
           - Safety guidelines for meal prep and storage
           - Container and labeling suggestions
        
        5. **Nutritional Summary:**
           - Weekly nutritional balance analysis
           - Daily target achievement assessment
           - Recommendations for nutritional optimization
        
        6. **Implementation Timeline:**
           - Recommended prep day schedule
           - Daily preparation requirements
           - Time estimates for each phase
        
        Format the output to be actionable and easy to follow for meal planning implementation.
        """,
        agent=create_meal_planner_agent(),
        output_pydantic=MealPlanningOutput
    )
    
    return task


# Utility functions for integration
def create_weekly_meal_plan(
    recipes: List[Recipe],
    nutritional_targets: Dict[str, float],
    schedule_preferences: SchedulePreferences,
    week_start_date: date
) -> WeeklyMealPlan:
    """
    Create a weekly meal plan using the Meal Planner Agent.
    
    Args:
        recipes: Available recipes to organize
        nutritional_targets: Daily nutritional targets
        schedule_preferences: User schedule preferences
        week_start_date: Start date for the meal plan
        
    Returns:
        WeeklyMealPlan object
    """
    try:
        # Convert recipes to dictionary format
        recipe_data = []
        for recipe in recipes:
            recipe_dict = {
                'name': recipe.name,
                'meal_type': recipe.meal_type.value,
                'prep_time': recipe.prep_time,
                'cook_time': recipe.cook_time,
                'servings': recipe.servings,
                'difficulty_level': recipe.difficulty_level.value,
                'ingredients': []
            }
            
            for ingredient in recipe.ingredients:
                recipe_dict['ingredients'].append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity,
                    'unit': ingredient.unit.value
                })
            
            recipe_data.append(recipe_dict)
        
        schedule_prefs = {
            'meals_per_day': schedule_preferences.meals_per_day,
            'snacks_per_day': schedule_preferences.snacks_per_day,
            'prep_time_limit': schedule_preferences.prep_time_limit,
            'meal_prep_days': schedule_preferences.meal_prep_days
        }
        
        # Create and execute task
        task = create_meal_planning_task(
            recipes=recipe_data,
            nutritional_targets=nutritional_targets,
            schedule_preferences=schedule_prefs,
            week_start_date=week_start_date.isoformat()
        )
        
        # For now, return a sample meal plan
        # In a full CrewAI implementation, this would execute the task
        return _generate_sample_meal_plan(recipes, week_start_date)
        
    except Exception as e:
        logger.error(f"Failed to create weekly meal plan: {e}")
        raise


def _generate_sample_meal_plan(recipes: List[Recipe], week_start_date: date) -> WeeklyMealPlan:
    """Generate a sample weekly meal plan for testing purposes."""
    
    # Create daily meal plans
    daily_plans = []
    
    for i in range(7):
        current_date = week_start_date + timedelta(days=i)
        
        # Assign recipes to meals (simplified logic)
        breakfast = None
        lunch = None
        dinner = None
        snacks = []
        
        # Find appropriate recipes for each meal type
        breakfast_recipes = [r for r in recipes if r.meal_type == MealType.BREAKFAST]
        lunch_recipes = [r for r in recipes if r.meal_type == MealType.LUNCH]
        dinner_recipes = [r for r in recipes if r.meal_type == MealType.DINNER]
        snack_recipes = [r for r in recipes if r.meal_type == MealType.SNACK]
        
        if breakfast_recipes:
            breakfast = breakfast_recipes[i % len(breakfast_recipes)]
        elif recipes:
            breakfast = recipes[0]  # Fallback
        
        if lunch_recipes:
            lunch = lunch_recipes[i % len(lunch_recipes)]
        elif len(recipes) > 1:
            lunch = recipes[1]  # Fallback
        
        if dinner_recipes:
            dinner = dinner_recipes[i % len(dinner_recipes)]
        elif len(recipes) > 2:
            dinner = recipes[2]  # Fallback
        
        if snack_recipes:
            snacks = [snack_recipes[i % len(snack_recipes)]]
        
        daily_plan = DailyMealPlan(
            date=current_date,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snacks=snacks
        )
        
        daily_plans.append(daily_plan)
    
    # Create meal plan
    meal_plan = WeeklyMealPlan(
        week_start_date=week_start_date,
        daily_plans=daily_plans,
        meal_prep_instructions=[
            "Prep vegetables and proteins on Sunday",
            "Cook grains in batches for the week",
            "Prepare grab-and-go snacks in advance",
            "Store prepped items in labeled containers"
        ]
    )
    
    # Generate shopping list and nutritional summary
    meal_plan.shopping_list = meal_plan.generate_shopping_list()
    meal_plan.nutritional_summary = meal_plan.calculate_nutritional_summary()
    
    return meal_plan
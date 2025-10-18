"""
Output formatting utilities for the Smart Recipe & Meal Planning System.

This module provides utilities for formatting meal plans, recipes, and shopping lists
into structured markdown reports and JSON serialization for data exchange between agents.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from dataclasses import asdict, is_dataclass
from enum import Enum

from .user_profile import UserProfile
from .recipe import (
    WeeklyMealPlan, DailyMealPlan, Recipe, Ingredient, ShoppingList, 
    NutritionalInfo, WeeklyNutritionalSummary
)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling dataclasses, enums, and dates."""
    
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


class JSONSerializer:
    """Utilities for JSON serialization and deserialization."""
    
    @staticmethod
    def serialize(obj: Any) -> str:
        """Serialize an object to JSON string."""
        return json.dumps(obj, cls=CustomJSONEncoder, indent=2, ensure_ascii=False)
    
    @staticmethod
    def serialize_to_dict(obj: Any) -> Dict[str, Any]:
        """Serialize an object to a dictionary."""
        return json.loads(JSONSerializer.serialize(obj))
    
    @staticmethod
    def deserialize(json_str: str) -> Dict[str, Any]:
        """Deserialize JSON string to dictionary."""
        return json.loads(json_str)
    
    @staticmethod
    def save_to_file(obj: Any, filepath: str) -> None:
        """Save object to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(JSONSerializer.serialize(obj))
    
    @staticmethod
    def load_from_file(filepath: str) -> Dict[str, Any]:
        """Load object from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)


class MarkdownReportGenerator:
    """Generator for structured markdown reports."""
    
    @staticmethod
    def format_nutritional_info(nutrition: NutritionalInfo, title: str = "Nutritional Information") -> str:
        """Format nutritional information as markdown."""
        lines = [
            f"### {title}",
            "",
            f"- **Calories:** {nutrition.calories:.0f} kcal",
            f"- **Protein:** {nutrition.protein:.1f}g",
            f"- **Carbohydrates:** {nutrition.carbohydrates:.1f}g",
            f"- **Fat:** {nutrition.fat:.1f}g",
            f"- **Fiber:** {nutrition.fiber:.1f}g",
            f"- **Sugar:** {nutrition.sugar:.1f}g",
            f"- **Sodium:** {nutrition.sodium:.0f}mg",
        ]
        
        # Add micronutrients if available
        if nutrition.vitamin_c:
            lines.append(f"- **Vitamin C:** {nutrition.vitamin_c:.1f}mg")
        if nutrition.calcium:
            lines.append(f"- **Calcium:** {nutrition.calcium:.1f}mg")
        if nutrition.iron:
            lines.append(f"- **Iron:** {nutrition.iron:.1f}mg")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_ingredient(ingredient: Ingredient) -> str:
        """Format a single ingredient as markdown."""
        unit_display = ingredient.unit.value
        cost_display = f" (${ingredient.get_total_cost():.2f})" if ingredient.cost_per_unit > 0 else ""
        
        return f"- {ingredient.quantity:.1f} {unit_display} {ingredient.name}{cost_display}"
    
    @staticmethod
    def format_recipe(recipe: Recipe, include_nutrition: bool = True, include_cost: bool = True) -> str:
        """Format a recipe as markdown."""
        lines = [
            f"## {recipe.name}",
            "",
        ]
        
        if recipe.description:
            lines.extend([recipe.description, ""])
        
        # Recipe metadata
        metadata = [
            f"- **Prep Time:** {recipe.prep_time} minutes",
            f"- **Cook Time:** {recipe.cook_time} minutes",
            f"- **Total Time:** {recipe.get_total_time()} minutes",
            f"- **Servings:** {recipe.servings}",
            f"- **Difficulty:** {recipe.difficulty_level.value.title()}",
        ]
        
        if recipe.cuisine_type:
            metadata.append(f"- **Cuisine:** {recipe.cuisine_type.title()}")
        
        if include_cost:
            metadata.append(f"- **Cost per Serving:** ${recipe.get_cost_per_serving():.2f}")
        
        if recipe.tags:
            metadata.append(f"- **Tags:** {', '.join(recipe.tags)}")
        
        lines.extend(metadata)
        lines.append("")
        
        # Ingredients
        lines.extend([
            "### Ingredients",
            "",
        ])
        
        for ingredient in recipe.ingredients:
            lines.append(MarkdownReportGenerator.format_ingredient(ingredient))
        
        lines.append("")
        
        # Instructions
        lines.extend([
            "### Instructions",
            "",
        ])
        
        for i, instruction in enumerate(recipe.instructions, 1):
            lines.append(f"{i}. {instruction}")
        
        lines.append("")
        
        # Nutritional information
        if include_nutrition:
            nutrition_per_serving = recipe.get_nutritional_info_per_serving()
            lines.extend([
                MarkdownReportGenerator.format_nutritional_info(
                    nutrition_per_serving, 
                    "Nutritional Information (Per Serving)"
                ),
                ""
            ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_daily_meal_plan(daily_plan: DailyMealPlan, include_nutrition: bool = True) -> str:
        """Format a daily meal plan as markdown."""
        date_str = daily_plan.date.strftime("%A, %B %d, %Y")
        lines = [
            f"## {date_str}",
            "",
        ]
        
        # Meals
        meals = [
            ("Breakfast", daily_plan.breakfast),
            ("Lunch", daily_plan.lunch),
            ("Dinner", daily_plan.dinner),
        ]
        
        for meal_name, recipe in meals:
            lines.append(f"### {meal_name}")
            if recipe:
                lines.extend([
                    f"**{recipe.name}**",
                    f"- Prep: {recipe.prep_time}min | Cook: {recipe.cook_time}min | Cost: ${recipe.get_cost_per_serving():.2f}",
                    ""
                ])
            else:
                lines.extend(["*No meal planned*", ""])
        
        # Snacks
        if daily_plan.snacks:
            lines.extend(["### Snacks", ""])
            for snack in daily_plan.snacks:
                lines.extend([
                    f"**{snack.name}**",
                    f"- Prep: {snack.prep_time}min | Cook: {snack.cook_time}min | Cost: ${snack.get_cost_per_serving():.2f}",
                    ""
                ])
        
        # Daily nutrition summary
        if include_nutrition:
            daily_nutrition = daily_plan.get_daily_nutrition()
            lines.extend([
                MarkdownReportGenerator.format_nutritional_info(
                    daily_nutrition, 
                    "Daily Nutritional Summary"
                ),
                ""
            ])
            
            lines.extend([
                f"**Daily Cost:** ${daily_plan.get_daily_cost():.2f}",
                ""
            ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_shopping_list(shopping_list: ShoppingList) -> str:
        """Format shopping list as markdown."""
        lines = [
            "## Shopping List",
            "",
            f"**Estimated Total Cost:** ${shopping_list.total_estimated_cost:.2f}",
            "",
        ]
        
        # Group by category
        grouped_items = shopping_list.group_by_category()
        
        for category, items in grouped_items.items():
            lines.extend([
                f"### {category}",
                "",
            ])
            
            for item in items:
                unit_display = item.unit.value
                cost_display = f" - ${item.estimated_cost:.2f}" if item.estimated_cost > 0 else ""
                alternatives_display = f" *(alternatives: {', '.join(item.alternatives)})*" if item.alternatives else ""
                
                lines.append(f"- [ ] {item.total_quantity:.1f} {unit_display} {item.ingredient_name}{cost_display}{alternatives_display}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_weekly_nutritional_summary(summary: WeeklyNutritionalSummary) -> str:
        """Format weekly nutritional summary as markdown."""
        lines = [
            "## Weekly Nutritional Summary",
            "",
        ]
        
        # Daily averages
        lines.extend([
            MarkdownReportGenerator.format_nutritional_info(
                summary.daily_averages, 
                "Daily Averages"
            ),
            ""
        ])
        
        # Weekly totals
        lines.extend([
            MarkdownReportGenerator.format_nutritional_info(
                summary.weekly_totals, 
                "Weekly Totals"
            ),
            ""
        ])
        
        # Nutritional consistency
        if summary.daily_variations:
            lines.extend([
                "### Nutritional Consistency",
                "",
                "*Lower values indicate more consistent daily intake*",
                "",
            ])
            
            for nutrient, variation in summary.daily_variations.items():
                consistency_level = "High" if variation < 0.1 else "Medium" if variation < 0.2 else "Low"
                lines.append(f"- **{nutrient.title()}:** {variation:.2f} ({consistency_level} consistency)")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_complete_meal_plan_report(
        meal_plan: WeeklyMealPlan, 
        user_profile: Optional[UserProfile] = None,
        include_recipes: bool = False
    ) -> str:
        """Generate a complete meal plan report in markdown format."""
        
        week_start = meal_plan.week_start_date.strftime("%B %d, %Y")
        week_end = meal_plan.daily_plans[-1].date.strftime("%B %d, %Y") if meal_plan.daily_plans else ""
        
        lines = [
            "# Weekly Meal Plan Report",
            "",
            f"**Week of:** {week_start} - {week_end}",
            f"**Generated on:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
        ]
        
        # User profile summary (if provided)
        if user_profile:
            lines.extend([
                "## User Profile Summary",
                "",
                f"- **Age:** {user_profile.personal_info.age} years",
                f"- **Activity Level:** {user_profile.personal_info.activity_level.value.replace('_', ' ').title()}",
                f"- **Health Goal:** {user_profile.health_goals.goal_type.value.replace('_', ' ').title()}",
                f"- **Weekly Budget:** ${user_profile.budget_constraints.weekly_budget:.2f}",
                "",
            ])
            
            if user_profile.dietary_preferences.restrictions:
                lines.extend([
                    f"- **Dietary Restrictions:** {', '.join(user_profile.dietary_preferences.restrictions)}",
                    ""
                ])
        
        # Weekly overview
        lines.extend([
            "## Weekly Overview",
            "",
            f"- **Total Cost:** ${meal_plan.get_total_cost():.2f}",
            f"- **Unique Recipes:** {len(meal_plan.get_all_recipes())}",
            "",
        ])
        
        # Daily meal plans
        lines.extend([
            "# Daily Meal Plans",
            "",
        ])
        
        for daily_plan in meal_plan.daily_plans:
            lines.extend([
                MarkdownReportGenerator.format_daily_meal_plan(daily_plan, include_nutrition=False),
                "---",
                ""
            ])
        
        # Weekly nutritional summary
        if meal_plan.nutritional_summary:
            lines.extend([
                MarkdownReportGenerator.format_weekly_nutritional_summary(meal_plan.nutritional_summary),
                ""
            ])
        
        # Shopping list
        if meal_plan.shopping_list and meal_plan.shopping_list.items:
            lines.extend([
                MarkdownReportGenerator.format_shopping_list(meal_plan.shopping_list),
                ""
            ])
        
        # Meal prep instructions
        if meal_plan.meal_prep_instructions:
            lines.extend([
                "## Meal Prep Instructions",
                "",
            ])
            
            for i, instruction in enumerate(meal_plan.meal_prep_instructions, 1):
                lines.append(f"{i}. {instruction}")
            
            lines.append("")
        
        # Full recipes (if requested)
        if include_recipes:
            lines.extend([
                "# Recipe Details",
                "",
            ])
            
            for recipe in meal_plan.get_all_recipes():
                lines.extend([
                    MarkdownReportGenerator.format_recipe(recipe),
                    "---",
                    ""
                ])
        
        return "\n".join(lines)


class AgentDataExchange:
    """Utilities for data exchange between CrewAI agents."""
    
    @staticmethod
    def prepare_user_profile_context(user_profile: UserProfile) -> Dict[str, Any]:
        """Prepare user profile data for agent context."""
        return {
            "user_profile": JSONSerializer.serialize_to_dict(user_profile),
            "dietary_restrictions": user_profile.dietary_preferences.restrictions,
            "allergies": user_profile.dietary_preferences.allergies,
            "budget": user_profile.budget_constraints.weekly_budget,
            "health_goal": user_profile.health_goals.goal_type.value,
            "activity_level": user_profile.personal_info.activity_level.value
        }
    
    @staticmethod
    def prepare_nutritional_requirements_context(
        calories: float, 
        protein: float, 
        carbs: float, 
        fat: float,
        additional_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare nutritional requirements for agent context."""
        context = {
            "daily_calories": calories,
            "daily_protein": protein,
            "daily_carbohydrates": carbs,
            "daily_fat": fat,
            "macros": {
                "protein_percentage": (protein * 4 / calories) * 100,
                "carb_percentage": (carbs * 4 / calories) * 100,
                "fat_percentage": (fat * 9 / calories) * 100
            }
        }
        
        if additional_requirements:
            context.update(additional_requirements)
        
        return context
    
    @staticmethod
    def prepare_recipe_context(recipes: List[Recipe]) -> Dict[str, Any]:
        """Prepare recipe data for agent context."""
        return {
            "recipes": [JSONSerializer.serialize_to_dict(recipe) for recipe in recipes],
            "recipe_count": len(recipes),
            "total_prep_time": sum(recipe.prep_time for recipe in recipes),
            "total_cook_time": sum(recipe.cook_time for recipe in recipes),
            "average_cost_per_serving": sum(recipe.get_cost_per_serving() for recipe in recipes) / len(recipes) if recipes else 0
        }
    
    @staticmethod
    def prepare_ingredient_pricing_context(ingredients: List[Ingredient]) -> Dict[str, Any]:
        """Prepare ingredient pricing data for agent context."""
        return {
            "ingredients": [JSONSerializer.serialize_to_dict(ingredient) for ingredient in ingredients],
            "total_cost": sum(ingredient.get_total_cost() for ingredient in ingredients),
            "ingredient_categories": list(set(ingredient.category for ingredient in ingredients if ingredient.category))
        }
    
    @staticmethod
    def format_agent_output(
        agent_name: str, 
        output_data: Any, 
        success: bool = True, 
        errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Format agent output for consistent data exchange."""
        return {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "data": JSONSerializer.serialize_to_dict(output_data) if output_data else None,
            "errors": errors or []
        }
"""
Custom calculation tools for the Smart Recipe & Meal Planning System.

This module provides utilities for cost calculations, nutritional balance checking,
recipe formatting, and validation algorithms.
"""

import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from ..models.recipe import (
    Recipe, Ingredient, NutritionalInfo, WeeklyMealPlan, 
    DailyMealPlan, Unit, MealType
)
from ..models.user_profile import UserProfile, GoalType, ActivityLevel, Gender

# Configure logging
logger = logging.getLogger(__name__)


class NutritionalStatus(Enum):
    """Nutritional balance status."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    DEFICIENT = "deficient"


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for meals."""
    ingredient_costs: Dict[str, float]
    total_cost: float
    cost_per_serving: float
    cost_per_meal_type: Dict[str, float]
    daily_costs: List[float]
    weekly_average: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'ingredient_costs': self.ingredient_costs,
            'total_cost': self.total_cost,
            'cost_per_serving': self.cost_per_serving,
            'cost_per_meal_type': self.cost_per_meal_type,
            'daily_costs': self.daily_costs,
            'weekly_average': self.weekly_average
        }


@dataclass
class NutritionalBalance:
    """Nutritional balance analysis result."""
    status: NutritionalStatus
    daily_targets: NutritionalInfo
    daily_actual: NutritionalInfo
    weekly_average: NutritionalInfo
    deficiencies: List[str]
    excesses: List[str]
    recommendations: List[str]
    balance_score: float  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'status': self.status.value,
            'daily_targets': self.daily_targets.__dict__,
            'daily_actual': self.daily_actual.__dict__,
            'weekly_average': self.weekly_average.__dict__,
            'deficiencies': self.deficiencies,
            'excesses': self.excesses,
            'recommendations': self.recommendations,
            'balance_score': self.balance_score
        }


@dataclass
class BudgetOptimization:
    """Budget optimization result."""
    original_cost: float
    optimized_cost: float
    savings: float
    savings_percentage: float
    substitutions: List[Dict[str, str]]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'original_cost': self.original_cost,
            'optimized_cost': self.optimized_cost,
            'savings': self.savings,
            'savings_percentage': self.savings_percentage,
            'substitutions': self.substitutions,
            'recommendations': self.recommendations
        }


class CostCalculator:
    """Utility class for cost calculations and budget optimization."""
    
    @staticmethod
    def calculate_recipe_cost(recipe: Recipe) -> float:
        """
        Calculate total cost for a recipe.
        
        Args:
            recipe: Recipe object with ingredients
            
        Returns:
            Total cost for the recipe
        """
        total_cost = 0.0
        
        for ingredient in recipe.ingredients:
            ingredient_cost = ingredient.quantity * ingredient.cost_per_unit
            total_cost += ingredient_cost
        
        return total_cost
    
    @staticmethod
    def calculate_cost_per_serving(recipe: Recipe) -> float:
        """
        Calculate cost per serving for a recipe.
        
        Args:
            recipe: Recipe object
            
        Returns:
            Cost per serving
        """
        total_cost = CostCalculator.calculate_recipe_cost(recipe)
        return total_cost / recipe.servings if recipe.servings > 0 else 0.0
    
    @staticmethod
    def calculate_daily_cost(daily_plan: DailyMealPlan) -> float:
        """
        Calculate total cost for a daily meal plan.
        
        Args:
            daily_plan: DailyMealPlan object
            
        Returns:
            Total daily cost
        """
        total_cost = 0.0
        
        # Add costs for main meals
        for recipe in [daily_plan.breakfast, daily_plan.lunch, daily_plan.dinner]:
            if recipe:
                total_cost += CostCalculator.calculate_cost_per_serving(recipe)
        
        # Add costs for snacks
        for snack in daily_plan.snacks:
            total_cost += CostCalculator.calculate_cost_per_serving(snack)
        
        return total_cost
    
    @staticmethod
    def calculate_weekly_cost_breakdown(meal_plan: WeeklyMealPlan) -> CostBreakdown:
        """
        Calculate detailed cost breakdown for a weekly meal plan.
        
        Args:
            meal_plan: WeeklyMealPlan object
            
        Returns:
            CostBreakdown with detailed analysis
        """
        ingredient_costs = {}
        daily_costs = []
        cost_per_meal_type = {
            'breakfast': 0.0,
            'lunch': 0.0,
            'dinner': 0.0,
            'snacks': 0.0
        }
        
        # Calculate costs for each day
        for daily_plan in meal_plan.daily_plans:
            daily_cost = CostCalculator.calculate_daily_cost(daily_plan)
            daily_costs.append(daily_cost)
            
            # Break down by meal type
            if daily_plan.breakfast:
                breakfast_cost = CostCalculator.calculate_cost_per_serving(daily_plan.breakfast)
                cost_per_meal_type['breakfast'] += breakfast_cost
                
                # Track ingredient costs
                for ingredient in daily_plan.breakfast.ingredients:
                    ingredient_cost = ingredient.quantity * ingredient.cost_per_unit
                    ingredient_costs[ingredient.name] = ingredient_costs.get(ingredient.name, 0) + ingredient_cost
            
            if daily_plan.lunch:
                lunch_cost = CostCalculator.calculate_cost_per_serving(daily_plan.lunch)
                cost_per_meal_type['lunch'] += lunch_cost
                
                for ingredient in daily_plan.lunch.ingredients:
                    ingredient_cost = ingredient.quantity * ingredient.cost_per_unit
                    ingredient_costs[ingredient.name] = ingredient_costs.get(ingredient.name, 0) + ingredient_cost
            
            if daily_plan.dinner:
                dinner_cost = CostCalculator.calculate_cost_per_serving(daily_plan.dinner)
                cost_per_meal_type['dinner'] += dinner_cost
                
                for ingredient in daily_plan.dinner.ingredients:
                    ingredient_cost = ingredient.quantity * ingredient.cost_per_unit
                    ingredient_costs[ingredient.name] = ingredient_costs.get(ingredient.name, 0) + ingredient_cost
            
            # Snacks
            snack_cost = sum(CostCalculator.calculate_cost_per_serving(snack) for snack in daily_plan.snacks)
            cost_per_meal_type['snacks'] += snack_cost
            
            for snack in daily_plan.snacks:
                for ingredient in snack.ingredients:
                    ingredient_cost = ingredient.quantity * ingredient.cost_per_unit
                    ingredient_costs[ingredient.name] = ingredient_costs.get(ingredient.name, 0) + ingredient_cost
        
        total_cost = sum(daily_costs)
        weekly_average = total_cost / 7 if daily_costs else 0.0
        
        return CostBreakdown(
            ingredient_costs=ingredient_costs,
            total_cost=total_cost,
            cost_per_serving=total_cost / (len(meal_plan.daily_plans) * 3),  # Assuming 3 main meals per day
            cost_per_meal_type=cost_per_meal_type,
            daily_costs=daily_costs,
            weekly_average=weekly_average
        )
    
    @staticmethod
    def optimize_budget(meal_plan: WeeklyMealPlan, target_budget: float) -> BudgetOptimization:
        """
        Optimize meal plan to fit within budget constraints.
        
        Args:
            meal_plan: WeeklyMealPlan object
            target_budget: Target weekly budget
            
        Returns:
            BudgetOptimization with suggestions
        """
        original_breakdown = CostCalculator.calculate_weekly_cost_breakdown(meal_plan)
        original_cost = original_breakdown.total_cost
        
        if original_cost <= target_budget:
            return BudgetOptimization(
                original_cost=original_cost,
                optimized_cost=original_cost,
                savings=0.0,
                savings_percentage=0.0,
                substitutions=[],
                recommendations=["Your meal plan is already within budget!"]
            )
        
        # Calculate required savings
        required_savings = original_cost - target_budget
        savings_percentage = (required_savings / original_cost) * 100
        
        # Generate optimization recommendations
        recommendations = []
        substitutions = []
        
        # Identify expensive ingredients
        expensive_ingredients = sorted(
            original_breakdown.ingredient_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for ingredient_name, cost in expensive_ingredients:
            if cost > target_budget * 0.1:  # If ingredient costs more than 10% of budget
                recommendations.append(f"Consider substituting {ingredient_name} (${cost:.2f}) with a cheaper alternative")
                substitutions.append({
                    'original': ingredient_name,
                    'suggestion': f"Generic or store-brand {ingredient_name.lower()}",
                    'potential_savings': f"${cost * 0.2:.2f}"  # Assume 20% savings
                })
        
        # Meal type recommendations
        if original_breakdown.cost_per_meal_type['dinner'] > target_budget * 0.4:
            recommendations.append("Dinner costs are high. Consider simpler dinner recipes or batch cooking.")
        
        if original_breakdown.cost_per_meal_type['snacks'] > target_budget * 0.15:
            recommendations.append("Snack costs are high. Consider homemade snacks or bulk purchases.")
        
        # General recommendations
        recommendations.extend([
            "Buy ingredients in bulk when possible",
            "Use seasonal produce for better prices",
            "Consider frozen vegetables as alternatives to fresh",
            "Plan meals around sales and discounts",
            "Reduce portion sizes slightly to stretch ingredients"
        ])
        
        # Estimate optimized cost (conservative estimate)
        estimated_savings = min(required_savings, original_cost * 0.25)  # Max 25% savings
        optimized_cost = original_cost - estimated_savings
        
        return BudgetOptimization(
            original_cost=original_cost,
            optimized_cost=optimized_cost,
            savings=estimated_savings,
            savings_percentage=(estimated_savings / original_cost) * 100,
            substitutions=substitutions,
            recommendations=recommendations
        )


class NutritionalCalculator:
    """Utility class for nutritional calculations and balance checking."""
    
    # Recommended Daily Allowances (RDA) - base values for adult males
    RDA_BASE = {
        'calories': 2000,
        'protein': 56,      # grams
        'carbohydrates': 300,  # grams (45-65% of calories)
        'fat': 67,          # grams (20-35% of calories)
        'fiber': 25,        # grams
        'sodium': 2300,     # mg
        'vitamin_c': 90,    # mg
        'calcium': 1000,    # mg
        'iron': 8,          # mg
    }
    
    @staticmethod
    def calculate_bmr(user_profile: UserProfile) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.
        
        Args:
            user_profile: UserProfile object
            
        Returns:
            BMR in calories per day
        """
        personal_info = user_profile.personal_info
        
        if personal_info.gender == Gender.MALE:
            bmr = 10 * personal_info.weight + 6.25 * personal_info.height - 5 * personal_info.age + 5
        else:  # Female or Other
            bmr = 10 * personal_info.weight + 6.25 * personal_info.height - 5 * personal_info.age - 161
        
        return bmr
    
    @staticmethod
    def calculate_tdee(user_profile: UserProfile) -> float:
        """
        Calculate Total Daily Energy Expenditure.
        
        Args:
            user_profile: UserProfile object
            
        Returns:
            TDEE in calories per day
        """
        bmr = NutritionalCalculator.calculate_bmr(user_profile)
        
        # Activity multipliers
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTREMELY_ACTIVE: 1.9
        }
        
        multiplier = activity_multipliers.get(user_profile.personal_info.activity_level, 1.2)
        return bmr * multiplier
    
    @staticmethod
    def calculate_daily_targets(user_profile: UserProfile) -> NutritionalInfo:
        """
        Calculate daily nutritional targets based on user profile.
        
        Args:
            user_profile: UserProfile object
            
        Returns:
            NutritionalInfo with daily targets
        """
        # Calculate caloric needs
        tdee = NutritionalCalculator.calculate_tdee(user_profile)
        
        # Adjust for goals
        if user_profile.health_goals.goal_type == GoalType.WEIGHT_LOSS:
            target_calories = tdee - 500  # 1 lb per week loss
        elif user_profile.health_goals.goal_type == GoalType.MUSCLE_GAIN:
            target_calories = tdee + 300  # Moderate surplus
        else:
            target_calories = tdee
        
        # Use user's target if specified
        if user_profile.health_goals.target_calories:
            target_calories = user_profile.health_goals.target_calories
        
        # Calculate macronutrient targets
        macro_prefs = user_profile.health_goals.macro_preferences
        
        if macro_prefs.protein_percentage:
            protein_grams = (target_calories * macro_prefs.protein_percentage / 100) / 4
        else:
            # Default: 1.2-1.6g per kg body weight for active individuals
            protein_grams = user_profile.personal_info.weight * 1.4
        
        if macro_prefs.carb_percentage:
            carb_grams = (target_calories * macro_prefs.carb_percentage / 100) / 4
        else:
            carb_grams = (target_calories * 0.50) / 4  # 50% of calories
        
        if macro_prefs.fat_percentage:
            fat_grams = (target_calories * macro_prefs.fat_percentage / 100) / 9
        else:
            fat_grams = (target_calories * 0.25) / 9  # 25% of calories
        
        # Adjust RDA based on gender, age, and activity
        rda = NutritionalCalculator.RDA_BASE.copy()
        
        # Gender adjustments
        if user_profile.personal_info.gender == Gender.FEMALE:
            rda['iron'] = 18  # Higher iron needs for women
            rda['calcium'] = 1000
        
        # Age adjustments
        if user_profile.personal_info.age > 50:
            rda['calcium'] = 1200
            rda['vitamin_c'] = 75 if user_profile.personal_info.gender == Gender.FEMALE else 90
        
        return NutritionalInfo(
            calories=target_calories,
            protein=protein_grams,
            carbohydrates=carb_grams,
            fat=fat_grams,
            fiber=rda['fiber'],
            sodium=rda['sodium'],
            vitamin_c=rda['vitamin_c'],
            calcium=rda['calcium'],
            iron=rda['iron']
        )
    
    @staticmethod
    def analyze_nutritional_balance(meal_plan: WeeklyMealPlan, user_profile: UserProfile) -> NutritionalBalance:
        """
        Analyze nutritional balance of a meal plan against user targets.
        
        Args:
            meal_plan: WeeklyMealPlan object
            user_profile: UserProfile object
            
        Returns:
            NutritionalBalance analysis
        """
        daily_targets = NutritionalCalculator.calculate_daily_targets(user_profile)
        
        # Calculate weekly nutritional summary
        weekly_nutrition = meal_plan.calculate_nutritional_summary()
        daily_actual = weekly_nutrition.daily_averages
        
        # Analyze deficiencies and excesses
        deficiencies = []
        excesses = []
        recommendations = []
        
        # Check each nutrient
        nutrients_to_check = [
            ('calories', 'calories', 0.9, 1.1),
            ('protein', 'protein', 0.8, 2.0),
            ('carbohydrates', 'carbohydrates', 0.7, 1.3),
            ('fat', 'fat', 0.7, 1.3),
            ('fiber', 'fiber', 0.8, float('inf')),
            ('sodium', 'sodium', 0, 1.0),
            ('vitamin_c', 'vitamin C', 0.8, float('inf')),
            ('calcium', 'calcium', 0.8, float('inf')),
            ('iron', 'iron', 0.8, float('inf'))
        ]
        
        balance_scores = []
        
        for nutrient_key, nutrient_name, min_ratio, max_ratio in nutrients_to_check:
            target_value = getattr(daily_targets, nutrient_key)
            actual_value = getattr(daily_actual, nutrient_key)
            
            if target_value > 0:
                ratio = actual_value / target_value
                
                if ratio < min_ratio:
                    deficiencies.append(f"Low {nutrient_name}: {actual_value:.1f} vs target {target_value:.1f}")
                    balance_scores.append(ratio / min_ratio * 100)
                elif ratio > max_ratio:
                    excesses.append(f"High {nutrient_name}: {actual_value:.1f} vs target {target_value:.1f}")
                    balance_scores.append(min(100, 100 / (ratio / max_ratio)))
                else:
                    balance_scores.append(100)
            else:
                balance_scores.append(100)
        
        # Calculate overall balance score
        balance_score = sum(balance_scores) / len(balance_scores) if balance_scores else 0
        
        # Determine status
        if balance_score >= 90:
            status = NutritionalStatus.EXCELLENT
        elif balance_score >= 80:
            status = NutritionalStatus.GOOD
        elif balance_score >= 70:
            status = NutritionalStatus.ADEQUATE
        elif balance_score >= 60:
            status = NutritionalStatus.POOR
        else:
            status = NutritionalStatus.DEFICIENT
        
        # Generate recommendations
        if deficiencies:
            recommendations.append("Consider adding nutrient-dense foods to address deficiencies")
        
        if excesses:
            recommendations.append("Consider reducing portion sizes or substituting high-sodium/high-calorie foods")
        
        # Specific recommendations based on deficiencies
        for deficiency in deficiencies:
            if 'protein' in deficiency.lower():
                recommendations.append("Add lean proteins like chicken, fish, beans, or Greek yogurt")
            elif 'fiber' in deficiency.lower():
                recommendations.append("Include more whole grains, fruits, and vegetables")
            elif 'calcium' in deficiency.lower():
                recommendations.append("Add dairy products, leafy greens, or fortified foods")
            elif 'iron' in deficiency.lower():
                recommendations.append("Include red meat, spinach, lentils, or fortified cereals")
            elif 'vitamin c' in deficiency.lower():
                recommendations.append("Add citrus fruits, berries, or bell peppers")
        
        return NutritionalBalance(
            status=status,
            daily_targets=daily_targets,
            daily_actual=daily_actual,
            weekly_average=weekly_nutrition.weekly_totals.multiply(1/7),
            deficiencies=deficiencies,
            excesses=excesses,
            recommendations=recommendations,
            balance_score=balance_score
        )


class RecipeFormatter:
    """Utility class for recipe formatting and validation."""
    
    @staticmethod
    def format_recipe_markdown(recipe: Recipe) -> str:
        """
        Format a recipe as markdown text.
        
        Args:
            recipe: Recipe object
            
        Returns:
            Formatted markdown string
        """
        markdown = f"# {recipe.name}\n\n"
        
        if recipe.description:
            markdown += f"{recipe.description}\n\n"
        
        # Recipe info
        markdown += "## Recipe Information\n\n"
        markdown += f"- **Servings:** {recipe.servings}\n"
        markdown += f"- **Prep Time:** {recipe.prep_time} minutes\n"
        markdown += f"- **Cook Time:** {recipe.cook_time} minutes\n"
        markdown += f"- **Total Time:** {recipe.get_total_time()} minutes\n"
        markdown += f"- **Difficulty:** {recipe.difficulty_level.value.title()}\n"
        
        if recipe.cuisine_type:
            markdown += f"- **Cuisine:** {recipe.cuisine_type}\n"
        
        if recipe.tags:
            markdown += f"- **Tags:** {', '.join(recipe.tags)}\n"
        
        markdown += "\n"
        
        # Nutritional information
        nutrition = recipe.get_nutritional_info_per_serving()
        markdown += "## Nutritional Information (per serving)\n\n"
        markdown += f"- **Calories:** {nutrition.calories:.0f}\n"
        markdown += f"- **Protein:** {nutrition.protein:.1f}g\n"
        markdown += f"- **Carbohydrates:** {nutrition.carbohydrates:.1f}g\n"
        markdown += f"- **Fat:** {nutrition.fat:.1f}g\n"
        markdown += f"- **Fiber:** {nutrition.fiber:.1f}g\n"
        markdown += f"- **Sodium:** {nutrition.sodium:.0f}mg\n\n"
        
        # Ingredients
        markdown += "## Ingredients\n\n"
        for ingredient in recipe.ingredients:
            markdown += f"- {ingredient.quantity} {ingredient.unit.value} {ingredient.name}\n"
        markdown += "\n"
        
        # Instructions
        markdown += "## Instructions\n\n"
        for i, instruction in enumerate(recipe.instructions, 1):
            markdown += f"{i}. {instruction}\n"
        
        # Cost information
        cost_per_serving = recipe.get_cost_per_serving()
        if cost_per_serving > 0:
            markdown += f"\n## Cost\n\n"
            markdown += f"- **Cost per serving:** ${cost_per_serving:.2f}\n"
            markdown += f"- **Total recipe cost:** ${recipe.get_total_cost():.2f}\n"
        
        return markdown
    
    @staticmethod
    def format_meal_plan_markdown(meal_plan: WeeklyMealPlan, user_profile: UserProfile) -> str:
        """
        Format a weekly meal plan as markdown text.
        
        Args:
            meal_plan: WeeklyMealPlan object
            user_profile: UserProfile object
            
        Returns:
            Formatted markdown string
        """
        markdown = f"# Weekly Meal Plan - {meal_plan.week_start_date.strftime('%B %d, %Y')}\n\n"
        
        # Summary
        cost_breakdown = CostCalculator.calculate_weekly_cost_breakdown(meal_plan)
        nutritional_balance = NutritionalCalculator.analyze_nutritional_balance(meal_plan, user_profile)
        
        markdown += "## Summary\n\n"
        markdown += f"- **Total Weekly Cost:** ${cost_breakdown.total_cost:.2f}\n"
        markdown += f"- **Average Daily Cost:** ${cost_breakdown.weekly_average:.2f}\n"
        markdown += f"- **Nutritional Balance Score:** {nutritional_balance.balance_score:.0f}/100 ({nutritional_balance.status.value.title()})\n\n"
        
        # Daily meal plans
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i, daily_plan in enumerate(meal_plan.daily_plans):
            day_name = days[i] if i < len(days) else f"Day {i+1}"
            markdown += f"## {day_name} - {daily_plan.date.strftime('%B %d')}\n\n"
            
            daily_cost = CostCalculator.calculate_daily_cost(daily_plan)
            daily_nutrition = daily_plan.get_daily_nutrition()
            
            markdown += f"**Daily Cost:** ${daily_cost:.2f} | **Calories:** {daily_nutrition.calories:.0f}\n\n"
            
            # Meals
            if daily_plan.breakfast:
                markdown += f"### Breakfast: {daily_plan.breakfast.name}\n"
                markdown += f"*{daily_plan.breakfast.prep_time + daily_plan.breakfast.cook_time} min | "
                markdown += f"${CostCalculator.calculate_cost_per_serving(daily_plan.breakfast):.2f}*\n\n"
            
            if daily_plan.lunch:
                markdown += f"### Lunch: {daily_plan.lunch.name}\n"
                markdown += f"*{daily_plan.lunch.prep_time + daily_plan.lunch.cook_time} min | "
                markdown += f"${CostCalculator.calculate_cost_per_serving(daily_plan.lunch):.2f}*\n\n"
            
            if daily_plan.dinner:
                markdown += f"### Dinner: {daily_plan.dinner.name}\n"
                markdown += f"*{daily_plan.dinner.prep_time + daily_plan.dinner.cook_time} min | "
                markdown += f"${CostCalculator.calculate_cost_per_serving(daily_plan.dinner):.2f}*\n\n"
            
            if daily_plan.snacks:
                markdown += "### Snacks:\n"
                for snack in daily_plan.snacks:
                    markdown += f"- {snack.name} (${CostCalculator.calculate_cost_per_serving(snack):.2f})\n"
                markdown += "\n"
        
        # Shopping list
        markdown += "## Shopping List\n\n"
        shopping_list = meal_plan.generate_shopping_list()
        
        # Group by category
        grouped_items = shopping_list.group_by_category()
        
        for category, items in grouped_items.items():
            markdown += f"### {category}\n\n"
            for item in items:
                markdown += f"- {item.total_quantity:.1f} {item.unit.value} {item.ingredient_name}"
                if item.estimated_cost > 0:
                    markdown += f" (${item.estimated_cost:.2f})"
                markdown += "\n"
            markdown += "\n"
        
        markdown += f"**Total Estimated Cost:** ${shopping_list.total_estimated_cost:.2f}\n\n"
        
        # Nutritional analysis
        markdown += "## Nutritional Analysis\n\n"
        markdown += f"**Balance Score:** {nutritional_balance.balance_score:.0f}/100\n\n"
        
        if nutritional_balance.deficiencies:
            markdown += "### Areas for Improvement:\n"
            for deficiency in nutritional_balance.deficiencies:
                markdown += f"- {deficiency}\n"
            markdown += "\n"
        
        if nutritional_balance.recommendations:
            markdown += "### Recommendations:\n"
            for recommendation in nutritional_balance.recommendations:
                markdown += f"- {recommendation}\n"
            markdown += "\n"
        
        # Meal prep instructions
        if meal_plan.meal_prep_instructions:
            markdown += "## Meal Prep Instructions\n\n"
            for i, instruction in enumerate(meal_plan.meal_prep_instructions, 1):
                markdown += f"{i}. {instruction}\n"
        
        return markdown
    
    @staticmethod
    def validate_recipe(recipe: Recipe) -> List[str]:
        """
        Validate a recipe for completeness and consistency.
        
        Args:
            recipe: Recipe object to validate
            
        Returns:
            List of validation errors
        """
        errors = recipe.validate()
        
        # Additional validation checks
        
        # Check for reasonable nutritional values
        nutrition = recipe.get_nutritional_info_per_serving()
        if nutrition.calories > 2000:
            errors.append("Calories per serving seem very high (>2000)")
        elif nutrition.calories < 50:
            errors.append("Calories per serving seem very low (<50)")
        
        # Check for reasonable cooking times
        if recipe.prep_time > 180:
            errors.append("Prep time seems excessive (>3 hours)")
        if recipe.cook_time > 480:
            errors.append("Cook time seems excessive (>8 hours)")
        
        # Check for reasonable cost
        cost_per_serving = recipe.get_cost_per_serving()
        if cost_per_serving > 50:
            errors.append("Cost per serving seems very high (>$50)")
        
        # Check ingredient consistency
        protein_ingredients = 0
        for ingredient in recipe.ingredients:
            if any(protein in ingredient.name.lower() for protein in ['chicken', 'beef', 'fish', 'pork', 'tofu', 'beans', 'lentils']):
                protein_ingredients += 1
        
        if protein_ingredients == 0 and recipe.meal_type in [MealType.LUNCH, MealType.DINNER]:
            errors.append("Main meals should typically include a protein source")
        
        return errors


# Convenience functions
def calculate_meal_plan_cost(meal_plan: WeeklyMealPlan) -> float:
    """Quick function to calculate total meal plan cost."""
    return CostCalculator.calculate_weekly_cost_breakdown(meal_plan).total_cost


def check_nutritional_balance(meal_plan: WeeklyMealPlan, user_profile: UserProfile) -> float:
    """Quick function to get nutritional balance score."""
    return NutritionalCalculator.analyze_nutritional_balance(meal_plan, user_profile).balance_score


def format_recipe(recipe: Recipe) -> str:
    """Quick function to format recipe as markdown."""
    return RecipeFormatter.format_recipe_markdown(recipe)
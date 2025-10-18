"""
Recipe and meal plan data models for the Smart Recipe & Meal Planning System.

This module contains data models for recipes, ingredients, meal plans, and nutritional
information with calculation methods.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import date, datetime
import uuid


class DifficultyLevel(Enum):
    """Recipe difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MealType(Enum):
    """Types of meals."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"


class Unit(Enum):
    """Measurement units for ingredients."""
    # Weight
    GRAMS = "g"
    KILOGRAMS = "kg"
    OUNCES = "oz"
    POUNDS = "lb"
    
    # Volume
    MILLILITERS = "ml"
    LITERS = "l"
    CUPS = "cup"
    TABLESPOONS = "tbsp"
    TEASPOONS = "tsp"
    FLUID_OUNCES = "fl_oz"
    
    # Count
    PIECES = "pieces"
    ITEMS = "items"
    CLOVES = "cloves"
    SLICES = "slices"


@dataclass
class NutritionalInfo:
    """Nutritional information per serving."""
    calories: float = 0.0
    protein: float = 0.0  # grams
    carbohydrates: float = 0.0  # grams
    fat: float = 0.0  # grams
    fiber: float = 0.0  # grams
    sugar: float = 0.0  # grams
    sodium: float = 0.0  # mg
    
    # Micronutrients (optional)
    vitamin_c: Optional[float] = None  # mg
    calcium: Optional[float] = None  # mg
    iron: Optional[float] = None  # mg
    
    def validate(self) -> List[str]:
        """Validate nutritional information."""
        errors = []
        
        if self.calories < 0:
            errors.append("Calories cannot be negative")
        
        if self.protein < 0:
            errors.append("Protein cannot be negative")
        
        if self.carbohydrates < 0:
            errors.append("Carbohydrates cannot be negative")
        
        if self.fat < 0:
            errors.append("Fat cannot be negative")
        
        if self.fiber < 0:
            errors.append("Fiber cannot be negative")
        
        if self.sugar < 0:
            errors.append("Sugar cannot be negative")
        
        if self.sodium < 0:
            errors.append("Sodium cannot be negative")
        
        # Check if macros align with calories (rough validation)
        calculated_calories = (self.protein * 4) + (self.carbohydrates * 4) + (self.fat * 9)
        if abs(calculated_calories - self.calories) > (self.calories * 0.2):  # 20% tolerance
            errors.append("Macronutrient calories don't align with total calories")
        
        return errors
    
    def add(self, other: 'NutritionalInfo') -> 'NutritionalInfo':
        """Add nutritional information from another source."""
        return NutritionalInfo(
            calories=self.calories + other.calories,
            protein=self.protein + other.protein,
            carbohydrates=self.carbohydrates + other.carbohydrates,
            fat=self.fat + other.fat,
            fiber=self.fiber + other.fiber,
            sugar=self.sugar + other.sugar,
            sodium=self.sodium + other.sodium,
            vitamin_c=(self.vitamin_c or 0) + (other.vitamin_c or 0) if self.vitamin_c or other.vitamin_c else None,
            calcium=(self.calcium or 0) + (other.calcium or 0) if self.calcium or other.calcium else None,
            iron=(self.iron or 0) + (other.iron or 0) if self.iron or other.iron else None
        )
    
    def multiply(self, factor: float) -> 'NutritionalInfo':
        """Multiply nutritional information by a factor."""
        return NutritionalInfo(
            calories=self.calories * factor,
            protein=self.protein * factor,
            carbohydrates=self.carbohydrates * factor,
            fat=self.fat * factor,
            fiber=self.fiber * factor,
            sugar=self.sugar * factor,
            sodium=self.sodium * factor,
            vitamin_c=self.vitamin_c * factor if self.vitamin_c else None,
            calcium=self.calcium * factor if self.calcium else None,
            iron=self.iron * factor if self.iron else None
        )


@dataclass
class Ingredient:
    """Individual ingredient with quantity and nutritional information."""
    name: str
    quantity: float
    unit: Unit
    cost_per_unit: float = 0.0
    nutritional_info_per_unit: NutritionalInfo = field(default_factory=NutritionalInfo)
    alternatives: List[str] = field(default_factory=list)
    category: str = ""  # e.g., "protein", "vegetable", "grain"
    
    def validate(self) -> List[str]:
        """Validate ingredient data."""
        errors = []
        
        if not self.name.strip():
            errors.append("Ingredient name cannot be empty")
        
        if self.quantity <= 0:
            errors.append("Ingredient quantity must be positive")
        
        if not isinstance(self.unit, Unit):
            errors.append("Unit must be a valid Unit enum")
        
        if self.cost_per_unit < 0:
            errors.append("Cost per unit cannot be negative")
        
        # Validate nutritional info
        nutrition_errors = self.nutritional_info_per_unit.validate()
        errors.extend([f"nutritional_info: {error}" for error in nutrition_errors])
        
        return errors
    
    def get_total_cost(self) -> float:
        """Calculate total cost for this ingredient."""
        return self.quantity * self.cost_per_unit
    
    def get_total_nutrition(self) -> NutritionalInfo:
        """Calculate total nutritional information for this ingredient."""
        return self.nutritional_info_per_unit.multiply(self.quantity)


@dataclass
class Recipe:
    """Recipe with ingredients, instructions, and nutritional information."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    ingredients: List[Ingredient] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    prep_time: int = 0  # minutes
    cook_time: int = 0  # minutes
    servings: int = 1
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    cuisine_type: str = ""
    meal_type: MealType = MealType.DINNER
    tags: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate recipe data."""
        errors = []
        
        if not self.name.strip():
            errors.append("Recipe name cannot be empty")
        
        if not self.ingredients:
            errors.append("Recipe must have at least one ingredient")
        
        if not self.instructions:
            errors.append("Recipe must have at least one instruction")
        
        if self.prep_time < 0:
            errors.append("Prep time cannot be negative")
        
        if self.cook_time < 0:
            errors.append("Cook time cannot be negative")
        
        if self.servings <= 0:
            errors.append("Servings must be positive")
        
        if not isinstance(self.difficulty_level, DifficultyLevel):
            errors.append("Difficulty level must be a valid DifficultyLevel enum")
        
        if not isinstance(self.meal_type, MealType):
            errors.append("Meal type must be a valid MealType enum")
        
        # Validate ingredients
        for i, ingredient in enumerate(self.ingredients):
            ingredient_errors = ingredient.validate()
            errors.extend([f"ingredient {i+1}: {error}" for error in ingredient_errors])
        
        return errors
    
    def get_total_time(self) -> int:
        """Get total preparation and cooking time."""
        return self.prep_time + self.cook_time
    
    def get_total_cost(self) -> float:
        """Calculate total cost for the recipe."""
        return sum(ingredient.get_total_cost() for ingredient in self.ingredients)
    
    def get_cost_per_serving(self) -> float:
        """Calculate cost per serving."""
        total_cost = self.get_total_cost()
        return total_cost / self.servings if self.servings > 0 else 0
    
    def get_nutritional_info(self) -> NutritionalInfo:
        """Calculate total nutritional information for the recipe."""
        total_nutrition = NutritionalInfo()
        for ingredient in self.ingredients:
            ingredient_nutrition = ingredient.get_total_nutrition()
            total_nutrition = total_nutrition.add(ingredient_nutrition)
        return total_nutrition
    
    def get_nutritional_info_per_serving(self) -> NutritionalInfo:
        """Calculate nutritional information per serving."""
        total_nutrition = self.get_nutritional_info()
        return total_nutrition.multiply(1 / self.servings) if self.servings > 0 else total_nutrition


@dataclass
class DailyMealPlan:
    """Meal plan for a single day."""
    date: date
    breakfast: Optional[Recipe] = None
    lunch: Optional[Recipe] = None
    dinner: Optional[Recipe] = None
    snacks: List[Recipe] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate daily meal plan."""
        errors = []
        
        if not isinstance(self.date, date):
            errors.append("Date must be a valid date object")
        
        # Validate recipes if present
        recipes_to_validate = [
            ("breakfast", self.breakfast),
            ("lunch", self.lunch),
            ("dinner", self.dinner)
        ]
        
        for meal_name, recipe in recipes_to_validate:
            if recipe:
                recipe_errors = recipe.validate()
                errors.extend([f"{meal_name}: {error}" for error in recipe_errors])
        
        for i, snack in enumerate(self.snacks):
            snack_errors = snack.validate()
            errors.extend([f"snack {i+1}: {error}" for error in snack_errors])
        
        return errors
    
    def get_all_recipes(self) -> List[Recipe]:
        """Get all recipes for the day."""
        recipes = []
        if self.breakfast:
            recipes.append(self.breakfast)
        if self.lunch:
            recipes.append(self.lunch)
        if self.dinner:
            recipes.append(self.dinner)
        recipes.extend(self.snacks)
        return recipes
    
    def get_daily_nutrition(self) -> NutritionalInfo:
        """Calculate total nutritional information for the day."""
        total_nutrition = NutritionalInfo()
        for recipe in self.get_all_recipes():
            recipe_nutrition = recipe.get_nutritional_info_per_serving()
            total_nutrition = total_nutrition.add(recipe_nutrition)
        return total_nutrition
    
    def get_daily_cost(self) -> float:
        """Calculate total cost for the day."""
        return sum(recipe.get_cost_per_serving() for recipe in self.get_all_recipes())


@dataclass
class ShoppingListItem:
    """Item in a shopping list."""
    ingredient_name: str
    total_quantity: float
    unit: Unit
    estimated_cost: float = 0.0
    category: str = ""
    alternatives: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate shopping list item."""
        errors = []
        
        if not self.ingredient_name.strip():
            errors.append("Ingredient name cannot be empty")
        
        if self.total_quantity <= 0:
            errors.append("Total quantity must be positive")
        
        if not isinstance(self.unit, Unit):
            errors.append("Unit must be a valid Unit enum")
        
        if self.estimated_cost < 0:
            errors.append("Estimated cost cannot be negative")
        
        return errors


@dataclass
class ShoppingList:
    """Shopping list for a meal plan."""
    items: List[ShoppingListItem] = field(default_factory=list)
    total_estimated_cost: float = 0.0
    
    def validate(self) -> List[str]:
        """Validate shopping list."""
        errors = []
        
        for i, item in enumerate(self.items):
            item_errors = item.validate()
            errors.extend([f"item {i+1}: {error}" for error in item_errors])
        
        if self.total_estimated_cost < 0:
            errors.append("Total estimated cost cannot be negative")
        
        return errors
    
    def calculate_total_cost(self) -> float:
        """Calculate total cost from all items."""
        return sum(item.estimated_cost for item in self.items)
    
    def group_by_category(self) -> Dict[str, List[ShoppingListItem]]:
        """Group shopping list items by category."""
        grouped = {}
        for item in self.items:
            category = item.category or "Other"
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(item)
        return grouped


@dataclass
class WeeklyNutritionalSummary:
    """Nutritional summary for a week."""
    daily_averages: NutritionalInfo = field(default_factory=NutritionalInfo)
    weekly_totals: NutritionalInfo = field(default_factory=NutritionalInfo)
    daily_variations: Dict[str, float] = field(default_factory=dict)  # coefficient of variation for each nutrient
    
    def validate(self) -> List[str]:
        """Validate weekly nutritional summary."""
        errors = []
        
        daily_errors = self.daily_averages.validate()
        errors.extend([f"daily_averages: {error}" for error in daily_errors])
        
        weekly_errors = self.weekly_totals.validate()
        errors.extend([f"weekly_totals: {error}" for error in weekly_errors])
        
        return errors


@dataclass
class WeeklyMealPlan:
    """Complete weekly meal plan with shopping list and nutritional summary."""
    week_start_date: date
    daily_plans: List[DailyMealPlan] = field(default_factory=list)
    shopping_list: ShoppingList = field(default_factory=ShoppingList)
    nutritional_summary: WeeklyNutritionalSummary = field(default_factory=WeeklyNutritionalSummary)
    meal_prep_instructions: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate weekly meal plan."""
        errors = []
        
        if not isinstance(self.week_start_date, date):
            errors.append("Week start date must be a valid date object")
        
        if len(self.daily_plans) != 7:
            errors.append("Weekly meal plan must have exactly 7 daily plans")
        
        # Validate daily plans
        for i, daily_plan in enumerate(self.daily_plans):
            daily_errors = daily_plan.validate()
            errors.extend([f"day {i+1}: {error}" for error in daily_errors])
        
        # Validate shopping list
        shopping_errors = self.shopping_list.validate()
        errors.extend([f"shopping_list: {error}" for error in shopping_errors])
        
        # Validate nutritional summary
        nutrition_errors = self.nutritional_summary.validate()
        errors.extend([f"nutritional_summary: {error}" for error in nutrition_errors])
        
        return errors
    
    def get_total_cost(self) -> float:
        """Calculate total cost for the week."""
        return sum(daily_plan.get_daily_cost() for daily_plan in self.daily_plans)
    
    def get_all_recipes(self) -> List[Recipe]:
        """Get all unique recipes for the week."""
        all_recipes = []
        recipe_ids = set()
        
        for daily_plan in self.daily_plans:
            for recipe in daily_plan.get_all_recipes():
                if recipe.id not in recipe_ids:
                    all_recipes.append(recipe)
                    recipe_ids.add(recipe.id)
        
        return all_recipes
    
    def calculate_nutritional_summary(self) -> WeeklyNutritionalSummary:
        """Calculate nutritional summary for the week."""
        daily_nutritions = [daily_plan.get_daily_nutrition() for daily_plan in self.daily_plans]
        
        # Calculate weekly totals
        weekly_totals = NutritionalInfo()
        for daily_nutrition in daily_nutritions:
            weekly_totals = weekly_totals.add(daily_nutrition)
        
        # Calculate daily averages
        daily_averages = weekly_totals.multiply(1/7)
        
        # Calculate variations (coefficient of variation)
        daily_variations = {}
        nutrients = ['calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium']
        
        for nutrient in nutrients:
            values = [getattr(daily_nutrition, nutrient) for daily_nutrition in daily_nutritions]
            mean_value = sum(values) / len(values)
            if mean_value > 0:
                variance = sum((x - mean_value) ** 2 for x in values) / len(values)
                std_dev = variance ** 0.5
                daily_variations[nutrient] = std_dev / mean_value  # coefficient of variation
            else:
                daily_variations[nutrient] = 0.0
        
        return WeeklyNutritionalSummary(
            daily_averages=daily_averages,
            weekly_totals=weekly_totals,
            daily_variations=daily_variations
        )
    
    def generate_shopping_list(self) -> ShoppingList:
        """Generate consolidated shopping list from all recipes."""
        ingredient_totals = {}
        
        for daily_plan in self.daily_plans:
            for recipe in daily_plan.get_all_recipes():
                for ingredient in recipe.ingredients:
                    key = (ingredient.name.lower(), ingredient.unit)
                    
                    if key not in ingredient_totals:
                        ingredient_totals[key] = {
                            'name': ingredient.name,
                            'unit': ingredient.unit,
                            'quantity': 0.0,
                            'cost': 0.0,
                            'category': ingredient.category,
                            'alternatives': set(ingredient.alternatives)
                        }
                    
                    ingredient_totals[key]['quantity'] += ingredient.quantity
                    ingredient_totals[key]['cost'] += ingredient.get_total_cost()
                    ingredient_totals[key]['alternatives'].update(ingredient.alternatives)
        
        # Create shopping list items
        shopping_items = []
        for item_data in ingredient_totals.values():
            shopping_item = ShoppingListItem(
                ingredient_name=item_data['name'],
                total_quantity=item_data['quantity'],
                unit=item_data['unit'],
                estimated_cost=item_data['cost'],
                category=item_data['category'],
                alternatives=list(item_data['alternatives'])
            )
            shopping_items.append(shopping_item)
        
        total_cost = sum(item.estimated_cost for item in shopping_items)
        
        return ShoppingList(
            items=shopping_items,
            total_estimated_cost=total_cost
        )
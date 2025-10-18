"""
Fallback data generation for when AI agents fail
"""
from datetime import date, timedelta
from typing import List, Dict, Any
from src.models.recipe import (
    WeeklyMealPlan, DailyMealPlan, Recipe, Ingredient, Unit, 
    MealType, DifficultyLevel, NutritionalInfo, ShoppingList, ShoppingListItem
)
from src.models.user_profile import UserProfile


class FallbackMealPlanGenerator:
    """Generate basic but complete meal plans when AI agents fail"""
    
    @staticmethod
    def create_fallback_meal_plan(user_profile: UserProfile, week_start_date: date) -> WeeklyMealPlan:
        """Create a complete fallback meal plan with real recipes"""
        
        # Create basic recipes
        breakfast_recipes = FallbackMealPlanGenerator._create_breakfast_recipes()
        lunch_recipes = FallbackMealPlanGenerator._create_lunch_recipes()
        dinner_recipes = FallbackMealPlanGenerator._create_dinner_recipes()
        
        # Create daily plans
        daily_plans = []
        for i in range(7):
            current_date = week_start_date + timedelta(days=i)
            
            # Rotate through recipes
            breakfast = breakfast_recipes[i % len(breakfast_recipes)]
            lunch = lunch_recipes[i % len(lunch_recipes)]
            dinner = dinner_recipes[i % len(dinner_recipes)]
            
            daily_plan = DailyMealPlan(
                date=current_date,
                breakfast=breakfast,
                lunch=lunch,
                dinner=dinner,
                snacks=[]
            )
            daily_plans.append(daily_plan)
        
        # Create shopping list
        shopping_list = FallbackMealPlanGenerator._create_shopping_list(daily_plans)
        
        # Create meal plan
        meal_plan = WeeklyMealPlan(
            week_start_date=week_start_date,
            daily_plans=daily_plans,
            shopping_list=shopping_list,
            meal_prep_instructions=[
                "This is a basic meal plan generated when our AI system was unavailable",
                "All recipes are simple and use common ingredients",
                "Feel free to customize based on your preferences",
                "Consider meal prepping on Sunday for the week ahead"
            ]
        )
        
        return meal_plan
    
    @staticmethod
    def _create_breakfast_recipes() -> List[Recipe]:
        """Create simple breakfast recipes"""
        return [
            Recipe(
                name="Classic Oatmeal",
                description="Hearty oatmeal with banana and honey",
                ingredients=[
                    Ingredient(name="rolled oats", quantity=50, unit=Unit.GRAMS, cost_per_unit=0.02),
                    Ingredient(name="milk", quantity=200, unit=Unit.MILLILITERS, cost_per_unit=0.005),
                    Ingredient(name="banana", quantity=1, unit=Unit.PIECES, cost_per_unit=0.50),
                    Ingredient(name="honey", quantity=15, unit=Unit.GRAMS, cost_per_unit=0.20)
                ],
                instructions=[
                    "Combine oats and milk in a pot",
                    "Cook over medium heat for 5 minutes, stirring occasionally",
                    "Slice banana and add to oatmeal",
                    "Drizzle with honey and serve"
                ],
                prep_time=5,
                cook_time=5,
                servings=1,
                difficulty_level=DifficultyLevel.EASY,
                meal_type=MealType.BREAKFAST,
                tags=["healthy", "filling", "quick"]
            ),
            Recipe(
                name="Scrambled Eggs with Toast",
                description="Simple scrambled eggs with whole grain toast",
                ingredients=[
                    Ingredient(name="eggs", quantity=2, unit=Unit.PIECES, cost_per_unit=0.25),
                    Ingredient(name="whole grain bread", quantity=2, unit=Unit.PIECES, cost_per_unit=0.30),
                    Ingredient(name="butter", quantity=10, unit=Unit.GRAMS, cost_per_unit=0.15),
                    Ingredient(name="milk", quantity=30, unit=Unit.MILLILITERS, cost_per_unit=0.005)
                ],
                instructions=[
                    "Beat eggs with milk in a bowl",
                    "Heat butter in a pan over medium-low heat",
                    "Add eggs and scramble gently until set",
                    "Toast bread and serve with eggs"
                ],
                prep_time=5,
                cook_time=5,
                servings=1,
                difficulty_level=DifficultyLevel.EASY,
                meal_type=MealType.BREAKFAST,
                tags=["protein", "quick", "classic"]
            ),
            Recipe(
                name="Greek Yogurt Bowl",
                description="Protein-rich yogurt with berries and granola",
                ingredients=[
                    Ingredient(name="Greek yogurt", quantity=150, unit=Unit.GRAMS, cost_per_unit=0.015),
                    Ingredient(name="mixed berries", quantity=80, unit=Unit.GRAMS, cost_per_unit=0.08),
                    Ingredient(name="granola", quantity=30, unit=Unit.GRAMS, cost_per_unit=0.10),
                    Ingredient(name="honey", quantity=10, unit=Unit.GRAMS, cost_per_unit=0.20)
                ],
                instructions=[
                    "Place yogurt in a bowl",
                    "Top with berries and granola",
                    "Drizzle with honey",
                    "Serve immediately"
                ],
                prep_time=3,
                cook_time=0,
                servings=1,
                difficulty_level=DifficultyLevel.EASY,
                meal_type=MealType.BREAKFAST,
                tags=["healthy", "protein", "no-cook"]
            )
        ]
    
    @staticmethod
    def _create_lunch_recipes() -> List[Recipe]:
        """Create simple lunch recipes"""
        return [
            Recipe(
                name="Turkey Sandwich",
                description="Classic turkey sandwich with vegetables",
                ingredients=[
                    Ingredient(name="whole grain bread", quantity=2, unit=Unit.PIECES, cost_per_unit=0.30),
                    Ingredient(name="sliced turkey", quantity=100, unit=Unit.GRAMS, cost_per_unit=0.08),
                    Ingredient(name="lettuce", quantity=30, unit=Unit.GRAMS, cost_per_unit=0.05),
                    Ingredient(name="tomato", quantity=50, unit=Unit.GRAMS, cost_per_unit=0.04),
                    Ingredient(name="mayonnaise", quantity=15, unit=Unit.GRAMS, cost_per_unit=0.10)
                ],
                instructions=[
                    "Toast bread lightly",
                    "Spread mayonnaise on one slice",
                    "Layer turkey, lettuce, and tomato",
                    "Top with second slice and cut in half"
                ],
                prep_time=5,
                cook_time=2,
                servings=1,
                difficulty_level=DifficultyLevel.EASY,
                meal_type=MealType.LUNCH,
                tags=["protein", "quick", "portable"]
            ),
            Recipe(
                name="Chicken Caesar Salad",
                description="Fresh salad with grilled chicken",
                ingredients=[
                    Ingredient(name="romaine lettuce", quantity=100, unit=Unit.GRAMS, cost_per_unit=0.03),
                    Ingredient(name="chicken breast", quantity=120, unit=Unit.GRAMS, cost_per_unit=0.12),
                    Ingredient(name="parmesan cheese", quantity=20, unit=Unit.GRAMS, cost_per_unit=0.25),
                    Ingredient(name="caesar dressing", quantity=30, unit=Unit.GRAMS, cost_per_unit=0.15),
                    Ingredient(name="croutons", quantity=20, unit=Unit.GRAMS, cost_per_unit=0.08)
                ],
                instructions=[
                    "Season and grill chicken breast until cooked through",
                    "Chop romaine lettuce",
                    "Slice cooked chicken",
                    "Combine lettuce, chicken, cheese, and croutons",
                    "Toss with dressing and serve"
                ],
                prep_time=10,
                cook_time=8,
                servings=1,
                difficulty_level=DifficultyLevel.MEDIUM,
                meal_type=MealType.LUNCH,
                tags=["healthy", "protein", "fresh"]
            ),
            Recipe(
                name="Vegetable Soup",
                description="Hearty mixed vegetable soup",
                ingredients=[
                    Ingredient(name="mixed vegetables", quantity=200, unit=Unit.GRAMS, cost_per_unit=0.04),
                    Ingredient(name="vegetable broth", quantity=300, unit=Unit.MILLILITERS, cost_per_unit=0.008),
                    Ingredient(name="white beans", quantity=100, unit=Unit.GRAMS, cost_per_unit=0.03),
                    Ingredient(name="olive oil", quantity=10, unit=Unit.MILLILITERS, cost_per_unit=0.15)
                ],
                instructions=[
                    "Heat olive oil in a pot",
                    "Add mixed vegetables and sauté for 5 minutes",
                    "Add broth and beans",
                    "Simmer for 15 minutes until vegetables are tender",
                    "Season to taste and serve hot"
                ],
                prep_time=5,
                cook_time=20,
                servings=1,
                difficulty_level=DifficultyLevel.EASY,
                meal_type=MealType.LUNCH,
                tags=["healthy", "vegetarian", "warming"]
            )
        ]
    
    @staticmethod
    def _create_dinner_recipes() -> List[Recipe]:
        """Create simple dinner recipes"""
        return [
            Recipe(
                name="Spaghetti with Marinara",
                description="Classic pasta with tomato sauce",
                ingredients=[
                    Ingredient(name="spaghetti", quantity=100, unit=Unit.GRAMS, cost_per_unit=0.03),
                    Ingredient(name="marinara sauce", quantity=150, unit=Unit.GRAMS, cost_per_unit=0.05),
                    Ingredient(name="parmesan cheese", quantity=20, unit=Unit.GRAMS, cost_per_unit=0.25),
                    Ingredient(name="olive oil", quantity=10, unit=Unit.MILLILITERS, cost_per_unit=0.15)
                ],
                instructions=[
                    "Cook spaghetti according to package directions",
                    "Heat marinara sauce in a pan",
                    "Drain pasta and toss with sauce",
                    "Serve with grated parmesan cheese"
                ],
                prep_time=5,
                cook_time=15,
                servings=1,
                difficulty_level=DifficultyLevel.EASY,
                meal_type=MealType.DINNER,
                tags=["comfort", "quick", "filling"]
            ),
            Recipe(
                name="Baked Chicken with Rice",
                description="Simple baked chicken with steamed rice",
                ingredients=[
                    Ingredient(name="chicken thigh", quantity=150, unit=Unit.GRAMS, cost_per_unit=0.08),
                    Ingredient(name="white rice", quantity=80, unit=Unit.GRAMS, cost_per_unit=0.02),
                    Ingredient(name="mixed vegetables", quantity=100, unit=Unit.GRAMS, cost_per_unit=0.04),
                    Ingredient(name="olive oil", quantity=10, unit=Unit.MILLILITERS, cost_per_unit=0.15)
                ],
                instructions=[
                    "Preheat oven to 375°F (190°C)",
                    "Season chicken with salt and pepper",
                    "Bake chicken for 25-30 minutes",
                    "Cook rice according to package directions",
                    "Steam vegetables and serve together"
                ],
                prep_time=10,
                cook_time=30,
                servings=1,
                difficulty_level=DifficultyLevel.MEDIUM,
                meal_type=MealType.DINNER,
                tags=["protein", "balanced", "hearty"]
            ),
            Recipe(
                name="Stir-Fried Vegetables with Tofu",
                description="Healthy vegetarian stir-fry",
                ingredients=[
                    Ingredient(name="firm tofu", quantity=120, unit=Unit.GRAMS, cost_per_unit=0.06),
                    Ingredient(name="mixed stir-fry vegetables", quantity=200, unit=Unit.GRAMS, cost_per_unit=0.05),
                    Ingredient(name="soy sauce", quantity=20, unit=Unit.MILLILITERS, cost_per_unit=0.08),
                    Ingredient(name="sesame oil", quantity=10, unit=Unit.MILLILITERS, cost_per_unit=0.20),
                    Ingredient(name="brown rice", quantity=80, unit=Unit.GRAMS, cost_per_unit=0.025)
                ],
                instructions=[
                    "Cook brown rice according to package directions",
                    "Cut tofu into cubes and pan-fry until golden",
                    "Heat sesame oil in a wok or large pan",
                    "Add vegetables and stir-fry for 5 minutes",
                    "Add tofu and soy sauce, stir-fry 2 more minutes",
                    "Serve over rice"
                ],
                prep_time=10,
                cook_time=15,
                servings=1,
                difficulty_level=DifficultyLevel.MEDIUM,
                meal_type=MealType.DINNER,
                tags=["vegetarian", "healthy", "asian"]
            )
        ]
    
    @staticmethod
    def _create_shopping_list(daily_plans: List[DailyMealPlan]) -> ShoppingList:
        """Create a shopping list from daily meal plans"""
        ingredient_totals = {}
        
        # Collect all ingredients
        for daily_plan in daily_plans:
            for meal in [daily_plan.breakfast, daily_plan.lunch, daily_plan.dinner]:
                if meal:
                    for ingredient in meal.ingredients:
                        key = ingredient.name
                        if key in ingredient_totals:
                            ingredient_totals[key]['quantity'] += ingredient.quantity
                            ingredient_totals[key]['cost'] += ingredient.get_total_cost()
                        else:
                            ingredient_totals[key] = {
                                'quantity': ingredient.quantity,
                                'unit': ingredient.unit,
                                'cost': ingredient.get_total_cost()
                            }
        
        # Create shopping items
        shopping_items = []
        for name, data in ingredient_totals.items():
            item = ShoppingListItem(
                ingredient_name=name,
                total_quantity=data['quantity'],
                unit=data['unit'],
                estimated_cost=data['cost'],
                category="Groceries"
            )
            shopping_items.append(item)
        
        return ShoppingList(
            items=shopping_items,
            total_estimated_cost=sum(item.estimated_cost for item in shopping_items)
        )
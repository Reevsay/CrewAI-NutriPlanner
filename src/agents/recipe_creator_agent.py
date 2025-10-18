"""
Recipe Creator Agent for the Smart Recipe & Meal Planning System.

This module implements the Recipe Creator Agent that generates custom recipes
based on nutritional requirements, dietary preferences, and cooking constraints.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import random
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.recipe import Recipe, Ingredient, NutritionalInfo, Unit, DifficultyLevel, MealType
from ..models.user_profile import CookingSkillLevel
from ..tools.nutrition_api import NutritionAPI

# Configure logging
logger = logging.getLogger(__name__)


class RecipeGenerationInput(BaseModel):
    """Input model for recipe generation."""
    nutritional_requirements: Dict[str, float] = Field(description="Daily nutritional targets")
    dietary_restrictions: List[str] = Field(description="List of dietary restrictions")
    cooking_preferences: Dict[str, Any] = Field(description="Cooking skill level and preferences")
    meal_type: str = Field(description="Type of meal (breakfast, lunch, dinner, snack)")
    cuisine_preference: Optional[str] = Field(default=None, description="Preferred cuisine type")


class RecipeOutput(BaseModel):
    """Output model for generated recipe."""
    name: str = Field(description="Recipe name")
    description: str = Field(description="Recipe description")
    ingredients: List[Dict[str, Any]] = Field(description="List of ingredients with quantities")
    instructions: List[str] = Field(description="Step-by-step cooking instructions")
    prep_time: int = Field(description="Preparation time in minutes")
    cook_time: int = Field(description="Cooking time in minutes")
    servings: int = Field(description="Number of servings")
    difficulty_level: str = Field(description="Difficulty level (easy, medium, hard)")
    nutritional_info: Dict[str, float] = Field(description="Nutritional information per serving")
    tags: List[str] = Field(description="Recipe tags and categories")


class RecipeTemplateTool(BaseTool):
    """Tool for generating recipe templates based on meal type and preferences."""
    
    name: str = "recipe_template"
    description: str = "Generate recipe templates and ingredient combinations for different meal types"
    

    
    def _load_recipe_templates(self) -> Dict[str, Dict]:
        """Load recipe templates for different meal types and cuisines."""
        return {
            'breakfast': {
                'protein_bowl': {
                    'base': ['oats', 'quinoa', 'greek_yogurt'],
                    'protein': ['eggs', 'protein_powder', 'nuts', 'seeds'],
                    'fruits': ['berries', 'banana', 'apple', 'mango'],
                    'extras': ['honey', 'cinnamon', 'vanilla']
                },
                'scrambled_eggs': {
                    'base': ['eggs'],
                    'vegetables': ['spinach', 'tomatoes', 'bell_peppers', 'onions'],
                    'protein': ['cheese', 'ham', 'turkey'],
                    'extras': ['herbs', 'olive_oil']
                },
                'smoothie': {
                    'base': ['banana', 'berries'],
                    'liquid': ['almond_milk', 'coconut_milk', 'water'],
                    'protein': ['protein_powder', 'greek_yogurt', 'peanut_butter'],
                    'extras': ['spinach', 'chia_seeds', 'honey']
                }
            },
            'lunch': {
                'salad_bowl': {
                    'base': ['mixed_greens', 'spinach', 'arugula'],
                    'protein': ['chicken_breast', 'salmon', 'tofu', 'chickpeas'],
                    'vegetables': ['cucumber', 'tomatoes', 'carrots', 'bell_peppers'],
                    'healthy_fats': ['avocado', 'nuts', 'olive_oil', 'seeds'],
                    'extras': ['lemon', 'herbs', 'balsamic_vinegar']
                },
                'grain_bowl': {
                    'base': ['quinoa', 'brown_rice', 'farro'],
                    'protein': ['chicken', 'fish', 'beans', 'lentils'],
                    'vegetables': ['roasted_vegetables', 'steamed_broccoli', 'sauteed_spinach'],
                    'sauce': ['tahini', 'pesto', 'vinaigrette']
                },
                'soup': {
                    'base': ['vegetable_broth', 'chicken_broth'],
                    'protein': ['chicken', 'beans', 'lentils'],
                    'vegetables': ['carrots', 'celery', 'onions', 'tomatoes'],
                    'grains': ['rice', 'pasta', 'barley']
                }
            },
            'dinner': {
                'protein_and_sides': {
                    'protein': ['salmon', 'chicken_breast', 'lean_beef', 'tofu'],
                    'starch': ['sweet_potato', 'quinoa', 'brown_rice'],
                    'vegetables': ['broccoli', 'asparagus', 'green_beans', 'brussels_sprouts'],
                    'cooking_method': ['grilled', 'baked', 'roasted', 'sauteed']
                },
                'stir_fry': {
                    'protein': ['chicken', 'shrimp', 'tofu', 'beef'],
                    'vegetables': ['bell_peppers', 'broccoli', 'snap_peas', 'carrots'],
                    'base': ['brown_rice', 'quinoa', 'noodles'],
                    'sauce': ['soy_sauce', 'teriyaki', 'garlic_ginger']
                },
                'pasta': {
                    'base': ['whole_wheat_pasta', 'zucchini_noodles'],
                    'protein': ['chicken', 'shrimp', 'ground_turkey'],
                    'vegetables': ['spinach', 'tomatoes', 'mushrooms'],
                    'sauce': ['marinara', 'pesto', 'olive_oil_garlic']
                }
            },
            'snack': {
                'protein_snack': {
                    'base': ['greek_yogurt', 'cottage_cheese', 'hummus'],
                    'additions': ['berries', 'nuts', 'vegetables', 'whole_grain_crackers']
                },
                'energy_balls': {
                    'base': ['dates', 'oats'],
                    'protein': ['protein_powder', 'nut_butter'],
                    'extras': ['coconut', 'chia_seeds', 'dark_chocolate']
                }
            }
        }
    
    def _run(self, meal_type: str, dietary_restrictions: List[str], cuisine_preference: str = None) -> str:
        """
        Generate recipe template suggestions.
        
        Args:
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            dietary_restrictions: List of dietary restrictions
            cuisine_preference: Preferred cuisine type
            
        Returns:
            Recipe template suggestions
        """
        try:
            recipe_templates = self._load_recipe_templates()
            meal_templates = recipe_templates.get(meal_type.lower(), {})
            
            if not meal_templates:
                return f"No templates available for meal type: {meal_type}"
            
            # Filter templates based on dietary restrictions
            suitable_templates = []
            
            for template_name, template_data in meal_templates.items():
                is_suitable = True
                
                # Check dietary restrictions
                if 'vegetarian' in dietary_restrictions:
                    meat_items = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'shrimp', 'ham', 'turkey']
                    for category in template_data.values():
                        if isinstance(category, list):
                            if any(meat in item.lower() for item in category for meat in meat_items):
                                is_suitable = False
                                break
                
                if 'vegan' in dietary_restrictions:
                    animal_items = ['eggs', 'cheese', 'greek_yogurt', 'cottage_cheese', 'milk', 'honey']
                    for category in template_data.values():
                        if isinstance(category, list):
                            if any(animal in item.lower() for item in category for animal in animal_items):
                                is_suitable = False
                                break
                
                if 'gluten_free' in dietary_restrictions:
                    gluten_items = ['pasta', 'wheat', 'oats', 'barley']
                    for category in template_data.values():
                        if isinstance(category, list):
                            if any(gluten in item.lower() for item in category for gluten in gluten_items):
                                is_suitable = False
                                break
                
                if is_suitable:
                    suitable_templates.append((template_name, template_data))
            
            if not suitable_templates:
                return f"No suitable templates found for {meal_type} with restrictions: {dietary_restrictions}"
            
            # Format output
            result = f"Suitable {meal_type} recipe templates:\n\n"
            
            for template_name, template_data in suitable_templates:
                result += f"**{template_name.replace('_', ' ').title()}:**\n"
                for category, items in template_data.items():
                    if isinstance(items, list):
                        result += f"- {category.replace('_', ' ').title()}: {', '.join(items)}\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate recipe template: {e}")
            return f"Error generating recipe template: {str(e)}"


class IngredientSubstitutionTool(BaseTool):
    """Tool for suggesting ingredient substitutions based on dietary restrictions."""
    
    name: str = "ingredient_substitution"
    description: str = "Suggest ingredient substitutions for dietary restrictions and preferences"
    

    
    def _load_substitutions(self) -> Dict[str, Dict[str, List[str]]]:
        """Load ingredient substitution mappings."""
        return {
            'vegetarian': {
                'chicken': ['tofu', 'tempeh', 'seitan', 'mushrooms', 'chickpeas'],
                'beef': ['lentils', 'black_beans', 'portobello_mushrooms', 'tempeh'],
                'fish': ['tofu', 'tempeh', 'hearts_of_palm', 'mushrooms'],
                'pork': ['tempeh', 'mushrooms', 'jackfruit']
            },
            'vegan': {
                'eggs': ['flax_eggs', 'chia_eggs', 'applesauce', 'banana'],
                'milk': ['almond_milk', 'oat_milk', 'coconut_milk', 'soy_milk'],
                'cheese': ['nutritional_yeast', 'cashew_cheese', 'vegan_cheese'],
                'butter': ['coconut_oil', 'vegan_butter', 'olive_oil'],
                'honey': ['maple_syrup', 'agave_nectar', 'date_syrup'],
                'yogurt': ['coconut_yogurt', 'almond_yogurt', 'cashew_yogurt']
            },
            'gluten_free': {
                'wheat_flour': ['almond_flour', 'coconut_flour', 'rice_flour', 'oat_flour'],
                'pasta': ['rice_noodles', 'quinoa_pasta', 'zucchini_noodles'],
                'bread': ['gluten_free_bread', 'lettuce_wraps', 'rice_cakes'],
                'oats': ['quinoa_flakes', 'rice_cereal', 'millet_flakes']
            },
            'dairy_free': {
                'milk': ['almond_milk', 'coconut_milk', 'oat_milk', 'rice_milk'],
                'cheese': ['nutritional_yeast', 'dairy_free_cheese', 'cashew_cream'],
                'butter': ['coconut_oil', 'olive_oil', 'avocado'],
                'yogurt': ['coconut_yogurt', 'almond_yogurt']
            },
            'low_carb': {
                'rice': ['cauliflower_rice', 'shirataki_rice', 'broccoli_rice'],
                'pasta': ['zucchini_noodles', 'spaghetti_squash', 'shirataki_noodles'],
                'bread': ['lettuce_wraps', 'portobello_caps', 'cauliflower_bread'],
                'potatoes': ['cauliflower', 'turnips', 'radishes']
            }
        }
    
    def _run(self, ingredient: str, dietary_restrictions: List[str]) -> str:
        """
        Suggest substitutions for an ingredient based on dietary restrictions.
        
        Args:
            ingredient: Original ingredient name
            dietary_restrictions: List of dietary restrictions
            
        Returns:
            Substitution suggestions
        """
        try:
            suggestions = []
            ingredient_lower = ingredient.lower().replace(' ', '_')
            
            substitutions = self._load_substitutions()
            for restriction in dietary_restrictions:
                restriction_subs = substitutions.get(restriction.lower(), {})
                
                # Check for direct matches
                if ingredient_lower in restriction_subs:
                    suggestions.extend(restriction_subs[ingredient_lower])
                
                # Check for partial matches
                for key, subs in restriction_subs.items():
                    if key in ingredient_lower or ingredient_lower in key:
                        suggestions.extend(subs)
            
            if suggestions:
                unique_suggestions = list(set(suggestions))
                return f"Substitutions for {ingredient}: {', '.join(unique_suggestions)}"
            else:
                return f"No specific substitutions needed for {ingredient} with restrictions: {dietary_restrictions}"
                
        except Exception as e:
            logger.error(f"Failed to find substitutions for {ingredient}: {e}")
            return f"Error finding substitutions: {str(e)}"


class RecipeNutritionCalculatorTool(BaseTool):
    """Tool for calculating nutritional information of recipes."""
    
    name: str = "recipe_nutrition_calculator"
    description: str = "Calculate nutritional information for a recipe based on its ingredients"
    
    def _run(self, ingredients: List[Dict[str, Any]], servings: int = 1) -> str:
        """
        Calculate nutritional information for a recipe.
        
        Args:
            ingredients: List of ingredients with quantities
            servings: Number of servings the recipe makes
            
        Returns:
            Nutritional information summary
        """
        try:
            total_nutrition = NutritionalInfo()
            
            for ingredient_data in ingredients:
                name = ingredient_data.get('name', '')
                quantity = ingredient_data.get('quantity', 0)
                
                # Get nutrition data for ingredient
                nutrition_api = NutritionAPI()
                nutrition_info = nutrition_api.get_food_nutrition(name, quantity)
                total_nutrition = total_nutrition.add(nutrition_info)
            
            # Calculate per serving
            per_serving = total_nutrition.multiply(1 / servings) if servings > 0 else total_nutrition
            
            result = f"Nutritional Information (per serving, {servings} servings total):\n"
            result += f"- Calories: {per_serving.calories:.0f}\n"
            result += f"- Protein: {per_serving.protein:.1f}g\n"
            result += f"- Carbohydrates: {per_serving.carbohydrates:.1f}g\n"
            result += f"- Fat: {per_serving.fat:.1f}g\n"
            result += f"- Fiber: {per_serving.fiber:.1f}g\n"
            result += f"- Sodium: {per_serving.sodium:.0f}mg\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate recipe nutrition: {e}")
            return f"Error calculating nutrition: {str(e)}"


class CookingInstructionsTool(BaseTool):
    """Tool for generating cooking instructions based on ingredients and cooking method."""
    
    name: str = "cooking_instructions"
    description: str = "Generate step-by-step cooking instructions for recipes"
    
    def _run(self, recipe_type: str, ingredients: List[str], cooking_method: str, difficulty: str) -> str:
        """
        Generate cooking instructions.
        
        Args:
            recipe_type: Type of recipe (salad, stir_fry, baked_protein, etc.)
            ingredients: List of main ingredients
            cooking_method: Primary cooking method
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            Step-by-step cooking instructions
        """
        try:
            instructions = []
            
            # Basic instruction templates based on recipe type
            if recipe_type.lower() == 'salad':
                instructions = [
                    "Wash and prepare all vegetables by chopping into bite-sized pieces",
                    "If using protein, cook according to package directions and let cool",
                    "Combine all ingredients in a large bowl",
                    "Add dressing and toss gently to combine",
                    "Serve immediately or chill for 30 minutes before serving"
                ]
            
            elif recipe_type.lower() == 'stir_fry':
                instructions = [
                    "Prepare all ingredients by cutting into uniform pieces",
                    "Heat oil in a large wok or skillet over medium-high heat",
                    "Add protein and cook until nearly done, then remove and set aside",
                    "Add harder vegetables first, cooking for 2-3 minutes",
                    "Add softer vegetables and cook for another 2-3 minutes",
                    "Return protein to pan and add sauce",
                    "Stir-fry for 1-2 minutes until everything is heated through",
                    "Serve immediately over rice or noodles"
                ]
            
            elif recipe_type.lower() == 'baked_protein':
                instructions = [
                    "Preheat oven to 375°F (190°C)",
                    "Season protein with salt, pepper, and desired spices",
                    "Place protein on a baking sheet lined with parchment paper",
                    "If using vegetables, toss with oil and seasonings and add to sheet",
                    "Bake for 20-25 minutes or until protein reaches safe internal temperature",
                    "Let rest for 5 minutes before serving",
                    "Serve with prepared sides"
                ]
            
            elif recipe_type.lower() == 'soup':
                instructions = [
                    "Heat oil in a large pot over medium heat",
                    "Add onions and cook until softened, about 5 minutes",
                    "Add other vegetables and cook for 5-7 minutes",
                    "Add broth and bring to a boil",
                    "Add protein and grains if using",
                    "Reduce heat and simmer for 15-20 minutes",
                    "Season with salt, pepper, and herbs to taste",
                    "Serve hot with bread or crackers"
                ]
            
            elif recipe_type.lower() == 'smoothie':
                instructions = [
                    "Add liquid ingredients to blender first",
                    "Add frozen fruits and vegetables",
                    "Add protein powder or other supplements",
                    "Blend on high speed for 60-90 seconds until smooth",
                    "Add ice if needed for desired consistency",
                    "Taste and adjust sweetness if needed",
                    "Pour into glasses and serve immediately"
                ]
            
            else:
                # Generic instructions
                instructions = [
                    "Prepare all ingredients according to recipe specifications",
                    "Follow the primary cooking method for the main components",
                    "Combine ingredients as specified",
                    "Cook until done and season to taste",
                    "Serve as directed"
                ]
            
            # Adjust complexity based on difficulty level
            if difficulty.lower() == 'easy':
                # Keep instructions simple
                pass
            elif difficulty.lower() == 'hard':
                # Add more detailed steps
                detailed_instructions = []
                for instruction in instructions:
                    detailed_instructions.append(instruction)
                    if 'cook' in instruction.lower():
                        detailed_instructions.append("Monitor temperature and adjust heat as needed")
                instructions = detailed_instructions
            
            return "\n".join([f"{i+1}. {instruction}" for i, instruction in enumerate(instructions)])
            
        except Exception as e:
            logger.error(f"Failed to generate cooking instructions: {e}")
            return f"Error generating instructions: {str(e)}"


def create_recipe_creator_agent() -> Agent:
    """
    Create and configure the Recipe Creator Agent.
    
    Returns:
        Configured CrewAI Agent for recipe creation
    """
    
    # Initialize tools
    recipe_template_tool = RecipeTemplateTool()
    substitution_tool = IngredientSubstitutionTool()
    nutrition_calculator_tool = RecipeNutritionCalculatorTool()
    cooking_instructions_tool = CookingInstructionsTool()
    
    tools = [
        recipe_template_tool,
        substitution_tool,
        nutrition_calculator_tool,
        cooking_instructions_tool
    ]
    
    agent = Agent(
        role="Culinary Recipe Developer and Chef",
        goal="Create balanced, delicious recipes that meet specific nutritional requirements and dietary preferences",
        backstory="""You are a professional chef and recipe developer with over 12 years of experience in 
        creating healthy, nutritious meals. You specialize in adapting recipes for various dietary restrictions 
        and nutritional goals while maintaining flavor and appeal. Your expertise includes understanding 
        ingredient interactions, cooking techniques, and nutritional balance. You have worked in both 
        restaurant kitchens and as a private chef, giving you insight into both professional techniques 
        and home cooking practicalities. You stay current with food trends and nutritional science to 
        create recipes that are both healthy and delicious.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=True
    )
    
    return agent


def create_recipe_generation_task(
    nutritional_requirements: Dict[str, float],
    dietary_restrictions: List[str],
    cooking_preferences: Dict[str, Any],
    meal_type: str,
    cuisine_preference: Optional[str] = None
) -> Task:
    """
    Create a task for recipe generation.
    
    Args:
        nutritional_requirements: Daily nutritional targets
        dietary_restrictions: List of dietary restrictions
        cooking_preferences: Cooking skill level and preferences
        meal_type: Type of meal to create
        cuisine_preference: Preferred cuisine type
        
    Returns:
        CrewAI Task for recipe generation
    """
    
    task = Task(
        description=f"""
        Create a custom recipe that meets the specified nutritional requirements and dietary preferences.
        
        Requirements:
        - Nutritional targets: {nutritional_requirements}
        - Dietary restrictions: {dietary_restrictions}
        - Cooking preferences: {cooking_preferences}
        - Meal type: {meal_type}
        - Cuisine preference: {cuisine_preference or 'Any'}
        
        Your recipe should:
        
        1. Meet the nutritional targets as closely as possible
        2. Respect all dietary restrictions and allergies
        3. Match the specified meal type and cooking skill level
        4. Include complete ingredient list with quantities
        5. Provide clear, step-by-step cooking instructions
        6. Be practical for home cooking
        7. Use readily available ingredients
        8. Consider cooking time constraints
        
        Use the available tools to:
        - Generate appropriate recipe templates
        - Find suitable ingredient substitutions
        - Calculate nutritional information
        - Create detailed cooking instructions
        
        Ensure the recipe is balanced, flavorful, and achievable for the target cooking skill level.
        """,
        expected_output="""
        A complete recipe containing:
        
        1. **Recipe Name:** Creative and descriptive name
        
        2. **Description:** Brief description highlighting key features and benefits
        
        3. **Recipe Information:**
           - Servings: [number]
           - Prep time: [minutes]
           - Cook time: [minutes]
           - Difficulty level: [easy/medium/hard]
           - Cuisine type: [if applicable]
        
        4. **Ingredients:** Complete list with specific quantities and units
        
        5. **Instructions:** Clear, numbered step-by-step cooking instructions
        
        6. **Nutritional Information:** Per serving breakdown of calories, macronutrients, and key micronutrients
        
        7. **Tags:** Relevant tags (e.g., gluten-free, high-protein, quick, etc.)
        
        8. **Tips:** Any helpful cooking tips or variations
        
        The recipe should be formatted clearly and be ready for implementation in the meal planning system.
        """,
        agent=create_recipe_creator_agent(),
        output_pydantic=RecipeOutput
    )
    
    return task


# Utility functions for integration
def generate_recipe(
    nutritional_requirements: Dict[str, float],
    dietary_restrictions: List[str],
    cooking_skill: CookingSkillLevel,
    meal_type: MealType,
    cuisine_preference: Optional[str] = None
) -> Recipe:
    """
    Generate a recipe using the Recipe Creator Agent.
    
    Args:
        nutritional_requirements: Nutritional targets
        dietary_restrictions: List of dietary restrictions
        cooking_skill: User's cooking skill level
        meal_type: Type of meal to create
        cuisine_preference: Preferred cuisine type
        
    Returns:
        Generated Recipe object
    """
    try:
        cooking_preferences = {
            'skill_level': cooking_skill.value,
            'max_prep_time': 30 if cooking_skill == CookingSkillLevel.BEGINNER else 60,
            'max_cook_time': 45 if cooking_skill == CookingSkillLevel.BEGINNER else 90
        }
        
        # Create and execute task
        task = create_recipe_generation_task(
            nutritional_requirements=nutritional_requirements,
            dietary_restrictions=dietary_restrictions,
            cooking_preferences=cooking_preferences,
            meal_type=meal_type.value,
            cuisine_preference=cuisine_preference
        )
        
        # For now, return a sample recipe
        # In a full CrewAI implementation, this would execute the task
        return _generate_sample_recipe(meal_type, dietary_restrictions, cooking_skill)
        
    except Exception as e:
        logger.error(f"Failed to generate recipe: {e}")
        raise


def _generate_sample_recipe(meal_type: MealType, dietary_restrictions: List[str], cooking_skill: CookingSkillLevel) -> Recipe:
    """Generate a sample recipe for testing purposes."""
    
    # Sample recipe based on meal type
    if meal_type == MealType.BREAKFAST:
        recipe = Recipe(
            name="Protein-Packed Breakfast Bowl",
            description="A nutritious breakfast bowl with oats, berries, and protein",
            ingredients=[
                Ingredient(name="rolled oats", quantity=50, unit=Unit.GRAMS, cost_per_unit=0.02),
                Ingredient(name="greek yogurt", quantity=150, unit=Unit.GRAMS, cost_per_unit=0.01),
                Ingredient(name="mixed berries", quantity=100, unit=Unit.GRAMS, cost_per_unit=0.05),
                Ingredient(name="almonds", quantity=20, unit=Unit.GRAMS, cost_per_unit=0.15),
                Ingredient(name="honey", quantity=15, unit=Unit.GRAMS, cost_per_unit=0.20)
            ],
            instructions=[
                "Cook oats according to package directions",
                "Let oats cool slightly and transfer to bowl",
                "Top with Greek yogurt",
                "Add mixed berries and chopped almonds",
                "Drizzle with honey and serve"
            ],
            prep_time=5,
            cook_time=10,
            servings=1,
            difficulty_level=DifficultyLevel.EASY,
            meal_type=meal_type,
            tags=["high-protein", "breakfast", "healthy"]
        )
    
    elif meal_type == MealType.LUNCH:
        recipe = Recipe(
            name="Mediterranean Quinoa Salad",
            description="Fresh and healthy quinoa salad with Mediterranean flavors",
            ingredients=[
                Ingredient(name="quinoa", quantity=100, unit=Unit.GRAMS, cost_per_unit=0.08),
                Ingredient(name="cucumber", quantity=150, unit=Unit.GRAMS, cost_per_unit=0.02),
                Ingredient(name="cherry tomatoes", quantity=100, unit=Unit.GRAMS, cost_per_unit=0.04),
                Ingredient(name="feta cheese", quantity=50, unit=Unit.GRAMS, cost_per_unit=0.12),
                Ingredient(name="olive oil", quantity=15, unit=Unit.MILLILITERS, cost_per_unit=0.05),
                Ingredient(name="lemon juice", quantity=15, unit=Unit.MILLILITERS, cost_per_unit=0.03)
            ],
            instructions=[
                "Cook quinoa according to package directions and let cool",
                "Dice cucumber and halve cherry tomatoes",
                "Combine quinoa, cucumber, and tomatoes in a bowl",
                "Crumble feta cheese over the salad",
                "Whisk olive oil and lemon juice together",
                "Dress salad and toss gently",
                "Serve chilled or at room temperature"
            ],
            prep_time=15,
            cook_time=15,
            servings=2,
            difficulty_level=DifficultyLevel.EASY,
            meal_type=meal_type,
            tags=["mediterranean", "vegetarian", "gluten-free"]
        )
    
    else:  # DINNER
        recipe = Recipe(
            name="Baked Salmon with Roasted Vegetables",
            description="Healthy baked salmon with colorful roasted vegetables",
            ingredients=[
                Ingredient(name="salmon fillet", quantity=150, unit=Unit.GRAMS, cost_per_unit=0.20),
                Ingredient(name="broccoli", quantity=200, unit=Unit.GRAMS, cost_per_unit=0.03),
                Ingredient(name="bell peppers", quantity=150, unit=Unit.GRAMS, cost_per_unit=0.04),
                Ingredient(name="olive oil", quantity=20, unit=Unit.MILLILITERS, cost_per_unit=0.05),
                Ingredient(name="lemon", quantity=50, unit=Unit.GRAMS, cost_per_unit=0.02)
            ],
            instructions=[
                "Preheat oven to 400°F (200°C)",
                "Cut vegetables into uniform pieces",
                "Toss vegetables with half the olive oil and season",
                "Place vegetables on baking sheet and roast for 15 minutes",
                "Season salmon with salt, pepper, and remaining oil",
                "Add salmon to baking sheet with vegetables",
                "Bake for 12-15 minutes until salmon flakes easily",
                "Serve with lemon wedges"
            ],
            prep_time=10,
            cook_time=25,
            servings=1,
            difficulty_level=DifficultyLevel.MEDIUM,
            meal_type=meal_type,
            tags=["high-protein", "omega-3", "gluten-free"]
        )
    
    # Apply dietary restriction modifications
    if 'vegetarian' in dietary_restrictions and meal_type == MealType.DINNER:
        # Replace salmon with tofu
        recipe.name = "Baked Tofu with Roasted Vegetables"
        recipe.ingredients[0] = Ingredient(name="firm tofu", quantity=150, unit=Unit.GRAMS, cost_per_unit=0.08)
    
    if 'vegan' in dietary_restrictions:
        # Remove dairy and animal products
        recipe.ingredients = [ing for ing in recipe.ingredients if 'cheese' not in ing.name.lower() and 'yogurt' not in ing.name.lower()]
        if 'honey' in [ing.name for ing in recipe.ingredients]:
            # Replace honey with maple syrup
            for ing in recipe.ingredients:
                if ing.name == 'honey':
                    ing.name = 'maple syrup'
    
    return recipe
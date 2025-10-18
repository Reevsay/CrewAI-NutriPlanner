"""
Ingredient Sourcer Agent for the Smart Recipe & Meal Planning System.

This module implements the Ingredient Sourcer Agent that researches ingredient
availability, prices, and alternatives for meal planning optimization.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.recipe import Ingredient, Unit
from ..models.user_profile import PriceSensitivity
from ..tools.grocery_price_api import GroceryPriceAPI

# Configure logging
logger = logging.getLogger(__name__)


class IngredientAvailabilityInput(BaseModel):
    """Input model for ingredient availability research."""
    ingredients: List[Dict[str, Any]] = Field(description="List of ingredients to research")
    location: Optional[str] = Field(default=None, description="User location for price lookup")
    budget_constraints: Dict[str, Any] = Field(description="Budget constraints and preferences")


class IngredientAvailabilityOutput(BaseModel):
    """Output model for ingredient availability research."""
    ingredient_prices: Dict[str, float] = Field(description="Current prices for ingredients")
    availability_status: Dict[str, str] = Field(description="Availability status for each ingredient")
    price_alternatives: Dict[str, List[str]] = Field(description="Lower-cost alternatives for expensive ingredients")
    seasonal_considerations: List[str] = Field(description="Seasonal availability notes")
    shopping_recommendations: List[str] = Field(description="Shopping tips and recommendations")
    total_estimated_cost: float = Field(description="Total estimated cost for all ingredients")
    budget_optimization_suggestions: List[str] = Field(description="Suggestions for budget optimization")


class PriceLookupTool(BaseTool):
    """Tool for looking up current ingredient prices."""
    
    name: str = "price_lookup"
    description: str = "Look up current prices for ingredients at various stores"
    
    def _run(self, ingredient_name: str, quantity: float, unit: str, location: str = None) -> str:
        """
        Look up price for an ingredient.
        
        Args:
            ingredient_name: Name of the ingredient
            quantity: Quantity needed
            unit: Unit of measurement
            location: Location for price lookup
            
        Returns:
            Price information string
        """
        try:
            grocery_api = GroceryPriceAPI()
            price_data = grocery_api.get_ingredient_price(
                ingredient_name, quantity, unit, location
            )
            
            if price_data:
                result = f"Price information for {quantity} {unit} of {ingredient_name}:\n"
                result += f"- Average price: ${price_data.get('average_price', 0):.2f}\n"
                result += f"- Price range: ${price_data.get('min_price', 0):.2f} - ${price_data.get('max_price', 0):.2f}\n"
                
                if price_data.get('stores'):
                    result += "- Available at: " + ", ".join(price_data['stores']) + "\n"
                
                if price_data.get('availability') == 'limited':
                    result += "- Limited availability - consider alternatives\n"
                elif price_data.get('availability') == 'out_of_stock':
                    result += "- Currently out of stock at most locations\n"
                
                return result
            else:
                return f"Price information not available for {ingredient_name}"
                
        except Exception as e:
            logger.error(f"Failed to lookup price for {ingredient_name}: {e}")
            return f"Error looking up price for {ingredient_name}: {str(e)}"


class AvailabilityCheckerTool(BaseTool):
    """Tool for checking ingredient availability and seasonal considerations."""
    
    name: str = "availability_checker"
    description: str = "Check ingredient availability and seasonal considerations"
    

    
    def _load_seasonal_data(self) -> Dict[str, Dict[str, List[str]]]:
        """Load seasonal availability data for common ingredients."""
        return {
            'fruits': {
                'spring': ['strawberries', 'apricots', 'rhubarb', 'asparagus'],
                'summer': ['berries', 'stone_fruits', 'melons', 'tomatoes', 'corn', 'zucchini'],
                'fall': ['apples', 'pears', 'pumpkins', 'squash', 'cranberries'],
                'winter': ['citrus', 'pomegranates', 'persimmons', 'root_vegetables']
            },
            'vegetables': {
                'spring': ['asparagus', 'peas', 'artichokes', 'spring_onions'],
                'summer': ['tomatoes', 'peppers', 'eggplant', 'cucumber', 'zucchini'],
                'fall': ['brussels_sprouts', 'cauliflower', 'broccoli', 'cabbage'],
                'winter': ['kale', 'collards', 'turnips', 'parsnips', 'carrots']
            }
        }
    
    def _load_availability_data(self) -> Dict[str, str]:
        """Load general availability data for ingredients."""
        return {
            # Always available
            'rice': 'always_available',
            'pasta': 'always_available',
            'oats': 'always_available',
            'flour': 'always_available',
            'eggs': 'always_available',
            'milk': 'always_available',
            'chicken': 'always_available',
            'ground_beef': 'always_available',
            'canned_beans': 'always_available',
            'frozen_vegetables': 'always_available',
            
            # Seasonal
            'fresh_berries': 'seasonal',
            'stone_fruits': 'seasonal',
            'asparagus': 'seasonal',
            'corn': 'seasonal',
            
            # Sometimes limited
            'specialty_grains': 'limited',
            'exotic_fruits': 'limited',
            'specialty_cheeses': 'limited',
            'fresh_herbs': 'limited'
        }
    
    def _run(self, ingredient_name: str, season: str = 'current') -> str:
        """
        Check availability and seasonal considerations for an ingredient.
        
        Args:
            ingredient_name: Name of the ingredient
            season: Current season (spring, summer, fall, winter)
            
        Returns:
            Availability information
        """
        try:
            ingredient_lower = ingredient_name.lower().replace(' ', '_')
            
            # Load data locally
            seasonal_data = self._load_seasonal_data()
            availability_data = self._load_availability_data()
            
            # Check general availability
            availability = availability_data.get(ingredient_lower, 'unknown')
            
            result = f"Availability for {ingredient_name}:\n"
            
            if availability == 'always_available':
                result += "- Available year-round at most stores\n"
            elif availability == 'seasonal':
                result += "- Seasonal availability - check current season\n"
                
                # Check seasonal data
                for category, seasons in seasonal_data.items():
                    for season_name, ingredients in seasons.items():
                        if any(ing in ingredient_lower for ing in ingredients):
                            result += f"- Best season: {season_name}\n"
                            break
                            
            elif availability == 'limited':
                result += "- Limited availability - may need to check specialty stores\n"
            else:
                result += "- Availability unknown - recommend checking multiple stores\n"
            
            # Add seasonal recommendations
            if season != 'current':
                seasonal_items = []
                for category, seasons in seasonal_data.items():
                    seasonal_items.extend(seasons.get(season, []))
                
                if any(item in ingredient_lower for item in seasonal_items):
                    result += f"- In season for {season} - expect better prices and quality\n"
                else:
                    result += f"- Out of season for {season} - may be more expensive\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to check availability for {ingredient_name}: {e}")
            return f"Error checking availability: {str(e)}"


class AlternativeFinderTool(BaseTool):
    """Tool for finding ingredient alternatives and substitutions."""
    
    name: str = "alternative_finder"
    description: str = "Find alternative ingredients for budget optimization or availability issues"
    

    
    def _load_alternatives(self) -> Dict[str, Dict[str, List[str]]]:
        """Load ingredient alternatives organized by category and reason."""
        return {
            'budget_alternatives': {
                'salmon': ['canned_salmon', 'sardines', 'mackerel', 'tilapia'],
                'beef': ['ground_turkey', 'chicken_thighs', 'lentils', 'beans'],
                'fresh_berries': ['frozen_berries', 'dried_berries', 'seasonal_fruits'],
                'nuts': ['seeds', 'nut_butters', 'roasted_chickpeas'],
                'organic_vegetables': ['conventional_vegetables', 'frozen_vegetables'],
                'specialty_cheese': ['regular_cheese', 'nutritional_yeast'],
                'fresh_herbs': ['dried_herbs', 'herb_pastes', 'frozen_herbs']
            },
            'availability_alternatives': {
                'fresh_spinach': ['frozen_spinach', 'kale', 'arugula', 'swiss_chard'],
                'fresh_basil': ['dried_basil', 'pesto', 'oregano', 'parsley'],
                'avocado': ['olive_oil', 'nuts', 'seeds', 'hummus'],
                'quinoa': ['brown_rice', 'farro', 'bulgur', 'barley'],
                'coconut_milk': ['almond_milk', 'cashew_milk', 'oat_milk'],
                'specialty_flour': ['all_purpose_flour', 'whole_wheat_flour']
            },
            'nutritional_alternatives': {
                'high_protein': {
                    'chicken': ['tofu', 'tempeh', 'seitan', 'beans', 'lentils'],
                    'fish': ['hemp_seeds', 'chia_seeds', 'walnuts', 'flax_seeds'],
                    'dairy': ['plant_milk', 'nutritional_yeast', 'tahini']
                },
                'low_carb': {
                    'rice': ['cauliflower_rice', 'shirataki_rice', 'quinoa'],
                    'pasta': ['zucchini_noodles', 'spaghetti_squash', 'shirataki_noodles'],
                    'bread': ['lettuce_wraps', 'portobello_caps', 'cauliflower_bread']
                }
            }
        }
    
    def _run(self, ingredient_name: str, reason: str = 'budget', dietary_restrictions: List[str] = None) -> str:
        """
        Find alternatives for an ingredient.
        
        Args:
            ingredient_name: Original ingredient name
            reason: Reason for substitution (budget, availability, nutrition)
            dietary_restrictions: List of dietary restrictions to consider
            
        Returns:
            Alternative suggestions
        """
        try:
            ingredient_lower = ingredient_name.lower().replace(' ', '_')
            dietary_restrictions = dietary_restrictions or []
            
            # Load alternatives data locally
            alternatives_data = self._load_alternatives()
            alternatives = []
            
            # Check budget alternatives
            if reason in ['budget', 'cost']:
                budget_alts = alternatives_data['budget_alternatives']
                for key, alts in budget_alts.items():
                    if key in ingredient_lower or ingredient_lower in key:
                        alternatives.extend(alts)
            
            # Check availability alternatives
            elif reason in ['availability', 'unavailable']:
                avail_alts = alternatives_data['availability_alternatives']
                for key, alts in avail_alts.items():
                    if key in ingredient_lower or ingredient_lower in key:
                        alternatives.extend(alts)
            
            # Check nutritional alternatives
            elif reason in ['nutrition', 'dietary']:
                for category, category_alts in alternatives_data['nutritional_alternatives'].items():
                    for key, alts in category_alts.items():
                        if key in ingredient_lower or ingredient_lower in key:
                            alternatives.extend(alts)
            
            # Filter based on dietary restrictions
            if dietary_restrictions:
                filtered_alternatives = []
                for alt in alternatives:
                    is_suitable = True
                    
                    if 'vegetarian' in dietary_restrictions:
                        meat_items = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey']
                        if any(meat in alt.lower() for meat in meat_items):
                            is_suitable = False
                    
                    if 'vegan' in dietary_restrictions:
                        animal_items = ['cheese', 'milk', 'dairy', 'yogurt', 'butter']
                        if any(animal in alt.lower() for animal in animal_items):
                            is_suitable = False
                    
                    if 'gluten_free' in dietary_restrictions:
                        gluten_items = ['wheat', 'flour', 'bread', 'pasta']
                        if any(gluten in alt.lower() for gluten in gluten_items):
                            is_suitable = False
                    
                    if is_suitable:
                        filtered_alternatives.append(alt)
                
                alternatives = filtered_alternatives
            
            if alternatives:
                unique_alternatives = list(set(alternatives))
                result = f"Alternatives for {ingredient_name} ({reason}):\n"
                for alt in unique_alternatives[:5]:  # Limit to top 5
                    result += f"- {alt.replace('_', ' ').title()}\n"
                return result
            else:
                return f"No suitable alternatives found for {ingredient_name}"
                
        except Exception as e:
            logger.error(f"Failed to find alternatives for {ingredient_name}: {e}")
            return f"Error finding alternatives: {str(e)}"


class BudgetOptimizerTool(BaseTool):
    """Tool for optimizing ingredient costs within budget constraints."""
    
    name: str = "budget_optimizer"
    description: str = "Optimize ingredient selection to fit within budget constraints"
    
    def _run(self, ingredients: List[Dict[str, Any]], budget: float, price_sensitivity: str) -> str:
        """
        Optimize ingredient selection for budget.
        
        Args:
            ingredients: List of ingredients with prices
            budget: Available budget
            price_sensitivity: Price sensitivity level (low, medium, high)
            
        Returns:
            Budget optimization recommendations
        """
        try:
            total_cost = sum(ing.get('cost', 0) for ing in ingredients)
            
            result = f"Budget Analysis:\n"
            result += f"- Total estimated cost: ${total_cost:.2f}\n"
            result += f"- Available budget: ${budget:.2f}\n"
            
            if total_cost <= budget:
                result += "- Budget status: Within budget ✓\n"
                remaining = budget - total_cost
                result += f"- Remaining budget: ${remaining:.2f}\n"
            else:
                overage = total_cost - budget
                result += f"- Budget status: Over budget by ${overage:.2f} ✗\n"
                
                # Provide optimization suggestions
                result += "\nOptimization suggestions:\n"
                
                # Find most expensive ingredients
                expensive_ingredients = sorted(
                    ingredients, 
                    key=lambda x: x.get('cost', 0), 
                    reverse=True
                )[:3]
                
                for ing in expensive_ingredients:
                    cost = ing.get('cost', 0)
                    if cost > budget * 0.2:  # If ingredient costs more than 20% of budget
                        result += f"- Consider alternatives for {ing.get('name', 'unknown')} (${cost:.2f})\n"
                
                # General suggestions based on price sensitivity
                if price_sensitivity == 'high':
                    result += "- Shop at discount stores or use coupons\n"
                    result += "- Buy generic/store brands when possible\n"
                    result += "- Consider frozen alternatives to fresh produce\n"
                elif price_sensitivity == 'medium':
                    result += "- Look for sales and seasonal discounts\n"
                    result += "- Consider buying in bulk for non-perishables\n"
                else:  # low sensitivity
                    result += "- Focus on nutritional value over cost\n"
                    result += "- Consider premium alternatives if within budget\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize budget: {e}")
            return f"Error optimizing budget: {str(e)}"


def create_ingredient_sourcer_agent() -> Agent:
    """
    Create and configure the Ingredient Sourcer Agent.
    
    Returns:
        Configured CrewAI Agent for ingredient sourcing
    """
    
    # Initialize tools
    price_lookup_tool = PriceLookupTool()
    availability_checker_tool = AvailabilityCheckerTool()
    alternative_finder_tool = AlternativeFinderTool()
    budget_optimizer_tool = BudgetOptimizerTool()
    
    tools = [
        price_lookup_tool,
        availability_checker_tool,
        alternative_finder_tool,
        budget_optimizer_tool
    ]
    
    agent = Agent(
        role="Grocery Procurement Specialist and Ingredient Researcher",
        goal="Research ingredient availability, prices, and alternatives to optimize meal planning within budget constraints",
        backstory="""You are an experienced grocery procurement specialist with over 10 years of experience 
        in food sourcing and supply chain management. You have worked with both commercial kitchens and 
        individual meal planning services, giving you deep knowledge of ingredient availability, seasonal 
        pricing patterns, and cost optimization strategies. You understand how to find the best deals, 
        identify quality alternatives, and work within various budget constraints while maintaining 
        nutritional and quality standards. Your expertise includes knowledge of seasonal produce cycles, 
        store pricing strategies, and ingredient substitution principles.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=True
    )
    
    return agent


def create_ingredient_sourcing_task(
    ingredients: List[Dict[str, Any]],
    location: Optional[str],
    budget_constraints: Dict[str, Any]
) -> Task:
    """
    Create a task for ingredient sourcing and availability research.
    
    Args:
        ingredients: List of ingredients to research
        location: User location for price lookup
        budget_constraints: Budget constraints and preferences
        
    Returns:
        CrewAI Task for ingredient sourcing
    """
    
    task = Task(
        description=f"""
        Research ingredient availability, pricing, and alternatives for the provided ingredient list.
        
        Ingredients to research: {ingredients}
        Location: {location or 'General US market'}
        Budget constraints: {budget_constraints}
        
        Your research should include:
        
        1. Current price lookup for each ingredient
        2. Availability status and seasonal considerations
        3. Alternative ingredients for budget optimization
        4. Shopping recommendations and tips
        5. Total cost estimation and budget analysis
        6. Substitution suggestions for unavailable items
        
        Use the available tools to:
        - Look up current prices at various stores
        - Check availability and seasonal factors
        - Find suitable alternatives for expensive or unavailable items
        - Optimize the ingredient list within budget constraints
        
        Consider the user's price sensitivity and shopping preferences when making recommendations.
        Focus on maintaining nutritional value while optimizing for cost and availability.
        """,
        expected_output="""
        A comprehensive ingredient sourcing report containing:
        
        1. **Price Analysis:**
           - Current prices for each ingredient
           - Total estimated cost
           - Price ranges and store comparisons
        
        2. **Availability Assessment:**
           - Availability status for each ingredient
           - Seasonal considerations and timing
           - Store recommendations for hard-to-find items
        
        3. **Budget Optimization:**
           - Budget status (within/over budget)
           - Cost-saving alternatives for expensive ingredients
           - Bulk buying opportunities
        
        4. **Alternative Recommendations:**
           - Suitable substitutions for unavailable items
           - Lower-cost alternatives that maintain nutritional value
           - Seasonal alternatives for better pricing
        
        5. **Shopping Strategy:**
           - Best stores for each ingredient category
           - Timing recommendations for seasonal items
           - Money-saving tips and strategies
        
        6. **Final Recommendations:**
           - Optimized ingredient list within budget
           - Priority substitutions to make
           - Shopping list organized by store/section
        
        Format the output to be actionable for meal planning and shopping list generation.
        """,
        agent=create_ingredient_sourcer_agent(),
        output_pydantic=IngredientAvailabilityOutput
    )
    
    return task


# Utility functions for integration
def research_ingredients(
    ingredients: List[Ingredient],
    location: Optional[str],
    weekly_budget: float,
    price_sensitivity: PriceSensitivity
) -> IngredientAvailabilityOutput:
    """
    Research ingredient availability and pricing using the Ingredient Sourcer Agent.
    
    Args:
        ingredients: List of Ingredient objects to research
        location: User location for price lookup
        weekly_budget: Available weekly budget
        price_sensitivity: User's price sensitivity level
        
    Returns:
        IngredientAvailabilityOutput with research results
    """
    try:
        # Convert ingredients to dictionary format
        ingredient_data = []
        for ingredient in ingredients:
            ingredient_data.append({
                'name': ingredient.name,
                'quantity': ingredient.quantity,
                'unit': ingredient.unit.value,
                'cost': ingredient.cost_per_unit * ingredient.quantity
            })
        
        budget_constraints = {
            'weekly_budget': weekly_budget,
            'price_sensitivity': price_sensitivity.value
        }
        
        # Create and execute task
        task = create_ingredient_sourcing_task(
            ingredients=ingredient_data,
            location=location,
            budget_constraints=budget_constraints
        )
        
        # For now, return sample data
        # In a full CrewAI implementation, this would execute the task
        return _generate_sample_sourcing_data(ingredient_data, weekly_budget)
        
    except Exception as e:
        logger.error(f"Failed to research ingredients: {e}")
        raise


def _generate_sample_sourcing_data(ingredients: List[Dict[str, Any]], budget: float) -> IngredientAvailabilityOutput:
    """Generate sample sourcing data for testing purposes."""
    
    # Calculate sample prices and availability
    ingredient_prices = {}
    availability_status = {}
    price_alternatives = {}
    total_cost = 0
    
    for ingredient in ingredients:
        name = ingredient['name']
        cost = ingredient.get('cost', 0)
        
        # Sample price calculation
        base_price = cost if cost > 0 else 2.50  # Default price
        ingredient_prices[name] = base_price
        total_cost += base_price
        
        # Sample availability
        if 'exotic' in name.lower() or 'specialty' in name.lower():
            availability_status[name] = 'limited'
        else:
            availability_status[name] = 'available'
        
        # Sample alternatives for expensive items
        if base_price > 5.00:
            if 'salmon' in name.lower():
                price_alternatives[name] = ['canned salmon', 'sardines', 'mackerel']
            elif 'beef' in name.lower():
                price_alternatives[name] = ['ground turkey', 'chicken thighs', 'lentils']
            else:
                price_alternatives[name] = ['generic brand', 'frozen alternative']
    
    # Generate recommendations
    shopping_recommendations = [
        "Shop at discount grocery stores for basic ingredients",
        "Buy seasonal produce for better prices",
        "Consider frozen alternatives for out-of-season items",
        "Use store loyalty programs for additional savings"
    ]
    
    budget_optimization_suggestions = []
    if total_cost > budget:
        overage = total_cost - budget
        budget_optimization_suggestions = [
            f"Reduce costs by ${overage:.2f} to stay within budget",
            "Consider generic brands for packaged items",
            "Replace expensive proteins with plant-based alternatives",
            "Buy in bulk for non-perishable items"
        ]
    else:
        budget_optimization_suggestions = [
            "Budget allows for some premium ingredients",
            "Consider organic options for priority items"
        ]
    
    return IngredientAvailabilityOutput(
        ingredient_prices=ingredient_prices,
        availability_status=availability_status,
        price_alternatives=price_alternatives,
        seasonal_considerations=[
            "Berries are in season - expect lower prices",
            "Root vegetables are at peak availability",
            "Citrus fruits are currently in season"
        ],
        shopping_recommendations=shopping_recommendations,
        total_estimated_cost=total_cost,
        budget_optimization_suggestions=budget_optimization_suggestions
    )
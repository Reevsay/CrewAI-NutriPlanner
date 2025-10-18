"""
Cost Calculator Agent for the Smart Recipe & Meal Planning System.

This module implements the Cost Calculator Agent that analyzes meal costs,
optimizes budget allocation, and provides cost-effective meal planning strategies.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.recipe import Recipe, WeeklyMealPlan, DailyMealPlan
from ..models.user_profile import PriceSensitivity
from ..tools.calculation_tools import CostCalculator, BudgetOptimization

# Configure logging
logger = logging.getLogger(__name__)


class CostAnalysisInput(BaseModel):
    """Input model for cost analysis."""
    recipes: List[Dict[str, Any]] = Field(description="List of recipes with ingredient costs")
    meal_plan: Optional[Dict[str, Any]] = Field(default=None, description="Weekly meal plan data")
    budget_constraints: Dict[str, Any] = Field(description="Budget constraints and preferences")


class CostAnalysisOutput(BaseModel):
    """Output model for cost analysis."""
    total_weekly_cost: float = Field(description="Total weekly meal plan cost")
    daily_cost_breakdown: List[float] = Field(description="Cost breakdown by day")
    cost_per_meal_type: Dict[str, float] = Field(description="Cost breakdown by meal type")
    cost_per_serving: float = Field(description="Average cost per serving")
    budget_status: str = Field(description="Budget status (within/over/under)")
    budget_utilization: float = Field(description="Percentage of budget used")
    cost_optimization_opportunities: List[str] = Field(description="Opportunities to reduce costs")
    expensive_ingredients: List[Dict[str, float]] = Field(description="Most expensive ingredients")
    cost_saving_recommendations: List[str] = Field(description="Specific cost-saving recommendations")
    weekly_budget_allocation: Dict[str, float] = Field(description="Recommended budget allocation by category")


class RecipeCostCalculatorTool(BaseTool):
    """Tool for calculating individual recipe costs."""
    
    name: str = "recipe_cost_calculator"
    description: str = "Calculate total cost and cost per serving for individual recipes"
    
    def _run(self, recipe_data: Dict[str, Any]) -> str:
        """
        Calculate cost for a single recipe.
        
        Args:
            recipe_data: Dictionary containing recipe information
            
        Returns:
            Cost calculation results
        """
        try:
            ingredients = recipe_data.get('ingredients', [])
            servings = recipe_data.get('servings', 1)
            recipe_name = recipe_data.get('name', 'Unknown Recipe')
            
            total_cost = 0.0
            ingredient_costs = []
            
            for ingredient in ingredients:
                quantity = ingredient.get('quantity', 0)
                cost_per_unit = ingredient.get('cost_per_unit', 0)
                name = ingredient.get('name', 'Unknown')
                
                ingredient_cost = quantity * cost_per_unit
                total_cost += ingredient_cost
                
                ingredient_costs.append({
                    'name': name,
                    'cost': ingredient_cost,
                    'quantity': quantity
                })
            
            cost_per_serving = total_cost / servings if servings > 0 else 0
            
            result = f"Cost analysis for {recipe_name}:\n"
            result += f"- Total recipe cost: ${total_cost:.2f}\n"
            result += f"- Cost per serving: ${cost_per_serving:.2f}\n"
            result += f"- Number of servings: {servings}\n\n"
            
            # Show most expensive ingredients
            expensive_ingredients = sorted(ingredient_costs, key=lambda x: x['cost'], reverse=True)[:3]
            result += "Most expensive ingredients:\n"
            for ing in expensive_ingredients:
                result += f"- {ing['name']}: ${ing['cost']:.2f}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate recipe cost: {e}")
            return f"Error calculating recipe cost: {str(e)}"


class MealPlanCostAnalyzerTool(BaseTool):
    """Tool for analyzing weekly meal plan costs."""
    
    name: str = "meal_plan_cost_analyzer"
    description: str = "Analyze costs for complete weekly meal plans"
    
    def _run(self, meal_plan_data: Dict[str, Any]) -> str:
        """
        Analyze costs for a weekly meal plan.
        
        Args:
            meal_plan_data: Dictionary containing meal plan information
            
        Returns:
            Comprehensive cost analysis
        """
        try:
            daily_plans = meal_plan_data.get('daily_plans', [])
            
            total_weekly_cost = 0.0
            daily_costs = []
            meal_type_costs = {
                'breakfast': 0.0,
                'lunch': 0.0,
                'dinner': 0.0,
                'snacks': 0.0
            }
            
            all_ingredients = {}
            
            for day_data in daily_plans:
                daily_cost = 0.0
                
                # Process each meal type
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    meal = day_data.get(meal_type)
                    if meal:
                        meal_cost = self._calculate_meal_cost(meal)
                        daily_cost += meal_cost
                        meal_type_costs[meal_type] += meal_cost
                        
                        # Track ingredients
                        for ingredient in meal.get('ingredients', []):
                            name = ingredient.get('name', '')
                            cost = ingredient.get('quantity', 0) * ingredient.get('cost_per_unit', 0)
                            all_ingredients[name] = all_ingredients.get(name, 0) + cost
                
                # Process snacks
                snacks = day_data.get('snacks', [])
                for snack in snacks:
                    snack_cost = self._calculate_meal_cost(snack)
                    daily_cost += snack_cost
                    meal_type_costs['snacks'] += snack_cost
                    
                    for ingredient in snack.get('ingredients', []):
                        name = ingredient.get('name', '')
                        cost = ingredient.get('quantity', 0) * ingredient.get('cost_per_unit', 0)
                        all_ingredients[name] = all_ingredients.get(name, 0) + cost
                
                daily_costs.append(daily_cost)
                total_weekly_cost += daily_cost
            
            # Calculate averages and statistics
            avg_daily_cost = total_weekly_cost / 7 if daily_costs else 0
            total_servings = sum(len(daily_plans) * 3 for _ in daily_plans)  # Approximate
            avg_cost_per_serving = total_weekly_cost / total_servings if total_servings > 0 else 0
            
            result = f"Weekly Meal Plan Cost Analysis:\n"
            result += f"- Total weekly cost: ${total_weekly_cost:.2f}\n"
            result += f"- Average daily cost: ${avg_daily_cost:.2f}\n"
            result += f"- Average cost per serving: ${avg_cost_per_serving:.2f}\n\n"
            
            result += "Daily cost breakdown:\n"
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for i, cost in enumerate(daily_costs):
                day_name = days[i] if i < len(days) else f"Day {i+1}"
                result += f"- {day_name}: ${cost:.2f}\n"
            
            result += "\nCost by meal type:\n"
            for meal_type, cost in meal_type_costs.items():
                percentage = (cost / total_weekly_cost * 100) if total_weekly_cost > 0 else 0
                result += f"- {meal_type.title()}: ${cost:.2f} ({percentage:.1f}%)\n"
            
            # Show most expensive ingredients
            expensive_ingredients = sorted(all_ingredients.items(), key=lambda x: x[1], reverse=True)[:5]
            result += "\nMost expensive ingredients:\n"
            for name, cost in expensive_ingredients:
                percentage = (cost / total_weekly_cost * 100) if total_weekly_cost > 0 else 0
                result += f"- {name}: ${cost:.2f} ({percentage:.1f}%)\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze meal plan costs: {e}")
            return f"Error analyzing meal plan costs: {str(e)}"
    
    def _calculate_meal_cost(self, meal_data: Dict[str, Any]) -> float:
        """Calculate cost for a single meal."""
        ingredients = meal_data.get('ingredients', [])
        servings = meal_data.get('servings', 1)
        
        total_cost = 0.0
        for ingredient in ingredients:
            quantity = ingredient.get('quantity', 0)
            cost_per_unit = ingredient.get('cost_per_unit', 0)
            total_cost += quantity * cost_per_unit
        
        return total_cost / servings if servings > 0 else total_cost


class BudgetOptimizerTool(BaseTool):
    """Tool for optimizing meal plans within budget constraints."""
    
    name: str = "budget_optimizer"
    description: str = "Optimize meal plans to fit within specified budget constraints"
    
    def _run(self, current_cost: float, target_budget: float, price_sensitivity: str) -> str:
        """
        Provide budget optimization recommendations.
        
        Args:
            current_cost: Current total cost
            target_budget: Target budget amount
            price_sensitivity: Price sensitivity level
            
        Returns:
            Budget optimization recommendations
        """
        try:
            budget_difference = current_cost - target_budget
            utilization = (current_cost / target_budget * 100) if target_budget > 0 else 0
            
            result = f"Budget Optimization Analysis:\n"
            result += f"- Current cost: ${current_cost:.2f}\n"
            result += f"- Target budget: ${target_budget:.2f}\n"
            result += f"- Budget utilization: {utilization:.1f}%\n"
            
            if budget_difference > 0:
                result += f"- Over budget by: ${budget_difference:.2f}\n\n"
                result += "Optimization recommendations:\n"
                
                # Provide recommendations based on price sensitivity
                if price_sensitivity == 'high':
                    result += "- Switch to generic/store brands for packaged items\n"
                    result += "- Use frozen vegetables instead of fresh when possible\n"
                    result += "- Choose cheaper protein sources (beans, lentils, eggs)\n"
                    result += "- Shop at discount grocery stores\n"
                    result += "- Use coupons and take advantage of sales\n"
                elif price_sensitivity == 'medium':
                    result += "- Look for sales on preferred items\n"
                    result += "- Consider seasonal produce for better prices\n"
                    result += "- Buy in bulk for non-perishables\n"
                    result += "- Mix premium and budget ingredients\n"
                else:  # low sensitivity
                    result += "- Focus on reducing portion sizes slightly\n"
                    result += "- Choose less expensive cuts of premium proteins\n"
                    result += "- Reduce frequency of expensive ingredients\n"
                
                # Calculate required savings percentage
                savings_needed = (budget_difference / current_cost * 100)
                result += f"\nTarget cost reduction: {savings_needed:.1f}%\n"
                
            elif budget_difference < -10:  # Significantly under budget
                result += f"- Under budget by: ${abs(budget_difference):.2f}\n\n"
                result += "Budget enhancement opportunities:\n"
                result += "- Consider organic or premium ingredients\n"
                result += "- Add more variety to meals\n"
                result += "- Include specialty or gourmet items\n"
                result += "- Increase portion sizes if desired\n"
            else:
                result += "- Budget is well-balanced ✓\n"
                result += "- Current spending is optimal for the budget\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize budget: {e}")
            return f"Error optimizing budget: {str(e)}"


class CostComparisonTool(BaseTool):
    """Tool for comparing costs across different meal options."""
    
    name: str = "cost_comparison"
    description: str = "Compare costs between different meal options and alternatives"
    
    def _run(self, meal_options: List[Dict[str, Any]]) -> str:
        """
        Compare costs between different meal options.
        
        Args:
            meal_options: List of meal options with cost data
            
        Returns:
            Cost comparison analysis
        """
        try:
            if len(meal_options) < 2:
                return "Need at least 2 meal options for comparison"
            
            result = "Cost Comparison Analysis:\n\n"
            
            # Calculate costs for each option
            option_costs = []
            for i, option in enumerate(meal_options):
                name = option.get('name', f'Option {i+1}')
                ingredients = option.get('ingredients', [])
                servings = option.get('servings', 1)
                
                total_cost = sum(
                    ing.get('quantity', 0) * ing.get('cost_per_unit', 0)
                    for ing in ingredients
                )
                cost_per_serving = total_cost / servings if servings > 0 else 0
                
                option_costs.append({
                    'name': name,
                    'total_cost': total_cost,
                    'cost_per_serving': cost_per_serving,
                    'servings': servings
                })
            
            # Sort by cost per serving
            option_costs.sort(key=lambda x: x['cost_per_serving'])
            
            result += "Options ranked by cost per serving:\n"
            for i, option in enumerate(option_costs):
                rank = i + 1
                result += f"{rank}. {option['name']}: ${option['cost_per_serving']:.2f} per serving\n"
                result += f"   Total cost: ${option['total_cost']:.2f} ({option['servings']} servings)\n"
            
            # Calculate savings
            cheapest = option_costs[0]
            most_expensive = option_costs[-1]
            
            if len(option_costs) > 1:
                savings_per_serving = most_expensive['cost_per_serving'] - cheapest['cost_per_serving']
                savings_percentage = (savings_per_serving / most_expensive['cost_per_serving'] * 100)
                
                result += f"\nPotential savings:\n"
                result += f"- Save ${savings_per_serving:.2f} per serving ({savings_percentage:.1f}%)\n"
                result += f"- Choose '{cheapest['name']}' over '{most_expensive['name']}'\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to compare costs: {e}")
            return f"Error comparing costs: {str(e)}"


def create_cost_calculator_agent() -> Agent:
    """
    Create and configure the Cost Calculator Agent.
    
    Returns:
        Configured CrewAI Agent for cost analysis
    """
    
    # Initialize tools
    recipe_cost_tool = RecipeCostCalculatorTool()
    meal_plan_analyzer_tool = MealPlanCostAnalyzerTool()
    budget_optimizer_tool = BudgetOptimizerTool()
    cost_comparison_tool = CostComparisonTool()
    
    tools = [
        recipe_cost_tool,
        meal_plan_analyzer_tool,
        budget_optimizer_tool,
        cost_comparison_tool
    ]
    
    agent = Agent(
        role="Financial Analyst and Budget Optimization Specialist",
        goal="Analyze meal costs, optimize budget allocation, and provide cost-effective meal planning strategies",
        backstory="""You are a financial analyst specializing in food budgeting and cost optimization with 
        over 8 years of experience in helping individuals and families manage their food expenses effectively. 
        Your expertise includes analyzing food costs, identifying cost-saving opportunities, and developing 
        budget-conscious meal planning strategies. You understand the relationship between nutrition, quality, 
        and cost, and can help people make informed decisions about their food spending. You have worked with 
        various income levels and dietary needs, giving you insight into practical budgeting strategies that 
        don't compromise on health or satisfaction.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=True
    )
    
    return agent


def create_cost_analysis_task(
    recipes: List[Dict[str, Any]],
    meal_plan: Optional[Dict[str, Any]],
    budget_constraints: Dict[str, Any]
) -> Task:
    """
    Create a task for cost analysis and budget optimization.
    
    Args:
        recipes: List of recipes with ingredient costs
        meal_plan: Weekly meal plan data
        budget_constraints: Budget constraints and preferences
        
    Returns:
        CrewAI Task for cost analysis
    """
    
    task = Task(
        description=f"""
        Analyze the costs of the provided recipes and meal plan, and provide comprehensive budget optimization recommendations.
        
        Recipes to analyze: {len(recipes)} recipes
        Meal plan: {'Provided' if meal_plan else 'Individual recipes only'}
        Budget constraints: {budget_constraints}
        
        Your analysis should include:
        
        1. Calculate total costs for individual recipes and the complete meal plan
        2. Break down costs by day, meal type, and ingredient categories
        3. Identify the most expensive ingredients and cost drivers
        4. Analyze budget utilization and identify over/under budget situations
        5. Provide specific cost optimization recommendations
        6. Suggest ingredient substitutions for budget savings
        7. Compare cost-effectiveness of different meal options
        8. Recommend optimal budget allocation strategies
        
        Use the available tools to:
        - Calculate precise costs for recipes and meal plans
        - Analyze budget performance against targets
        - Identify optimization opportunities
        - Compare costs between alternatives
        
        Focus on practical, actionable recommendations that maintain nutritional value while optimizing costs.
        Consider the user's price sensitivity and budget constraints in all recommendations.
        """,
        expected_output="""
        A comprehensive cost analysis report containing:
        
        1. **Cost Summary:**
           - Total weekly meal plan cost
           - Average daily cost
           - Cost per serving breakdown
           - Budget utilization percentage
        
        2. **Detailed Cost Breakdown:**
           - Daily cost analysis
           - Cost by meal type (breakfast, lunch, dinner, snacks)
           - Most expensive ingredients and their impact
        
        3. **Budget Analysis:**
           - Budget status (within/over/under budget)
           - Areas of highest spending
           - Cost drivers and expensive items
        
        4. **Optimization Opportunities:**
           - Specific cost-saving recommendations
           - Ingredient substitution suggestions
           - Shopping strategy improvements
        
        5. **Budget Allocation Recommendations:**
           - Optimal spending distribution by meal type
           - Priority areas for cost reduction
           - Investment opportunities for better value
        
        6. **Action Items:**
           - Immediate cost-reduction steps
           - Long-term budget optimization strategies
           - Monitoring and adjustment recommendations
        
        Format the output to be actionable for meal planning and budget management.
        """,
        agent=create_cost_calculator_agent(),
        output_pydantic=CostAnalysisOutput
    )
    
    return task


# Utility functions for integration
def analyze_meal_plan_costs(
    recipes: List[Recipe],
    weekly_budget: float,
    price_sensitivity: PriceSensitivity
) -> CostAnalysisOutput:
    """
    Analyze costs for a list of recipes using the Cost Calculator Agent.
    
    Args:
        recipes: List of Recipe objects to analyze
        weekly_budget: Available weekly budget
        price_sensitivity: User's price sensitivity level
        
    Returns:
        CostAnalysisOutput with cost analysis results
    """
    try:
        # Convert recipes to dictionary format
        recipe_data = []
        for recipe in recipes:
            recipe_dict = {
                'name': recipe.name,
                'servings': recipe.servings,
                'ingredients': []
            }
            
            for ingredient in recipe.ingredients:
                recipe_dict['ingredients'].append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity,
                    'cost_per_unit': ingredient.cost_per_unit
                })
            
            recipe_data.append(recipe_dict)
        
        budget_constraints = {
            'weekly_budget': weekly_budget,
            'price_sensitivity': price_sensitivity.value
        }
        
        # Create and execute task
        task = create_cost_analysis_task(
            recipes=recipe_data,
            meal_plan=None,
            budget_constraints=budget_constraints
        )
        
        # For now, return calculated values directly
        # In a full CrewAI implementation, this would execute the task
        return _generate_sample_cost_analysis(recipe_data, weekly_budget)
        
    except Exception as e:
        logger.error(f"Failed to analyze meal plan costs: {e}")
        raise


def _generate_sample_cost_analysis(recipes: List[Dict[str, Any]], budget: float) -> CostAnalysisOutput:
    """Generate sample cost analysis for testing purposes."""
    
    # Calculate total costs
    total_weekly_cost = 0.0
    daily_costs = []
    cost_per_meal_type = {'breakfast': 0.0, 'lunch': 0.0, 'dinner': 0.0, 'snacks': 0.0}
    expensive_ingredients = []
    
    # Simulate 7 days of meals
    for day in range(7):
        daily_cost = 0.0
        
        # Assign recipes to meal types (simplified)
        for i, recipe in enumerate(recipes[:3]):  # Use first 3 recipes per day
            meal_cost = sum(
                ing.get('quantity', 0) * ing.get('cost_per_unit', 0)
                for ing in recipe.get('ingredients', [])
            ) / recipe.get('servings', 1)
            
            daily_cost += meal_cost
            
            # Assign to meal type
            if i == 0:
                cost_per_meal_type['breakfast'] += meal_cost
            elif i == 1:
                cost_per_meal_type['lunch'] += meal_cost
            else:
                cost_per_meal_type['dinner'] += meal_cost
        
        daily_costs.append(daily_cost)
        total_weekly_cost += daily_cost
    
    # Calculate expensive ingredients
    all_ingredients = {}
    for recipe in recipes:
        for ingredient in recipe.get('ingredients', []):
            name = ingredient.get('name', '')
            cost = ingredient.get('quantity', 0) * ingredient.get('cost_per_unit', 0)
            all_ingredients[name] = all_ingredients.get(name, 0) + cost
    
    expensive_ingredients = [
        {ingredient: cost} for ingredient, cost in 
        sorted(all_ingredients.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Determine budget status
    if total_weekly_cost <= budget:
        budget_status = "within_budget"
    else:
        budget_status = "over_budget"
    
    budget_utilization = (total_weekly_cost / budget * 100) if budget > 0 else 0
    
    # Generate recommendations
    cost_optimization_opportunities = [
        "Replace expensive proteins with plant-based alternatives",
        "Use seasonal produce for better prices",
        "Buy generic brands for packaged items"
    ]
    
    cost_saving_recommendations = [
        "Shop at discount grocery stores",
        "Use coupons and loyalty programs",
        "Buy in bulk for non-perishables",
        "Plan meals around sales and promotions"
    ]
    
    weekly_budget_allocation = {
        'breakfast': budget * 0.20,
        'lunch': budget * 0.30,
        'dinner': budget * 0.40,
        'snacks': budget * 0.10
    }
    
    return CostAnalysisOutput(
        total_weekly_cost=total_weekly_cost,
        daily_cost_breakdown=daily_costs,
        cost_per_meal_type=cost_per_meal_type,
        cost_per_serving=total_weekly_cost / (len(recipes) * 7) if recipes else 0,
        budget_status=budget_status,
        budget_utilization=budget_utilization,
        cost_optimization_opportunities=cost_optimization_opportunities,
        expensive_ingredients=expensive_ingredients,
        cost_saving_recommendations=cost_saving_recommendations,
        weekly_budget_allocation=weekly_budget_allocation
    )
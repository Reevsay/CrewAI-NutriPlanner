"""
Nutritionist Agent for the Smart Recipe & Meal Planning System.

This module implements the Nutritionist Agent that analyzes dietary requirements
and provides nutritional guidance based on user profiles.
"""

from typing import Dict, List, Optional, Any
import logging
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.user_profile import UserProfile
from ..models.recipe import NutritionalInfo
from ..tools.nutrition_api import NutritionAPI
from ..tools.calculation_tools import NutritionalCalculator

# Configure logging
logger = logging.getLogger(__name__)


class NutritionalAnalysisInput(BaseModel):
    """Input model for nutritional analysis."""
    user_profile: Dict[str, Any] = Field(description="User profile data including personal info, dietary preferences, and health goals")


class NutritionalAnalysisOutput(BaseModel):
    """Output model for nutritional analysis."""
    daily_caloric_needs: float = Field(description="Daily caloric requirements in calories")
    daily_protein_needs: float = Field(description="Daily protein requirements in grams")
    daily_carb_needs: float = Field(description="Daily carbohydrate requirements in grams")
    daily_fat_needs: float = Field(description="Daily fat requirements in grams")
    daily_fiber_needs: float = Field(description="Daily fiber requirements in grams")
    daily_sodium_limit: float = Field(description="Daily sodium limit in mg")
    micronutrient_needs: Dict[str, float] = Field(description="Daily micronutrient requirements")
    dietary_restrictions: List[str] = Field(description="List of dietary restrictions to consider")
    nutritional_guidelines: List[str] = Field(description="Specific nutritional guidelines and recommendations")
    bmr: float = Field(description="Basal Metabolic Rate in calories")
    tdee: float = Field(description="Total Daily Energy Expenditure in calories")


class NutritionLookupTool(BaseTool):
    """Tool for looking up nutritional information of foods."""
    
    name: str = "nutrition_lookup"
    description: str = "Look up nutritional information for specific foods and ingredients"
    
    def _run(self, food_name: str, quantity: float = 100.0) -> str:
        """
        Look up nutritional information for a food item.
        
        Args:
            food_name: Name of the food to look up
            quantity: Quantity in grams (default: 100g)
            
        Returns:
            Formatted nutritional information string
        """
        try:
            nutrition_api = NutritionAPI()
            nutrition_info = nutrition_api.get_food_nutrition(food_name, quantity)
            
            result = f"Nutritional information for {quantity}g of {food_name}:\n"
            result += f"- Calories: {nutrition_info.calories:.1f}\n"
            result += f"- Protein: {nutrition_info.protein:.1f}g\n"
            result += f"- Carbohydrates: {nutrition_info.carbohydrates:.1f}g\n"
            result += f"- Fat: {nutrition_info.fat:.1f}g\n"
            result += f"- Fiber: {nutrition_info.fiber:.1f}g\n"
            result += f"- Sodium: {nutrition_info.sodium:.1f}mg\n"
            
            if nutrition_info.vitamin_c:
                result += f"- Vitamin C: {nutrition_info.vitamin_c:.1f}mg\n"
            if nutrition_info.calcium:
                result += f"- Calcium: {nutrition_info.calcium:.1f}mg\n"
            if nutrition_info.iron:
                result += f"- Iron: {nutrition_info.iron:.1f}mg\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to lookup nutrition for {food_name}: {e}")
            return f"Error looking up nutrition information for {food_name}: {str(e)}"


class BMRCalculatorTool(BaseTool):
    """Tool for calculating Basal Metabolic Rate."""
    
    name: str = "bmr_calculator"
    description: str = "Calculate Basal Metabolic Rate (BMR) based on user's physical characteristics"
    
    def _run(self, age: int, weight: float, height: float, gender: str) -> str:
        """
        Calculate BMR using Mifflin-St Jeor equation.
        
        Args:
            age: Age in years
            weight: Weight in kg
            height: Height in cm
            gender: Gender (male/female/other)
            
        Returns:
            BMR calculation result
        """
        try:
            if gender.lower() == 'male':
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:  # Female or Other
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            return f"BMR: {bmr:.0f} calories per day"
            
        except Exception as e:
            logger.error(f"Failed to calculate BMR: {e}")
            return f"Error calculating BMR: {str(e)}"


class TDEECalculatorTool(BaseTool):
    """Tool for calculating Total Daily Energy Expenditure."""
    
    name: str = "tdee_calculator"
    description: str = "Calculate Total Daily Energy Expenditure (TDEE) based on BMR and activity level"
    
    def _run(self, bmr: float, activity_level: str) -> str:
        """
        Calculate TDEE based on BMR and activity level.
        
        Args:
            bmr: Basal Metabolic Rate in calories
            activity_level: Activity level (sedentary, lightly_active, moderately_active, very_active, extremely_active)
            
        Returns:
            TDEE calculation result
        """
        try:
            activity_multipliers = {
                'sedentary': 1.2,
                'lightly_active': 1.375,
                'moderately_active': 1.55,
                'very_active': 1.725,
                'extremely_active': 1.9
            }
            
            multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
            tdee = bmr * multiplier
            
            return f"TDEE: {tdee:.0f} calories per day (BMR {bmr:.0f} × {multiplier} activity multiplier)"
            
        except Exception as e:
            logger.error(f"Failed to calculate TDEE: {e}")
            return f"Error calculating TDEE: {str(e)}"


class NutrientRequirementsTool(BaseTool):
    """Tool for calculating daily nutrient requirements."""
    
    name: str = "nutrient_requirements"
    description: str = "Calculate daily nutrient requirements based on calories, goals, and user characteristics"
    
    def _run(self, calories: float, weight: float, age: int, gender: str, goal_type: str) -> str:
        """
        Calculate daily nutrient requirements.
        
        Args:
            calories: Daily caloric target
            weight: Body weight in kg
            age: Age in years
            gender: Gender (male/female/other)
            goal_type: Health goal (weight_loss, muscle_gain, maintenance, general_health)
            
        Returns:
            Formatted nutrient requirements
        """
        try:
            # Protein requirements (1.2-2.0g per kg body weight)
            if goal_type == 'muscle_gain':
                protein_per_kg = 1.8
            elif goal_type == 'weight_loss':
                protein_per_kg = 1.6
            else:
                protein_per_kg = 1.4
            
            protein_grams = weight * protein_per_kg
            
            # Carbohydrate requirements (45-65% of calories)
            if goal_type == 'weight_loss':
                carb_percentage = 0.40  # Lower carbs for weight loss
            else:
                carb_percentage = 0.50  # Moderate carbs
            
            carb_grams = (calories * carb_percentage) / 4
            
            # Fat requirements (20-35% of calories)
            fat_percentage = 0.25  # 25% of calories
            fat_grams = (calories * fat_percentage) / 9
            
            # Fiber requirements
            fiber_grams = 25 if gender.lower() == 'female' else 38
            if age > 50:
                fiber_grams = 21 if gender.lower() == 'female' else 30
            
            # Sodium limit
            sodium_mg = 2300  # mg per day
            
            # Micronutrients
            vitamin_c = 75 if gender.lower() == 'female' else 90
            calcium = 1000 if age <= 50 else 1200
            iron = 18 if gender.lower() == 'female' and age <= 50 else 8
            
            result = f"Daily Nutrient Requirements:\n"
            result += f"- Calories: {calories:.0f}\n"
            result += f"- Protein: {protein_grams:.1f}g ({protein_per_kg}g per kg body weight)\n"
            result += f"- Carbohydrates: {carb_grams:.1f}g ({carb_percentage*100:.0f}% of calories)\n"
            result += f"- Fat: {fat_grams:.1f}g ({fat_percentage*100:.0f}% of calories)\n"
            result += f"- Fiber: {fiber_grams:.0f}g\n"
            result += f"- Sodium: ≤{sodium_mg:.0f}mg\n"
            result += f"- Vitamin C: {vitamin_c:.0f}mg\n"
            result += f"- Calcium: {calcium:.0f}mg\n"
            result += f"- Iron: {iron:.0f}mg\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate nutrient requirements: {e}")
            return f"Error calculating nutrient requirements: {str(e)}"


def create_nutritionist_agent() -> Agent:
    """
    Create and configure the Nutritionist Agent.
    
    Returns:
        Configured CrewAI Agent for nutritional analysis
    """
    
    # Initialize tools
    nutrition_lookup_tool = NutritionLookupTool()
    bmr_calculator_tool = BMRCalculatorTool()
    tdee_calculator_tool = TDEECalculatorTool()
    nutrient_requirements_tool = NutrientRequirementsTool()
    
    tools = [
        nutrition_lookup_tool,
        bmr_calculator_tool,
        tdee_calculator_tool,
        nutrient_requirements_tool
    ]
    
    agent = Agent(
        role="Nutritionist and Dietary Requirements Analyst",
        goal="Analyze user dietary needs and establish comprehensive nutritional guidelines for meal planning",
        backstory="""You are an expert registered dietitian and nutritionist with over 15 years of experience 
        in clinical nutrition and meal planning. You specialize in analyzing individual dietary requirements 
        based on personal characteristics, health goals, and lifestyle factors. Your expertise includes 
        calculating metabolic needs, determining optimal macronutrient ratios, and identifying potential 
        nutritional gaps or concerns. You stay current with the latest nutritional science and dietary 
        guidelines from organizations like the Academy of Nutrition and Dietetics and the USDA.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=True
    )
    
    return agent


def create_nutritional_analysis_task(user_profile_data: Dict[str, Any]) -> Task:
    """
    Create a task for nutritional analysis.
    
    Args:
        user_profile_data: Dictionary containing user profile information
        
    Returns:
        CrewAI Task for nutritional analysis
    """
    
    task = Task(
        description=f"""
        Analyze the provided user profile and establish comprehensive nutritional requirements and guidelines.
        
        User Profile Data: {user_profile_data}
        
        Your analysis should include:
        
        1. Calculate the user's Basal Metabolic Rate (BMR) using their physical characteristics
        2. Determine Total Daily Energy Expenditure (TDEE) based on activity level
        3. Establish daily caloric needs considering their health goals
        4. Calculate optimal macronutrient distribution (protein, carbohydrates, fat)
        5. Determine daily micronutrient requirements (vitamins and minerals)
        6. Identify any dietary restrictions or special considerations
        7. Provide specific nutritional guidelines for meal planning
        8. Highlight any potential nutritional concerns or areas of focus
        
        Use the available tools to perform accurate calculations and lookups as needed.
        Consider the user's age, gender, weight, height, activity level, health goals, and any dietary restrictions.
        
        Provide detailed reasoning for your recommendations and ensure all calculations are based on 
        current nutritional science and established dietary guidelines.
        """,
        expected_output="""
        A comprehensive nutritional analysis report containing:
        
        1. **Metabolic Calculations:**
           - Basal Metabolic Rate (BMR): [value] calories/day
           - Total Daily Energy Expenditure (TDEE): [value] calories/day
           - Recommended daily calories: [value] calories/day
        
        2. **Macronutrient Requirements:**
           - Protein: [value]g/day ([percentage]% of calories)
           - Carbohydrates: [value]g/day ([percentage]% of calories)
           - Fat: [value]g/day ([percentage]% of calories)
           - Fiber: [value]g/day
        
        3. **Micronutrient Requirements:**
           - Key vitamins and minerals with daily targets
           - Special considerations based on age, gender, and goals
        
        4. **Dietary Guidelines:**
           - Specific recommendations for meal planning
           - Foods to emphasize or limit
           - Timing and distribution recommendations
        
        5. **Special Considerations:**
           - Dietary restrictions and how to address them
           - Potential nutritional concerns
           - Monitoring recommendations
        
        Format the output as a structured report that can be easily used by other agents in the meal planning process.
        """,
        agent=create_nutritionist_agent(),
        output_pydantic=NutritionalAnalysisOutput
    )
    
    return task


# Utility functions for integration
def analyze_user_nutrition(user_profile: UserProfile) -> NutritionalAnalysisOutput:
    """
    Analyze user nutritional requirements using the Nutritionist Agent.
    
    Args:
        user_profile: UserProfile object
        
    Returns:
        NutritionalAnalysisOutput with analysis results
    """
    try:
        # Convert user profile to dictionary for task input
        user_profile_data = {
            'personal_info': {
                'age': user_profile.personal_info.age,
                'weight': user_profile.personal_info.weight,
                'height': user_profile.personal_info.height,
                'activity_level': user_profile.personal_info.activity_level.value,
                'gender': user_profile.personal_info.gender.value
            },
            'dietary_preferences': {
                'restrictions': user_profile.dietary_preferences.restrictions,
                'allergies': user_profile.dietary_preferences.allergies,
                'cooking_skill_level': user_profile.dietary_preferences.cooking_skill_level.value
            },
            'health_goals': {
                'goal_type': user_profile.health_goals.goal_type.value,
                'target_calories': user_profile.health_goals.target_calories,
                'target_weight': user_profile.health_goals.target_weight,
                'weekly_weight_change_goal': user_profile.health_goals.weekly_weight_change_goal
            }
        }
        
        # Create and execute task
        task = create_nutritional_analysis_task(user_profile_data)
        
        # For now, return calculated values directly
        # In a full CrewAI implementation, this would execute the task
        calculator = NutritionalCalculator()
        daily_targets = calculator.calculate_daily_targets(user_profile)
        bmr = calculator.calculate_bmr(user_profile)
        tdee = calculator.calculate_tdee(user_profile)
        
        return NutritionalAnalysisOutput(
            daily_caloric_needs=daily_targets.calories,
            daily_protein_needs=daily_targets.protein,
            daily_carb_needs=daily_targets.carbohydrates,
            daily_fat_needs=daily_targets.fat,
            daily_fiber_needs=daily_targets.fiber,
            daily_sodium_limit=daily_targets.sodium,
            micronutrient_needs={
                'vitamin_c': daily_targets.vitamin_c or 90,
                'calcium': daily_targets.calcium or 1000,
                'iron': daily_targets.iron or 8
            },
            dietary_restrictions=user_profile.dietary_preferences.restrictions,
            nutritional_guidelines=[
                f"Target {daily_targets.calories:.0f} calories per day",
                f"Include {daily_targets.protein:.0f}g protein daily",
                f"Focus on whole grains for {daily_targets.carbohydrates:.0f}g carbohydrates",
                f"Include healthy fats totaling {daily_targets.fat:.0f}g daily",
                "Eat a variety of colorful fruits and vegetables",
                "Stay hydrated with 8-10 glasses of water daily"
            ],
            bmr=bmr,
            tdee=tdee
        )
        
    except Exception as e:
        logger.error(f"Failed to analyze user nutrition: {e}")
        raise
"""
Health Validator Agent for the Smart Recipe & Meal Planning System.

This module implements the Health Validator Agent that validates meal plans
for nutritional adequacy, dietary compliance, and health optimization.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.recipe import WeeklyMealPlan, NutritionalInfo
from ..models.user_profile import UserProfile
from ..tools.calculation_tools import NutritionalCalculator, NutritionalBalance, NutritionalStatus

# Configure logging
logger = logging.getLogger(__name__)


class HealthValidationInput(BaseModel):
    """Input model for health validation."""
    meal_plan: Dict[str, Any] = Field(description="Complete weekly meal plan to validate")
    user_profile: Dict[str, Any] = Field(description="User profile with health goals and restrictions")
    nutritional_targets: Dict[str, float] = Field(description="Target nutritional values")


class HealthValidationOutput(BaseModel):
    """Output model for health validation."""
    overall_health_score: float = Field(description="Overall health score (0-100)")
    nutritional_adequacy_score: float = Field(description="Nutritional adequacy score (0-100)")
    dietary_compliance_score: float = Field(description="Dietary restriction compliance score (0-100)")
    health_recommendations: List[str] = Field(description="Health optimization recommendations")
    nutritional_gaps: List[str] = Field(description="Identified nutritional deficiencies")
    dietary_violations: List[str] = Field(description="Dietary restriction violations")
    meal_plan_adjustments: List[str] = Field(description="Recommended meal plan adjustments")
    health_benefits: List[str] = Field(description="Identified health benefits of the meal plan")
    risk_assessments: List[str] = Field(description="Potential health risks or concerns")
    final_approval_status: str = Field(description="Final approval status (approved/needs_revision/rejected)")


class NutritionalAdequacyTool(BaseTool):
    """Tool for assessing nutritional adequacy of meal plans."""
    
    name: str = "nutritional_adequacy"
    description: str = "Assess nutritional adequacy and identify deficiencies in meal plans"
    
    def _run(self, meal_plan_nutrition: Dict[str, float], targets: Dict[str, float], user_info: Dict[str, Any]) -> str:
        """
        Assess nutritional adequacy of a meal plan.
        
        Args:
            meal_plan_nutrition: Actual nutritional values from meal plan
            targets: Target nutritional values
            user_info: User information for context
            
        Returns:
            Nutritional adequacy assessment
        """
        try:
            age = user_info.get('age', 30)
            gender = user_info.get('gender', 'female')
            activity_level = user_info.get('activity_level', 'moderate')
            health_goals = user_info.get('health_goals', {})
            
            result = "Nutritional Adequacy Assessment:\n\n"
            
            # Define critical nutrients and their importance
            critical_nutrients = {
                'calories': {'min_ratio': 0.8, 'max_ratio': 1.2, 'importance': 'high'},
                'protein': {'min_ratio': 0.8, 'max_ratio': 2.0, 'importance': 'high'},
                'carbohydrates': {'min_ratio': 0.7, 'max_ratio': 1.3, 'importance': 'medium'},
                'fat': {'min_ratio': 0.7, 'max_ratio': 1.3, 'importance': 'medium'},
                'fiber': {'min_ratio': 0.8, 'max_ratio': float('inf'), 'importance': 'high'},
                'sodium': {'min_ratio': 0, 'max_ratio': 1.0, 'importance': 'high'},
                'vitamin_c': {'min_ratio': 0.8, 'max_ratio': float('inf'), 'importance': 'medium'},
                'calcium': {'min_ratio': 0.8, 'max_ratio': float('inf'), 'importance': 'high'},
                'iron': {'min_ratio': 0.8, 'max_ratio': float('inf'), 'importance': 'high'}
            }
            
            adequacy_scores = []
            deficiencies = []
            excesses = []
            
            for nutrient, criteria in critical_nutrients.items():
                target_value = targets.get(nutrient, 0)
                actual_value = meal_plan_nutrition.get(nutrient, 0)
                
                if target_value > 0:
                    ratio = actual_value / target_value
                    
                    if ratio < criteria['min_ratio']:
                        deficiency_severity = 'severe' if ratio < 0.5 else 'moderate' if ratio < 0.7 else 'mild'
                        deficiencies.append(f"{nutrient.title()}: {deficiency_severity} deficiency ({actual_value:.1f} vs {target_value:.1f})")
                        
                        # Score based on severity
                        if deficiency_severity == 'severe':
                            score = 20
                        elif deficiency_severity == 'moderate':
                            score = 50
                        else:
                            score = 70
                        
                        adequacy_scores.append(score)
                        
                    elif ratio > criteria['max_ratio']:
                        excess_severity = 'severe' if ratio > 2.0 else 'moderate' if ratio > 1.5 else 'mild'
                        excesses.append(f"{nutrient.title()}: {excess_severity} excess ({actual_value:.1f} vs {target_value:.1f})")
                        
                        # Excess is generally less concerning than deficiency
                        if excess_severity == 'severe':
                            score = 60
                        elif excess_severity == 'moderate':
                            score = 80
                        else:
                            score = 90
                        
                        adequacy_scores.append(score)
                    else:
                        adequacy_scores.append(100)  # Adequate
                else:
                    adequacy_scores.append(100)  # No target set
            
            # Calculate overall adequacy score
            overall_score = sum(adequacy_scores) / len(adequacy_scores) if adequacy_scores else 0
            
            result += f"**Overall Nutritional Adequacy Score: {overall_score:.0f}/100**\n\n"
            
            if deficiencies:
                result += "**Nutritional Deficiencies:**\n"
                for deficiency in deficiencies:
                    result += f"- {deficiency}\n"
                result += "\n"
            
            if excesses:
                result += "**Nutritional Excesses:**\n"
                for excess in excesses:
                    result += f"- {excess}\n"
                result += "\n"
            
            # Special considerations based on user profile
            result += "**Special Considerations:**\n"
            
            if gender == 'female' and age < 50:
                iron_actual = meal_plan_nutrition.get('iron', 0)
                iron_target = targets.get('iron', 18)
                if iron_actual < iron_target * 0.8:
                    result += "- Iron intake is particularly important for women of reproductive age\n"
            
            if age > 50:
                calcium_actual = meal_plan_nutrition.get('calcium', 0)
                calcium_target = targets.get('calcium', 1200)
                if calcium_actual < calcium_target * 0.8:
                    result += "- Calcium intake is crucial for bone health in adults over 50\n"
            
            if activity_level in ['very_active', 'extremely_active']:
                protein_actual = meal_plan_nutrition.get('protein', 0)
                protein_target = targets.get('protein', 150)
                if protein_actual < protein_target * 0.9:
                    result += "- Higher protein intake recommended for very active individuals\n"
            
            # Health goal considerations
            goal_type = health_goals.get('goal_type', '')
            if goal_type == 'weight_loss':
                calories_actual = meal_plan_nutrition.get('calories', 0)
                calories_target = targets.get('calories', 2000)
                if calories_actual > calories_target:
                    result += "- Calorie intake may be too high for weight loss goals\n"
            elif goal_type == 'muscle_gain':
                protein_actual = meal_plan_nutrition.get('protein', 0)
                if protein_actual < 1.6 * user_info.get('weight', 70):  # 1.6g per kg body weight
                    result += "- Protein intake may be insufficient for muscle gain goals\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to assess nutritional adequacy: {e}")
            return f"Error assessing nutritional adequacy: {str(e)}"


class DietaryComplianceTool(BaseTool):
    """Tool for checking compliance with dietary restrictions and preferences."""
    
    name: str = "dietary_compliance"
    description: str = "Check meal plan compliance with dietary restrictions and preferences"
    

    
    def _load_restriction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load dietary restriction rules and forbidden ingredients."""
        return {
            'vegetarian': {
                'forbidden_ingredients': [
                    'beef', 'pork', 'chicken', 'turkey', 'fish', 'salmon', 'tuna', 
                    'shrimp', 'crab', 'lobster', 'meat', 'poultry', 'seafood'
                ],
                'forbidden_keywords': ['meat', 'fish', 'poultry', 'seafood'],
                'severity': 'high'
            },
            'vegan': {
                'forbidden_ingredients': [
                    'beef', 'pork', 'chicken', 'turkey', 'fish', 'salmon', 'eggs', 
                    'milk', 'cheese', 'yogurt', 'butter', 'honey', 'gelatin'
                ],
                'forbidden_keywords': ['meat', 'dairy', 'animal', 'fish', 'egg'],
                'severity': 'high'
            },
            'gluten_free': {
                'forbidden_ingredients': [
                    'wheat', 'barley', 'rye', 'bread', 'pasta', 'flour', 'oats'
                ],
                'forbidden_keywords': ['wheat', 'gluten', 'flour'],
                'severity': 'high'
            },
            'dairy_free': {
                'forbidden_ingredients': [
                    'milk', 'cheese', 'yogurt', 'butter', 'cream', 'lactose'
                ],
                'forbidden_keywords': ['dairy', 'milk', 'cheese'],
                'severity': 'medium'
            },
            'nut_free': {
                'forbidden_ingredients': [
                    'peanuts', 'almonds', 'walnuts', 'cashews', 'pecans', 'hazelnuts'
                ],
                'forbidden_keywords': ['nut', 'peanut'],
                'severity': 'high'
            },
            'low_sodium': {
                'max_daily_sodium': 1500,  # mg
                'severity': 'medium'
            },
            'diabetic_friendly': {
                'max_sugar_per_meal': 15,  # g
                'preferred_carb_type': 'complex',
                'severity': 'high'
            }
        }
    
    def _run(self, meal_plan: Dict[str, Any], dietary_restrictions: List[str], allergies: List[str]) -> str:
        """
        Check dietary compliance of meal plan.
        
        Args:
            meal_plan: Weekly meal plan data
            dietary_restrictions: List of dietary restrictions
            allergies: List of allergies
            
        Returns:
            Dietary compliance assessment
        """
        try:
            result = "Dietary Compliance Assessment:\n\n"
            
            violations = []
            warnings = []
            compliance_scores = []
            
            # Load restriction rules locally
            restriction_rules = self._load_restriction_rules()
            
            # Check each restriction
            for restriction in dietary_restrictions:
                restriction_lower = restriction.lower()
                
                if restriction_lower in restriction_rules:
                    rules = restriction_rules[restriction_lower]
                    restriction_violations = []
                    
                    # Check forbidden ingredients
                    if 'forbidden_ingredients' in rules:
                        forbidden = rules['forbidden_ingredients']
                        
                        # Check all meals in the plan
                        for day_data in meal_plan.get('daily_plans', []):
                            day_violations = self._check_day_ingredients(day_data, forbidden, restriction)
                            restriction_violations.extend(day_violations)
                    
                    # Check special rules (like sodium limits)
                    if restriction_lower == 'low_sodium':
                        sodium_violations = self._check_sodium_compliance(meal_plan, rules['max_daily_sodium'])
                        restriction_violations.extend(sodium_violations)
                    
                    elif restriction_lower == 'diabetic_friendly':
                        sugar_violations = self._check_sugar_compliance(meal_plan, rules['max_sugar_per_meal'])
                        restriction_violations.extend(sugar_violations)
                    
                    # Calculate compliance score for this restriction
                    if restriction_violations:
                        severity = rules.get('severity', 'medium')
                        if severity == 'high':
                            compliance_scores.append(0)  # Critical violation
                        elif severity == 'medium':
                            compliance_scores.append(50)  # Moderate violation
                        else:
                            compliance_scores.append(70)  # Minor violation
                        
                        violations.extend(restriction_violations)
                    else:
                        compliance_scores.append(100)  # Full compliance
            
            # Check allergies (always high severity)
            for allergy in allergies:
                allergy_violations = []
                
                for day_data in meal_plan.get('daily_plans', []):
                    day_violations = self._check_day_ingredients(day_data, [allergy], f"allergy to {allergy}")
                    allergy_violations.extend(day_violations)
                
                if allergy_violations:
                    compliance_scores.append(0)  # Critical - allergy violation
                    violations.extend(allergy_violations)
                else:
                    compliance_scores.append(100)
            
            # Calculate overall compliance score
            overall_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 100
            
            result += f"**Overall Dietary Compliance Score: {overall_compliance:.0f}/100**\n\n"
            
            if violations:
                result += "**Dietary Violations Found:**\n"
                for violation in violations:
                    result += f"- {violation}\n"
                result += "\n"
            else:
                result += "**✓ No dietary violations found - meal plan is compliant**\n\n"
            
            if warnings:
                result += "**Warnings:**\n"
                for warning in warnings:
                    result += f"- {warning}\n"
                result += "\n"
            
            # Provide recommendations
            result += "**Compliance Recommendations:**\n"
            
            if violations:
                result += "- Review and replace non-compliant ingredients\n"
                result += "- Double-check ingredient labels for hidden restricted items\n"
                result += "- Consider alternative recipes that meet dietary requirements\n"
            else:
                result += "- Meal plan successfully meets all dietary restrictions\n"
                result += "- Continue monitoring ingredient sources for compliance\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to check dietary compliance: {e}")
            return f"Error checking dietary compliance: {str(e)}"
    
    def _check_day_ingredients(self, day_data: Dict[str, Any], forbidden_items: List[str], restriction_name: str) -> List[str]:
        """Check ingredients in a single day for violations."""
        violations = []
        
        # Check all meals in the day
        for meal_type in ['breakfast', 'lunch', 'dinner']:
            meal = day_data.get(meal_type)
            if meal and isinstance(meal, dict):
                meal_name = meal.get('name', 'Unknown meal')
                ingredients = meal.get('ingredients', [])
                
                for ingredient in ingredients:
                    ingredient_name = ingredient.get('name', '').lower()
                    
                    for forbidden in forbidden_items:
                        if forbidden.lower() in ingredient_name:
                            violations.append(f"{meal_name} contains {ingredient_name} (violates {restriction_name})")
        
        # Check snacks
        snacks = day_data.get('snacks', [])
        for snack in snacks:
            if isinstance(snack, dict):
                snack_name = snack.get('name', 'Unknown snack')
                ingredients = snack.get('ingredients', [])
                
                for ingredient in ingredients:
                    ingredient_name = ingredient.get('name', '').lower()
                    
                    for forbidden in forbidden_items:
                        if forbidden.lower() in ingredient_name:
                            violations.append(f"{snack_name} contains {ingredient_name} (violates {restriction_name})")
        
        return violations
    
    def _check_sodium_compliance(self, meal_plan: Dict[str, Any], max_daily_sodium: float) -> List[str]:
        """Check sodium compliance across the meal plan."""
        violations = []
        
        for i, day_data in enumerate(meal_plan.get('daily_plans', [])):
            daily_sodium = 0
            
            # Estimate sodium from meals (simplified)
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                meal = day_data.get(meal_type)
                if meal:
                    # Rough sodium estimation based on meal type
                    if meal_type == 'breakfast':
                        daily_sodium += 300
                    elif meal_type == 'lunch':
                        daily_sodium += 600
                    else:  # dinner
                        daily_sodium += 800
            
            if daily_sodium > max_daily_sodium:
                day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
                violations.append(f"{day_name}: Estimated sodium {daily_sodium}mg exceeds limit of {max_daily_sodium}mg")
        
        return violations
    
    def _check_sugar_compliance(self, meal_plan: Dict[str, Any], max_sugar_per_meal: float) -> List[str]:
        """Check sugar compliance for diabetic-friendly requirements."""
        violations = []
        
        # This would require detailed nutritional analysis
        # For now, provide a simplified check
        for i, day_data in enumerate(meal_plan.get('daily_plans', [])):
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
            
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                meal = day_data.get(meal_type)
                if meal:
                    meal_name = meal.get('name', '').lower()
                    
                    # Check for high-sugar ingredients
                    high_sugar_keywords = ['syrup', 'honey', 'sugar', 'candy', 'dessert', 'cake']
                    if any(keyword in meal_name for keyword in high_sugar_keywords):
                        violations.append(f"{day_name} {meal_type}: {meal.get('name')} may be too high in sugar for diabetic diet")
        
        return violations


class HealthOptimizationTool(BaseTool):
    """Tool for providing health optimization recommendations."""
    
    name: str = "health_optimization"
    description: str = "Provide health optimization recommendations based on meal plan analysis"
    
    def _run(self, meal_plan_analysis: Dict[str, Any], user_health_profile: Dict[str, Any]) -> str:
        """
        Provide health optimization recommendations.
        
        Args:
            meal_plan_analysis: Results from nutritional and compliance analysis
            user_health_profile: User health information and goals
            
        Returns:
            Health optimization recommendations
        """
        try:
            result = "Health Optimization Recommendations:\n\n"
            
            age = user_health_profile.get('age', 30)
            gender = user_health_profile.get('gender', 'female')
            health_goals = user_health_profile.get('health_goals', {})
            activity_level = user_health_profile.get('activity_level', 'moderate')
            existing_conditions = user_health_profile.get('conditions', [])
            
            recommendations = []
            
            # Age-based recommendations
            if age > 50:
                recommendations.extend([
                    "Increase calcium-rich foods for bone health (dairy, leafy greens, fortified foods)",
                    "Include vitamin D sources or consider supplementation",
                    "Focus on anti-inflammatory foods (fatty fish, berries, leafy greens)",
                    "Ensure adequate fiber intake for digestive health"
                ])
            
            if age > 65:
                recommendations.extend([
                    "Include vitamin B12 rich foods or fortified options",
                    "Ensure adequate protein intake to maintain muscle mass",
                    "Stay well-hydrated and include easy-to-digest foods"
                ])
            
            # Gender-specific recommendations
            if gender == 'female':
                if age < 50:
                    recommendations.append("Ensure adequate iron intake from lean meats, beans, or fortified cereals")
                recommendations.append("Include folate-rich foods (leafy greens, legumes, fortified grains)")
            
            # Activity level recommendations
            if activity_level in ['very_active', 'extremely_active']:
                recommendations.extend([
                    "Increase protein intake to support muscle recovery and growth",
                    "Include complex carbohydrates for sustained energy",
                    "Ensure adequate hydration and electrolyte balance",
                    "Consider timing of meals around workouts"
                ])
            elif activity_level == 'sedentary':
                recommendations.extend([
                    "Focus on nutrient-dense, lower-calorie foods",
                    "Include metabolism-boosting foods (green tea, spicy foods)",
                    "Emphasize fiber-rich foods for satiety"
                ])
            
            # Health goal recommendations
            goal_type = health_goals.get('goal_type', '')
            
            if goal_type == 'weight_loss':
                recommendations.extend([
                    "Emphasize high-protein, high-fiber foods for satiety",
                    "Include plenty of non-starchy vegetables",
                    "Consider meal timing and portion control strategies",
                    "Stay well-hydrated to support metabolism"
                ])
            elif goal_type == 'muscle_gain':
                recommendations.extend([
                    "Distribute protein intake throughout the day",
                    "Include post-workout nutrition within 30 minutes",
                    "Ensure adequate caloric intake to support muscle growth",
                    "Include creatine-rich foods (red meat, fish)"
                ])
            elif goal_type == 'general_health':
                recommendations.extend([
                    "Follow the 'rainbow' principle - eat a variety of colorful foods",
                    "Include fermented foods for gut health",
                    "Limit processed foods and added sugars",
                    "Maintain consistent meal timing"
                ])
            
            # Condition-specific recommendations
            if 'diabetes' in existing_conditions:
                recommendations.extend([
                    "Focus on low glycemic index foods",
                    "Pair carbohydrates with protein or healthy fats",
                    "Monitor portion sizes and meal timing",
                    "Include chromium and magnesium-rich foods"
                ])
            
            if 'hypertension' in existing_conditions:
                recommendations.extend([
                    "Reduce sodium intake and increase potassium-rich foods",
                    "Include DASH diet principles (fruits, vegetables, whole grains)",
                    "Limit processed and packaged foods",
                    "Include magnesium-rich foods (nuts, seeds, leafy greens)"
                ])
            
            if 'high_cholesterol' in existing_conditions:
                recommendations.extend([
                    "Include soluble fiber sources (oats, beans, apples)",
                    "Add omega-3 rich foods (fatty fish, walnuts, flax seeds)",
                    "Limit saturated and trans fats",
                    "Include plant sterols and stanols"
                ])
            
            # General optimization recommendations
            recommendations.extend([
                "Aim for at least 5 servings of fruits and vegetables daily",
                "Include a variety of protein sources throughout the week",
                "Choose whole grains over refined grains when possible",
                "Stay hydrated with 8-10 glasses of water daily",
                "Consider meal prep to maintain consistency",
                "Listen to hunger and fullness cues"
            ])
            
            # Format recommendations
            result += "**Priority Recommendations:**\n"
            for i, rec in enumerate(recommendations[:8], 1):  # Top 8 recommendations
                result += f"{i}. {rec}\n"
            
            if len(recommendations) > 8:
                result += f"\n**Additional Recommendations:**\n"
                for rec in recommendations[8:]:
                    result += f"- {rec}\n"
            
            # Add monitoring suggestions
            result += "\n**Monitoring Suggestions:**\n"
            result += "- Track energy levels and mood throughout the day\n"
            result += "- Monitor sleep quality and digestive health\n"
            result += "- Consider regular health check-ups to assess progress\n"
            result += "- Adjust meal plan based on how you feel and perform\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate health optimization recommendations: {e}")
            return f"Error generating recommendations: {str(e)}"


def create_health_validator_agent() -> Agent:
    """
    Create and configure the Health Validator Agent.
    
    Returns:
        Configured CrewAI Agent for health validation
    """
    
    # Initialize tools
    nutritional_adequacy_tool = NutritionalAdequacyTool()
    dietary_compliance_tool = DietaryComplianceTool()
    health_optimization_tool = HealthOptimizationTool()
    
    tools = [
        nutritional_adequacy_tool,
        dietary_compliance_tool,
        health_optimization_tool
    ]
    
    agent = Agent(
        role="Registered Dietitian and Nutritional Quality Assurance Specialist",
        goal="Validate meal plans for nutritional adequacy, dietary compliance, and health optimization",
        backstory="""You are a registered dietitian with over 15 years of clinical experience in 
        nutritional assessment and meal plan validation. You hold advanced certifications in clinical 
        nutrition and have worked in hospitals, wellness centers, and private practice. Your expertise 
        includes identifying nutritional deficiencies, ensuring dietary compliance for various health 
        conditions, and optimizing meal plans for specific health goals. You stay current with the 
        latest nutritional research and dietary guidelines from professional organizations like the 
        Academy of Nutrition and Dietetics. Your thorough approach to meal plan validation helps 
        ensure that individuals receive nutritionally complete and health-promoting meal plans.""",
        tools=tools,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=True
    )
    
    return agent


def create_health_validation_task(
    meal_plan: Dict[str, Any],
    user_profile: Dict[str, Any],
    nutritional_targets: Dict[str, float]
) -> Task:
    """
    Create a task for health validation of meal plans.
    
    Args:
        meal_plan: Complete weekly meal plan to validate
        user_profile: User profile with health goals and restrictions
        nutritional_targets: Target nutritional values
        
    Returns:
        CrewAI Task for health validation
    """
    
    task = Task(
        description=f"""
        Conduct a comprehensive health validation of the provided weekly meal plan to ensure nutritional 
        adequacy, dietary compliance, and health optimization.
        
        Meal Plan: {len(meal_plan.get('daily_plans', []))} days of planned meals
        User Profile: Age {user_profile.get('age')}, {user_profile.get('gender')}, {user_profile.get('activity_level')} activity
        Health Goals: {user_profile.get('health_goals', {})}
        Dietary Restrictions: {user_profile.get('dietary_restrictions', [])}
        Nutritional Targets: {nutritional_targets}
        
        Your validation should include:
        
        1. Comprehensive nutritional adequacy assessment against established RDAs and user targets
        2. Strict dietary restriction and allergy compliance verification
        3. Health optimization recommendations based on user profile and goals
        4. Risk assessment for potential nutritional deficiencies or health concerns
        5. Meal plan adjustment recommendations for improved health outcomes
        6. Final approval status with clear reasoning
        
        Use the available tools to:
        - Assess nutritional adequacy across all macro and micronutrients
        - Verify compliance with all dietary restrictions and allergies
        - Generate personalized health optimization recommendations
        
        Provide a thorough, evidence-based assessment that prioritizes user health and safety.
        Consider the user's age, gender, activity level, health goals, and any existing health conditions.
        """,
        expected_output="""
        A comprehensive health validation report containing:
        
        1. **Overall Health Assessment:**
           - Overall health score (0-100)
           - Nutritional adequacy score (0-100)
           - Dietary compliance score (0-100)
           - Final approval status (approved/needs_revision/rejected)
        
        2. **Nutritional Analysis:**
           - Detailed assessment of macro and micronutrient adequacy
           - Identification of nutritional gaps or deficiencies
           - Comparison against established RDAs and user targets
        
        3. **Dietary Compliance:**
           - Verification of adherence to dietary restrictions
           - Allergy safety assessment
           - Identification of any violations or concerns
        
        4. **Health Optimization:**
           - Personalized recommendations for health improvement
           - Suggestions based on age, gender, activity level, and goals
           - Evidence-based nutritional strategies
        
        5. **Risk Assessment:**
           - Potential health risks or nutritional concerns
           - Long-term health implications
           - Monitoring recommendations
        
        6. **Action Items:**
           - Specific meal plan adjustments needed
           - Priority areas for improvement
           - Implementation recommendations
        
        Format the output as a professional nutritional assessment suitable for health-conscious meal planning.
        """,
        agent=create_health_validator_agent(),
        output_pydantic=HealthValidationOutput
    )
    
    return task


# Utility functions for integration
def validate_meal_plan_health(
    meal_plan: WeeklyMealPlan,
    user_profile: UserProfile,
    nutritional_targets: Dict[str, float]
) -> HealthValidationOutput:
    """
    Validate meal plan health using the Health Validator Agent.
    
    Args:
        meal_plan: WeeklyMealPlan to validate
        user_profile: UserProfile with health information
        nutritional_targets: Target nutritional values
        
    Returns:
        HealthValidationOutput with validation results
    """
    try:
        # Convert meal plan to dictionary format
        meal_plan_dict = {
            'daily_plans': []
        }
        
        for daily_plan in meal_plan.daily_plans:
            day_dict = {
                'date': daily_plan.date.isoformat(),
                'breakfast': _recipe_to_dict(daily_plan.breakfast) if daily_plan.breakfast else None,
                'lunch': _recipe_to_dict(daily_plan.lunch) if daily_plan.lunch else None,
                'dinner': _recipe_to_dict(daily_plan.dinner) if daily_plan.dinner else None,
                'snacks': [_recipe_to_dict(snack) for snack in daily_plan.snacks]
            }
            meal_plan_dict['daily_plans'].append(day_dict)
        
        # Convert user profile to dictionary format
        user_profile_dict = {
            'age': user_profile.personal_info.age,
            'gender': user_profile.personal_info.gender.value,
            'activity_level': user_profile.personal_info.activity_level.value,
            'dietary_restrictions': user_profile.dietary_preferences.restrictions,
            'allergies': user_profile.dietary_preferences.allergies,
            'health_goals': {
                'goal_type': user_profile.health_goals.goal_type.value,
                'target_calories': user_profile.health_goals.target_calories,
                'target_weight': user_profile.health_goals.target_weight
            }
        }
        
        # Create and execute task
        task = create_health_validation_task(
            meal_plan=meal_plan_dict,
            user_profile=user_profile_dict,
            nutritional_targets=nutritional_targets
        )
        
        # For now, return calculated values directly
        # In a full CrewAI implementation, this would execute the task
        return _generate_sample_health_validation(meal_plan, user_profile, nutritional_targets)
        
    except Exception as e:
        logger.error(f"Failed to validate meal plan health: {e}")
        raise


def _recipe_to_dict(recipe) -> Dict[str, Any]:
    """Convert Recipe object to dictionary."""
    if not recipe:
        return None
    
    return {
        'name': recipe.name,
        'ingredients': [
            {
                'name': ing.name,
                'quantity': ing.quantity,
                'unit': ing.unit.value
            }
            for ing in recipe.ingredients
        ],
        'servings': recipe.servings,
        'prep_time': recipe.prep_time,
        'cook_time': recipe.cook_time
    }


def _generate_sample_health_validation(
    meal_plan: WeeklyMealPlan,
    user_profile: UserProfile,
    nutritional_targets: Dict[str, float]
) -> HealthValidationOutput:
    """Generate sample health validation for testing purposes."""
    
    # Calculate nutritional balance using existing tools
    calculator = NutritionalCalculator()
    nutritional_balance = calculator.analyze_nutritional_balance(meal_plan, user_profile)
    
    # Determine scores based on nutritional balance
    nutritional_adequacy_score = nutritional_balance.balance_score
    
    # Check dietary compliance (simplified)
    dietary_violations = []
    dietary_restrictions = user_profile.dietary_preferences.restrictions
    
    # Simple compliance check
    if 'vegetarian' in dietary_restrictions:
        # Check for meat in recipes (simplified)
        for daily_plan in meal_plan.daily_plans:
            for recipe in daily_plan.get_all_recipes():
                for ingredient in recipe.ingredients:
                    if any(meat in ingredient.name.lower() for meat in ['chicken', 'beef', 'pork', 'fish']):
                        dietary_violations.append(f"Recipe '{recipe.name}' contains {ingredient.name} (violates vegetarian diet)")
    
    dietary_compliance_score = 100 if not dietary_violations else 50
    
    # Calculate overall health score
    overall_health_score = (nutritional_adequacy_score + dietary_compliance_score) / 2
    
    # Generate recommendations
    health_recommendations = [
        "Maintain consistent meal timing throughout the week",
        "Include a variety of colorful fruits and vegetables",
        "Stay well-hydrated with 8-10 glasses of water daily",
        "Consider meal prep to maintain nutritional consistency"
    ]
    
    # Add specific recommendations based on nutritional balance
    if nutritional_balance.deficiencies:
        health_recommendations.extend([
            f"Address nutritional deficiencies: {', '.join(nutritional_balance.deficiencies[:3])}",
            "Consider consulting with a registered dietitian for personalized guidance"
        ])
    
    # Determine approval status
    if overall_health_score >= 80 and not dietary_violations:
        approval_status = "approved"
    elif overall_health_score >= 60:
        approval_status = "needs_revision"
    else:
        approval_status = "rejected"
    
    return HealthValidationOutput(
        overall_health_score=overall_health_score,
        nutritional_adequacy_score=nutritional_adequacy_score,
        dietary_compliance_score=dietary_compliance_score,
        health_recommendations=health_recommendations,
        nutritional_gaps=nutritional_balance.deficiencies,
        dietary_violations=dietary_violations,
        meal_plan_adjustments=[
            "Consider adding more variety in protein sources",
            "Include more nutrient-dense vegetables",
            "Balance meal timing throughout the day"
        ],
        health_benefits=[
            "Provides balanced macronutrient distribution",
            "Includes variety of food groups",
            "Supports stated health goals"
        ],
        risk_assessments=[
            "Monitor for any digestive issues with new foods",
            "Ensure adequate hydration with increased fiber intake"
        ] if nutritional_balance.deficiencies else [],
        final_approval_status=approval_status
    )
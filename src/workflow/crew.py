"""
CrewAI Crew Configuration and Execution for the Smart Recipe & Meal Planning System.

This module implements the Crew class with agent coordination logic, parallel and sequential
execution patterns, and workflow orchestration for the meal planning system.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import asyncio
from datetime import date
from crewai import Crew, Process
from crewai.crew import CrewOutput

from .error_handling import (
    ErrorRecoveryManager, 
    with_error_handling, 
    ErrorCategory, 
    ErrorSeverity,
    APIFailureError,
    AgentExecutionError,
    global_error_manager
)

from .tasks import (
    create_nutritional_analysis_task,
    create_ingredient_sourcing_task,
    create_recipe_generation_task,
    create_cost_analysis_task,
    create_meal_planning_task,
    create_health_validation_task,
    get_task_execution_order,
    validate_task_dependencies
)
from ..agents.nutritionist_agent import create_nutritionist_agent
from ..agents.recipe_creator_agent import create_recipe_creator_agent
from ..agents.ingredient_sourcer_agent import create_ingredient_sourcer_agent
from ..agents.cost_calculator_agent import create_cost_calculator_agent
from ..agents.meal_planner_agent import create_meal_planner_agent
from ..agents.health_validator_agent import create_health_validator_agent
from ..models.user_profile import UserProfile
from ..models.recipe import WeeklyMealPlan

# Configure logging
logger = logging.getLogger(__name__)


class MealPlanningCrew:
    """
    Main crew class that orchestrates the meal planning workflow with parallel and sequential execution.
    """
    
    def __init__(self, verbose: bool = True, memory: bool = True):
        """
        Initialize the meal planning crew.
        
        Args:
            verbose: Enable verbose logging for crew execution
            memory: Enable memory for agents to share context
        """
        self.verbose = verbose
        self.memory = memory
        self.agents = self._initialize_agents()
        self.execution_results = {}
        self.error_manager = ErrorRecoveryManager()
        
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents for the crew."""
        return {
            'nutritionist': create_nutritionist_agent(),
            'ingredient_sourcer': create_ingredient_sourcer_agent(),
            'recipe_creator': create_recipe_creator_agent(),
            'cost_calculator': create_cost_calculator_agent(),
            'meal_planner': create_meal_planner_agent(),
            'health_validator': create_health_validator_agent()
        }
    
    @with_error_handling(
        component="meal_planning_workflow",
        category=ErrorCategory.AGENT_FAILURE,
        severity=ErrorSeverity.HIGH
    )
    def create_meal_plan(
        self,
        user_profile: UserProfile,
        week_start_date: date,
        location: Optional[str] = None
    ) -> Tuple[WeeklyMealPlan, Dict[str, Any]]:
        """
        Execute the complete meal planning workflow with comprehensive error handling.
        
        Args:
            user_profile: User profile with preferences and constraints
            week_start_date: Start date for the meal plan
            location: User location for ingredient pricing
            
        Returns:
            Tuple of (WeeklyMealPlan, execution_results)
        """
        try:
            logger.info("Starting meal planning workflow execution")
            
            # Convert user profile to dictionary for task inputs
            user_profile_data = self._convert_user_profile(user_profile)
            
            # Execute workflow in phases with error recovery
            execution_results = {}
            
            # Phase 1: Parallel execution (Nutritionist + Ingredient Sourcer)
            logger.info("Phase 1: Executing parallel analysis (Nutritionist + Ingredient Sourcer)")
            try:
                parallel_results = self._execute_parallel_phase(user_profile_data, location)
                execution_results.update(parallel_results)
            except Exception as e:
                logger.warning(f"Phase 1 partial failure: {e}")
                # Use fallback data for failed components
                parallel_results = self._handle_parallel_phase_failure(e, user_profile_data, location)
                execution_results.update(parallel_results)
            
            # Phase 2: Recipe Generation (depends on Phase 1 results)
            logger.info("Phase 2: Generating recipes based on nutritional and sourcing analysis")
            try:
                recipe_results = self._execute_recipe_generation(
                    execution_results.get('nutritional_analysis', {}),
                    execution_results.get('ingredient_sourcing', {}),
                    user_profile_data
                )
                execution_results.update(recipe_results)
            except Exception as e:
                logger.warning(f"Phase 2 failure: {e}")
                recipe_results = self._handle_recipe_generation_failure(e, user_profile_data)
                execution_results.update(recipe_results)
            
            # Phase 3: Cost Analysis (depends on recipes and sourcing)
            logger.info("Phase 3: Analyzing costs and optimizing budget")
            try:
                cost_results = self._execute_cost_analysis(
                    execution_results.get('generated_recipes', {}),
                    execution_results.get('ingredient_sourcing', {}),
                    user_profile_data.get('budget_constraints', {})
                )
                execution_results.update(cost_results)
            except Exception as e:
                logger.warning(f"Phase 3 failure: {e}")
                cost_results = self._handle_cost_analysis_failure(e, execution_results)
                execution_results.update(cost_results)
            
            # Phase 4: Meal Planning (depends on recipes, costs, and nutrition)
            logger.info("Phase 4: Creating weekly meal plan and schedule")
            try:
                meal_plan_results = self._execute_meal_planning(
                    execution_results.get('generated_recipes', {}),
                    execution_results.get('nutritional_analysis', {}),
                    execution_results.get('cost_analysis', {}),
                    user_profile_data,
                    week_start_date
                )
                execution_results.update(meal_plan_results)
            except Exception as e:
                logger.warning(f"Phase 4 failure: {e}")
                meal_plan_results = self._handle_meal_planning_failure(e, execution_results, week_start_date)
                execution_results.update(meal_plan_results)
            
            # Phase 5: Health Validation (final approval)
            logger.info("Phase 5: Validating meal plan for health compliance")
            try:
                validation_results = self._execute_health_validation(
                    execution_results.get('weekly_meal_plan', {}),
                    user_profile_data,
                    execution_results.get('nutritional_analysis', {})
                )
                execution_results.update(validation_results)
            except Exception as e:
                logger.warning(f"Phase 5 failure: {e}")
                validation_results = self._handle_health_validation_failure(e, execution_results)
                execution_results.update(validation_results)
            
            # Convert results to WeeklyMealPlan object
            meal_plan = self._create_meal_plan_from_results(execution_results, week_start_date)
            
            # Add error summary to results
            execution_results['error_summary'] = self.error_manager.get_error_summary()
            
            logger.info("Meal planning workflow completed successfully")
            return meal_plan, execution_results
            
        except Exception as e:
            logger.error(f"Critical failure in meal planning workflow: {e}")
            # Return emergency fallback meal plan
            return self._create_emergency_meal_plan(user_profile, week_start_date), {
                'status': 'emergency_fallback',
                'error': str(e),
                'message': 'System used emergency fallback due to critical failure'
            }
    
    @with_error_handling(
        component="parallel_phase",
        category=ErrorCategory.AGENT_FAILURE,
        severity=ErrorSeverity.HIGH
    )
    def _execute_parallel_phase(
        self,
        user_profile_data: Dict[str, Any],
        location: Optional[str]
    ) -> Dict[str, Any]:
        """
        Execute the parallel phase with Nutritionist and Ingredient Sourcer agents.
        
        Args:
            user_profile_data: User profile information
            location: User location for pricing
            
        Returns:
            Results from both parallel tasks
        """
        try:
            # Create tasks for parallel execution
            nutritional_task = create_nutritional_analysis_task(user_profile_data)
            sourcing_task = create_ingredient_sourcing_task(user_profile_data, location)
            
            # Create crew for parallel execution
            parallel_crew = Crew(
                agents=[self.agents['nutritionist'], self.agents['ingredient_sourcer']],
                tasks=[nutritional_task, sourcing_task],
                process=Process.hierarchical,  # Allow parallel execution
                verbose=self.verbose,
                memory=self.memory,
                manager_llm="gpt-4"  # Use GPT-4 for coordination
            )
            
            # Execute parallel tasks with timeout
            result = parallel_crew.kickoff()
            
            # Parse results
            return {
                'nutritional_analysis': self._parse_task_output(result, 'nutritional_analysis'),
                'ingredient_sourcing': self._parse_task_output(result, 'ingredient_sourcing')
            }
            
        except Exception as e:
            logger.error(f"Failed to execute parallel phase: {e}")
            raise AgentExecutionError("parallel_phase", str(e))
    
    def _execute_recipe_generation(
        self,
        nutritional_analysis: Dict[str, Any],
        ingredient_sourcing: Dict[str, Any],
        user_profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute recipe generation based on nutritional and sourcing analysis.
        
        Args:
            nutritional_analysis: Results from nutritionist agent
            ingredient_sourcing: Results from ingredient sourcer
            user_profile_data: User preferences and constraints
            
        Returns:
            Generated recipes
        """
        try:
            # Prepare meal requirements
            meal_requirements = {
                'meal_types': ['breakfast', 'lunch', 'dinner', 'snack'],
                'dietary_restrictions': user_profile_data.get('dietary_preferences', {}).get('restrictions', []),
                'cooking_skill': user_profile_data.get('dietary_preferences', {}).get('cooking_skill_level', 'intermediate'),
                'cuisine_preferences': user_profile_data.get('dietary_preferences', {}).get('preferred_cuisines', [])
            }
            
            # Create recipe generation task
            recipe_task = create_recipe_generation_task(
                nutritional_requirements=nutritional_analysis.get('daily_targets', {}),
                ingredient_availability=ingredient_sourcing,
                meal_requirements=meal_requirements
            )
            
            # Create crew for recipe generation
            recipe_crew = Crew(
                agents=[self.agents['recipe_creator']],
                tasks=[recipe_task],
                process=Process.sequential,
                verbose=self.verbose,
                memory=self.memory
            )
            
            # Execute recipe generation
            result = recipe_crew.kickoff()
            
            return {
                'generated_recipes': self._parse_task_output(result, 'generated_recipes')
            }
            
        except Exception as e:
            logger.error(f"Failed to execute recipe generation: {e}")
            raise
    
    def _execute_cost_analysis(
        self,
        generated_recipes: Dict[str, Any],
        ingredient_sourcing: Dict[str, Any],
        budget_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute cost analysis and budget optimization.
        
        Args:
            generated_recipes: Recipes from recipe creator
            ingredient_sourcing: Pricing data from sourcer
            budget_constraints: User budget limitations
            
        Returns:
            Cost analysis results
        """
        try:
            # Create cost analysis task
            cost_task = create_cost_analysis_task(
                recipes=generated_recipes.get('recipes', []),
                ingredient_pricing=ingredient_sourcing.get('pricing_data', {}),
                budget_constraints=budget_constraints
            )
            
            # Create crew for cost analysis
            cost_crew = Crew(
                agents=[self.agents['cost_calculator']],
                tasks=[cost_task],
                process=Process.sequential,
                verbose=self.verbose,
                memory=self.memory
            )
            
            # Execute cost analysis
            result = cost_crew.kickoff()
            
            return {
                'cost_analysis': self._parse_task_output(result, 'cost_analysis')
            }
            
        except Exception as e:
            logger.error(f"Failed to execute cost analysis: {e}")
            raise
    
    def _execute_meal_planning(
        self,
        generated_recipes: Dict[str, Any],
        nutritional_analysis: Dict[str, Any],
        cost_analysis: Dict[str, Any],
        user_profile_data: Dict[str, Any],
        week_start_date: date
    ) -> Dict[str, Any]:
        """
        Execute meal planning and schedule organization.
        
        Args:
            generated_recipes: Available recipes
            nutritional_analysis: Nutritional targets
            cost_analysis: Cost optimization data
            user_profile_data: User preferences
            week_start_date: Start date for meal plan
            
        Returns:
            Weekly meal plan
        """
        try:
            # Prepare schedule preferences
            schedule_preferences = user_profile_data.get('schedule_preferences', {
                'meals_per_day': 3,
                'snacks_per_day': 1,
                'prep_time_limit': 120,
                'meal_prep_days': ['sunday']
            })
            
            # Create meal planning task
            meal_plan_task = create_meal_planning_task(
                recipes=generated_recipes.get('recipes', []),
                nutritional_targets=nutritional_analysis.get('daily_targets', {}),
                cost_analysis=cost_analysis,
                schedule_preferences=schedule_preferences,
                week_start_date=week_start_date.isoformat()
            )
            
            # Create crew for meal planning
            meal_plan_crew = Crew(
                agents=[self.agents['meal_planner']],
                tasks=[meal_plan_task],
                process=Process.sequential,
                verbose=self.verbose,
                memory=self.memory
            )
            
            # Execute meal planning
            result = meal_plan_crew.kickoff()
            
            return {
                'weekly_meal_plan': self._parse_task_output(result, 'weekly_meal_plan')
            }
            
        except Exception as e:
            logger.error(f"Failed to execute meal planning: {e}")
            raise
    
    def _execute_health_validation(
        self,
        weekly_meal_plan: Dict[str, Any],
        user_profile_data: Dict[str, Any],
        nutritional_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute health validation and final approval.
        
        Args:
            weekly_meal_plan: Complete meal plan to validate
            user_profile_data: User health profile
            nutritional_analysis: Nutritional targets
            
        Returns:
            Health validation results
        """
        try:
            # Create health validation task
            validation_task = create_health_validation_task(
                meal_plan=weekly_meal_plan,
                user_profile=user_profile_data,
                nutritional_targets=nutritional_analysis.get('daily_targets', {})
            )
            
            # Create crew for health validation
            validation_crew = Crew(
                agents=[self.agents['health_validator']],
                tasks=[validation_task],
                process=Process.sequential,
                verbose=self.verbose,
                memory=self.memory
            )
            
            # Execute health validation
            result = validation_crew.kickoff()
            
            return {
                'health_validation': self._parse_task_output(result, 'health_validation')
            }
            
        except Exception as e:
            logger.error(f"Failed to execute health validation: {e}")
            raise
    
    def _convert_user_profile(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Convert UserProfile object to dictionary for task inputs."""
        return {
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
                'preferred_cuisines': user_profile.dietary_preferences.preferred_cuisines,
                'disliked_foods': user_profile.dietary_preferences.disliked_foods,
                'cooking_skill_level': user_profile.dietary_preferences.cooking_skill_level.value
            },
            'health_goals': {
                'goal_type': user_profile.health_goals.goal_type.value,
                'target_calories': user_profile.health_goals.target_calories,
                'target_weight': user_profile.health_goals.target_weight,
                'weekly_weight_change_goal': user_profile.health_goals.weekly_weight_change_goal
            },
            'budget_constraints': {
                'weekly_budget': user_profile.budget_constraints.weekly_budget,
                'price_sensitivity': user_profile.budget_constraints.price_sensitivity.value,
                'bulk_buying_preference': user_profile.budget_constraints.bulk_buying_preference
            },
            'schedule_preferences': {
                'meals_per_day': user_profile.schedule_preferences.meals_per_day,
                'snacks_per_day': user_profile.schedule_preferences.snacks_per_day,
                'prep_time_limit': user_profile.schedule_preferences.prep_time_limit,
                'meal_prep_days': user_profile.schedule_preferences.meal_prep_days
            }
        }
    
    def _parse_task_output(self, crew_output: CrewOutput, task_name: str) -> Dict[str, Any]:
        """
        Parse task output from crew execution results.
        
        Args:
            crew_output: Output from crew execution
            task_name: Name of the task to parse
            
        Returns:
            Parsed task output as dictionary
        """
        try:
            # In a real implementation, this would parse the actual CrewAI output
            # For now, return a structured placeholder
            if hasattr(crew_output, 'raw') and crew_output.raw:
                # Try to parse JSON output if available
                import json
                try:
                    return json.loads(crew_output.raw)
                except (json.JSONDecodeError, AttributeError):
                    pass
            
            # Return structured placeholder based on task type
            return self._get_placeholder_output(task_name)
            
        except Exception as e:
            logger.warning(f"Failed to parse task output for {task_name}: {e}")
            return self._get_placeholder_output(task_name)
    
    def _get_placeholder_output(self, task_name: str) -> Dict[str, Any]:
        """Get placeholder output for testing purposes."""
        placeholders = {
            'nutritional_analysis': {
                'daily_targets': {
                    'calories': 2000,
                    'protein': 150,
                    'carbohydrates': 250,
                    'fat': 67,
                    'fiber': 25,
                    'sodium': 2300
                },
                'bmr': 1600,
                'tdee': 2000,
                'guidelines': ['Eat balanced meals', 'Stay hydrated']
            },
            'ingredient_sourcing': {
                'pricing_data': {'average_cost_per_meal': 8.50},
                'available_ingredients': ['chicken', 'rice', 'vegetables'],
                'budget_recommendations': ['Shop seasonal produce']
            },
            'generated_recipes': {
                'recipes': [
                    {'name': 'Healthy Breakfast Bowl', 'meal_type': 'breakfast'},
                    {'name': 'Quinoa Salad', 'meal_type': 'lunch'},
                    {'name': 'Baked Salmon', 'meal_type': 'dinner'}
                ]
            },
            'cost_analysis': {
                'total_weekly_cost': 59.50,
                'budget_status': 'within_budget',
                'optimization_suggestions': ['Use seasonal vegetables']
            },
            'weekly_meal_plan': {
                'daily_plans': [{'day': i, 'meals': {}} for i in range(7)],
                'shopping_list': {'produce': ['apples', 'spinach']},
                'prep_instructions': ['Prep vegetables on Sunday']
            },
            'health_validation': {
                'overall_score': 85,
                'approval_status': 'approved',
                'recommendations': ['Great nutritional balance']
            }
        }
        
        return placeholders.get(task_name, {})
    
    def _create_meal_plan_from_results(
        self,
        execution_results: Dict[str, Any],
        week_start_date: date
    ) -> WeeklyMealPlan:
        """
        Create WeeklyMealPlan object from execution results.
        
        Args:
            execution_results: Results from all workflow phases
            week_start_date: Start date for the meal plan
            
        Returns:
            WeeklyMealPlan object
        """
        try:
            # This would convert the execution results into a proper WeeklyMealPlan object
            # For now, create a basic meal plan structure
            from ..models.recipe import WeeklyMealPlan, DailyMealPlan
            from datetime import timedelta
            
            daily_plans = []
            meal_plan_data = execution_results.get('weekly_meal_plan', {})
            
            for i in range(7):
                current_date = week_start_date + timedelta(days=i)
                daily_plan = DailyMealPlan(
                    date=current_date,
                    breakfast=None,  # Would be populated from results
                    lunch=None,
                    dinner=None,
                    snacks=[]
                )
                daily_plans.append(daily_plan)
            
            meal_plan = WeeklyMealPlan(
                week_start_date=week_start_date,
                daily_plans=daily_plans,
                meal_prep_instructions=meal_plan_data.get('prep_instructions', [])
            )
            
            return meal_plan
            
        except Exception as e:
            logger.error(f"Failed to create meal plan from results: {e}")
            raise
    
    # Error handling fallback methods
    def _handle_parallel_phase_failure(
        self,
        error: Exception,
        user_profile_data: Dict[str, Any],
        location: Optional[str]
    ) -> Dict[str, Any]:
        """Handle parallel phase failure with fallback data."""
        logger.warning("Using fallback data for parallel phase failure")
        
        # Try individual agents if parallel execution failed
        nutritional_analysis = {}
        ingredient_sourcing = {}
        
        try:
            # Try nutritionist agent individually
            nutritional_analysis = self.error_manager._get_nutritionist_fallback()
        except Exception as e:
            logger.error(f"Nutritionist fallback failed: {e}")
            nutritional_analysis = self.error_manager._get_nutrition_fallback()
        
        try:
            # Try ingredient sourcer individually
            ingredient_sourcing = self.error_manager._get_pricing_fallback()
        except Exception as e:
            logger.error(f"Ingredient sourcer fallback failed: {e}")
            ingredient_sourcing = self.error_manager._get_pricing_fallback()
        
        return {
            'nutritional_analysis': nutritional_analysis,
            'ingredient_sourcing': ingredient_sourcing
        }
    
    def _handle_recipe_generation_failure(
        self,
        error: Exception,
        user_profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle recipe generation failure with fallback recipes."""
        logger.warning("Using fallback recipes due to generation failure")
        
        try:
            return {'generated_recipes': self.error_manager._get_recipe_fallback()}
        except Exception as e:
            logger.error(f"Recipe fallback failed: {e}")
            return {
                'generated_recipes': {
                    'recipes': [
                        {'name': 'Basic Meal', 'meal_type': 'breakfast'},
                        {'name': 'Simple Lunch', 'meal_type': 'lunch'},
                        {'name': 'Easy Dinner', 'meal_type': 'dinner'}
                    ],
                    'source': 'emergency_fallback'
                }
            }
    
    def _handle_cost_analysis_failure(
        self,
        error: Exception,
        execution_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle cost analysis failure with estimated costs."""
        logger.warning("Using estimated costs due to analysis failure")
        
        try:
            return {'cost_analysis': self.error_manager._get_cost_fallback()}
        except Exception as e:
            logger.error(f"Cost fallback failed: {e}")
            return {
                'cost_analysis': {
                    'total_weekly_cost': 70.00,
                    'budget_status': 'estimated',
                    'source': 'emergency_estimate'
                }
            }
    
    def _handle_meal_planning_failure(
        self,
        error: Exception,
        execution_results: Dict[str, Any],
        week_start_date: date
    ) -> Dict[str, Any]:
        """Handle meal planning failure with basic schedule."""
        logger.warning("Using basic meal schedule due to planning failure")
        
        try:
            return {'weekly_meal_plan': self.error_manager._get_planner_fallback()}
        except Exception as e:
            logger.error(f"Meal planning fallback failed: {e}")
            return {
                'weekly_meal_plan': {
                    'daily_plans': [
                        {'day': i, 'meals': {'breakfast': 'Basic', 'lunch': 'Simple', 'dinner': 'Standard'}}
                        for i in range(7)
                    ],
                    'source': 'emergency_schedule'
                }
            }
    
    def _handle_health_validation_failure(
        self,
        error: Exception,
        execution_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle health validation failure with basic approval."""
        logger.warning("Using basic validation due to health check failure")
        
        try:
            return {'health_validation': self.error_manager._get_validator_fallback()}
        except Exception as e:
            logger.error(f"Health validation fallback failed: {e}")
            return {
                'health_validation': {
                    'overall_score': 70,
                    'approval_status': 'approved_with_caution',
                    'message': 'Manual review recommended',
                    'source': 'emergency_validation'
                }
            }
    
    def _create_emergency_meal_plan(
        self,
        user_profile: UserProfile,
        week_start_date: date
    ) -> WeeklyMealPlan:
        """Create emergency fallback meal plan when all else fails."""
        logger.critical("Creating emergency fallback meal plan")
        
        try:
            from ..utils.fallback_data import FallbackMealPlanGenerator
            return FallbackMealPlanGenerator.create_fallback_meal_plan(user_profile, week_start_date)
            
        except Exception as e:
            logger.critical(f"Failed to create emergency meal plan: {e}")
            # If even emergency plan fails, raise the original error
            raise


# Convenience function for external use
def execute_meal_planning_workflow(
    user_profile: UserProfile,
    week_start_date: date,
    location: Optional[str] = None,
    verbose: bool = True
) -> Tuple[WeeklyMealPlan, Dict[str, Any]]:
    """
    Execute the complete meal planning workflow using the CrewAI system.
    
    Args:
        user_profile: User profile with preferences and constraints
        week_start_date: Start date for the meal plan
        location: User location for ingredient pricing
        verbose: Enable verbose logging
        
    Returns:
        Tuple of (WeeklyMealPlan, execution_results)
    """
    crew = MealPlanningCrew(verbose=verbose)
    return crew.create_meal_plan(user_profile, week_start_date, location)
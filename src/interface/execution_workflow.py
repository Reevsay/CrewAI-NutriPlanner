"""
Meal plan execution workflow with progress tracking and user feedback.

This module provides the main execution function that orchestrates the crew,
implements progress tracking, user feedback, and execution time monitoring.
"""

import time
import sys
from typing import Dict, Any, Optional, Callable
from datetime import date, datetime, timedelta
from loguru import logger

from src.models.user_profile import UserProfile
from src.models.recipe import WeeklyMealPlan
from src.workflow.crew import execute_meal_planning_workflow


class ProgressTracker:
    """Progress tracking utility for meal planning workflow execution."""
    
    def __init__(self):
        self.start_time = None
        self.current_phase = ""
        self.total_phases = 5
        self.completed_phases = 0
        self.phase_start_time = None
        self.phase_times = {}
        
    def start_execution(self):
        """Start tracking execution progress."""
        self.start_time = time.time()
        logger.info("Starting meal planning execution tracking")
        
    def start_phase(self, phase_name: str):
        """Start tracking a specific phase."""
        if self.phase_start_time:
            # Complete previous phase
            self.complete_phase()
        
        self.current_phase = phase_name
        self.phase_start_time = time.time()
        logger.info(f"Starting phase: {phase_name}")
        
    def complete_phase(self):
        """Complete the current phase and record timing."""
        if self.phase_start_time and self.current_phase:
            phase_duration = time.time() - self.phase_start_time
            self.phase_times[self.current_phase] = phase_duration
            self.completed_phases += 1
            
            logger.info(f"Completed phase '{self.current_phase}' in {phase_duration:.2f} seconds")
            self.phase_start_time = None
            
    def get_progress_percentage(self) -> float:
        """Get current progress as percentage."""
        return (self.completed_phases / self.total_phases) * 100
        
    def get_elapsed_time(self) -> float:
        """Get total elapsed time in seconds."""
        if self.start_time:
            return time.time() - self.start_time
        return 0
        
    def get_estimated_remaining_time(self) -> Optional[float]:
        """Estimate remaining execution time based on completed phases."""
        if self.completed_phases == 0:
            return None
            
        avg_phase_time = sum(self.phase_times.values()) / len(self.phase_times)
        remaining_phases = self.total_phases - self.completed_phases
        return avg_phase_time * remaining_phases
        
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get complete execution summary."""
        total_time = self.get_elapsed_time()
        
        return {
            'total_execution_time': total_time,
            'completed_phases': self.completed_phases,
            'total_phases': self.total_phases,
            'progress_percentage': self.get_progress_percentage(),
            'phase_times': self.phase_times.copy(),
            'average_phase_time': sum(self.phase_times.values()) / len(self.phase_times) if self.phase_times else 0
        }


class UserFeedbackManager:
    """Manager for providing user feedback during execution."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.feedback_history = []
        
    def show_welcome_message(self):
        """Display welcome message for meal plan generation."""
        if not self.verbose:
            return
            
        print("\n" + "="*60)
        print("🍽️  SMART MEAL PLANNING SYSTEM - EXECUTION")
        print("="*60)
        print("Creating your personalized weekly meal plan...")
        print("This process involves 5 phases and typically takes 2-5 minutes.")
        print("="*60 + "\n")
        
    def show_phase_start(self, phase_name: str, phase_number: int, total_phases: int):
        """Display phase start information."""
        if not self.verbose:
            return
            
        phase_messages = {
            "nutritional_analysis": "🔬 Analyzing your nutritional needs and dietary requirements",
            "ingredient_sourcing": "🛒 Researching ingredient availability and pricing",
            "recipe_generation": "👨‍🍳 Creating custom recipes based on your preferences",
            "cost_analysis": "💰 Calculating costs and optimizing your budget",
            "meal_planning": "📅 Organizing recipes into your weekly meal schedule",
            "health_validation": "✅ Validating meal plan for nutritional compliance"
        }
        
        message = phase_messages.get(phase_name, f"Processing {phase_name}")
        progress_bar = self._create_progress_bar(phase_number - 1, total_phases)
        
        print(f"\n[{phase_number}/{total_phases}] {message}")
        print(f"Progress: {progress_bar}")
        print("⏳ Working...")
        
        self.feedback_history.append({
            'timestamp': datetime.now(),
            'phase': phase_name,
            'message': message
        })
        
    def show_phase_complete(self, phase_name: str, duration: float, results_summary: str = ""):
        """Display phase completion information."""
        if not self.verbose:
            return
            
        print(f"✅ Completed in {duration:.1f}s")
        if results_summary:
            print(f"   {results_summary}")
            
    def show_progress_update(self, current_phase: int, total_phases: int, elapsed_time: float, estimated_remaining: Optional[float] = None):
        """Show progress update during execution."""
        if not self.verbose:
            return
            
        progress_bar = self._create_progress_bar(current_phase, total_phases)
        
        print(f"\nOverall Progress: {progress_bar}")
        print(f"Elapsed Time: {elapsed_time:.1f}s", end="")
        
        if estimated_remaining:
            print(f" | Estimated Remaining: {estimated_remaining:.1f}s")
        else:
            print()
            
    def show_completion_message(self, execution_summary: Dict[str, Any], meal_plan: WeeklyMealPlan):
        """Display completion message with summary."""
        if not self.verbose:
            return
            
        print("\n" + "="*60)
        print("🎉 MEAL PLAN GENERATION COMPLETE!")
        print("="*60)
        
        total_time = execution_summary.get('total_execution_time', 0)
        print(f"⏱️  Total Execution Time: {total_time:.1f} seconds")
        
        # Show meal plan summary
        daily_plans = len(meal_plan.daily_plans) if meal_plan.daily_plans else 0
        print(f"📅 Generated {daily_plans}-day meal plan")
        
        if hasattr(meal_plan, 'total_cost') and meal_plan.total_cost:
            print(f"💰 Estimated Weekly Cost: ${meal_plan.total_cost:.2f}")
            
        print("\n✨ Your personalized meal plan is ready!")
        print("="*60 + "\n")
        
    def show_error_message(self, error: Exception, phase: str = ""):
        """Display error message to user."""
        print(f"\n❌ Error occurred", end="")
        if phase:
            print(f" during {phase}", end="")
        print(f": {str(error)}")
        
    def show_warning_message(self, message: str):
        """Display warning message to user."""
        if self.verbose:
            print(f"⚠️  {message}")
            
    def _create_progress_bar(self, current: int, total: int, width: int = 30) -> str:
        """Create a text-based progress bar."""
        filled = int(width * current / total)
        bar = "█" * filled + "░" * (width - filled)
        percentage = (current / total) * 100
        return f"[{bar}] {percentage:.1f}%"


class ExecutionOptimizer:
    """Optimizer for execution performance and resource management."""
    
    def __init__(self):
        self.performance_metrics = {}
        self.optimization_suggestions = []
        
    def monitor_memory_usage(self):
        """Monitor memory usage during execution."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            self.performance_metrics['memory_usage_mb'] = memory_info.rss / 1024 / 1024
            
            # Warn if memory usage is high
            if self.performance_metrics['memory_usage_mb'] > 512:
                self.optimization_suggestions.append(
                    "High memory usage detected. Consider reducing batch sizes."
                )
                
        except ImportError:
            # psutil not available, skip memory monitoring
            pass
            
    def monitor_execution_time(self, phase_times: Dict[str, float]):
        """Monitor execution times and suggest optimizations."""
        self.performance_metrics['phase_times'] = phase_times.copy()
        
        # Identify slow phases
        avg_time = sum(phase_times.values()) / len(phase_times) if phase_times else 0
        
        for phase, duration in phase_times.items():
            if duration > avg_time * 2:  # Phase taking more than 2x average
                self.optimization_suggestions.append(
                    f"Phase '{phase}' took longer than expected ({duration:.1f}s). "
                    "Consider checking API connectivity or reducing complexity."
                )
                
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get optimization report with suggestions."""
        return {
            'performance_metrics': self.performance_metrics.copy(),
            'optimization_suggestions': self.optimization_suggestions.copy(),
            'overall_performance': self._calculate_overall_performance()
        }
        
    def _calculate_overall_performance(self) -> str:
        """Calculate overall performance rating."""
        total_time = sum(self.performance_metrics.get('phase_times', {}).values())
        
        if total_time < 60:  # Under 1 minute
            return "excellent"
        elif total_time < 180:  # Under 3 minutes
            return "good"
        elif total_time < 300:  # Under 5 minutes
            return "acceptable"
        else:
            return "slow"


class MealPlanExecutionWorkflow:
    """Main execution workflow orchestrator with comprehensive monitoring."""
    
    def __init__(self, verbose: bool = True, enable_optimization: bool = True):
        self.verbose = verbose
        self.enable_optimization = enable_optimization
        
        self.progress_tracker = ProgressTracker()
        self.feedback_manager = UserFeedbackManager(verbose)
        self.optimizer = ExecutionOptimizer() if enable_optimization else None
        
    def execute_meal_planning(
        self,
        user_profile: UserProfile,
        week_start_date: Optional[date] = None,
        location: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete meal planning workflow with comprehensive monitoring.
        
        Args:
            user_profile: User profile with preferences and constraints
            week_start_date: Start date for meal plan (defaults to next Monday)
            location: User location for ingredient pricing
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing meal plan and execution results
        """
        try:
            # Initialize execution
            if week_start_date is None:
                week_start_date = self._get_next_monday()
                
            self.progress_tracker.start_execution()
            self.feedback_manager.show_welcome_message()
            
            # Phase tracking setup
            phases = [
                ("nutritional_analysis", "Nutritional Analysis"),
                ("ingredient_sourcing", "Ingredient Sourcing"), 
                ("recipe_generation", "Recipe Generation"),
                ("cost_analysis", "Cost Analysis"),
                ("meal_planning", "Meal Planning"),
                ("health_validation", "Health Validation")
            ]
            
            # Execute workflow with monitoring
            logger.info(f"Starting meal plan execution for week of {week_start_date}")
            
            # Show initial progress
            self.feedback_manager.show_phase_start("nutritional_analysis", 1, len(phases))
            self.progress_tracker.start_phase("nutritional_analysis")
            
            # Execute the CrewAI workflow
            meal_plan, execution_results = execute_meal_planning_workflow(
                user_profile=user_profile,
                week_start_date=week_start_date,
                location=location,
                verbose=self.verbose
            )
            
            # Check if meal plan is empty and use fallback if needed
            if not meal_plan or not meal_plan.daily_plans or all(
                not daily_plan.breakfast and not daily_plan.lunch and not daily_plan.dinner 
                for daily_plan in meal_plan.daily_plans
            ):
                logger.warning("Meal plan is empty, using enhanced fallback system")
                from src.utils.fallback_data import FallbackMealPlanGenerator
                meal_plan = FallbackMealPlanGenerator.create_fallback_meal_plan(user_profile, week_start_date)
                execution_results['fallback_used'] = True
                execution_results['fallback_reason'] = 'Empty meal plan detected'
            
            # Complete final phase
            self.progress_tracker.complete_phase()
            
            # Monitor performance if enabled
            if self.optimizer:
                self.optimizer.monitor_memory_usage()
                self.optimizer.monitor_execution_time(self.progress_tracker.phase_times)
                
            # Get execution summary
            execution_summary = self.progress_tracker.get_execution_summary()
            
            # Show completion message
            self.feedback_manager.show_completion_message(execution_summary, meal_plan)
            
            # Prepare final results
            final_results = {
                'meal_plan': meal_plan,
                'execution_results': execution_results,
                'execution_summary': execution_summary,
                'user_profile': user_profile,
                'week_start_date': week_start_date,
                'location': location,
                'success': True
            }
            
            # Add optimization report if available
            if self.optimizer:
                final_results['optimization_report'] = self.optimizer.get_optimization_report()
                
            # Call progress callback if provided
            if progress_callback:
                progress_callback(100, "Complete", final_results)
                
            logger.info("Meal planning execution completed successfully")
            return final_results
            
        except KeyboardInterrupt:
            logger.info("Meal planning execution cancelled by user")
            self.feedback_manager.show_error_message(
                Exception("Execution cancelled by user"), 
                self.progress_tracker.current_phase
            )
            return {
                'success': False,
                'error': 'cancelled_by_user',
                'message': 'Meal planning was cancelled by the user'
            }
            
        except Exception as e:
            logger.error(f"Meal planning execution failed: {e}")
            self.feedback_manager.show_error_message(e, self.progress_tracker.current_phase)
            
            return {
                'success': False,
                'error': str(e),
                'phase': self.progress_tracker.current_phase,
                'execution_summary': self.progress_tracker.get_execution_summary(),
                'message': 'Meal planning execution failed. Please try again or contact support.'
            }
            
    def _get_next_monday(self) -> date:
        """Get the date of the next Monday."""
        today = date.today()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + timedelta(days_ahead)
        
    def estimate_execution_time(self, user_profile: UserProfile) -> Dict[str, Any]:
        """
        Estimate execution time based on user profile complexity.
        
        Args:
            user_profile: User profile to analyze
            
        Returns:
            Dictionary with time estimates
        """
        base_time = 120  # 2 minutes base time
        
        # Add time for complexity factors
        complexity_factors = 0
        
        # Dietary restrictions add complexity
        if user_profile.dietary_preferences.restrictions:
            complexity_factors += len(user_profile.dietary_preferences.restrictions) * 10
            
        # Multiple allergies add complexity
        if user_profile.dietary_preferences.allergies:
            complexity_factors += len(user_profile.dietary_preferences.allergies) * 5
            
        # Tight budget adds complexity
        if user_profile.budget_constraints.weekly_budget < 50:
            complexity_factors += 30
            
        # High meal frequency adds complexity
        total_meals = (user_profile.schedule_preferences.meals_per_day + 
                      user_profile.schedule_preferences.snacks_per_day) * 7
        if total_meals > 28:  # More than 4 items per day
            complexity_factors += 20
            
        estimated_time = base_time + complexity_factors
        
        return {
            'estimated_seconds': estimated_time,
            'estimated_minutes': estimated_time / 60,
            'complexity_factors': complexity_factors,
            'complexity_level': self._get_complexity_level(complexity_factors)
        }
        
    def _get_complexity_level(self, complexity_factors: int) -> str:
        """Determine complexity level based on factors."""
        if complexity_factors < 20:
            return "low"
        elif complexity_factors < 50:
            return "medium"
        elif complexity_factors < 100:
            return "high"
        else:
            return "very_high"


# Convenience function for simple execution
def execute_meal_plan_with_monitoring(
    user_profile: UserProfile,
    week_start_date: Optional[date] = None,
    location: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Execute meal planning with full monitoring and user feedback.
    
    Args:
        user_profile: User profile with preferences and constraints
        week_start_date: Start date for meal plan (defaults to next Monday)
        location: User location for ingredient pricing
        verbose: Enable verbose output and progress tracking
        
    Returns:
        Dictionary containing meal plan and execution results
    """
    workflow = MealPlanExecutionWorkflow(verbose=verbose)
    return workflow.execute_meal_planning(
        user_profile=user_profile,
        week_start_date=week_start_date,
        location=location
    )
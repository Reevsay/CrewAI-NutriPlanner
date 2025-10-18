"""
Simplified user input interface for quick meal planning
"""
import sys
from typing import Optional
from loguru import logger

from src.models.user_profile import (
    UserProfile, PersonalInfo, DietaryPreferences, HealthGoals, 
    BudgetConstraints, SchedulePreferences, Gender, ActivityLevel, GoalType, 
    CookingSkillLevel, PriceSensitivity, MacroPreferences
)


class SimpleUserInput:
    """Simplified user input collection for quick meal planning"""
    
    def __init__(self):
        self.clear_screen = lambda: print("\n" * 2)
    
    def collect_user_profile(self) -> Optional[UserProfile]:
        """Collect user profile with minimal questions"""
        try:
            print("🍽️  Smart Recipe & Meal Planning System - Quick Setup")
            print("=" * 55)
            print("Let's create your meal plan with just a few questions!\n")
            
            # Basic info (required)
            age = self._get_number("Your age", 18, 100, default=30)
            weight = self._get_number("Your weight (kg)", 40, 200, default=70)
            height = self._get_number("Your height (cm)", 140, 220, default=170)
            
            # Gender
            print("\nGender:")
            print("1. Male")
            print("2. Female") 
            print("3. Other")
            gender_choice = self._get_choice("Select gender (1-3)", ["1", "2", "3"], default="2")
            gender_map = {"1": Gender.MALE, "2": Gender.FEMALE, "3": Gender.OTHER}
            gender = gender_map[gender_choice]
            
            # Activity level
            print("\nActivity Level:")
            print("1. Sedentary (desk job, no exercise)")
            print("2. Lightly active (light exercise 1-3 days/week)")
            print("3. Moderately active (moderate exercise 3-5 days/week)")
            print("4. Very active (hard exercise 6-7 days/week)")
            activity_choice = self._get_choice("Select activity level (1-4)", ["1", "2", "3", "4"], default="2")
            activity_map = {
                "1": ActivityLevel.SEDENTARY,
                "2": ActivityLevel.LIGHTLY_ACTIVE, 
                "3": ActivityLevel.MODERATELY_ACTIVE,
                "4": ActivityLevel.VERY_ACTIVE
            }
            activity_level = activity_map[activity_choice]
            
            # Health goal
            print("\nHealth Goal:")
            print("1. Lose weight")
            print("2. Maintain weight")
            print("3. Gain weight/muscle")
            goal_choice = self._get_choice("Select your goal (1-3)", ["1", "2", "3"], default="2")
            goal_map = {"1": GoalType.WEIGHT_LOSS, "2": GoalType.MAINTENANCE, "3": GoalType.MUSCLE_GAIN}
            goal_type = goal_map[goal_choice]
            
            # Dietary restrictions (optional)
            print("\nDietary Restrictions (optional):")
            print("1. None")
            print("2. Vegetarian")
            print("3. Vegan")
            print("4. Keto/Low-carb")
            print("5. Gluten-free")
            diet_choice = self._get_choice("Select dietary preference (1-5)", ["1", "2", "3", "4", "5"], default="1")
            
            dietary_restrictions = []
            if diet_choice == "2":
                dietary_restrictions = ["vegetarian"]
            elif diet_choice == "3":
                dietary_restrictions = ["vegan"]
            elif diet_choice == "4":
                dietary_restrictions = ["keto", "low-carb"]
            elif diet_choice == "5":
                dietary_restrictions = ["gluten-free"]
            
            # Budget
            budget = self._get_number("Weekly grocery budget ($)", 20, 500, default=75)
            
            # Create profile
            personal_info = PersonalInfo(
                age=age,
                weight=weight,
                height=height,
                gender=gender,
                activity_level=activity_level
            )
            
            dietary_preferences = DietaryPreferences(
                restrictions=dietary_restrictions,
                allergies=[],
                disliked_foods=[],
                preferred_cuisines=["any"],
                cooking_skill_level=CookingSkillLevel.INTERMEDIATE
            )
            
            health_goals = HealthGoals(
                goal_type=goal_type,
                target_calories=None,  # Will be calculated
                macro_preferences=MacroPreferences()  # Use defaults
            )
            
            budget_constraints = BudgetConstraints(
                weekly_budget=budget,
                price_sensitivity=PriceSensitivity.MEDIUM,
                bulk_buying_preference=True,
                preferred_stores=["local_grocery"]
            )
            
            schedule_preferences = SchedulePreferences(
                meals_per_day=3,
                snacks_per_day=1,
                prep_time_limit=45,
                cooking_time_limit=60,
                meal_prep_days=["sunday"]
            )
            
            user_profile = UserProfile(
                personal_info=personal_info,
                dietary_preferences=dietary_preferences,
                health_goals=health_goals,
                budget_constraints=budget_constraints,
                schedule_preferences=schedule_preferences
            )
            
            # Show summary
            self._show_summary(user_profile)
            
            confirm = input("\nLooks good? (y/n, or press Enter for yes): ").strip().lower()
            if confirm and confirm not in ['y', 'yes']:
                print("Let's try again...")
                return self.collect_user_profile()
            
            return user_profile
            
        except KeyboardInterrupt:
            print("\n\nSetup cancelled. Goodbye!")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error in simple profile collection: {e}")
            print(f"❌ Error: {e}")
            print("Let's try again...")
            return self.collect_user_profile()
    
    def _get_number(self, prompt: str, min_val: int, max_val: int, default: int) -> int:
        """Get a number input with validation"""
        while True:
            try:
                response = input(f"{prompt} ({min_val}-{max_val}, or press Enter for {default}): ").strip()
                if not response:
                    return default
                
                value = int(response)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"Please enter a number between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
    
    def _get_choice(self, prompt: str, valid_choices: list, default: str) -> str:
        """Get a choice input with validation"""
        while True:
            response = input(f"{prompt} (or press Enter for {default}): ").strip()
            if not response:
                return default
            
            if response in valid_choices:
                return response
            else:
                print(f"Please enter one of: {', '.join(valid_choices)}")
    
    def _show_summary(self, profile: UserProfile):
        """Show a brief summary of the profile"""
        print("\n" + "="*40)
        print("📋 Your Profile Summary")
        print("="*40)
        
        # Personal info
        pi = profile.personal_info
        print(f"👤 {pi.age} year old {pi.gender.value}, {pi.height}cm, {pi.weight}kg")
        print(f"🏃 Activity: {pi.activity_level.value.replace('_', ' ').title()}")
        
        # Goal
        goal_text = profile.health_goals.goal_type.value.replace('_', ' ').title()
        print(f"🎯 Goal: {goal_text}")
        
        # Diet
        if profile.dietary_preferences.restrictions:
            diet_text = ", ".join(profile.dietary_preferences.restrictions).title()
            print(f"🥗 Diet: {diet_text}")
        else:
            print("🥗 Diet: No restrictions")
        
        # Budget
        print(f"💰 Budget: ${profile.budget_constraints.weekly_budget}/week")
        
        print("="*40)
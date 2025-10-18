"""
User input processing for the Smart Recipe & Meal Planning System.

This module provides command-line interface functionality for collecting and validating
user profile information with user-friendly prompts and comprehensive input validation.
"""

import sys
from typing import List, Optional, Dict, Any, Tuple
from loguru import logger

from src.models.user_profile import (
    UserProfile, PersonalInfo, DietaryPreferences, HealthGoals, 
    BudgetConstraints, SchedulePreferences, MacroPreferences,
    ActivityLevel, Gender, GoalType, CookingSkillLevel, PriceSensitivity
)


class UserPrompts:
    """User-friendly prompts and help messages for input collection."""
    
    WELCOME_MESSAGE = """
🍽️  Smart Recipe & Meal Planning System
=====================================

Welcome! I'll help you create a personalized weekly meal plan with recipes,
nutritional analysis, and shopping lists tailored to your preferences and goals.

Let's start by gathering some information about you and your preferences.
You can type 'help' at any prompt for more information, or 'quit' to exit.
"""

    PERSONAL_INFO_INTRO = """
📊 Personal Information
======================
First, I need some basic information to calculate your nutritional needs.
"""

    DIETARY_PREFS_INTRO = """
🥗 Dietary Preferences
=====================
Now let's talk about your dietary preferences and restrictions.
"""

    HEALTH_GOALS_INTRO = """
🎯 Health Goals
==============
What are your health and fitness goals?
"""

    BUDGET_INTRO = """
💰 Budget Information
====================
Let's discuss your budget and shopping preferences.
"""

    SCHEDULE_INTRO = """
⏰ Schedule Preferences
======================
Finally, tell me about your meal timing and preparation preferences.
"""

    @staticmethod
    def get_help_text(field: str) -> str:
        """Get help text for specific input fields."""
        help_texts = {
            "age": "Enter your age in years (13-120). This helps calculate your nutritional needs.",
            "weight": "Enter your current weight in kilograms. For reference: 1 lb = 0.45 kg",
            "height": "Enter your height in centimeters. For reference: 1 inch = 2.54 cm, 5'6\" = 168 cm",
            "activity_level": """Activity levels:
- sedentary: Little to no exercise, desk job
- lightly_active: Light exercise 1-3 days/week
- moderately_active: Moderate exercise 3-5 days/week  
- very_active: Hard exercise 6-7 days/week
- extremely_active: Very hard exercise, physical job""",
            "gender": "Select your gender for accurate nutritional calculations (male/female/other)",
            "restrictions": """Common dietary restrictions (separate multiple with commas):
vegetarian, vegan, pescatarian, keto, paleo, mediterranean, gluten_free, 
dairy_free, nut_free, low_sodium, low_carb, high_protein, diabetic_friendly, 
heart_healthy, kosher, halal""",
            "allergies": """Common allergens (separate multiple with commas):
peanuts, tree_nuts, milk, eggs, fish, shellfish, soy, wheat, sesame, sulfites""",
            "goal_type": """Health goals:
- weight_loss: Lose weight safely
- muscle_gain: Build muscle mass
- maintenance: Maintain current weight
- general_health: Focus on overall health""",
            "weekly_budget": "Enter your weekly grocery budget in your local currency (e.g., 100 for $100/week)",
            "price_sensitivity": """Price sensitivity levels:
- low: Premium ingredients, organic options
- medium: Balance of quality and cost
- high: Focus on budget-friendly options"""
        }
        return help_texts.get(field, "No help available for this field.")


class InputValidator:
    """Input validation utilities with user-friendly error messages."""
    
    @staticmethod
    def validate_numeric_input(value: str, min_val: float, max_val: float, 
                             field_name: str, is_int: bool = False) -> Tuple[bool, Optional[float], str]:
        """Validate numeric input with range checking."""
        try:
            if is_int:
                num_value = int(value)
            else:
                num_value = float(value)
            
            if not (min_val <= num_value <= max_val):
                return False, None, f"{field_name} must be between {min_val} and {max_val}"
            
            return True, num_value, ""
        except ValueError:
            return False, None, f"{field_name} must be a valid number"
    
    @staticmethod
    def validate_enum_input(value: str, enum_class, field_name: str) -> Tuple[bool, Optional[Any], str]:
        """Validate enum input with suggestions."""
        try:
            # Try direct enum value lookup
            enum_value = enum_class(value.lower())
            return True, enum_value, ""
        except ValueError:
            valid_options = [e.value for e in enum_class]
            return False, None, f"Invalid {field_name}. Valid options: {', '.join(valid_options)}"
    
    @staticmethod
    def validate_list_input(value: str, valid_items: set = None) -> Tuple[bool, List[str], str]:
        """Validate comma-separated list input."""
        if not value.strip():
            return True, [], ""
        
        items = [item.strip().lower() for item in value.split(',') if item.strip()]
        
        if valid_items:
            invalid_items = [item for item in items if item not in valid_items]
            if invalid_items:
                return False, [], f"Invalid items: {', '.join(invalid_items)}"
        
        return True, items, ""


class UserInputProcessor:
    """Main class for processing user input with validation and user-friendly prompts."""
    
    def __init__(self):
        self.prompts = UserPrompts()
        self.validator = InputValidator()
    
    def get_input_with_validation(self, prompt: str, validator_func, help_text: str = "") -> Any:
        """Get user input with validation and retry logic."""
        while True:
            try:
                user_input = input(f"{prompt}: ").strip()
                
                if user_input.lower() == 'quit':
                    print("Goodbye!")
                    sys.exit(0)
                
                if user_input.lower() == 'help':
                    print(f"\n{help_text}\n")
                    continue
                
                if not user_input and hasattr(validator_func, '__defaults__'):
                    # Allow empty input if there's a default value
                    return validator_func("")
                
                result = validator_func(user_input)
                if isinstance(result, tuple) and len(result) == 3:
                    is_valid, value, error_msg = result
                    if is_valid:
                        return value
                    else:
                        print(f"❌ {error_msg}")
                        continue
                else:
                    return result
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Input processing error: {e}")
                print("❌ An error occurred. Please try again.")
    
    def collect_personal_info(self) -> PersonalInfo:
        """Collect and validate personal information."""
        print(self.prompts.PERSONAL_INFO_INTRO)
        
        # Age
        age = self.get_input_with_validation(
            "Enter your age (years)",
            lambda x: self.validator.validate_numeric_input(x, 13, 120, "Age", is_int=True),
            self.prompts.get_help_text("age")
        )
        
        # Weight
        weight = self.get_input_with_validation(
            "Enter your weight (kg)",
            lambda x: self.validator.validate_numeric_input(x, 30, 300, "Weight"),
            self.prompts.get_help_text("weight")
        )
        
        # Height
        height = self.get_input_with_validation(
            "Enter your height (cm)",
            lambda x: self.validator.validate_numeric_input(x, 100, 250, "Height"),
            self.prompts.get_help_text("height")
        )
        
        # Activity Level
        activity_level = self.get_input_with_validation(
            "Enter your activity level (sedentary/lightly_active/moderately_active/very_active/extremely_active)",
            lambda x: self.validator.validate_enum_input(x, ActivityLevel, "activity level"),
            self.prompts.get_help_text("activity_level")
        )
        
        # Gender
        gender = self.get_input_with_validation(
            "Enter your gender (male/female/other)",
            lambda x: self.validator.validate_enum_input(x, Gender, "gender"),
            self.prompts.get_help_text("gender")
        )
        
        return PersonalInfo(
            age=age,
            weight=weight,
            height=height,
            activity_level=activity_level,
            gender=gender
        )
    
    def collect_dietary_preferences(self) -> DietaryPreferences:
        """Collect and validate dietary preferences."""
        print(self.prompts.DIETARY_PREFS_INTRO)
        
        # Dietary restrictions
        restrictions_input = input("Enter dietary restrictions (comma-separated, or press Enter for none): ").strip()
        is_valid, restrictions, error_msg = self.validator.validate_list_input(
            restrictions_input, DietaryPreferences.VALID_RESTRICTIONS
        )
        if not is_valid:
            print(f"❌ {error_msg}")
            print(f"Valid restrictions: {', '.join(DietaryPreferences.VALID_RESTRICTIONS)}")
            restrictions = []
        
        # Allergies
        allergies_input = input("Enter food allergies (comma-separated, or press Enter for none): ").strip()
        is_valid, allergies, _ = self.validator.validate_list_input(allergies_input)
        
        # Preferred cuisines
        cuisines_input = input("Enter preferred cuisines (comma-separated, or press Enter for any): ").strip()
        is_valid, preferred_cuisines, _ = self.validator.validate_list_input(cuisines_input)
        
        # Disliked foods
        dislikes_input = input("Enter foods you dislike (comma-separated, or press Enter for none): ").strip()
        is_valid, disliked_foods, _ = self.validator.validate_list_input(dislikes_input)
        
        # Cooking skill level
        cooking_skill = self.get_input_with_validation(
            "Enter your cooking skill level (beginner/intermediate/advanced)",
            lambda x: self.validator.validate_enum_input(x, CookingSkillLevel, "cooking skill level") if x else (True, CookingSkillLevel.INTERMEDIATE, ""),
            "Your cooking skill level helps determine recipe complexity"
        )
        
        return DietaryPreferences(
            restrictions=restrictions,
            allergies=allergies,
            preferred_cuisines=preferred_cuisines,
            disliked_foods=disliked_foods,
            cooking_skill_level=cooking_skill
        )
    
    def collect_health_goals(self) -> HealthGoals:
        """Collect and validate health goals."""
        print(self.prompts.HEALTH_GOALS_INTRO)
        
        # Goal type
        goal_type = self.get_input_with_validation(
            "Enter your primary health goal (weight_loss/muscle_gain/maintenance/general_health)",
            lambda x: self.validator.validate_enum_input(x, GoalType, "goal type"),
            self.prompts.get_help_text("goal_type")
        )
        
        # Target calories (optional)
        calories_input = input("Enter target daily calories (or press Enter to calculate automatically): ").strip()
        target_calories = None
        if calories_input:
            is_valid, target_calories, error_msg = self.validator.validate_numeric_input(
                calories_input, 800, 5000, "Target calories", is_int=True
            )
            if not is_valid:
                print(f"❌ {error_msg}. Will calculate automatically.")
                target_calories = None
        
        # Macro preferences (optional)
        print("\nMacronutrient preferences (optional - press Enter to use defaults):")
        
        protein_input = input("Protein percentage (10-35%, or press Enter for default): ").strip()
        protein_pct = None
        if protein_input:
            is_valid, protein_pct, error_msg = self.validator.validate_numeric_input(
                protein_input, 10, 35, "Protein percentage"
            )
            if not is_valid:
                print(f"❌ {error_msg}")
                protein_pct = None
        
        carb_input = input("Carbohydrate percentage (45-65%, or press Enter for default): ").strip()
        carb_pct = None
        if carb_input:
            is_valid, carb_pct, error_msg = self.validator.validate_numeric_input(
                carb_input, 45, 65, "Carbohydrate percentage"
            )
            if not is_valid:
                print(f"❌ {error_msg}")
                carb_pct = None
        
        fat_input = input("Fat percentage (20-35%, or press Enter for default): ").strip()
        fat_pct = None
        if fat_input:
            is_valid, fat_pct, error_msg = self.validator.validate_numeric_input(
                fat_input, 20, 35, "Fat percentage"
            )
            if not is_valid:
                print(f"❌ {error_msg}")
                fat_pct = None
        
        macro_preferences = MacroPreferences(
            protein_percentage=protein_pct,
            carb_percentage=carb_pct,
            fat_percentage=fat_pct
        )
        
        return HealthGoals(
            goal_type=goal_type,
            target_calories=target_calories,
            macro_preferences=macro_preferences
        )
    
    def collect_budget_constraints(self) -> BudgetConstraints:
        """Collect and validate budget constraints."""
        print(self.prompts.BUDGET_INTRO)
        
        # Weekly budget
        weekly_budget = self.get_input_with_validation(
            "Enter your weekly grocery budget",
            lambda x: self.validator.validate_numeric_input(x, 1, 1000, "Weekly budget"),
            self.prompts.get_help_text("weekly_budget")
        )
        
        # Price sensitivity
        price_sensitivity = self.get_input_with_validation(
            "Enter your price sensitivity (low/medium/high)",
            lambda x: self.validator.validate_enum_input(x, PriceSensitivity, "price sensitivity") if x else (True, PriceSensitivity.MEDIUM, ""),
            self.prompts.get_help_text("price_sensitivity")
        )
        
        # Bulk buying preference
        bulk_input = input("Do you prefer bulk buying when possible? (y/n, or press Enter for no): ").strip().lower()
        bulk_buying = bulk_input in ['y', 'yes', 'true', '1']
        
        # Preferred stores (optional)
        stores_input = input("Enter preferred grocery stores (comma-separated, or press Enter for any): ").strip()
        is_valid, preferred_stores, _ = self.validator.validate_list_input(stores_input)
        
        return BudgetConstraints(
            weekly_budget=weekly_budget,
            price_sensitivity=price_sensitivity,
            bulk_buying_preference=bulk_buying,
            preferred_stores=preferred_stores
        )
    
    def collect_schedule_preferences(self) -> SchedulePreferences:
        """Collect and validate schedule preferences."""
        print(self.prompts.SCHEDULE_INTRO)
        
        # Meals per day
        meals_per_day = self.get_input_with_validation(
            "How many main meals per day? (1-6, or press Enter for 3)",
            lambda x: self.validator.validate_numeric_input(x, 1, 6, "Meals per day", is_int=True) if x.strip() else (True, 3, ""),
            "Number of main meals (breakfast, lunch, dinner, etc.)"
        )
        
        # Snacks per day
        snacks_per_day = self.get_input_with_validation(
            "How many snacks per day? (0-5, or press Enter for 1)",
            lambda x: self.validator.validate_numeric_input(x, 0, 5, "Snacks per day", is_int=True) if x.strip() else (True, 1, ""),
            "Number of snacks between meals"
        )
        
        # Prep time limit
        prep_time = self.get_input_with_validation(
            "Maximum prep time per meal in minutes? (5-180, or press Enter for 60)",
            lambda x: self.validator.validate_numeric_input(x, 5, 180, "Prep time", is_int=True) if x.strip() else (True, 60, ""),
            "Maximum time you want to spend preparing ingredients"
        )
        
        # Cooking time limit
        cook_time = self.get_input_with_validation(
            "Maximum cooking time per meal in minutes? (10-240, or press Enter for 45)",
            lambda x: self.validator.validate_numeric_input(x, 10, 240, "Cooking time", is_int=True) if x.strip() else (True, 45, ""),
            "Maximum time you want to spend actively cooking"
        )
        
        return SchedulePreferences(
            meals_per_day=meals_per_day,
            snacks_per_day=snacks_per_day,
            prep_time_limit=prep_time,
            cooking_time_limit=cook_time
        )
    
    def collect_user_profile(self) -> UserProfile:
        """Collect complete user profile with validation."""
        print(self.prompts.WELCOME_MESSAGE)
        
        try:
            # Collect all profile sections
            personal_info = self.collect_personal_info()
            dietary_preferences = self.collect_dietary_preferences()
            health_goals = self.collect_health_goals()
            budget_constraints = self.collect_budget_constraints()
            schedule_preferences = self.collect_schedule_preferences()
            
            # Create user profile
            user_profile = UserProfile(
                personal_info=personal_info,
                dietary_preferences=dietary_preferences,
                health_goals=health_goals,
                budget_constraints=budget_constraints,
                schedule_preferences=schedule_preferences
            )
            
            # Validate the complete profile
            validation_results = user_profile.validate()
            
            # Display validation results
            has_errors = False
            for section, errors in validation_results.items():
                if errors:
                    has_errors = True
                    print(f"\n⚠️  Issues in {section}:")
                    for error in errors:
                        print(f"   • {error}")
            
            if has_errors:
                print("\n❌ Please review the issues above.")
                retry = input("Would you like to re-enter your information? (y/n): ").strip().lower()
                if retry in ['y', 'yes']:
                    return self.collect_user_profile()
                else:
                    print("Proceeding with current information...")
            else:
                print("\n✅ Profile validation successful!")
            
            # Display profile summary
            self.display_profile_summary(user_profile)
            
            confirm = input("\nIs this information correct? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                return self.collect_user_profile()
            
            return user_profile
            
        except KeyboardInterrupt:
            print("\n\nProfile collection cancelled. Goodbye!")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error collecting user profile: {e}")
            print("❌ An error occurred while collecting your profile. Please try again.")
            return self.collect_user_profile()
    
    def display_profile_summary(self, profile: UserProfile) -> None:
        """Display a summary of the collected user profile."""
        print("\n" + "="*50)
        print("📋 PROFILE SUMMARY")
        print("="*50)
        
        # Personal Info
        print(f"👤 Personal: {profile.personal_info.age}y, {profile.personal_info.weight}kg, {profile.personal_info.height}cm")
        print(f"   Activity: {profile.personal_info.activity_level.value}, Gender: {profile.personal_info.gender.value}")
        
        # Dietary Preferences
        if profile.dietary_preferences.restrictions:
            print(f"🥗 Restrictions: {', '.join(profile.dietary_preferences.restrictions)}")
        if profile.dietary_preferences.allergies:
            print(f"⚠️  Allergies: {', '.join(profile.dietary_preferences.allergies)}")
        print(f"👨‍🍳 Cooking Level: {profile.dietary_preferences.cooking_skill_level.value}")
        
        # Health Goals
        print(f"🎯 Goal: {profile.health_goals.goal_type.value}")
        if profile.health_goals.target_calories:
            print(f"   Target Calories: {profile.health_goals.target_calories}/day")
        
        # Budget
        print(f"💰 Weekly Budget: ${profile.budget_constraints.weekly_budget}")
        print(f"   Price Sensitivity: {profile.budget_constraints.price_sensitivity.value}")
        
        # Schedule
        print(f"⏰ Meals/Day: {profile.schedule_preferences.meals_per_day}, Snacks: {profile.schedule_preferences.snacks_per_day}")
        print(f"   Max Prep: {profile.schedule_preferences.prep_time_limit}min, Max Cook: {profile.schedule_preferences.cooking_time_limit}min")
        
        print("="*50)
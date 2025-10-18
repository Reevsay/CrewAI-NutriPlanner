"""
User profile data models for the Smart Recipe & Meal Planning System.

This module contains data models for user profiles, personal information,
dietary preferences, health goals, and budget constraints with validation methods.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import re
from datetime import date


class ActivityLevel(Enum):
    """User activity levels for caloric calculations."""
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class Gender(Enum):
    """User gender for nutritional calculations."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class GoalType(Enum):
    """Health goal types."""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    GENERAL_HEALTH = "general_health"


class CookingSkillLevel(Enum):
    """Cooking skill levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class PriceSensitivity(Enum):
    """Budget price sensitivity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class MacroPreferences:
    """Macronutrient preferences and targets."""
    protein_percentage: Optional[float] = None  # 10-35%
    carb_percentage: Optional[float] = None     # 45-65%
    fat_percentage: Optional[float] = None      # 20-35%
    
    def validate(self) -> List[str]:
        """Validate macro preferences."""
        errors = []
        
        if self.protein_percentage is not None:
            if not (10 <= self.protein_percentage <= 35):
                errors.append("Protein percentage must be between 10-35%")
        
        if self.carb_percentage is not None:
            if not (45 <= self.carb_percentage <= 65):
                errors.append("Carbohydrate percentage must be between 45-65%")
        
        if self.fat_percentage is not None:
            if not (20 <= self.fat_percentage <= 35):
                errors.append("Fat percentage must be between 20-35%")
        
        # Check if percentages add up to 100 when all are provided
        if all([self.protein_percentage, self.carb_percentage, self.fat_percentage]):
            total = self.protein_percentage + self.carb_percentage + self.fat_percentage
            if abs(total - 100) > 1:  # Allow 1% tolerance
                errors.append("Macro percentages must add up to 100%")
        
        return errors


@dataclass
class PersonalInfo:
    """Personal information for nutritional calculations."""
    age: int
    weight: float  # in kg
    height: float  # in cm
    activity_level: ActivityLevel
    gender: Gender
    
    def validate(self) -> List[str]:
        """Validate personal information."""
        errors = []
        
        if not (13 <= self.age <= 120):
            errors.append("Age must be between 13 and 120 years")
        
        if not (30 <= self.weight <= 300):
            errors.append("Weight must be between 30 and 300 kg")
        
        if not (100 <= self.height <= 250):
            errors.append("Height must be between 100 and 250 cm")
        
        if not isinstance(self.activity_level, ActivityLevel):
            errors.append("Activity level must be a valid ActivityLevel enum")
        
        if not isinstance(self.gender, Gender):
            errors.append("Gender must be a valid Gender enum")
        
        return errors


@dataclass
class DietaryPreferences:
    """Dietary preferences, restrictions, and cooking preferences."""
    restrictions: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    preferred_cuisines: List[str] = field(default_factory=list)
    disliked_foods: List[str] = field(default_factory=list)
    cooking_skill_level: CookingSkillLevel = CookingSkillLevel.INTERMEDIATE
    
    # Common dietary restrictions for validation
    VALID_RESTRICTIONS = {
        "vegetarian", "vegan", "pescatarian", "keto", "paleo", "mediterranean",
        "gluten_free", "dairy_free", "nut_free", "low_sodium", "low_carb",
        "high_protein", "diabetic_friendly", "heart_healthy", "kosher", "halal"
    }
    
    # Common allergens
    COMMON_ALLERGENS = {
        "peanuts", "tree_nuts", "milk", "eggs", "fish", "shellfish", 
        "soy", "wheat", "sesame", "sulfites"
    }
    
    def validate(self) -> List[str]:
        """Validate dietary preferences."""
        errors = []
        
        # Validate restrictions
        for restriction in self.restrictions:
            if restriction.lower() not in self.VALID_RESTRICTIONS:
                errors.append(f"Unknown dietary restriction: {restriction}")
        
        # Validate allergies
        for allergy in self.allergies:
            if allergy.lower() not in self.COMMON_ALLERGENS:
                # Allow custom allergies but warn
                pass
        
        # Check for conflicting restrictions
        if "vegan" in self.restrictions and "pescatarian" in self.restrictions:
            errors.append("Vegan and pescatarian restrictions are conflicting")
        
        if "vegetarian" in self.restrictions and "pescatarian" in self.restrictions:
            errors.append("Vegetarian and pescatarian restrictions are conflicting")
        
        if not isinstance(self.cooking_skill_level, CookingSkillLevel):
            errors.append("Cooking skill level must be a valid CookingSkillLevel enum")
        
        return errors


@dataclass
class HealthGoals:
    """Health goals and nutritional targets."""
    goal_type: GoalType
    target_calories: Optional[int] = None
    macro_preferences: MacroPreferences = field(default_factory=MacroPreferences)
    target_weight: Optional[float] = None  # in kg
    weekly_weight_change_goal: Optional[float] = None  # kg per week
    
    def validate(self) -> List[str]:
        """Validate health goals."""
        errors = []
        
        if not isinstance(self.goal_type, GoalType):
            errors.append("Goal type must be a valid GoalType enum")
        
        if self.target_calories is not None:
            if not (800 <= self.target_calories <= 5000):
                errors.append("Target calories must be between 800 and 5000")
        
        if self.target_weight is not None:
            if not (30 <= self.target_weight <= 300):
                errors.append("Target weight must be between 30 and 300 kg")
        
        if self.weekly_weight_change_goal is not None:
            if not (-2 <= self.weekly_weight_change_goal <= 2):
                errors.append("Weekly weight change goal must be between -2 and 2 kg per week")
        
        # Validate macro preferences
        macro_errors = self.macro_preferences.validate()
        errors.extend(macro_errors)
        
        return errors


@dataclass
class BudgetConstraints:
    """Budget constraints and shopping preferences."""
    weekly_budget: float
    price_sensitivity: PriceSensitivity = PriceSensitivity.MEDIUM
    bulk_buying_preference: bool = False
    preferred_stores: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate budget constraints."""
        errors = []
        
        if self.weekly_budget <= 0:
            errors.append("Weekly budget must be greater than 0")
        
        if self.weekly_budget > 1000:
            errors.append("Weekly budget seems unreasonably high (>$1000)")
        
        if not isinstance(self.price_sensitivity, PriceSensitivity):
            errors.append("Price sensitivity must be a valid PriceSensitivity enum")
        
        return errors


@dataclass
class SchedulePreferences:
    """Meal timing and preparation preferences."""
    meals_per_day: int = 3
    snacks_per_day: int = 1
    prep_time_limit: int = 60  # minutes
    cooking_time_limit: int = 45  # minutes
    meal_prep_days: List[str] = field(default_factory=lambda: ["sunday"])
    
    def validate(self) -> List[str]:
        """Validate schedule preferences."""
        errors = []
        
        if not (1 <= self.meals_per_day <= 6):
            errors.append("Meals per day must be between 1 and 6")
        
        if not (0 <= self.snacks_per_day <= 5):
            errors.append("Snacks per day must be between 0 and 5")
        
        if not (5 <= self.prep_time_limit <= 180):
            errors.append("Prep time limit must be between 5 and 180 minutes")
        
        if not (10 <= self.cooking_time_limit <= 240):
            errors.append("Cooking time limit must be between 10 and 240 minutes")
        
        valid_days = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        for day in self.meal_prep_days:
            if day.lower() not in valid_days:
                errors.append(f"Invalid meal prep day: {day}")
        
        return errors


@dataclass
class UserProfile:
    """Complete user profile for meal planning system."""
    personal_info: PersonalInfo
    dietary_preferences: DietaryPreferences
    health_goals: HealthGoals
    budget_constraints: BudgetConstraints
    schedule_preferences: SchedulePreferences = field(default_factory=SchedulePreferences)
    
    def validate(self) -> Dict[str, List[str]]:
        """Validate the complete user profile."""
        validation_results = {
            "personal_info": self.personal_info.validate(),
            "dietary_preferences": self.dietary_preferences.validate(),
            "health_goals": self.health_goals.validate(),
            "budget_constraints": self.budget_constraints.validate(),
            "schedule_preferences": self.schedule_preferences.validate()
        }
        
        # Cross-validation checks
        cross_validation_errors = []
        
        # Check if target weight is reasonable compared to current weight
        if (self.health_goals.target_weight and 
            abs(self.health_goals.target_weight - self.personal_info.weight) > 50):
            cross_validation_errors.append(
                "Target weight differs significantly from current weight (>50kg)"
            )
        
        # Check if calorie goals align with weight goals
        if (self.health_goals.goal_type == GoalType.WEIGHT_LOSS and 
            self.health_goals.weekly_weight_change_goal and 
            self.health_goals.weekly_weight_change_goal > 0):
            cross_validation_errors.append(
                "Weight loss goal conflicts with positive weight change goal"
            )
        
        if cross_validation_errors:
            validation_results["cross_validation"] = cross_validation_errors
        
        return validation_results
    
    def is_valid(self) -> bool:
        """Check if the user profile is valid."""
        validation_results = self.validate()
        return all(not errors for errors in validation_results.values())
    
    def get_all_errors(self) -> List[str]:
        """Get all validation errors as a flat list."""
        validation_results = self.validate()
        all_errors = []
        for section, errors in validation_results.items():
            for error in errors:
                all_errors.append(f"{section}: {error}")
        return all_errors
"""
Sample user profiles for testing and demonstration.

This module contains diverse user profiles covering different dietary needs,
edge cases with multiple restrictions, tight budgets, and realistic scenarios
for demonstrating the Smart Recipe & Meal Planning System capabilities.
"""

from src.models.user_profile import (
    UserProfile, PersonalInfo, DietaryPreferences, HealthGoals, 
    BudgetConstraints, SchedulePreferences, MacroPreferences,
    ActivityLevel, Gender, GoalType, CookingSkillLevel, PriceSensitivity
)


# Profile 1: Young Professional - Weight Loss on Tight Budget
young_professional_weight_loss = UserProfile(
    personal_info=PersonalInfo(
        age=28,
        weight=75.0,  # kg
        height=165.0,  # cm
        activity_level=ActivityLevel.LIGHTLY_ACTIVE,
        gender=Gender.FEMALE
    ),
    dietary_preferences=DietaryPreferences(
        restrictions=["vegetarian"],
        allergies=[],
        preferred_cuisines=["mediterranean", "asian"],
        disliked_foods=["mushrooms", "olives"],
        cooking_skill_level=CookingSkillLevel.BEGINNER
    ),
    health_goals=HealthGoals(
        goal_type=GoalType.WEIGHT_LOSS,
        target_calories=1500,
        macro_preferences=MacroPreferences(
            protein_percentage=25.0,
            carb_percentage=45.0,
            fat_percentage=30.0
        ),
        target_weight=65.0,
        weekly_weight_change_goal=-0.5
    ),
    budget_constraints=BudgetConstraints(
        weekly_budget=50.0,  # Very tight budget
        price_sensitivity=PriceSensitivity.HIGH,
        bulk_buying_preference=True,
        preferred_stores=["walmart", "aldi"]
    ),
    schedule_preferences=SchedulePreferences(
        meals_per_day=3,
        snacks_per_day=2,
        prep_time_limit=30,  # Limited time
        cooking_time_limit=20,  # Quick meals
        meal_prep_days=["sunday"]
    )
)


# Profile 2: Athletic Male - Muscle Gain with High Budget
athletic_muscle_gain = UserProfile(
    personal_info=PersonalInfo(
        age=24,
        weight=80.0,
        height=180.0,
        activity_level=ActivityLevel.VERY_ACTIVE,
        gender=Gender.MALE
    ),
    dietary_preferences=DietaryPreferences(
        restrictions=["high_protein"],
        allergies=["peanuts"],
        preferred_cuisines=["american", "mexican"],
        disliked_foods=["seafood"],
        cooking_skill_level=CookingSkillLevel.INTERMEDIATE
    ),
    health_goals=HealthGoals(
        goal_type=GoalType.MUSCLE_GAIN,
        target_calories=3200,
        macro_preferences=MacroPreferences(
            protein_percentage=25.0,
            carb_percentage=45.0,
            fat_percentage=30.0
        ),
        target_weight=85.0,
        weekly_weight_change_goal=0.3
    ),
    budget_constraints=BudgetConstraints(
        weekly_budget=150.0,  # High budget
        price_sensitivity=PriceSensitivity.LOW,
        bulk_buying_preference=True,
        preferred_stores=["whole_foods", "costco"]
    ),
    schedule_preferences=SchedulePreferences(
        meals_per_day=4,
        snacks_per_day=3,
        prep_time_limit=60,
        cooking_time_limit=45,
        meal_prep_days=["sunday", "wednesday"]
    )
)


# Profile 3: Senior with Multiple Restrictions - Health Maintenance
senior_multiple_restrictions = UserProfile(
    personal_info=PersonalInfo(
        age=68,
        weight=70.0,
        height=160.0,
        activity_level=ActivityLevel.LIGHTLY_ACTIVE,
        gender=Gender.FEMALE
    ),
    dietary_preferences=DietaryPreferences(
        restrictions=["diabetic_friendly", "heart_healthy", "low_sodium", "gluten_free"],
        allergies=["shellfish", "tree_nuts"],
        preferred_cuisines=["mediterranean", "american"],
        disliked_foods=["spicy_food", "raw_fish"],
        cooking_skill_level=CookingSkillLevel.ADVANCED
    ),
    health_goals=HealthGoals(
        goal_type=GoalType.GENERAL_HEALTH,
        target_calories=1800,
        macro_preferences=MacroPreferences(
            protein_percentage=20.0,
            carb_percentage=50.0,
            fat_percentage=30.0
        ),
        target_weight=68.0,
        weekly_weight_change_goal=-0.1
    ),
    budget_constraints=BudgetConstraints(
        weekly_budget=80.0,
        price_sensitivity=PriceSensitivity.MEDIUM,
        bulk_buying_preference=False,  # Prefers fresh ingredients
        preferred_stores=["kroger", "publix"]
    ),
    schedule_preferences=SchedulePreferences(
        meals_per_day=3,
        snacks_per_day=1,
        prep_time_limit=90,  # Has time to cook
        cooking_time_limit=60,
        meal_prep_days=["monday", "thursday"]
    )
)


# Profile 4: Vegan Student - Extremely Tight Budget
vegan_student_tight_budget = UserProfile(
    personal_info=PersonalInfo(
        age=20,
        weight=55.0,
        height=155.0,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        gender=Gender.OTHER
    ),
    dietary_preferences=DietaryPreferences(
        restrictions=["vegan", "nut_free"],  # Multiple restrictions
        allergies=["tree_nuts", "peanuts"],
        preferred_cuisines=["indian", "thai", "mexican"],
        disliked_foods=["fake_meat_products"],
        cooking_skill_level=CookingSkillLevel.BEGINNER
    ),
    health_goals=HealthGoals(
        goal_type=GoalType.MAINTENANCE,
        target_calories=2000,
        macro_preferences=MacroPreferences(
            protein_percentage=15.0,  # Lower protein due to vegan diet
            carb_percentage=60.0,
            fat_percentage=25.0
        ),
        target_weight=55.0,
        weekly_weight_change_goal=0.0
    ),
    budget_constraints=BudgetConstraints(
        weekly_budget=25.0,  # Extremely tight student budget
        price_sensitivity=PriceSensitivity.HIGH,
        bulk_buying_preference=True,
        preferred_stores=["aldi", "walmart", "ethnic_markets"]
    ),
    schedule_preferences=SchedulePreferences(
        meals_per_day=3,
        snacks_per_day=2,
        prep_time_limit=20,  # Very limited time
        cooking_time_limit=15,  # Quick student meals
        meal_prep_days=["sunday"]
    )
)


# Profile 5: Keto Enthusiast - Moderate Budget
keto_enthusiast = UserProfile(
    personal_info=PersonalInfo(
        age=35,
        weight=85.0,
        height=175.0,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        gender=Gender.MALE
    ),
    dietary_preferences=DietaryPreferences(
        restrictions=["keto", "dairy_free"],
        allergies=["milk"],
        preferred_cuisines=["american", "italian"],
        disliked_foods=["organ_meat", "sardines"],
        cooking_skill_level=CookingSkillLevel.INTERMEDIATE
    ),
    health_goals=HealthGoals(
        goal_type=GoalType.WEIGHT_LOSS,
        target_calories=2200,
        macro_preferences=MacroPreferences(
            protein_percentage=25.0,
            carb_percentage=45.0,  # Adjusted to meet validation
            fat_percentage=30.0    # Adjusted to meet validation
        ),
        target_weight=78.0,
        weekly_weight_change_goal=-0.4
    ),
    budget_constraints=BudgetConstraints(
        weekly_budget=100.0,
        price_sensitivity=PriceSensitivity.MEDIUM,
        bulk_buying_preference=True,
        preferred_stores=["costco", "kroger"]
    ),
    schedule_preferences=SchedulePreferences(
        meals_per_day=2,  # Intermittent fasting
        snacks_per_day=1,
        prep_time_limit=45,
        cooking_time_limit=30,
        meal_prep_days=["saturday", "tuesday"]
    )
)


# Profile 6: Family Parent - Balanced Approach
family_parent_balanced = UserProfile(
    personal_info=PersonalInfo(
        age=42,
        weight=68.0,
        height=168.0,
        activity_level=ActivityLevel.LIGHTLY_ACTIVE,
        gender=Gender.FEMALE
    ),
    dietary_preferences=DietaryPreferences(
        restrictions=["heart_healthy"],
        allergies=[],
        preferred_cuisines=["american", "italian", "mexican"],
        disliked_foods=["liver", "anchovies"],
        cooking_skill_level=CookingSkillLevel.ADVANCED
    ),
    health_goals=HealthGoals(
        goal_type=GoalType.MAINTENANCE,
        target_calories=2100,
        macro_preferences=MacroPreferences(
            protein_percentage=20.0,
            carb_percentage=50.0,
            fat_percentage=30.0
        ),
        target_weight=68.0,
        weekly_weight_change_goal=0.0
    ),
    budget_constraints=BudgetConstraints(
        weekly_budget=120.0,  # Family budget
        price_sensitivity=PriceSensitivity.MEDIUM,
        bulk_buying_preference=True,
        preferred_stores=["target", "kroger", "costco"]
    ),
    schedule_preferences=SchedulePreferences(
        meals_per_day=3,
        snacks_per_day=2,
        prep_time_limit=75,  # Has cooking experience
        cooking_time_limit=50,
        meal_prep_days=["sunday", "wednesday"]
    )
)


# Profile 7: Pescatarian Athlete - High Performance
pescatarian_athlete = UserProfile(
    personal_info=PersonalInfo(
        age=26,
        weight=62.0,
        height=170.0,
        activity_level=ActivityLevel.EXTREMELY_ACTIVE,
        gender=Gender.FEMALE
    ),
    dietary_preferences=DietaryPreferences(
        restrictions=["pescatarian", "high_protein"],
        allergies=["soy"],
        preferred_cuisines=["mediterranean", "japanese", "scandinavian"],
        disliked_foods=["processed_foods"],
        cooking_skill_level=CookingSkillLevel.INTERMEDIATE
    ),
    health_goals=HealthGoals(
        goal_type=GoalType.MUSCLE_GAIN,
        target_calories=2800,
        macro_preferences=MacroPreferences(
            protein_percentage=25.0,
            carb_percentage=45.0,
            fat_percentage=30.0
        ),
        target_weight=65.0,
        weekly_weight_change_goal=0.2
    ),
    budget_constraints=BudgetConstraints(
        weekly_budget=140.0,
        price_sensitivity=PriceSensitivity.LOW,
        bulk_buying_preference=False,  # Prefers fresh fish
        preferred_stores=["whole_foods", "fresh_market"]
    ),
    schedule_preferences=SchedulePreferences(
        meals_per_day=4,
        snacks_per_day=3,
        prep_time_limit=50,
        cooking_time_limit=35,
        meal_prep_days=["sunday", "thursday"]
    )
)


# Profile 8: Busy Executive - Convenience Focus
busy_executive = UserProfile(
    personal_info=PersonalInfo(
        age=45,
        weight=78.0,
        height=178.0,
        activity_level=ActivityLevel.SEDENTARY,
        gender=Gender.MALE
    ),
    dietary_preferences=DietaryPreferences(
        restrictions=["low_carb"],
        allergies=[],
        preferred_cuisines=["american", "asian"],
        disliked_foods=["brussels_sprouts", "beets"],
        cooking_skill_level=CookingSkillLevel.BEGINNER
    ),
    health_goals=HealthGoals(
        goal_type=GoalType.WEIGHT_LOSS,
        target_calories=2000,
        macro_preferences=MacroPreferences(
            protein_percentage=25.0,
            carb_percentage=45.0,
            fat_percentage=30.0
        ),
        target_weight=72.0,
        weekly_weight_change_goal=-0.3
    ),
    budget_constraints=BudgetConstraints(
        weekly_budget=200.0,  # High budget, values convenience
        price_sensitivity=PriceSensitivity.LOW,
        bulk_buying_preference=False,
        preferred_stores=["whole_foods", "fresh_direct"]
    ),
    schedule_preferences=SchedulePreferences(
        meals_per_day=3,
        snacks_per_day=1,
        prep_time_limit=15,  # Very limited time
        cooking_time_limit=10,  # Wants quick meals
        meal_prep_days=["sunday"]
    )
)


# Dictionary of all sample profiles for easy access
SAMPLE_PROFILES = {
    "young_professional_weight_loss": young_professional_weight_loss,
    "athletic_muscle_gain": athletic_muscle_gain,
    "senior_multiple_restrictions": senior_multiple_restrictions,
    "vegan_student_tight_budget": vegan_student_tight_budget,
    "keto_enthusiast": keto_enthusiast,
    "family_parent_balanced": family_parent_balanced,
    "pescatarian_athlete": pescatarian_athlete,
    "busy_executive": busy_executive
}


def get_profile_by_name(name: str) -> UserProfile:
    """Get a sample profile by name."""
    if name not in SAMPLE_PROFILES:
        raise ValueError(f"Profile '{name}' not found. Available profiles: {list(SAMPLE_PROFILES.keys())}")
    return SAMPLE_PROFILES[name]


def get_all_profiles() -> dict:
    """Get all sample profiles."""
    return SAMPLE_PROFILES.copy()


def validate_all_profiles() -> dict:
    """Validate all sample profiles and return results."""
    validation_results = {}
    for name, profile in SAMPLE_PROFILES.items():
        validation_results[name] = {
            "is_valid": profile.is_valid(),
            "errors": profile.get_all_errors()
        }
    return validation_results


def get_profile_summaries() -> dict:
    """Get brief summaries of all profiles for documentation."""
    summaries = {}
    for name, profile in SAMPLE_PROFILES.items():
        summaries[name] = {
            "description": _get_profile_description(name, profile),
            "key_features": _get_key_features(profile),
            "budget": f"${profile.budget_constraints.weekly_budget}/week",
            "goal": profile.health_goals.goal_type.value,
            "restrictions": profile.dietary_preferences.restrictions
        }
    return summaries


def _get_profile_description(name: str, profile: UserProfile) -> str:
    """Generate a description for a profile."""
    descriptions = {
        "young_professional_weight_loss": "28-year-old female professional seeking weight loss on a tight budget with vegetarian preferences",
        "athletic_muscle_gain": "24-year-old very active male focused on muscle gain with high protein needs and generous budget",
        "senior_multiple_restrictions": "68-year-old female with multiple health restrictions (diabetic, heart-healthy, gluten-free, low-sodium)",
        "vegan_student_tight_budget": "20-year-old vegan student with nut allergies on an extremely tight budget",
        "keto_enthusiast": "35-year-old male following ketogenic diet with dairy-free requirements",
        "family_parent_balanced": "42-year-old parent focused on heart-healthy family meals with moderate budget",
        "pescatarian_athlete": "26-year-old extremely active female pescatarian athlete with high performance needs",
        "busy_executive": "45-year-old sedentary male executive prioritizing convenience and quick meal preparation"
    }
    return descriptions.get(name, "Sample user profile for testing")


def _get_key_features(profile: UserProfile) -> list:
    """Extract key features of a profile."""
    features = []
    
    # Activity level
    features.append(f"Activity: {profile.personal_info.activity_level.value}")
    
    # Budget level
    if profile.budget_constraints.weekly_budget < 40:
        features.append("Tight budget")
    elif profile.budget_constraints.weekly_budget > 150:
        features.append("High budget")
    else:
        features.append("Moderate budget")
    
    # Time constraints
    if profile.schedule_preferences.prep_time_limit < 30:
        features.append("Time-constrained")
    
    # Multiple restrictions
    if len(profile.dietary_preferences.restrictions) > 2:
        features.append("Multiple dietary restrictions")
    
    # Allergies
    if profile.dietary_preferences.allergies:
        features.append("Food allergies")
    
    return features
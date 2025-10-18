"""
Validation script for sample user profiles.

This script validates all sample profiles and provides detailed reports
on their validity and characteristics.
"""

import sys
import os

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sample_data.user_profiles import validate_all_profiles, get_profile_summaries, SAMPLE_PROFILES


def main():
    """Main validation function."""
    print("=" * 60)
    print("SAMPLE USER PROFILES VALIDATION REPORT")
    print("=" * 60)
    
    # Validate all profiles
    validation_results = validate_all_profiles()
    
    # Count valid/invalid profiles
    valid_count = sum(1 for result in validation_results.values() if result["is_valid"])
    total_count = len(validation_results)
    
    print(f"\nValidation Summary: {valid_count}/{total_count} profiles are valid\n")
    
    # Detailed validation results
    for name, result in validation_results.items():
        status = "✓ VALID" if result["is_valid"] else "✗ INVALID"
        print(f"{name}: {status}")
        
        if result["errors"]:
            for error in result["errors"]:
                print(f"  - {error}")
        print()
    
    # Profile summaries
    print("=" * 60)
    print("PROFILE SUMMARIES")
    print("=" * 60)
    
    summaries = get_profile_summaries()
    for name, summary in summaries.items():
        print(f"\n{name.upper().replace('_', ' ')}")
        print("-" * len(name))
        print(f"Description: {summary['description']}")
        print(f"Budget: {summary['budget']}")
        print(f"Goal: {summary['goal']}")
        print(f"Restrictions: {', '.join(summary['restrictions']) if summary['restrictions'] else 'None'}")
        print(f"Key Features: {', '.join(summary['key_features'])}")
    
    # Coverage analysis
    print("\n" + "=" * 60)
    print("COVERAGE ANALYSIS")
    print("=" * 60)
    
    analyze_coverage()
    
    return valid_count == total_count


def analyze_coverage():
    """Analyze the coverage of different scenarios in sample profiles."""
    
    # Collect statistics
    age_ranges = {"young (18-30)": 0, "middle (31-50)": 0, "senior (51+)": 0}
    activity_levels = {}
    goals = {}
    restrictions = {}
    budget_ranges = {"tight (<$50)": 0, "moderate ($50-$150)": 0, "high (>$150)": 0}
    genders = {}
    skill_levels = {}
    
    for profile in SAMPLE_PROFILES.values():
        # Age ranges
        age = profile.personal_info.age
        if 18 <= age <= 30:
            age_ranges["young (18-30)"] += 1
        elif 31 <= age <= 50:
            age_ranges["middle (31-50)"] += 1
        else:
            age_ranges["senior (51+)"] += 1
        
        # Activity levels
        activity = profile.personal_info.activity_level.value
        activity_levels[activity] = activity_levels.get(activity, 0) + 1
        
        # Goals
        goal = profile.health_goals.goal_type.value
        goals[goal] = goals.get(goal, 0) + 1
        
        # Restrictions
        for restriction in profile.dietary_preferences.restrictions:
            restrictions[restriction] = restrictions.get(restriction, 0) + 1
        
        # Budget ranges
        budget = profile.budget_constraints.weekly_budget
        if budget < 50:
            budget_ranges["tight (<$50)"] += 1
        elif budget <= 150:
            budget_ranges["moderate ($50-$150)"] += 1
        else:
            budget_ranges["high (>$150)"] += 1
        
        # Genders
        gender = profile.personal_info.gender.value
        genders[gender] = genders.get(gender, 0) + 1
        
        # Skill levels
        skill = profile.dietary_preferences.cooking_skill_level.value
        skill_levels[skill] = skill_levels.get(skill, 0) + 1
    
    # Print coverage analysis
    print("\nAge Distribution:")
    for age_range, count in age_ranges.items():
        print(f"  {age_range}: {count}")
    
    print("\nActivity Levels:")
    for activity, count in activity_levels.items():
        print(f"  {activity}: {count}")
    
    print("\nHealth Goals:")
    for goal, count in goals.items():
        print(f"  {goal}: {count}")
    
    print("\nDietary Restrictions (top 5):")
    sorted_restrictions = sorted(restrictions.items(), key=lambda x: x[1], reverse=True)[:5]
    for restriction, count in sorted_restrictions:
        print(f"  {restriction}: {count}")
    
    print("\nBudget Distribution:")
    for budget_range, count in budget_ranges.items():
        print(f"  {budget_range}: {count}")
    
    print("\nGender Distribution:")
    for gender, count in genders.items():
        print(f"  {gender}: {count}")
    
    print("\nCooking Skill Levels:")
    for skill, count in skill_levels.items():
        print(f"  {skill}: {count}")
    
    # Edge cases covered
    print("\nEdge Cases Covered:")
    edge_cases = []
    
    for name, profile in SAMPLE_PROFILES.items():
        if profile.budget_constraints.weekly_budget < 30:
            edge_cases.append(f"Extremely tight budget: {name}")
        
        if len(profile.dietary_preferences.restrictions) >= 3:
            edge_cases.append(f"Multiple restrictions: {name}")
        
        if profile.dietary_preferences.allergies:
            edge_cases.append(f"Food allergies: {name}")
        
        if profile.schedule_preferences.prep_time_limit < 20:
            edge_cases.append(f"Very limited time: {name}")
        
        if profile.health_goals.macro_preferences.carb_percentage and profile.health_goals.macro_preferences.carb_percentage < 10:
            edge_cases.append(f"Extreme low-carb: {name}")
    
    for edge_case in edge_cases:
        print(f"  ✓ {edge_case}")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
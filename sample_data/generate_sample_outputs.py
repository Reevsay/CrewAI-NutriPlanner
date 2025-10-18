"""
Generate sample meal plan outputs using the sample user profiles.

This script runs the meal planning system with each sample profile
to create example outputs showcasing system capabilities.
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from loguru import logger
from config.settings import settings
from src.utils.gemini_config import configure_gemini
from sample_data.user_profiles import SAMPLE_PROFILES


def setup_logging():
    """Configure logging for sample generation"""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )


def generate_sample_meal_plan(profile_name: str, user_profile, output_dir: Path):
    """Generate a meal plan for a specific profile."""
    try:
        # Import interface components
        from src.interface import (
            MealPlanExecutionWorkflow,
            ComprehensiveReportGenerator
        )
        
        logger.info(f"Generating meal plan for: {profile_name}")
        
        # Initialize components
        execution_workflow = MealPlanExecutionWorkflow(verbose=False)
        report_generator = ComprehensiveReportGenerator()
        
        # Execute meal planning workflow
        execution_results = execution_workflow.execute_meal_planning(
            user_profile=user_profile,
            location=None
        )
        
        if execution_results.get('success'):
            meal_plan = execution_results['meal_plan']
            
            # Create profile-specific output directory
            profile_output_dir = output_dir / profile_name
            profile_output_dir.mkdir(exist_ok=True)
            
            # Generate comprehensive reports
            reports = report_generator.generate_complete_report(
                meal_plan=meal_plan,
                user_profile=user_profile,
                execution_results=execution_results,
                include_recipes=True,
                save_to_file=True,
                output_dir=str(profile_output_dir)
            )
            
            # Generate summary for documentation
            summary = report_generator.generate_summary_report(meal_plan, user_profile)
            
            # Save profile information
            profile_info = {
                "profile_name": profile_name,
                "generation_date": datetime.now().isoformat(),
                "user_profile_summary": {
                    "age": user_profile.personal_info.age,
                    "gender": user_profile.personal_info.gender.value,
                    "activity_level": user_profile.personal_info.activity_level.value,
                    "goal": user_profile.health_goals.goal_type.value,
                    "weekly_budget": user_profile.budget_constraints.weekly_budget,
                    "dietary_restrictions": user_profile.dietary_preferences.restrictions,
                    "allergies": user_profile.dietary_preferences.allergies,
                    "cooking_skill": user_profile.dietary_preferences.cooking_skill_level.value
                },
                "execution_summary": {
                    "success": execution_results.get('success', False),
                    "execution_time": execution_results.get('execution_time', 0),
                    "agents_used": execution_results.get('agents_used', [])
                },
                "meal_plan_summary": summary
            }
            
            # Save profile info as JSON
            with open(profile_output_dir / "profile_info.json", "w") as f:
                json.dump(profile_info, f, indent=2)
            
            logger.info(f"✓ Successfully generated meal plan for {profile_name}")
            return True, profile_output_dir
            
        else:
            error_msg = execution_results.get('message', 'Unknown error')
            logger.error(f"✗ Failed to generate meal plan for {profile_name}: {error_msg}")
            return False, None
            
    except Exception as e:
        logger.error(f"✗ Error generating meal plan for {profile_name}: {e}")
        return False, None


def create_sample_outputs_overview(output_dir: Path, results: dict):
    """Create an overview document of all generated sample outputs."""
    
    overview_content = f"""# Sample Meal Plan Outputs

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This directory contains sample meal plan outputs generated using diverse user profiles to demonstrate the Smart Recipe & Meal Planning System capabilities.

## Generated Profiles

"""
    
    successful_profiles = []
    failed_profiles = []
    
    for profile_name, (success, output_path) in results.items():
        if success:
            successful_profiles.append((profile_name, output_path))
        else:
            failed_profiles.append(profile_name)
    
    # Add successful profiles
    for profile_name, output_path in successful_profiles:
        # Load profile info
        try:
            with open(output_path / "profile_info.json", "r") as f:
                profile_info = json.load(f)
            
            user_summary = profile_info["user_profile_summary"]
            
            overview_content += f"""### {profile_name.replace('_', ' ').title()}

**Profile Details:**
- Age: {user_summary['age']} years old
- Gender: {user_summary['gender']}
- Activity Level: {user_summary['activity_level']}
- Health Goal: {user_summary['goal']}
- Weekly Budget: ${user_summary['weekly_budget']}
- Dietary Restrictions: {', '.join(user_summary['dietary_restrictions']) if user_summary['dietary_restrictions'] else 'None'}
- Food Allergies: {', '.join(user_summary['allergies']) if user_summary['allergies'] else 'None'}
- Cooking Skill: {user_summary['cooking_skill']}

**Generated Files:**
- `{profile_name}/meal_plan_report.md` - Complete meal plan with recipes
- `{profile_name}/shopping_list.md` - Organized shopping list
- `{profile_name}/nutritional_analysis.md` - Detailed nutritional breakdown
- `{profile_name}/profile_info.json` - Profile metadata and execution details

**Meal Plan Summary:**
{profile_info['meal_plan_summary']}

---

"""
        except Exception as e:
            logger.warning(f"Could not load profile info for {profile_name}: {e}")
    
    # Add failed profiles if any
    if failed_profiles:
        overview_content += f"""## Failed Generations

The following profiles failed to generate meal plans:
"""
        for profile_name in failed_profiles:
            overview_content += f"- {profile_name.replace('_', ' ').title()}\n"
        
        overview_content += "\nCheck the logs for error details.\n\n"
    
    # Add usage instructions
    overview_content += """## How to Use These Samples

1. **Review Profile Diversity**: Each profile represents different user scenarios, dietary needs, and constraints
2. **Examine Output Quality**: Check the generated meal plans for nutritional balance, budget compliance, and preference adherence
3. **Analyze System Capabilities**: See how the system handles various edge cases and restrictions
4. **Use for Testing**: These outputs can serve as reference examples for system validation

## File Structure

Each profile directory contains:
- **meal_plan_report.md**: Complete weekly meal plan with detailed recipes
- **shopping_list.md**: Organized shopping list with cost estimates
- **nutritional_analysis.md**: Nutritional breakdown and compliance analysis
- **profile_info.json**: Metadata about the profile and execution results

## System Performance

"""
    
    # Add performance summary
    total_profiles = len(results)
    successful_count = len(successful_profiles)
    success_rate = (successful_count / total_profiles) * 100 if total_profiles > 0 else 0
    
    overview_content += f"""- Total Profiles Processed: {total_profiles}
- Successful Generations: {successful_count}
- Success Rate: {success_rate:.1f}%

This demonstrates the system's reliability and ability to handle diverse user requirements.
"""
    
    # Save overview
    with open(output_dir / "README.md", "w") as f:
        f.write(overview_content)
    
    logger.info(f"Created sample outputs overview: {output_dir / 'README.md'}")


def main():
    """Main function to generate all sample outputs."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    logger.info("Starting sample meal plan output generation")
    
    # Validate configuration
    if not settings.google_api_key:
        logger.error("Google Gemini API key is required. Please set GOOGLE_API_KEY in your .env file.")
        sys.exit(1)
    
    # Configure Gemini API
    if not configure_gemini():
        logger.error("Failed to configure Gemini API. Please check your API key.")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path("sample_data/sample_outputs")
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Output directory: {output_dir}")
    
    # Generate meal plans for each profile
    results = {}
    
    # Select a subset of profiles for demonstration (to avoid long execution times)
    demo_profiles = [
        "young_professional_weight_loss",
        "vegan_student_tight_budget", 
        "senior_multiple_restrictions"
    ]
    
    logger.info(f"Generating meal plans for {len(demo_profiles)} demo profiles...")
    
    for profile_name in demo_profiles:
        if profile_name in SAMPLE_PROFILES:
            user_profile = SAMPLE_PROFILES[profile_name]
            success, output_path = generate_sample_meal_plan(profile_name, user_profile, output_dir)
            results[profile_name] = (success, output_path)
        else:
            logger.warning(f"Profile {profile_name} not found in SAMPLE_PROFILES")
    
    # Create overview documentation
    create_sample_outputs_overview(output_dir, results)
    
    # Summary
    successful_count = sum(1 for success, _ in results.values() if success)
    total_count = len(results)
    
    logger.info(f"Sample generation complete: {successful_count}/{total_count} profiles successful")
    
    if successful_count > 0:
        logger.info(f"Sample outputs saved to: {output_dir}")
        logger.info("Check the README.md file for a complete overview of generated samples")
    
    return successful_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
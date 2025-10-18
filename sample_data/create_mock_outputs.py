"""
Create mock sample meal plan outputs for demonstration purposes.

This script creates realistic example outputs that showcase the system's capabilities
without requiring actual API calls or long execution times.
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime, date, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sample_data.user_profiles import SAMPLE_PROFILES, get_profile_summaries


def create_mock_meal_plan_report(profile_name: str, user_profile, output_dir: Path):
    """Create a mock meal plan report for a profile."""
    
    # Profile-specific meal plan content
    meal_plans = {
        "young_professional_weight_loss": {
            "weekly_theme": "Quick & Healthy Vegetarian Meals",
            "daily_plans": [
                {
                    "day": "Monday",
                    "breakfast": {
                        "name": "Greek Yogurt Berry Bowl",
                        "calories": 280,
                        "prep_time": 5,
                        "ingredients": ["Greek yogurt (1 cup)", "Mixed berries (1/2 cup)", "Granola (2 tbsp)", "Honey (1 tsp)"],
                        "cost": 3.50
                    },
                    "lunch": {
                        "name": "Mediterranean Chickpea Salad",
                        "calories": 420,
                        "prep_time": 15,
                        "ingredients": ["Chickpeas (1 can)", "Cucumber (1 medium)", "Tomatoes (2 medium)", "Feta cheese (1/4 cup)", "Ol
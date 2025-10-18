"""
Enhanced output generation and formatting for the Smart Recipe & Meal Planning System.

This module provides comprehensive output generation including structured markdown reports,
organized shopping lists, nutritional summaries, and cost breakdowns with enhanced formatting.
"""

import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import date, datetime
from pathlib import Path
from loguru import logger

from src.models.user_profile import UserProfile
from src.models.recipe import WeeklyMealPlan, Recipe, ShoppingList, NutritionalInfo
from src.models.formatters import MarkdownReportGenerator, JSONSerializer


class EnhancedShoppingListFormatter:
    """Enhanced shopping list formatter with organization and optimization features."""
    
    CATEGORY_ORDER = [
        "Produce", "Meat & Seafood", "Dairy & Eggs", "Pantry & Dry Goods",
        "Frozen Foods", "Bakery", "Beverages", "Condiments & Sauces",
        "Spices & Seasonings", "Other"
    ]
    
    STORE_SECTIONS = {
        "Produce": ["fruits", "vegetables", "herbs", "fresh"],
        "Meat & Seafood": ["chicken", "beef", "pork", "fish", "seafood", "turkey"],
        "Dairy & Eggs": ["milk", "cheese", "yogurt", "eggs", "butter", "cream"],
        "Pantry & Dry Goods": ["rice", "pasta", "beans", "lentils", "flour", "sugar", "oil"],
        "Frozen Foods": ["frozen"],
        "Bakery": ["bread", "rolls", "bagels"],
        "Beverages": ["juice", "soda", "water", "tea", "coffee"],
        "Condiments & Sauces": ["sauce", "dressing", "vinegar", "mustard", "ketchup"],
        "Spices & Seasonings": ["spice", "herb", "seasoning", "salt", "pepper"],
        "Other": []
    }
    
    @staticmethod
    def format_organized_shopping_list(shopping_list: ShoppingList, include_alternatives: bool = True) -> str:
        """Format shopping list organized by store sections with optimization tips."""
        lines = [
            "# 🛒 Organized Shopping List",
            "",
            f"**Estimated Total Cost:** ${shopping_list.total_estimated_cost:.2f}",
            f"**Total Items:** {len(shopping_list.items)}",
            "",
            "## Shopping Tips",
            "- Check store flyers for sales on these items",
            "- Consider buying in bulk for non-perishables to save money",
            "- Shop produce section first, then refrigerated items last",
            "- Bring reusable bags to reduce waste",
            "",
        ]
        
        # Group items by category in store order
        grouped_items = shopping_list.group_by_category()
        
        for category in EnhancedShoppingListFormatter.CATEGORY_ORDER:
            if category in grouped_items and grouped_items[category]:
                items = grouped_items[category]
                
                # Calculate category total
                category_total = sum(item.estimated_cost for item in items)
                
                lines.extend([
                    f"## {category} (${category_total:.2f})",
                    "",
                ])
                
                # Sort items by name for easier shopping
                sorted_items = sorted(items, key=lambda x: x.ingredient_name)
                
                for item in sorted_items:
                    unit_display = item.unit.value
                    cost_display = f" - ${item.estimated_cost:.2f}" if item.estimated_cost > 0 else ""
                    
                    # Add quantity consolidation note if needed
                    quantity_note = ""
                    if item.total_quantity > 10:
                        quantity_note = " *(consider bulk purchase)*"
                    elif item.total_quantity < 1:
                        quantity_note = " *(small amount - check if you have some)*"
                    
                    lines.append(f"- [ ] {item.total_quantity:.1f} {unit_display} **{item.ingredient_name}**{cost_display}{quantity_note}")
                    
                    # Add alternatives if requested and available
                    if include_alternatives and item.alternatives:
                        alternatives_text = ", ".join(item.alternatives[:3])  # Limit to 3 alternatives
                        lines.append(f"      *Alternatives: {alternatives_text}*")
                
                lines.append("")
        
        # Add budget optimization suggestions
        lines.extend([
            "## 💡 Budget Optimization Tips",
            "",
        ])
        
        # Analyze shopping list for optimization opportunities
        optimization_tips = EnhancedShoppingListFormatter._generate_optimization_tips(shopping_list)
        for tip in optimization_tips:
            lines.append(f"- {tip}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _generate_optimization_tips(shopping_list: ShoppingList) -> List[str]:
        """Generate budget optimization tips based on shopping list analysis."""
        tips = []
        
        # Analyze expensive items
        expensive_items = [item for item in shopping_list.items if item.estimated_cost > 10]
        if expensive_items:
            tips.append(f"Consider generic brands for expensive items: {', '.join([item.ingredient_name for item in expensive_items[:3]])}")
        
        # Analyze produce items
        produce_items = [item for item in shopping_list.items if any(keyword in item.ingredient_name.lower() for keyword in ["fruit", "vegetable", "herb"])]
        if produce_items:
            tips.append("Buy seasonal produce for better prices and freshness")
        
        # Analyze bulk opportunities
        bulk_items = [item for item in shopping_list.items if item.total_quantity > 5]
        if bulk_items:
            tips.append(f"Consider bulk buying for: {', '.join([item.ingredient_name for item in bulk_items[:3]])}")
        
        # General tips
        tips.extend([
            "Check store loyalty programs for additional discounts",
            "Compare unit prices rather than package prices",
            "Shop with a full stomach to avoid impulse purchases"
        ])
        
        return tips


class NutritionalSummaryFormatter:
    """Enhanced nutritional summary formatter with detailed analysis."""
    
    @staticmethod
    def format_detailed_nutritional_summary(
        meal_plan: WeeklyMealPlan,
        user_profile: Optional[UserProfile] = None
    ) -> str:
        """Format detailed nutritional summary with analysis and recommendations."""
        lines = [
            "# 📊 Detailed Nutritional Analysis",
            "",
        ]
        
        if not meal_plan.nutritional_summary:
            lines.extend([
                "⚠️ Nutritional summary not available.",
                ""
            ])
            return "\n".join(lines)
        
        summary = meal_plan.nutritional_summary
        
        # Daily averages with targets
        lines.extend([
            "## Daily Nutritional Averages",
            "",
        ])
        
        # Add target comparison if user profile available
        if user_profile:
            targets = NutritionalSummaryFormatter._calculate_nutritional_targets(user_profile)
            lines.extend(NutritionalSummaryFormatter._format_nutrition_with_targets(summary.daily_averages, targets))
        else:
            lines.extend([
                MarkdownReportGenerator.format_nutritional_info(summary.daily_averages, ""),
                ""
            ])
        
        # Weekly consistency analysis
        if summary.daily_variations:
            lines.extend([
                "## Nutritional Consistency Analysis",
                "",
                "*Consistency scores help ensure balanced daily intake*",
                "",
            ])
            
            consistency_analysis = NutritionalSummaryFormatter._analyze_consistency(summary.daily_variations)
            for nutrient, analysis in consistency_analysis.items():
                status_emoji = "✅" if analysis["status"] == "excellent" else "⚠️" if analysis["status"] == "good" else "❌"
                lines.append(f"{status_emoji} **{nutrient.title()}:** {analysis['description']}")
            
            lines.append("")
        
        # Nutritional highlights and concerns
        highlights, concerns = NutritionalSummaryFormatter._analyze_nutritional_quality(
            summary.daily_averages, user_profile
        )
        
        if highlights:
            lines.extend([
                "## ✨ Nutritional Highlights",
                "",
            ])
            for highlight in highlights:
                lines.append(f"- {highlight}")
            lines.append("")
        
        if concerns:
            lines.extend([
                "## ⚠️ Areas for Improvement",
                "",
            ])
            for concern in concerns:
                lines.append(f"- {concern}")
            lines.append("")
        
        # Weekly totals
        lines.extend([
            "## Weekly Totals",
            "",
            MarkdownReportGenerator.format_nutritional_info(summary.weekly_totals, ""),
            ""
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def _calculate_nutritional_targets(user_profile: UserProfile) -> Dict[str, float]:
        """Calculate nutritional targets based on user profile."""
        # Basic BMR calculation (Mifflin-St Jeor Equation)
        personal_info = user_profile.personal_info
        
        if personal_info.gender.value == "male":
            bmr = 88.362 + (13.397 * personal_info.weight) + (4.799 * personal_info.height) - (5.677 * personal_info.age)
        else:
            bmr = 447.593 + (9.247 * personal_info.weight) + (3.098 * personal_info.height) - (4.330 * personal_info.age)
        
        # Activity multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "lightly_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725,
            "extremely_active": 1.9
        }
        
        tdee = bmr * activity_multipliers.get(personal_info.activity_level.value, 1.55)
        
        # Adjust for health goals
        if user_profile.health_goals.goal_type.value == "weight_loss":
            target_calories = tdee - 500  # 1 lb per week loss
        elif user_profile.health_goals.goal_type.value == "muscle_gain":
            target_calories = tdee + 300  # Moderate surplus
        else:
            target_calories = tdee
        
        # Use user's target calories if specified
        if user_profile.health_goals.target_calories:
            target_calories = user_profile.health_goals.target_calories
        
        # Calculate macro targets
        macro_prefs = user_profile.health_goals.macro_preferences
        
        protein_pct = macro_prefs.protein_percentage or 25
        carb_pct = macro_prefs.carb_percentage or 50
        fat_pct = macro_prefs.fat_percentage or 25
        
        return {
            "calories": target_calories,
            "protein": (target_calories * protein_pct / 100) / 4,  # 4 cal/g
            "carbohydrates": (target_calories * carb_pct / 100) / 4,  # 4 cal/g
            "fat": (target_calories * fat_pct / 100) / 9,  # 9 cal/g
            "fiber": 25,  # General recommendation
            "sodium": 2300  # General recommendation (mg)
        }
    
    @staticmethod
    def _format_nutrition_with_targets(actual: NutritionalInfo, targets: Dict[str, float]) -> List[str]:
        """Format nutrition info with target comparisons."""
        lines = []
        
        nutrients = [
            ("calories", "Calories", "kcal"),
            ("protein", "Protein", "g"),
            ("carbohydrates", "Carbohydrates", "g"),
            ("fat", "Fat", "g"),
            ("fiber", "Fiber", "g"),
            ("sodium", "Sodium", "mg")
        ]
        
        for nutrient_key, nutrient_name, unit in nutrients:
            actual_value = getattr(actual, nutrient_key, 0)
            target_value = targets.get(nutrient_key, 0)
            
            if target_value > 0:
                percentage = (actual_value / target_value) * 100
                status_emoji = "✅" if 90 <= percentage <= 110 else "⚠️" if 80 <= percentage <= 120 else "❌"
                
                lines.append(f"- **{nutrient_name}:** {actual_value:.1f}{unit} / {target_value:.1f}{unit} ({percentage:.0f}%) {status_emoji}")
            else:
                lines.append(f"- **{nutrient_name}:** {actual_value:.1f}{unit}")
        
        return lines
    
    @staticmethod
    def _analyze_consistency(variations: Dict[str, float]) -> Dict[str, Dict[str, str]]:
        """Analyze nutritional consistency and provide feedback."""
        analysis = {}
        
        for nutrient, variation in variations.items():
            if variation < 0.1:
                status = "excellent"
                description = f"Very consistent daily intake (variation: {variation:.1%})"
            elif variation < 0.2:
                status = "good"
                description = f"Good consistency with minor daily variations ({variation:.1%})"
            else:
                status = "needs_improvement"
                description = f"High daily variation ({variation:.1%}) - consider more consistent portions"
            
            analysis[nutrient] = {
                "status": status,
                "description": description,
                "variation": variation
            }
        
        return analysis
    
    @staticmethod
    def _analyze_nutritional_quality(
        nutrition: NutritionalInfo,
        user_profile: Optional[UserProfile] = None
    ) -> Tuple[List[str], List[str]]:
        """Analyze nutritional quality and generate highlights and concerns."""
        highlights = []
        concerns = []
        
        # Analyze protein intake
        if nutrition.protein >= 1.2 * (user_profile.personal_info.weight if user_profile else 70):
            highlights.append("Excellent protein intake for muscle maintenance and satiety")
        elif nutrition.protein < 0.8 * (user_profile.personal_info.weight if user_profile else 70):
            concerns.append("Protein intake may be below recommended levels")
        
        # Analyze fiber intake
        if nutrition.fiber >= 25:
            highlights.append("Great fiber intake supporting digestive health")
        elif nutrition.fiber < 15:
            concerns.append("Low fiber intake - consider adding more fruits, vegetables, and whole grains")
        
        # Analyze sodium intake
        if nutrition.sodium <= 2300:
            highlights.append("Sodium intake within healthy guidelines")
        elif nutrition.sodium > 3000:
            concerns.append("High sodium intake - consider reducing processed foods")
        
        # Analyze sugar intake
        if nutrition.sugar <= 50:
            highlights.append("Moderate sugar intake supporting stable energy levels")
        elif nutrition.sugar > 100:
            concerns.append("High sugar intake - consider reducing added sugars")
        
        return highlights, concerns


class CostBreakdownFormatter:
    """Enhanced cost breakdown formatter with detailed analysis."""
    
    @staticmethod
    def format_detailed_cost_breakdown(
        meal_plan: WeeklyMealPlan,
        user_profile: Optional[UserProfile] = None
    ) -> str:
        """Format detailed cost breakdown with budget analysis."""
        lines = [
            "# 💰 Detailed Cost Breakdown",
            "",
        ]
        
        total_cost = meal_plan.get_total_cost()
        
        # Weekly overview
        lines.extend([
            "## Weekly Cost Overview",
            "",
            f"**Total Weekly Cost:** ${total_cost:.2f}",
            f"**Average Cost per Day:** ${total_cost / 7:.2f}",
            f"**Average Cost per Meal:** ${total_cost / (len(meal_plan.daily_plans) * 3):.2f}",
            "",
        ])
        
        # Budget comparison if available
        if user_profile:
            budget = user_profile.budget_constraints.weekly_budget
            budget_percentage = (total_cost / budget) * 100
            
            budget_status = "✅ Under Budget" if budget_percentage <= 100 else "⚠️ Over Budget"
            savings = budget - total_cost
            
            lines.extend([
                "## Budget Analysis",
                "",
                f"**Weekly Budget:** ${budget:.2f}",
                f"**Budget Used:** {budget_percentage:.1f}% {budget_status}",
                f"**Remaining/Overage:** ${savings:.2f}",
                "",
            ])
        
        # Daily cost breakdown
        lines.extend([
            "## Daily Cost Breakdown",
            "",
        ])
        
        for daily_plan in meal_plan.daily_plans:
            day_name = daily_plan.date.strftime("%A")
            daily_cost = daily_plan.get_daily_cost()
            
            lines.append(f"**{day_name}:** ${daily_cost:.2f}")
            
            # Meal-by-meal breakdown
            meals = [
                ("Breakfast", daily_plan.breakfast),
                ("Lunch", daily_plan.lunch),
                ("Dinner", daily_plan.dinner)
            ]
            
            for meal_name, recipe in meals:
                if recipe:
                    cost = recipe.get_cost_per_serving()
                    lines.append(f"  - {meal_name}: ${cost:.2f}")
            
            # Snacks
            if daily_plan.snacks:
                snack_cost = sum(snack.get_cost_per_serving() for snack in daily_plan.snacks)
                lines.append(f"  - Snacks: ${snack_cost:.2f}")
        
        lines.append("")
        
        # Cost optimization suggestions
        optimization_suggestions = CostBreakdownFormatter._generate_cost_optimization_suggestions(
            meal_plan, user_profile
        )
        
        if optimization_suggestions:
            lines.extend([
                "## 💡 Cost Optimization Suggestions",
                "",
            ])
            
            for suggestion in optimization_suggestions:
                lines.append(f"- {suggestion}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _generate_cost_optimization_suggestions(
        meal_plan: WeeklyMealPlan,
        user_profile: Optional[UserProfile] = None
    ) -> List[str]:
        """Generate cost optimization suggestions based on meal plan analysis."""
        suggestions = []
        
        # Analyze expensive recipes
        all_recipes = meal_plan.get_all_recipes()
        if all_recipes:
            avg_cost = sum(recipe.get_cost_per_serving() for recipe in all_recipes) / len(all_recipes)
            expensive_recipes = [recipe for recipe in all_recipes if recipe.get_cost_per_serving() > avg_cost * 1.5]
            
            if expensive_recipes:
                suggestions.append(f"Consider substituting expensive recipes: {', '.join([recipe.name for recipe in expensive_recipes[:2]])}")
        
        # Analyze ingredient usage
        if meal_plan.shopping_list:
            expensive_ingredients = [item for item in meal_plan.shopping_list.items if item.estimated_cost > 8]
            if expensive_ingredients:
                suggestions.append(f"Look for sales or alternatives for: {', '.join([item.ingredient_name for item in expensive_ingredients[:3]])}")
        
        # Budget-specific suggestions
        if user_profile and user_profile.budget_constraints.price_sensitivity.value == "high":
            suggestions.extend([
                "Focus on seasonal produce for better prices",
                "Consider batch cooking and freezing portions",
                "Use dried beans and lentils instead of canned for savings"
            ])
        
        # General suggestions
        suggestions.extend([
            "Plan meals around store sales and seasonal ingredients",
            "Buy generic brands for basic ingredients",
            "Consider meal prep to reduce food waste"
        ])
        
        return suggestions[:5]  # Limit to top 5 suggestions


class ComprehensiveReportGenerator:
    """Main class for generating comprehensive meal plan reports."""
    
    def __init__(self, output_directory: str = "output_examples"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
    def generate_complete_report(
        self,
        meal_plan: WeeklyMealPlan,
        user_profile: Optional[UserProfile] = None,
        execution_results: Optional[Dict[str, Any]] = None,
        include_recipes: bool = True,
        save_to_file: bool = True
    ) -> Dict[str, str]:
        """
        Generate a complete meal plan report with all components.
        
        Args:
            meal_plan: The weekly meal plan to format
            user_profile: User profile information
            execution_results: Results from the meal planning execution
            include_recipes: Whether to include full recipe details
            save_to_file: Whether to save reports to files
            
        Returns:
            Dictionary containing all report sections
        """
        logger.info("Generating comprehensive meal plan report")
        
        # Generate timestamp for file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        week_start = meal_plan.week_start_date.strftime("%Y%m%d")
        
        # Generate all report sections
        reports = {
            "main_report": MarkdownReportGenerator.generate_complete_meal_plan_report(
                meal_plan, user_profile, include_recipes
            ),
            "shopping_list": EnhancedShoppingListFormatter.format_organized_shopping_list(
                meal_plan.shopping_list
            ) if meal_plan.shopping_list else "No shopping list available.",
            "nutritional_analysis": NutritionalSummaryFormatter.format_detailed_nutritional_summary(
                meal_plan, user_profile
            ),
            "cost_breakdown": CostBreakdownFormatter.format_detailed_cost_breakdown(
                meal_plan, user_profile
            )
        }
        
        # Add execution summary if available
        if execution_results:
            reports["execution_summary"] = self._format_execution_summary(execution_results)
        
        # Save to files if requested
        if save_to_file:
            file_paths = self._save_reports_to_files(reports, week_start, timestamp)
            reports["file_paths"] = file_paths
            logger.info(f"Reports saved to {len(file_paths)} files")
        
        return reports
    
    def _format_execution_summary(self, execution_results: Dict[str, Any]) -> str:
        """Format execution summary as markdown."""
        lines = [
            "# 🔧 Execution Summary",
            "",
            f"**Generated on:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
        ]
        
        # Execution timing
        if "execution_summary" in execution_results:
            summary = execution_results["execution_summary"]
            total_time = summary.get("total_execution_time", 0)
            
            lines.extend([
                "## Execution Performance",
                "",
                f"**Total Execution Time:** {total_time:.1f} seconds",
                f"**Phases Completed:** {summary.get('completed_phases', 0)}/{summary.get('total_phases', 5)}",
                "",
            ])
            
            # Phase timing breakdown
            if "phase_times" in summary:
                lines.extend([
                    "### Phase Timing Breakdown",
                    "",
                ])
                
                for phase, duration in summary["phase_times"].items():
                    lines.append(f"- **{phase.replace('_', ' ').title()}:** {duration:.1f}s")
                
                lines.append("")
        
        # Error summary if available
        if "error_summary" in execution_results:
            error_summary = execution_results["error_summary"]
            if error_summary.get("total_errors", 0) > 0:
                lines.extend([
                    "## Issues Encountered",
                    "",
                    f"**Total Issues:** {error_summary.get('total_errors', 0)}",
                    f"**Warnings:** {error_summary.get('warnings', 0)}",
                    f"**Errors:** {error_summary.get('errors', 0)}",
                    "",
                ])
        
        # Optimization report if available
        if "optimization_report" in execution_results:
            opt_report = execution_results["optimization_report"]
            performance = opt_report.get("overall_performance", "unknown")
            
            lines.extend([
                "## Performance Analysis",
                "",
                f"**Overall Performance:** {performance.title()}",
                "",
            ])
            
            if opt_report.get("optimization_suggestions"):
                lines.extend([
                    "### Optimization Suggestions",
                    "",
                ])
                
                for suggestion in opt_report["optimization_suggestions"][:3]:
                    lines.append(f"- {suggestion}")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def _cleanup_old_reports(self):
        """Delete all existing meal plan reports to save space."""
        try:
            if self.output_directory.exists():
                for file_path in self.output_directory.glob("*.md"):
                    file_path.unlink()
                    logger.debug(f"Deleted old report: {file_path}")
                logger.info("Cleaned up old meal plan reports")
        except Exception as e:
            logger.warning(f"Failed to cleanup old reports: {e}")
    
    def _save_reports_to_files(
        self,
        reports: Dict[str, str],
        week_start: str,
        timestamp: str
    ) -> Dict[str, str]:
        """Save all reports to individual files."""
        # Clean up old reports first
        self._cleanup_old_reports()
        
        file_paths = {}
        
        file_mappings = {
            "main_report": f"meal_plan_{week_start}_{timestamp}.md",
            "shopping_list": f"shopping_list_{week_start}_{timestamp}.md",
            "nutritional_analysis": f"nutrition_analysis_{week_start}_{timestamp}.md",
            "cost_breakdown": f"cost_breakdown_{week_start}_{timestamp}.md",
            "execution_summary": f"execution_summary_{week_start}_{timestamp}.md"
        }
        
        for report_type, content in reports.items():
            if report_type in file_mappings:
                file_path = self.output_directory / file_mappings[report_type]
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    file_paths[report_type] = str(file_path)
                    logger.debug(f"Saved {report_type} to {file_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to save {report_type}: {e}")
        
        return file_paths
    
    def generate_summary_report(
        self,
        meal_plan: WeeklyMealPlan,
        user_profile: Optional[UserProfile] = None
    ) -> str:
        """Generate a concise summary report for quick review."""
        week_start = meal_plan.week_start_date.strftime("%B %d, %Y")
        total_cost = meal_plan.get_total_cost()
        
        lines = [
            "# 📋 Meal Plan Summary",
            "",
            f"**Week of:** {week_start}",
            f"**Total Cost:** ${total_cost:.2f}",
            f"**Recipes:** {len(meal_plan.get_all_recipes())} unique recipes",
            "",
        ]
        
        # Quick nutritional overview
        if meal_plan.nutritional_summary:
            daily_avg = meal_plan.nutritional_summary.daily_averages
            lines.extend([
                "## Daily Nutritional Averages",
                "",
                f"- **Calories:** {daily_avg.calories:.0f} kcal",
                f"- **Protein:** {daily_avg.protein:.0f}g",
                f"- **Carbs:** {daily_avg.carbohydrates:.0f}g",
                f"- **Fat:** {daily_avg.fat:.0f}g",
                "",
            ])
        
        # Budget status
        if user_profile:
            budget = user_profile.budget_constraints.weekly_budget
            budget_status = "✅ Under Budget" if total_cost <= budget else "⚠️ Over Budget"
            lines.extend([
                f"**Budget Status:** {budget_status} (${total_cost:.2f} / ${budget:.2f})",
                ""
            ])
        
        return "\n".join(lines)
"""
Main entry point for the Smart Recipe & Meal Planning System
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from loguru import logger
from config.settings import settings
from src.utils.gemini_config import configure_gemini


def setup_logging():
    """Configure logging for the application"""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file logging
    logger.add(
        "logs/meal_planner.log",
        rotation="10 MB",
        retention="7 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )


def main():
    """Main application entry point"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    logger.info("Starting Smart Recipe & Meal Planning System")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    try:
        # Validate required configuration
        if not settings.google_api_key:
            logger.error("Google Gemini API key is required. Please set GOOGLE_API_KEY in your .env file.")
            logger.info("Get your free API key from: https://makersuite.google.com/app/apikey")
            sys.exit(1)
        
        # Configure Gemini API
        logger.info("Configuring Google Gemini API...")
        if not configure_gemini():
            logger.error("Failed to configure Gemini API. Please check your API key.")
            sys.exit(1)
        
        logger.info("Configuration validated successfully")
        logger.info("System ready for meal planning operations")
        
        # Import interface components
        from src.interface.simple_input import SimpleUserInput
        from src.interface import (
            MealPlanExecutionWorkflow,
            ComprehensiveReportGenerator
        )
        
        # Initialize components
        input_processor = SimpleUserInput()
        execution_workflow = MealPlanExecutionWorkflow(verbose=True)
        report_generator = ComprehensiveReportGenerator()
        
        # Collect user profile
        logger.info("Starting user profile collection")
        user_profile = input_processor.collect_user_profile()
        
        # Show execution time estimate
        time_estimate = execution_workflow.estimate_execution_time(user_profile)
        print(f"\n⏱️  Estimated execution time: {time_estimate['estimated_minutes']:.1f} minutes")
        print(f"Complexity level: {time_estimate['complexity_level']}")
        
        # Confirm execution
        proceed = input("\nProceed with meal plan generation? (y/n): ").strip().lower()
        if proceed not in ['y', 'yes']:
            print("Meal plan generation cancelled. Goodbye!")
            return
        
        # Execute meal planning workflow
        logger.info("Starting meal plan execution")
        execution_results = execution_workflow.execute_meal_planning(
            user_profile=user_profile,
            location=None  # Could be enhanced to ask for location
        )
        
        if execution_results.get('success'):
            meal_plan = execution_results['meal_plan']
            
            # Generate comprehensive reports
            print("\n📄 Generating detailed reports...")
            reports = report_generator.generate_complete_report(
                meal_plan=meal_plan,
                user_profile=user_profile,
                execution_results=execution_results,
                include_recipes=True,
                save_to_file=True
            )
            
            # Display summary
            print("\n" + "="*60)
            print("🎉 MEAL PLAN GENERATION COMPLETE!")
            print("="*60)
            
            if "file_paths" in reports:
                print("\n📁 Reports saved to:")
                for report_type, file_path in reports["file_paths"].items():
                    print(f"  • {report_type.replace('_', ' ').title()}: {file_path}")
            
            # Show quick summary
            summary = report_generator.generate_summary_report(meal_plan, user_profile)
            print(f"\n{summary}")
            
            print("\n✨ Your personalized meal plan is ready!")
            print("Check the generated files for detailed recipes, shopping lists, and nutritional analysis.")
            
        else:
            print(f"\n❌ Meal plan generation failed: {execution_results.get('message', 'Unknown error')}")
            logger.error(f"Execution failed: {execution_results}")
        
    except KeyboardInterrupt:
        print("\n\nMeal plan generation cancelled. Goodbye!")
        logger.info("Application cancelled by user")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"\n❌ Application error: {e}")
        print("Please check the logs for more details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Validation script to verify project setup is complete
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def validate_project_structure():
    """Validate that all required directories and files exist"""
    print("🔍 Validating project structure...")
    
    required_dirs = [
        "src", "src/agents", "src/tools", "src/models", "src/utils",
        "config", "tests", "logs"
    ]
    
    required_files = [
        "requirements.txt", ".env.example", ".gitignore", "README.md",
        "setup.py", "pyproject.toml", "src/main.py", "config/settings.py"
    ]
    
    # Check directories
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
        print(f"✅ Directory exists: {dir_path}")
    
    # Check files
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ Missing file: {file_path}")
            return False
        print(f"✅ File exists: {file_path}")
    
    return True


def validate_imports():
    """Validate that key modules can be imported"""
    print("\n🔍 Validating imports...")
    
    try:
        from config.settings import settings
        print("✅ Settings module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import settings: {e}")
        return False
    
    try:
        from src.main import main
        print("✅ Main module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import main: {e}")
        return False
    
    return True


def validate_dependencies():
    """Validate that key dependencies are installed"""
    print("\n🔍 Validating dependencies...")
    
    required_packages = [
        "crewai", "pydantic", "pydantic_settings",
        "dotenv", "loguru", "requests", "pandas", "numpy"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ Package installed: {package}")
        except ImportError:
            print(f"❌ Missing package: {package}")
            return False
    
    # Check Google Generative AI separately
    try:
        import google.generativeai
        print("✅ Package installed: google.generativeai")
    except ImportError:
        print("❌ Missing package: google.generativeai")
        return False
    
    # Check CrewAI tools (optional - may have compatibility issues)
    try:
        import crewai_tools
        print("✅ Package installed: crewai_tools")
    except ImportError:
        print("⚠️  CrewAI tools not available (optional - may have compatibility issues)")
        # Don't fail validation for this
    
    return True


def main():
    """Run all validation checks"""
    print("🚀 Smart Recipe & Meal Planning System - Setup Validation")
    print("=" * 60)
    
    checks = [
        ("Project Structure", validate_project_structure),
        ("Module Imports", validate_imports),
        ("Dependencies", validate_dependencies)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
            print(f"\n❌ {check_name} validation failed!")
        else:
            print(f"\n✅ {check_name} validation passed!")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All validation checks passed! Project setup is complete.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your Google Gemini API key")
        print("   Get your free API key from: https://makersuite.google.com/app/apikey")
        print("2. Run: python -m src.main")
        print("3. Start implementing the agents (Task 2)")
    else:
        print("❌ Some validation checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
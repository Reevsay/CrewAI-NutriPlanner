#!/usr/bin/env python3
"""
Comprehensive test runner for the Smart Recipe & Meal Planning System.

This script runs all test suites and provides a summary of test coverage
and results across unit tests, integration tests, and end-to-end workflows.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_test_suite(test_file, description):
    """Run a specific test suite and return results."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Duration: {duration:.2f} seconds")
        
        if result.returncode == 0:
            print(f"✅ {description} - ALL TESTS PASSED")
            # Count passed tests
            passed_count = result.stdout.count(" PASSED")
            print(f"   {passed_count} tests passed")
        else:
            print(f"❌ {description} - SOME TESTS FAILED")
            # Count passed and failed tests
            passed_count = result.stdout.count(" PASSED")
            failed_count = result.stdout.count(" FAILED")
            print(f"   {passed_count} tests passed, {failed_count} tests failed")
            
        return result.returncode == 0, passed_count, result.stdout, result.stderr
        
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False, 0, "", str(e)


def main():
    """Run comprehensive test suite."""
    print("🧪 Smart Recipe & Meal Planning System - Comprehensive Test Suite")
    print("=" * 80)
    
    test_suites = [
        ("tests/test_user_profile_models.py", "Unit Tests - User Profile Models"),
        ("tests/test_recipe_models.py", "Unit Tests - Recipe Models"),
        ("tests/test_formatters.py", "Unit Tests - Formatters"),
        ("tests/test_nutrition_api_integration.py", "Integration Tests - Nutrition API"),
        ("tests/test_grocery_price_api_integration.py", "Integration Tests - Grocery Price API"),
        ("tests/test_calculation_tools_integration.py", "Integration Tests - Calculation Tools"),
        ("tests/test_end_to_end_workflows.py", "End-to-End Workflow Tests"),
    ]
    
    total_passed = 0
    total_suites = len(test_suites)
    passed_suites = 0
    
    results = []
    
    for test_file, description in test_suites:
        success, passed_count, stdout, stderr = run_test_suite(test_file, description)
        
        results.append({
            'description': description,
            'success': success,
            'passed_count': passed_count,
            'stdout': stdout,
            'stderr': stderr
        })
        
        if success:
            passed_suites += 1
        
        total_passed += passed_count
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    print(f"Test Suites: {passed_suites}/{total_suites} passed")
    print(f"Total Tests: {total_passed} passed")
    
    if passed_suites == total_suites:
        print("\n🎉 ALL TEST SUITES PASSED! 🎉")
        print("\nThe Smart Recipe & Meal Planning System has comprehensive test coverage:")
        print("✅ Unit Tests - Data model validation and core functionality")
        print("✅ Integration Tests - External API integration and error handling")
        print("✅ End-to-End Tests - Complete workflow validation")
        
        print("\nTest Coverage Areas:")
        print("• User profile validation and cross-validation")
        print("• Recipe and meal plan data models")
        print("• Nutritional calculations and balance analysis")
        print("• Cost calculations and budget optimization")
        print("• External API integration (Nutrition & Grocery Price APIs)")
        print("• Caching and error handling mechanisms")
        print("• Output formatting (Markdown & JSON)")
        print("• Agent data exchange protocols")
        print("• Complete meal planning workflows")
        print("• Various user profile scenarios")
        
    else:
        print(f"\n⚠️  {total_suites - passed_suites} test suite(s) failed")
        print("\nFailed test suites:")
        for result in results:
            if not result['success']:
                print(f"❌ {result['description']}")
    
    print(f"\n{'='*80}")
    
    # Return appropriate exit code
    return 0 if passed_suites == total_suites else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
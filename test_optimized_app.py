"""
Test script to validate the optimized app has no import or function definition errors
"""

import sys
import traceback

def test_imports():
    """Test all imports work correctly"""
    try:
        print("🧪 Testing imports...")
        
        # Test core imports
        import streamlit as st
        print("✅ Streamlit import successful")
        
        import time
        from datetime import datetime, timedelta
        print("✅ Standard library imports successful")
        
        # Test custom imports
        from optimized_hr_agent import OptimizedHRAgent
        print("✅ OptimizedHRAgent import successful")
        
        from hr_agent import InterviewSlot, LeaveRequest
        print("✅ HR Agent components import successful")
        
        from performance_optimizer import (
            PerformanceOptimizer, StreamlitStateManager, 
            LazyUIRenderer, monitor_performance
        )
        print("✅ Performance optimizer imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_function_definitions():
    """Test that all functions are properly defined"""
    try:
        print("\n🧪 Testing function definitions...")
        
        # Read the app file and check for function calls
        with open('app_optimized.py', 'r') as f:
            content = f.read()
        
        # Check for potential undefined function calls
        undefined_functions = []
        
        # List of functions that should be defined inline
        inline_functions = [
            'create_job_description',
            'create_candidates', 
            'create_interview_slots',
            'show_performance_report'
        ]
        
        for func in inline_functions:
            if f"{func}(" in content:
                # Check if it's defined before being called
                func_def = f"def {func}("
                call_pos = content.find(f"{func}(")
                def_pos = content.find(func_def)
                
                if def_pos == -1:
                    undefined_functions.append(f"{func} - not defined")
                elif def_pos > call_pos:
                    undefined_functions.append(f"{func} - called before definition")
        
        if undefined_functions:
            print("❌ Function definition issues:")
            for issue in undefined_functions:
                print(f"   - {issue}")
            return False
        else:
            print("✅ All functions properly defined")
            return True
            
    except Exception as e:
        print(f"❌ Function definition test error: {e}")
        return False

def test_syntax():
    """Test Python syntax is valid"""
    try:
        print("\n🧪 Testing Python syntax...")
        
        with open('app_optimized.py', 'r') as f:
            content = f.read()
        
        # Compile to check syntax
        compile(content, 'app_optimized.py', 'exec')
        print("✅ Python syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Syntax test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Optimized HR Agent App")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Function Definition Test", test_function_definitions), 
        ("Syntax Test", test_syntax)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The optimized app should run without errors.")
        print("\n🚀 Ready to run: streamlit run app_optimized.py")
    else:
        print("❌ SOME TESTS FAILED! Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
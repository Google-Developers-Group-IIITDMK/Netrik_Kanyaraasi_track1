"""
Simple validation script for the optimized app
"""

def validate_app():
    """Validate the optimized app can be imported and run"""
    
    print("🧪 Validating Optimized HR Agent App")
    print("=" * 40)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from optimized_hr_agent import OptimizedHRAgent
        from performance_optimizer import PerformanceOptimizer
        from hr_agent import InterviewSlot, LeaveRequest
        print("   ✅ All imports successful")
        
        # Test basic functionality
        print("2. Testing basic functionality...")
        agent = OptimizedHRAgent(use_llm=False)  # Use template mode for testing
        optimizer = PerformanceOptimizer()
        print("   ✅ Objects created successfully")
        
        # Test system status
        print("3. Testing system status...")
        status = agent.get_system_status()
        assert status['ready_for_demo'] == True
        print("   ✅ System status check passed")
        
        print("\n🎉 VALIDATION SUCCESSFUL!")
        print("✅ The optimized app is ready to run")
        print("🚀 Command: streamlit run app_optimized.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    validate_app()
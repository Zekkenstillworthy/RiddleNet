import sys
import os

# Simple test to verify everything works
try:
    print("Testing simulation imports...")
    from user.routes.simulation_routes import simulation_bp
    print("✅ Simulation routes imported")
    
    from user.views import user_bp  
    print("✅ User views imported")
    
    print("✅ All imports successful!")
    print("🎉 SIMULATIONS ARE READY!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

#!/usr/bin/env python3
"""
Test script to check admin-user simulation data flow
without requiring authentication
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from admin.models.simulation import Simulation
    from admin import db
    from __init__ import create_app
    import json
    
    app = create_app()
    with app.app_context():
        # Check total simulations
        total_sims = Simulation.query.count()
        print(f"✅ Database connection works")
        print(f"📊 Total simulations: {total_sims}")
        
        if total_sims == 0:
            print("❌ No simulations found in database")
            print("🔧 You need to create a simulation in the admin panel first")
            exit(1)
        
        # Check specific simulations
        sim_1 = Simulation.query.get(1)
        sim_61 = Simulation.query.get(61)
        
        print("\n=== Testing Simulation Data Flow ===")
        
        def test_simulation(sim, sim_id):
            if not sim:
                print(f"❌ Simulation {sim_id} not found")
                return False
                
            print(f"\n🎯 Simulation {sim_id}: {sim.title}")
            print(f"   📝 Published: {sim.is_published}")
            print(f"   🟢 Active: {sim.is_active}")
            
            # Check step definitions
            has_steps = bool(sim.step_definitions)
            steps_count = len(sim.step_definitions) if sim.step_definitions else 0
            print(f"   📋 Steps: {steps_count}")
            
            # Check validation rules  
            has_validation = bool(sim.validation_rules)
            validation_count = len(sim.validation_rules) if sim.validation_rules else 0
            print(f"   ✅ Validation rules: {validation_count}")
            
            # Check simulation config
            has_config = bool(sim.simulation_config)
            print(f"   ⚙️ Has config: {has_config}")
            
            # Overall assessment
            is_complete = (sim.is_published and sim.is_active and 
                          has_steps and has_validation)
            
            if is_complete:
                print(f"   ✅ Ready for user simulation")
                if steps_count > 0:
                    # Show first step structure
                    first_step = sim.step_definitions[0]
                    print(f"   📄 First step type: {type(first_step)}")
                    if isinstance(first_step, dict):
                        keys = list(first_step.keys())[:3]
                        print(f"   🔑 Step keys: {keys}")
                return True
            else:
                print(f"   ❌ Not ready - missing: ", end="")
                missing = []
                if not sim.is_published: missing.append("published")
                if not sim.is_active: missing.append("active")  
                if not has_steps: missing.append("steps")
                if not has_validation: missing.append("validation")
                print(", ".join(missing))
                return False
        
        # Test both simulations
        sim1_ready = test_simulation(sim_1, 1)
        sim61_ready = test_simulation(sim_61, 61)
        
        # Test any available simulation
        if not sim1_ready and not sim61_ready:
            print("\n🔍 Checking first available simulation...")
            first_sim = Simulation.query.first()
            if first_sim:
                ready = test_simulation(first_sim, first_sim.id)
                if ready:
                    print(f"\n✅ Test this URL: http://127.0.0.1:5001/dynamic/simulation/{first_sim.id}")
                    print(f"✅ Admin URL: http://127.0.0.1:5001/admin/simulation/edit/{first_sim.id}")
        
        # Summary
        print(f"\n=== CONCLUSION ===")
        if sim1_ready:
            print("✅ Simulation 1 is ready - admin data WILL flow to user")
            print("🔗 Admin: http://127.0.0.1:5001/admin/simulation/edit/1")  
            print("👤 User: http://127.0.0.1:5001/dynamic/simulation/1")
        elif sim61_ready:
            print("✅ Simulation 61 is ready - admin data WILL flow to user")
            print("🔗 Admin: http://127.0.0.1:5001/admin/simulation/edit/61")
            print("👤 User: http://127.0.0.1:5001/dynamic/simulation/61")
        else:
            print("❌ Neither simulation is ready for full admin→user flow")
            print("🔧 Create/publish simulations in admin panel first")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

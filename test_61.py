#!/usr/bin/env python3
"""
Test actual connectivity between same simulation ID in admin and user
"""

import sqlite3
import json

def test_same_simulation():
    """Test if the SAME simulation works in both admin and user interfaces"""
    try:
        conn = sqlite3.connect('instance/riddlenet.db')
        cursor = conn.cursor()
        
        print("🎯 TESTING SAME SIMULATION (ID 61) IN BOTH INTERFACES")
        print("=" * 60)
        
        cursor.execute("""
            SELECT id, title, step_definitions, validation_rules, simulation_config, 
                   is_published, is_active
            FROM simulations WHERE id = 61
        """)
        
        result = cursor.fetchone()
        if result:
            sim_id, title, step_defs, val_rules, sim_config, published, active = result
            
            print(f"📋 SIMULATION 61 ANALYSIS")
            print(f"Title: {title}")
            print(f"Published: {published}, Active: {active}")
            
            # Detailed step analysis
            if step_defs:
                try:
                    if isinstance(step_defs, str):
                        steps = json.loads(step_defs)
                    else:
                        steps = step_defs
                        
                    print(f"\n🔍 STEP DEFINITIONS ({len(steps)} steps):")
                    for i, step in enumerate(steps[:3]):  # First 3 steps
                        if isinstance(step, dict):
                            print(f"   Step {i+1}:")
                            print(f"      Title: {step.get('title', 'N/A')}")
                            print(f"      Type: {step.get('type', 'N/A')}")
                            print(f"      Instruction: {step.get('instruction', 'N/A')[:50]}...")
                            print(f"      Description: {step.get('description', 'N/A')[:50]}...")
                        
                except Exception as e:
                    print(f"   ❌ Step parsing error: {e}")
            
            # Validation rules analysis
            if val_rules:
                try:
                    if isinstance(val_rules, str):
                        rules = json.loads(val_rules)
                    else:
                        rules = val_rules
                        
                    print(f"\n🔍 VALIDATION RULES ({len(rules)} rules):")
                    for step_idx, rule in list(rules.items())[:3]:
                        print(f"   Step {step_idx}: {rule.get('type', 'unknown')} validation")
                        
                except Exception as e:
                    print(f"   ❌ Validation parsing error: {e}")
            
            # Simulation config analysis
            if sim_config:
                try:
                    if isinstance(sim_config, str):
                        config = json.loads(sim_config)
                    else:
                        config = sim_config
                        
                    print(f"\n🔍 SIMULATION CONFIG:")
                    print(f"   Has topology: {'network_topology' in config}")
                    print(f"   Has devices: {'devices' in config}")
                    print(f"   Keys: {list(config.keys())}")
                        
                except Exception as e:
                    print(f"   ❌ Config parsing error: {e}")
        
        print(f"\n🚨 THE REAL PROBLEM:")
        print(f"=" * 30)
        print(f"❌ User should access: http://127.0.0.1:5001/dynamic/simulation/61")
        print(f"❌ Not: http://127.0.0.1:5001/dynamic/simulation/1")
        print(f"✅ Admin edits simulation 61, user should RUN simulation 61!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_same_simulation()

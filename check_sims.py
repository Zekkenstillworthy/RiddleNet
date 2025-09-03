#!/usr/bin/env python3
"""
Check connectivity between admin simulation 61 and user simulation 1
Based on the screenshots provided
"""

import sqlite3
import json

def check_simulation_connectivity():
    """Check the actual data flow between admin and user simulations"""
    try:
        conn = sqlite3.connect('instance/riddlenet.db')
        cursor = conn.cursor()
        
        print("🔍 ANALYZING ADMIN→USER SIMULATION CONNECTIVITY")
        print("=" * 60)
        print("Admin Editor: http://localhost:5001/admin/simulation/edit/61")
        print("User Runner:  http://127.0.0.1:5001/dynamic/simulation/1")
        print()
        
        # Check both simulations
        for sim_id in [1, 61]:
            cursor.execute("""
                SELECT id, title, step_definitions, validation_rules, is_published, is_active
                FROM simulations WHERE id = ?
            """, (sim_id,))
            
            result = cursor.fetchone()
            if result:
                sim_id, title, step_defs, val_rules, published, active = result
                print(f"📋 SIMULATION {sim_id}: {title}")
                print(f"   Published: {published}, Active: {active}")
                
                # Parse step definitions
                if step_defs:
                    try:
                        if isinstance(step_defs, str):
                            parsed_steps = json.loads(step_defs)
                        else:
                            parsed_steps = step_defs
                            
                        # Handle double-encoded JSON
                        if isinstance(parsed_steps, str):
                            parsed_steps = json.loads(parsed_steps)
                            
                        print(f"   ✅ Steps parsed: {len(parsed_steps)} steps")
                        
                        # Analyze first step structure
                        if len(parsed_steps) > 0:
                            step1 = parsed_steps[0]
                            if isinstance(step1, dict):
                                print(f"      First step type: {type(step1)}")
                                print(f"      Keys: {list(step1.keys())}")
                                
                                # Check for user-facing fields
                                has_title = bool(step1.get('title') or step1.get('instruction'))
                                has_content = bool(step1.get('description') or step1.get('content'))
                                print(f"      Has title/instruction: {'✅' if has_title else '❌'}")
                                print(f"      Has content: {'✅' if has_content else '❌'}")
                                
                    except Exception as e:
                        print(f"   ❌ Step parsing error: {e}")
                else:
                    print(f"   ❌ No step definitions")
                
                # Check validation rules
                if val_rules:
                    try:
                        if isinstance(val_rules, str):
                            parsed_rules = json.loads(val_rules)
                        else:
                            parsed_rules = val_rules
                            
                        print(f"   ✅ Validation rules: {len(parsed_rules)} rules")
                    except Exception as e:
                        print(f"   ❌ Validation parsing error: {e}")
                else:
                    print(f"   ❌ No validation rules")
                    
            else:
                print(f"❌ Simulation {sim_id} not found")
            
            print()
        
        conn.close()
        
        # Analyze the connectivity based on screenshots
        print("📸 SCREENSHOT ANALYSIS")
        print("=" * 30)
        print("User Interface (Simulation 1):")
        print("- Shows 'IPv4 Subnetting Fundamentals'")
        print("- Has 3 steps: Introduction, Learning Objective, Assessment")
        print("- Step 1 shows 'Follow the instructions to proceed'")
        print("- Interface is functional but basic")
        print()
        print("Admin Interface (Simulation 61):")
        print("- Shows 'Troubleshooting Simulation Editor'") 
        print("- Title: 'Static Routing Configuration'")
        print("- Has network topology canvas")
        print("- Rich editing tools and device placement")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    check_simulation_connectivity()

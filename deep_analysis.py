#!/usr/bin/env python3
"""
Database Deep Dive Test - Check actual simulation data structure
"""

import sqlite3
import json

def analyze_simulation_data():
    """Analyze the actual simulation data structure"""
    try:
        conn = sqlite3.connect('instance/riddlenet.db')
        cursor = conn.cursor()
        
        print("🔍 DEEP DATABASE ANALYSIS")
        print("=" * 50)
        
        # Get first few simulations with full details
        cursor.execute("""
            SELECT id, title, step_definitions, validation_rules, simulation_config
            FROM simulations 
            WHERE is_published = 1 AND is_active = 1
            ORDER BY id ASC
            LIMIT 3
        """)
        
        results = cursor.fetchall()
        
        for sim_id, title, step_defs, val_rules, sim_config in results:
            print(f"\n📋 SIMULATION {sim_id}: {title}")
            print("-" * 40)
            
            # Analyze step_definitions
            print(f"Step definitions type: {type(step_defs)}")
            if step_defs:
                print(f"Step definitions length: {len(str(step_defs))}")
                print(f"First 200 chars: {str(step_defs)[:200]}...")
                
                # Try to parse as JSON
                try:
                    if isinstance(step_defs, str):
                        parsed_steps = json.loads(step_defs)
                    else:
                        parsed_steps = step_defs
                    
                    print(f"Parsed successfully: {type(parsed_steps)}")
                    if isinstance(parsed_steps, list):
                        print(f"Steps count: {len(parsed_steps)}")
                        if len(parsed_steps) > 0:
                            print(f"First step type: {type(parsed_steps[0])}")
                            if isinstance(parsed_steps[0], dict):
                                print(f"First step keys: {list(parsed_steps[0].keys())}")
                            else:
                                print(f"First step content: {parsed_steps[0]}")
                    else:
                        print(f"Not a list: {type(parsed_steps)}")
                        
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
                except Exception as e:
                    print(f"Parse error: {e}")
            else:
                print("No step definitions")
            
            # Analyze validation_rules
            print(f"\nValidation rules type: {type(val_rules)}")
            if val_rules:
                print(f"Validation rules length: {len(str(val_rules))}")
                try:
                    if isinstance(val_rules, str):
                        parsed_rules = json.loads(val_rules)
                    else:
                        parsed_rules = val_rules
                    print(f"Validation rules parsed: {type(parsed_rules)}")
                    if isinstance(parsed_rules, dict):
                        print(f"Rules count: {len(parsed_rules)}")
                        print(f"Rule keys: {list(parsed_rules.keys())[:5]}")
                except Exception as e:
                    print(f"Validation rules parse error: {e}")
            else:
                print("No validation rules")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    analyze_simulation_data()

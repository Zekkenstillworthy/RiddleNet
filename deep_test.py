import sqlite3
import json

conn = sqlite3.connect('instance/riddlenet.db')
cursor = conn.cursor()

try:
    # Get detailed info about simulation 1 
    cursor.execute("""
        SELECT id, title, step_definitions, validation_rules, simulation_config, 
               is_published, is_active, base_score 
        FROM simulations WHERE id = 1
    """)
    
    result = cursor.fetchone()
    if result:
        sim_id, title, steps_raw, validation_raw, config_raw, published, active, base_score = result
        
        print(f"=== SIMULATION {sim_id} DATA ANALYSIS ===")
        print(f"🎯 Title: {title}")
        print(f"📊 Published: {published}, Active: {active}")
        print(f"💯 Base Score: {base_score}")
        
        # Test step definitions parsing
        print(f"\n📋 STEP DEFINITIONS:")
        print(f"   Raw type: {type(steps_raw)}")
        print(f"   Raw length: {len(steps_raw) if steps_raw else 0}")
        
        if steps_raw:
            try:
                if isinstance(steps_raw, str):
                    steps_parsed = json.loads(steps_raw)
                else:
                    steps_parsed = steps_raw
                    
                print(f"   ✅ Parsed successfully: {len(steps_parsed)} steps")
                
                # Show first step structure
                if steps_parsed and len(steps_parsed) > 0:
                    first_step = steps_parsed[0]
                    print(f"   📄 First step type: {type(first_step)}")
                    if isinstance(first_step, dict):
                        print(f"   🔑 Keys: {list(first_step.keys())}")
                        # Check for common fields
                        has_title = 'title' in first_step or 'question_text' in first_step or 'questionText' in first_step
                        has_content = 'content' in first_step or 'description' in first_step
                        has_type = 'type' in first_step or 'question_type' in first_step or 'questionType' in first_step
                        print(f"   ✅ Has title/text: {has_title}")
                        print(f"   ✅ Has content: {has_content}")  
                        print(f"   ✅ Has type: {has_type}")
                        
            except Exception as e:
                print(f"   ❌ Parse error: {e}")
                print(f"   Raw preview: {str(steps_raw)[:100]}...")
        else:
            print(f"   ❌ No step definitions found")
        
        # Test validation rules
        print(f"\n⚖️ VALIDATION RULES:")
        print(f"   Raw type: {type(validation_raw)}")
        print(f"   Has data: {bool(validation_raw)}")
        
        if validation_raw:
            try:
                if isinstance(validation_raw, str):
                    validation_parsed = json.loads(validation_raw)
                else:
                    validation_parsed = validation_raw
                    
                print(f"   ✅ Parsed successfully: {len(validation_parsed)} rules")
                
                if validation_parsed and isinstance(validation_parsed, dict):
                    print(f"   🔑 Rule keys: {list(validation_parsed.keys())[:5]}")
                    
            except Exception as e:
                print(f"   ❌ Parse error: {e}")
        else:
            print(f"   ⚠️ No validation rules (will generate from steps)")
        
        # Test simulation config  
        print(f"\n⚙️ SIMULATION CONFIG:")
        print(f"   Raw type: {type(config_raw)}")
        print(f"   Has data: {bool(config_raw)}")
        
        if config_raw:
            try:
                if isinstance(config_raw, str):
                    config_parsed = json.loads(config_raw)
                else:
                    config_parsed = config_raw
                    
                print(f"   ✅ Parsed successfully: {len(config_parsed)} items")
                print(f"   🔑 Keys: {list(config_parsed.keys())[:5]}")
                    
            except Exception as e:
                print(f"   ❌ Parse error: {e}")
        
        # Final assessment
        print(f"\n=== CONNECTION ASSESSMENT ===")
        has_steps = bool(steps_raw)
        is_ready = published and active and has_steps
        
        if is_ready:
            print(f"✅ FULLY CONNECTED: Admin data flows to user simulation")
            print(f"🔗 Admin URL: http://127.0.0.1:5001/admin/simulation/edit/{sim_id}")
            print(f"👤 User URL: http://127.0.0.1:5001/dynamic/simulation/{sim_id}")
            print(f"🎮 The simulation WILL work end-to-end!")
        else:
            missing = []
            if not published: missing.append("not published")
            if not active: missing.append("not active")
            if not has_steps: missing.append("no steps")
            print(f"❌ NOT READY: {', '.join(missing)}")
        
    else:
        print("❌ Simulation 1 not found")
        
    # Also test simulation 61
    print(f"\n" + "="*50)
    cursor.execute("SELECT id, title, is_published, is_active, step_definitions FROM simulations WHERE id = 61")
    sim61 = cursor.fetchone()
    
    if sim61:
        sim_id, title, published, active, steps_raw = sim61
        print(f"🎯 Simulation 61: {title}")
        print(f"📊 Published: {published}, Active: {active}")
        has_steps = bool(steps_raw)
        print(f"📋 Has steps: {has_steps}")
        
        if published and active and has_steps:
            print(f"✅ Simulation 61 is also ready!")
            print(f"🔗 Admin URL: http://127.0.0.1:5001/admin/simulation/edit/61")
            print(f"👤 User URL: http://127.0.0.1:5001/dynamic/simulation/61")

finally:
    conn.close()

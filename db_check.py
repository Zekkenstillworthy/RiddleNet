import sqlite3

try:
    conn = sqlite3.connect('instance/riddlenet.db')
    cursor = conn.cursor()
    
    # Check if simulations table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simulations'")
    if cursor.fetchone():
        print("✅ Simulations table exists")
        
        # Get simulation count
        cursor.execute("SELECT COUNT(*) FROM simulations")
        count = cursor.fetchone()[0]
        print(f"📊 Total simulations: {count}")
        
        if count > 0:
            # Check specific simulations
            cursor.execute("SELECT id, title, is_published, is_active FROM simulations WHERE id IN (1, 61)")
            sims = cursor.fetchall()
            
            print("\n=== Simulation Status ===")
            for sim_id, title, published, active in sims:
                print(f"ID {sim_id}: {title} (Published: {published}, Active: {active})")
                
            # Check if any simulation has step definitions
            cursor.execute("SELECT id, title, step_definitions FROM simulations WHERE step_definitions IS NOT NULL AND step_definitions != '[]' LIMIT 3")
            sims_with_steps = cursor.fetchall()
            
            print(f"\n📋 Simulations with steps: {len(sims_with_steps)}")
            for sim_id, title, steps in sims_with_steps:
                print(f"  ID {sim_id}: {title} - Has step data")
                
        else:
            print("❌ No simulations found in database")
    else:
        print("❌ No simulations table found")
        
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")

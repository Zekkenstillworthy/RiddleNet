"""
Run Task Builder Database Migration
=====================================
This script runs the task assignment system migration to add:
1. task_config column to simulations table
2. task_assignments table for tracking student progress
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import create_app, db
from sqlalchemy import text

def run_migration():
    """Run the task builder database migration"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 70)
            print("🚀 Running Task Builder Database Migration")
            print("=" * 70)
            
            # Read the migration file
            migration_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'migrations',
                '004_add_task_assignment_system.sql'
            )
            
            if not os.path.exists(migration_file):
                print(f"[ERROR] Migration file not found: {migration_file}")
                return False
            
            print(f"📄 Reading migration file: {migration_file}")
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Split by semicolons but preserve function definitions
            # This is a simple approach - might need refinement for complex SQL
            statements = []
            current_statement = []
            in_function = False
            
            for line in sql_content.split('\n'):
                # Skip comments and empty lines
                if line.strip().startswith('--') or not line.strip():
                    continue
                    
                # Track function blocks
                if 'CREATE OR REPLACE FUNCTION' in line.upper() or 'CREATE FUNCTION' in line.upper():
                    in_function = True
                elif in_function and '$$' in line and 'LANGUAGE' in line.upper():
                    in_function = False
                    current_statement.append(line)
                    statements.append('\n'.join(current_statement))
                    current_statement = []
                    continue
                
                current_statement.append(line)
                
                # If not in function and line ends with semicolon, it's end of statement
                if not in_function and line.rstrip().endswith(';'):
                    statements.append('\n'.join(current_statement))
                    current_statement = []
            
            # Add any remaining statement
            if current_statement:
                statements.append('\n'.join(current_statement))
            
            print(f"[NOTE] Found {len(statements)} SQL statements to execute")
            print()
            
            # Execute each statement
            success_count = 0
            for i, statement in enumerate(statements, 1):
                statement = statement.strip()
                if not statement:
                    continue
                
                try:
                    # Show what we're executing (first 100 chars)
                    preview = statement[:100].replace('\n', ' ')
                    print(f"[{i}/{len(statements)}] Executing: {preview}...")
                    
                    db.session.execute(text(statement))
                    db.session.commit()
                    success_count += 1
                    print(f"    [OK] Success")
                    
                except Exception as e:
                    error_msg = str(e)
                    # Check if it's an "already exists" error (which is OK)
                    if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                        print(f"    [WARNING]  Already exists (skipping)")
                        db.session.rollback()
                        success_count += 1
                    else:
                        print(f"    [ERROR] Error: {error_msg}")
                        db.session.rollback()
            
            print()
            print("=" * 70)
            print(f"[OK] Migration complete! {success_count}/{len(statements)} statements executed")
            print("=" * 70)
            print()
            
            # Verify the changes
            print("[DEBUG] Verifying migration...")
            
            # Check if task_config column exists
            try:
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'simulations' 
                    AND column_name = 'task_config'
                """))
                if result.fetchone():
                    print("[OK] task_config column exists in simulations table")
                else:
                    print("[WARNING]  task_config column NOT found in simulations table")
            except Exception as e:
                print(f"[WARNING]  Could not verify task_config column: {e}")
            
            # Check if task_assignments table exists
            try:
                result = db.session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'task_assignments'
                    )
                """))
                if result.scalar():
                    print("[OK] task_assignments table exists")
                    
                    # Count rows
                    count_result = db.session.execute(text("SELECT COUNT(*) FROM task_assignments"))
                    count = count_result.scalar()
                    print(f"   📊 {count} task assignment(s) in database")
                else:
                    print("[WARNING]  task_assignments table NOT found")
            except Exception as e:
                print(f"[WARNING]  Could not verify task_assignments table: {e}")
            
            # Check if sample data was added to simulation id=1
            try:
                from instructor.models.simulation import Simulation
                sim = Simulation.query.get(1)
                if sim and sim.task_config:
                    print(f"[OK] Sample task configuration loaded in simulation #{sim.id} ('{sim.title}')")
                    print(f"   Task enabled: {sim.task_config.get('enabled', False)}")
                    print(f"   Devices: {len(sim.task_config.get('device_requirements', []))}")
                    print(f"   Connections: {len(sim.task_config.get('connection_requirements', []))}")
                elif sim:
                    print(f"[WARNING]  Simulation #{sim.id} exists but has no task_config")
                else:
                    print("ℹ️  No simulation with id=1 found (this is OK for new installations)")
            except Exception as e:
                print(f"[WARNING]  Could not verify sample data: {e}")
            
            print()
            print("=" * 70)
            print("🎉 Task Builder Migration Complete!")
            print("=" * 70)
            print()
            print("📚 Next Steps:")
            print("   1. Restart your application: python run.py")
            print("   2. Navigate to: /admin/simulation/edit/<id>")
            print("   3. Click the clipboard icon to open Task Builder")
            print("   4. Start creating task assignments!")
            print()
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)

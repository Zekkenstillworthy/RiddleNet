"""
Migrate task_config data from simulation_config['task_config'] to dedicated task_config column
This fixes the issue where task builder data was saved in the wrong location
"""

from instructor.models.simulation import Simulation
from __init__ import db, create_app

def migrate_task_config():
    """Move task_config from simulation_config to dedicated column"""
    app = create_app()
    
    with app.app_context():
        # Get all simulations
        simulations = Simulation.query.all()
        migrated_count = 0
        
        for sim in simulations:
            try:
                # Parse simulation_config if it's a string
                simulation_config = sim.simulation_config
                if isinstance(simulation_config, str):
                    import json
                    try:
                        simulation_config = json.loads(simulation_config)
                    except:
                        simulation_config = {}
                
                # Check if simulation_config contains task_config
                if isinstance(simulation_config, dict) and 'task_config' in simulation_config:
                    old_task_config = simulation_config['task_config']
                    
                    # Only migrate if there's actual data (not empty)
                    if old_task_config and isinstance(old_task_config, dict):
                        # Check if it has meaningful data
                        has_data = (
                            (old_task_config.get('device_requirements') and len(old_task_config.get('device_requirements', [])) > 0) or
                            (old_task_config.get('connection_requirements') and len(old_task_config.get('connection_requirements', [])) > 0) or
                            (old_task_config.get('cli_requirements') and len(old_task_config.get('cli_requirements', {})) > 0)
                        )
                        
                        if has_data:
                            # Migrate to dedicated column
                            sim.task_config = old_task_config
                            
                            # Optionally remove from old location (keep for now for safety)
                            # del sim.simulation_config['task_config']
                            
                            migrated_count += 1
                            print(f"✅ Migrated simulation #{sim.id}: {sim.title}")
                            print(f"   - Devices: {len(old_task_config.get('device_requirements', []))}")
                            print(f"   - Connections: {len(old_task_config.get('connection_requirements', []))}")
                            print(f"   - CLI devices: {len(old_task_config.get('cli_requirements', {}))}")
            
            except Exception as e:
                print(f"❌ Error migrating simulation #{sim.id}: {e}")
                continue
        
        # Commit all changes
        if migrated_count > 0:
            db.session.commit()
            print(f"\n🎉 Successfully migrated {migrated_count} simulation(s)")
        else:
            print("\nℹ️ No simulations needed migration")

if __name__ == '__main__':
    migrate_task_config()

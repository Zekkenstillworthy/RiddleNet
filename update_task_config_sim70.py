"""
Update Task Configuration for Simulation 70
Changes device requirements from R1, R2 to router_1, router_2
"""

from application import create_app
from __init__ import db
from instructor.models.simulation import Simulation
import json

def update_simulation_70_task_config():
    """Update the task configuration for simulation 70"""
    
    # Get simulation 70
    simulation = Simulation.query.get(70)
    
    if not simulation:
        print("❌ Simulation 70 not found!")
        return False
    
    print(f"📋 Found simulation: {simulation.title}")
    
    # Get current task_config
    task_config = simulation.task_config or {}
    
    if isinstance(task_config, str):
        task_config = json.loads(task_config)
    
    print("\n🔍 Current Task Config:")
    print(json.dumps(task_config, indent=2))
    
    # Update device_requirements
    if 'device_requirements' in task_config:
        for device in task_config['device_requirements']:
            if device.get('id') == 'R1':
                device['id'] = 'router_1'
                print(f"✅ Updated R1 -> router_1")
            elif device.get('id') == 'R2':
                device['id'] = 'router_2'
                print(f"✅ Updated R2 -> router_2")
    
    # Update connection_requirements
    if 'connection_requirements' in task_config:
        for connection in task_config['connection_requirements']:
            if connection.get('source_device') == 'R1':
                connection['source_device'] = 'router_1'
                print(f"✅ Updated connection source_device R1 -> router_1")
            if connection.get('target_device') == 'R1':
                connection['target_device'] = 'router_1'
                print(f"✅ Updated connection target_device R1 -> router_1")
            if connection.get('source_device') == 'R2':
                connection['source_device'] = 'router_2'
                print(f"✅ Updated connection source_device R2 -> router_2")
            if connection.get('target_device') == 'R2':
                connection['target_device'] = 'router_2'
                print(f"✅ Updated connection target_device R2 -> router_2")
    
    # Update cli_requirements
    if 'cli_requirements' in task_config:
        old_cli_reqs = task_config['cli_requirements']
        new_cli_reqs = {}
        
        for device_id, commands in old_cli_reqs.items():
            if device_id == 'R1':
                new_cli_reqs['router_1'] = commands
                print(f"✅ Updated CLI requirements R1 -> router_1")
            elif device_id == 'R2':
                new_cli_reqs['router_2'] = commands
                print(f"✅ Updated CLI requirements R2 -> router_2")
            else:
                new_cli_reqs[device_id] = commands
        
        task_config['cli_requirements'] = new_cli_reqs
    
    # Save updated task_config
    simulation.task_config = task_config
    
    # Mark the field as modified (required for JSONB columns in SQLAlchemy)
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(simulation, 'task_config')
    
    try:
        db.session.commit()
        print("\n✅ Task configuration updated successfully!")
        print("\n📋 Updated Task Config:")
        print(json.dumps(task_config, indent=2))
        return True
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error updating task config: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting task configuration update for simulation 70...\n")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        success = update_simulation_70_task_config()
        
        if success:
            print("\n✅ Update completed successfully!")
            print("\n📝 Next steps:")
            print("1. Restart the Flask server")
            print("2. Hard refresh your browser (Ctrl+F5)")
            print("3. The validation should now accept router_1 and router_2")
        else:
            print("\n❌ Update failed!")

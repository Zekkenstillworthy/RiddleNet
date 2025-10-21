from application import create_app
from __init__ import db
from instructor.models.simulation import Simulation
import json

app = create_app()

with app.app_context():
    sim = Simulation.query.get(70)
    print("\n" + "="*80)
    print("CURRENT DATABASE STATE - Simulation 70 task_config")
    print("="*80)
    
    print("\n📋 Device Requirements:")
    print(json.dumps(sim.task_config.get('device_requirements', []), indent=2))
    
    print("\n🔗 Connection Requirements:")
    print(json.dumps(sim.task_config.get('connection_requirements', []), indent=2))
    
    print("\n💻 CLI Requirements (device keys):")
    cli_reqs = sim.task_config.get('cli_requirements', {})
    print(list(cli_reqs.keys()))
    
    print("\n" + "="*80)

import eventlet
eventlet.monkey_patch()

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run import create_app
from admin.models.simulation import Simulation
import json

app = create_app()

with app.app_context():
    sim1 = Simulation.query.get(1)
    sim2 = Simulation.query.get(2)
    
    print("\n=== DETAILED CHECK ===")
    
    if sim1:
        print(f"\nSimulation 1: {sim1.title}")
        print(f"Config length: {len(sim1.simulation_config) if sim1.simulation_config else 0} characters")
        if sim1.simulation_config:
            config = json.loads(sim1.simulation_config)
            print(f"Config keys: {list(config.keys())}")
            if 'step_definitions' in config:
                print(f"Steps: {len(config['step_definitions'])}")
            else:
                print("No step_definitions found")
    
    if sim2:
        print(f"\nSimulation 2: {sim2.title}")
        print(f"Config length: {len(sim2.simulation_config) if sim2.simulation_config else 0} characters")
        if sim2.simulation_config:
            config = json.loads(sim2.simulation_config)
            print(f"Config keys: {list(config.keys())}")
            if 'step_definitions' in config:
                print(f"Steps: {len(config['step_definitions'])}")
            else:
                print("No step_definitions found")
    
    print(f"\nConfigs are identical: {sim1.simulation_config == sim2.simulation_config if sim1 and sim2 else 'N/A'}")
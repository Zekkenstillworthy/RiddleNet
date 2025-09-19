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
    # Check the simulations
    sim1 = Simulation.query.get(1)
    sim2 = Simulation.query.get(2)
    
    print("\n=== VERIFICATION OF FIX ===")
    
    if sim1:
        print(f"\nSimulation 1: {sim1.title}")
        if sim1.simulation_config:
            config = json.loads(sim1.simulation_config)
            print(f"- Has topology: {'topology' in config}")
            if 'topology' in config:
                print(f"- Devices: {len(config['topology'].get('devices', []))}")
                print(f"- Device types: {[d.get('type') for d in config['topology'].get('devices', [])]}")
                if config['topology'].get('devices'):
                    print(f"- First device: {config['topology']['devices'][0].get('name', 'Unknown')}")
        else:
            print("- No configuration found")
    
    if sim2:
        print(f"\nSimulation 2: {sim2.title}")
        if sim2.simulation_config:
            config = json.loads(sim2.simulation_config)
            print(f"- Has topology: {'topology' in config}")
            if 'topology' in config:
                print(f"- Devices: {len(config['topology'].get('devices', []))}")
                print(f"- Device types: {[d.get('type') for d in config['topology'].get('devices', [])]}")
                if config['topology'].get('devices'):
                    print(f"- First device: {config['topology']['devices'][0].get('name', 'Unknown')}")
        else:
            print("- No configuration found")
    
    # Check if configs are different now
    if sim1 and sim2 and sim1.simulation_config and sim2.simulation_config:
        same_config = sim1.simulation_config == sim2.simulation_config
        print(f"\nConfigurations identical: {same_config}")
        
        if not same_config:
            print("✅ SUCCESS: Simulations now have different configurations!")
            
            # Quick check of step counts
            config1 = json.loads(sim1.simulation_config)
            config2 = json.loads(sim2.simulation_config)
            
            steps1 = len(config1.get('step_definitions', []))
            steps2 = len(config2.get('step_definitions', []))
            
            print(f"- Simulation 1 steps: {steps1}")
            print(f"- Simulation 2 steps: {steps2}")
        else:
            print("❌ ISSUE: Configurations are still identical")
    else:
        print("❌ Could not verify - missing simulation data")
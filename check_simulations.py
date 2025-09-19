#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run import create_app
from admin.models.simulation import Simulation
import json

def check_simulations():
    """Check simulations in the database"""
    app = create_app()
    
    with app.app_context():
        print("=== CHECKING SIMULATIONS IN DATABASE ===\n")
        
        simulations = Simulation.query.all()
        
        if not simulations:
            print("No simulations found in database.")
            return
        
        for sim in simulations:
            print(f"Simulation ID: {sim.id}")
            print(f"Title: {sim.title}")
            print(f"Type: {sim.simulation_type}")
            print(f"Category: {sim.category}")
            print(f"Active: {sim.is_active}")
            print(f"Published: {sim.is_published}")
            
            # Check simulation config
            sim_config = sim.simulation_config or {}
            if isinstance(sim_config, str):
                try:
                    sim_config = json.loads(sim_config)
                except:
                    sim_config = {}
            
            if isinstance(sim_config, dict):
                print(f"Config keys: {list(sim_config.keys()) if sim_config else 'None'}")
            else:
                print(f"Config type: {type(sim_config)} - {str(sim_config)[:100]}...")
            
            # Check topology data specifically
            topology = sim_config.get('network_topology', {})
            if topology:
                devices = topology.get('devices', [])
                connections = topology.get('connections', [])
                print(f"Topology - Devices: {len(devices)}, Connections: {len(connections)}")
                
                # Show first few devices for verification
                if devices:
                    print(f"  Sample devices: {[d.get('id', 'no-id') + ':' + d.get('type', 'no-type') for d in devices[:3]]}")
            else:
                print("No network topology found")
            
            # Check step definitions
            steps = sim.step_definitions or []
            if isinstance(steps, str):
                try:
                    steps = json.loads(steps)
                except:
                    steps = []
            
            print(f"Steps: {len(steps) if steps else 0}")
            
            print("-" * 50)

if __name__ == "__main__":
    check_simulations()

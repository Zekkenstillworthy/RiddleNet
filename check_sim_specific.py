#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment to handle Unicode better
os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask
from admin import db
from run import create_app
from admin.models.simulation import Simulation
import json

def check_specific_simulations():
    """Check specific simulations 1 and 2"""
    app = create_app()
    
    with app.app_context():
        print("=== CHECKING SPECIFIC SIMULATIONS ===")
        
        # Get simulations 1 and 2
        sim1 = Simulation.query.get(1)
        sim2 = Simulation.query.get(2)
        
        if sim1:
            print(f"\nSimulation 1:")
            print(f"  ID: {sim1.id}")
            print(f"  Title: {sim1.title}")
            print(f"  Description: {sim1.description[:100]}...")
            
            config1 = sim1.simulation_config
            if isinstance(config1, str):
                try:
                    config1 = json.loads(config1)
                except:
                    config1 = None
            
            if config1:
                # Check for topology data
                topo1 = config1.get('network_topology', {})
                if topo1:
                    devices1 = topo1.get('devices', [])
                    print(f"  Topology devices: {len(devices1)}")
                    if devices1:
                        print(f"    Sample device: {devices1[0] if devices1 else 'None'}")
                else:
                    print("  No network topology in config")
                
                print(f"  Config keys: {list(config1.keys())}")
            else:
                print("  No valid config found")
        else:
            print("Simulation 1 not found")
        
        if sim2:
            print(f"\nSimulation 2:")
            print(f"  ID: {sim2.id}")
            print(f"  Title: {sim2.title}")
            print(f"  Description: {sim2.description[:100]}...")
            
            config2 = sim2.simulation_config
            if isinstance(config2, str):
                try:
                    config2 = json.loads(config2)
                except:
                    config2 = None
            
            if config2:
                # Check for topology data
                topo2 = config2.get('network_topology', {})
                if topo2:
                    devices2 = topo2.get('devices', [])
                    print(f"  Topology devices: {len(devices2)}")
                    if devices2:
                        print(f"    Sample device: {devices2[0] if devices2 else 'None'}")
                else:
                    print("  No network topology in config")
                
                print(f"  Config keys: {list(config2.keys())}")
            else:
                print("  No valid config found")
        else:
            print("Simulation 2 not found")
        
        # Check if they are actually different
        if sim1 and sim2:
            print(f"\nComparison:")
            print(f"  Same title: {sim1.title == sim2.title}")
            print(f"  Same description: {sim1.description == sim2.description}")
            print(f"  Same config: {sim1.simulation_config == sim2.simulation_config}")

if __name__ == "__main__":
    check_specific_simulations()
#!/usr/bin/env python3

from run import app
from admin.models.simulation import Simulation
import json

# Create app context
with app.app_context():
    # Get simulation 1
    sim = Simulation.query.get(1)
    if sim:
        print('Simulation 1 found:')
        print('Title:', sim.title)
        print('Simulation Config Type:', type(sim.simulation_config))
        
        # Parse simulation config
        config = sim.simulation_config
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except:
                config = {}
        
        if isinstance(config, dict):
            print('Network Topology exists:', 'network_topology' in config)
            if 'network_topology' in config:
                nt = config['network_topology']
                print('Network Topology type:', type(nt))
                if isinstance(nt, dict):
                    print('Has devices:', 'devices' in nt and len(nt.get('devices', [])) > 0)
                    print('Has connections:', 'connections' in nt and len(nt.get('connections', [])) > 0)
                    print('Devices count:', len(nt.get('devices', [])))
                    print('Connections count:', len(nt.get('connections', [])))
                    if nt.get('devices'):
                        print('First device sample:', str(nt['devices'][0])[:200] if nt['devices'] else 'None')
            else:
                print('No network_topology found in config')
        else:
            print('Config is not a dict:', config)
    else:
        print('Simulation 1 not found')
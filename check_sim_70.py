#!/usr/bin/env python3

from admin.models.simulation import Simulation
from __init__ import create_app, db
import json

app = create_app()
with app.app_context():
    simulation = Simulation.query.get(70)
    if simulation:
        print(f'Simulation Title: {simulation.title}')
        config = simulation.simulation_config
        if isinstance(config, str):
            config = json.loads(config)
        print('Current config keys:', list(config.keys()) if config else 'No config')
        if config and 'network_config' in config:
            print('Network config exists')
            print('Network config:', json.dumps(config['network_config'], indent=2))
        else:
            print('No network_config found')
    else:
        print('Simulation 70 not found')
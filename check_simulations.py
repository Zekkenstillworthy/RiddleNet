#!/usr/bin/env python3

import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from admin.models import DynamicSimulation
    from admin import db
    import json

    print("Checking for existing simulations...")
    
    # Try to find any existing simulation
    sim = DynamicSimulation.query.first()
    if sim:
        print(f'Found simulation: ID={sim.id}, Title={sim.title}')
        print(f'URL: http://127.0.0.1:5001/dynamic/simulation/{sim.id}')
    else:
        print('No simulations found. Creating a test simulation...')
        # Create a simple test simulation
        test_sim = DynamicSimulation(
            title='Test Toggle Palette Simulation',
            description='A test simulation to verify togglePalette functionality',
            category='networking',
            difficulty='beginner',
            network_config=json.dumps({
                'devices': [
                    {'type': 'router', 'name': 'R1', 'position': {'x': 100, 'y': 100}},
                    {'type': 'switch', 'name': 'SW1', 'position': {'x': 300, 'y': 100}}
                ],
                'connections': []
            }),
            steps=[
                {
                    'title': 'Test Step',
                    'description': 'Click the palette toggle button to test functionality',
                    'requirements': ['Device palette should toggle visibility'],
                    'validation_criteria': []
                }
            ],
            published=True
        )
        
        db.session.add(test_sim)
        db.session.commit()
        print(f'Created test simulation: ID={test_sim.id}')
        print(f'URL: http://127.0.0.1:5001/dynamic/simulation/{test_sim.id}')
        
except Exception as e:
    print(f"Error: {e}")
    print("Make sure Flask application context is available")

#!/usr/bin/env python3
"""
Gamified Topology Scenarios Setup Script
========================================

This script populates the database with the initial Easy/Medium/Hard topology scenarios
for the gamified network topology simulation system.

Usage:
    python scripts/setup_gamified_scenarios.py
"""

import sys
import os

# Add the parent directory to the path so we can import from the main application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from application import create_app
from user.models import db
from admin.models.topology import Topology
from datetime import datetime

def create_initial_scenarios():
    """Create the initial Easy/Medium/Hard topology scenarios"""
    
    scenarios = [
        # STAR TOPOLOGY - Easy
        {
            'topology_type': 'star-topology',
            'title': 'Star Network - Easy',
            'description': 'Create a basic star topology with 4 devices connected to a central switch.',
            'difficulty': 'easy',
            'device_requirements': {
                'pc': 4,
                'switch': 1,
                'router': 0,
                'server': 0
            },
            'time_limit': 300,  # 5 minutes
            'base_score': 100,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'perfect_score': 150
            },
            'expected_config': {
                'total_devices': 5,
                'topology_type': 'star',
                'central_device': 'switch',
                'connections': 4
            },
            'tutorial_steps': [
                'Drag a switch from the device palette to the center of the canvas',
                'Add 4 PCs around the switch',
                'Use connection mode to connect each PC to the central switch',
                'Click validate to check your topology'
            ],
            'hints': [
                'A star topology has all devices connected to one central device',
                'The central device in this scenario should be a switch',
                'Each PC should connect directly to the switch, not to each other'
            ]
        },
        
        # STAR TOPOLOGY - Medium
        {
            'topology_type': 'star-topology',
            'title': 'Star Network - Medium',
            'description': 'Create a star topology with a router connecting to multiple switches and devices.',
            'difficulty': 'medium',
            'device_requirements': {
                'pc': 6,
                'switch': 2,
                'router': 1,
                'server': 1
            },
            'time_limit': 480,  # 8 minutes
            'base_score': 200,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'perfect_score': 300
            },
            'expected_config': {
                'total_devices': 10,
                'topology_type': 'star',
                'central_device': 'router',
                'connections': 9
            },
            'tutorial_steps': [
                'Place a router in the center as the main hub',
                'Add 2 switches connected to the router',
                'Connect 3 PCs to each switch',
                'Add 1 server connected to one of the switches',
                'Validate your complete star network'
            ],
            'hints': [
                'The router should be the central device connecting everything',
                'Switches can act as intermediate connection points',
                'Make sure all devices can reach each other through the router'
            ]
        },
        
        # STAR TOPOLOGY - Hard
        {
            'topology_type': 'star-topology',
            'title': 'Star Network - Hard',
            'description': 'Create a complex hierarchical star topology with multiple levels and redundancy.',
            'difficulty': 'hard',
            'device_requirements': {
                'pc': 8,
                'switch': 4,
                'router': 2,
                'server': 2
            },
            'time_limit': 600,  # 10 minutes
            'base_score': 300,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'redundancy_bonus': True,
                'perfect_score': 500
            },
            'expected_config': {
                'total_devices': 16,
                'topology_type': 'hierarchical-star',
                'central_device': 'router',
                'connections': 15,
                'redundancy': True
            },
            'tutorial_steps': [
                'Create a main router as the core',
                'Add a secondary router for redundancy',
                'Connect 4 switches to distribute connections',
                'Add 8 PCs across the switches',
                'Add 2 servers for different services',
                'Ensure proper hierarchical structure'
            ],
            'hints': [
                'Think about creating levels: Core (routers) → Distribution (switches) → Access (devices)',
                'Consider redundancy between the two routers',
                'Each switch should serve multiple end devices'
            ]
        },
        
        # BUS TOPOLOGY - Easy
        {
            'topology_type': 'bus-topology',
            'title': 'Bus Network - Easy',
            'description': 'Create a simple bus topology with devices connected in a linear fashion.',
            'difficulty': 'easy',
            'device_requirements': {
                'pc': 4,
                'switch': 0,
                'router': 0,
                'server': 1
            },
            'time_limit': 240,  # 4 minutes
            'base_score': 80,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'perfect_score': 120
            },
            'expected_config': {
                'total_devices': 5,
                'topology_type': 'bus',
                'connections': 4
            },
            'tutorial_steps': [
                'Place devices in a straight line',
                'Connect the first PC to the second PC',
                'Continue connecting each device to the next one',
                'Include the server in the linear chain'
            ],
            'hints': [
                'In a bus topology, devices are connected in a single line',
                'Each device connects to its immediate neighbors',
                'Data travels along the bus to reach all devices'
            ]
        },
        
        # BUS TOPOLOGY - Medium
        {
            'topology_type': 'bus-topology',
            'title': 'Bus Network - Medium',
            'description': 'Create a bus topology with terminators and multiple segments.',
            'difficulty': 'medium',
            'device_requirements': {
                'pc': 6,
                'switch': 1,
                'router': 1,
                'server': 2
            },
            'time_limit': 420,  # 7 minutes
            'base_score': 180,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'perfect_score': 270
            },
            'expected_config': {
                'total_devices': 10,
                'topology_type': 'segmented-bus',
                'connections': 9
            },
            'tutorial_steps': [
                'Create the main bus segment with the router',
                'Add a switch to create a secondary segment',
                'Connect PCs along both bus segments',
                'Place servers at strategic points',
                'Ensure proper bus termination'
            ],
            'hints': [
                'Use the router to connect different bus segments',
                'The switch can help manage traffic on one segment',
                'Consider where to place servers for best access'
            ]
        },
        
        # BUS TOPOLOGY - Hard
        {
            'topology_type': 'bus-topology',
            'title': 'Bus Network - Hard',
            'description': 'Create a complex bus network with multiple segments and backbone.',
            'difficulty': 'hard',
            'device_requirements': {
                'pc': 10,
                'switch': 3,
                'router': 2,
                'server': 3
            },
            'time_limit': 720,  # 12 minutes
            'base_score': 280,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'segmentation_bonus': True,
                'perfect_score': 450
            },
            'expected_config': {
                'total_devices': 18,
                'topology_type': 'backbone-bus',
                'connections': 17,
                'segments': 3
            },
            'tutorial_steps': [
                'Create a backbone bus with routers',
                'Attach multiple switch-based segments',
                'Distribute PCs across segments',
                'Place servers for different network services',
                'Optimize for performance and reliability'
            ],
            'hints': [
                'Think of a main backbone connecting smaller bus segments',
                'Use switches to manage individual segments',
                'Consider traffic flow and potential bottlenecks'
            ]
        },
        
        # RING TOPOLOGY - Easy
        {
            'topology_type': 'ring-topology',
            'title': 'Ring Network - Easy',
            'description': 'Create a simple ring topology where all devices form a closed loop.',
            'difficulty': 'easy',
            'device_requirements': {
                'pc': 4,
                'switch': 0,
                'router': 0,
                'server': 1
            },
            'time_limit': 300,  # 5 minutes
            'base_score': 90,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'perfect_score': 135
            },
            'expected_config': {
                'total_devices': 5,
                'topology_type': 'ring',
                'connections': 5,
                'closed_loop': True
            },
            'tutorial_steps': [
                'Arrange devices in a circular pattern',
                'Connect each device to its two neighbors',
                'Ensure the ring is completely closed',
                'Include the server as part of the ring'
            ],
            'hints': [
                'Every device should connect to exactly two other devices',
                'The ring must be completely closed - no breaks',
                'Data travels in one direction around the ring'
            ]
        },
        
        # RING TOPOLOGY - Medium
        {
            'topology_type': 'ring-topology',
            'title': 'Ring Network - Medium',
            'description': 'Create a dual-ring topology for redundancy and better performance.',
            'difficulty': 'medium',
            'device_requirements': {
                'pc': 6,
                'switch': 2,
                'router': 1,
                'server': 2
            },
            'time_limit': 540,  # 9 minutes
            'base_score': 220,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'redundancy_bonus': True,
                'perfect_score': 330
            },
            'expected_config': {
                'total_devices': 11,
                'topology_type': 'dual-ring',
                'connections': 22,  # Dual connections
                'redundancy': True
            },
            'tutorial_steps': [
                'Create the primary ring with all devices',
                'Add a secondary ring going in the opposite direction',
                'Use switches to manage ring segments',
                'Place the router as a gateway',
                'Ensure both rings are complete'
            ],
            'hints': [
                'Dual rings provide redundancy if one ring fails',
                'Each device should be part of both rings',
                'Consider which direction data flows in each ring'
            ]
        },
        
        # MESH TOPOLOGY - Easy
        {
            'topology_type': 'mesh-topology',
            'title': 'Mesh Network - Easy',
            'description': 'Create a partial mesh topology with some redundant connections.',
            'difficulty': 'easy',
            'device_requirements': {
                'pc': 3,
                'switch': 1,
                'router': 1,
                'server': 1
            },
            'time_limit': 360,  # 6 minutes
            'base_score': 110,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'perfect_score': 165
            },
            'expected_config': {
                'total_devices': 6,
                'topology_type': 'partial-mesh',
                'min_connections': 8,
                'redundancy': True
            },
            'tutorial_steps': [
                'Connect the router to all other devices',
                'Add connections between switches and servers',
                'Create some PC-to-PC connections',
                'Ensure multiple paths exist between devices'
            ],
            'hints': [
                'In mesh topology, devices have multiple connections',
                'Not every device needs to connect to every other device',
                'Focus on creating redundant paths'
            ]
        },
        
        # MESH TOPOLOGY - Hard
        {
            'topology_type': 'mesh-topology',
            'title': 'Mesh Network - Hard',
            'description': 'Create a full mesh topology with maximum redundancy and performance.',
            'difficulty': 'hard',
            'device_requirements': {
                'pc': 5,
                'switch': 3,
                'router': 2,
                'server': 2
            },
            'time_limit': 900,  # 15 minutes
            'base_score': 400,
            'scoring_metrics': {
                'time_bonus': True,
                'efficiency_bonus': True,
                'full_mesh_bonus': True,
                'perfect_score': 600
            },
            'expected_config': {
                'total_devices': 12,
                'topology_type': 'full-mesh',
                'connections': 66,  # n(n-1)/2 for full mesh
                'redundancy': True
            },
            'tutorial_steps': [
                'Connect every router to every other router',
                'Connect switches to multiple routers',
                'Create connections between critical devices',
                'Ensure maximum redundancy',
                'Optimize for performance and fault tolerance'
            ],
            'hints': [
                'Full mesh means every device connects to every other device',
                'This provides maximum redundancy but uses many connections',
                'Focus on the most critical connections first'
            ]
        }
    ]
    
    print("Creating gamified topology scenarios...")
    
    for scenario_data in scenarios:
        # Check if scenario already exists
        existing = Topology.query.filter_by(
            topology_type=scenario_data['topology_type'],
            title=scenario_data['title']
        ).first()
        
        if existing:
            print(f"Scenario '{scenario_data['title']}' already exists, skipping...")
            continue
        
        # Create new topology scenario
        topology = Topology(
            topology_type=scenario_data['topology_type'],
            title=scenario_data['title'],
            description=scenario_data['description'],
            device_requirements=scenario_data['device_requirements'],
            base_score=scenario_data['base_score'],
            scoring_metrics=scenario_data['scoring_metrics'],
            expected_config=scenario_data['expected_config'],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add additional gamified fields if the model supports them
        if hasattr(topology, 'difficulty'):
            topology.difficulty = scenario_data['difficulty']
        if hasattr(topology, 'time_limit'):
            topology.time_limit = scenario_data['time_limit']
        if hasattr(topology, 'tutorial_steps'):
            topology.tutorial_steps = scenario_data['tutorial_steps']
        if hasattr(topology, 'hints'):
            topology.hints = scenario_data['hints']
        
        db.session.add(topology)
        print(f"Created scenario: {scenario_data['title']} ({scenario_data['difficulty']})")
    
    try:
        db.session.commit()
        print("\n✓ Successfully created all gamified topology scenarios!")
        print(f"  Total scenarios created: {len(scenarios)}")
        print("  Difficulties: Easy (4), Medium (3), Hard (4)")
        print("  Topology types: Star, Bus, Ring, Mesh")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Error creating scenarios: {e}")
        raise

def list_scenarios():
    """List all existing scenarios in the database"""
    topologies = Topology.query.all()
    
    if not topologies:
        print("No scenarios found in database.")
        return
    
    print(f"\nExisting scenarios ({len(topologies)} total):")
    print("=" * 60)
    
    by_type = {}
    for topology in topologies:
        ttype = topology.topology_type
        if ttype not in by_type:
            by_type[ttype] = []
        by_type[ttype].append(topology)
    
    for ttype, scenarios in by_type.items():
        print(f"\n{ttype.upper()}:")
        for scenario in scenarios:
            difficulty = getattr(scenario, 'difficulty', 'unknown')
            score = scenario.base_score
            print(f"  • {scenario.title} ({difficulty}) - {score} pts")

def main():
    """Main function to setup scenarios"""
    app = create_app()
    
    with app.app_context():
        print("Gamified Topology Scenarios Setup")
        print("=" * 40)
        
        # List existing scenarios first
        list_scenarios()
        
        # Ask user if they want to create new scenarios
        print("\nDo you want to create the initial gamified scenarios?")
        response = input("This will add new scenarios to the database (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            create_initial_scenarios()
            print("\nUpdated scenario list:")
            list_scenarios()
        else:
            print("Setup cancelled.")

if __name__ == '__main__':
    main()
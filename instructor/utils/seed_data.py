"""
Utility script to seed sample data for troubleshooting scenarios and topologies.
"""

import sys
import os
from datetime import datetime
import json

# Add parent directories to path so imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import models and database
from __init__ import db, create_app
from instructor.models.troubleshooting import Troubleshooting
from instructor.models.topology import Topology

def seed_troubleshooting():
    """Add sample troubleshooting scenarios to the database."""
    print("Seeding troubleshooting scenarios...")
    
    # Sample troubleshooting data
    troubleshooting_data = [
        {
            'title': 'Network Connectivity Issue',
            'description': 'A client reports that they cannot access the company database server.',
            'difficulty': 'medium',
            'scenario': 'A workstation in the marketing department cannot connect to the database server. Other workstations in the same department can connect without issues. The problem persists after restarting the computer.',
            'solution': 'The workstation has an incorrect subnet mask configured. The correct subnet mask should be 255.255.255.0 instead of 255.255.0.0.',
            'hints': [
                'Check the network configuration on the problematic workstation',
                'Compare the IP configuration with a working workstation in the same department',
                'Look for inconsistencies in subnet mask configuration'
            ],
            'is_active': True
        },
        {
            'title': 'Server Authentication Problem',
            'description': 'Users report being unable to log into the file server.',
            'difficulty': 'hard',
            'scenario': 'Multiple users from different departments cannot authenticate to the file server. The issue started after a scheduled maintenance window last night. The server appears to be online and responding to ping requests.',
            'solution': 'The authentication service on the server is not running. Start the LDAP service and make sure it\'s set to automatic startup.',
            'hints': [
                'Check if all users are affected or only specific departments',
                'Look at what changed during the maintenance window',
                'Check the status of authentication services on the server',
                'Review server logs for authentication failures'
            ],
            'is_active': True
        },
        {
            'title': 'Slow Network Performance',
            'description': 'Users complain about slow network speeds and intermittent connectivity.',
            'difficulty': 'easy',
            'scenario': 'All users on the second floor report slow network performance and occasional disconnects. The issue is not affecting users on other floors.',
            'solution': 'The network switch for the second floor is experiencing high error rates due to a bad cable connection. Replace the uplink cable between the second floor switch and the main distribution switch.',
            'hints': [
                'Check if the issue is isolated to a specific location',
                'Look at the network infrastructure serving the affected area',
                'Check error rates and statistics on network devices',
                'Inspect physical connections between network devices'
            ],
            'is_active': True
        }
    ]
    
    # Check if scenarios already exist
    existing_count = Troubleshooting.query.count()
    if existing_count > 0:
        print(f"Found {existing_count} existing troubleshooting scenarios. Skipping seed.")
        return
        
    # Add scenarios to the database
    for data in troubleshooting_data:
        scenario = Troubleshooting(
            title=data['title'],
            description=data['description'],
            difficulty=data['difficulty'],
            scenario=data['scenario'],
            solution=data['solution'],
            is_active=data['is_active'],
            created_at=datetime.utcnow()
        )
        scenario.hints = data['hints']
        db.session.add(scenario)
    
    db.session.commit()
    print(f"Added {len(troubleshooting_data)} troubleshooting scenarios.")

def seed_topologies():
    """Add sample topology scenarios to the database."""
    print("Seeding topology scenarios...")
    
    # Sample topology data
    topology_data = [
        {
            'title': 'Simple Star Network',
            'description': 'Create a star topology with a central switch and 4 connected devices.',
            'topology_type': 'star',
            'difficulty': 'easy',
            'initial_config': {
                'devices': [
                    {'id': 1, 'label': 'Switch', 'type': 'switch', 'x': 400, 'y': 250}
                ],
                'connections': []
            },
            'expected_config': {
                'devices': [
                    {'id': 1, 'label': 'Switch', 'type': 'switch', 'x': 400, 'y': 250},
                    {'id': 2, 'label': 'PC1', 'type': 'pc', 'x': 250, 'y': 150},
                    {'id': 3, 'label': 'PC2', 'type': 'pc', 'x': 550, 'y': 150},
                    {'id': 4, 'label': 'Server', 'type': 'server', 'x': 250, 'y': 350},
                    {'id': 5, 'label': 'Printer', 'type': 'pc', 'x': 550, 'y': 350}
                ],
                'connections': [
                    {'device1': 'Switch', 'device2': 'PC1'},
                    {'device1': 'Switch', 'device2': 'PC2'},
                    {'device1': 'Switch', 'device2': 'Server'},
                    {'device1': 'Switch', 'device2': 'Printer'}
                ]
            },
            'base_score': 10,
            'time_bonus': 5,
            'perfect_match_bonus': 3,
            'is_active': True
        },
        {
            'title': 'Corporate Network Topology',
            'description': 'Create a corporate network with multiple segments and proper routing.',
            'topology_type': 'hybrid',
            'difficulty': 'hard',
            'initial_config': {
                'devices': [
                    {'id': 1, 'label': 'Router', 'type': 'router', 'x': 400, 'y': 200},
                    {'id': 2, 'label': 'Switch1', 'type': 'switch', 'x': 200, 'y': 300},
                    {'id': 3, 'label': 'Switch2', 'type': 'switch', 'x': 600, 'y': 300}
                ],
                'connections': [
                    {'device1': 'Router', 'device2': 'Switch1'},
                    {'device1': 'Router', 'device2': 'Switch2'}
                ]
            },
            'expected_config': {
                'devices': [
                    {'id': 1, 'label': 'Router', 'type': 'router', 'x': 400, 'y': 200},
                    {'id': 2, 'label': 'Switch1', 'type': 'switch', 'x': 200, 'y': 300},
                    {'id': 3, 'label': 'Switch2', 'type': 'switch', 'x': 600, 'y': 300},
                    {'id': 4, 'label': 'PC1', 'type': 'pc', 'x': 100, 'y': 400},
                    {'id': 5, 'label': 'PC2', 'type': 'pc', 'x': 300, 'y': 400},
                    {'id': 6, 'label': 'Server1', 'type': 'server', 'x': 500, 'y': 400},
                    {'id': 7, 'label': 'Server2', 'type': 'server', 'x': 700, 'y': 400}
                ],
                'connections': [
                    {'device1': 'Router', 'device2': 'Switch1'},
                    {'device1': 'Router', 'device2': 'Switch2'},
                    {'device1': 'Switch1', 'device2': 'PC1'},
                    {'device1': 'Switch1', 'device2': 'PC2'},
                    {'device1': 'Switch2', 'device2': 'Server1'},
                    {'device1': 'Switch2', 'device2': 'Server2'}
                ]
            },
            'base_score': 25,
            'time_bonus': 10,
            'perfect_match_bonus': 15,
            'is_active': True
        },
        {
            'title': 'Mesh Network Configuration',
            'description': 'Create a mesh network where each device connects to every other device.',
            'topology_type': 'mesh',
            'difficulty': 'medium',
            'initial_config': {
                'devices': [
                    {'id': 1, 'label': 'Node1', 'type': 'router', 'x': 200, 'y': 200},
                    {'id': 2, 'label': 'Node2', 'type': 'router', 'x': 400, 'y': 200},
                    {'id': 3, 'label': 'Node3', 'type': 'router', 'x': 300, 'y': 350}
                ],
                'connections': []
            },
            'expected_config': {
                'devices': [
                    {'id': 1, 'label': 'Node1', 'type': 'router', 'x': 200, 'y': 200},
                    {'id': 2, 'label': 'Node2', 'type': 'router', 'x': 400, 'y': 200},
                    {'id': 3, 'label': 'Node3', 'type': 'router', 'x': 300, 'y': 350},
                    {'id': 4, 'label': 'Node4', 'type': 'router', 'x': 500, 'y': 350}
                ],
                'connections': [
                    {'device1': 'Node1', 'device2': 'Node2'},
                    {'device1': 'Node1', 'device2': 'Node3'},
                    {'device1': 'Node1', 'device2': 'Node4'},
                    {'device1': 'Node2', 'device2': 'Node3'},
                    {'device1': 'Node2', 'device2': 'Node4'},
                    {'device1': 'Node3', 'device2': 'Node4'}
                ]
            },
            'base_score': 15,
            'time_bonus': 8,
            'perfect_match_bonus': 10,
            'is_active': True
        }
    ]
    
    # Check if topologies already exist
    existing_count = Topology.query.count()
    if existing_count > 0:
        print(f"Found {existing_count} existing topologies. Skipping seed.")
        return
        
    # Add topologies to the database
    for data in topology_data:
        topology = Topology(
            title=data['title'],
            description=data['description'],
            topology_type=data['topology_type'],
            difficulty=data['difficulty'],
            initial_config=data['initial_config'],
            expected_config=data['expected_config'],
            base_score=data['base_score'],
            time_bonus=data['time_bonus'],
            perfect_match_bonus=data['perfect_match_bonus'],
            is_active=data['is_active'],
            created_at=datetime.utcnow()
        )
        db.session.add(topology)
    
    db.session.commit()
    print(f"Added {len(topology_data)} topology scenarios.")

def main():
    """Main function to seed all data."""
    app = create_app()
    with app.app_context():
        print("Starting data seeding...")
        seed_troubleshooting()
        seed_topologies()
        print("Data seeding completed successfully!")

if __name__ == "__main__":
    main()

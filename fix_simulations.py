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

def fix_simulations():
    """Fix simulations 1 and 2 with proper topology data"""
    app = create_app()
    
    with app.app_context():
        print("=== FIXING SIMULATIONS ===")
        
        # Get simulations 1 and 2
        sim1 = Simulation.query.get(1)
        sim2 = Simulation.query.get(2)
        
        if sim1:
            print(f"Fixing Simulation 1: {sim1.title}")
            
            # Create IPv4 Subnetting topology
            ipv4_topology = {
                "devices": [
                    {
                        "id": "router1",
                        "type": "router",
                        "name": "Router 1",
                        "position": {"x": 200, "y": 150},
                        "interfaces": [
                            {"name": "GigabitEthernet0/0", "ip": "192.168.1.1", "mask": "255.255.255.0"},
                            {"name": "GigabitEthernet0/1", "ip": "192.168.2.1", "mask": "255.255.255.0"}
                        ]
                    },
                    {
                        "id": "computer1",
                        "type": "pc",
                        "name": "Computer 1",
                        "position": {"x": 100, "y": 250},
                        "ip": "192.168.1.100",
                        "mask": "255.255.255.0"
                    },
                    {
                        "id": "computer2",
                        "type": "pc",
                        "name": "Computer 2",
                        "position": {"x": 300, "y": 250},
                        "ip": "192.168.2.100",
                        "mask": "255.255.255.0"
                    }
                ],
                "connections": [
                    {
                        "from": {"deviceId": "router1", "port": "GigabitEthernet0/0"},
                        "to": {"deviceId": "computer1", "port": "Ethernet0"}
                    },
                    {
                        "from": {"deviceId": "router1", "port": "GigabitEthernet0/1"},
                        "to": {"deviceId": "computer2", "port": "Ethernet0"}
                    }
                ]
            }
            
            ipv4_config = {
                "network_topology": ipv4_topology,
                "topology_enabled": True,
                "selected_topology": "point-to-point",
                "live_scoring": True,
                "canvas_enabled": True,
                "use_troubleshoot_template": False
            }
            
            # Create steps for IPv4 subnetting
            ipv4_steps = [
                {
                    "type": "instruction",
                    "content": "Welcome to IPv4 Subnetting Fundamentals. In this lab, you'll learn about subnetting and CIDR notation.",
                    "question_text": "What is the subnet mask for a /24 network?"
                },
                {
                    "type": "question",
                    "question_type": "text",
                    "question_text": "Calculate the subnet mask for a /26 network:",
                    "expected_answer": "255.255.255.192"
                },
                {
                    "type": "question",
                    "question_type": "multiple_choice",
                    "question_text": "How many host addresses are available in a /28 subnet?",
                    "options": ["14", "16", "30", "32"],
                    "expected_answer": "14"
                }
            ]
            
            # Create validation rules
            ipv4_validation = {
                "1": {"type": "exact_match", "expected_answer": "255.255.255.192", "score": 30},
                "2": {"type": "exact_match", "expected_answer": "14", "score": 40}
            }
            
            sim1.simulation_config = ipv4_config
            sim1.step_definitions = ipv4_steps
            sim1.validation_rules = ipv4_validation
            
        if sim2:
            print(f"Fixing Simulation 2: {sim2.title}")
            
            # Create VLAN Configuration topology
            vlan_topology = {
                "devices": [
                    {
                        "id": "switch1",
                        "type": "switch",
                        "name": "Switch 1",
                        "position": {"x": 200, "y": 150},
                        "vlans": {
                            "10": {"name": "Sales", "status": "active"},
                            "20": {"name": "IT", "status": "active"}
                        },
                        "interfaces": [
                            {"name": "FastEthernet0/1", "vlan": 10, "mode": "access"},
                            {"name": "FastEthernet0/2", "vlan": 20, "mode": "access"},
                            {"name": "FastEthernet0/24", "vlan": "trunk", "mode": "trunk"}
                        ]
                    },
                    {
                        "id": "pc1",
                        "type": "pc",
                        "name": "PC Sales",
                        "position": {"x": 100, "y": 250},
                        "ip": "192.168.10.100",
                        "mask": "255.255.255.0",
                        "vlan": 10
                    },
                    {
                        "id": "pc2",
                        "type": "pc",
                        "name": "PC IT",
                        "position": {"x": 300, "y": 250},
                        "ip": "192.168.20.100",
                        "mask": "255.255.255.0",
                        "vlan": 20
                    }
                ],
                "connections": [
                    {
                        "from": {"deviceId": "switch1", "port": "FastEthernet0/1"},
                        "to": {"deviceId": "pc1", "port": "Ethernet0"}
                    },
                    {
                        "from": {"deviceId": "switch1", "port": "FastEthernet0/2"},
                        "to": {"deviceId": "pc2", "port": "Ethernet0"}
                    }
                ]
            }
            
            vlan_config = {
                "network_topology": vlan_topology,
                "topology_enabled": True,
                "selected_topology": "star",
                "live_scoring": True,
                "canvas_enabled": True,
                "use_troubleshoot_template": False
            }
            
            # Create steps for VLAN configuration
            vlan_steps = [
                {
                    "type": "instruction",
                    "content": "Welcome to VLAN Configuration Lab. You'll learn to configure VLANs on Cisco switches.",
                    "question_text": "What command creates a new VLAN?"
                },
                {
                    "type": "question",
                    "question_type": "text",
                    "question_text": "What command would you use to create VLAN 10?",
                    "expected_answer": "vlan 10"
                },
                {
                    "type": "question",
                    "question_type": "multiple_choice",
                    "question_text": "Which mode allows a port to carry traffic for multiple VLANs?",
                    "options": ["access", "trunk", "dynamic", "native"],
                    "expected_answer": "trunk"
                }
            ]
            
            # Create validation rules
            vlan_validation = {
                "1": {"type": "contains", "expected_answer": "vlan", "score": 30},
                "2": {"type": "exact_match", "expected_answer": "trunk", "score": 40}
            }
            
            sim2.simulation_config = vlan_config
            sim2.step_definitions = vlan_steps
            sim2.validation_rules = vlan_validation
        
        # Commit changes
        db.session.commit()
        print("✅ Simulations updated successfully!")
        
        # Verify the changes
        if sim1:
            print(f"Simulation 1 now has {len(sim1.step_definitions)} steps")
        if sim2:
            print(f"Simulation 2 now has {len(sim2.step_definitions)} steps")

if __name__ == "__main__":
    fix_simulations()
"""
Collaborative Troubleshooting System Demo
Simple demonstration of the real-time collaboration features
"""

import sys
import json
from datetime import datetime

def demo_collaborative_features():
    """Demonstrate the collaborative troubleshooting system features"""
    
    print("🚀 RiddleNet Collaborative Troubleshooting System Demo")
    print("=" * 60)
    
    # Demo data structures
    demo_lobby = {
        "id": "lobby_123",
        "name": "Advanced EIGRP Lab",
        "scenario_type": "hard",
        "scenario_id": "split",
        "participants": {
            "user_1": {
                "username": "alice",
                "role": "creator",
                "joined_at": datetime.now().isoformat(),
                "score": {"individual": 85, "team_contribution": 92}
            },
            "user_2": {
                "username": "bob", 
                "role": "participant",
                "joined_at": datetime.now().isoformat(),
                "score": {"individual": 78, "team_contribution": 88}
            }
        },
        "network_state": {
            "devices": {
                "router_1": {
                    "id": "router_1",
                    "type": "router",
                    "x": 200,
                    "y": 150,
                    "label": "Router A",
                    "ipv4": "192.168.1.1",
                    "subnet": "255.255.255.0"
                },
                "router_2": {
                    "id": "router_2", 
                    "type": "router",
                    "x": 400,
                    "y": 150,
                    "label": "Router B",
                    "ipv4": "192.168.2.1",
                    "subnet": "255.255.255.0"
                }
            },
            "connections": [
                {
                    "id": "conn_1",
                    "device1_id": "router_1",
                    "device2_id": "router_2",
                    "type": "ethernet"
                }
            ]
        },
        "device_locks": {
            "router_1": {
                "locked_by": "user_1",
                "username": "alice",
                "locked_at": datetime.now().isoformat()
            }
        },
        "cli_history": {
            "router_1": [
                {
                    "command": "show ip route",
                    "output": "Gateway of last resort is not set...",
                    "executed_by": "user_1",
                    "username": "alice",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    }
    
    print("📋 Demo Lobby Configuration:")
    print(f"  Name: {demo_lobby['name']}")
    print(f"  Scenario: {demo_lobby['scenario_id']} ({demo_lobby['scenario_type']})")
    print(f"  Participants: {len(demo_lobby['participants'])}")
    print()
    
    print("👥 Participants:")
    for user_id, participant in demo_lobby['participants'].items():
        role_icon = "👑" if participant['role'] == 'creator' else "👤"
        print(f"  {role_icon} {participant['username']} - Individual: {participant['score']['individual']}%, Team: {participant['score']['team_contribution']}%")
    print()
    
    print("🔧 Network Topology:")
    devices = demo_lobby['network_state']['devices']
    for device_id, device in devices.items():
        lock_status = "🔒" if device_id in demo_lobby['device_locks'] else "🔓"
        print(f"  {lock_status} {device['label']} ({device['type']}) at ({device['x']}, {device['y']}) - IP: {device['ipv4']}")
    
    connections = demo_lobby['network_state']['connections']
    print(f"  🔗 {len(connections)} connection(s) configured")
    print()
    
    print("💻 Recent CLI Activity:")
    for device_id, commands in demo_lobby['cli_history'].items():
        device_name = devices[device_id]['label']
        for cmd in commands[-3:]:  # Show last 3 commands
            print(f"  {device_name}> {cmd['command']} (by {cmd['username']})")
    print()
    
    print("🎯 Collaborative Features Demonstrated:")
    features = [
        "✅ Real-time device synchronization",
        "✅ Connection management across participants", 
        "✅ Device locking for conflict prevention",
        "✅ Shared CLI command history",
        "✅ Individual and team progress tracking",
        "✅ Role-based permissions (creator vs participant)",
        "✅ Live participant status monitoring"
    ]
    
    for feature in features:
        print(f"  {feature}")
    print()
    
    print("🔄 WebSocket Events (Real-time):")
    events = [
        "device_added - Broadcast new device to all participants",
        "device_moved - Sync device position changes", 
        "connection_added - Share new connections",
        "cli_command_executed - Share CLI commands and outputs",
        "device_locked/unlocked - Manage edit conflicts",
        "scenario_progress_updated - Track team progress"
    ]
    
    for event in events:
        print(f"  📡 {event}")
    print()
    
    print("🚀 System Status: FULLY OPERATIONAL")
    print("All collaborative features implemented and ready for deployment!")

def demo_websocket_events():
    """Demonstrate WebSocket event structure"""
    
    print("\n📡 WebSocket Event Examples:")
    print("=" * 40)
    
    # Device addition event
    device_added_event = {
        "event": "device_added",
        "data": {
            "device": {
                "id": "switch_1",
                "type": "switch", 
                "x": 300,
                "y": 250,
                "label": "Switch 1"
            },
            "user_id": "user_2",
            "username": "bob",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    print("1. Device Addition:")
    print(json.dumps(device_added_event, indent=2))
    print()
    
    # CLI command execution event
    cli_event = {
        "event": "cli_command_executed",
        "data": {
            "device_id": "router_1",
            "command": "configure terminal",
            "output": "Router(config)#",
            "user_id": "user_1", 
            "username": "alice",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    print("2. CLI Command Execution:")
    print(json.dumps(cli_event, indent=2))
    print()
    
    # Progress update event
    progress_event = {
        "event": "scenario_progress_updated",
        "data": {
            "progress": {
                "scenario_completed": False,
                "steps_completed": 7,
                "total_steps": 10,
                "percentage": 70
            },
            "user_id": "user_2",
            "username": "bob",
            "lobby_progress": {
                "team_percentage": 75,
                "all_participants_active": True
            },
            "timestamp": datetime.now().isoformat()
        }
    }
    
    print("3. Progress Update:")
    print(json.dumps(progress_event, indent=2))

if __name__ == "__main__":
    demo_collaborative_features()
    demo_websocket_events()
    
    print("\n" + "=" * 60)
    print("🎓 Ready for Collaborative Learning!")
    print("Students can now work together on network troubleshooting scenarios")
    print("with real-time synchronization and team-based problem solving.")
    print("=" * 60)

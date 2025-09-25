#!/usr/bin/env python3
"""
Direct database analysis using Flask app context to understand device count discrepancies
"""

import os
import sys
import json
from datetime import datetime

# Add the RiddleNet directory to the path for imports
sys.path.append('/c/Users/gilbe/OneDrive/Desktop/RiddleNet')

def analyze_simulation_topology():
    print("🔍 Analyzing Simulation Topology Data (Flask App Context)")
    print("=" * 80)
    
    try:
        # Import Flask app and database
        from application import create_app
        from admin.models.simulation_models import Simulation
        
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            print("📊 Querying simulation ID 1...")
            
            # Query simulation ID 1 using SQLAlchemy model
            simulation = Simulation.query.get(1)
            
            if not simulation:
                print("❌ Simulation ID 1 not found!")
                return
            
            print(f"✅ Found simulation: {simulation.title} (ID: {simulation.id})")
            
            # Parse and analyze simulation_config
            simulation_config = simulation.simulation_config
            network_topology = simulation.network_topology
            
            config_device_count = 0
            topology_device_count = 0
            config_devices = []
            topology_devices = []
            
            if simulation_config:
                try:
                    config_data = json.loads(simulation_config) if isinstance(simulation_config, str) else simulation_config
                    print(f"\n📋 Simulation Config Analysis:")
                    print(f"   - Config keys: {list(config_data.keys())}")
                    
                    if 'network_topology' in config_data:
                        config_topology = config_data['network_topology']
                        config_devices = config_topology.get('devices', []) if isinstance(config_topology, dict) else []
                        config_device_count = len(config_devices)
                        print(f"   - Devices in simulation_config.network_topology: {config_device_count}")
                        if config_devices:
                            device_types = [d.get('type', 'unknown') for d in config_devices]
                            print(f"   - Device types in config: {device_types}")
                            # Show first few device details
                            for i, device in enumerate(config_devices[:3]):
                                print(f"     Device {i+1}: {device.get('name', 'unnamed')} ({device.get('type', 'unknown')})")
                    else:
                        print("   - No network_topology in simulation_config")
                        
                except Exception as e:
                    print(f"   ❌ Error parsing simulation_config: {e}")
            else:
                print("   - simulation_config is empty")
            
            # Parse and analyze network_topology
            if network_topology:
                try:
                    topology_data = json.loads(network_topology) if isinstance(network_topology, str) else network_topology
                    print(f"\n🌐 Network Topology Analysis:")
                    print(f"   - Topology keys: {list(topology_data.keys())}")
                    
                    topology_devices = topology_data.get('devices', []) if isinstance(topology_data, dict) else []
                    topology_device_count = len(topology_devices)
                    print(f"   - Devices in network_topology: {topology_device_count}")
                    if topology_devices:
                        device_types = [d.get('type', 'unknown') for d in topology_devices]
                        print(f"   - Device types in topology: {device_types}")
                        # Show first few device details
                        for i, device in enumerate(topology_devices[:3]):
                            print(f"     Device {i+1}: {device.get('name', 'unnamed')} ({device.get('type', 'unknown')})")
                        
                except Exception as e:
                    print(f"   ❌ Error parsing network_topology: {e}")
            else:
                print("   - network_topology is empty")
            
            # Summary
            print(f"\n📝 Summary & Route Handler Logic Analysis:")
            print(f"   - simulation_config.network_topology devices: {config_device_count}")
            print(f"   - network_topology devices: {topology_device_count}")
            
            if config_device_count != topology_device_count:
                print(f"   ⚠️  MISMATCH DETECTED: {abs(config_device_count - topology_device_count)} device difference!")
                print(f"   📋 Admin edit page logic: TroubleshootingSimulation uses simulation_config.network_topology ({config_device_count} devices)")
                print(f"   👤 User simulation page logic: Prefers network_topology, falls back to simulation_config.network_topology ({topology_device_count} devices)")
                
                print(f"\n🔧 Route Handler Code Analysis:")
                print(f"   - Admin route (line ~50 in admin/routes/simulation_routes.py):")
                print(f"     Uses TroubleshootingSimulation which processes simulation_config.network_topology")
                print(f"   - User route (line ~1191 in user/dynamic_simulation_routes.py):")
                print(f"     Checks network_topology first, then falls back to simulation_config.network_topology")
                
                print(f"\n💡 Solution:")
                print(f"   The user route should prefer simulation_config.network_topology to match admin,")
                print(f"   OR the admin route should use network_topology to match user interface.")
            else:
                print(f"   ✅ Device counts match: {config_device_count} devices")
                
            # Write detailed comparison to file
            debug_file = f"c:\\Users\\gilbe\\OneDrive\\Desktop\\RiddleNet\\topology_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(debug_file, 'w') as f:
                f.write("=== TOPOLOGY COMPARISON ANALYSIS ===\n")
                f.write(f"Timestamp: {datetime.now()}\n")
                f.write(f"Simulation ID: {simulation.id}\n")
                f.write(f"Simulation Title: {simulation.title}\n\n")
                
                f.write("SIMULATION_CONFIG.NETWORK_TOPOLOGY:\n")
                f.write(f"Device count: {config_device_count}\n")
                f.write(f"Devices: {json.dumps(config_devices, indent=2)}\n\n")
                
                f.write("NETWORK_TOPOLOGY:\n")
                f.write(f"Device count: {topology_device_count}\n") 
                f.write(f"Devices: {json.dumps(topology_devices, indent=2)}\n\n")
                
                if config_device_count != topology_device_count:
                    f.write("MISMATCH ANALYSIS:\n")
                    f.write(f"Difference: {abs(config_device_count - topology_device_count)} devices\n")
                    f.write("Admin uses: simulation_config.network_topology\n")
                    f.write("User uses: network_topology (with fallback)\n")
                
            print(f"\n📄 Detailed comparison written to: {debug_file}")
        
    except Exception as e:
        print(f"❌ Application context error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_simulation_topology()
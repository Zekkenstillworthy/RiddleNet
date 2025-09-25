#!/usr/bin/env python3
"""
Direct database analysis to understand device count discrepancies
"""

import os
import sys
import psycopg2
import json
from datetime import datetime

# Add the RiddleNet directory to the path for imports
sys.path.append('/c/Users/gilbe/OneDrive/Desktop/RiddleNet')

def analyze_simulation_topology():
    print("🔍 Analyzing Simulation Topology Data (Direct Database Access)")
    print("=" * 80)
    
    try:
        # Connect to PostgreSQL database (using same config as the app)
        conn = psycopg2.connect(
            host="localhost",
            database="riddlenet",
            user="postgres", 
            password=""
        )
        cursor = conn.cursor()
        
        # Query simulation ID 1
        print("📊 Querying simulation ID 1...")
        cursor.execute("""
            SELECT id, title, simulation_config, network_topology
            FROM simulations 
            WHERE id = 1
        """)
        
        result = cursor.fetchone()
        if not result:
            print("❌ Simulation ID 1 not found!")
            return
        
        sim_id, title, simulation_config, network_topology = result
        print(f"✅ Found simulation: {title} (ID: {sim_id})")
        
        # Parse and analyze simulation_config
        if simulation_config:
            try:
                config_data = json.loads(simulation_config) if isinstance(simulation_config, str) else simulation_config
                print(f"\n📋 Simulation Config Analysis:")
                print(f"   - Config keys: {list(config_data.keys())}")
                
                if 'network_topology' in config_data:
                    config_topology = config_data['network_topology']
                    config_devices = config_topology.get('devices', []) if isinstance(config_topology, dict) else []
                    print(f"   - Devices in simulation_config.network_topology: {len(config_devices)}")
                    if config_devices:
                        device_types = [d.get('type', 'unknown') for d in config_devices]
                        print(f"   - Device types in config: {device_types}")
                else:
                    print("   - No network_topology in simulation_config")
                    
            except json.JSONDecodeError as e:
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
                print(f"   - Devices in network_topology: {len(topology_devices)}")
                if topology_devices:
                    device_types = [d.get('type', 'unknown') for d in topology_devices]
                    print(f"   - Device types in topology: {device_types}")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ Error parsing network_topology: {e}")
        else:
            print("   - network_topology is empty")
        
        # Summary
        print(f"\n📝 Summary:")
        config_device_count = 0
        topology_device_count = 0
        
        if simulation_config:
            try:
                config_data = json.loads(simulation_config) if isinstance(simulation_config, str) else simulation_config
                if 'network_topology' in config_data and isinstance(config_data['network_topology'], dict):
                    config_device_count = len(config_data['network_topology'].get('devices', []))
            except:
                pass
        
        if network_topology:
            try:
                topology_data = json.loads(network_topology) if isinstance(network_topology, str) else network_topology
                topology_device_count = len(topology_data.get('devices', [])) if isinstance(topology_data, dict) else 0
            except:
                pass
        
        print(f"   - simulation_config.network_topology devices: {config_device_count}")
        print(f"   - network_topology devices: {topology_device_count}")
        
        if config_device_count != topology_device_count:
            print(f"   ⚠️  MISMATCH DETECTED: {abs(config_device_count - topology_device_count)} device difference!")
            print(f"   📋 Admin edit page uses: simulation_config.network_topology ({config_device_count} devices)")
            print(f"   👤 User simulation page uses: network_topology OR falls back to simulation_config ({topology_device_count} devices)")
        else:
            print(f"   ✅ Device counts match: {config_device_count} devices")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("💡 This may be because PostgreSQL is not running or credentials are incorrect")

if __name__ == "__main__":
    analyze_simulation_topology()
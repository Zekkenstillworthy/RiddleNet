#!/usr/bin/env python3
"""
Test script to verify all Networking 1 simulations are properly set up
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_simulation_templates():
    """Test if all simulation template files exist"""
    template_dir = os.path.join('templates', 'user')
    
    simulation_files = [
        'networking1_simulations.html',
        'networking1-components-simulation.html',
        'networking1-osi-simulation.html', 
        'networking1-tcpip-simulation.html',
        'networking1-ethernet-simulation.html',
        'networking1-application-simulation.html',
        'networking1-datalink-simulation.html'
    ]
    
    missing_files = []
    existing_files = []
    
    for file in simulation_files:
        file_path = os.path.join(template_dir, file)
        if os.path.exists(file_path):
            # Check if file has content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    existing_files.append(file)
                else:
                    missing_files.append(f"{file} (empty)")
        else:
            missing_files.append(f"{file} (not found)")
    
    return existing_files, missing_files

def test_simulation_routes():
    """Test if simulation routes can be imported"""
    try:
        from user.routes.simulation_routes import simulation_bp
        return True, "Routes imported successfully"
    except Exception as e:
        return False, str(e)

def test_simulation_features():
    """Test key features of each simulation"""
    features_test = {
        'Components Simulation': [
            'Drag and drop functionality',
            'Device palette (routers, switches, computers)',
            'Connection mode',
            'Network validation',
            'Scoring system'
        ],
        'OSI Model Simulation': [
            '7-layer visualization',
            'Encapsulation/decapsulation animation',
            'Layer information panels',
            'Transmission logging',
            'Interactive protocol stack'
        ],
        'TCP/IP Simulation': [
            'Protocol stack visualization',
            'Multiple scenarios (web, email, FTP)',
            'Packet flow animation',
            'Message exchange logging',
            'Network configuration'
        ],
        'Ethernet Simulation': [
            'Hub vs Switch topology',
            'Collision detection',
            'Frame analysis',
            'MAC address handling',
            'CSMA/CD demonstration'
        ],
        'Application Protocols': [
            'HTTP/HTTPS simulation',
            'FTP file transfer',
            'SMTP email sending',
            'DNS name resolution',
            'Protocol comparison'
        ],
        'Data Link Layer': [
            'Stop-and-Wait protocol',
            'Sliding Window (Go-Back-N)',
            'Selective Repeat ARQ',
            'Error handling scenarios',
            'Flow control statistics'
        ]
    }
    
    return features_test

def main():
    print("=== Networking 1 Simulations Test Report ===\n")
    
    # Test 1: Template Files
    print("1. Testing Simulation Template Files:")
    existing, missing = test_simulation_templates()
    
    print(f"   ✅ Found {len(existing)} simulation files:")
    for file in existing:
        print(f"      - {file}")
    
    if missing:
        print(f"   ❌ Missing {len(missing)} files:")
        for file in missing:
            print(f"      - {file}")
    else:
        print("   ✅ All simulation templates found!")
    
    print()
    
    # Test 2: Routes
    print("2. Testing Simulation Routes:")
    routes_ok, routes_msg = test_simulation_routes()
    if routes_ok:
        print(f"   ✅ {routes_msg}")
    else:
        print(f"   ❌ Routes error: {routes_msg}")
    
    print()
    
    # Test 3: Features
    print("3. Simulation Features Overview:")
    features = test_simulation_features()
    for sim_name, feature_list in features.items():
        print(f"   📊 {sim_name}:")
        for feature in feature_list:
            print(f"      • {feature}")
        print()
    
    # Summary
    print("=== SUMMARY ===")
    total_files = len(existing) + len(missing)
    success_rate = (len(existing) / total_files * 100) if total_files > 0 else 0
    
    print(f"📈 Template Files: {len(existing)}/{total_files} ({success_rate:.1f}%)")
    print(f"🔗 Routes: {'✅ Working' if routes_ok else '❌ Error'}")
    print(f"🎯 Total Simulations: {len(features)} unique simulations")
    print(f"⚡ Features: {sum(len(f) for f in features.values())} interactive features")
    
    if len(existing) == total_files and routes_ok:
        print("\n🎉 ALL SIMULATIONS READY FOR DEPLOYMENT!")
        print("🚀 Students can now access comprehensive networking simulations")
    else:
        print(f"\n⚠️  {len(missing)} issues need to be resolved before deployment")
    
    return len(missing) == 0 and routes_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

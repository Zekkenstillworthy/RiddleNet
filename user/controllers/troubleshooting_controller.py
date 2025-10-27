from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from instructor.models.troubleshooting import Troubleshooting
from instructor.models.troubleshooting_progress import TroubleshootingProgress
from __init__ import db
from datetime import datetime
import json
import numpy as np

class TroubleshootingController:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # The controller doesn't directly register routes, this is done in run.py
        # using the blueprint from user.routes.troubleshooting_routes
        pass

    def get_active_scenarios(self):
        """Get all active troubleshooting scenarios"""
        return Troubleshooting.query.filter_by(is_active=True).all()
    
    def get_scenario_by_id(self, scenario_id):
        """Get scenario by ID without exposing solutions"""
        scenario = Troubleshooting.query.get_or_404(scenario_id)
        scenario_data = scenario.to_dict()
        
        # Don't send sensitive data to client
        if 'solution' in scenario_data:
            del scenario_data['solution']
            
        if 'expected_topology' in scenario_data:
            del scenario_data['expected_topology']
        
        return scenario_data
        
    def submit_solution(self, user_id, data):
        """Submit a solution for scoring"""
        print("\n" + "="*80)
        print("🚀 BACKEND: SOLUTION SUBMISSION RECEIVED")
        print("="*80)
        print(f"[USER] User ID: {user_id}")
        print(f"📦 Data keys: {list(data.keys()) if data else 'None'}")
        
        if not data or 'scenario_id' not in data or 'user_solution' not in data:
            print("[ERROR] ERROR: Missing required fields!")
            print(f"   - Has scenario_id: {'scenario_id' in data if data else False}")
            print(f"   - Has user_solution: {'user_solution' in data if data else False}")
            return {"error": "Missing required fields"}, 400
        
        scenario_id = data['scenario_id']
        user_solution = data['user_solution']
        time_taken = data.get('time_taken', 0)
        
        print(f"[KEY] Scenario ID: '{scenario_id}'")
        print(f"⏱️  Time Taken: {time_taken} seconds")
        print(f"📊 Solution has {len(user_solution.get('devices', []))} devices")
        print("="*80 + "\n")
        
        # Check if this is a hardcoded Link Up challenge (not from database)
        # Convention: All hardcoded challenges use STRING IDs; DB scenarios use INTEGER IDs.
        # To avoid DB type mismatches and 500s, short-circuit all string IDs to hardcoded handler.
        if isinstance(scenario_id, str):
            print(f"🎯 Detected string-based scenario id -> treating as hardcoded: {scenario_id}")
            return self._submit_hardcoded_challenge(user_id, scenario_id, user_solution, time_taken)

        # Get the scenario from database (for integer IDs only)
        try:
            print(f"[DEBUG] Looking up database scenario with ID: {scenario_id}")
            scenario = Troubleshooting.query.get(scenario_id)
        except Exception as e:
            # If any error occurs during DB lookup, fall back to hardcoded submission path
            print(f"[WARNING] DB lookup error for scenario_id={scenario_id}: {e}")
            import traceback
            traceback.print_exc()
            return self._submit_hardcoded_challenge(user_id, scenario_id, user_solution, time_taken)

        if not scenario:
            # If not found in database, try as hardcoded challenge
            return self._submit_hardcoded_challenge(user_id, scenario_id, user_solution, time_taken)
        
        # Calculate match percentage
        match_percentage = self.calculate_match_percentage(user_solution, scenario.expected_topology)
        
        # Calculate score
        base_score = scenario.base_score
        
        # Time bonus calculation
        time_bonus = 0
        if time_taken > 0:
            max_time = 15 * 60  # 15 minutes in seconds
            min_time = 5 * 60   # 5 minutes in seconds
            
            if time_taken <= min_time:
                time_bonus = scenario.time_bonus
            elif time_taken < max_time:
                # Scale linearly between min and max time
                time_bonus = int(scenario.time_bonus * (max_time - time_taken) / (max_time - min_time))
        
        # Match score based on topology match percentage
        match_score = int(scenario.perfect_match_bonus * (match_percentage / 100))
        
        # Calculate total score
        total_score = base_score + time_bonus + match_score
        
        # Save the progress
        progress = TroubleshootingProgress(
            user_id=user_id,
            troubleshooting_id=scenario_id,
            score=total_score,
            time_taken=time_taken,
            is_completed=True,
            topology_match_percentage=match_percentage,
            user_solution=user_solution
        )
        
        # Check if this is a retry
        existing_progress = TroubleshootingProgress.query.filter_by(
            user_id=user_id,
            troubleshooting_id=scenario_id
        ).first()
        
        if existing_progress:
            progress.attempts = existing_progress.attempts + 1
        
        # Save to database
        db.session.add(progress)
        
        # Save to new ChallengeScore table (MVP)
        # Use match_percentage (0-100) which is already normalized
        from user.models.challenge_score import ChallengeScore
        challenge_score = ChallengeScore.save_score(
            user_id=user_id,
            challenge_type='troubleshooting',
            score=match_percentage,  # Already normalized 0-100 percentage
            metadata={
                'scenario_id': scenario.id,
                'time_taken': time_taken,
                'attempts': progress.attempts
            },
            completion_time=time_taken
        )
        
        # Check and award badges (MVP)
        from user.services.badge_service import BadgeService
        newly_earned_badges = BadgeService.check_and_award_badges(
            user_id=user_id,
            challenge_type='troubleshooting',
            score=match_percentage,
            metadata={'scenario_id': scenario.id}
        )
        
        db.session.commit()
        
        # Generate feedback based on match percentage
        feedback = self.generate_feedback(match_percentage, scenario)
        
        # Prepare response
        response = {
            "score": total_score,
            "base_score": base_score,
            "time_bonus": time_bonus,
            "match_score": match_score,
            "topology_match_percentage": match_percentage,
            "feedback": feedback,
            "expected_topology": scenario.expected_topology,  # Now share the expected topology
            "badges_earned": newly_earned_badges,
            "challenge_completed": challenge_score.is_completed
        }
        
        return response

    def calculate_match_percentage(self, user_solution, expected_solution):
        """Calculate match percentage between two topologies"""
        try:
            # Device count comparison
            user_devices = len(user_solution.get('devices', []))
            expected_devices = len(expected_solution.get('devices', []))
            device_count_match = min(user_devices / max(1, expected_devices), 1.0) if expected_devices > 0 else 0
            
            # Connection count comparison
            user_connections = len(user_solution.get('connections', []))
            expected_connections = len(expected_solution.get('connections', []))
            connection_count_match = min(user_connections / max(1, expected_connections), 1.0) if expected_connections > 0 else 0
            
            # For now, use a simple weighted average
            match_percentage = (device_count_match * 0.4 + connection_count_match * 0.6) * 100
            return round(match_percentage, 1)
        except Exception as e:
            print(f"Error calculating match percentage: {e}")
            return 0.0

    def generate_feedback(self, match_percentage, scenario):
        """Generate feedback based on match percentage"""
        if match_percentage >= 90:
            return f"""
            <p class="success">Excellent work! Your solution is very close to the expected one.</p>
            <p>You've demonstrated a strong understanding of the scenario and how to resolve it properly.</p>
            <p>Here's the correct approach:</p>
            <div class="solution-steps">{scenario.solution}</div>
            """
        elif match_percentage >= 70:
            return f"""
            <p class="good">Good job! Your solution addresses most of the key issues.</p>
            <p>There are a few small differences between your solution and the ideal approach.</p>
            <p>Here's the correct approach:</p>
            <div class="solution-steps">{scenario.solution}</div>
            """
        elif match_percentage >= 50:
            return f"""
            <p class="warning">You're on the right track, but there are some important differences.</p>
            <p>Review the scenario requirements carefully and compare your solution with the expected one.</p>
            <p>Here's the correct approach:</p>
            <div class="solution-steps">{scenario.solution}</div>
            """
        else:
            return f"""
            <p class="danger">There are significant differences between your solution and the expected one.</p>
            <p>Take some time to review the scenario requirements and the expected solution.</p>
            <p>Here's the correct approach:</p>
            <div class="solution-steps">{scenario.solution}</div>
            """

    def get_user_progress(self, user_id):
        """Get user's progress on troubleshooting scenarios"""
        progress = TroubleshootingProgress.query.filter_by(user_id=user_id).all()
        return progress
    
    def _submit_hardcoded_challenge(self, user_id, scenario_id, user_solution, time_taken):
        """Handle hardcoded Link Up challenges (vlan-basics, default-gateway, etc.)"""
        try:
            # Define hardcoded challenge metadata
            challenge_metadata = {
                'vlan-basics': {
                    'name': 'VLAN Setup Basics',
                    'difficulty': 'easy',
                    'base_score': 100,
                    'description': 'Configure VLANs 10 (Sales) and 20 (Engineering) on the switch'
                },
                'default-gateway': {
                    'name': 'Default Gateway Configuration',
                    'difficulty': 'easy',
                    'base_score': 100,
                    'description': 'Configure default gateways for network devices'
                },
                'default-gateway-setup': {  # Alternative name for same challenge
                    'name': 'Default Gateway Configuration',
                    'difficulty': 'easy',
                    'base_score': 100,
                    'description': 'Configure default gateways for network devices'
                },
                'dhcp-client': {
                    'name': 'DHCP Client Configuration',
                    'difficulty': 'easy',
                    'base_score': 100,
                    'description': 'Configure DHCP clients to obtain IP addresses automatically'
                },
                'dhcp-client-config': {  # Alternative name for same challenge
                    'name': 'DHCP Client Configuration',
                    'difficulty': 'easy',
                    'base_score': 100,
                    'description': 'Configure DHCP clients to obtain IP addresses automatically'
                },
                'extended-ring-redundancy': {
                    'name': 'Extended Ring with Redundancy',
                    'difficulty': 'medium',
                    'base_score': 200,
                    'description': 'Create two ring networks connected by a bridge switch with redundant paths'
                },
                'hybrid-star-ring': {
                    'name': 'Hybrid Star-Ring Topology',
                    'difficulty': 'medium',
                    'base_score': 200,
                    'description': 'Combine star and ring topologies with a central switch connecting to a ring network'
                },
                'partial-mesh-ospf': {
                    'name': 'Partial Mesh OSPF Network',
                    'difficulty': 'medium',
                    'base_score': 200,
                    'description': 'Configure a partial mesh topology with OSPF multi-area routing'
                },
                'mpls-vpn-complex': {
                    'name': 'MPLS VPN Route Leaking',
                    'difficulty': 'hard',
                    'base_score': 300,
                    'description': 'Configure MPLS VPN with route leaking between customer VRFs'
                },
                'datacenter-fabric': {
                    'name': 'Data Center Spine-Leaf VXLAN',
                    'difficulty': 'hard',
                    'base_score': 300,
                    'description': 'Implement a data center fabric with spine-leaf architecture and VXLAN overlay'
                },
                'sd-wan-overlay': {
                    'name': 'SD-WAN Overlay Issues',
                    'difficulty': 'hard',
                    'base_score': 300,
                    'description': 'Troubleshoot SD-WAN overlay connectivity and routing issues'
                }
            }
            
            challenge_info = challenge_metadata.get(scenario_id, {
                'name': scenario_id,
                'difficulty': 'easy',
                'base_score': 100,
                'description': 'Link Up Challenge'
            })
            
            # Validate the user solution against expected topology
            match_percentage = self._validate_linkup_solution(scenario_id, user_solution)
            base_score = challenge_info['base_score']
            
            # Calculate time bonus (max 20 points for completing quickly)
            time_bonus = 0
            if time_taken > 0 and time_taken < 300:  # Under 5 minutes
                time_bonus = min(20, int(20 * (300 - time_taken) / 300))
            
            total_score = base_score + time_bonus
            
            # [FIX] FIX: Normalize score to 0-100 percentage for leaderboard consistency
            # Convert raw score (which can be 100-320) to percentage (0-100)
            # Easy challenges: base_score=100, max=120 -> normalize to 100%
            # Medium challenges: base_score=200, max=220 -> normalize to 100%
            # Hard challenges: base_score=300, max=320 -> normalize to 100%
            max_possible_score = base_score + 20  # Max score includes 20 point time bonus
            normalized_score = min((total_score / max_possible_score) * 100, 100.0)
            
            print(f"📊 Score calculation:")
            print(f"   Raw score: {total_score} (base: {base_score}, bonus: {time_bonus})")
            print(f"   Normalized: {normalized_score:.1f}% (for leaderboard)")
            
            # Determine challenge type based on difficulty
            difficulty = challenge_info['difficulty']
            if difficulty == 'easy':
                challenge_type = 'linkup_easy'
            elif difficulty == 'medium':
                challenge_type = 'troubleshooting_medium'
            elif difficulty == 'hard':
                challenge_type = 'troubleshooting_hard'
            else:
                challenge_type = 'linkup_easy'
            
            # Save to ChallengeScore table (MVP system) using normalized score
            from user.models.challenge_score import ChallengeScore
            challenge_score = ChallengeScore.save_score(
                user_id=user_id,
                challenge_type=challenge_type,
                score=normalized_score,  # Use normalized 0-100 score
                metadata={
                    'scenario_id': scenario_id,
                    'scenario_name': challenge_info['name'],
                    'time_taken': time_taken,
                    'difficulty': challenge_info['difficulty']
                },
                completion_time=time_taken
            )
            
            # Check and award badges
            from user.services.badge_service import BadgeService
            newly_earned_badges = BadgeService.check_and_award_badges(
                user_id=user_id,
                challenge_type=challenge_type,
                score=total_score,
                metadata={'scenario_id': scenario_id, 'difficulty': difficulty}
            )
            
            db.session.commit()
            
            # Return success response
            response = {
                "success": True,
                "score": total_score,
                "base_score": base_score,
                "time_bonus": time_bonus,
                "topology_match_percentage": match_percentage,
                "feedback": f"""
                    <p class="success">🎉 Excellent work! Challenge completed successfully!</p>
                    <p>You've successfully configured <strong>{challenge_info['name']}</strong>.</p>
                    <p><strong>Score:</strong> {total_score}/100 ({base_score} base + {time_bonus} time bonus)</p>
                """,
                "scenario_name": challenge_info['name'],
                "scenario_id": scenario_id,
                "badges_earned": newly_earned_badges,
                "challenge_completed": True
            }
            
            return response
            
        except Exception as e:
            print(f"[ERROR] Error submitting hardcoded challenge: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Error processing challenge: {str(e)}"}, 500
    
    def _validate_linkup_solution(self, scenario_id, user_solution):
        """Validate Link Up challenge solutions"""
        try:
            print(f"[DEBUG] Validating {scenario_id} solution...")
            print(f"📦 User solution: {json.dumps(user_solution, indent=2)}")
            
            devices = user_solution.get('devices', [])
            connections = user_solution.get('connections', [])
            
            if scenario_id in ['default-gateway', 'default-gateway-setup']:
                return self._validate_default_gateway(devices)
            elif scenario_id in ['dhcp-client', 'dhcp-client-config']:
                return self._validate_dhcp_client(devices)
            elif scenario_id == 'vlan-basics':
                return self._validate_vlan_basics(devices)
            elif scenario_id == 'extended-ring-redundancy':
                return self._validate_extended_ring_redundancy(devices, connections)
            elif scenario_id == 'hybrid-star-ring':
                return self._validate_hybrid_star_ring(devices, connections)
            elif scenario_id == 'partial-mesh-ospf':
                return self._validate_partial_mesh_ospf(devices, connections)
            elif scenario_id == 'mpls-vpn-complex':
                return self._validate_mpls_vpn_complex(devices, connections)
            elif scenario_id == 'datacenter-fabric':
                return self._validate_datacenter_fabric(devices, connections)
            elif scenario_id == 'sd-wan-overlay':
                return self._validate_sd_wan_overlay(devices, connections)
            else:
                print(f"[WARNING] Unknown scenario: {scenario_id}, returning 0%")
                return 0
                
        except Exception as e:
            print(f"[ERROR] Validation error: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _validate_default_gateway(self, devices):
        """Validate Default Gateway Configuration"""
        print("🌐 Validating Default Gateway Configuration...")
        score = 0
        
        # Find Gateway Router
        router = next((d for d in devices if d.get('type') == 'router' and d.get('label') == 'Gateway Router'), None)
        if not router:
            print("[ERROR] Gateway Router not found")
            return 0
        
        print(f"[OK] Found Gateway Router: {router.get('label')}")
        
        # Check router interface configuration
        interfaces = router.get('interfaces', {})
        gi00 = interfaces.get('GigabitEthernet0/0', {})
        
        if gi00.get('ip') == '192.168.1.1' and gi00.get('subnet') == '255.255.255.0':
            score += 30
            print("[OK] Router IP configured: 192.168.1.1/24 (+30 points)")
        else:
            print(f"[ERROR] Router IP incorrect: {gi00.get('ip')}/{gi00.get('subnet')}")
            return score
        
        if gi00.get('status') == 'up':
            score += 20
            print("[OK] Router interface is up (+20 points)")
        else:
            print(f"[ERROR] Router interface status: {gi00.get('status')}")
        
        # Check PCs
        pcs = [d for d in devices if d.get('type') == 'pc']
        print(f"[PIN] Found {len(pcs)} PCs")
        
        correctly_configured_pcs = 0
        for pc in pcs:
            pc_name = pc.get('label', 'Unknown')
            ip = pc.get('ipv4', '')
            subnet = pc.get('subnet', '')
            gateway = pc.get('defaultGateway', '')
            
            print(f"   Checking {pc_name}: {ip}/{subnet} GW:{gateway}")
            
            if (ip.startswith('192.168.1.') and 
                subnet == '255.255.255.0' and 
                gateway == '192.168.1.1'):
                correctly_configured_pcs += 1
                print(f"   [OK] {pc_name} correctly configured")
            else:
                print(f"   [ERROR] {pc_name} incorrect configuration")
        
        # Award points for each correctly configured PC (50 points total / 3 PCs ≈ 16.67 each)
        pc_score = int((correctly_configured_pcs / len(pcs)) * 50) if pcs else 0
        score += pc_score
        print(f"[OK] {correctly_configured_pcs}/{len(pcs)} PCs configured (+{pc_score} points)")
        
        print(f"📊 Final score: {score}/100")
        return score
    
    def _validate_dhcp_client(self, devices):
        """Validate DHCP Client Configuration"""
        print("📡 Validating DHCP Client Configuration...")
        score = 0
        
        # Find DHCP Server router
        router = next((d for d in devices if d.get('type') == 'router' and d.get('label') == 'DHCP Server'), None)
        if not router:
            print("[ERROR] DHCP Server router not found")
            return 0
        
        print(f"[OK] Found DHCP Server: {router.get('label')}")
        
        # Check DHCP pool configuration
        dhcp_pools = router.get('dhcpPools', {})
        if not dhcp_pools:
            print("[ERROR] No DHCP pools configured")
            return 0
        
        score += 20
        print(f"[OK] DHCP pool exists (+20 points)")
        
        # Check pool configuration
        pool_name = list(dhcp_pools.keys())[0]
        pool = dhcp_pools[pool_name]
        
        if pool.get('network', '').startswith('192.168.1.'):
            score += 15
            print(f"[OK] Network configured: {pool.get('network')} (+15 points)")
        else:
            print(f"[ERROR] Network incorrect: {pool.get('network')}")
        
        if pool.get('defaultRouter') == '192.168.1.1':
            score += 15
            print(f"[OK] Default router configured: 192.168.1.1 (+15 points)")
        else:
            print(f"[ERROR] Default router incorrect: {pool.get('defaultRouter')}")
        
        # Check excluded addresses
        excluded = router.get('dhcpExcluded', [])
        if excluded:
            score += 10
            print(f"[OK] Excluded addresses configured (+10 points)")
        else:
            print("[ERROR] No excluded addresses")
        
        # Check PCs have DHCP addresses
        pcs = [d for d in devices if d.get('type') == 'pc']
        print(f"[PIN] Found {len(pcs)} PCs")
        
        correctly_configured_pcs = 0
        for pc in pcs:
            pc_name = pc.get('label', 'Unknown')
            ip = pc.get('ipv4', '')
            gateway = pc.get('defaultGateway', '')
            
            print(f"   Checking {pc_name}: {ip} GW:{gateway}")
            
            # Check if PC has DHCP IP (not APIPA 169.254.x.x)
            if (ip.startswith('192.168.1.') and 
                not ip.startswith('169.254.') and 
                gateway == '192.168.1.1'):
                correctly_configured_pcs += 1
                print(f"   [OK] {pc_name} has DHCP address")
            else:
                print(f"   [ERROR] {pc_name} does not have DHCP address")
        
        # Award points for PCs with DHCP addresses (40 points total)
        pc_score = int((correctly_configured_pcs / len(pcs)) * 40) if pcs else 0
        score += pc_score
        print(f"[OK] {correctly_configured_pcs}/{len(pcs)} PCs with DHCP (+{pc_score} points)")
        
        print(f"📊 Final score: {score}/100")
        return score
    
    def _validate_vlan_basics(self, devices):
        """Validate VLAN Basics configuration"""
        print("🔌 Validating VLAN Basics...")
        score = 0
        
        # Find switch
        switch = next((d for d in devices if d.get('type') == 'switch'), None)
        if not switch:
            print("[ERROR] Switch not found")
            return 0
        
        # Check VLANs exist
        vlans = switch.get('vlans', {})
        if '10' in vlans and '20' in vlans:
            score += 40
            print("[OK] VLANs 10 and 20 created (+40 points)")
        else:
            print(f"[ERROR] VLANs missing: {list(vlans.keys())}")
            return score
        
        # Check port assignments
        port_assignments = switch.get('portVlanAssignments', {})
        interface_modes = switch.get('interfaceMode', {})
        
        correct_ports = 0
        if port_assignments.get('Fa0/1') == '10' and interface_modes.get('Fa0/1') == 'access':
            correct_ports += 1
        if port_assignments.get('Fa0/2') == '10' and interface_modes.get('Fa0/2') == 'access':
            correct_ports += 1
        if port_assignments.get('Fa0/3') == '20' and interface_modes.get('Fa0/3') == 'access':
            correct_ports += 1
        if port_assignments.get('Fa0/4') == '20' and interface_modes.get('Fa0/4') == 'access':
            correct_ports += 1
        
        port_score = int((correct_ports / 4) * 60)
        score += port_score
        print(f"[OK] {correct_ports}/4 ports correctly configured (+{port_score} points)")
        
        print(f"📊 Final score: {score}/100")
        return score
    
    def _validate_extended_ring_redundancy(self, devices, connections):
        """Validate Extended Ring with Redundancy (2 rings + bridge switch)"""
        print("🔄 Validating Extended Ring with Redundancy...")
        score = 0
        
        # Count switches (should be 8: 4 in Ring1, 3 in Ring2, 1 Bridge)
        switches = [d for d in devices if d.get('type') == 'switch']
        if len(switches) != 8:
            print(f"[ERROR] Expected 8 switches, found {len(switches)}")
            return 0
        
        print(f"[OK] Found 8 switches (+20 points)")
        score += 20
        
        # Identify Ring 1 switches (4 switches)
        ring1_switches = [s for s in switches if 'Ring1' in s.get('label', '')]
        # Identify Ring 2 switches (3 switches)
        ring2_switches = [s for s in switches if 'Ring2' in s.get('label', '')]
        # Identify Bridge switch
        bridge_switch = next((s for s in switches if 'Bridge' in s.get('label', '')), None)
        
        if len(ring1_switches) == 4:
            print(f"[OK] Found 4 Ring1 switches (+10 points)")
            score += 10
        else:
            print(f"[ERROR] Expected 4 Ring1 switches, found {len(ring1_switches)}")
        
        if len(ring2_switches) == 3:
            print(f"[OK] Found 3 Ring2 switches (+10 points)")
            score += 10
        else:
            print(f"[ERROR] Expected 3 Ring2 switches, found {len(ring2_switches)}")
        
        if bridge_switch:
            print(f"[OK] Found Bridge switch (+10 points)")
            score += 10
        else:
            print(f"[ERROR] Bridge switch not found")
        
        # Check Ring 1 forms a complete ring
        if len(ring1_switches) == 4:
            ring1_names = {s.get('id') or s.get('label') for s in ring1_switches}
            ring1_connections = {name: [] for name in ring1_names}
            
            for conn in connections:
                dev1 = conn.get('device1')
                dev2 = conn.get('device2')
                if dev1 in ring1_names and dev2 in ring1_names:
                    ring1_connections[dev1].append(dev2)
                    ring1_connections[dev2].append(dev1)
            
            # Each switch in Ring1 should have exactly 2 connections within the ring
            correct_ring1 = sum(1 for name in ring1_names if len(ring1_connections[name]) == 2)
            if correct_ring1 == 4:
                print("[OK] Ring1 forms complete ring topology (+20 points)")
                score += 20
            else:
                print(f"[WARNING] Ring1 incomplete: {correct_ring1}/4 switches correctly connected")
        
        # Check Ring 2 forms a complete ring
        if len(ring2_switches) == 3:
            ring2_names = {s.get('id') or s.get('label') for s in ring2_switches}
            ring2_connections = {name: [] for name in ring2_names}
            
            for conn in connections:
                dev1 = conn.get('device1')
                dev2 = conn.get('device2')
                if dev1 in ring2_names and dev2 in ring2_names:
                    ring2_connections[dev1].append(dev2)
                    ring2_connections[dev2].append(dev1)
            
            # Each switch in Ring2 should have exactly 2 connections within the ring
            correct_ring2 = sum(1 for name in ring2_names if len(ring2_connections[name]) == 2)
            if correct_ring2 == 3:
                print("[OK] Ring2 forms complete ring topology (+15 points)")
                score += 15
            else:
                print(f"[WARNING] Ring2 incomplete: {correct_ring2}/3 switches correctly connected")
        
        # Check bridge connections (Bridge should connect to both rings)
        if bridge_switch:
            bridge_name = bridge_switch.get('id') or bridge_switch.get('label')
            bridge_connections = []
            
            for conn in connections:
                if conn.get('device1') == bridge_name:
                    bridge_connections.append(conn.get('device2'))
                elif conn.get('device2') == bridge_name:
                    bridge_connections.append(conn.get('device1'))
            
            # Check if bridge connects to at least one switch from each ring
            connects_ring1 = any(conn in [s.get('id') or s.get('label') for s in ring1_switches] for conn in bridge_connections)
            connects_ring2 = any(conn in [s.get('id') or s.get('label') for s in ring2_switches] for conn in bridge_connections)
            
            if connects_ring1 and connects_ring2:
                print("[OK] Bridge connects both rings (+15 points)")
                score += 15
            else:
                print(f"[ERROR] Bridge missing connections (Ring1: {connects_ring1}, Ring2: {connects_ring2})")
        
        print(f"📊 Final score: {score}/100")
        return score
    
    def _validate_hybrid_star_ring(self, devices, connections):
        """Validate Hybrid Star-Ring Topology (star section + ring section connected)"""
        print("🔄 Validating Hybrid Star-Ring Topology...")
        score = 0
        
        # Count devices by type
        switches = [d for d in devices if d.get('type') == 'switch']
        pcs = [d for d in devices if d.get('type') == 'pc']
        
        if len(switches) != 4:
            print(f"[ERROR] Expected 4 switches, found {len(switches)}")
            return 0
        
        if len(pcs) != 4:
            print(f"[ERROR] Expected 4 PCs, found {len(pcs)}")
            return 0
        
        print(f"[OK] Found correct device count: 4 switches, 4 PCs (+20 points)")
        score += 20
        
        # Identify star topology devices
        core_star = next((s for s in switches if 'Core' in s.get('label', '') or 'Star SW' in s.get('label', '')), None)
        star_pcs = [p for p in pcs if 'Star' in p.get('label', '')]
        
        # Identify ring topology devices  
        ring_switches = [s for s in switches if 'Ring' in s.get('label', '') and s != core_star]
        ring_pcs = [p for p in pcs if 'Ring' in p.get('label', '')]
        
        # Validate star section
        if core_star:
            print(f"[OK] Found central star switch (+10 points)")
            score += 10
            
            # Check star connections (central switch to star PCs)
            core_name = core_star.get('id') or core_star.get('label')
            star_pc_names = [p.get('id') or p.get('label') for p in star_pcs]
            
            connected_star_pcs = 0
            for conn in connections:
                if (conn.get('device1') == core_name and conn.get('device2') in star_pc_names) or \
                   (conn.get('device2') == core_name and conn.get('device1') in star_pc_names):
                    connected_star_pcs += 1
            
            if connected_star_pcs == 2:
                print(f"[OK] Star topology correct: 2 PCs connected to central switch (+20 points)")
                score += 20
            else:
                print(f"[WARNING] Star connections incomplete: {connected_star_pcs}/2 PCs connected")
        
        # Validate ring section (3 switches forming a ring)
        if len(ring_switches) == 3:
            print(f"[OK] Found 3 ring switches (+10 points)")
            score += 10
            
            ring_names = {s.get('id') or s.get('label') for s in ring_switches}
            ring_connections = {name: [] for name in ring_names}
            
            for conn in connections:
                dev1 = conn.get('device1')
                dev2 = conn.get('device2')
                if dev1 in ring_names and dev2 in ring_names:
                    ring_connections[dev1].append(dev2)
                    ring_connections[dev2].append(dev1)
            
            # Each switch in ring should have exactly 2 connections within the ring
            correct_ring = sum(1 for name in ring_names if len(ring_connections[name]) == 2)
            if correct_ring == 3:
                print("[OK] Ring topology correct: all 3 switches properly connected (+20 points)")
                score += 20
            else:
                print(f"[WARNING] Ring incomplete: {correct_ring}/3 switches correctly connected")
        
        # Validate ring PCs are connected to ring switches
        ring_pc_names = [p.get('id') or p.get('label') for p in ring_pcs]
        ring_switch_names = [s.get('id') or s.get('label') for s in ring_switches]
        
        connected_ring_pcs = 0
        for conn in connections:
            if (conn.get('device1') in ring_pc_names and conn.get('device2') in ring_switch_names) or \
               (conn.get('device2') in ring_pc_names and conn.get('device1') in ring_switch_names):
                connected_ring_pcs += 1
        
        if connected_ring_pcs >= 2:
            print(f"[OK] Ring PCs properly connected (+10 points)")
            score += 10
        
        # Validate hybrid connection (star center to ring network)
        if core_star:
            core_name = core_star.get('id') or core_star.get('label')
            ring_switch_names = [s.get('id') or s.get('label') for s in ring_switches]
            
            hybrid_connections = 0
            for conn in connections:
                if (conn.get('device1') == core_name and conn.get('device2') in ring_switch_names) or \
                   (conn.get('device2') == core_name and conn.get('device1') in ring_switch_names):
                    hybrid_connections += 1
            
            if hybrid_connections >= 1:
                print(f"[OK] Hybrid connection present: star connected to ring (+10 points)")
                score += 10
            else:
                print(f"[ERROR] Missing hybrid connection between star and ring")
        
        print(f"📊 Final score: {score}/100")
        return score
    
    def _validate_partial_mesh_ospf(self, devices, connections):
        """Validate Partial Mesh OSPF Network with multi-area topology"""
        print("🔄 Validating Partial Mesh OSPF Network...")
        score = 0
        
        # Count routers (should be 5)
        routers = [d for d in devices if d.get('type') == 'router']
        
        if len(routers) != 5:
            print(f"[ERROR] Expected 5 routers, found {len(routers)}")
            return 0
        
        print(f"[OK] Found 5 routers (+20 points)")
        score += 20
        
        # Identify Area 0 routers (backbone)
        area0_routers = [r for r in routers if 'Area0' in r.get('label', '') or 'R1' in r.get('label', '') or 'R2' in r.get('label', '')]
        # Identify Area 1 routers
        area1_routers = [r for r in routers if 'Area1' in r.get('label', '') or 'R3' in r.get('label', '') or 'R4' in r.get('label', '')]
        # Identify ABR (Area Border Router)
        abr = next((r for r in routers if 'ABR' in r.get('label', '') or 'R5' in r.get('label', '')), None)
        
        # Validate router distribution
        if len(area0_routers) >= 2:
            print(f"[OK] Found Area 0 routers (+10 points)")
            score += 10
        
        if len(area1_routers) >= 2:
            print(f"[OK] Found Area 1 routers (+10 points)")
            score += 10
        
        if abr:
            print(f"[OK] Found ABR (Area Border Router) (+15 points)")
            score += 15
        
        # Validate connections (partial mesh = not all routers directly connected)
        total_connections = len(connections)
        
        if total_connections >= 6 and total_connections <= 8:
            print(f"[OK] Good partial mesh connectivity: {total_connections} connections (+15 points)")
            score += 15
        elif total_connections > 0:
            print(f"[WARNING] Suboptimal connectivity: {total_connections} connections (+5 points)")
            score += 5
        
        # Validate Area 0 internal connections
        if len(area0_routers) >= 2:
            area0_names = [r.get('id') or r.get('label') for r in area0_routers]
            area0_connections = 0
            
            for conn in connections:
                if conn.get('device1') in area0_names and conn.get('device2') in area0_names:
                    area0_connections += 1
            
            if area0_connections >= 1:
                print(f"[OK] Area 0 routers interconnected (+10 points)")
                score += 10
        
        # Validate Area 1 internal connections
        if len(area1_routers) >= 2:
            area1_names = [r.get('id') or r.get('label') for r in area1_routers]
            area1_connections = 0
            
            for conn in connections:
                if conn.get('device1') in area1_names and conn.get('device2') in area1_names:
                    area1_connections += 1
            
            if area1_connections >= 1:
                print(f"[OK] Area 1 routers interconnected (+10 points)")
                score += 10
        
        # Validate ABR connections to both areas
        if abr:
            abr_name = abr.get('id') or abr.get('label')
            area0_names = [r.get('id') or r.get('label') for r in area0_routers]
            area1_names = [r.get('id') or r.get('label') for r in area1_routers]
            
            connects_area0 = any(
                (conn.get('device1') == abr_name and conn.get('device2') in area0_names) or
                (conn.get('device2') == abr_name and conn.get('device1') in area0_names)
                for conn in connections
            )
            
            connects_area1 = any(
                (conn.get('device1') == abr_name and conn.get('device2') in area1_names) or
                (conn.get('device2') == abr_name and conn.get('device1') in area1_names)
                for conn in connections
            )
            
            if connects_area0 and connects_area1:
                print(f"[OK] ABR connects both areas (+10 points)")
                score += 10
            else:
                print(f"[ERROR] ABR not properly connecting areas (Area0: {connects_area0}, Area1: {connects_area1})")
        
        print(f"📊 Final score: {score}/100")
        return score
    
    def _validate_mpls_vpn_complex(self, devices, connections):
        """Validate MPLS VPN Route Leaking scenario"""
        print("🌐 Validating MPLS VPN Route Leaking scenario...")
        score = 0
        
        try:
            routers = [d for d in devices if d.get('type') == 'router']
            
            if len(routers) < 6:
                print(f"[ERROR] Insufficient routers: {len(routers)}/6+ required")
                return 0
            
            print(f"[OK] Found {len(routers)} routers (+20 points)")
            score += 20
            
            # Identify router types by label (with safe string handling)
            p_routers = [r for r in routers if r.get('label', '').startswith('P')]
            pe_routers = [r for r in routers if r.get('label', '').startswith('PE')]
            ce_routers = [r for r in routers if r.get('label', '').startswith('CE')]
            
            if len(p_routers) >= 2:
                print(f"[OK] Found {len(p_routers)} P routers (core) (+15 points)")
                score += 15
            
            if len(pe_routers) >= 2:
                print(f"[OK] Found {len(pe_routers)} PE routers (edge) (+15 points)")
                score += 15
            
            if len(ce_routers) >= 2:
                print(f"[OK] Found {len(ce_routers)} CE routers (customer) (+15 points)")
                score += 15
            
            # Build device ID to label mapping for safe connection validation
            id_to_label = {(r.get('id') or r.get('label')): r.get('label', '') for r in routers}
            
            # Validate MPLS core connections (P-to-P and P-to-PE)
            mpls_core_connections = 0
            for conn in connections:
                dev1_id = conn.get('device1', '')
                dev2_id = conn.get('device2', '')
                dev1_label = id_to_label.get(dev1_id, '')
                dev2_label = id_to_label.get(dev2_id, '')
                
                if ((dev1_label.startswith('P') and dev2_label.startswith('P')) or
                    (dev1_label.startswith('P') and dev2_label.startswith('PE')) or
                    (dev1_label.startswith('PE') and dev2_label.startswith('P'))):
                    mpls_core_connections += 1
            
            if mpls_core_connections >= 3:
                print(f"[OK] MPLS core properly connected ({mpls_core_connections} links) (+20 points)")
                score += 20
            elif mpls_core_connections > 0:
                print(f"[WARNING] Partial MPLS core connectivity (+10 points)")
                score += 10
            
            # Validate CE-to-PE connections (customer access)
            ce_connections = 0
            for conn in connections:
                dev1_id = conn.get('device1', '')
                dev2_id = conn.get('device2', '')
                dev1_label = id_to_label.get(dev1_id, '')
                dev2_label = id_to_label.get(dev2_id, '')
                
                if ((dev1_label.startswith('CE') and dev2_label.startswith('PE')) or
                    (dev1_label.startswith('PE') and dev2_label.startswith('CE'))):
                    ce_connections += 1
            
            if ce_connections >= len(ce_routers):
                print(f"[OK] All CE routers connected to PE (+15 points)")
                score += 15
            elif ce_connections > 0:
                print(f"[WARNING] Some CE connections present (+5 points)")
                score += 5
            
            print(f"📊 Final score: {score}/100")
            return score
            
        except Exception as e:
            print(f"[ERROR] Error in MPLS VPN validation: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _validate_datacenter_fabric(self, devices, connections):
        """Validate Data Center Spine-Leaf VXLAN scenario"""
        print("🏢 Validating Data Center Spine-Leaf VXLAN scenario...")
        score = 0
        
        switches = [d for d in devices if d.get('type') == 'switch']
        servers = [d for d in devices if d.get('type') == 'pc' or 'server' in d.get('label', '').lower()]
        
        # Identify spine and leaf switches
        spine_switches = [s for s in switches if 'spine' in s.get('label', '').lower()]
        leaf_switches = [s for s in switches if 'leaf' in s.get('label', '').lower()]
        
        if len(spine_switches) >= 2:
            print(f"[OK] Found {len(spine_switches)} spine switches (+20 points)")
            score += 20
        elif len(spine_switches) > 0:
            print(f"[WARNING] At least 1 spine switch present (+10 points)")
            score += 10
        
        if len(leaf_switches) >= 2:
            print(f"[OK] Found {len(leaf_switches)} leaf switches (+20 points)")
            score += 20
        elif len(leaf_switches) > 0:
            print(f"[WARNING] At least 1 leaf switch present (+10 points)")
            score += 10
        
        # Validate spine-leaf connections (every leaf should connect to every spine)
        expected_spine_leaf_connections = len(spine_switches) * len(leaf_switches)
        spine_leaf_connections = 0
        
        spine_ids = [s.get('id') or s.get('label') for s in spine_switches]
        leaf_ids = [l.get('id') or l.get('label') for l in leaf_switches]
        
        for conn in connections:
            dev1 = conn.get('device1')
            dev2 = conn.get('device2')
            if (dev1 in spine_ids and dev2 in leaf_ids) or \
               (dev1 in leaf_ids and dev2 in spine_ids):
                spine_leaf_connections += 1
        
        if spine_leaf_connections >= expected_spine_leaf_connections:
            print(f"[OK] Full mesh spine-leaf connectivity ({spine_leaf_connections} links) (+30 points)")
            score += 30
        elif spine_leaf_connections >= expected_spine_leaf_connections * 0.5:
            print(f"[WARNING] Partial spine-leaf connectivity ({spine_leaf_connections}/{expected_spine_leaf_connections} links) (+15 points)")
            score += 15
        
        # Validate server connections to leaf switches
        if len(servers) >= 2:
            print(f"[OK] Found {len(servers)} servers (+10 points)")
            score += 10
            
            server_connections = 0
            server_ids = [s.get('id') or s.get('label') for s in servers]
            
            for conn in connections:
                dev1 = conn.get('device1')
                dev2 = conn.get('device2')
                if (dev1 in server_ids and dev2 in leaf_ids) or \
                   (dev1 in leaf_ids and dev2 in server_ids):
                    server_connections += 1
            
            if server_connections >= len(servers):
                print(f"[OK] All servers connected to leaf switches (+20 points)")
                score += 20
            elif server_connections > 0:
                print(f"[WARNING] Some server connections present (+10 points)")
                score += 10
        
        print(f"📊 Final score: {score}/100")
        return score
    
    def _validate_sd_wan_overlay(self, devices, connections):
        """Validate SD-WAN Overlay Issues scenario"""
        print("☁️ Validating SD-WAN Overlay Issues scenario...")
        score = 0
        
        routers = [d for d in devices if d.get('type') == 'router']
        pcs = [d for d in devices if d.get('type') == 'pc']
        
        # Identify SD-WAN components
        controllers = [r for r in routers if 'controller' in r.get('label', '').lower() or 'vmanage' in r.get('label', '').lower()]
        edge_routers = [r for r in routers if 'edge' in r.get('label', '').lower() or 'vedge' in r.get('label', '').lower()]
        hub_routers = [r for r in routers if 'hub' in r.get('label', '').lower()]
        
        if len(controllers) >= 1:
            print(f"[OK] Found SD-WAN controller (+25 points)")
            score += 25
        else:
            print(f"[ERROR] No SD-WAN controller found")
        
        if len(edge_routers) >= 2:
            print(f"[OK] Found {len(edge_routers)} edge routers (+20 points)")
            score += 20
        elif len(edge_routers) > 0:
            print(f"[WARNING] Found {len(edge_routers)} edge router (+10 points)")
            score += 10
        
        if len(hub_routers) >= 1:
            print(f"[OK] Found {len(hub_routers)} hub router(s) (+15 points)")
            score += 15
        
        # Validate controller connections to edge/hub routers
        if controllers:
            controller_id = controllers[0].get('id') or controllers[0].get('label')
            controller_connections = 0
            
            for conn in connections:
                dev1 = conn.get('device1')
                dev2 = conn.get('device2')
                if controller_id in [dev1, dev2]:
                    controller_connections += 1
            
            if controller_connections >= 2:
                print(f"[OK] Controller connected to multiple devices (+15 points)")
                score += 15
            elif controller_connections > 0:
                print(f"[WARNING] Controller has at least one connection (+5 points)")
                score += 5
        
        # Validate overlay topology (edge-to-hub or edge-to-edge connections)
        overlay_connections = 0
        edge_hub_ids = [r.get('id') or r.get('label') for r in edge_routers + hub_routers]
        
        for conn in connections:
            dev1 = conn.get('device1')
            dev2 = conn.get('device2')
            if dev1 in edge_hub_ids and dev2 in edge_hub_ids:
                overlay_connections += 1
        
        if overlay_connections >= 3:
            print(f"[OK] Good SD-WAN overlay connectivity ({overlay_connections} links) (+15 points)")
            score += 15
        elif overlay_connections > 0:
            print(f"[WARNING] Some overlay connectivity present (+5 points)")
            score += 5
        
        # Validate client connections
        if len(pcs) >= 2:
            print(f"[OK] Found {len(pcs)} client devices (+10 points)")
            score += 10
        
        print(f"📊 Final score: {score}/100")
        return score
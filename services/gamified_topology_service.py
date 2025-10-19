"""
Gamified Topology Simulation Service
====================================

This service manages the gamified topology simulation system with:
- Difficulty-based progression (Easy, Medium, Hard)
- Scoring and achievement tracking
- Interactive tutorial system
- Progress visualization
- Learning path management
"""

from sqlalchemy import func, and_, or_
from flask import current_app
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Optional, Tuple

from instructor.models.topology import Topology
from user.models.topology_progress import TopologyProgress
from instructor.models.simulation import Simulation
from user.models import User, Score
from __init__ import db


class GamifiedTopologyService:
    """Service for managing gamified topology simulations"""
    
    # Difficulty-based scoring multipliers
    DIFFICULTY_MULTIPLIERS = {
        'easy': 1.0,
        'medium': 1.5,
        'hard': 2.0
    }
    
    # Achievement definitions
    ACHIEVEMENTS = {
        'first_topology': {
            'name': 'Network Builder',
            'description': 'Complete your first topology',
            'icon': '🏗️',
            'points': 50
        },
        'speed_demon': {
            'name': 'Speed Demon',
            'description': 'Complete a topology in under 60 seconds',
            'icon': '⚡',
            'points': 100
        },
        'perfectionist': {
            'name': 'Perfectionist',
            'description': 'Complete a topology with perfect score',
            'icon': '💎',
            'points': 150
        },
        'difficulty_master': {
            'name': 'Difficulty Master',
            'description': 'Complete all difficulties for any topology type',
            'icon': '🏆',
            'points': 200
        },
        'topology_expert': {
            'name': 'Topology Expert',
            'description': 'Complete all topology types',
            'icon': '🎓',
            'points': 500
        }
    }
    
    def __init__(self):
        self.topology_scenarios = self._initialize_topology_scenarios()
    
    def _initialize_topology_scenarios(self) -> Dict:
        """Initialize predefined topology scenarios with difficulty progression"""
        return {
            'point-to-point': {
                'easy': {
                    'name': 'Basic Connection',
                    'description': 'Connect two computers directly',
                    'requirements': {'pc': 2},
                    'max_devices': 2,
                    'time_limit': 300,  # 5 minutes
                    'tutorial_steps': [
                        "Drag two PC devices to the canvas",
                        "Click 'Connection Mode' to enable connections",
                        "Click on first PC, then second PC to connect them",
                        "Click 'Check Topology' to validate"
                    ]
                },
                'medium': {
                    'name': 'PC to Router Link',
                    'description': 'Connect a PC to a router for internet access',
                    'requirements': {'pc': 1, 'router': 1},
                    'max_devices': 2,
                    'time_limit': 240,  # 4 minutes
                    'tutorial_steps': [
                        "Place one PC and one router on the canvas",
                        "Connect the PC to the router's LAN port",
                        "Verify the connection is properly established"
                    ]
                },
                'hard': {
                    'name': 'WAN Connection',
                    'description': 'Create a point-to-point WAN link between routers',
                    'requirements': {'router': 2},
                    'max_devices': 2,
                    'time_limit': 180,  # 3 minutes
                    'configuration_required': True,
                    'tutorial_steps': [
                        "Place two routers on the canvas",
                        "Connect them using WAN interfaces",
                        "Configure IP addressing (will be tested)",
                        "Validate the WAN connection"
                    ]
                }
            },
            'star': {
                'easy': {
                    'name': 'Simple Star Network',
                    'description': 'Connect 3 PCs to a central switch',
                    'requirements': {'pc': 3, 'switch': 1},
                    'max_devices': 4,
                    'time_limit': 420,  # 7 minutes
                    'tutorial_steps': [
                        "Place one switch in the center of the canvas",
                        "Add three PCs around the switch",
                        "Connect each PC to the switch",
                        "Verify all connections form a star pattern"
                    ]
                },
                'medium': {
                    'name': 'Office Network',
                    'description': 'Create a typical office network with router and switch',
                    'requirements': {'pc': 4, 'switch': 1, 'router': 1},
                    'max_devices': 6,
                    'time_limit': 360,  # 6 minutes
                    'tutorial_steps': [
                        "Connect the router to the switch",
                        "Connect all PCs to the switch",
                        "Ensure the router provides internet access",
                        "Verify star topology with central switch"
                    ]
                },
                'hard': {
                    'name': 'Enterprise Star Network',
                    'description': 'Complex star with servers and multiple device types',
                    'requirements': {'pc': 3, 'switch': 1, 'router': 1, 'server': 2},
                    'max_devices': 7,
                    'time_limit': 480,  # 8 minutes
                    'configuration_required': True,
                    'tutorial_steps': [
                        "Design a hierarchical star network",
                        "Place servers in appropriate network segments",
                        "Configure VLANs (will be tested)",
                        "Validate enterprise-grade topology"
                    ]
                }
            },
            'mesh': {
                'easy': {
                    'name': 'Three-Node Mesh',
                    'description': 'Create a simple mesh with 3 routers',
                    'requirements': {'router': 3},
                    'max_devices': 3,
                    'time_limit': 360,  # 6 minutes
                    'tutorial_steps': [
                        "Place three routers on the canvas",
                        "Connect each router to every other router",
                        "Verify full mesh connectivity",
                        "Check redundant paths exist"
                    ]
                },
                'medium': {
                    'name': 'Four-Node Full Mesh',
                    'description': 'Create a full mesh network with 4 routers',
                    'requirements': {'router': 4},
                    'max_devices': 4,
                    'time_limit': 480,  # 8 minutes
                    'tutorial_steps': [
                        "Deploy four routers strategically",
                        "Establish full mesh connectivity (6 links total)",
                        "Ensure every router connects to every other",
                        "Validate redundancy and fault tolerance"
                    ]
                },
                'hard': {
                    'name': 'Partial Mesh with Optimization',
                    'description': 'Design an optimized partial mesh topology',
                    'requirements': {'router': 5},
                    'max_devices': 7,
                    'time_limit': 600,  # 10 minutes
                    'configuration_required': True,
                    'tutorial_steps': [
                        "Create a partial mesh balancing cost and redundancy",
                        "Add end devices (PCs) to edge routers",
                        "Configure routing protocols (will be tested)",
                        "Optimize for performance and reliability"
                    ]
                }
            },
            'bus': {
                'easy': {
                    'name': 'Simple Bus Network',
                    'description': 'Connect 3 PCs in a linear bus topology',
                    'requirements': {'pc': 3},
                    'max_devices': 3,
                    'time_limit': 300,  # 5 minutes
                    'tutorial_steps': [
                        "Place three PCs in a line",
                        "Connect them sequentially (PC1-PC2-PC3)",
                        "Verify linear bus structure",
                        "Test that middle PC can relay traffic"
                    ]
                },
                'medium': {
                    'name': 'Extended Bus Network',
                    'description': 'Create a bus network with 5 devices',
                    'requirements': {'pc': 4, 'server': 1},
                    'max_devices': 5,
                    'time_limit': 420,  # 7 minutes
                    'tutorial_steps': [
                        "Arrange devices in a linear fashion",
                        "Connect devices sequentially along the bus",
                        "Place server at one end of the bus",
                        "Verify single collision domain"
                    ]
                },
                'hard': {
                    'name': 'Ethernet Bus with Terminators',
                    'description': 'Design a proper Ethernet bus with termination',
                    'requirements': {'pc': 5, 'server': 1},
                    'max_devices': 6,
                    'time_limit': 540,  # 9 minutes
                    'configuration_required': True,
                    'tutorial_steps': [
                        "Create linear bus topology",
                        "Add proper bus terminators",
                        "Configure collision detection",
                        "Test CSMA/CD behavior"
                    ]
                }
            },
            'ring': {
                'easy': {
                    'name': 'Simple Ring',
                    'description': 'Connect 4 switches in a ring topology',
                    'requirements': {'switch': 4},
                    'max_devices': 4,
                    'time_limit': 360,  # 6 minutes
                    'tutorial_steps': [
                        "Place four switches in a circle",
                        "Connect each switch to the next in sequence",
                        "Close the ring by connecting last to first",
                        "Verify circular topology with no breaks"
                    ]
                },
                'medium': {
                    'name': 'Ring with Redundancy',
                    'description': 'Create a ring network with attached devices',
                    'requirements': {'switch': 4, 'pc': 4},
                    'max_devices': 8,
                    'time_limit': 480,  # 8 minutes
                    'tutorial_steps': [
                        "Build the ring topology with switches",
                        "Attach one PC to each switch",
                        "Verify ring integrity and redundancy",
                        "Test fault tolerance by simulating link failure"
                    ]
                },
                'hard': {
                    'name': 'Dual Ring Architecture',
                    'description': 'Design a dual counter-rotating ring for high availability',
                    'requirements': {'switch': 6, 'router': 2},
                    'max_devices': 8,
                    'time_limit': 720,  # 12 minutes
                    'configuration_required': True,
                    'tutorial_steps': [
                        "Create primary ring with switches",
                        "Add secondary counter-rotating ring",
                        "Configure ring protection protocols",
                        "Test automatic failover mechanisms"
                    ]
                }
            },
            'tree': {
                'easy': {
                    'name': 'Basic Tree',
                    'description': 'Create a simple hierarchical tree structure',
                    'requirements': {'switch': 3, 'pc': 4},
                    'max_devices': 7,
                    'time_limit': 420,  # 7 minutes
                    'tutorial_steps': [
                        "Place one switch as root of the tree",
                        "Connect two switches as branches",
                        "Attach PCs as leaves to branch switches",
                        "Verify hierarchical structure"
                    ]
                },
                'medium': {
                    'name': 'Three-Tier Hierarchy',
                    'description': 'Build a standard three-tier network architecture',
                    'requirements': {'router': 1, 'switch': 4, 'pc': 6},
                    'max_devices': 11,
                    'time_limit': 600,  # 10 minutes
                    'tutorial_steps': [
                        "Create core tier with router",
                        "Add distribution tier with switches",
                        "Build access tier with end devices",
                        "Ensure proper hierarchical design"
                    ]
                },
                'hard': {
                    'name': 'Campus Network Tree',
                    'description': 'Design a complex campus network with multiple tiers',
                    'requirements': {'router': 2, 'switch': 6, 'pc': 8, 'server': 2},
                    'max_devices': 18,
                    'time_limit': 900,  # 15 minutes
                    'configuration_required': True,
                    'tutorial_steps': [
                        "Design core, distribution, and access layers",
                        "Implement proper spanning tree protocols",
                        "Configure VLANs and inter-VLAN routing",
                        "Optimize for scalability and performance"
                    ]
                }
            },
            'hybrid': {
                'easy': {
                    'name': 'Star-Bus Hybrid',
                    'description': 'Combine star and bus topologies',
                    'requirements': {'switch': 2, 'pc': 4},
                    'max_devices': 6,
                    'time_limit': 480,  # 8 minutes
                    'tutorial_steps': [
                        "Create a star topology with one switch",
                        "Add a bus segment with another switch",
                        "Connect the two topologies",
                        "Verify hybrid functionality"
                    ]
                },
                'medium': {
                    'name': 'Ring-Star Hybrid',
                    'description': 'Integrate ring and star topologies with router',
                    'requirements': {'router': 1, 'switch': 4, 'pc': 6},
                    'max_devices': 11,
                    'time_limit': 600,  # 10 minutes
                    'tutorial_steps': [
                        "Build ring topology with switches",
                        "Create star segments from ring nodes",
                        "Add router for inter-segment routing",
                        "Test connectivity between segments"
                    ]
                },
                'hard': {
                    'name': 'Complex Hybrid Network',
                    'description': 'Design a real-world hybrid topology with multiple patterns',
                    'requirements': {'router': 3, 'switch': 6, 'pc': 8, 'server': 3},
                    'max_devices': 20,
                    'time_limit': 1200,  # 20 minutes
                    'configuration_required': True,
                    'tutorial_steps': [
                        "Integrate multiple topology types",
                        "Create redundant paths and segments",
                        "Configure advanced routing and switching",
                        "Optimize for real-world requirements"
                    ]
                }
            }
        }
    
    def get_available_scenarios(self, user_id: int = None) -> List[Dict]:
        """Get all available topology scenarios organized by difficulty"""
        scenarios = []
        
        for topology_type, difficulties in self.topology_scenarios.items():
            for difficulty, scenario in difficulties.items():
                # Get user progress for this scenario if user_id provided
                progress = None
                if user_id:
                    progress = TopologyProgress.query.filter_by(
                        user_id=user_id,
                        topology_type=topology_type,
                        difficulty=difficulty
                    ).first()
                
                scenario_data = {
                    'id': f"{topology_type}_{difficulty}",
                    'topology_type': topology_type,
                    'difficulty': difficulty,
                    'name': scenario['name'],
                    'description': scenario['description'],
                    'requirements': scenario['requirements'],
                    'max_devices': scenario['max_devices'],
                    'time_limit': scenario['time_limit'],
                    'tutorial_steps': scenario['tutorial_steps'],
                    'configuration_required': scenario.get('configuration_required', False),
                    'is_completed': progress.is_completed if progress else False,
                    'best_score': progress.best_score if progress else 0,
                    'completion_count': progress.completion_count if progress else 0,
                    'best_time': progress.best_time if progress else None,
                    'is_unlocked': self._is_scenario_unlocked(topology_type, difficulty, user_id)
                }
                
                scenarios.append(scenario_data)
        
        return scenarios
    
    def _is_scenario_unlocked(self, topology_type: str, difficulty: str, user_id: int = None) -> bool:
        """Check if a scenario is unlocked for the user"""
        if not user_id:
            return True
        
        # Easy scenarios are always unlocked
        if difficulty == 'easy':
            return True
        
        # Medium scenarios require completion of easy version
        if difficulty == 'medium':
            easy_progress = TopologyProgress.query.filter_by(
                user_id=user_id,
                topology_type=topology_type,
                difficulty='easy'
            ).first()
            return easy_progress and easy_progress.is_completed
        
        # Hard scenarios require completion of medium version
        if difficulty == 'hard':
            medium_progress = TopologyProgress.query.filter_by(
                user_id=user_id,
                topology_type=topology_type,
                difficulty='medium'
            ).first()
            return medium_progress and medium_progress.is_completed
        
        return False
    
    def start_scenario(self, user_id: int, topology_type: str, difficulty: str) -> Dict:
        """Start a new topology scenario for the user"""
        # Validate scenario exists
        if topology_type not in self.topology_scenarios:
            raise ValueError(f"Unknown topology type: {topology_type}")
        
        if difficulty not in self.topology_scenarios[topology_type]:
            raise ValueError(f"Unknown difficulty for {topology_type}: {difficulty}")
        
        # Check if scenario is unlocked
        if not self._is_scenario_unlocked(topology_type, difficulty, user_id):
            raise ValueError(f"Scenario {topology_type}_{difficulty} is locked")
        
        scenario = self.topology_scenarios[topology_type][difficulty]
        
        # Create or update progress record
        progress = TopologyProgress.query.filter_by(
            user_id=user_id,
            topology_type=topology_type,
            difficulty=difficulty
        ).first()
        
        if not progress:
            progress = TopologyProgress(
                user_id=user_id,
                topology_type=topology_type,
                difficulty=difficulty
            )
            db.session.add(progress)
        
        # Update start time for this attempt
        progress.last_attempt_start = datetime.utcnow()
        db.session.commit()
        
        return {
            'scenario_id': f"{topology_type}_{difficulty}",
            'scenario': scenario,
            'progress_id': progress.id,
            'start_time': progress.last_attempt_start.isoformat()
        }
    
    def validate_topology(self, user_id: int, topology_type: str, difficulty: str, 
                         devices: List[Dict], connections: List[Dict], 
                         completion_time: int = None) -> Dict:
        """Validate a user's topology submission and calculate score"""
        
        # Get scenario requirements
        scenario = self.topology_scenarios[topology_type][difficulty]
        requirements = scenario['requirements']
        
        # Count device types
        device_counts = {}
        for device in devices:
            device_type = device.get('type', '').lower()
            device_counts[device_type] = device_counts.get(device_type, 0) + 1
        
        # Validate device requirements
        validation_errors = []
        for req_type, req_count in requirements.items():
            actual_count = device_counts.get(req_type, 0)
            if actual_count < req_count:
                validation_errors.append(
                    f"Missing {req_count - actual_count} {req_type} device(s)"
                )
            elif actual_count > req_count and scenario.get('strict_requirements', False):
                validation_errors.append(
                    f"Too many {req_type} devices: {actual_count} (max: {req_count})"
                )
        
        # Check device limit
        if len(devices) > scenario['max_devices']:
            validation_errors.append(
                f"Too many devices: {len(devices)} (max: {scenario['max_devices']})"
            )
        
        # Validate topology structure
        structure_valid, structure_message = self._validate_topology_structure(
            topology_type, devices, connections
        )
        
        if not structure_valid:
            validation_errors.append(structure_message)
        
        # Calculate score
        is_valid = len(validation_errors) == 0
        score = self._calculate_score(
            topology_type, difficulty, completion_time, 
            is_valid, len(validation_errors), scenario
        )
        
        # Update progress if valid
        if is_valid:
            self._update_progress(user_id, topology_type, difficulty, score, completion_time)
        
        # Check for achievements
        achievements = self._check_achievements(user_id, topology_type, difficulty, score, completion_time)
        
        return {
            'valid': is_valid,
            'score': score,
            'errors': validation_errors,
            'feedback': structure_message if structure_valid else "Check the validation errors above",
            'achievements': achievements,
            'difficulty_multiplier': self.DIFFICULTY_MULTIPLIERS[difficulty]
        }
    
    def _validate_topology_structure(self, topology_type: str, devices: List[Dict], 
                                   connections: List[Dict]) -> Tuple[bool, str]:
        """Validate the topology structure based on type"""
        
        if topology_type == 'point-to-point':
            if len(devices) != 2:
                return False, "Point-to-point topology requires exactly 2 devices"
            if len(connections) != 1:
                return False, "Point-to-point topology requires exactly 1 connection"
            return True, "Valid point-to-point topology"
        
        elif topology_type == 'star':
            if len(devices) < 3:
                return False, "Star topology requires at least 3 devices"
            
            # Check for central device (most connections)
            connection_counts = {}
            for device in devices:
                connection_counts[device['id']] = 0
            
            for conn in connections:
                connection_counts[conn['device1']['id']] += 1
                connection_counts[conn['device2']['id']] += 1
            
            max_connections = max(connection_counts.values()) if connection_counts else 0
            central_devices = sum(1 for count in connection_counts.values() if count == max_connections)
            
            if central_devices != 1 or max_connections != len(devices) - 1:
                return False, "Star topology requires one central device connected to all others"
            
            return True, "Valid star topology"
        
        elif topology_type == 'mesh':
            if len(devices) < 3:
                return False, "Mesh topology requires at least 3 devices"
            
            # For full mesh, each device should connect to all others
            expected_connections = len(devices) * (len(devices) - 1) // 2
            if len(connections) < expected_connections:
                return False, f"Mesh topology requires {expected_connections} connections for full mesh"
            
            return True, "Valid mesh topology"
        
        elif topology_type == 'bus':
            if len(devices) < 3:
                return False, "Bus topology requires at least 3 devices"
            
            # Check for linear structure (each device has max 2 connections)
            connection_counts = {}
            for device in devices:
                connection_counts[device['id']] = 0
            
            for conn in connections:
                connection_counts[conn['device1']['id']] += 1
                connection_counts[conn['device2']['id']] += 1
            
            # In a bus, exactly 2 devices should have 1 connection (ends)
            # All others should have exactly 2 connections
            end_devices = sum(1 for count in connection_counts.values() if count == 1)
            middle_devices = sum(1 for count in connection_counts.values() if count == 2)
            
            if end_devices != 2 or middle_devices != len(devices) - 2:
                return False, "Bus topology requires linear connection pattern"
            
            return True, "Valid bus topology"
        
        elif topology_type == 'ring':
            if len(devices) < 3:
                return False, "Ring topology requires at least 3 devices"
            
            # Each device should have exactly 2 connections
            connection_counts = {}
            for device in devices:
                connection_counts[device['id']] = 0
            
            for conn in connections:
                connection_counts[conn['device1']['id']] += 1
                connection_counts[conn['device2']['id']] += 1
            
            if not all(count == 2 for count in connection_counts.values()):
                return False, "Ring topology requires each device to have exactly 2 connections"
            
            if len(connections) != len(devices):
                return False, f"Ring topology requires exactly {len(devices)} connections"
            
            return True, "Valid ring topology"
        
        elif topology_type == 'tree':
            if len(devices) < 3:
                return False, "Tree topology requires at least 3 devices"
            
            # Tree should have exactly n-1 connections where n is number of devices
            if len(connections) != len(devices) - 1:
                return False, f"Tree topology requires exactly {len(devices) - 1} connections"
            
            return True, "Valid tree topology"
        
        elif topology_type == 'hybrid':
            # Hybrid topologies are more flexible - just check basic connectivity
            if len(devices) < 4:
                return False, "Hybrid topology requires at least 4 devices"
            
            if len(connections) < len(devices) - 1:
                return False, "Hybrid topology requires sufficient connections for full connectivity"
            
            return True, "Valid hybrid topology"
        
        return False, "Unknown topology type"
    
    def _calculate_score(self, topology_type: str, difficulty: str, completion_time: int,
                        is_valid: bool, error_count: int, scenario: Dict) -> int:
        """Calculate score based on various factors"""
        if not is_valid:
            return 0
        
        base_score = 100
        time_limit = scenario['time_limit']
        
        # Apply difficulty multiplier
        difficulty_multiplier = self.DIFFICULTY_MULTIPLIERS[difficulty]
        base_score = int(base_score * difficulty_multiplier)
        
        # Time bonus (up to 50% of base score)
        time_bonus = 0
        if completion_time and completion_time < time_limit:
            time_efficiency = (time_limit - completion_time) / time_limit
            time_bonus = int(base_score * 0.5 * time_efficiency)
        
        # Perfect execution bonus
        perfect_bonus = 0
        if error_count == 0 and completion_time and completion_time < time_limit * 0.5:
            perfect_bonus = int(base_score * 0.3)
        
        total_score = base_score + time_bonus + perfect_bonus
        return max(0, min(1000, total_score))  # Cap at 1000 points
    
    def _update_progress(self, user_id: int, topology_type: str, difficulty: str,
                        score: int, completion_time: int = None):
        """Update user's progress for this topology"""
        progress = TopologyProgress.query.filter_by(
            user_id=user_id,
            topology_type=topology_type,
            difficulty=difficulty
        ).first()
        
        if not progress:
            progress = TopologyProgress(
                user_id=user_id,
                topology_type=topology_type,
                difficulty=difficulty
            )
            db.session.add(progress)
        
        # Update completion status
        progress.is_completed = True
        progress.completion_count += 1
        progress.last_completed = datetime.utcnow()
        
        # Update best score and time
        if score > progress.best_score:
            progress.best_score = score
        
        if completion_time and (not progress.best_time or completion_time < progress.best_time):
            progress.best_time = completion_time
        
        # Save to score table as well for leaderboards
        score_entry = Score(
            user_id=user_id,
            category='topology',
            subcategory=f"{topology_type}_{difficulty}",
            score=score,
            timestamp=datetime.utcnow()
        )
        db.session.add(score_entry)
        
        db.session.commit()
    
    def _check_achievements(self, user_id: int, topology_type: str, difficulty: str,
                          score: int, completion_time: int = None) -> List[Dict]:
        """Check and award achievements"""
        achievements_earned = []
        
        # First topology achievement
        total_completed = TopologyProgress.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).count()
        
        if total_completed == 1:
            achievements_earned.append(self.ACHIEVEMENTS['first_topology'])
        
        # Speed demon achievement
        if completion_time and completion_time < 60:
            achievements_earned.append(self.ACHIEVEMENTS['speed_demon'])
        
        # Perfectionist achievement
        if score >= 200:  # High score threshold
            achievements_earned.append(self.ACHIEVEMENTS['perfectionist'])
        
        # Difficulty master achievement
        user_progress = TopologyProgress.query.filter_by(
            user_id=user_id,
            topology_type=topology_type,
            is_completed=True
        ).all()
        
        completed_difficulties = {p.difficulty for p in user_progress}
        if len(completed_difficulties) == 3:  # Easy, Medium, Hard
            achievements_earned.append(self.ACHIEVEMENTS['difficulty_master'])
        
        # Topology expert achievement
        completed_types = {p.topology_type for p in TopologyProgress.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).all()}
        
        if len(completed_types) >= 6:  # All topology types
            achievements_earned.append(self.ACHIEVEMENTS['topology_expert'])
        
        return achievements_earned
    
    def get_user_progress(self, user_id: int) -> Dict:
        """Get comprehensive progress data for a user"""
        progress_records = TopologyProgress.query.filter_by(user_id=user_id).all()
        
        # Organize by topology type and difficulty
        progress_by_type = {}
        total_score = 0
        total_completed = 0
        
        for progress in progress_records:
            if progress.topology_type not in progress_by_type:
                progress_by_type[progress.topology_type] = {}
            
            progress_by_type[progress.topology_type][progress.difficulty] = {
                'is_completed': progress.is_completed,
                'best_score': progress.best_score,
                'completion_count': progress.completion_count,
                'best_time': progress.best_time,
                'last_completed': progress.last_completed.isoformat() if progress.last_completed else None
            }
            
            if progress.is_completed:
                total_score += progress.best_score
                total_completed += 1
        
        # Calculate overall statistics
        total_scenarios = sum(len(difficulties) for difficulties in self.topology_scenarios.values())
        completion_percentage = (total_completed / total_scenarios) * 100 if total_scenarios > 0 else 0
        
        return {
            'progress_by_type': progress_by_type,
            'total_score': total_score,
            'total_completed': total_completed,
            'total_scenarios': total_scenarios,
            'completion_percentage': round(completion_percentage, 1),
            'achievements_earned': self._get_user_achievements(user_id)
        }
    
    def _get_user_achievements(self, user_id: int) -> List[Dict]:
        """Get list of achievements earned by user"""
        # This would typically be stored in a separate achievements table
        # For now, we'll calculate based on current progress
        user_progress = TopologyProgress.query.filter_by(user_id=user_id).all()
        achievements = []
        
        completed_count = sum(1 for p in user_progress if p.is_completed)
        if completed_count > 0:
            achievements.append(self.ACHIEVEMENTS['first_topology'])
        
        # Check for other achievements based on stored data
        fast_completions = sum(1 for p in user_progress if p.best_time and p.best_time < 60)
        if fast_completions > 0:
            achievements.append(self.ACHIEVEMENTS['speed_demon'])
        
        high_scores = sum(1 for p in user_progress if p.best_score >= 200)
        if high_scores > 0:
            achievements.append(self.ACHIEVEMENTS['perfectionist'])
        
        return achievements
    
    def get_leaderboard(self, topology_type: str = None, difficulty: str = None, 
                       limit: int = 10) -> List[Dict]:
        """Get leaderboard data for topology challenges"""
        query = db.session.query(
            User.username,
            User.id,
            func.max(Score.score).label('best_score'),
            func.count(Score.id).label('attempt_count')
        ).join(Score, User.id == Score.user_id).filter(
            Score.category == 'topology'
        )
        
        if topology_type and difficulty:
            query = query.filter(Score.subcategory == f"{topology_type}_{difficulty}")
        elif topology_type:
            query = query.filter(Score.subcategory.like(f"{topology_type}_%"))
        
        query = query.group_by(User.id, User.username).order_by(
            func.max(Score.score).desc()
        ).limit(limit)
        
        results = query.all()
        
        leaderboard = []
        for i, (username, user_id, best_score, attempt_count) in enumerate(results, 1):
            leaderboard.append({
                'rank': i,
                'username': username,
                'user_id': user_id,
                'best_score': best_score,
                'attempt_count': attempt_count
            })
        
        return leaderboard
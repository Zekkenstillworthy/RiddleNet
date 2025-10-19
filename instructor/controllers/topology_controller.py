from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from __init__ import db
from instructor.models.topology import Topology
from datetime import datetime

class TopologyController:
    """Controller for Topology-related operations"""
    
    def get_all_topologies(self):
        """Get all topology challenges"""
        try:
            topologies = Topology.query.all()
            return jsonify({
                "status": "success",
                "topologies": [self._serialize_topology(topology) for topology in topologies]
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_topology(self, topology_id):
        """Get a specific topology challenge by ID"""
        try:
            topology = Topology.query.get(topology_id)
            if not topology:
                return jsonify({"status": "error", "message": "Topology not found"}), 404
            
            return jsonify({
                "status": "success",
                "topology": self._serialize_topology(topology)
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def create_topology(self, data):
        """Create a new topology challenge"""
        try:
            # Create a new topology
            topology = Topology(
                title=data.get('title'),
                description=data.get('description'),
                difficulty=data.get('difficulty', 'medium'),
                topology_type=data.get('topology_type', 'point-to-point'),
                base_score=data.get('base_score', 10),
                time_bonus=data.get('time_bonus', 0),
                perfect_match_bonus=data.get('perfect_match_bonus', 5),
                is_active=data.get('is_active', True)
            )
            
            # Set complex properties
            if 'initial_config' in data:
                topology.initial_config = data['initial_config']
            
            if 'expected_config' in data:
                topology.expected_config = data['expected_config']
            
            if 'scoring_metrics' in data:
                topology.scoring_metrics = data['scoring_metrics']
            
            if 'device_requirements' in data:
                topology.device_requirements = data['device_requirements']
            
            # Save to database
            db.session.add(topology)
            db.session.commit()
            
            return jsonify({
                "status": "success", 
                "message": "Topology created successfully",
                "topology": self._serialize_topology(topology)
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def update_topology(self, topology_id, data):
        """Update an existing topology challenge"""
        try:
            topology = Topology.query.get(topology_id)
            if not topology:
                return jsonify({"status": "error", "message": "Topology not found"}), 404
            
            # Update basic fields
            if 'title' in data:
                topology.title = data['title']
            if 'description' in data:
                topology.description = data['description']
            if 'difficulty' in data:
                topology.difficulty = data['difficulty']
            if 'topology_type' in data:
                topology.topology_type = data['topology_type']
            if 'base_score' in data:
                topology.base_score = data['base_score']
            if 'time_bonus' in data:
                topology.time_bonus = data['time_bonus']
            if 'perfect_match_bonus' in data:
                topology.perfect_match_bonus = data['perfect_match_bonus']
            if 'is_active' in data:
                topology.is_active = data['is_active']
            
            # Update complex properties
            if 'initial_config' in data:
                topology.initial_config = data['initial_config']
            if 'expected_config' in data:
                topology.expected_config = data['expected_config']
            if 'scoring_metrics' in data:
                topology.scoring_metrics = data['scoring_metrics']
            if 'device_requirements' in data:
                topology.device_requirements = data['device_requirements']
            
            # Update timestamp
            topology.updated_at = datetime.utcnow()
            
            # Save to database
            db.session.commit()
            
            return jsonify({
                "status": "success", 
                "message": "Topology updated successfully",
                "topology": self._serialize_topology(topology)
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def delete_topology(self, topology_id):
        """Delete a topology challenge"""
        try:
            topology = Topology.query.get(topology_id)
            if not topology:
                return jsonify({"status": "error", "message": "Topology not found"}), 404
            
            db.session.delete(topology)
            db.session.commit()
            
            return jsonify({
                "status": "success", 
                "message": "Topology deleted successfully"
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def toggle_active_status(self, topology_id):
        """Toggle the active status of a topology challenge"""
        try:
            topology = Topology.query.get(topology_id)
            if not topology:
                return jsonify({"status": "error", "message": "Topology not found"}), 404
            
            topology.is_active = not topology.is_active
            db.session.commit()
            
            return jsonify({
                "status": "success", 
                "message": f"Topology is now {'active' if topology.is_active else 'inactive'}",
                "is_active": topology.is_active
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def preview_topology(self, topology_id):
        """Get a topology in a format suitable for previewing"""
        try:
            topology = Topology.query.get(topology_id)
            if not topology:
                return jsonify({"status": "error", "message": "Topology not found"}), 404
            
            # Return a simplified version for preview purposes
            preview_data = {
                "id": topology.id,
                "title": topology.title,
                "description": topology.description,
                "difficulty": topology.difficulty,
                "topology_type": topology.topology_type,
                "initial_config": topology.initial_config,
                "device_requirements": topology.device_requirements,
                "is_active": topology.is_active
            }
            
            return jsonify({
                "status": "success", 
                "preview": preview_data
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def get_topology_types(self):
        """Get all available topology types"""
        try:
            # Get distinct topology types from the database
            topology_types = db.session.query(Topology.topology_type).distinct().all()
            topology_types = [t[0] for t in topology_types]
            
            # If no types in the database yet, return the default ones
            if not topology_types:
                topology_types = [
                    'point-to-point', 'mesh', 'star', 'bus', 'ring', 'tree', 'hybrid'
                ]
            
            return jsonify({
                "status": "success",
                "topology_types": topology_types
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def _serialize_topology(self, topology):
        """Helper method to serialize a topology model to a dictionary"""
        return {
            "id": topology.id,
            "title": topology.title,
            "description": topology.description,
            "difficulty": topology.difficulty,
            "topology_type": topology.topology_type,
            "initial_config": topology.initial_config,
            "expected_config": topology.expected_config,
            "scoring_metrics": topology.scoring_metrics,
            "device_requirements": topology.device_requirements,
            "base_score": topology.base_score,
            "time_bonus": topology.time_bonus,
            "perfect_match_bonus": topology.perfect_match_bonus,
            "is_active": topology.is_active,
            "created_at": topology.created_at.isoformat() if topology.created_at else None,
            "updated_at": topology.updated_at.isoformat() if topology.updated_at else None
        }
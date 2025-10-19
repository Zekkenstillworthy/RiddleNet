from flask import request, jsonify
from __init__ import db
from instructor.models.troubleshooting import Troubleshooting
from instructor.models.troubleshooting_progress import TroubleshootingProgress
from datetime import datetime
from sqlalchemy import func, desc

class TroubleshootingController:

    def get_all_troubleshooting(self):
        try:
            items = Troubleshooting.query.all()
            return jsonify([item.to_dict() for item in items]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_troubleshooting(self, troubleshooting_id):
        try:
            item = Troubleshooting.query.get_or_404(troubleshooting_id)
            return jsonify(item.to_dict()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def create_troubleshooting(self):
        data = request.json
        if not data or not all(k in data for k in ['title', 'description', 'scenario', 'solution']):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            new_item = Troubleshooting(
                title=data['title'],
                description=data['description'],
                difficulty=data.get('difficulty', 'medium'),
                scenario=data['scenario'],
                solution=data['solution'],
                base_score=data.get('base_score', 100),
                time_bonus=data.get('time_bonus', 20),
                perfect_match_bonus=data.get('perfect_match_bonus', 10),
                topology_type=data.get('topology_type'),
                is_active=data.get('is_active', True)
            )
            if 'hints' in data:
                new_item.hints = data['hints']
            if 'scoring_metrics' in data:
                new_item.scoring_metrics = data['scoring_metrics']
            if 'required_devices' in data:
                new_item.required_devices = data['required_devices']
            if 'topology_config' in data:
                new_item.topology_config = data['topology_config']
            if 'initial_topology' in data:
                new_item.initial_topology = data['initial_topology']
            if 'expected_topology' in data:
                new_item.expected_topology = data['expected_topology']
            db.session.add(new_item)
            db.session.commit()
            return jsonify({"message": "Troubleshooting created successfully", "id": new_item.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    def update_troubleshooting(self, troubleshooting_id):
        item = Troubleshooting.query.get_or_404(troubleshooting_id)
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        try:
            for field in ['title', 'description', 'difficulty', 'scenario', 'solution', 'base_score', 'time_bonus', 'perfect_match_bonus', 'topology_type', 'is_active']:
                if field in data:
                    setattr(item, field, data[field])
            if 'hints' in data:
                item.hints = data['hints']
            if 'scoring_metrics' in data:
                item.scoring_metrics = data['scoring_metrics']
            if 'required_devices' in data:
                item.required_devices = data['required_devices']
            if 'topology_config' in data:
                item.topology_config = data['topology_config']
            if 'initial_topology' in data:
                item.initial_topology = data['initial_topology']
            if 'expected_topology' in data:
                item.expected_topology = data['expected_topology']
            item.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({"message": "Troubleshooting updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    def delete_troubleshooting(self, troubleshooting_id):
        item = Troubleshooting.query.get_or_404(troubleshooting_id)
        try:
            # Instead of hard delete, mark as inactive
            item.is_active = False
            item.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({"success": True, "message": "Troubleshooting scenario deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
            
    def list_troubleshootings(self, page=1, per_page=10, search='', difficulty=''):
        """Get paginated list of troubleshooting scenarios with filtering options"""
        try:
            query = Troubleshooting.query
            
            # Apply filters
            if search:
                query = query.filter(Troubleshooting.title.ilike(f'%{search}%') | 
                                    Troubleshooting.description.ilike(f'%{search}%'))
            
            if difficulty:
                query = query.filter(Troubleshooting.difficulty == difficulty)
            
            # Get total count for pagination
            total = query.count()
            
            # Apply pagination
            items = query.order_by(desc(Troubleshooting.created_at)).paginate(page=page, per_page=per_page, error_out=False)
            
            result = {
                "troubleshootings": [item.to_dict() for item in items.items],
                "pagination": {
                    "total": total,
                    "pages": items.pages,
                    "current_page": page,
                    "per_page": per_page,
                    "has_next": items.has_next,
                    "has_prev": items.has_prev
                }
            }
            
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_troubleshooting_stats(self):
        """Get statistics about troubleshooting scenarios usage"""
        try:
            stats = {}
            
            # Total scenarios
            stats["total_scenarios"] = Troubleshooting.query.count()
            stats["active_scenarios"] = Troubleshooting.query.filter_by(is_active=True).count()
            
            # Scenarios by difficulty
            difficulty_counts = db.session.query(
                Troubleshooting.difficulty, 
                func.count(Troubleshooting.id)
            ).group_by(Troubleshooting.difficulty).all()
            
            stats["by_difficulty"] = {difficulty: count for difficulty, count in difficulty_counts}
            
            # Get usage stats
            total_attempts = TroubleshootingProgress.query.count()
            completed_attempts = TroubleshootingProgress.query.filter_by(is_completed=True).count()
            
            stats["usage"] = {
                "total_attempts": total_attempts,
                "completed_attempts": completed_attempts,
                "completion_rate": round((completed_attempts / total_attempts) * 100, 2) if total_attempts > 0 else 0
            }
            
            # Most popular scenarios
            popular_scenarios = db.session.query(
                Troubleshooting.id,
                Troubleshooting.title,
                func.count(TroubleshootingProgress.id).label('attempt_count')
            ).join(TroubleshootingProgress, TroubleshootingProgress.troubleshooting_id == Troubleshooting.id) \
             .group_by(Troubleshooting.id) \
             .order_by(desc('attempt_count')) \
             .limit(5) \
             .all()
            
            stats["popular_scenarios"] = [
                {"id": id, "title": title, "attempts": attempts} 
                for id, title, attempts in popular_scenarios
            ]
            
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def preview_troubleshooting(self):
        """Generate a preview of a troubleshooting scenario without saving it"""
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        try:
            # Create a transient object (not added to the session)
            preview = Troubleshooting(
                title=data.get('title', 'Preview Title'),
                description=data.get('description', 'Preview Description'),
                difficulty=data.get('difficulty', 'medium'),
                scenario=data.get('scenario', 'Preview Scenario'),
                solution=data.get('solution', 'Preview Solution'),
                base_score=data.get('base_score', 100),
                time_bonus=data.get('time_bonus', 20),
                perfect_match_bonus=data.get('perfect_match_bonus', 10),
                topology_type=data.get('topology_type', 'default')
            )
            
            # Handle JSON fields
            if 'hints' in data:
                preview.hints = data['hints']
            if 'scoring_metrics' in data:
                preview.scoring_metrics = data['scoring_metrics']
            if 'required_devices' in data:
                preview.required_devices = data['required_devices']
            if 'topology_config' in data:
                preview.topology_config = data['topology_config']
            if 'initial_topology' in data:
                preview.initial_topology = data['initial_topology']
            if 'expected_topology' in data:
                preview.expected_topology = data['expected_topology']
                
            # Convert to dict without saving to database
            result = preview.to_dict()
            return jsonify({"status": "success", "preview": result}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def toggle_troubleshooting_status(self, troubleshooting_id, action='toggle'):
        """Toggle or set the active status of a troubleshooting scenario"""
        item = Troubleshooting.query.get_or_404(troubleshooting_id)
        
        try:
            if action == 'activate':
                item.is_active = True
                message = "Troubleshooting scenario activated successfully"
            elif action == 'deactivate':
                item.is_active = False
                message = "Troubleshooting scenario deactivated successfully"
            else:  # toggle
                item.is_active = not item.is_active
                message = f"Troubleshooting scenario {'activated' if item.is_active else 'deactivated'} successfully"
                
            item.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                "message": message,
                "is_active": item.is_active,
                "id": item.id
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
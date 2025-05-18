from flask import request, jsonify
from __init__ import db
from admin.models.troubleshooting import Troubleshooting
from datetime import datetime

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
                is_active=data.get('is_active', True)
            )
            if 'hints' in data:
                new_item.hints = data['hints']
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
            for field in ['title', 'description', 'difficulty', 'scenario', 'solution', 'is_active']:
                if field in data:
                    setattr(item, field, data[field])
            if 'hints' in data:
                item.hints = data['hints']
            item.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({"message": "Troubleshooting updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    def delete_troubleshooting(self, troubleshooting_id):
        item = Troubleshooting.query.get_or_404(troubleshooting_id)
        try:
            db.session.delete(item)
            db.session.commit()
            return jsonify({"message": "Troubleshooting deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
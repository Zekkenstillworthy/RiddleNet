"""
RNet File Viewer Routes
Handles displaying RNet files with embedded QR codes
"""

from flask import Blueprint, render_template, request, jsonify, send_file, abort
from flask_login import login_required
import json
import os
from datetime import datetime
import tempfile
import base64
from io import BytesIO

# Create blueprint
rnet_viewer_bp = Blueprint('rnet_viewer', __name__, url_prefix='/rnet')


@rnet_viewer_bp.route('/viewer')
def view_rnet_file():
    """Display RNet file viewer interface"""
    return render_template('admin/rnet_file_viewer.html')


@rnet_viewer_bp.route('/api/parse', methods=['POST'])
def parse_rnet_file():
    """Parse uploaded RNet file and extract data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        if not file.filename.lower().endswith('.rnet'):
            return jsonify({'error': 'Invalid file format. Please upload a .rnet file'}), 400
        
        # Parse file content
        try:
            file_content = file.read().decode('utf-8')
            rnet_data = json.loads(file_content)
        except Exception as e:
            return jsonify({'error': f'Invalid file format: {str(e)}'}), 400
        
        # Validate RNet file format
        if rnet_data.get('format') != 'rnetfile':
            return jsonify({'error': 'Invalid RNet file format'}), 400
        
        # Extract key information
        simulation = rnet_data.get('simulation', {})
        verification = rnet_data.get('verification', {})
        export_metadata = rnet_data.get('export_metadata', {})
        
        response_data = {
            'success': True,
            'file_info': {
                'filename': file.filename,
                'format': rnet_data.get('format'),
                'version': rnet_data.get('version'),
                'exported_at': rnet_data.get('exported_at'),
                'exported_by': rnet_data.get('exported_by')
            },
            'simulation_info': {
                'id': simulation.get('id'),
                'title': simulation.get('title'),
                'description': simulation.get('description'),
                'simulation_type': simulation.get('simulation_type'),
                'category': simulation.get('category'),
                'difficulty': simulation.get('difficulty'),
                'estimated_duration': simulation.get('estimated_duration')
            },
            'verification_info': {
                'qr_code_included': verification.get('qr_code_included', False),
                'qr_code_base64': verification.get('qr_code_base64'),
                'confirmation_url': verification.get('confirmation_url'),
                'instructions': verification.get('instructions'),
                'qr_metadata': verification.get('qr_metadata')
            },
            'export_metadata': export_metadata
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to parse file: {str(e)}'}), 500


@rnet_viewer_bp.route('/api/qr-image/<file_id>')
def get_qr_image(file_id):
    """Serve QR code image from session or temporary storage"""
    try:
        # This is a simplified version - in production, you'd want to store
        # the QR code data temporarily with a session-based ID
        # For now, we'll expect the QR code data to be passed via query params
        qr_base64 = request.args.get('data')
        
        if not qr_base64:
            abort(404)
        
        # Decode base64 image
        img_data = base64.b64decode(qr_base64)
        
        return send_file(
            BytesIO(img_data),
            mimetype='image/png',
            as_attachment=False,
            download_name=f'qr_code_{file_id}.png'
        )
        
    except Exception as e:
        abort(500)
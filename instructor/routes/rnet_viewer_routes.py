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
rnet_viewer_bp = Blueprint('rnet_viewer', __name__, url_prefix='/instructor/rnet')


@rnet_viewer_bp.route('/viewer')
def view_rnet_file():
    """Display RNet file viewer interface"""
    return render_template('instructor/rnet_file_viewer.html', active_page='rnet_viewer')


@rnet_viewer_bp.route('/api/parse', methods=['POST'])
def parse_rnet_file():
    """Parse uploaded RNet file and extract data"""
    print("\n" + "="*80)
    print("🔍 RNET FILE PARSE REQUEST")
    print("="*80)
    
    try:
        print(f"📋 Request method: {request.method}")
        print(f"📋 Request content type: {request.content_type}")
        print(f"📋 Request files: {list(request.files.keys())}")
        print(f"📋 Request form: {list(request.form.keys())}")
        
        if 'file' not in request.files:
            print("❌ No 'file' key in request.files")
            print(f"   Available keys: {list(request.files.keys())}")
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        print(f"✅ File object received: {file}")
        print(f"📄 Filename: {file.filename}")
        print(f"📄 Content type: {file.content_type}")
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        if not file.filename.lower().endswith('.rnet'):
            print(f"❌ Invalid file extension: {file.filename}")
            return jsonify({'error': 'Invalid file format. Please upload a .rnet file'}), 400
        
        print("✅ File validation passed")
        
        # Parse file content
        try:
            print("📖 Reading file content...")
            file_content = file.read().decode('utf-8')
            print(f"✅ File read successfully, length: {len(file_content)} characters")
            print(f"📋 First 200 chars: {file_content[:200]}...")
            
            print("🔧 Parsing JSON...")
            rnet_data = json.loads(file_content)
            print(f"✅ JSON parsed successfully")
            print(f"📋 Top-level keys: {list(rnet_data.keys())}")
            
        except UnicodeDecodeError as e:
            print(f"❌ Unicode decode error: {str(e)}")
            return jsonify({'error': f'File encoding error: {str(e)}'}), 400
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {str(e)}")
            print(f"   Position: {e.pos}")
            print(f"   Line: {e.lineno}, Column: {e.colno}")
            return jsonify({'error': f'Invalid JSON format: {str(e)}'}), 400
        except Exception as e:
            print(f"❌ Unexpected parsing error: {str(e)}")
            return jsonify({'error': f'Invalid file format: {str(e)}'}), 400
        
        # Validate RNet file format
        file_format = rnet_data.get('format')
        print(f"📋 File format field: {file_format}")
        
        if file_format != 'rnetfile':
            print(f"❌ Invalid RNet file format: {file_format}")
            return jsonify({'error': 'Invalid RNet file format'}), 400
        
        print("✅ RNet format validation passed")
        
        # Extract key information
        simulation = rnet_data.get('simulation', {})
        verification = rnet_data.get('verification', {})
        export_metadata = rnet_data.get('export_metadata', {})
        
        print(f"📋 Simulation data keys: {list(simulation.keys())}")
        print(f"📋 Verification data keys: {list(verification.keys())}")
        print(f"📋 Export metadata keys: {list(export_metadata.keys())}")
        
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
        
        print("✅ Response data prepared successfully")
        print(f"📋 Response keys: {list(response_data.keys())}")
        print(f"📋 QR code included: {response_data['verification_info']['qr_code_included']}")
        print("="*80)
        print("✅ PARSE SUCCESSFUL - Returning response")
        print("="*80 + "\n")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in parse_rnet_file:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")
        print("="*80 + "\n")
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
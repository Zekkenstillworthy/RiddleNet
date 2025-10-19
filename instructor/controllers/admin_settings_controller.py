"""
Admin Settings Controller
Centralized configuration management for admin settings
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from utils.auth_decorators import instructor_required
from config.defaults import DEFAULTS, get_default
from __init__ import db
import os
import json

admin_settings_bp = Blueprint('admin_settings', __name__, url_prefix='/admin/settings')


@admin_settings_bp.route('/')
@login_required
@instructor_required
def admin_settings_page():
    """Render the admin settings page"""
    return render_template('instructor/admin_settings.html',
                         defaults=DEFAULTS,
                         active_page='admin_settings')


@admin_settings_bp.route('/api/defaults', methods=['GET'])
@login_required
@instructor_required
def get_all_defaults():
    """Get all default configuration values"""
    return jsonify({
        'success': True,
        'defaults': DEFAULTS,
        'documentation': {
            'grading': {
                'rounding': 'How to round final grades (nearest, up, down)',
                'min_passing_percentage': 'Minimum percentage required to pass',
                'partial_credit_enabled': 'Allow partial credit on assignments'
            },
            'deadlines': {
                'late_penalty_per_day': 'Points deducted per day late',
                'grace_minutes': 'Grace period in minutes after deadline',
                'allow_late_submissions': 'Whether to accept late submissions'
            },
            'gamification': {
                'hint_penalty_points': 'Points deducted for using hints',
                'combo_bonus': 'Bonus points for consecutive correct answers'
            },
            'validation': {
                'max_connectivity_tests': 'Maximum connectivity tests per simulation',
                'max_devices': 'Maximum devices allowed per simulation'
            }
        }
    })


@admin_settings_bp.route('/api/defaults/<path:setting_path>', methods=['GET'])
@login_required
@instructor_required
def get_setting(setting_path):
    """Get a specific setting value"""
    value = get_default(setting_path)
    if value is None:
        return jsonify({'error': 'Setting not found'}), 404
    
    return jsonify({
        'success': True,
        'path': setting_path,
        'value': value
    })


@admin_settings_bp.route('/api/defaults/<path:setting_path>', methods=['PUT'])
@login_required
@instructor_required
def update_setting(setting_path):
    """Update a specific setting value"""
    try:
        data = request.json or {}
        new_value = data.get('value')
        
        if new_value is None:
            return jsonify({'error': 'Value is required'}), 400
        
        # Navigate to the setting in DEFAULTS
        parts = setting_path.split('.')
        node = DEFAULTS
        for part in parts[:-1]:
            if part not in node:
                return jsonify({'error': 'Invalid setting path'}), 400
            node = node[part]
        
        if parts[-1] not in node:
            return jsonify({'error': 'Invalid setting path'}), 400
        
        # Validate the new value type matches the existing type
        old_value = node[parts[-1]]
        if type(new_value) != type(old_value):
            return jsonify({'error': f'Value must be of type {type(old_value).__name__}'}), 400
        
        # Update the value
        node[parts[-1]] = new_value
        
        # Save to persistent storage (you might want to implement this)
        _save_defaults_to_file()
        
        return jsonify({
            'success': True,
            'message': f'Setting {setting_path} updated successfully',
            'old_value': old_value,
            'new_value': new_value
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_settings_bp.route('/api/defaults/reset', methods=['POST'])
@login_required
@instructor_required
def reset_defaults():
    """Reset all defaults to factory settings"""
    try:
        # Only super_admin can reset all defaults
        if not hasattr(current_user, 'role') or current_user.role != 'super_admin':
            return jsonify({'error': 'Super admin access required'}), 403
        
        # Reset to factory defaults
        _reset_to_factory_defaults()
        
        return jsonify({
            'success': True,
            'message': 'All defaults reset to factory settings'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_settings_bp.route('/api/defaults/export', methods=['GET'])
@login_required
@instructor_required
def export_defaults():
    """Export current defaults as JSON"""
    return jsonify({
        'success': True,
        'defaults': DEFAULTS,
        'exported_at': __import__('datetime').datetime.utcnow().isoformat()
    })


@admin_settings_bp.route('/api/defaults/import', methods=['POST'])
@login_required
@instructor_required
def import_defaults():
    """Import defaults from JSON"""
    try:
        # Only super_admin can import defaults
        if not hasattr(current_user, 'role') or current_user.role != 'super_admin':
            return jsonify({'error': 'Super admin access required'}), 403
        
        data = request.json or {}
        imported_defaults = data.get('defaults')
        
        if not imported_defaults:
            return jsonify({'error': 'No defaults provided'}), 400
        
        # Validate structure
        if not _validate_defaults_structure(imported_defaults):
            return jsonify({'error': 'Invalid defaults structure'}), 400
        
        # Update DEFAULTS
        DEFAULTS.update(imported_defaults)
        
        # Save to persistent storage
        _save_defaults_to_file()
        
        return jsonify({
            'success': True,
            'message': 'Defaults imported successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _save_defaults_to_file():
    """Save current defaults to a persistent file"""
    try:
        config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
        overrides_file = os.path.join(config_dir, 'defaults_overrides.json')
        
        with open(overrides_file, 'w') as f:
            json.dump(DEFAULTS, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving defaults: {e}")
        return False


def _reset_to_factory_defaults():
    """Reset DEFAULTS to original factory values"""
    global DEFAULTS
    DEFAULTS.clear()
    DEFAULTS.update({
        'grading': {
            'rounding': 'nearest',
            'min_passing_percentage': 60,
            'partial_credit_enabled': True,
        },
        'deadlines': {
            'late_penalty_per_day': 10.0,
            'grace_minutes': 10,
            'allow_late_submissions': True,
        },
        'gamification': {
            'hint_penalty_points': 5,
            'combo_bonus': 10,
        },
        'validation': {
            'max_connectivity_tests': 50,
            'max_devices': 50,
        },
    })
    _save_defaults_to_file()


def _validate_defaults_structure(defaults):
    """Validate that the defaults structure is correct"""
    required_sections = ['grading', 'deadlines', 'gamification', 'validation']
    
    if not isinstance(defaults, dict):
        return False
    
    for section in required_sections:
        if section not in defaults:
            return False
        if not isinstance(defaults[section], dict):
            return False
    
    return True


# Load overrides on module import
def _load_defaults_overrides():
    """Load defaults overrides from file if they exist"""
    try:
        config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
        overrides_file = os.path.join(config_dir, 'defaults_overrides.json')
        
        if os.path.exists(overrides_file):
            with open(overrides_file, 'r') as f:
                overrides = json.load(f)
            DEFAULTS.update(overrides)
            print("✅ Loaded defaults overrides from file")
    except Exception as e:
        print(f"⚠️ Could not load defaults overrides: {e}")


# Load overrides when module is imported
_load_defaults_overrides()

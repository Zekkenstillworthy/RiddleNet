from flask import Blueprint, render_template
from flask_login import login_required
from utils.permission_decorators import admin_required

collaboration_test_bp = Blueprint('collaboration_test', __name__, url_prefix='/admin/test')

@collaboration_test_bp.route('/collaboration')
@login_required
@admin_required
def collaboration_test():
    """Test page for collaboration functionality"""
    return render_template('admin/collaboration_test.html')
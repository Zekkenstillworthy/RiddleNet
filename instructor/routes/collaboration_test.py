from flask import Blueprint, render_template
from flask_login import login_required
from utils.permission_decorators import instructor_required

collaboration_test_bp = Blueprint('collaboration_test', __name__, url_prefix='/instructor/test')

@collaboration_test_bp.route('/collaboration')
@login_required
@instructor_required
def collaboration_test():
    """Test page for collaboration functionality"""
    return render_template('instructor/collaboration_test.html')

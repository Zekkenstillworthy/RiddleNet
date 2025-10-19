from flask import Blueprint, render_template
from flask_login import login_required
from utils.permission_decorators import teacher_required
from instructor.models.lab import Lab


instructor_lab_bp = Blueprint('instructor_lab_bp', __name__, template_folder='../../templates')


@instructor_lab_bp.route('/admin/labs/dashboard')
@login_required
@teacher_required
def labs_dashboard():
    labs = Lab.query.order_by(Lab.created_at.desc()).all()
    return render_template('instructor/instructor_labs_dashboard.html', labs=labs)

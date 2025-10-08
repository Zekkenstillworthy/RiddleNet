from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from __init__ import db
import json

# Create separate blueprint for quiz challenges
quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@quiz_bp.route('/')
@login_required
def index():
    """Show quiz challenge page"""
    # Get user data from database like other routes to ensure consistent user data
    user = None
    
    # Try to get user from session first
    if 'user_id' in session:
        try:
            from user.models.user import User as UserModel
            user = UserModel.query.get(session['user_id'])
        except Exception as e:
            print(f"Error getting user from session: {e}")
    
    # If no session user found, fallback to current_user
    if not user and current_user.is_authenticated:
        user = current_user
    
    # If still no user, try to get authenticated user info another way
    if not user:
        try:
            from user.models.user import User as UserModel
            if hasattr(current_user, 'id') and current_user.id:
                user = UserModel.query.get(current_user.id)
        except Exception as e:
            print(f"Error getting current user: {e}")
    
    print(f"Quiz route - User: {user.username if user else 'None'}")
    return render_template('user/quiz_challenge.html', user=user)

@quiz_bp.route('/test-images')
def test_images():
    """Test page to verify topology images are loaded correctly"""
    return render_template('test_images.html')

@quiz_bp.route('/api/submit', methods=['POST'])
@login_required
def submit_quiz():
    """Submit quiz results"""
    try:
        data = request.json
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        time_taken = data.get('time_taken', 0)
        lifelines_used = data.get('lifelines_used', {})
        
        # Save score to database
        from user.models.score import Score
        new_score = Score(
            score=score,
            user_id=current_user.id,
            category='quiz_challenge'
        )
        db.session.add(new_score)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quiz results saved successfully!',
            'score': score,
            'total': total_questions,
            'percentage': (score / total_questions * 100) if total_questions > 0 else 0
        })
    except Exception as e:
        print(f"Error submitting quiz: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

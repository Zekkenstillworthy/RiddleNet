from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from __init__ import db
from datetime import datetime
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
    """Submit quiz results (MVP with Badge System)"""
    try:
        data = request.json
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        time_taken = data.get('time_taken', 0)
        lifelines_used = data.get('lifelines_used', {})
        
        # Calculate percentage score
        score_percentage = (score / total_questions * 100) if total_questions > 0 else 0
        
        # Save to legacy Score table
        from user.models.score import Score
        new_score = Score(
            score=score_percentage,  # Store as percentage
            user_id=current_user.id,
            category='quiz_challenge'
        )
        db.session.add(new_score)
        
        # Save to new ChallengeScore table
        from user.models.challenge_score import ChallengeScore
        challenge_score = ChallengeScore.save_score(
            user_id=current_user.id,
            challenge_type='quiz',
            score=score_percentage,
            metadata={
                'total_questions': total_questions,
                'correct_answers': score,
                'time_taken': time_taken,
                'lifelines_used': lifelines_used
            },
            completion_time=time_taken
        )
        
        # Check and award badges
        from user.services.badge_service import BadgeService
        newly_earned_badges = BadgeService.check_and_award_badges(
            user_id=current_user.id,
            challenge_type='quiz',
            score=score_percentage,
            metadata={'total_questions': total_questions, 'lifelines_used': lifelines_used}
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quiz results saved successfully!',
            'score': score,
            'total': total_questions,
            'percentage': score_percentage,
            'badges_earned': newly_earned_badges,
            'challenge_completed': challenge_score.is_completed
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting quiz: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@quiz_bp.route('/api/save_progress', methods=['POST'])
@login_required
def save_progress():
    """Save quiz progress for later resumption"""
    try:
        data = request.json
        
        # Store progress in ChallengeScore metadata
        from user.models.challenge_score import ChallengeScore
        
        # Get or create challenge score entry
        challenge_score = ChallengeScore.query.filter_by(
            user_id=current_user.id,
            challenge_type='quiz'
        ).first()
        
        if not challenge_score:
            challenge_score = ChallengeScore(
                user_id=current_user.id,
                challenge_type='quiz',
                best_score=0.0,
                latest_score=0.0,
                total_attempts=0
            )
            db.session.add(challenge_score)
        
        # Update metadata with progress
        if not challenge_score.challenge_metadata:
            challenge_score.challenge_metadata = {}
        
        challenge_score.challenge_metadata['in_progress'] = True
        challenge_score.challenge_metadata['progress'] = {
            'currentQuestion': data.get('currentQuestion', 0),
            'score': data.get('score', 0),
            'answeredQuestions': data.get('answeredQuestions', []),
            'lifelinesUsed': data.get('lifelinesUsed', {}),
            'questionOrder': data.get('questionOrder', []),
            'totalQuestions': data.get('totalQuestions', 11),
            'sessionId': data.get('sessionId'),
            'savedAt': datetime.now().isoformat()
        }
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress saved successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error saving progress: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@quiz_bp.route('/api/get_progress', methods=['GET'])
@login_required
def get_progress():
    """Get saved quiz progress"""
    try:
        from user.models.challenge_score import ChallengeScore
        
        challenge_score = ChallengeScore.query.filter_by(
            user_id=current_user.id,
            challenge_type='quiz'
        ).first()
        
        if challenge_score and challenge_score.challenge_metadata:
            in_progress = challenge_score.challenge_metadata.get('in_progress', False)
            progress = challenge_score.challenge_metadata.get('progress', {})
            
            if in_progress and progress:
                return jsonify({
                    'has_progress': True,
                    'progress': progress
                })
        
        return jsonify({
            'has_progress': False
        })
    except Exception as e:
        print(f"Error getting progress: {e}")
        return jsonify({'has_progress': False, 'error': str(e)}), 500

@quiz_bp.route('/api/clear_progress', methods=['POST'])
@login_required
def clear_progress():
    """Clear saved quiz progress"""
    try:
        from user.models.challenge_score import ChallengeScore
        
        challenge_score = ChallengeScore.query.filter_by(
            user_id=current_user.id,
            challenge_type='quiz'
        ).first()
        
        if challenge_score and challenge_score.challenge_metadata:
            if 'in_progress' in challenge_score.challenge_metadata:
                del challenge_score.challenge_metadata['in_progress']
            if 'progress' in challenge_score.challenge_metadata:
                del challenge_score.challenge_metadata['progress']
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress cleared successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing progress: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

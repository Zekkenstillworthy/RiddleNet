"""
Live Quiz Routes - Slido-style quiz with real-time leaderboard
"""
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from __init__ import db
from datetime import datetime
import random
import string

# Create blueprint
live_quiz_bp = Blueprint('live_quiz', __name__, url_prefix='/api/live-quiz')


def generate_session_code():
    """Generate a unique 6-character session code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        from user.models.live_quiz import LiveQuizSession
        if not LiveQuizSession.query.filter_by(session_code=code).first():
            return code


@live_quiz_bp.route('/sessions/<int:module_id>', methods=['GET'])
@login_required
def get_module_quiz_sessions(module_id):
    """Get active quiz sessions for a module"""
    try:
        from user.models.live_quiz import LiveQuizSession
        
        # Get active sessions for this module
        sessions = LiveQuizSession.query.filter_by(
            module_id=module_id,
            status='active'
        ).all()
        
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        })
    except Exception as e:
        print(f"Error getting quiz sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_bp.route('/join', methods=['POST'])
@login_required  
def join_quiz():
    """Join a live quiz session"""
    print("🎯 [JOIN_QUIZ] Route handler called!")
    print(f"🎯 [JOIN_QUIZ] Request method: {request.method}")
    print(f"🎯 [JOIN_QUIZ] Request path: {request.path}")
    print(f"🎯 [JOIN_QUIZ] Current user: {current_user}")
    print(f"🎯 [JOIN_QUIZ] Is authenticated: {current_user.is_authenticated}")
    try:
        from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
        
        data = request.json
        print(f"🎯 [JOIN_QUIZ] Request data: {data}")
        quiz_id = data.get('quiz_id')
        session_code = data.get('session_code')
        
        # Find session
        if quiz_id:
            session = LiveQuizSession.query.get(quiz_id)
        elif session_code:
            session = LiveQuizSession.query.filter_by(session_code=session_code).first()
        else:
            return jsonify({'success': False, 'error': 'No quiz_id or session_code provided'}), 400
        
        if not session:
            return jsonify({'success': False, 'error': 'Quiz session not found'}), 404
        
        # Check if session allows joining
        if session.status == 'completed':
            return jsonify({'success': False, 'error': 'This quiz has ended'}), 400
        
        if session.status == 'active' and not session.allow_join_after_start:
            return jsonify({'success': False, 'error': 'Quiz has already started'}), 400
        
        # Check if user already joined
        participant = LiveQuizParticipant.query.filter_by(
            session_id=session.id,
            user_id=current_user.id
        ).first()
        
        if participant:
            return jsonify({
                'success': True,
                'message': 'Already joined',
                'participant': participant.to_dict(),
                'session': session.to_dict()
            })
        
        # Create new participant
        participant = LiveQuizParticipant(
            session_id=session.id,
            user_id=current_user.id,
            display_name=current_user.username
        )
        db.session.add(participant)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Successfully joined quiz!',
            'participant': participant.to_dict(),
            'session': session.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error joining quiz: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_bp.route('/questions/<int:session_id>', methods=['GET'])
@login_required
def get_quiz_questions(session_id):
    """Get questions for a quiz session"""
    try:
        from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
        from instructor.models.question_group import QuestionGroup
        
        session = LiveQuizSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Verify user is participant
        participant = LiveQuizParticipant.query.filter_by(
            session_id=session.id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            return jsonify({'success': False, 'error': 'You are not a participant in this quiz'}), 403
        
        # Get question group
        question_group = QuestionGroup.query.get(session.question_group_id)
        if not question_group:
            return jsonify({'success': False, 'error': 'Questions not found'}), 404
        
        # Get questions
        questions = []
        for question in question_group.questions:
            q_dict = question.to_dict()
            # Remove correct answer from response (for security)
            q_dict_safe = {
                'id': q_dict['id'],
                'numb': q_dict['numb'],
                'question': q_dict['question'],
                'options': q_dict['options'],
                'category': q_dict.get('category', 'general')
            }
            questions.append(q_dict_safe)
        
        # Randomize if needed
        if session.randomize_questions:
            random.shuffle(questions)
        
        if session.randomize_answers:
            for q in questions:
                if q.get('options'):
                    random.shuffle(q['options'])
        
        return jsonify({
            'success': True,
            'questions': questions,
            'time_per_question': session.time_per_question,
            'session': session.to_dict()
        })
        
    except Exception as e:
        print(f"Error getting questions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_bp.route('/submit-answer', methods=['POST'])
@login_required
def submit_answer():
    """Submit an answer to a quiz question"""
    try:
        from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant, LiveQuizResponse
        from instructor.models.question import Question
        
        data = request.json
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        response_time = data.get('response_time', 0)  # seconds
        
        # Get session
        session = LiveQuizSession.query.get(session_id)
        if not session or session.status == 'completed':
            return jsonify({'success': False, 'error': 'Quiz session not active'}), 400
        
        # Get participant
        participant = LiveQuizParticipant.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            return jsonify({'success': False, 'error': 'Not a participant'}), 403
        
        # Check if already answered
        existing_response = LiveQuizResponse.query.filter_by(
            participant_id=participant.id,
            question_id=question_id
        ).first()
        
        if existing_response:
            return jsonify({
                'success': False,
                'error': 'Already answered this question'
            }), 400
        
        # Get question and check answer
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'error': 'Question not found'}), 404
        
        # Handle cases where selected_answer is None (e.g., timer expired without answer)
        if selected_answer is None or selected_answer == '':
            is_correct = False
            selected_answer = ''  # Convert None to empty string for database NOT NULL constraint
        else:
            is_correct = (selected_answer.strip().lower() == question.answer.strip().lower())
        
        # Create response
        response = LiveQuizResponse(
            participant_id=participant.id,
            session_id=session_id,
            question_id=question_id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            response_time=response_time,
            question_text=question.question,
            correct_answer=question.answer
        )
        
        # Calculate base points
        points = response.calculate_points(
            max_time=session.time_per_question,
            max_points=1000
        )
        
        # ===== SPEED BONUS: Apply multipliers for fastest correct answers =====
        if is_correct:
            # Get all correct responses for this question, ordered by response time
            fastest_responses = LiveQuizResponse.query.filter_by(
                session_id=session_id,
                question_id=question_id,
                is_correct=True
            ).order_by(LiveQuizResponse.response_time.asc()).all()
            
            # Determine this answer's speed rank
            speed_rank = len(fastest_responses) + 1  # +1 because current answer not yet in list
            
            if speed_rank == 1:
                # Fastest answer: +20% bonus
                speed_multiplier = 1.20
                print(f'🏆 [SPEED BONUS] FASTEST answer! {participant.display_name} gets +20% ({points} → {int(points * speed_multiplier)})')
                points = int(points * speed_multiplier)
            elif speed_rank == 2:
                # Second fastest: +10% bonus
                speed_multiplier = 1.10
                print(f'🥈 [SPEED BONUS] 2nd fastest answer! {participant.display_name} gets +10% ({points} → {int(points * speed_multiplier)})')
                points = int(points * speed_multiplier)
            # No bonus for 3rd place and beyond (keeps it competitive but not overwhelming)
        
        response.points_awarded = points
        
        db.session.add(response)
        
        # Update participant stats
        participant.total_answered += 1
        if is_correct:
            participant.total_correct += 1
            participant.total_score += points
        
        participant.total_time += response_time
        participant.average_response_time = participant.total_time / participant.total_answered
        
        db.session.commit()
        
        # Get updated leaderboard
        leaderboard = get_session_leaderboard(session_id)
        
        # ===== REAL-TIME LEADERBOARD UPDATE: Broadcast to all participants =====
        from socket_manager import socketio
        room_name = f'live_quiz_{session_id}'
        
        print(f'\n[LEADERBOARD UPDATE] 📊 Broadcasting updated leaderboard to room: {room_name}')
        print(f'[LEADERBOARD UPDATE] Trigger: {participant.display_name} answered Q{question_id}')
        print(f'[LEADERBOARD UPDATE] Answer: {"✅ Correct" if is_correct else "❌ Incorrect"} | Points: {points}')
        print(f'[LEADERBOARD UPDATE] Leaderboard size: {len(leaderboard)} participants\n')
        
        socketio.emit('leaderboard_updated', {
            'session_id': session_id,
            'leaderboard': leaderboard,
            'trigger_user': participant.display_name,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_name)
        
        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'correct_answer': question.answer,
            'explanation': question.explanation,
            'points_awarded': points,
            'total_score': participant.total_score,
            'total_correct': participant.total_correct,
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting answer: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_bp.route('/leaderboard/<int:session_id>', methods=['GET'])
@login_required
def get_leaderboard(session_id):
    """Get current leaderboard for a quiz session"""
    try:
        leaderboard = get_session_leaderboard(session_id)
        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        })
    except Exception as e:
        print(f"Error getting leaderboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def get_session_leaderboard(session_id):
    """
    Helper function to calculate leaderboard rankings with Slido-style tiebreakers
    
    Ranking Logic:
    1. Primary: Total score (descending) - higher score ranks higher
    2. Secondary: Average response time (ascending) - faster average ranks higher
    3. Tertiary: Joined timestamp (ascending) - earlier join ranks higher
    """
    from user.models.live_quiz import LiveQuizParticipant
    
    # Get all active participants
    participants = LiveQuizParticipant.query.filter_by(
        session_id=session_id,
        is_active=True
    ).all()
    
    # Cache current_user.id safely for comparisons during serialization
    current_user_id = None
    try:
        if getattr(current_user, 'is_authenticated', False):
            current_user_id = getattr(current_user, 'id', None)
    except Exception:
        current_user_id = None

    # Sort using multi-level criteria (Slido-style)
    # Python's sort is stable, so we can chain sorts in reverse order
    participants_sorted = sorted(
        participants,
        key=lambda p: (
            -p.total_score,  # Higher score = better (negative for descending)
            p.average_response_time if p.average_response_time else 999999,  # Lower time = better
            p.joined_at  # Earlier join = better (for exact ties)
        )
    )
    
    # Assign ranks and prepare leaderboard
    leaderboard = []
    for rank, p in enumerate(participants_sorted, start=1):
        p.rank = rank  # Update participant's rank in database
        leaderboard.append({
            'rank': rank,
            'display_name': p.display_name,
            'total_score': p.total_score,
            'total_correct': p.total_correct,
            'total_answered': p.total_answered,
            'questions_answered': p.total_answered,
            'user_id': p.user_id,
            'average_response_time': round(p.average_response_time, 2) if p.average_response_time is not None else 0,
            'is_current_user': bool(current_user_id is not None and p.user_id == current_user_id),
            'joined_at': p.joined_at.isoformat() if p.joined_at else None  # Include for debugging/transparency
        })
    
    db.session.commit()
    
    return leaderboard


@live_quiz_bp.route('/complete/<int:session_id>', methods=['POST'])
@login_required
def complete_quiz(session_id):
    """Mark quiz as completed for current user"""
    try:
        from user.models.live_quiz import LiveQuizParticipant
        
        participant = LiveQuizParticipant.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            return jsonify({'success': False, 'error': 'Not a participant'}), 403
        
        participant.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Get final leaderboard
        leaderboard = get_session_leaderboard(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Quiz completed!',
            'final_score': participant.total_score,
            'total_correct': participant.total_correct,
            'rank': participant.rank,
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error completing quiz: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_bp.route('/status/<int:session_id>', methods=['GET'])
@login_required
def get_quiz_status(session_id):
    """Get current quiz session status"""
    try:
        from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
        
        session = LiveQuizSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        participant = LiveQuizParticipant.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'participant': participant.to_dict() if participant else None,
            'is_participant': bool(participant)
        })
        
    except Exception as e:
        print(f"Error getting quiz status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

"""
Instructor API for Live Quiz Management
Allows instructors to create, start, stop, and manage live quiz sessions
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils.auth_decorators import instructor_required
from __init__ import db
from datetime import datetime
import random
import string

# Create blueprint - matches frontend URL structure /instructor/api/live-quiz
live_quiz_instructor_bp = Blueprint('live_quiz_instructor', __name__, url_prefix='/instructor/api/live-quiz')


def generate_session_code():
    """Generate a unique 6-character session code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        from user.models.live_quiz import LiveQuizSession
        if not LiveQuizSession.query.filter_by(session_code=code).first():
            return code


@live_quiz_instructor_bp.route('/create', methods=['POST'])
@instructor_required
def create_quiz_session():
    """Create a new live quiz session"""
    try:
        from user.models.live_quiz import LiveQuizSession
        from instructor.models.question_group import QuestionGroup
        
        data = request.json
        question_group_id = data.get('question_group_id')
        class_id = data.get('class_id')
        module_id = data.get('module_id')
        lesson_id = data.get('lesson_id')
        title = data.get('title', 'Live Quiz')
        time_per_question = data.get('time_per_question', 30)
        
        # Validate question group exists
        question_group = QuestionGroup.query.get(question_group_id)
        if not question_group:
            return jsonify({'success': False, 'error': 'Question group not found'}), 404
        
        # Generate unique session code
        session_code = generate_session_code()
        
        # CLEANUP: Reset any old active sessions for this class/module/lesson
        # This prevents students from joining stale sessions
        print(f'\n[SESSION CLEANUP] Checking for old active sessions...')
        print(f'[SESSION CLEANUP] Class: {class_id}, Module: {module_id}, Lesson: {lesson_id}')
        
        old_sessions = LiveQuizSession.query.filter_by(
            class_id=class_id,
            module_id=module_id,
            lesson_id=lesson_id,
            status='active'
        ).all()
        
        if old_sessions:
            print(f'[SESSION CLEANUP] Found {len(old_sessions)} old active session(s)')
            for old_session in old_sessions:
                print(f'[SESSION CLEANUP] Resetting session {old_session.id} (code: {old_session.session_code})')
                print(f'[SESSION CLEANUP] - Title: {old_session.title}')
                print(f'[SESSION CLEANUP] - Started at: {old_session.started_at}')
                old_session.status = 'completed'
                old_session.ended_at = datetime.utcnow()
            db.session.flush()  # Commit the cleanup before creating new session
            print(f'[SESSION CLEANUP] ✅ Reset {len(old_sessions)} old session(s) to "completed"')
        else:
            print(f'[SESSION CLEANUP] ✅ No old active sessions found - database is clean')
        
        # Create new session
        print(f'[SESSION CREATE] Creating new session with code: {session_code}')
        session = LiveQuizSession(
            question_group_id=question_group_id,
            class_id=class_id,
            module_id=module_id,
            lesson_id=lesson_id,
            session_code=session_code,
            title=title,
            time_per_question=time_per_question,
            status='waiting',
            created_by=current_user.id,
            show_leaderboard=data.get('show_leaderboard', True),
            allow_join_after_start=data.get('allow_join_after_start', True),
            randomize_questions=data.get('randomize_questions', False),
            randomize_answers=data.get('randomize_answers', True)
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Broadcast to students in the module room via WebSocket
        module_room = f'module_{module_id}'
        broadcast_data = {
            'session_id': session.id,
            'status': session.status,
            'title': session.title,
            'session_code': session.session_code,
            'class_id': session.class_id,
            'module_id': session.module_id,
            'lesson_id': session.lesson_id
        }
        
        print(f"\n{'='*80}")
        print(f"[SESSION CREATE] 📡 Broadcasting new session to module room: {module_room}")
        print(f"[SESSION CREATE] Session ID: {session.id}, Status: {session.status}")
        print(f"[SESSION CREATE] Broadcast data: {broadcast_data}")
        print(f"{'='*80}\n")
        
        socketio.emit('live_quiz_session_status_changed', broadcast_data, room=module_room)
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'message': f'Live quiz created with code: {session_code}'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating live quiz session: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_instructor_bp.route('/sessions', methods=['GET'])
@instructor_required
def get_all_sessions():
    """Get all live quiz sessions created by this instructor"""
    try:
        from user.models.live_quiz import LiveQuizSession
        
        class_id = request.args.get('class_id', type=int)
        status = request.args.get('status')  # active, waiting, completed
        
        query = LiveQuizSession.query.filter_by(created_by=current_user.id)
        
        if class_id:
            query = query.filter_by(class_id=class_id)
        
        if status:
            query = query.filter_by(status=status)
        
        sessions = query.order_by(LiveQuizSession.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        })
        
    except Exception as e:
        print(f"Error getting quiz sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_instructor_bp.route('/<int:session_id>', methods=['GET'])
@instructor_required
def get_session(session_id):
    """Get details of a specific live quiz session"""
    try:
        from user.models.live_quiz import LiveQuizSession
        
        session = LiveQuizSession.query.get(session_id)
        if not session or session.created_by != current_user.id:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        })
        
    except Exception as e:
        print(f"Error getting quiz session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_instructor_bp.route('/<int:session_id>/start', methods=['POST'])
@live_quiz_instructor_bp.route('/session/<int:session_id>/start', methods=['POST'])
@instructor_required
def start_session(session_id):
    """Start a live quiz session"""
    try:
        from user.models.live_quiz import LiveQuizSession
        
        print(f'\n{"="*80}')
        print(f'[INSTRUCTOR START QUIZ] Request received for session {session_id}')
        print(f'[INSTRUCTOR START QUIZ] Instructor ID: {current_user.id}')
        print(f'[INSTRUCTOR START QUIZ] Instructor username: {current_user.username}')
        
        session = LiveQuizSession.query.get(session_id)
        if not session or session.created_by != current_user.id:
            print(f'[INSTRUCTOR START QUIZ] ❌ ERROR: Session not found or not owned by instructor')
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        print(f'[INSTRUCTOR START QUIZ] Session found - Current status: {session.status}')
        
        if session.status != 'waiting':
            print(f'[INSTRUCTOR START QUIZ] ❌ ERROR: Quiz already started (status: {session.status})')
            return jsonify({'success': False, 'error': 'Quiz already started'}), 400
        
        print(f'[INSTRUCTOR START QUIZ] ✅ Status check passed - proceeding to start quiz')
        
        session.status = 'active'
        session.started_at = datetime.utcnow()
        session.current_question_index = 0
        db.session.commit()
        
        print(f'[INSTRUCTOR START QUIZ] ✅ Database updated:')
        print(f'   - Status: waiting → active')
        print(f'   - Started at: {session.started_at.isoformat()}')
        print(f'   - Question index: 0')
        
        # Emit socket event to notify all participants
        from socket_manager import socketio
        room_name = f'live_quiz_{session_id}'
        
        print(f'[INSTRUCTOR START QUIZ] 📡 Broadcasting quiz_started event to room: {room_name}')
        
        socketio.emit('quiz_started', {
            'session_id': session_id,
            'started_at': session.started_at.isoformat(),
            'current_question_index': 0
        }, room=room_name)
        
        print(f'[INSTRUCTOR START QUIZ] ✅ Socket event broadcast complete')
        
        # ===== MVP REALTIME: Broadcast to module room for page-level updates =====
        module_room = f'module_{session.module_id}'
        
        print(f'\n[MVP REALTIME] 🚀 Broadcasting session status change to module room: {module_room}')
        print(f'[MVP REALTIME] Session details:')
        print(f'   - Session ID: {session.id}')
        print(f'   - Status: waiting → active')
        print(f'   - Module ID: {session.module_id}')
        print(f'   - Lesson ID: {session.lesson_id}')
        print(f'   - Class ID: {session.class_id}')
        
        broadcast_data = {
            'session_id': session.id,
            'status': 'active',
            'class_id': session.class_id,
            'module_id': session.module_id,
            'lesson_id': session.lesson_id,
            'title': session.title,
            'session_code': session.session_code,
            'started_at': session.started_at.isoformat() if session.started_at else None
        }
        
        socketio.emit('live_quiz_session_status_changed', broadcast_data, room=module_room)
        
        print(f'[MVP REALTIME] ✅ Module room broadcast complete')
        print(f'[MVP REALTIME] 📢 All students on module page should now see LIVE button')
        print(f'[INSTRUCTOR START QUIZ] 🎉 Quiz started successfully!')
        print(f'{"="*80}\n')
        
        return jsonify({
            'success': True,
            'message': 'Quiz started!',
            'session': session.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"[MVP LiveQuiz] Error starting quiz: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_instructor_bp.route('/<int:session_id>/next-question', methods=['POST'])
@live_quiz_instructor_bp.route('/session/<int:session_id>/next-question', methods=['POST'])
@instructor_required
def next_question(session_id):
    """Advance the live quiz to the next question or complete it if finished"""
    try:
        from user.models.live_quiz import LiveQuizSession
        from instructor.models.question_group import QuestionGroup

        print(f'\n{"="*80}')
        print(f'[INSTRUCTOR NEXT QUESTION] Request received for session {session_id}')
        print(f'[INSTRUCTOR NEXT QUESTION] Instructor ID: {current_user.id}')

        session = LiveQuizSession.query.get(session_id)
        if not session or session.created_by != current_user.id:
            print(f'[INSTRUCTOR NEXT QUESTION] ❌ ERROR: Session not found or not owned')
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        print(f'[INSTRUCTOR NEXT QUESTION] Session status: {session.status}')
        print(f'[INSTRUCTOR NEXT QUESTION] Current question index: {session.current_question_index}')

        if session.status == 'completed':
            print(f'[INSTRUCTOR NEXT QUESTION] ❌ ERROR: Quiz already completed')
            return jsonify({'success': False, 'error': 'Quiz already completed'}), 400

        question_group = QuestionGroup.query.get(session.question_group_id)
        total_questions = len(getattr(question_group, 'questions', []) or [])
        
        print(f'[INSTRUCTOR NEXT QUESTION] Total questions in group: {total_questions}')
        
        if total_questions == 0:
            print(f'[INSTRUCTOR NEXT QUESTION] ❌ ERROR: No questions available')
            return jsonify({'success': False, 'error': 'No questions available for this quiz'}), 400

        from socket_manager import socketio

        quiz_completed = False
        old_question_index = session.current_question_index

        if session.current_question_index >= total_questions - 1:
            session.status = 'completed'
            session.ended_at = datetime.utcnow()
            quiz_completed = True
            print(f'[INSTRUCTOR NEXT QUESTION] 🏁 Quiz completing - was at last question')
        else:
            session.current_question_index += 1
            print(f'[INSTRUCTOR NEXT QUESTION] ✅ Advancing: Q{old_question_index} → Q{session.current_question_index}')

        db.session.commit()
        print(f'[INSTRUCTOR NEXT QUESTION] ✅ Database updated')

        # Get updated leaderboard for both completion and advancement
        from user.routes.live_quiz_routes import get_session_leaderboard
        
        print(f'[INSTRUCTOR NEXT QUESTION] 📊 Fetching updated leaderboard...')
        leaderboard = get_session_leaderboard(session_id)
        print(f'[INSTRUCTOR NEXT QUESTION] 📊 Leaderboard fetched: {len(leaderboard)} participants')

        room_name = f'live_quiz_{session_id}'

        if quiz_completed:
            print(f'[INSTRUCTOR NEXT QUESTION] 📡 Broadcasting quiz_ended to room: {room_name}')
            socketio.emit('quiz_ended', {
                'session_id': session_id,
                'ended_at': session.ended_at.isoformat() if session.ended_at else None,
                'leaderboard': leaderboard
            }, room=room_name)
            print(f'[INSTRUCTOR NEXT QUESTION] ✅ Quiz ended event broadcast complete')
        else:
            print(f'[INSTRUCTOR NEXT QUESTION] 📡 Broadcasting next_question to room: {room_name}')
            print(f'[INSTRUCTOR NEXT QUESTION]    - Question index: {session.current_question_index}')
            print(f'[INSTRUCTOR NEXT QUESTION]    - Leaderboard size: {len(leaderboard)}')
            
            socketio.emit('next_question', {
                'question_index': session.current_question_index,
                'timestamp': datetime.utcnow().isoformat(),
                'leaderboard': leaderboard  # Include updated leaderboard
            }, room=room_name)
            
            print(f'[INSTRUCTOR NEXT QUESTION] ✅ Next question event broadcast complete')
            print(f'[INSTRUCTOR NEXT QUESTION] 🎯 Students should now see Q{session.current_question_index + 1}')

        current_question_number = min(session.current_question_index + 1, total_questions)

        response = {
            'success': True,
            'current_question': current_question_number,
            'quiz_completed': quiz_completed,
            'total_questions': total_questions,
            'leaderboard': leaderboard  # Always include leaderboard in response
        }

        print(f'[INSTRUCTOR NEXT QUESTION] 📤 Sending response to instructor:')
        print(f'   - Current question: {current_question_number}/{total_questions}')
        print(f'   - Quiz completed: {quiz_completed}')
        print(f'   - Leaderboard participants: {len(leaderboard)}')
        print(f'{"="*80}\n')

        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        print(f"[MVP LiveQuiz] Error advancing quiz: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_instructor_bp.route('/<int:session_id>/end', methods=['POST'])
@live_quiz_instructor_bp.route('/session/<int:session_id>/end', methods=['POST'])
@instructor_required
def end_session(session_id):
    """End a live quiz session"""
    try:
        from user.models.live_quiz import LiveQuizSession
        from user.routes.live_quiz_routes import get_session_leaderboard
        
        session = LiveQuizSession.query.get(session_id)
        if not session or session.created_by != current_user.id:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        session.status = 'completed'
        session.ended_at = datetime.utcnow()
        db.session.commit()
        
        # Get final leaderboard
        leaderboard = get_session_leaderboard(session_id)
        
        # Emit socket event to notify participants
        from socket_manager import socketio
        socketio.emit('quiz_ended', {
            'session_id': session_id,
            'ended_at': session.ended_at.isoformat(),
            'leaderboard': leaderboard
        }, room=f'live_quiz_{session_id}')
        
        # ===== MVP REALTIME: Broadcast to module room for page-level updates =====
        module_room = f'module_{session.module_id}'
        
        print(f'\n[MVP REALTIME] 🏁 Broadcasting session END to module room: {module_room}')
        print(f'[MVP REALTIME] Session {session.id} status: active → completed')
        
        broadcast_data = {
            'session_id': session.id,
            'status': 'completed',
            'class_id': session.class_id,
            'module_id': session.module_id,
            'lesson_id': session.lesson_id,
            'title': session.title,
            'session_code': session.session_code,
            'ended_at': session.ended_at.isoformat() if session.ended_at else None
        }
        
        socketio.emit('live_quiz_session_status_changed', broadcast_data, room=module_room)
        
        print(f'[MVP REALTIME] ✅ Module room broadcast complete - students should see button disappear')
        
        return jsonify({
            'success': True,
            'message': 'Quiz ended!',
            'session': session.to_dict(),
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error ending quiz: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_instructor_bp.route('/<int:session_id>/participants', methods=['GET'])
@live_quiz_instructor_bp.route('/session/<int:session_id>/participants', methods=['GET'])
@instructor_required
def get_participants(session_id):
    """Get all participants in a live quiz session"""
    try:
        from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
        
        session = LiveQuizSession.query.get(session_id)
        if not session or session.created_by != current_user.id:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        participants = LiveQuizParticipant.query.filter_by(
            session_id=session_id,
            is_active=True
        ).all()
        
        return jsonify({
            'success': True,
            'participants': [p.to_dict() for p in participants],
            'total_count': len(participants)
        })
        
    except Exception as e:
        print(f"Error getting participants: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_instructor_bp.route('/<int:session_id>/leaderboard', methods=['GET'])
@live_quiz_instructor_bp.route('/session/<int:session_id>/leaderboard', methods=['GET'])
@instructor_required
def get_instructor_leaderboard(session_id):
    """Get leaderboard for instructor view"""
    try:
        from user.models.live_quiz import LiveQuizSession
        from user.routes.live_quiz_routes import get_session_leaderboard
        
        print(f'[INSTRUCTOR LEADERBOARD] GET request for session {session_id}')
        
        session = LiveQuizSession.query.get(session_id)
        if not session or session.created_by != current_user.id:
            print(f'[INSTRUCTOR LEADERBOARD] ❌ ERROR: Session not found or not owned')
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Get leaderboard without current_user context
        from user.models.live_quiz import LiveQuizParticipant
        
        participants = LiveQuizParticipant.query.filter_by(
            session_id=session_id,
            is_active=True
        ).all()
        
        print(f'[INSTRUCTOR LEADERBOARD] Found {len(participants)} active participants')
        
        # Calculate rank scores and sort
        participant_scores = []
        for p in participants:
            rank_score = p.calculate_rank_score()
            participant_scores.append({
                'participant': p,
                'rank_score': rank_score
            })
            print(f'[INSTRUCTOR LEADERBOARD]   - {p.display_name}: score={p.total_score}, correct={p.total_correct}/{p.total_answered}')
        
        participant_scores.sort(key=lambda x: x['rank_score'], reverse=True)
        
        # Prepare leaderboard
        leaderboard = []
        for rank, item in enumerate(participant_scores, start=1):
            p = item['participant']
            p.rank = rank
            leaderboard.append({
                'rank': rank,
                'display_name': p.display_name,
                'total_score': p.total_score,
                'total_correct': p.total_correct,
                'total_answered': p.total_answered,
                'average_response_time': round(p.average_response_time, 2)
            })
        
        db.session.commit()
        
        print(f'[INSTRUCTOR LEADERBOARD] ✅ Returning leaderboard with {len(leaderboard)} entries')
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'total_participants': len(participants)
        })
        
    except Exception as e:
        print(f"Error getting leaderboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@live_quiz_instructor_bp.route('/<int:session_id>/delete', methods=['DELETE'])
@live_quiz_instructor_bp.route('/session/<int:session_id>/delete', methods=['DELETE'])
@instructor_required
def delete_session(session_id):
    """Delete a live quiz session"""
    try:
        from user.models.live_quiz import LiveQuizSession
        
        session = LiveQuizSession.query.get(session_id)
        if not session or session.created_by != current_user.id:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quiz session deleted'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting quiz session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

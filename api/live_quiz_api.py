"""
Live Quiz API - MVP Implementation
Slido-like real-time quiz system with leaderboard functionality
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from time import time
from typing import Dict, Any

live_quiz_bp = Blueprint('live_quiz_mvp', __name__, url_prefix='/api/live-quiz-mvp')

# In-memory MVP store. Replace with DB/Redis for production.
_sessions: Dict[str, Dict[str, Any]] = {}


def _get_session(session_id: str) -> Dict[str, Any]:
    """Get or create a quiz session"""
    return _sessions.setdefault(session_id, {
        'participants': {},   # user_id -> stats
        'questions': {},      # question_id -> {correct_answer, explanation}
        'answered_questions': {},  # user_id -> set of answered question_ids
        'created_at': time(),
        'finalized': False,
    })


def _display_name() -> str:
    """Get current user's display name"""
    return getattr(current_user, 'username', f'User {current_user.get_id()}')


def _compute_points(is_correct: bool, response_time_sec: float) -> int:
    """
    Compute points using Slido-like scoring:
    - Correct answer: 1000 points max
    - Faster responses get more points (30 second window)
    - Incorrect: 0 points
    """
    if not is_correct:
        return 0
    remaining = max(0.0, 30.0 - float(response_time_sec or 0.0))
    return int(round(1000.0 * (remaining / 30.0)))


def _leaderboard_payload(s: Dict[str, Any], current_uid: int = None):
    """
    Generate leaderboard sorted by:
    1. Total score (descending)
    2. Average response time (ascending) - tiebreaker
    3. Last answer timestamp (ascending) - second tiebreaker
    """
    items = []
    for uid, p in s['participants'].items():
        avg_time = (p['total_time_sec'] / p['total_answered']) if p['total_answered'] else 0.0
        items.append({
            'user_id': uid,
            'display_name': p['display_name'],
            'total_score': p['total_score'],
            'total_correct': p['total_correct'],
            'total_answered': p['total_answered'],
            'average_response_time': round(avg_time, 2),
            'last_answer_at': p['last_answer_at'],
        })
    
    # Slido-like sorting
    items.sort(key=lambda r: (-r['total_score'], r['average_response_time'], r['last_answer_at'] or 0))
    
    # Add rank and highlight current user
    for i, r in enumerate(items, start=1):
        r['rank'] = i
        r['is_current_user'] = (current_uid is not None and r['user_id'] == current_uid)
    
    return items


@live_quiz_bp.route('/join', methods=['POST'])
@login_required
def join():
    """
    Join a live quiz session
    
    MVP: Only allow joining if session status is 'active' (instructor-controlled)
    
    Request body:
    {
        "session_id": "6",  // or "quiz_id"
        "class_id": 7,
        "module_id": 1,
        "lesson_id": 2,
        "questions": [  // Optional: seed questions for this session
            {
                "id": "1",
                "correct_answer": "B",
                "explanation": "..."
            }
        ]
    }
    
    Response:
    {
        "success": true,
        "session": {"id": "6", "class_id": 7, ...},
        "participant": {...},
        "leaderboard": [...]
    }
    """
    data = request.get_json(silent=True) or {}

    # Accept either session_id or quiz_id (front-end uses both)
    session_id = str(data.get('session_id') or data.get('quiz_id') or '').strip()
    class_id = data.get('class_id')
    module_id = data.get('module_id')
    lesson_id = data.get('lesson_id')

    user_id = getattr(current_user, 'id', None)
    print(f'\n{"="*80}')
    print('[STUDENT JOIN] Incoming join request')
    print(f'[STUDENT JOIN] User ID: {user_id}')
    print(f'[STUDENT JOIN] Username: {getattr(current_user, "username", "Unknown")}')
    print(f'[STUDENT JOIN] Session ID from request: {session_id}')
    print(f'[STUDENT JOIN] Quiz ID from request: {data.get("quiz_id")}')
    print(f'[STUDENT JOIN] Class ID: {class_id}')
    print(f'[STUDENT JOIN] Module ID: {module_id}')
    print(f'[STUDENT JOIN] Lesson ID: {lesson_id}')

    if not session_id:
        print('[STUDENT JOIN] ❌ ERROR: Missing session identifier')
        print(f'{"="*80}\n')
        return jsonify({'success': False, 'error': 'Missing session_id/quiz_id'}), 400

    # MVP GUARD: Check database session status before allowing join
    try:
        from user.models.live_quiz import LiveQuizSession
        from __init__ import db
        
        print(f'[STUDENT JOIN] Checking database for session {session_id}...')
        
        db_session = LiveQuizSession.query.get(int(session_id))
        if db_session:
            print(f'[STUDENT JOIN] ✅ Session found in database')
            print(f'[STUDENT JOIN] Session title: {db_session.title}')
            print(f'[STUDENT JOIN] Session status: {db_session.status}')
            print(f'[STUDENT JOIN] Created by instructor: {db_session.created_by}')
            
            # Allow joining 'waiting' or 'active' sessions (lobby flow enabled)
            # Block only 'completed' sessions
            if db_session.status == 'completed':
                print(f'[STUDENT JOIN] ❌ BLOCKED: Session has ended')
                print(f'{"="*80}\n')
                return jsonify({
                    'success': False,
                    'error': 'This Live Quiz has already ended.',
                    'status': db_session.status
                }), 403
            
            if db_session.status not in ['waiting', 'active']:
                print(f'[STUDENT JOIN] ❌ BLOCKED: Invalid session status "{db_session.status}"')
                print(f'{"="*80}\n')
                return jsonify({
                    'success': False,
                    'error': 'Cannot join this quiz session.',
                    'status': db_session.status
                }), 403
            
            print(f'[STUDENT JOIN] ✅ Status check passed - session is {db_session.status}')
        else:
            print(f'[STUDENT JOIN] ⚠️ WARNING: Session {session_id} not found in database')
    except Exception as db_err:
        print(f'[STUDENT JOIN] ⚠️ Database error: {str(db_err)}')
        print(f'[STUDENT JOIN] Continuing with in-memory store as fallback')

    s = _get_session(session_id)
    print(f'[STUDENT JOIN] Session state retrieved')
    print(f'[STUDENT JOIN] Current participants: {len(s["participants"])}')
    print(f'[STUDENT JOIN] Current questions: {len(s["questions"])}')

    # Optional: seed questions for this session (client provides id + correct answer + explanation)
    questions_to_seed = data.get('questions', []) or []
    if questions_to_seed:
        print(f'[STUDENT JOIN] Seeding {len(questions_to_seed)} questions...')
        for q in questions_to_seed:
            qid = str(q.get('id'))
            if not qid:
                continue
            s['questions'][qid] = {
                'correct_answer': q.get('correct_answer') or q.get('answer'),
                'explanation': q.get('explanation'),
            }
        print(f'[STUDENT JOIN] ✅ Questions seeded - total now: {len(s["questions"])}')

    uid = int(current_user.get_id())
    participants = s['participants']
    
    if uid not in participants:
        print(f'[STUDENT JOIN] Creating new participant entry for user {uid}')
        participants[uid] = {
            'display_name': _display_name(),
            'total_score': 0,
            'total_correct': 0,
            'total_answered': 0,
            'total_time_sec': 0.0,
            'last_answer_at': None,
        }
        print(f'[STUDENT JOIN] ✅ Participant created')
    else:
        print(f'[STUDENT JOIN] User {uid} already a participant - using existing data')
    
    # Initialize answered questions set for this user if not exists
    if 'answered_questions' not in s:
        s['answered_questions'] = {}
    if uid not in s['answered_questions']:
        s['answered_questions'][uid] = set()

    leaderboard_snapshot = _leaderboard_payload(s, current_uid=uid)

    print(f'[STUDENT JOIN] ✅ Join successful!')
    print(f'[STUDENT JOIN] Participant stats:')
    print(f'   - Display name: {participants[uid]["display_name"]}')
    print(f'   - Total score: {participants[uid]["total_score"]}')
    print(f'   - Total answered: {participants[uid]["total_answered"]}')
    print(f'[STUDENT JOIN] Leaderboard size: {len(leaderboard_snapshot)}')
    print(f'{"="*80}\n')

    # Get session status from database
    session_status = 'active'  # Default fallback
    try:
        from user.models.live_quiz import LiveQuizSession
        db_session = LiveQuizSession.query.get(int(session_id))
        if db_session:
            session_status = db_session.status
            print(f'[STUDENT JOIN] Including session status in response: {session_status}')
    except Exception as e:
        print(f'[STUDENT JOIN] Could not fetch session status: {e}')
    
    return jsonify({
        'success': True,
        'session': {
            'id': session_id,
            'class_id': class_id,
            'module_id': module_id,
            'lesson_id': lesson_id,
            'status': session_status
        },
        'participant': participants[uid],
        'leaderboard': leaderboard_snapshot
    })


@live_quiz_bp.route('/submit-answer', methods=['POST'])
@login_required
def submit_answer():
    """
    Submit an answer and get instant feedback
    
    Request body:
    {
        "session_id": "6",
        "question_id": "1",
        "selected_answer": "B",
        "response_time": 5.3  // seconds
    }
    
    Response:
    {
        "success": true,
        "is_correct": true,
        "correct_answer": "B",
        "explanation": "...",
        "points_awarded": 850,
        "total_score": 1700,
        "leaderboard": [...],
        "already_answered": false
    }
    """
    data = request.get_json(silent=True) or {}
    session_id = str(data.get('session_id') or '').strip()
    question_id = str(data.get('question_id') or '').strip()
    selected_answer = data.get('selected_answer')
    response_time = float(data.get('response_time') or 0.0)
    
    if not session_id or not question_id:
        return jsonify({'success': False, 'error': 'Missing session_id or question_id'}), 400

    s = _get_session(session_id)
    uid = int(current_user.get_id())
    p = s['participants'].get(uid)
    
    if p is None:
        return jsonify({'success': False, 'error': 'You must join the session first'}), 400

    # Initialize answered questions tracking if not exists
    if 'answered_questions' not in s:
        s['answered_questions'] = {}
    if uid not in s['answered_questions']:
        s['answered_questions'][uid] = set()
    
    # Check if already answered this question
    if question_id in s['answered_questions'][uid]:
        # Return cached result without updating stats
        meta = s['questions'].get(question_id, {})
        return jsonify({
            'success': True,
            'already_answered': True,
            'is_correct': False,  # We don't know their previous answer
            'correct_answer': meta.get('correct_answer'),
            'explanation': meta.get('explanation'),
            'points_awarded': 0,
            'total_score': p['total_score'],
            'leaderboard': _leaderboard_payload(s, current_uid=uid),
            'message': 'You have already answered this question'
        })

    # Mark question as answered
    s['answered_questions'][uid].add(question_id)

    # Get question metadata
    meta = s['questions'].get(question_id, {})
    correct_answer = meta.get('correct_answer')
    explanation = meta.get('explanation')

    # Check if answer is correct
    # Handle cases where selected_answer is None (e.g., timer expired without answer)
    if selected_answer is None or selected_answer == '':
        is_correct = False
    else:
        is_correct = (correct_answer is not None and 
                      str(selected_answer).strip() == str(correct_answer).strip())
    
    # Compute Slido-like points
    points = _compute_points(is_correct, response_time)

    # Update participant stats
    p['total_answered'] += 1
    p['total_time_sec'] += response_time
    p['last_answer_at'] = time()
    
    if is_correct:
        p['total_correct'] += 1
        p['total_score'] += points

    return jsonify({
        'success': True,
        'already_answered': False,
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'explanation': explanation,
        'points_awarded': points,
        'total_score': p['total_score'],
        'leaderboard': _leaderboard_payload(s, current_uid=uid)
    })


@live_quiz_bp.route('/leaderboard/<session_id>', methods=['GET'])
@login_required
def leaderboard(session_id):
    """
    Get current leaderboard for polling
    
    Response:
    {
        "success": true,
        "leaderboard": [
            {
                "rank": 1,
                "user_id": 3,
                "display_name": "Gilbert",
                "total_score": 2450,
                "total_correct": 3,
                "total_answered": 4,
                "average_response_time": 4.5,
                "is_current_user": true
            },
            ...
        ]
    }
    """
    s = _get_session(str(session_id))
    uid = int(current_user.get_id())
    return jsonify({
        'success': True,
        'leaderboard': _leaderboard_payload(s, current_uid=uid)
    })


@live_quiz_bp.route('/complete/<session_id>', methods=['POST'])
@login_required
def complete(session_id):
    """
    Finalize quiz and get final results
    
    Response:
    {
        "success": true,
        "leaderboard": [...],
        "final_score": 2450,
        "rank": 1
    }
    """
    s = _get_session(str(session_id))
    s['finalized'] = True
    
    lb = _leaderboard_payload(s, current_uid=int(current_user.get_id()))
    
    # Find current user's final results
    me = next((r for r in lb if r['is_current_user']), None)
    
    return jsonify({
        'success': True,
        'leaderboard': lb,
        'final_score': me['total_score'] if me else 0,
        'rank': me['rank'] if me else None
    })


@live_quiz_bp.route('/state/<session_id>', methods=['GET'])
@login_required
def get_state(session_id):
    """
    Get full session state (for debugging)
    
    Response:
    {
        "success": true,
        "session_id": "6",
        "participants_count": 5,
        "questions_count": 10,
        "finalized": false,
        "created_at": 1698345678.123
    }
    """
    s = _get_session(str(session_id))
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'participants_count': len(s['participants']),
        'questions_count': len(s['questions']),
        'finalized': s['finalized'],
        'created_at': s['created_at']
    })


@live_quiz_bp.route('/session-status/<session_id>', methods=['GET'])
@login_required
def get_session_status(session_id):
    """
    Get session status from database
    
    Response:
    {
        "success": true,
        "session_id": "6",
        "status": "active",  // waiting, active, or completed
        "title": "Quiz Title"
    }
    """
    try:
        from user.models.live_quiz import LiveQuizSession
        
        db_session = LiveQuizSession.query.get(int(session_id))
        if db_session:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'status': db_session.status,
                'title': db_session.title
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found',
                'status': 'unknown'
            }), 404
    except Exception as e:
        print(f'[SESSION STATUS] Error: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'unknown'
        }), 500


@live_quiz_bp.route('/answered-questions/<session_id>', methods=['GET'])
@login_required
def get_answered_questions(session_id):
    """
    Get list of question IDs that current user has already answered
    
    Response:
    {
        "success": true,
        "answered_questions": ["1", "2", "5"]
    }
    """
    s = _get_session(str(session_id))
    uid = int(current_user.get_id())
    
    # Initialize if not exists
    if 'answered_questions' not in s:
        s['answered_questions'] = {}
    if uid not in s['answered_questions']:
        s['answered_questions'][uid] = set()
    
    return jsonify({
        'success': True,
        'answered_questions': list(s['answered_questions'][uid])
    })


@live_quiz_bp.route('/my-active-session', methods=['GET'])
@login_required
def get_my_active_session():
    """
    Check if current user has an active quiz session
    
    Query params:
    - class_id: Filter by class (optional)
    - module_id: Filter by module (optional)
    
    Response:
    {
        "success": true,
        "has_active_session": true,
        "session": {
            "session_id": "6",
            "class_id": 7,
            "module_id": 1,
            "lesson_id": 2,
            "title": "Quiz Title",
            "status": "active",
            "current_question_index": 2,
            "total_questions": 10,
            "answered_questions": ["1", "2"],
            "participant_stats": {...}
        }
    }
    """
    from user.models.live_quiz import LiveQuizSession
    from __init__ import db
    
    user_id = getattr(current_user, 'id', None)
    class_id = request.args.get('class_id', type=int)
    module_id = request.args.get('module_id', type=int)
    
    print(f'\n{"="*80}')
    print('[CHECK ACTIVE SESSION] Checking for active session')
    print(f'[CHECK ACTIVE SESSION] User ID: {user_id}')
    print(f'[CHECK ACTIVE SESSION] Class ID filter: {class_id}')
    print(f'[CHECK ACTIVE SESSION] Module ID filter: {module_id}')
    
    try:
        # Find active or recently completed sessions from database
        # Include 'completed' status so students can detect when quiz has ended on refresh
        query = LiveQuizSession.query.filter(
            LiveQuizSession.status.in_(['active', 'waiting', 'completed'])
        )
        
        if class_id:
            query = query.filter_by(class_id=class_id)
        if module_id:
            query = query.filter_by(module_id=module_id)
        
        active_db_sessions = query.order_by(LiveQuizSession.created_at.desc()).all()
        
        print(f'[CHECK ACTIVE SESSION] Found {len(active_db_sessions)} active/waiting/completed sessions in DB')
        
        # Check if user has joined any of these sessions
        for db_session in active_db_sessions:
            session_id = str(db_session.id)
            memory_session = _sessions.get(session_id)
            
            if memory_session and user_id in memory_session['participants']:
                participant = memory_session['participants'][user_id]
                
                # Get answered questions for this user
                answered_questions = []
                if 'answered_questions' in memory_session and user_id in memory_session['answered_questions']:
                    answered_questions = list(memory_session['answered_questions'][user_id])
                
                print(f'[CHECK ACTIVE SESSION] ✅ User is participant in session {session_id}')
                print(f'[CHECK ACTIVE SESSION] Session status: {db_session.status}')
                print(f'[CHECK ACTIVE SESSION] Current question: {db_session.current_question_index}')
                print(f'[CHECK ACTIVE SESSION] Answered questions: {len(answered_questions)}')
                print(f'{"="*80}\n')
                
                # Get question count from memory session
                total_questions = len(memory_session.get('questions', [])) if memory_session else 0
                
                return jsonify({
                    'success': True,
                    'has_active_session': True,
                    'session': {
                        'session_id': session_id,
                        'class_id': db_session.class_id,
                        'module_id': db_session.module_id,
                        'lesson_id': db_session.lesson_id,
                        'title': db_session.title,
                        'status': db_session.status,
                        'current_question_index': db_session.current_question_index or 0,
                        'total_questions': total_questions,
                        'answered_questions': answered_questions,
                        'participant_stats': {
                            'total_score': participant.get('total_score', 0),
                            'total_correct': participant.get('total_correct', 0),
                            'total_answered': participant.get('total_answered', 0)
                        }
                    }
                })
        
        print(f'[CHECK ACTIVE SESSION] User has not joined any active sessions')
        print(f'{"="*80}\n')
        
        return jsonify({
            'success': True,
            'has_active_session': False,
            'session': None
        })
        
    except Exception as e:
        print(f'[CHECK ACTIVE SESSION] ❌ Error: {e}')
        print(f'{"="*80}\n')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


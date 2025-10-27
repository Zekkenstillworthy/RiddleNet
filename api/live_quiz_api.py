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
    print('[LIVE_QUIZ_MVP][JOIN] Incoming request', {
        'user_id': user_id,
        'session_id': session_id,
        'quiz_id_field': data.get('quiz_id'),
        'session_code': data.get('session_code'),
        'class_id': class_id,
        'module_id': module_id,
        'lesson_id': lesson_id
    })

    if not session_id:
        print('[LIVE_QUIZ_MVP][JOIN][ERROR] Missing session identifier', {'user_id': user_id, 'payload': data})
        return jsonify({'success': False, 'error': 'Missing session_id/quiz_id'}), 400

    s = _get_session(session_id)
    print('[LIVE_QUIZ_MVP][JOIN] Session state snapshot', {
        'session_id': session_id,
        'participant_count': len(s['participants']),
        'question_count': len(s['questions'])
    })

    # Optional: seed questions for this session (client provides id + correct answer + explanation)
    for q in data.get('questions', []) or []:
        qid = str(q.get('id'))
        if not qid:
            continue
        s['questions'][qid] = {
            'correct_answer': q.get('correct_answer') or q.get('answer'),
            'explanation': q.get('explanation'),
        }
    if data.get('questions'):
        print('[LIVE_QUIZ_MVP][JOIN] Seeded questions', {
            'session_id': session_id,
            'seed_count': len(data.get('questions') or [])
        })

    uid = int(current_user.get_id())
    participants = s['participants']
    
    if uid not in participants:
        participants[uid] = {
            'display_name': _display_name(),
            'total_score': 0,
            'total_correct': 0,
            'total_answered': 0,
            'total_time_sec': 0.0,
            'last_answer_at': None,
        }

    leaderboard_snapshot = _leaderboard_payload(s, current_uid=uid)

    print('[LIVE_QUIZ_MVP][JOIN] Participant ready', {
        'session_id': session_id,
        'user_id': uid,
        'participant_total_score': participants[uid]['total_score'],
        'participant_total_answered': participants[uid]['total_answered'],
        'leaderboard_size': len(leaderboard_snapshot)
    })

    return jsonify({
        'success': True,
        'session': {
            'id': session_id,
            'class_id': class_id,
            'module_id': module_id,
            'lesson_id': lesson_id
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
        "leaderboard": [...]
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

    # Get question metadata
    meta = s['questions'].get(question_id, {})
    correct_answer = meta.get('correct_answer')
    explanation = meta.get('explanation')

    # Check if answer is correct
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

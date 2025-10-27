# Live Quiz MVP Implementation - Slido-like Leaderboard

## Overview
This MVP implements a real-time live quiz system with Slido-style scoring and leaderboard functionality.

## Architecture

### Backend (Python/Flask)
- **File**: `api/live_quiz_api.py`
- **Blueprint**: `live_quiz_bp` registered at `/api/live-quiz`
- **Storage**: In-memory (MVP) - replace with Redis/DB for production

### Scoring Logic (Slido-like)
```python
# Maximum 1000 points per correct answer
# Time-based scoring: faster = more points (30 second window)
points = round(1000 * max(0, 30 - response_time_sec) / 30)

# Incorrect answer = 0 points
```

### Leaderboard Sorting
1. **Total Score** (descending) - primary
2. **Average Response Time** (ascending) - tiebreaker
3. **Last Answer Timestamp** (ascending) - second tiebreaker

## API Endpoints

### POST /api/live-quiz/join
Join or create a quiz session.

**Request:**
```json
{
  "session_id": "6",
  "class_id": 7,
  "module_id": 1,
  "lesson_id": 2,
  "questions": [
    {
      "id": "1",
      "correct_answer": "B",
      "explanation": "..."
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "session": {
    "id": "6",
    "class_id": 7,
    "module_id": 1,
    "lesson_id": 2
  },
  "participant": {
    "display_name": "Gilbert I. Requitud",
    "total_score": 0,
    "total_correct": 0,
    "total_answered": 0,
    "total_time_sec": 0.0,
    "last_answer_at": null
  },
  "leaderboard": []
}
```

### POST /api/live-quiz/submit-answer
Submit an answer and receive instant feedback.

**Request:**
```json
{
  "session_id": "6",
  "question_id": "1",
  "selected_answer": "B",
  "response_time": 5.3
}
```

**Response:**
```json
{
  "success": true,
  "is_correct": true,
  "correct_answer": "B",
  "explanation": "...",
  "points_awarded": 850,
  "total_score": 850,
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 3,
      "display_name": "Gilbert I. Requitud",
      "total_score": 850,
      "total_correct": 1,
      "total_answered": 1,
      "average_response_time": 5.3,
      "is_current_user": true
    }
  ]
}
```

### GET /api/live-quiz/leaderboard/<session_id>
Poll for updated leaderboard (for clients without WebSockets).

**Response:**
```json
{
  "success": true,
  "leaderboard": [...]
}
```

### POST /api/live-quiz/complete/<session_id>
Finalize quiz and get final results.

**Response:**
```json
{
  "success": true,
  "leaderboard": [...],
  "final_score": 2450,
  "rank": 1
}
```

### GET /api/live-quiz/state/<session_id>
Get session state (debugging).

**Response:**
```json
{
  "success": true,
  "session_id": "6",
  "participants_count": 5,
  "questions_count": 10,
  "finalized": false,
  "created_at": 1698345678.123
}
```

## Frontend Integration

### Template Context
Questions are seeded from the template context:
```javascript
const __lessonQuestions = {{ lesson_questions|tojson|safe if lesson_questions else '[]' }};
```

### Join Flow
```javascript
// 1. Join session with embedded questions
const joinResponse = await fetch('/api/live-quiz/join', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        session_id: String(sessionId),
        class_id: classId,
        module_id: moduleId,
        lesson_id: lessonId,
        questions: (__lessonQuestions || []).map(q => ({
            id: String(q.id || q.numb),
            correct_answer: q.answer,
            explanation: q.explanation || null
        }))
    })
});

// 2. Use embedded questions (no separate fetch)
quizQuestions = (__lessonQuestions || []).map(q => ({
    id: (q.id || q.numb),
    question: q.question,
    options: q.options || [],
    answer: q.answer,
    explanation: q.explanation || null
}));
```

### Submit Answer Flow
```javascript
const response = await fetch('/api/live-quiz/submit-answer', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        session_id: currentQuizSession.id,
        question_id: String(questionId),
        selected_answer: selectedAnswer,
        response_time: responseTime
    })
});

const data = await response.json();
// data.is_correct, data.points_awarded, data.leaderboard
```

## Fixes Implemented

### Issue: 404 on /api/live-quiz/join
**Root Cause**: No backend route existed
**Fix**: Created `api/live_quiz_api.py` and registered blueprint in `application.py`

### Issue: "Unexpected token '<'" JSON parse error
**Root Cause**: 404 returned HTML error page, not JSON
**Fix**: Blueprint now returns proper JSON responses

### Issue: Missing questions endpoint
**Root Cause**: Client tried to GET `/api/live-quiz/questions/{id}` which didn't exist
**Fix**: Questions are now seeded during join from template context (`lesson_questions`)

## Next Steps (Future Enhancements)

1. **WebSocket Integration**: Real-time leaderboard updates via Socket.IO
   ```python
   # In submit_answer():
   socketio.emit('live_quiz:leaderboard', payload['leaderboard'], 
                 room=f'quiz_{session_id}')
   ```

2. **Persistent Storage**: Replace in-memory dict with Redis or PostgreSQL
   ```python
   # Example with Redis:
   import redis
   r = redis.Redis()
   r.hset(f'quiz:{session_id}', 'participants', json.dumps(participants))
   ```

3. **Instructor Controls**: 
   - Start/pause quiz
   - Skip to next question
   - End quiz early

4. **Advanced Features**:
   - Question time limits per question
   - Bonus points for streaks
   - Team mode
   - Export results to CSV

## Testing

### Manual Test (User Flow)
1. Navigate to: `http://127.0.0.1:5001/class/7/module/1?lesson_id=2`
2. Click "Join Live Quiz" button
3. Console should show: `✅ Successfully joined quiz: {session: {...}}`
4. No 404 errors
5. Questions load from embedded template data
6. Submit answers and see instant feedback
7. Leaderboard updates with correct sorting

### API Test (curl)
```bash
# Join quiz
curl -X POST http://127.0.0.1:5001/api/live-quiz/join \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test123","class_id":7,"module_id":1,"lesson_id":2}'

# Submit answer
curl -X POST http://127.0.0.1:5001/api/live-quiz/submit-answer \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test123","question_id":"1","selected_answer":"B","response_time":5.3}'

# Get leaderboard
curl http://127.0.0.1:5001/api/live-quiz/leaderboard/test123
```

## Files Modified

1. **NEW**: `api/live_quiz_api.py` - MVP API implementation
2. **MODIFIED**: `application.py` - Registered live_quiz_bp blueprint
3. **MODIFIED**: `templates/user/module_detail.html`:
   - Added `__lessonQuestions` template variable
   - Updated `loadLiveQuiz()` to use new API
   - Updated `joinLiveQuizSession()` to seed questions
   - Existing `submitQuizAnswer()` already compatible

## Blueprint Registration

```python
# In application.py, line ~146
from api.live_quiz_api import live_quiz_bp as live_quiz_api_bp
application.register_blueprint(live_quiz_api_bp)
print("✅ Live Quiz MVP API registered at /api/live-quiz")
```

## Session State Structure

```python
{
    'participants': {
        3: {  # user_id
            'display_name': 'Gilbert I. Requitud',
            'total_score': 2450,
            'total_correct': 3,
            'total_answered': 4,
            'total_time_sec': 18.7,
            'last_answer_at': 1698345678.123
        }
    },
    'questions': {
        '1': {
            'correct_answer': 'B',
            'explanation': '...'
        }
    },
    'created_at': 1698345600.0,
    'finalized': False
}
```

## Key Design Decisions

1. **In-memory storage** for MVP speed (easy to migrate to Redis later)
2. **Template-seeded questions** to avoid extra API calls
3. **Slido-like scoring** for engaging time-pressure gameplay
4. **Polling-based** leaderboard (WebSocket upgrade later)
5. **Stateless participant join** (idempotent - can rejoin anytime)

---

**Status**: ✅ MVP Complete - Ready for Testing
**Date**: October 27, 2025
**Author**: GitHub Copilot

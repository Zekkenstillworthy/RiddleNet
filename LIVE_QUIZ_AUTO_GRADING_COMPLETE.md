# Live Quiz Auto-Grading System - Complete Implementation ✅

## Overview
Live Quizzes are **automatically graded** when the quiz ends. No manual grading is required by instructors.

---

## How Auto-Grading Works

### 1. **During Quiz - Real-time Scoring**
When a student submits an answer (`/api/live-quiz-mvp/submit-answer`):
- Answer is automatically checked for correctness
- Points are calculated based on Slido-like scoring:
  - **Correct answer**: 1000 points max
  - **Faster responses**: More points (within 30-second window)
  - **Incorrect answer**: 0 points
- Student's `total_score`, `total_correct`, and `total_answered` are updated immediately

**Location**: `api/live_quiz_api.py` lines 321-342

---

### 2. **Quiz Completion - Auto-Grade Trigger**
When the quiz ends, the system **automatically marks all participants as completed**, which triggers grade calculation.

#### Method A: Instructor Manually Ends Quiz
**Socket Event**: `instructor_end_quiz` 
**Location**: `socket_events.py` lines 2998-3003

```python
# CRITICAL: Mark all participants as completed for gradebook integration
participants = LiveQuizParticipant.query.filter_by(session_id=session_id).all()
completed_count = 0
for participant in participants:
    if not participant.completed_at:  # Only set if not already completed
        participant.completed_at = datetime.utcnow()
        completed_count += 1
```

**HTTP API**: `/instructor/api/live-quiz/session/<id>/end`
**Location**: `instructor/api/live_quiz_api.py` lines 430-454
```python
# CRITICAL: Auto-grade by marking all participants as completed
participants = LiveQuizParticipant.query.filter_by(session_id=session_id).all()
completed_count = 0
for participant in participants:
    if not participant.completed_at:
        participant.completed_at = datetime.utcnow()
        completed_count += 1
```

#### Method B: Auto-Timer Completes Quiz
**Location**: `socket_events.py` lines 2810-2819

When the quiz naturally reaches the last question and timer expires:
```python
completed_count = 0
participants = LiveQuizParticipant.query.filter_by(session_id=session_id).all()
for participant in participants:
    if not participant.completed_at:
        participant.completed_at = completion_time
        completed_count += 1
```

---

### 3. **Grade Calculation - Automatic Percentage**
When grades are fetched for the Gradebook (`/instructor/api/grades/class/<id>`):
**Location**: `instructor/api/grades_api.py` lines 258-276

```python
# Add live quiz grades
for session in live_quiz_sessions:
    participant = LiveQuizParticipant.query.filter_by(
        session_id=session.id,
        user_id=student.id
    ).first()
    
    if participant:
        key = f"quiz_{session.id}"
        # Normalize quiz score to percentage (0-100)
        q_count = question_counts.get(session.question_group_id, 0)
        max_possible_points = (q_count or 0) * 1000  # 1000 pts per question
        total_score = participant.total_score or 0
        percentage_score = min(100, (total_score / max_possible_points) * 100) if max_possible_points > 0 else 0
        grades[key] = {"score": round(percentage_score, 2)}
```

**Formula**: 
```
Percentage = (student_total_points / (num_questions × 1000)) × 100
```

---

## Student View - Grade Display

Students see their performance in the **completion screen** after the quiz ends:

**Location**: `templates/user/module_detail.html` lines 6683-6700

```javascript
// Calculate total questions in the quiz (not just answered)
const totalQuestions = Array.isArray(liveQuizState.questions) 
    ? liveQuizState.questions.length 
    : (currentUserData?.total_questions || totalAnswered || 0);

// Calculate accuracy based on total questions in quiz
const accuracy = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;

// Display format: "8/10" (8 correct out of 10 total questions)
finalCorrectEl.textContent = `${correctAnswers}/${totalQuestions}`;
finalAccuracyEl.textContent = `${accuracy}%`;
```

---

## Instructor View - Gradebook

Instructors can view all Live Quiz grades in the **Grades tab** of Class Content Manager:

1. Navigate to `/instructor/class/<class_id>/content`
2. Click **"Grades"** tab
3. All Live Quizzes appear automatically with percentage scores
4. Format: `quiz_<session_id>` with calculated percentage (0-100)

**Status Indicators**:
- ✅ **Completed**: Student finished quiz (`participant.completed_at` is set)
- ⏳ **In Progress**: Student joined but quiz not ended yet

---

## Key Database Fields

### `live_quiz_participants` Table:
- `total_score`: Accumulated points (max 1000 per question)
- `total_correct`: Number of correct answers
- `total_answered`: Number of questions attempted
- `completed_at`: Timestamp when quiz ended (NULL = not graded yet)

### `live_quiz_sessions` Table:
- `status`: 'active', 'waiting', or 'completed'
- `ended_at`: When quiz ended
- `question_group_id`: Links to questions for max score calculation

---

## Fix Applied (2025-11-04)

### Issue:
HTTP API endpoint `/session/<id>/end` was not marking participants as completed, while socket event was. This created inconsistency if instructors used direct API calls.

### Solution:
Added participant completion logic to HTTP endpoint to match socket event behavior:

```python
# CRITICAL: Auto-grade by marking all participants as completed
participants = LiveQuizParticipant.query.filter_by(session_id=session_id).all()
completed_count = 0
for participant in participants:
    if not participant.completed_at:
        participant.completed_at = datetime.utcnow()
        completed_count += 1

print(f"[AUTO-GRADE] Marked {completed_count} participants as completed for session {session_id}")
print(f"[AUTO-GRADE] Grades will now appear in Gradebook automatically")
```

---

## Summary

✅ **Live Quizzes are fully auto-graded:**
1. Answers checked in real-time during quiz
2. Participants marked completed when quiz ends (3 methods)
3. Grades calculated as percentage in Gradebook API
4. No manual grading required from instructors
5. Students see results immediately after quiz completion

**All grading is automatic and requires no instructor action!** 🎉

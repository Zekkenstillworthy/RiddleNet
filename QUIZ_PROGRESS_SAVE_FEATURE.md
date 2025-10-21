# Quiz Progress Save Feature - Implementation Summary

## Overview
Implemented a quiz progress save/resume feature that allows users to quit the quiz at any time and resume from where they left off. Progress is stored in the database using the `ChallengeScore` model's metadata field.

## Changes Made

### 1. Frontend Changes (`templates/user/quiz_challenge.html`)

#### New State Variables
- Added `quizSessionId` to track unique quiz sessions

#### New Functions

**`loadSavedProgress()`**
- Fetches saved progress from the server when quiz page loads
- Shows resume dialog if progress exists
- Otherwise starts a new quiz

**`showResumeDialog(savedData)`**
- Displays a dialog showing saved progress stats
- Offers "Resume Quiz" or "Start Fresh" options

**`resumeQuiz()`**
- Restores quiz state from saved progress:
  - Current question number
  - Score
  - Answered questions
  - Lifeline usage
  - Question order (preserves shuffle)
- Updates UI and continues from saved position

**`startNewQuiz()`**
- Resets all quiz state
- Shuffles questions fresh
- Clears any saved progress
- Initializes a new quiz session

**`saveProgress()`**
- Saves current quiz state to server
- Called after each question
- Stores:
  - Current question index
  - Current score
  - Answered questions array
  - Lifeline usage
  - Question order
  - Session ID

**`clearSavedProgress()`**
- Removes saved progress from database
- Called when quiz is completed or user starts fresh

**`quitQuiz()`**
- Saves progress and returns to challenges page
- Added as "Save & Quit" button after each question

**`updateLifelineButtons()`**
- Updates lifeline button states based on usage
- Called when resuming quiz

#### Modified Functions

**`goBackToChallenges()`**
- Removed confirmation dialog
- Now saves progress automatically before leaving
- Allows seamless exit and resume

**`nextQuestion()`**
- Added automatic progress save after each question

**`submitQuizResults()`**
- Clears saved progress after successful quiz completion

**`retakeQuiz()`**
- Now calls `startNewQuiz()` for consistency

**`showNextButton()`**
- Added "Save & Quit" button alongside "Next Question"

### 2. Backend Changes (`user/routes/quiz_routes.py`)

#### New API Endpoints

**`POST /quiz/api/save_progress`**
- Saves quiz progress to database
- Stores progress in `ChallengeScore.challenge_metadata['progress']`
- Includes:
  - Current question number
  - Score
  - Answered questions
  - Lifelines used
  - Question order (preserves shuffle)
  - Session ID
  - Timestamp

**`GET /quiz/api/get_progress`**
- Retrieves saved progress for current user
- Returns progress data if exists
- Returns `has_progress: false` if no saved data

**`POST /quiz/api/clear_progress`**
- Clears saved progress from database
- Removes `in_progress` and `progress` keys from metadata

#### Modified Endpoints

**`POST /quiz/api/submit`**
- No changes to core functionality
- Progress is cleared by frontend after submission

### 3. Database Schema

No schema changes required! Uses existing `ChallengeScore` table:

```python
challenge_metadata = {
    'in_progress': True/False,
    'progress': {
        'currentQuestion': 5,
        'score': 3,
        'answeredQuestions': [...],
        'lifelinesUsed': {...},
        'questionOrder': [...],  # Preserves shuffle
        'totalQuestions': 11,
        'sessionId': 'unique-id',
        'savedAt': '2025-10-22T...'
    }
}
```

## User Experience Flow

### Starting a Quiz
1. User navigates to `/quiz/`
2. System checks for saved progress
3. If progress exists:
   - Shows resume dialog with stats
   - User can "Resume" or "Start Fresh"
4. If no progress:
   - Starts new quiz immediately

### During Quiz
1. User answers questions one by one
2. After each answer:
   - Progress auto-saves to database
   - User can click "Next Question" or "Save & Quit"
3. Lifeline usage is tracked and restored on resume
4. Question order is preserved (shuffle doesn't change)

### Quitting Quiz
1. User clicks "Back" button or "Save & Quit"
2. Progress saves automatically
3. User returns to challenges page
4. No data loss

### Resuming Quiz
1. User returns to `/quiz/`
2. Resume dialog shows:
   - Questions completed (e.g., "6/11")
   - Current score
3. User clicks "Resume Quiz"
4. Quiz continues from exact position:
   - Same question order
   - Same score
   - Same lifeline states

### Completing Quiz
1. User finishes all questions
2. Results are submitted
3. Saved progress is automatically cleared
4. Badge system evaluates performance
5. Results page shows final stats

### Starting Fresh
1. User can choose "Start Fresh" from resume dialog
2. Or click "Retake Quiz" from results
3. Progress is cleared
4. New question shuffle occurs
5. Fresh quiz session begins

## Key Features

### ✅ Auto-Save
- Progress saves after every question
- No manual save button needed
- Seamless experience

### ✅ Preservation
- Question order preserved (shuffle doesn't change)
- Lifeline usage tracked
- Score maintained
- Answered questions recorded

### ✅ Flexible Exit
- "Back" button saves and exits
- "Save & Quit" button after each question
- No penalties for quitting

### ✅ Resume Capability
- Shows clear progress stats
- Restores exact quiz state
- Option to start fresh instead

### ✅ Database Persistence
- Progress stored in `ChallengeScore` table
- Uses existing metadata field
- No new tables needed
- Survives browser refresh
- Survives logout/login

### ✅ Session Tracking
- Unique session ID per quiz attempt
- Helps differentiate multiple attempts
- Useful for analytics

## Testing Checklist

- [x] Start new quiz → quit midway → resume successfully
- [x] Answer 5 questions → quit → resume from question 6
- [x] Use lifelines → quit → lifelines properly restored
- [x] Complete quiz → progress cleared automatically
- [x] Start fresh → old progress removed
- [x] Resume dialog shows correct stats
- [x] Question order preserved on resume
- [x] Score maintained on resume
- [x] Back button saves progress
- [x] Save & Quit button works
- [x] Browser refresh preserves progress
- [x] Multiple users have separate progress

## Benefits

1. **User Flexibility**: Users can quit anytime without losing progress
2. **Better Completion Rate**: Lower barrier to completing quiz
3. **Mobile Friendly**: Users can pause on mobile and resume later
4. **No Pressure**: Removes time pressure to finish in one session
5. **Data Persistence**: Progress survives browser/device changes
6. **Seamless UX**: Auto-save means users don't think about saving

## Future Enhancements (Optional)

1. **Progress Expiry**: Auto-clear progress after 7 days
2. **Multiple Saves**: Allow multiple saved sessions
3. **Progress Indicator**: Visual badge on challenges page showing "In Progress"
4. **Time Tracking**: Track total time spent across sessions
5. **Analytics**: Track quit/resume patterns for UX improvements

## Technical Notes

- Progress data is JSON serializable and stored in PostgreSQL JSONB field
- Question order includes full question objects (not just IDs) for flexibility
- Session IDs are client-generated using timestamp + random string
- Progress saves are non-blocking (don't interrupt quiz flow)
- Error handling ensures graceful fallback to new quiz on issues

## Conclusion

The quiz progress save feature is now fully implemented and integrated with the existing challenge system. Users can confidently start the quiz knowing they can quit anytime and resume later without losing progress. The feature uses the existing database schema and follows RiddleNet's architecture patterns.

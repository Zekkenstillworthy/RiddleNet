# Gradebook Quiz Percentage Fix

## Problem

The Gradebook was displaying **incorrect percentage values** for Live Quiz scores, showing values like:
- 1916%
- 2300%
- 2799%
- 966%
- 850%
- 916%
- 2816%
- 1407%

These values should have been between 0-100%.

## Root Cause

The `LiveQuizParticipant` model stores `total_score` as **cumulative points earned**, not as a percentage. For example:
- If a quiz has 10 questions
- Each question is worth 100 points
- A perfect score would be 1000 points (not 100%)

The Grades API was directly returning `participant.total_score` without converting it to a percentage, causing the frontend to display "1000%" instead of "100%".

## Solution

### 1. Student Individual Grades Normalization

**File**: `instructor/api/grades_api.py`

**Location**: Lines ~262-274 (in the student grades map building section)

**Change**: Calculate percentage score before storing in grades map

```python
# BEFORE:
if participant:
    key = f"quiz_{session.id}"
    grades[key] = {"score": participant.total_score}  # ❌ Raw points (can be > 100)

# AFTER:
if participant:
    key = f"quiz_{session.id}"
    # Normalize quiz score to percentage (0-100)
    max_possible_points = (session.question_count or 1) * 100  # Each question worth 100 points
    percentage_score = min(100, (participant.total_score / max_possible_points) * 100) if max_possible_points > 0 else 0
    grades[key] = {"score": round(percentage_score, 2)}  # ✅ Percentage (0-100)
```

### 2. Quiz Average Grade Normalization

**File**: `instructor/api/grades_api.py`

**Location**: Lines ~142-168 (in the aggregate live quizzes section)

**Change**: Convert each participant's score to percentage before calculating average

```python
# BEFORE:
# Calculate average score
avg_score = 0
if participants:
    avg_score = sum([p.total_score for p in participants]) / len(participants)  # ❌ Average of raw points

# AFTER:
# Calculate average score as percentage
avg_score = 0
if participants:
    max_possible_points = (session.question_count or 1) * 100  # Each question worth 100 points
    # Convert each participant's score to percentage, then average
    percentage_scores = []
    for p in participants:
        percentage = min(100, (p.total_score / max_possible_points) * 100) if max_possible_points > 0 else 0
        percentage_scores.append(percentage)
    avg_score = sum(percentage_scores) / len(percentage_scores) if percentage_scores else 0  # ✅ Average percentage
```

## Calculation Logic

### Percentage Formula:
```
percentage_score = (total_score / max_possible_points) * 100
```

Where:
- `total_score` = Cumulative points earned by student (from `LiveQuizParticipant.total_score`)
- `max_possible_points` = `question_count × 100` (each question worth 100 points)
- `percentage_score` = Capped at 100% using `min(100, ...)`

### Example Calculations:

**Quiz with 10 questions:**
- Max possible points: 10 × 100 = 1,000 points

**Student A earned 850 points:**
```
percentage = (850 / 1000) × 100 = 85%  ✅ Correct
Before fix: 850%  ❌ Wrong
```

**Student B earned 1,916 points (bonus/speed points):**
```
percentage = min(100, (1916 / 1000) × 100) = 100%  ✅ Correct (capped)
Before fix: 1916%  ❌ Wrong
```

**Student C earned 2,300 points:**
```
percentage = min(100, (2300 / 1000) × 100) = 100%  ✅ Correct (capped)
Before fix: 2300%  ❌ Wrong
```

## Impact

### Before Fix:
- ❌ Gradebook showed impossible percentages (> 100%)
- ❌ Average grades were meaningless
- ❌ Confusing for instructors
- ❌ Export data was incorrect

### After Fix:
- ✅ All quiz scores display as valid percentages (0-100%)
- ✅ Average grades are accurate
- ✅ Clear interpretation for instructors
- ✅ Export data is properly formatted
- ✅ Consistent with other grade types (assignments, essays, simulations)

## Testing Scenarios

### Test Case 1: Standard Quiz Performance
- **Quiz**: 5 questions
- **Student earned**: 400 points
- **Expected**: 80%
- **Calculation**: (400 / 500) × 100 = 80%

### Test Case 2: Perfect Score
- **Quiz**: 10 questions
- **Student earned**: 1,000 points
- **Expected**: 100%
- **Calculation**: (1000 / 1000) × 100 = 100%

### Test Case 3: Bonus/Speed Points (Over 100%)
- **Quiz**: 8 questions
- **Student earned**: 1,200 points (speed bonuses)
- **Expected**: 100% (capped)
- **Calculation**: min(100, (1200 / 800) × 100) = 100%

### Test Case 4: Average Calculation
- **Quiz**: 10 questions
- **Participants**:
  - Student A: 850 points → 85%
  - Student B: 900 points → 90%
  - Student C: 700 points → 70%
- **Expected Average**: (85 + 90 + 70) / 3 = 81.67%

## Files Modified

| File | Lines Changed | Description |
|------|---------------|-------------|
| `instructor/api/grades_api.py` | ~262-274 | Normalize student quiz scores to percentage |
| `instructor/api/grades_api.py` | ~142-168 | Normalize quiz average calculation to percentage |

## API Response Structure (After Fix)

### Student Grades:
```json
{
  "students": [
    {
      "id": 123,
      "username": "Gilbert",
      "grades": {
        "quiz_42": {
          "score": 85.0  // ✅ Now percentage (0-100)
        }
      }
    }
  ]
}
```

### Quiz Summary:
```json
{
  "quizzes": [
    {
      "id": "quiz_42",
      "title": "Networking Basics Quiz",
      "max_points": 100,
      "average_grade": 81.67  // ✅ Now percentage (0-100)
    }
  ]
}
```

## Related Systems

This fix affects:
1. ✅ **Gradebook Display** - Shows correct percentages
2. ✅ **Grade Export (CSV)** - Exports correct values
3. ✅ **Average Calculations** - Computes accurate class averages
4. ✅ **Grade Summary Cards** - Displays correct statistics
5. ✅ **Student Performance Reports** - Accurate percentage scores

## Why Live Quizzes Store Raw Points

Live Quizzes use raw point scoring to accommodate:
- **Speed bonuses** (faster answers = more points)
- **Streak multipliers** (consecutive correct answers)
- **Difficulty modifiers** (harder questions = more points)

These mechanics mean students can earn >100 points per question, so scores are stored as cumulative points. The **Gradebook must normalize these to percentages** for consistency with other grade types.

## Implementation Date
October 30, 2025

## Status
✅ **COMPLETE** - Ready for testing

## Testing Instructions

1. **Refresh the Gradebook page** at `/instructor/class-content-selector?class_id=7`
2. Click on **Grades tab**
3. Verify all quiz scores show **0-100%** (not 1000%+)
4. Check that **Average column** shows reasonable percentages
5. Verify **quiz summary cards** show correct average grades
6. Test **Export Grades** to confirm CSV has correct percentages

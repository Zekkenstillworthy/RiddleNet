# 📊 Link Up Challenge Tracking - Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    USER COMPLETES LINK UP CHALLENGE                     │
│                    (e.g., "Small Office Network")                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
         ┌──────────────────────────────────────────────────┐
         │   showResultsPopup(data, scenario) Called       │
         │   • Calculates final score & match percentage   │
         │   • Determines if challenge passed (≥70%)       │
         └──────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
        │  LOCALSTORAGE   │ │   BACKEND   │ │   UI UPDATE      │
        │   UPDATE        │ │    SAVE     │ │                  │
        └─────────────────┘ └─────────────┘ └──────────────────┘
                │                   │                  │
                ▼                   ▼                  ▼
    ┌──────────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ completed_linkup_    │ │ POST /api/   │ │ updateChallenge  │
    │ challenges: [        │ │ challenge/   │ │ ButtonState()    │
    │  "small-office",     │ │ save-        │ │                  │
    │  "home-network"      │ │ progress     │ │ button.classList │
    │ ]                    │ │              │ │ .add('completed')│
    └──────────────────────┘ └──────────────┘ └──────────────────┘
                │                   │                  │
                │                   ▼                  │
                │          ┌─────────────────┐        │
                │          │ challenge_      │        │
                │          │ progress table  │        │
                │          │ ─────────────── │        │
                │          │ state_data: {   │        │
                │          │   scenario_id,  │        │
                │          │   completed_    │        │
                │          │   scenarios:[   │        │
                │          │     "small-     │        │
                │          │     office"     │        │
                │          │   ]             │        │
                │          │ }               │        │
                │          └─────────────────┘        │
                │                   │                  │
                ▼                   ▼                  ▼
    ┌──────────────────────────────────────────────────────────┐
    │              CHALLENGE RESULTS TRACKER UPDATE             │
    │  challengeResultsTracker.addResult(difficulty, data)     │
    │  • Adds to linkup_challenge_results localStorage         │
    │  • Calls updateResultsDisplay() (forced refresh)         │
    └──────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   RESULTS SIDEBAR UPDATED     │
                    │   Shows completion record     │
                    │   with score, time, date      │
                    └───────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                          PAGE LOAD / REFRESH
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                  DOMContentLoaded Event Fired                           │
│              initializeChallengeTracking() Called                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌─────────────┐ ┌──────────────────┐
        │ FETCH BACKEND    │ │ LOAD LOCAL  │ │ UPDATE RESULTS   │
        │ COMPLETIONS      │ │ STORAGE     │ │ DISPLAY          │
        └──────────────────┘ └─────────────┘ └──────────────────┘
                │                   │                  │
                ▼                   ▼                  ▼
    ┌──────────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ GET /api/challenge/  │ │ Read:        │ │ challengeResults │
    │ completed-list/      │ │ completed_   │ │ Tracker.update   │
    │ linkup               │ │ linkup_      │ │ ResultsDisplay() │
    │                      │ │ challenges   │ │                  │
    │ Returns:             │ │              │ │                  │
    │ {                    │ │ Parse array  │ │                  │
    │   completed_         │ │ of IDs       │ │                  │
    │   challenges: [...]  │ │              │ │                  │
    │ }                    │ │              │ │                  │
    └──────────────────────┘ └──────────────┘ └──────────────────┘
                │                   │                  │
                └─────────┬─────────┘                  │
                          ▼                            │
            ┌─────────────────────────────┐           │
            │  SYNC BACKEND → LOCALSTORAGE│           │
            │  • Merge arrays             │           │
            │  • Update if changed        │           │
            └─────────────────────────────┘           │
                          │                            │
                          ▼                            │
            ┌─────────────────────────────┐           │
            │  UPDATE ALL BUTTON STATES   │           │
            │  For each completed ID:     │           │
            │  updateChallengeButtonState │           │
            │  (id, true)                 │           │
            └─────────────────────────────┘           │
                          │                            │
                          └────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   UI FULLY SYNCHRONIZED       │
                    │   • Buttons show completed    │
                    │   • Results sidebar populated │
                    │   • Backend & localStorage    │
                    │     in sync                   │
                    └───────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                        DATABASE SCHEMA STRUCTURE
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                       challenge_progress TABLE                          │
├─────────────────────────────────────────────────────────────────────────┤
│  id             │ INTEGER (Primary Key)                                 │
│  user_id        │ INTEGER (Foreign Key → users.id)                      │
│  challenge_type │ VARCHAR(50) = 'linkup'                                │
│  state_data     │ JSON {                                                │
│                 │   "scenario_id": "small-office-network",              │
│                 │   "scenario_title": "Small Office Network",           │
│                 │   "difficulty": "easy",                               │
│                 │   "score": 85,                                        │
│                 │   "match_percentage": 92,                             │
│                 │   "time_taken": 245,                                  │
│                 │   "badges_earned": [],                                │
│                 │   "completed_at": "2025-10-11T12:34:56.789Z",         │
│                 │   "completed_scenarios": [                            │
│                 │     "small-office-network",                           │
│                 │     "home-network",                                   │
│                 │     "pc-to-pc"                                        │
│                 │   ]                                                   │
│                 │ }                                                     │
│  is_completed   │ BOOLEAN = true                                        │
│  last_updated   │ DATETIME                                              │
│  created_at     │ DATETIME                                              │
├─────────────────────────────────────────────────────────────────────────┤
│ UNIQUE CONSTRAINT: (user_id, challenge_type)                            │
│ → Only ONE record per user for all Link Up challenges                  │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                      LOCALSTORAGE DATA STRUCTURE
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│  KEY: completed_linkup_challenges                                       │
│  VALUE: ["small-office-network", "home-network", "pc-to-pc"]            │
│  PURPOSE: Quick lookup for UI button states                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  KEY: linkup_challenge_results                                          │
│  VALUE: {                                                               │
│    "foundation": [                                                      │
│      {                                                                  │
│        "id": "small-office",                                            │
│        "name": "Small Office Network",                                  │
│        "score": 100,                                                    │
│        "timeSpent": "4:05",                                             │
│        "completedAt": "2025-10-11T12:34:56.789Z",                       │
│        "accuracy": 100,                                                 │
│        "hintsUsed": 0                                                   │
│      }                                                                  │
│    ],                                                                   │
│    "easy": [...],                                                       │
│    "intermediate": [...],                                               │
│    "hard": [...]                                                        │
│  }                                                                      │
│  PURPOSE: Detailed results for Challenge Results sidebar               │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                          KEY FUNCTION FLOW
═══════════════════════════════════════════════════════════════════════════

updateChallengeButtonState(challengeId, isCompleted)
    │
    ├─ Try multiple selectors: #id-btn, [data-scenario-id], etc.
    ├─ Find button element
    └─ Add/remove 'completed' class

loadCompletedChallenges()
    │
    ├─ Read from localStorage: 'completed_linkup_challenges'
    ├─ For each ID in array
    └─ Call updateChallengeButtonState(id, true)

fetchCompletedChallengesFromBackend()
    │
    ├─ GET /api/challenge/completed-list/linkup
    ├─ Receive array of completed scenarios
    ├─ Sync with localStorage (merge arrays)
    └─ Update UI for each completed scenario

initializeChallengeTracking()
    │
    ├─ fetchCompletedChallengesFromBackend()
    ├─ loadCompletedChallenges()
    └─ challengeResultsTracker.updateResultsDisplay()
```

---

**Legend**:
- `┌─┐ └─┘` = Process/Component Box
- `│` = Data Flow
- `▼` = Sequential Flow Direction
- `┬─┴` = Branch/Merge Points
- `═══` = Section Separator

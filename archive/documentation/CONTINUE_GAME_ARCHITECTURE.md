# 🏗️ Continue Game System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONTINUE GAME MVP ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  USER PLAYS CHALLENGE                                                        │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  Challenge Page (crimping-simulation.html, osi_model.html, etc.)  │     │
│  │                                                                     │     │
│  │  ┌─────────────────────────────────────────────────────────────┐  │     │
│  │  │  Challenge JavaScript                                        │  │     │
│  │  │                                                               │  │     │
│  │  │  let currentLevel = 1;                                        │  │     │
│  │  │  let score = 0;                                               │  │     │
│  │  │  let playerState = { ... };                                   │  │     │
│  │  └─────────────────────────────────────────────────────────────┘  │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ includes
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  CHALLENGE PROGRESS MANAGER MODULE                                           │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  static/js/challenge-progress-manager.js                           │     │
│  │                                                                     │     │
│  │  class ChallengeProgressManager {                                  │     │
│  │    ┌─────────────────────────────────────────────────────────┐    │     │
│  │    │  checkForProgress()       // Load saved state            │    │     │
│  │    │  saveProgress()           // Manual save                 │    │     │
│  │    │  startAutoSave()          // Auto-save every 10s         │    │     │
│  │    │  setupBeforeUnloadSave()  // Save on exit                │    │     │
│  │    │  markCompleted()          // Mark as done                │    │     │
│  │    │  clearProgress()          // Delete saved state          │    │     │
│  │    └─────────────────────────────────────────────────────────┘    │     │
│  │  }                                                                  │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                               │
                    │ HTTP Requests                 │ shows/hides
                    ▼                               ▼
┌──────────────────────────────────┐  ┌────────────────────────────────────┐
│  API ROUTES (Flask)              │  │  CONTINUE GAME MODAL               │
│  user/api.py                     │  │  templates/components/             │
│                                  │  │  continue_game_modal.html          │
│  POST /api/challenge/            │  │                                    │
│       save-progress              │  │  ┌──────────────────────────────┐ │
│       ├─ Validate session        │  │  │  [?] Welcome Back!            │ │
│       ├─ Get state_data          │  │  │                               │ │
│       └─ Save to DB              │  │  │  Last played: Oct 9, 10:30am │ │
│                                  │  │  │                               │ │
│  GET /api/challenge/             │  │  │  [▶ Continue Game]            │ │
│      load-progress/<type>        │  │  │  [🔄 Start Fresh]             │ │
│      ├─ Check session            │  │  └──────────────────────────────┘ │
│      ├─ Query DB                 │  │                                    │
│      └─ Return state_data        │  │  Triggers events:                 │
│                                  │  │  • loadSavedGame                   │
│  DELETE /api/challenge/          │  │  • startNewGame                    │
│         clear-progress/<type>    │  └────────────────────────────────────┘
│         ├─ Check session         │
│         └─ Delete from DB        │
└──────────────────────────────────┘
                    │
                    │ SQLAlchemy ORM
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  DATABASE LAYER                                                              │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  user/models/challenge_progress.py                                 │     │
│  │                                                                     │     │
│  │  class ChallengeProgress(db.Model):                                │     │
│  │    ├─ id (PK)                                                      │     │
│  │    ├─ user_id (FK to users.id)                                     │     │
│  │    ├─ challenge_type (e.g., 'crimping', 'osi')                     │     │
│  │    ├─ state_data (JSON) ← Stores game state                        │     │
│  │    ├─ last_updated (DateTime)                                      │     │
│  │    ├─ is_completed (Boolean)                                       │     │
│  │    └─ created_at (DateTime)                                        │     │
│  │                                                                     │     │
│  │  Methods:                                                           │     │
│  │    save_progress(user, type, data)                                 │     │
│  │    load_progress(user, type)                                       │     │
│  │    clear_progress(user, type)                                      │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SQLITE/POSTGRESQL DATABASE                                                  │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  Table: challenge_progress                                         │     │
│  │  ┌─────────┬─────────┬───────────────┬────────────────────────┐  │     │
│  │  │ user_id │ type    │ state_data    │ last_updated           │  │     │
│  │  ├─────────┼─────────┼───────────────┼────────────────────────┤  │     │
│  │  │    1    │crimping │{"level":3,...}│ 2025-10-09 10:30:00   │  │     │
│  │  │    1    │osi      │{"layer":5,...}│ 2025-10-09 09:15:00   │  │     │
│  │  │    2    │linkup   │{"score":450}  │ 2025-10-09 11:00:00   │  │     │
│  │  └─────────┴─────────┴───────────────┴────────────────────────┘  │     │
│  │  Unique constraint: (user_id, challenge_type)                     │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                              TYPICAL USER FLOW
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  SCENARIO 1: First Time Playing                                             │
└─────────────────────────────────────────────────────────────────────────────┘

  1. User opens challenge
       ↓
  2. checkForProgress() queries DB
       ↓
  3. No saved progress found
       ↓
  4. Challenge starts fresh
       ↓
  5. Auto-save begins (every 10s)
       ↓
  6. User plays, state saves periodically
       ↓
  7. User leaves page → exit-save triggers


┌─────────────────────────────────────────────────────────────────────────────┐
│  SCENARIO 2: Returning to Unfinished Challenge                              │
└─────────────────────────────────────────────────────────────────────────────┘

  1. User opens challenge
       ↓
  2. checkForProgress() queries DB
       ↓
  3. Saved progress found!
       ↓
  4. Modal shows: "Continue?" or "Start Fresh?"
       ↓
  5a. User clicks "Continue"            5b. User clicks "Start Fresh"
       ↓                                      ↓
  6a. loadSavedGame event fires         6b. startNewGame event fires
       ↓                                      ↓
  7a. State restored from DB            7b. clearProgress() called
       ↓                                      ↓
  8a. Challenge resumes at saved point  8b. Challenge starts from beginning


┌─────────────────────────────────────────────────────────────────────────────┐
│  SCENARIO 3: Completing Challenge                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  1. User completes all tasks
       ↓
  2. markCompleted(finalState) called
       ↓
  3. State saved with is_completed=true
       ↓
  4. Auto-save stops
       ↓
  5. User leaves and returns later
       ↓
  6. checkForProgress() sees is_completed=true
       ↓
  7. Progress cleared automatically
       ↓
  8. No modal shown, fresh start


═══════════════════════════════════════════════════════════════════════════════
                            DATA FLOW DIAGRAM
═══════════════════════════════════════════════════════════════════════════════

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Browser    │────▶│  JavaScript  │────▶│  Flask API   │────▶│   Database   │
│   (Client)   │◀────│   Manager    │◀────│   Routes     │◀────│  (SQLAlchemy)│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
      │                     │                     │                     │
      │ User Action         │ fetch()             │ Query/Insert        │
      │ (play game)         │ (HTTP)              │ (ORM)               │
      │                     │                     │                     │
      │ Shows Modal ◀───────┤                     │                     │
      │                     │                     │                     │
      │ Button Click ───────▶ Event Dispatch      │                     │
      │                     │ (loadSavedGame)     │                     │
      │                     │                     │                     │
      │ State Restored ◀────┤ JSON Parse          │                     │
      │                     │ (state_data)        │                     │


═══════════════════════════════════════════════════════════════════════════════
                         SAVE MECHANISMS (3 WAYS)
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. AUTO-SAVE (Every 10 seconds)                                            │
│                                                                              │
│  setInterval(() => {                                                        │
│    const state = getStateCallback();                                        │
│    saveProgress(state);  ────────────────▶  API  ────────▶  Database       │
│  }, 10000);                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. EXIT-SAVE (When leaving page)                                           │
│                                                                              │
│  window.addEventListener('beforeunload', () => {                            │
│    const state = getStateCallback();                                        │
│    navigator.sendBeacon('/api/...', state);  ──▶  API  ──▶  Database       │
│  });                                                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. MANUAL-SAVE (On specific events)                                        │
│                                                                              │
│  function onLevelComplete() {                                               │
│    const state = getGameState();                                            │
│    challengeProgress.saveImmediately(state);  ──▶  API  ──▶  Database      │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                            INTEGRATION POINTS
═══════════════════════════════════════════════════════════════════════════════

Challenge Template (HTML)
    ├── {% include 'components/continue_game_modal.html' %}
    ├── <script src=".../challenge-progress-manager.js"></script>
    └── <script>
            // Your challenge code
            window.challengeProgress = new ChallengeProgressManager('type');
            // ... integration code
        </script>


═══════════════════════════════════════════════════════════════════════════════
                          FILE DEPENDENCIES
═══════════════════════════════════════════════════════════════════════════════

migrate_challenge_progress.py  ────creates──────▶  Database Table
                                                         │
                                                         │ stores
                                                         ▼
user/models/challenge_progress.py  ─────ORM─────▶  challenge_progress
                                                         ▲
                                                         │ queries
                                                         │
user/api.py (3 routes)  ─────HTTP────▶  Flask Routes  ──┘
                                              ▲
                                              │
                                         fetch requests
                                              │
static/js/challenge-progress-manager.js  ────┘
                                              │
                                      called by & shows
                                              │
templates/components/continue_game_modal.html
                                              ▲
                                              │
                                          included in
                                              │
templates/user/[challenge].html  ────────────┘


═══════════════════════════════════════════════════════════════════════════════
                              SECURITY LAYER
═══════════════════════════════════════════════════════════════════════════════

Every API request:
    ├── Check session['user_id']  ──▶  401 if not logged in
    ├── Validate input data       ──▶  400 if invalid
    ├── Use parameterized queries ──▶  Prevent SQL injection
    └── Only access own data      ──▶  403 if unauthorized


═══════════════════════════════════════════════════════════════════════════════
                              TECHNOLOGY STACK
═══════════════════════════════════════════════════════════════════════════════

Frontend:
  • Vanilla JavaScript (ES6+)
  • Fetch API for HTTP requests
  • Custom Events for communication
  • localStorage (deprecated, replaced with DB)

Backend:
  • Flask (Python web framework)
  • SQLAlchemy ORM
  • Flask sessions for auth
  • JSON for state serialization

Database:
  • SQLite/PostgreSQL
  • JSON column type for flexible state storage
  • Unique constraints for data integrity


═══════════════════════════════════════════════════════════════════════════════
                          END OF ARCHITECTURE DIAGRAM
═══════════════════════════════════════════════════════════════════════════════
```

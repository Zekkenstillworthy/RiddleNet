# 🔌 CLI Task Assignment Connection - Visual Guide

## Before Fix ❌

```
┌─────────────────────────────────────┐
│  Student executes CLI command       │
│  "show interfaces"                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  executeCLICommand()                │
│  • Processes command                │
│  • Shows output                     │
│  • Ends here                        │
└─────────────────────────────────────┘
               
               ❌ NO CONNECTION
               
┌─────────────────────────────────────┐
│  TaskAssignmentManager              │
│  • Waiting for event...             │
│  • Never receives it                │
│  • CLI not tracked ❌               │
└─────────────────────────────────────┘
```

---

## After Fix ✅

```
┌─────────────────────────────────────┐
│  Student executes CLI command       │
│  "show interfaces"                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  executeCLICommand()                │
│  • Processes command                │
│  • Shows output                     │
│  • ✨ Dispatches event ✨           │
└──────────────┬──────────────────────┘
               │
               │  'cli-command-executed'
               │  CustomEvent
               │
               ▼
┌─────────────────────────────────────┐
│  TaskAssignmentManager              │
│  • Receives event ✅                │
│  • Tracks CLI command               │
│  • Updates progress                 │
│  • Saves to database                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Real-time Updates                  │
│  • Progress bar: 75% → 80%          │
│  • CLI checklist: ✓ show interfaces │
│  • Submit button: Enabled           │
└─────────────────────────────────────┘
```

---

## Event Flow Detail

```
📍 Event Dispatch Locations (4 Total)

1️⃣ dynamic_simulation.html
   └─> Device Interfaces Modal CLI
   
2️⃣ network-simulation-engine.js  
   └─> MVP Configuration Popup CLI
   
3️⃣ network-device-configurator.js
   └─> Legacy Configurator CLI
   
4️⃣ collaboration-real-time.js
   └─> Team/Collaboration CLI

        │ All dispatch same event:
        │ 'cli-command-executed'
        ▼

┌─────────────────────────────────────┐
│  document.addEventListener()        │
│  'cli-command-executed'             │
│  (task_assignment_fix.js:237)       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  trackCLICommand(detail)            │
│  • Push to cli_history[]            │
│  • Log activity                     │
│  • saveProgress()                   │
│  • updateProgressUI()               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  POST /task-progress                │
│  • Updates TaskAssignment model     │
│  • Calculates completion %          │
│  • Emits real-time to instructor    │
└─────────────────────────────────────┘
```

---

## Code Structure

### Event Dispatching Pattern (Added to all 4 locations)

```javascript
// ✅ TASK ASSIGNMENT: Dispatch event for CLI command tracking
console.log('📋 [CLI→TASK] Dispatching cli-command-executed event:', 
    { deviceId, command });

document.dispatchEvent(new CustomEvent('cli-command-executed', {
    detail: {
        device_id: deviceId,      // Device identifier
        command: command,          // Raw command string
        output: response,          // Command output
        timestamp: new Date().toISOString()
    }
}));
```

### Event Listener (Already existed in task_assignment_fix.js)

```javascript
// Line 237 - task_assignment_fix.js
document.addEventListener('cli-command-executed', 
    (e) => this.trackCLICommand(e.detail)
);
```

### Tracking Handler (Already existed)

```javascript
// Line 343 - task_assignment_fix.js
trackCLICommand(detail) {
    if (!this.taskConfig?.enabled) return;

    console.log('💻 [TASK FIX] CLI command executed:', detail.command);
    
    this.userProgress.cli_history.push({
        device_id: detail.device_id,
        command: detail.command,
        output: detail.output,
        executed_at: new Date().toISOString()
    });
    
    this.logActivity('cli_command', {
        device_id: detail.device_id,
        command: detail.command
    });
    
    this.saveProgress();
    this.updateProgressUI();
}
```

---

## Database Storage

### Task Assignment Record

```sql
SELECT * FROM task_assignments 
WHERE simulation_id = 1 AND user_id = 123;
```

```json
{
  "id": 456,
  "simulation_id": 1,
  "user_id": 123,
  "cli_history": [
    {
      "device_id": "R1",
      "command": "configure terminal",
      "output": "Entering configuration mode...",
      "executed_at": "2025-10-21T10:30:00.000Z"
    },
    {
      "device_id": "R1",
      "command": "hostname Router1",
      "output": "Hostname set to Router1",
      "executed_at": "2025-10-21T10:30:15.000Z"
    },
    {
      "device_id": "R1",
      "command": "show interfaces",
      "output": "GigabitEthernet0/0 is up...",
      "executed_at": "2025-10-21T10:30:30.000Z"
    }
  ],
  "completion_percentage": 85.5,
  "status": "in_progress"
}
```

---

## Console Logs to Expect

### When CLI Command Executed:

```
📋 [CLI→TASK] Dispatching cli-command-executed event: 
  {deviceId: "R1", command: "show interfaces"}

💻 [TASK FIX] CLI command executed: show interfaces

📊 [TASK FIX] Activity logged: cli_command 
  {device_id: "R1", command: "show interfaces"}

💾 [TASK FIX] Progress saved successfully
```

---

## UI Indicators

### Task Assignment Sidebar

```
┌─────────────────────────────────────┐
│ 📋 Task Assignment                  │
│ Progress: 85% ████████████░░░       │
├─────────────────────────────────────┤
│ CLI Commands Required:              │
│  ✓ configure terminal               │
│  ✓ hostname Router1                 │
│  ✓ show interfaces                  │
│  ⭘ interface GigabitEthernet0/0     │
│  ⭘ ip address 192.168.1.1 /24       │
├─────────────────────────────────────┤
│ [Submit Task for Grading] 🔓        │
└─────────────────────────────────────┘
```

---

## Success Criteria ✅

- [x] Event dispatched from all 4 CLI locations
- [x] Event caught by TaskAssignmentManager
- [x] CLI commands saved to cli_history
- [x] Progress percentage updates
- [x] UI checkboxes update in real-time
- [x] Database persists CLI history
- [x] Submit button enables at 100%
- [x] Instructor sees real-time progress
- [x] Auto-grading includes CLI score

---

## Troubleshooting

### Issue: Console shows event dispatch but no tracking

**Check:**
1. Is `window.taskAssignmentManager` defined?
   ```javascript
   console.log(window.taskAssignmentManager);
   ```

2. Is task mode enabled for this simulation?
   ```javascript
   console.log(window.taskAssignmentManager?.taskConfig?.enabled);
   ```

3. Is the event listener attached?
   ```javascript
   // Should see listener in setupEventListeners()
   ```

### Issue: Progress not updating in UI

**Check:**
1. Console for "Progress saved successfully"
2. Network tab for POST to `/task-progress`
3. Check if sidebar is visible
4. Verify `updateProgressUI()` is called

### Issue: CLI history empty in database

**Check:**
1. Is student authenticated?
2. Check simulation_id matches
3. Verify TaskAssignment record exists
4. Check database logs for errors

---

**Visual Guide Created:** October 21, 2025  
**Status:** CLI Commands → Task Assignment = CONNECTED ✅

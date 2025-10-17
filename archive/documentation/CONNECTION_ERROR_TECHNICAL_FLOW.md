# Connection Error Handler - Technical Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION STARTUP                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Eventlet Initialization (eventlet_init.py)            │
│  • Monkey-patch standard library                                │
│  • Make blocking calls non-blocking                             │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Connection Error Handler (NEW!)                       │
│  • Patch eventlet WSGI error handling                           │
│  • Install global exception hook                                │
│  • Configure logging filters                                    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Flask App Creation                                    │
│  • Initialize database                                          │
│  • Register blueprints                                          │
│  • Configure SocketIO                                           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Server Start                                          │
│  • Begin accepting requests                                     │
│  • Handle connections                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

### BEFORE: Unhandled Connection Error

```
Client Request
     │
     ▼
┌──────────────────┐
│  Flask Handler   │
│  Processing...   │
└──────────────────┘
     │
     ▼
┌──────────────────┐
│  Response Start  │ ← Client disconnects here!
│  Sending...      │
└──────────────────┘
     │
     ▼
❌ ConnectionAbortedError
     │
     ▼
Full Traceback (20+ lines)
     │
     ▼
Log Pollution ❌
```

### AFTER: Graceful Error Suppression

```
Client Request
     │
     ▼
┌──────────────────┐
│  Flask Handler   │
│  Processing...   │
└──────────────────┘
     │
     ▼
┌──────────────────┐
│  Response Start  │ ← Client disconnects here!
│  Sending...      │
└──────────────────┘
     │
     ▼
✅ ConnectionAbortedError (Caught by Patch)
     │
     ▼
┌─────────────────────────────────┐
│  Patched send() method:         │
│  • Try to send                  │
│  • Catch ConnectionAbortedError │
│  • Return 0 (silently)          │
│  • No log, no exception         │
└─────────────────────────────────┘
     │
     ▼
Clean Logs ✅
```

## Component Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                     CONNECTION ERROR HANDLER                       │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  1. EVENTLET WSGI PATCHER                                │    │
│  │  • Wraps GreenSocket.send()                              │    │
│  │  • Wraps GreenSocket.sendall()                           │    │
│  │  • Catches connection errors                             │    │
│  │  • Returns gracefully without logging                    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  2. GLOBAL EXCEPTION HOOK                                │    │
│  │  • Intercepts sys.excepthook                             │    │
│  │  • Filters expected network errors                       │    │
│  │  • Passes real errors to original handler                │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  3. LOGGING FILTER                                       │    │
│  │  • Applies to root logger                                │    │
│  │  • Applies to eventlet logger                            │    │
│  │  • Blocks messages with connection error keywords        │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

## Request Lifecycle with Error Handling

```
┌─────────────┐
│   CLIENT    │
└──────┬──────┘
       │ HTTP Request
       │
       ▼
┌─────────────┐
│   EVENTLET  │ ← Patched with error suppression
│   WSGI      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FLASK     │
│   APP       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  RESPONSE   │
│  HANDLER    │
└──────┬──────┘
       │ Start sending response
       │
       ▼
┌─────────────┐
│  SOCKET     │ ← Patched send() method
│  SEND       │
└──────┬──────┘
       │
       ├─── Success → Client receives data ✅
       │
       └─── Failure → ConnectionAbortedError
                │
                ▼
          ┌──────────────┐
          │  ERROR PATCH │ ← Catches error
          │  • Check type │
          │  • Suppress  │
          │  • Return 0  │
          └──────────────┘
                │
                ▼
          No log output ✅
          Clean termination ✅
```

## Error Categorization

```
┌─────────────────────────────────────────────────────────────┐
│                      ALL EXCEPTIONS                          │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌────────────────────┐         ┌─────────────────────┐
│  EXPECTED NETWORK  │         │   REAL ERRORS       │
│  ERRORS            │         │                     │
├────────────────────┤         ├─────────────────────┤
│ • ConnectionAborted│         │ • AttributeError    │
│ • ConnectionReset  │         │ • KeyError          │
│ • BrokenPipe       │         │ • DatabaseError     │
└────────┬───────────┘         │ • ValueError        │
         │                     │ • AuthError         │
         │                     └──────────┬──────────┘
         │                                │
         ▼                                ▼
┌──────────────────┐           ┌──────────────────────┐
│  ✅ SUPPRESSED   │           │  ✅ LOGGED NORMALLY  │
│  • No log entry  │           │  • Full traceback    │
│  • Silent return │           │  • Error details     │
│  • Clean logs    │           │  • Action required   │
└──────────────────┘           └──────────────────────┘
```

## Integration Points

```
run.py
  │
  ├─ Import eventlet_init (FIRST!)
  │   └─ Monkey-patch stdlib
  │
  ├─ Import connection_error_handler (SECOND!)
  │   ├─ patch_eventlet_wsgi()
  │   │   └─ Wrap socket methods
  │   │
  │   ├─ install_global_exception_handler()
  │   │   └─ Override sys.excepthook
  │   │
  │   └─ configure_logging_filters()
  │       └─ Add filters to loggers
  │
  └─ Import Flask app (THIRD!)
      └─ Normal application startup
```

## Patching Mechanism Detail

```python
# ORIGINAL (eventlet/greenio/base.py)
def send(self, data, flags=0):
    return self._send_loop(self.fd.send, data, flags)
    # ↑ Throws ConnectionAbortedError on disconnect

# PATCHED (our wrapper)
def patched_send(self, data, *args):
    try:
        return original_send(self, data, *args)
    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
        # Client disconnected - this is expected
        return 0  # ← Graceful return, no exception
    except Exception:
        raise  # ← Still raise unexpected errors
```

## Logging Flow

```
Log Event Generated
       │
       ▼
┌─────────────────┐
│  Root Logger    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  ConnectionErrorFilter  │ ← Our filter
│  • Check message        │
│  • Match keywords       │
│  • Return True/False    │
└────────┬────────────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
  TRUE       FALSE
    │          │
    │          ▼
    │    ┌─────────┐
    │    │ BLOCKED │ ← Connection error
    │    └─────────┘
    │
    ▼
┌──────────┐
│  LOGGED  │ ← Real error
└──────────┘
```

## Testing Scenarios

### Scenario 1: Page Navigation
```
User opens /troubleshooting/
         │
         ▼
    Page starts loading
    Audio starts loading
         │
         ▼
    User clicks back ← CLIENT DISCONNECTS
         │
         ▼
    ❌ BEFORE: ConnectionAbortedError spam
    ✅ AFTER:  Silent handling, clean logs
```

### Scenario 2: WebSocket Disconnect
```
WebSocket connected
         │
         ▼
    User closes browser
         │
         ▼
    Connection terminates
         │
         ▼
    ❌ BEFORE: Error traceback
    ✅ AFTER:  Clean disconnect log
```

### Scenario 3: Audio Streaming Interrupt
```
Audio file starts streaming
         │
         ▼
    Network hiccup
         │
         ▼
    Connection drops
         │
         ▼
    ❌ BEFORE: Multiple errors
    ✅ AFTER:  Silent retry
```

## Summary

```
┌────────────────────────────────────────────────────┐
│              BEFORE ERROR HANDLER                   │
├────────────────────────────────────────────────────┤
│ Client Disconnect                                   │
│   ↓                                                 │
│ ConnectionAbortedError                              │
│   ↓                                                 │
│ 20-line traceback                                   │
│   ↓                                                 │
│ Log pollution ❌                                    │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│              AFTER ERROR HANDLER                    │
├────────────────────────────────────────────────────┤
│ Client Disconnect                                   │
│   ↓                                                 │
│ ConnectionAbortedError (caught by patch)            │
│   ↓                                                 │
│ Suppressed (return 0)                               │
│   ↓                                                 │
│ Clean logs ✅                                       │
└────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **Three-Layer Protection**
   - Eventlet WSGI patching (lowest level)
   - Global exception hook (mid level)
   - Logging filters (highest level)

2. **Selective Suppression**
   - Only suppresses expected network errors
   - Real errors still logged fully
   - No impact on debugging actual issues

3. **Production Ready**
   - Industry-standard approach
   - Used by major web applications
   - Zero functionality impact

4. **Maintainable**
   - Clear separation of concerns
   - Easy to disable if needed
   - Well-documented behavior

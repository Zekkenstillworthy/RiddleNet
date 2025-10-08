# JavaScript Function Scope Fixes Summary

## Issue Description
After adding TCP/IP model support to the OSI simulation, the page stopped working due to multiple JavaScript `ReferenceError` exceptions. The console showed errors like:
- `Uncaught ReferenceError: drag is not defined`
- `Uncaught ReferenceError: allowDrop is not defined`
- `Uncaught ReferenceError: switchModel is not defined`

## Root Cause
The `renderModel()` function dynamically generates HTML content using template literals and injects it via `innerHTML`. This dynamically generated HTML includes inline event handlers (e.g., `onclick="switchModel('osi')"`, `ondragstart="drag(event)"`). 

**Problem**: Functions defined within a `<script>` block are not accessible to inline event handlers in dynamically generated HTML. They need to be attached to the `window` object to be globally accessible.

## Solution Applied
Converted all function declarations to `window` object properties for functions that are referenced in inline event handlers.

### Functions Fixed (9 total)

| Function | Original Declaration | Fixed Declaration | Line Location | Referenced In |
|----------|---------------------|-------------------|---------------|---------------|
| `allowDrop` | `function allowDrop(event)` | `window.allowDrop = function(event)` | ~1801 | ondragover handlers |
| `drag` | `function drag(event)` | `window.drag = function(event)` | ~1808 | ondragstart handlers |
| `drop` | `function drop(event)` | `window.drop = function(event)` | ~1817 | ondrop handlers |
| `switchModel` | `function switchModel(model)` | `window.switchModel = function(model)` | ~1620 | onclick handlers (model buttons) |
| `showLayerInfo` | `function showLayerInfo(layer)` | `window.showLayerInfo = function(layer)` | ~1898 | onclick handlers (layer pills) |
| `closeModal` | `function closeModal()` | `window.closeModal = function()` | ~1988 | onclick handlers (close buttons) |
| `closeModalAndCheckCompletion` | `function closeModalAndCheckCompletion()` | `window.closeModalAndCheckCompletion = function()` | ~2000 | onclick handlers (quiz modals) |
| `resetSimulation` | `function resetSimulation()` | `window.resetSimulation = function()` | ~2595 | onclick handlers (reset button) |
| `checkQuizAnswer` | `function checkQuizAnswer(selected, correct, explanation)` | `window.checkQuizAnswer = function(selected, correct, explanation)` | ~2263 | onclick handlers (quiz buttons) |

## Affected Code Patterns

### 1. Model Selector Buttons
```javascript
// Dynamically generated in renderModel()
<button class="model-btn" onclick="switchModel('osi')">OSI Model</button>
<button class="model-btn" onclick="switchModel('tcpip')">TCP/IP Model</button>
```

### 2. Draggable Layer Pills
```javascript
// Dynamically generated in renderModel()
<div class="draggable-item" 
     draggable="true" 
     ondragstart="drag(event)" 
     onclick="showLayerInfo(${layer})">
```

### 3. Drop Slots
```javascript
// Dynamically generated in renderModel()
<div class="drop-slot" 
     ondrop="drop(event)" 
     ondragover="allowDrop(event)">
```

### 4. Quiz Answer Buttons
```javascript
// Dynamically generated when quiz opens
<button class="quiz-option-button" 
        onclick="checkQuizAnswer(${index}, ${currentQuizData.correct}, '${currentQuizData.explanation}')">
```

### 5. Modal Close Buttons
```javascript
// Static HTML with inline handlers
<button class="close-btn" onclick="closeModal()">×</button>
<button onclick="closeModalAndCheckCompletion()">Continue</button>
```

## Technical Details

### Why This Pattern Is Needed
1. **innerHTML injection timing**: When `renderModel()` is called, it replaces entire sections of the DOM with new HTML strings
2. **Event handler parsing**: The browser parses inline event handlers (`onclick`, `ondragstart`, etc.) at runtime when the HTML is injected
3. **Scope resolution**: Inline handlers look for functions in the global (`window`) scope, not in the script's local scope
4. **Dynamic content**: Since content is generated dynamically based on the `currentModel` variable, handlers can't be attached via `addEventListener()` at page load

### Alternative Patterns (Not Used Here)
- **Event Delegation**: Could attach listeners to parent containers and use `event.target` to determine which element was clicked
  - **Con**: Would require significant refactoring of existing drag-and-drop logic
- **No Inline Handlers**: Could generate HTML without inline handlers and attach listeners via `addEventListener()` after injection
  - **Con**: More complex code, harder to maintain parameter passing (e.g., layer numbers)

## Testing Checklist

After these fixes, verify:
- ✅ Model selector buttons work (switch between OSI and TCP/IP)
- ✅ Layer pills are draggable (ondragstart fires)
- ✅ Drop slots accept drops (ondragover and ondrop fire)
- ✅ Clicking layer pills shows info modal (onclick fires)
- ✅ Quiz answer buttons work (onclick fires with correct parameters)
- ✅ Modal close buttons work (onclick fires)
- ✅ Reset button works (onclick fires)
- ✅ No console errors appear

## Files Modified
- `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\templates\user\osi-simulation.html`

## Related Documentation
- TCP/IP Model Addition: `TCPIP_MODEL_ADDITION_SUMMARY.md`
- Drag & Drop Fixes: `DRAG_DROP_FIX_SUMMARY.md`

---

**Status**: ✅ All 9 functions have been successfully converted to window object properties
**Date**: 2025-01-XX
**Impact**: Critical - Fixes prevent the entire simulation from functioning

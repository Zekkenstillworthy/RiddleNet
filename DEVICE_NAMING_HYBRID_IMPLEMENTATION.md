# 🎉 Device Naming Scenario - HYBRID APPROACH IMPLEMENTED!

## ✅ What Changed

The "Device Naming" scenario now **ACTUALLY REQUIRES DEVICE NAMING**! 

### Before (Old Version):
- ❌ Devices pre-named with professional names
- ❌ Only required connecting devices
- ❌ No CLI usage needed
- ❌ Name was misleading - just a connection exercise

### After (New Hybrid Version):
- ✅ Devices start with GENERIC names (PC-1, PC-2, Switch-1)
- ✅ **PART 1: Rename devices** using CLI `hostname` command
- ✅ **PART 2: Connect devices** using WIRED button
- ✅ Name is now ACCURATE - requires both naming AND connecting!

---

## 🎯 How to Complete the NEW Device Naming Scenario

### PART 1: Rename All Devices (Using CLI)

**Initial Device Names:**
- `PC-1` (needs to become `Workstation-01`)
- `PC-2` (needs to become `Workstation-02`)
- `Switch-1` (needs to become `Core-Switch`)

**Steps:**

1. **Rename First PC:**
   - Double-click `PC-1`
   - CLI opens automatically
   - Type: `hostname Workstation-01`
   - Press ENTER
   - Close CLI (click X or press ESC)

2. **Rename Second PC:**
   - Double-click `PC-2`
   - CLI opens
   - Type: `hostname Workstation-02`
   - Press ENTER
   - Close CLI

3. **Rename Switch:**
   - Double-click `Switch-1`
   - CLI opens
   - Type: `hostname Core-Switch`
   - Press ENTER
   - Close CLI

**✅ After PART 1 Completion:**
```
Console shows:
✅ pc named "Workstation-01" - FOUND ✅
✅ pc named "Workstation-02" - FOUND ✅
✅ switch named "Core-Switch" - FOUND ✅
✅ All devices have correct names!
```

---

### PART 2: Connect All Devices (Using WIRED Button)

**Required Connections:**
- `Workstation-01` → `Core-Switch`
- `Workstation-02` → `Core-Switch`

**Steps:**

4. **Click WIRED button** (bottom of screen)

5. **Create First Connection:**
   - Click `Workstation-01` (left PC)
   - Click `Core-Switch` (center switch)
   - Cyan line appears!

6. **Create Second Connection:**
   - Click `Workstation-02` (left PC)
   - Click `Core-Switch` (center switch)
   - Second cyan line appears!

**✅ After PART 2 Completion:**
```
Console shows:
✅ All connections present!
🎉 ========== ALL OBJECTIVES MET! COMPLETING SCENARIO... ==========
```

---

## 🔍 Console Output Walkthrough

### When Scenario Starts:
```
🏷️ ========== STARTING DEVICE NAMING SCENARIO ==========
📋 Objective: Rename 2 PCs + 1 Switch, then connect them
💡 Focus: Practice naming devices AND building connections

⚠️ ========== HOW TO COMPLETE THIS SCENARIO ==========
✅ PART 1: RENAME ALL DEVICES using CLI
   1️⃣ Double-click first PC → CLI opens
   2️⃣ Type: hostname Workstation-01
   3️⃣ Press ENTER, then close CLI
   4️⃣ Double-click second PC → Type: hostname Workstation-02
   5️⃣ Press ENTER, then close CLI
   6️⃣ Double-click Switch → Type: hostname Core-Switch
   7️⃣ Press ENTER, then close CLI

✅ PART 2: CONNECT ALL DEVICES using WIRED button
   8️⃣ Click WIRED button at bottom
   9️⃣ Click Workstation-01 → Click Core-Switch
   🔟 Click Workstation-02 → Click Core-Switch

🎉 AUTO-COMPLETION will trigger when BOTH parts are done!

✅ Devices placed on canvas with GENERIC names: [
    { type: 'pc', label: 'PC-1' },
    { type: 'pc', label: 'PC-2' },
    { type: 'switch', label: 'Switch-1' }
]

🎯 Requirements:
   ✓ Rename Devices:
      • PC-1 → Workstation-01
      • PC-2 → Workstation-02
      • Switch-1 → Core-Switch
   ✓ Create Connections:
      • Workstation-01 → Core-Switch
      • Workstation-02 → Core-Switch

📝 Current Status:
   ❌ Device names: GENERIC (need renaming!)
   ❌ Connections: 0 (need wiring!)

💡 START WITH PART 1: Double-click a device to open CLI!
```

---

### During PART 1 (After renaming first PC):
```
🎯 ========== SCENARIO COMPLETION CHECK ==========
📝 Current Scenario: device-naming
⏱️ Time Elapsed: 5 seconds

🖥️ STEP 1: Checking Device Requirements...
  ✅ All devices present!

🔗 STEP 2: Checking Connection Requirements...
  ✓ pc ↔ switch: Found 0, Need 2 ❌
  ❌ FAILED: Missing 2 more pc-switch connection(s)
⏸️ Waiting for correct connections...

🏷️ STEP 3: Checking Device Naming Requirements...
  🔍 Required Device Names: [
    { type: 'pc', label: 'Workstation-01' },
    { type: 'pc', label: 'Workstation-02' },
    { type: 'switch', label: 'Core-Switch' }
  ]
  📝 Current Device Labels: [
    { type: 'pc', label: 'Workstation-01' },  ← RENAMED! ✅
    { type: 'pc', label: 'PC-2' },             ← Still generic ❌
    { type: 'switch', label: 'Switch-1' }      ← Still generic ❌
  ]
  
  ✅ pc named "Workstation-01" - FOUND ✅
  ❌ pc named "Workstation-02" - NOT FOUND ❌
     Current pc names: [Workstation-01, PC-2]
     💡 TIP: Double-click the device and use CLI command: hostname Workstation-02
⏸️ Waiting for devices to be renamed...
```

---

### After PART 1 Complete (All devices renamed):
```
🏷️ STEP 3: Checking Device Naming Requirements...
  📝 Current Device Labels: [
    { type: 'pc', label: 'Workstation-01' },
    { type: 'pc', label: 'Workstation-02' },
    { type: 'switch', label: 'Core-Switch' }
  ]
  
  ✅ pc named "Workstation-01" - FOUND ✅
  ✅ pc named "Workstation-02" - FOUND ✅
  ✅ switch named "Core-Switch" - FOUND ✅
  ✅ All devices have correct names!

🔗 STEP 2: Checking Connection Requirements...
  ✓ pc ↔ switch: Found 0, Need 2 ❌
⏸️ Waiting for correct connections...

💡 NOW DO PART 2: Click WIRED button and connect the devices!
```

---

### After BOTH Parts Complete:
```
🎯 ========== SCENARIO COMPLETION CHECK ==========

🖥️ STEP 1: Checking Device Requirements...
  ✅ All devices present!

🔗 STEP 2: Checking Connection Requirements...
  🔌 Current Connections: [
    { from: 'pc', to: 'switch', fromLabel: 'Workstation-01', toLabel: 'Core-Switch' },
    { from: 'pc', to: 'switch', fromLabel: 'Workstation-02', toLabel: 'Core-Switch' }
  ]
  ✓ pc ↔ switch: Found 2, Need 2 ✅
  ✅ All connections present!

🏷️ STEP 3: Checking Device Naming Requirements...
  ✅ pc named "Workstation-01" - FOUND ✅
  ✅ pc named "Workstation-02" - FOUND ✅
  ✅ switch named "Core-Switch" - FOUND ✅
  ✅ All devices have correct names!

🎉 ========== ALL OBJECTIVES MET! COMPLETING SCENARIO... ==========
```

---

## 💻 Technical Implementation Details

### New Scenario Objective Structure:
```javascript
'device-naming': {
    requiredDevices: [
        { type: 'pc', count: 2 }, 
        { type: 'switch', count: 1 }
    ],
    requiredConnections: [
        { from: 'pc', to: 'switch', count: 2 }
    ],
    requiredDeviceNames: [          // ← NEW FIELD!
        { type: 'pc', label: 'Workstation-01' },
        { type: 'pc', label: 'Workstation-02' },
        { type: 'switch', label: 'Core-Switch' }
    ],
    description: "Rename devices using CLI and connect them to build a properly named network"
}
```

### New Check Function:
```javascript
function checkDeviceNamesRequirements(requiredDeviceNames) {
    // Skip if no naming requirements
    if (!requiredDeviceNames || requiredDeviceNames.length === 0) {
        return true;
    }
    
    // For each required device name
    for (const requirement of requiredDeviceNames) {
        // Find device with matching type AND label
        const matchingDevice = devices.find(device => 
            device.type === requirement.type && 
            device.label === requirement.label
        );
        
        if (!matchingDevice) {
            // Show helpful error with current names
            console.log(`❌ ${requirement.type} named "${requirement.label}" - NOT FOUND`);
            console.log(`💡 TIP: Use CLI command: hostname ${requirement.label}`);
            return false;
        }
    }
    
    return true;
}
```

### Updated Completion Flow:
```javascript
function checkScenarioCompletion() {
    // Step 1: Check devices present
    if (!checkDeviceRequirements(...)) return false;
    
    // Step 2: Check connections made
    if (!checkConnectionRequirements(...)) return false;
    
    // Step 3: Check device names (NEW!)
    if (objectives.requiredDeviceNames) {
        if (!checkDeviceNamesRequirements(...)) return false;
    }
    
    // All checks passed - complete!
    completeScenarioAutomatically();
}
```

---

## 🎓 Educational Benefits

### Why This Hybrid Approach is Better:

**1. Teaches CLI Usage**
- Students must use the `hostname` command
- Practice opening CLI, typing commands, closing CLI
- Real-world device naming experience

**2. Teaches Network Building**
- Students must use WIRED button
- Practice creating connections
- Understanding network topology

**3. Sequential Learning**
- Logical flow: Name first, then connect
- Can't skip naming step (auto-check enforces it)
- Both skills required for completion

**4. Clear Feedback**
- Console shows exactly what's missing
- Helpful tips for each incomplete step
- Visual progress through 3 check steps

**5. Accurate Naming**
- Scenario name now matches what you do
- No more confusion about completion method
- Professional naming conventions demonstrated

---

## 🔄 Migration from Old Version

### If You Completed Old Version:
The old version only required connections, not naming. If you already completed the old "Device Naming" scenario, you can:

**Option A:** Mark it complete and move on (you learned connections)

**Option B:** Retry with new version to learn CLI naming

### User Experience:
- Users who refresh browser will see NEW version
- Scenario still in Phase 4: Basic Configuration
- Same position in curriculum, enhanced content

---

## 📊 Comparison Chart

| Feature | Old Version | New Hybrid Version |
|---------|-------------|-------------------|
| **Device Names** | Pre-named (Workstation-01, etc.) | Generic (PC-1, PC-2, Switch-1) |
| **CLI Usage** | Not required ❌ | Required ✅ |
| **Connections** | Required ✅ | Required ✅ |
| **Learning Objectives** | Connection only | Naming + Connection |
| **Steps to Complete** | 1 (wire devices) | 2 (rename, then wire) |
| **Scenario Name Accuracy** | Misleading ❌ | Accurate ✅ |
| **Console Guidance** | Basic | Step-by-step with tips |
| **Auto-Check Steps** | 2 (devices, connections) | 3 (devices, connections, names) |

---

## 🚀 How to Test It

1. **Hard refresh browser** (Ctrl+F5) to load new code
2. **Open DevTools Console** (F12)
3. **Start Device Naming scenario** from Phase 4
4. **Follow console instructions** - it guides you through both parts!

Expected timeline:
- **Part 1 (Renaming):** ~1-2 minutes
- **Part 2 (Connecting):** ~30 seconds
- **Total:** ~2-3 minutes for complete scenario

---

## ✨ Summary

**Now the "Device Naming" scenario truly lives up to its name!**

Students will:
1. ✅ Learn CLI `hostname` command
2. ✅ Practice meaningful device naming
3. ✅ Build network connections with WIRED button
4. ✅ Understand complete network setup workflow

The hybrid approach combines **configuration skills** (naming) with **physical skills** (wiring) for a comprehensive learning experience! 🎓🔧

# 🎯 DEVICE NAMING - QUICK COMPLETION GUIDE

## ⚠️ YOUR CURRENT SITUATION

Looking at your screenshot, you're viewing **Network Expansion** (which is already completed ✅ with Score: 100%).

You need to **start the Device Naming scenario** from Phase 4!

---

## 📋 WHAT YOU NEED TO DO

### **Step 1: Start Device Naming Scenario**
Go to **Phase 4: Basic Configuration** and click on **Device Naming**.

### **Step 2: You'll See This Layout**
```
Workstation-01 (PC)    
                        Core-Switch (Switch)
Workstation-02 (PC)
```
**Currently: NO connections**

### **Step 3: Make TWO Connections**

#### **Connection 1:**
1. Click the **WIRED** button (bottom toolbar)
2. Click **Workstation-01** (top-left PC)
3. Click **Core-Switch** (center Switch)
4. ✅ You'll see a cyan cable line!

#### **Connection 2:**
1. The **WIRED** button is still active
2. Click **Workstation-02** (bottom-left PC)
3. Click **Core-Switch** (center Switch)
4. ✅ You'll see a second cyan cable line!

### **Step 4: Auto-Completion!**
Within **500ms**, the scenario will:
- ✅ Detect both PC-Switch connections
- ✅ Complete automatically
- ✅ Save 100% score to Challenge Results
- ✅ Unlock next scenario

---

## 🔍 WHAT THE CONSOLE WILL SHOW

### **When You Start:**
```
🏷️ ========== STARTING DEVICE NAMING SCENARIO ==========
📋 Objective: 2 PCs + 1 Switch
🔗 Required Connections: Both PCs → Switch

⚠️ ========== HOW TO COMPLETE THIS SCENARIO ==========
❌ DO NOT use the CLI (hostname command) - that's for renaming only!
✅ STEP 1: Click the WIRED button at the bottom
✅ STEP 2: Click on Workstation-01 (left PC)
✅ STEP 3: Click on Core-Switch (center)
✅ STEP 4: Click on Workstation-02 (left PC)
✅ STEP 5: Click on Core-Switch (center) again
🎉 AUTO-COMPLETION will trigger within 500ms!

✅ Devices placed on canvas: [
    { type: 'pc', label: 'Workstation-01' },
    { type: 'pc', label: 'Workstation-02' },
    { type: 'switch', label: 'Core-Switch' }
]
```

### **After First Connection:**
```
🎯 ========== SCENARIO COMPLETION CHECK ==========
📝 Current Scenario: device-naming

🖥️ STEP 1: Checking Device Requirements...
  ✅ All devices present!

🔗 STEP 2: Checking Connection Requirements...
  🔌 Current Connections: [
    { from: 'pc', to: 'switch', fromLabel: 'Workstation-01', toLabel: 'Core-Switch' }
  ]
  ✓ pc ↔ switch: Found 1, Need 2 ❌
  ❌ FAILED: Missing 1 more pc-switch connection(s)
⏸️ Waiting for correct connections...
```

### **After Second Connection (COMPLETE!):**
```
🎯 ========== SCENARIO COMPLETION CHECK ==========
📝 Current Scenario: device-naming

🖥️ STEP 1: Checking Device Requirements...
  ✅ All devices present!

🔗 STEP 2: Checking Connection Requirements...
  🔌 Current Connections: [
    { from: 'pc', to: 'switch', fromLabel: 'Workstation-01', toLabel: 'Core-Switch' },
    { from: 'pc', to: 'switch', fromLabel: 'Workstation-02', toLabel: 'Core-Switch' }
  ]
  ✓ pc ↔ switch: Found 2, Need 2 ✅
  ✅ All connections present!

🎉 ========== ALL OBJECTIVES MET! COMPLETING SCENARIO... ==========
```

---

## ✅ FINAL TOPOLOGY (What You Need)

```
Workstation-01 ──────┐
                     ├── Core-Switch
Workstation-02 ──────┘
```

**This creates a simple star topology with 2 connections!**

---

## 🚨 COMMON MISTAKES TO AVOID

### ❌ **Mistake 1: Opening CLI**
- **DON'T** double-click devices
- **DON'T** type `hostname` commands
- The CLI is for **renaming**, not for completing scenarios!

### ❌ **Mistake 2: Wrong Scenario**
- Make sure you're in **Device Naming** (Phase 4)
- NOT in **Network Expansion** (Phase 3) - that's already done!

### ❌ **Mistake 3: Missing Connections**
- You need **BOTH** PCs connected to the Switch
- **ONE** connection won't complete it

### ❌ **Mistake 4: Not Using WIRED Button**
- You MUST click the **WIRED** button first
- Then click the devices to connect them

---

## 🧪 TESTING CHECKLIST

Before asking for help, verify:

- [ ] I refreshed the browser (Ctrl+F5)
- [ ] I opened the console (F12 → Console tab)
- [ ] I'm in **Phase 4: Device Naming** (not Network Expansion!)
- [ ] I see **3 devices** on canvas (2 PCs + 1 Switch)
- [ ] I clicked the **WIRED** button
- [ ] I made **1st connection**: Workstation-01 → Core-Switch
- [ ] I made **2nd connection**: Workstation-02 → Core-Switch
- [ ] I see **2 cyan cables** on the canvas
- [ ] The console shows "ALL OBJECTIVES MET!"

---

## 📊 CURRENT VS TARGET

### **Your Current View (Screenshot):**
- Showing: **Network Expansion** (Phase 3)
- Status: ✅ **Already Completed** (Score: 100%)
- Topology: PC → Switch → Router

### **What You Need:**
- Navigate to: **Phase 4: Device Naming**
- Status: ⚠️ **Not Started**
- Topology: 2 PCs → 1 Switch (no router!)

---

## 🎯 SUMMARY

1. **Go to Phase 4** (not Phase 3!)
2. **Click Device Naming** scenario
3. **Click WIRED button** (bottom toolbar)
4. **Connect PC 1 to Switch** (click PC, then Switch)
5. **Connect PC 2 to Switch** (click PC, then Switch)
6. **Done!** Auto-completion happens!

**That's it - literally just 2 connections!** 🎉

---

## 💡 WHY IT'S CALLED "DEVICE NAMING"

The scenario is called "Device Naming" because:
- Devices come **pre-named** with professional examples
- You **observe** the naming conventions (Workstation-01, Core-Switch)
- You **learn** how real networks use descriptive names

**You don't manually name them - you just connect them!**

---

**Now navigate to Device Naming and wire those PCs! 🔌✨**

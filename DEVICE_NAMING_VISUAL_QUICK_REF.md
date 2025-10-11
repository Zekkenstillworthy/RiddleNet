# 🎯 Device Naming - Quick Visual Reference

## 📋 Completion Checklist

### PART 1: RENAME DEVICES ✏️
- [ ] Double-click PC-1 → Type `hostname Workstation-01` → Close CLI
- [ ] Double-click PC-2 → Type `hostname Workstation-02` → Close CLI  
- [ ] Double-click Switch-1 → Type `hostname Core-Switch` → Close CLI

### PART 2: CONNECT DEVICES 🔌
- [ ] Click WIRED button
- [ ] Click Workstation-01 → Click Core-Switch (cyan line appears)
- [ ] Click Workstation-02 → Click Core-Switch (second cyan line appears)

### ✅ AUTO-COMPLETE!
When BOTH parts are done, scenario completes automatically! 🎉

---

## 🎨 Visual Topology

### Initial State (Generic Names):
```
┌──────────┐
│  PC-1    │ ← Need to rename to "Workstation-01"
└──────────┘

┌──────────┐
│  PC-2    │ ← Need to rename to "Workstation-02"
└──────────┘

    ┌──────────┐
    │Switch-1  │ ← Need to rename to "Core-Switch"
    └──────────┘
```

### After PART 1 (Renamed):
```
┌────────────────┐
│ Workstation-01 │ ✅ Renamed!
└────────────────┘

┌────────────────┐
│ Workstation-02 │ ✅ Renamed!
└────────────────┘

    ┌──────────────┐
    │ Core-Switch  │ ✅ Renamed!
    └──────────────┘
```

### After PART 2 (Connected):
```
┌────────────────┐
│ Workstation-01 │────┐
└────────────────┘    │ ✅ Wired!
                      │
┌────────────────┐    │
│ Workstation-02 │────┤ ✅ Wired!
└────────────────┘    │
                      │
    ┌──────────────┐  │
    │ Core-Switch  │──┘
    └──────────────┘
```

---

## 🖥️ CLI Commands Reference

### Opening CLI:
- **Double-click** any device
- CLI modal appears automatically

### Renaming Command:
```bash
hostname <NewName>
```

**Examples:**
```bash
hostname Workstation-01
hostname Workstation-02
hostname Core-Switch
```

### Closing CLI:
- Click **X** button (top-right)
- OR Press **ESC** key

---

## 📊 Progress Indicators

### Console Shows 3 Steps:

**STEP 1: ✅ Device Requirements** (Auto-satisfied at start)
```
✅ pc: Found 2, Need 2 ✅
✅ switch: Found 1, Need 1 ✅
```

**STEP 2: 🔌 Connection Requirements** (Do in PART 2)
```
Initially:
❌ pc ↔ switch: Found 0, Need 2 ❌

After PART 2:
✅ pc ↔ switch: Found 2, Need 2 ✅
```

**STEP 3: 🏷️ Device Naming Requirements** (Do in PART 1)
```
Initially:
❌ pc named "Workstation-01" - NOT FOUND ❌
   Current pc names: [PC-1, PC-2]
   💡 TIP: Use CLI command: hostname Workstation-01

After PART 1:
✅ pc named "Workstation-01" - FOUND ✅
✅ pc named "Workstation-02" - FOUND ✅
✅ switch named "Core-Switch" - FOUND ✅
```

---

## ⚡ Troubleshooting

### "My device names aren't changing!"
- Make sure you pressed **ENTER** after typing the hostname command
- Check spelling - names are **case-sensitive**!
- Close CLI after each rename

### "Connections won't create!"
- Click **WIRED** button first (bottom of screen)
- Click on device icons, not empty space
- Must use renamed devices (complete PART 1 first recommended)

### "Scenario won't complete!"
- Check console for which step failed
- All 3 steps must show ✅
- Auto-check runs every 500ms - wait a moment!

### "I don't see the console output!"
- Press **F12** to open DevTools
- Click **Console** tab
- Refresh and restart scenario

---

## 🎓 Learning Objectives

After completing this scenario, you will know how to:

1. **Use CLI commands** to configure network devices
2. **Apply naming conventions** for professional network management
3. **Create physical connections** between network devices
4. **Build a basic network topology** with proper organization
5. **Follow a systematic workflow** for network setup

---

## 🔄 Order Matters?

**Recommended:** Do PART 1 (naming) first, then PART 2 (connecting)

**But technically:** Order doesn't matter! You can:
- Name all devices first, then connect them ✅
- Connect devices first, then rename them ✅
- Mix and match (rename one, connect one, etc.) ✅

The auto-check validates ALL requirements regardless of order!

**However:** Console output is clearer if you follow the recommended order.

---

## 📱 Expected Time

| Task | Estimated Time |
|------|----------------|
| Rename PC-1 | 15 seconds |
| Rename PC-2 | 15 seconds |
| Rename Switch-1 | 15 seconds |
| **PART 1 Total** | **~1 minute** |
| Click WIRED button | 2 seconds |
| Connect Workstation-01 | 5 seconds |
| Connect Workstation-02 | 5 seconds |
| **PART 2 Total** | **~15 seconds** |
| **GRAND TOTAL** | **~1-2 minutes** |

---

## 🎉 Success Indicators

You know you're done when you see:

```
🎉 ========== ALL OBJECTIVES MET! COMPLETING SCENARIO... ==========
```

Followed by:
- ✅ Scenario marked complete in UI
- ✅ Challenge results tracker shows completion
- ✅ Progress saved automatically
- ✅ Can move to next scenario

---

**Quick Start: Hard refresh (Ctrl+F5) → Open Console (F12) → Start Device Naming → Follow instructions!** 🚀

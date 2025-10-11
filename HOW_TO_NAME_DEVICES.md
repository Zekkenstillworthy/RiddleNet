# 🏷️ How to Name Devices in RiddleNet

## 📖 Overview
In RiddleNet's Link Up challenges, devices can be named in **two different ways** depending on the scenario and your needs. This guide shows you both methods!

---

## ✨ Method 1: Pre-Named Devices (Automatic)

### **When This Happens:**
In **Phase 4: Basic Configuration**, specifically the **Device Naming** scenario, devices come pre-configured with professional naming conventions.

### **Example:**
When you start the Device Naming scenario, you'll see:
- **Workstation-01** (PC)
- **Workstation-02** (PC)
- **Core-Switch** (Switch)

### **How It Works:**
```javascript
// Devices are created with names when the scenario starts:
let pc1 = new PC(100, 150, 'Workstation-01');
let pc2 = new PC(100, 300, 'Workstation-02');
let switch1 = new Switch(350, 225, 'Core-Switch');
```

### **What You Learn:**
This scenario teaches you **professional naming conventions**:
- ✅ Descriptive names that indicate function
- ✅ Sequential numbering (Workstation-01, Workstation-02)
- ✅ Role-based names (Core-Switch, Edge-Router)

---

## 🛠️ Method 2: Manual Naming via CLI (Interactive)

### **When to Use This:**
When you want to **rename devices** or **configure hostnames** in any scenario (especially troubleshooting challenges).

### **Steps:**

#### **1. Double-Click the Device**
- **Double-click** any device (PC, Router, or Switch) on the canvas
- A **CLI Configuration Modal** will appear

#### **2. Access the Command Line Interface**
You'll see a terminal-style interface with:
```
Device: [Current Device Name]
CLI> _
```

#### **3. Use the `hostname` Command**
Type the following command and press **Enter**:
```
hostname [YourNewName]
```

### **Example:**
```bash
CLI> hostname NYC-Router-01
✅ Hostname updated to: NYC-Router-01

CLI> hostname Floor2-Switch-A
✅ Hostname updated to: Floor2-Switch-A

CLI> hostname HR-Workstation-01
✅ Hostname updated to: HR-Workstation-01
```

#### **4. Verify the Change**
After setting the hostname, you can verify it with:
```bash
CLI> show running-config
```

This will display the current configuration including:
```
hostname NYC-Router-01
!
[other configuration details...]
```

#### **5. Close the Modal**
Click the **X** button or outside the modal to return to the canvas.

---

## 🎯 Professional Naming Best Practices

### **Good Naming Conventions:**

#### **By Location:**
- `Floor2-Switch-A`
- `BuildingB-Router-01`
- `NYC-DataCenter-Core-01`
- `LA-Office-Switch-Main`

#### **By Function/Role:**
- `Core-Switch`
- `Edge-Router`
- `Distribution-Switch-01`
- `Access-Switch-Floor3`
- `Backbone-Router`

#### **By Department:**
- `HR-Workstation-01`
- `IT-Server-Main`
- `Finance-PC-Desktop`
- `Sales-Laptop-Mobile`

#### **Combined Approach (Best):**
- `NYC-Core-Switch-01` (Location + Role + Number)
- `LA-Edge-Router-02` (Location + Function + Number)
- `Floor3-Access-Switch-A` (Location + Function + Identifier)

### **❌ Avoid These:**
- Generic names: `Switch1`, `Router2`, `Device3`
- Meaningless names: `Thing`, `Test`, `Temp`
- Special characters that break systems: `@`, `#`, `%`, `&`
- Spaces in names: `My Switch` (use hyphens: `My-Switch`)

---

## 🔍 Where Device Names Appear

### **1. On the Canvas:**
The device label appears **below the device icon** in cyan text.

### **2. In the CLI Modal:**
Shows at the top: `Device: [Device Name]`

### **3. In Configuration Output:**
```
hostname Workstation-01
!
```

### **4. In Connection Logs:**
```
✓ pc ↔ switch: Found 1, Need 2
  { from: 'pc', to: 'switch', fromLabel: 'Workstation-01', toLabel: 'Core-Switch' }
```

### **5. In Debug Console:**
Open browser console (F12) to see device names in logs:
```
✅ Devices placed on canvas: [
    { type: 'pc', label: 'Workstation-01' },
    { type: 'pc', label: 'Workstation-02' },
    { type: 'switch', label: 'Core-Switch' }
]
```

---

## 🎓 Learning Objectives

### **Why Device Naming Matters:**

#### **1. Troubleshooting:**
❌ "Switch2 is down" - Which switch? Where is it?
✅ "Floor3-Access-Switch-A is down" - Clear location and function!

#### **2. Documentation:**
Professional network diagrams use clear naming:
```
Internet
   ↓
Border-Router-01
   ↓
Core-Switch-Main ←→ Core-Switch-Backup
   ↓                    ↓
Floor1-Switch-A    Floor2-Switch-A
```

#### **3. Team Communication:**
- Everyone immediately understands what "NYC-Core-Switch-01" refers to
- No confusion during incidents or maintenance
- Faster resolution times

#### **4. Automation & Scripts:**
Scripts can target devices by naming patterns:
```python
# Backup all core switches
for device in devices:
    if 'Core-Switch' in device.hostname:
        backup_config(device)
```

#### **5. Compliance:**
Many industries require standardized naming:
- Healthcare (HIPAA)
- Finance (PCI-DSS)
- Government (NIST)

---

## 🧪 Try It Yourself!

### **Practice Exercise:**

1. **Start any Link Up scenario** (e.g., Small Office Network)
2. **Double-click on a PC**
3. **Type:** `hostname Sales-Laptop-01`
4. **Press Enter**
5. **Type:** `show running-config`
6. **Verify** the hostname appears in the output!

### **Advanced Challenge:**

Rename ALL devices in a scenario with a professional naming scheme:
- **Router:** `Branch-Office-Gateway`
- **Switch:** `Access-Switch-Floor1`
- **PC 1:** `Manager-Workstation`
- **PC 2:** `Employee-Desktop-01`
- **PC 3:** `Employee-Desktop-02`

---

## 🔧 Technical Details

### **Device Class Structure:**
```javascript
class Device {
    constructor(type, x, y, label) {
        this.type = type;      // 'pc', 'router', 'switch'
        this.x = x;            // Canvas X position
        this.y = y;            // Canvas Y position
        this.label = label;    // Device name/hostname
        // ... other properties
    }
}

// Creating devices:
let pc = new PC(100, 150, 'Workstation-01');
// PC inherits from Device, sets type='pc', label='Workstation-01'
```

### **How Naming Works:**
1. **Initial Creation:** Name set when device is created (constructor)
2. **Display:** Canvas draws `this.label` below device icon
3. **CLI Access:** Double-click opens modal showing device name
4. **Hostname Command:** Updates `device.label` property
5. **Validation:** Auto-completion checks device labels for requirements

---

## 📱 Quick Reference Card

| **Action** | **Method** | **Example** |
|------------|------------|-------------|
| **View Current Name** | Look below device icon | `Core-Switch` |
| **Open CLI** | Double-click device | Opens config modal |
| **Change Name** | `hostname [NewName]` | `hostname NYC-Router-01` |
| **Verify Name** | `show running-config` | Shows `hostname NYC-Router-01` |
| **Close Modal** | Click X or outside | Returns to canvas |

---

## 💡 Pro Tips

1. **Consistency is Key:** Use the same naming pattern across your entire network
2. **Keep it Short:** Names should be descriptive but not excessive (max 15-20 characters)
3. **Use Hyphens:** Separate words with hyphens, not spaces or underscores
4. **Add Numbers:** Use sequential numbering for similar devices (01, 02, 03)
5. **Document Your Scheme:** Create a naming convention guide for your team
6. **Plan Ahead:** Design your naming scheme before building the network

---

## 🎯 Common Use Cases

### **Small Office Network:**
```
Internet-Gateway (Router)
Main-Switch (Switch)
Manager-PC (PC 1)
Employee-PC-01 (PC 2)
Employee-PC-02 (PC 3)
```

### **Multi-Floor Building:**
```
Core-Router (Router)
Floor1-Switch (Switch 1)
Floor2-Switch (Switch 2)
Floor1-Workstation-01 (PC 1)
Floor2-Workstation-01 (PC 2)
```

### **Campus Network:**
```
Campus-Core-Router (Router)
Building-A-Switch (Switch 1)
Building-B-Switch (Switch 2)
Admin-Workstation (PC 1)
Lab-PC-01 (PC 2)
Classroom-PC-01 (PC 3)
```

---

## 🏆 Scenario Progression

### **Phase 4: Device Naming** ⭐
**Focus:** Learn professional naming conventions
- Devices come **pre-named** with examples
- **Practice:** Connect devices while observing naming patterns
- **Objective:** Understand how names help identify network components

### **Later Phases** ⭐⭐⭐
**Advanced:** Rename devices using CLI commands
- **Double-click** devices to access CLI
- **Use** `hostname` command to rename
- **Apply** naming conventions to complex topologies

---

## ❓ FAQ

### **Q: Can I rename devices after placing them?**
A: Yes! Double-click any device and use the `hostname` command.

### **Q: Do device names affect scenario completion?**
A: No. Completion is based on device **types** and **connections**, not names.

### **Q: Can I use spaces in device names?**
A: It's not recommended. Use hyphens instead: `My-Switch` not `My Switch`

### **Q: What's the maximum name length?**
A: While there's no hard limit, keep names under 20 characters for readability.

### **Q: Can I reset a device name to default?**
A: Yes, use `hostname [OriginalName]` or refresh the scenario to restart.

---

## 🎓 Real-World Example

Here's how a real network engineer might name devices in a company network:

```
Branch Office Network (New York)

Internet
   ↓
NY-Border-Router-01 (Primary Internet Gateway)
   ↓
NY-Firewall-01 (Security Appliance)
   ↓
NY-Core-Switch-01 ──┬── NY-Dist-Switch-Floor1
                     ├── NY-Dist-Switch-Floor2
                     └── NY-Dist-Switch-Floor3
                            ↓
                    NY-F3-Access-Switch-A ──┬── NY-F3-Sales-PC-01
                                            ├── NY-F3-Sales-PC-02
                                            └── NY-F3-Sales-Printer
```

**Naming Pattern:**
- **Location:** `NY` (New York)
- **Function:** `Core`, `Dist`, `Access`, `Sales`
- **Device Type:** `Router`, `Switch`, `PC`, `Printer`
- **Number/ID:** `01`, `02`, `Floor1`, `A`

---

## 🌟 Summary

**Device naming in RiddleNet:**
1. ✅ **Learn from examples** in the Device Naming scenario (Phase 4)
2. ✅ **Practice manually** using the CLI `hostname` command
3. ✅ **Apply best practices** like location-function-number patterns
4. ✅ **Use professional conventions** that real network admins use
5. ✅ **Make troubleshooting easier** with descriptive, consistent names

**Remember:** Good naming conventions are a sign of a professional network administrator! 🏆

---

## 📚 Related Documentation

- [DEVICE_NAMING_DEBUG_GUIDE.md](DEVICE_NAMING_DEBUG_GUIDE.md) - Troubleshooting the Device Naming scenario
- [LINKUP_CHALLENGE_RESULTS_INTEGRATION.md](LINKUP_CHALLENGE_RESULTS_INTEGRATION.md) - How Challenge Results track your progress
- [CHALLENGE_NAVIGATION_SUMMARY.md](CHALLENGE_NAVIGATION_SUMMARY.md) - Navigating through Link Up phases

---

**Happy Networking! 🌐✨**

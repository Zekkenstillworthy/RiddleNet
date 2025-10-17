# 🚀 VLAN Setup Basics - Quick Start Guide

## ✅ Challenge is READY TO PLAY!

---

## 🎯 Mission
Configure VLANs on a switch to separate Sales and Engineering departments.

---

## 📍 How to Start

1. **Open RiddleNet**
2. Go to **Challenges** (gamepad icon in sidebar)
3. Click **Novice Scenarios**
4. Select **🏷️ VLAN Setup Basics**
5. Click on **Switch 1** to open its CLI

---

## ⚡ Quick Solution (Step-by-Step)

### **Enter Config Mode:**
```
enable
configure terminal
```

### **Create VLANs:**
```
vlan 10
name Sales
exit

vlan 20
name Engineering
exit
```

### **Configure Sales Ports (VLAN 10):**
```
interface Fa0/1
switchport mode access
switchport access vlan 10
exit

interface Fa0/2
switchport mode access
switchport access vlan 10
exit
```

### **Configure Engineering Ports (VLAN 20):**
```
interface Fa0/3
switchport mode access
switchport access vlan 20
exit

interface Fa0/4
switchport mode access
switchport access vlan 20
exit
```

### **Verify Your Work:**
```
show vlan brief
```

**You should see:**
```
VLAN ID | Name          | Ports
--------|---------------|------------------
10      | Sales         | Fa0/1, Fa0/2
20      | Engineering   | Fa0/3, Fa0/4
```

### **Submit:**
Click the **SUBMIT** button! ✅

---

## 💡 Key Concepts

- **VLAN 10** = Sales Department (192.168.10.x network)
- **VLAN 20** = Engineering Department (192.168.20.x network)
- **Fa0/1 & Fa0/2** = Connected to Sales PCs
- **Fa0/3 & Fa0/4** = Connected to Engineering PCs

---

## 🎓 What You're Learning

1. How to create VLANs
2. How to name VLANs for organization
3. How to configure switch ports in access mode
4. How to assign ports to specific VLANs
5. How to verify VLAN configuration
6. Why VLANs isolate traffic between departments

---

## ❓ Need Help?

### **Available Commands:**
- `help` - Show all commands
- `show vlan brief` - See VLAN configuration
- `show interface Fa0/X` - Check specific port

### **Common Issues:**

**❌ "Unknown command" error:**
- Make sure you're in the right mode (`configure terminal` first)

**❌ "VLAN does not exist" error:**
- Create the VLAN before assigning ports to it

**❌ Submit fails:**
- Double-check all 4 ports are configured
- Verify all ports are in access mode
- Make sure VLANs 10 and 20 exist

---

## 🏆 Success Criteria

To pass, you must:
- ✅ Create VLAN 10 (Sales)
- ✅ Create VLAN 20 (Engineering)
- ✅ Set Fa0/1 to access mode, VLAN 10
- ✅ Set Fa0/2 to access mode, VLAN 10
- ✅ Set Fa0/3 to access mode, VLAN 20
- ✅ Set Fa0/4 to access mode, VLAN 20

---

## 🎉 Rewards

- **XP:** 25 points
- **Badge:** VLAN Basics (if enabled)
- **Unlock:** Progress toward Intermediate challenges

---

## 📚 More Info

See `VLAN_BASICS_CHALLENGE_COMPLETE.md` for:
- Detailed explanations
- Troubleshooting guide
- Command reference
- Technical implementation details

---

**Ready? Let's configure those VLANs! 🚀**

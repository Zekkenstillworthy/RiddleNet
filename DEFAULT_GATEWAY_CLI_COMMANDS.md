# 🌐 Default Gateway Configuration - Complete CLI Guide

## ✅ What Was Fixed

The challenge was showing **0% Match Percentage** because:
1. Backend expected `scenario_id: 'default-gateway'` but frontend sent `'default-gateway-setup'`
2. No validation function existed for Default Gateway challenge
3. Backend assumed 100% match without actually checking configuration

**All fixed!** Now the backend:
- Accepts both `'default-gateway'` and `'default-gateway-setup'`
- Validates router IP configuration (30 points)
- Validates router interface status (20 points)
- Validates each PC configuration (50 points total)

---

## 📋 Complete CLI Commands

### **Step 1: Configure Gateway Router**

Click on **Gateway Router** and type:

```cisco
enable
configure terminal
interface GigabitEthernet0/0
ip address 192.168.1.1 255.255.255.0
no shutdown
exit
exit
```

**Verify:**
```cisco
show ip interface brief
show running-config
```

---

### **Step 2: Configure PC-1**

Click on **PC-1** and type:

```bash
ip 192.168.1.10 255.255.255.0 192.168.1.1
```

**Verify:**
```bash
ipconfig
```

---

### **Step 3: Configure PC-2**

Click on **PC-2** and type:

```bash
ip 192.168.1.11 255.255.255.0 192.168.1.1
```

**Verify:**
```bash
ipconfig
```

---

### **Step 4: Configure PC-3**

Click on **PC-3** and type:

```bash
ip 192.168.1.12 255.255.255.0 192.168.1.1
```

**Verify:**
```bash
ipconfig
```

---

## 🎯 Validation Criteria (Backend Scoring)

| Component | Points | Requirement |
|-----------|--------|-------------|
| Router IP | 30 | IP: `192.168.1.1/24` on GigabitEthernet0/0 |
| Router Status | 20 | Interface must be `up` (no shutdown) |
| PC Configuration | 50 | All 3 PCs with correct IP/subnet/gateway |

**Total: 100 points**

---

## 🔍 Validation Logic

The backend now performs these checks:

### Router Validation:
- ✅ Router labeled "Gateway Router" exists
- ✅ GigabitEthernet0/0 has IP `192.168.1.1`
- ✅ Subnet mask is `255.255.255.0`
- ✅ Interface status is `up`

### PC Validation (for each PC):
- ✅ IP address in `192.168.1.0/24` subnet
- ✅ Subnet mask is `255.255.255.0`
- ✅ Default gateway is `192.168.1.1`

---

## 🎮 Quick Copy-Paste Commands

**Gateway Router (all at once):**
```
enable
configure terminal
interface GigabitEthernet0/0
ip address 192.168.1.1 255.255.255.0
no shutdown
exit
exit
```

**PC-1:**
```
ip 192.168.1.10 255.255.255.0 192.168.1.1
```

**PC-2:**
```
ip 192.168.1.11 255.255.255.0 192.168.1.1
```

**PC-3:**
```
ip 192.168.1.12 255.255.255.0 192.168.1.1
```

---

## 🐛 Troubleshooting

### Issue: Still showing 0%
**Solution:** Clear browser cache (Ctrl+Shift+Del) and refresh the page

### Issue: "Unknown command"
**Solution:** Make sure you're clicking on the correct device before typing commands

### Issue: Router commands not working
**Solution:** Type commands in this exact order:
1. `enable` first
2. `configure terminal` second
3. Then `interface` command

### Issue: PC configuration not saving
**Solution:** Use exact format: `ip <address> <subnet> <gateway>` with actual values, not placeholders

---

## 📊 Expected Results

After configuration, clicking **Submit** should show:

```
✅ Router IP configured: 192.168.1.1/24 (+30 points)
✅ Router interface is up (+20 points)
✅ 3/3 PCs configured (+50 points)
📊 Final score: 100/100
```

**Match Percentage: 100%** ✨

---

## 💡 Tips

1. **Use `help` or `?`** in the CLI to see available commands for each device
2. **Router commands** require entering config modes in sequence
3. **PC commands** can be typed directly (no modes)
4. **All values must be exact** - the backend validates specific IPs
5. **Clear cache** if changes don't appear to work

---

## 🔗 Related Files

- Frontend validation: `templates/user/troubleshoot.html` (function `checkDefaultGatewaySetup`)
- Backend validation: `user/controllers/troubleshooting_controller.py` (function `_validate_default_gateway`)
- CLI handlers: `templates/user/troubleshoot.html` (function `handleCliCommandForDefaultGateway`)

---

**Last Updated:** October 12, 2025  
**Status:** ✅ Fully Functional with Backend Validation

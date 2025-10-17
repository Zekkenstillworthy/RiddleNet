# 🧪 CLI Terminal Test Guide

## Quick Test: Default Gateway Configuration

### Step 1: Start the Challenge
1. Run application: `python run.py`
2. Navigate to **Link Up!** → **Novice Level**
3. Click **🌐 Default Gateway Configuration**

### Step 2: Test Router CLI
Click on the **Gateway Router** device, then in the CLI terminal type:

```bash
enable
```
**Expected:** Should NOT show "Unknown command". Should enter privileged mode.

```bash
configure terminal
```
**Expected:** "Enter configuration commands, one per line. End with CNTL/Z.\nRouter(config)# "

```bash
show ip interface brief
```
**Expected:** Display router interfaces with IP addresses

```bash
?
```
**Expected:** Show help menu with available commands

### Step 3: Test PC CLI
Click on **PC-1** device, then type:

```bash
ipconfig
```
**Expected:** Display current IP configuration (IP, Subnet, Gateway)

```bash
set gateway 192.168.1.1
```
**Expected:** "Default gateway set to: 192.168.1.1"

```bash
ipconfig
```
**Expected:** Gateway should now show 192.168.1.1

### Step 4: Test with Simplified Command
```bash
ip 192.168.1.10 255.255.255.0 192.168.1.1
```
**Expected:** "IP configuration updated:\n  Address: 192.168.1.10\n  Subnet: 255.255.255.0\n  Gateway: 192.168.1.1"

---

## Quick Test: DHCP Client Configuration

### Step 1: Start the Challenge
1. Navigate to **Link Up!** → **Novice Level**
2. Click **🔄 DHCP Client Configuration**

### Step 2: Configure DHCP on Router
Click on **DHCP Server** router, then type:

```bash
enable
configure terminal
interface GigabitEthernet0/0
ip address 192.168.1.1 255.255.255.0
no shutdown
exit
ip dhcp pool LAN_POOL
network 192.168.1.0 255.255.255.0
default-router 192.168.1.1
dns-server 8.8.8.8 8.8.4.4
exit
ip dhcp excluded-address 192.168.1.1 192.168.1.99
exit
show ip dhcp pool
```

**Expected:** Should see DHCP pool configuration displayed

### Step 3: Test PC DHCP Client
Click on any **PC** device, then type:

```bash
ipconfig
```
**Expected:** Should show APIPA address (169.254.x.x)

```bash
ipconfig /release
```
**Expected:** "IP address released. Address: 0.0.0.0"

```bash
ipconfig /renew
```
**Expected:** Should obtain IP from DHCP pool (192.168.1.100-200 range)

```bash
ipconfig /all
```
**Expected:** Should show:
- IP Address: 192.168.1.1xx
- Subnet: 255.255.255.0
- Gateway: 192.168.1.1
- DNS: 8.8.8.8, 8.8.4.4
- DHCP Enabled: Yes

---

## 🎯 Success Criteria

### Default Gateway Challenge
- ✅ Router accepts `enable` command
- ✅ Router accepts `configure terminal`
- ✅ PC accepts `ipconfig` command
- ✅ PC accepts `set gateway` command
- ✅ PC accepts `ip <addr> <subnet> <gateway>` command
- ✅ Help command (`?`) works on both devices
- ✅ No "Unknown command" errors

### DHCP Challenge
- ✅ Router accepts all DHCP configuration commands
- ✅ `show ip dhcp pool` displays configuration
- ✅ PC accepts `ipconfig /release`
- ✅ PC accepts `ipconfig /renew`
- ✅ PC obtains IP in 192.168.1.100-200 range
- ✅ PC shows DHCP details with `ipconfig /all`
- ✅ No "Unknown command" errors

---

## 🐛 Common Issues

### Issue: Still seeing "Unknown command"
**Fix:** Clear browser cache (Ctrl+Shift+Delete), refresh page (Ctrl+F5)

### Issue: Commands not responding
**Fix:** Make sure device is clicked/selected (should see device name in terminal header)

### Issue: DHCP not assigning IPs
**Fix:** Make sure router DHCP pool is fully configured with `network` command

### Issue: Terminal not visible
**Fix:** Click on a device to open its configuration panel

---

## 📋 Quick Command Reference

### Router Commands
```bash
enable                              # Enter privileged mode
configure terminal                  # Enter global config
interface GigabitEthernet0/0        # Enter interface config
ip address 192.168.1.1 255.255.255.0  # Configure IP
no shutdown                         # Enable interface
show ip interface brief             # Show interfaces
show running-config                 # Show config
?                                   # Help
```

### PC Commands (Default Gateway)
```bash
ipconfig                            # Show IP config
ip 192.168.1.10 255.255.255.0 192.168.1.1  # Set all
set gateway 192.168.1.1             # Set gateway only
?                                   # Help
```

### PC Commands (DHCP)
```bash
ipconfig                            # Show config
ipconfig /all                       # Show detailed config
ipconfig /release                   # Release DHCP lease
ipconfig /renew                     # Request DHCP lease
sudo dhclient eth0                  # Linux DHCP request
?                                   # Help
```

---

*Last Updated: October 12, 2025*

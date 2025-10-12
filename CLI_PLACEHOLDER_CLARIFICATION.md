# 🚨 CLI Command Clarification Guide

## ⚠️ Important: Placeholders vs Actual Values

### ❌ **WRONG - Don't Type the Placeholders!**
```bash
ip address <ip> <mask>           # ❌ This is DOCUMENTATION syntax
network <ip> <mask>              # ❌ Don't type the angle brackets!
default-router <ip>              # ❌ These are PLACEHOLDERS
```

### ✅ **CORRECT - Use Actual Values!**
```bash
ip address 192.168.1.1 255.255.255.0      # ✅ Actual IP and mask
network 192.168.1.0 255.255.255.0         # ✅ Real network address
default-router 192.168.1.1                # ✅ Real gateway IP
```

---

## 🎯 Challenge-Specific Commands

### 🌐 **Default Gateway Configuration Challenge**

This challenge does **NOT** use DHCP commands!

#### ✅ Available Commands:
```bash
# Router Configuration
enable
configure terminal
interface GigabitEthernet0/0
ip address 192.168.1.1 255.255.255.0      # ← Use actual IPs!
no shutdown
show ip interface brief
show running-config
exit
```

#### ❌ NOT Available in This Challenge:
```bash
ip dhcp pool <name>              # ❌ DHCP commands don't work here!
network <ip> <mask>              # ❌ Only in DHCP challenge
default-router <ip>              # ❌ Only in DHCP challenge
dns-server <ip>                  # ❌ Only in DHCP challenge
```

---

### 🔄 **DHCP Client Configuration Challenge**

This challenge **DOES** use DHCP commands!

#### ✅ Available DHCP Commands:
```bash
# First configure interface
enable
configure terminal
interface GigabitEthernet0/0
ip address 192.168.1.1 255.255.255.0
no shutdown
exit

# Then configure DHCP pool
ip dhcp pool LAN_POOL                    # ← Use actual pool name!
network 192.168.1.0 255.255.255.0        # ← Use actual network!
default-router 192.168.1.1               # ← Use actual gateway!
dns-server 8.8.8.8 8.8.4.4               # ← Use actual DNS servers!
exit

# Exclude router IP
ip dhcp excluded-address 192.168.1.1 192.168.1.99
exit

# Verify
show ip dhcp pool
show ip dhcp binding
```

---

## 📝 Correct Usage Examples

### Example 1: Configure Router Interface (Both Challenges)

#### ❌ WRONG:
```bash
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address <ip> <mask>    # ← Wrong! Don't type <ip> <mask>
```

#### ✅ CORRECT:
```bash
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.0    # ← Real values!
```

---

### Example 2: Configure DHCP Pool (DHCP Challenge ONLY)

#### ❌ WRONG:
```bash
Router(config)# ip dhcp pool <name>          # ← Don't type <name>
Router(dhcp-config)# network <ip> <mask>     # ← Don't type <ip> <mask>
```

#### ✅ CORRECT:
```bash
Router(config)# ip dhcp pool LAN_POOL        # ← Actual pool name
Router(dhcp-config)# network 192.168.1.0 255.255.255.0    # ← Real network
Router(dhcp-config)# default-router 192.168.1.1           # ← Real gateway
Router(dhcp-config)# dns-server 8.8.8.8 8.8.4.4          # ← Real DNS
```

---

## 🔧 Complete Working Example

### For Default Gateway Configuration Challenge:

```bash
# Step 1: Select the challenge
Link Up! → Novice Level → 🌐 Default Gateway Configuration

# Step 2: Click on "Gateway Router" device

# Step 3: Type these commands (Router already configured):
enable
show ip interface brief
show running-config

# Step 4: Click on "PC-1" device

# Step 5: Configure PC:
set gateway 192.168.1.1

# OR use full command:
ip 192.168.1.10 255.255.255.0 192.168.1.1

# Step 6: Verify:
ipconfig

# Step 7: Repeat for PC-2 and PC-3
```

---

### For DHCP Client Configuration Challenge:

```bash
# Step 1: Select the challenge
Link Up! → Novice Level → 🔄 DHCP Client Configuration

# Step 2: Click on "DHCP Server" router

# Step 3: Configure DHCP server:
enable
configure terminal
interface GigabitEthernet0/0
ip address 192.168.1.1 255.255.255.0
no shutdown
exit

# Create DHCP pool (ACTUAL VALUES, NOT PLACEHOLDERS!)
ip dhcp pool LAN_POOL
network 192.168.1.0 255.255.255.0
default-router 192.168.1.1
dns-server 8.8.8.8 8.8.4.4
exit

# Exclude router IP
ip dhcp excluded-address 192.168.1.1 192.168.1.99
exit

# Verify DHCP configuration
show ip dhcp pool

# Step 4: Click on any PC device

# Step 5: Request DHCP IP:
ipconfig /release
ipconfig /renew

# Step 6: Verify:
ipconfig /all

# Should show IP in range 192.168.1.100-192.168.1.199
```

---

## 🎯 Quick Reference Card

### Documentation Syntax → What You Type

| Documentation Says | What You Type |
|-------------------|---------------|
| `ip address <ip> <mask>` | `ip address 192.168.1.1 255.255.255.0` |
| `interface Gi<slot>/<port>` | `interface GigabitEthernet0/0` |
| `ip dhcp pool <name>` | `ip dhcp pool LAN_POOL` |
| `network <network> <mask>` | `network 192.168.1.0 255.255.255.0` |
| `default-router <gateway>` | `default-router 192.168.1.1` |
| `dns-server <ip> [<ip2>]` | `dns-server 8.8.8.8 8.8.4.4` |
| `excluded-address <start> <end>` | `ip dhcp excluded-address 192.168.1.1 192.168.1.99` |

---

## 🚨 Common Mistakes

### Mistake 1: Typing Placeholders
```bash
❌ ip address <ip> <mask>
✅ ip address 192.168.1.1 255.255.255.0
```

### Mistake 2: Using DHCP Commands in Wrong Challenge
```bash
❌ In "Default Gateway Configuration" challenge:
   ip dhcp pool LAN_POOL          # Won't work!

✅ Use DHCP commands ONLY in "DHCP Client Configuration" challenge
```

### Mistake 3: Missing "ip" in DHCP Excluded Command
```bash
❌ dhcp excluded-address 192.168.1.1 192.168.1.99
✅ ip dhcp excluded-address 192.168.1.1 192.168.1.99
```

### Mistake 4: Wrong Interface Name Format
```bash
❌ interface Gi0/0                 # Too short
✅ interface GigabitEthernet0/0    # Full name
```

---

## 💡 Pro Tips

1. **Type `?` or `help`** in any mode to see available commands for that specific challenge
2. **Check which challenge you're in** - DHCP commands only work in DHCP challenge
3. **Placeholders are documentation** - Always replace `<something>` with actual values
4. **IP addresses need dots** - 192.168.1.1, not 192168011
5. **Subnet masks are long** - 255.255.255.0, not /24

---

## 📞 Help Commands

```bash
?                    # Show available commands
help                 # Show available commands
show ?               # Show all "show" commands (if supported)
```

---

## ✅ Testing Your Understanding

### Quiz: Which command is correct?

1. ❓ `ip address <192.168.1.1> <255.255.255.0>`
2. ❓ `ip address 192.168.1.1 255.255.255.0`
3. ❓ `ipaddress 192.168.1.1 255.255.255.0`

**Answer:** #2 is correct! ✅

---

*Remember: `<placeholder>` means "replace this with your actual value"*

*CLI Command Clarification Guide - October 12, 2025*

# 🎯 Quick Reference: Challenge Completion Commands

## 🌐 Default Gateway Configuration

### Scenario Setup
- **Router:** Gateway Router (192.168.1.1/24)
- **Switch:** LAN Switch
- **PCs:** 3 PCs need gateway configuration

### Solution Steps

#### 1. Router Configuration (Already Configured)
```bash
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
```

#### 2. PC Configuration (What You Need to Do)

**PC-1:**
```bash
# Windows
netsh interface ip set address "Ethernet" static 192.168.1.10 255.255.255.0 192.168.1.1

# Linux
sudo ifconfig eth0 192.168.1.10 netmask 255.255.255.0
sudo route add default gw 192.168.1.1
```

**PC-2:**
```bash
# Windows
netsh interface ip set address "Ethernet" static 192.168.1.11 255.255.255.0 192.168.1.1

# Linux
sudo ifconfig eth0 192.168.1.11 netmask 255.255.255.0
sudo route add default gw 192.168.1.1
```

**PC-3:**
```bash
# Windows
netsh interface ip set address "Ethernet" static 192.168.1.12 255.255.255.0 192.168.1.1

# Linux
sudo ifconfig eth0 192.168.1.12 netmask 255.255.255.0
sudo route add default gw 192.168.1.1
```

#### 3. Verification
```bash
# Test gateway connectivity
ping 192.168.1.1

# Check routing table (Windows)
route print

# Check routing table (Linux)
ip route show
netstat -rn
```

---

## 🔄 DHCP Client Configuration

### Scenario Setup
- **Router:** DHCP Server (192.168.1.1/24)
- **Switch:** LAN Switch  
- **PCs:** 3 PCs with APIPA addresses (169.254.x.x)

### Solution Steps

#### 1. Router DHCP Configuration
```bash
Router> enable
Router# configure terminal

# Configure interface
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

# Create DHCP pool
Router(config)# ip dhcp pool LAN_POOL
Router(dhcp-config)# network 192.168.1.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.1.1
Router(dhcp-config)# dns-server 8.8.8.8 8.8.4.4
Router(dhcp-config)# exit

# Exclude router IP
Router(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.99
Router(config)# exit
Router# write memory
```

#### 2. PC Configuration (Enable DHCP)

**Windows:**
```bash
# Release current IP
ipconfig /release

# Request new IP from DHCP
ipconfig /renew

# Verify DHCP lease
ipconfig /all
```

**Linux:**
```bash
# Request DHCP address
sudo dhclient eth0

# OR using dhcpcd
sudo dhcpcd eth0

# Verify configuration
ifconfig eth0
ip addr show eth0
```

#### 3. Verification
```bash
# Verify DHCP on Router
Router# show ip dhcp pool
Router# show ip dhcp binding
Router# show ip dhcp server statistics

# Verify on PC (Windows)
ipconfig /all
# Look for:
# - DHCP Enabled: Yes
# - IP Address: 192.168.1.100-200
# - Default Gateway: 192.168.1.1
# - DNS Server: 8.8.8.8

# Verify on PC (Linux)
cat /var/lib/dhcp/dhclient.leases
```

---

## 🏷️ VLAN Basics Setup

### Scenario Setup
- **Switch:** 1 Switch
- **VLAN 10:** Sales Department (2 PCs)
- **VLAN 20:** Engineering Department (2 PCs)

### Solution Steps

#### 1. Create VLANs
```bash
Switch> enable
Switch# configure terminal

# Create VLAN 10
Switch(config)# vlan 10
Switch(config-vlan)# name Sales
Switch(config-vlan)# exit

# Create VLAN 20
Switch(config)# vlan 20
Switch(config-vlan)# name Engineering
Switch(config-vlan)# exit
```

#### 2. Assign Ports to VLANs
```bash
# Sales ports (Fa0/1-2)
Switch(config)# interface range FastEthernet0/1-2
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 10
Switch(config-if-range)# exit

# Engineering ports (Fa0/3-4)
Switch(config)# interface range FastEthernet0/3-4
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 20
Switch(config-if-range)# exit

Switch(config)# exit
Switch# write memory
```

#### 3. Configure PC IP Addresses
```bash
# Sales PCs (VLAN 10)
Sales-PC1: 192.168.10.10/24
Sales-PC2: 192.168.10.11/24

# Engineering PCs (VLAN 20)
Eng-PC1: 192.168.20.10/24
Eng-PC2: 192.168.20.11/24
```

#### 4. Verification
```bash
# Verify VLANs
Switch# show vlan brief
Switch# show vlan id 10
Switch# show vlan id 20

# Verify port assignments
Switch# show interfaces FastEthernet0/1 switchport
Switch# show interfaces switchport

# Test connectivity
# PCs in same VLAN should ping successfully
# PCs in different VLANs should NOT ping (expected)
```

---

## 🔧 Common Verification Commands

### Router
```bash
show ip interface brief          # Interface status & IPs
show ip route                    # Routing table
show running-config              # Current configuration
show ip dhcp pool                # DHCP pool info
show ip dhcp binding             # DHCP leases
show interfaces                  # Detailed interface info
```

### Switch
```bash
show vlan brief                  # VLAN summary
show interfaces trunk            # Trunk ports
show mac address-table           # MAC address table
show spanning-tree              # STP status
show interfaces status          # Port status
show running-config             # Current configuration
```

### PC (Windows)
```bash
ipconfig                        # Basic IP info
ipconfig /all                   # Detailed IP info
ipconfig /release               # Release DHCP lease
ipconfig /renew                 # Renew DHCP lease
ping <ip>                       # Test connectivity
tracert <ip>                    # Trace route
route print                     # Routing table
netstat -rn                     # Routing table (alternative)
```

### PC (Linux)
```bash
ifconfig                        # Interface info (deprecated)
ip addr show                    # Interface info
ip route show                   # Routing table
ping <ip>                       # Test connectivity
traceroute <ip>                 # Trace route
sudo dhclient eth0              # Request DHCP
netstat -rn                     # Routing table
```

---

## 🎯 Troubleshooting Tips

### Default Gateway Issues
```bash
# Problem: Can't reach outside network
# Check: Default gateway configured?
route print  # Windows
ip route show  # Linux

# Should see: 0.0.0.0/0 via 192.168.1.1

# Fix: Add default gateway
route add 0.0.0.0 mask 0.0.0.0 192.168.1.1  # Windows
sudo ip route add default via 192.168.1.1   # Linux
```

### DHCP Not Working
```bash
# Problem: PC has 169.254.x.x address (APIPA)
# Check: DHCP server running?
Router# show ip dhcp pool
Router# show ip dhcp binding

# Check: PC DHCP client enabled?
ipconfig /all  # Should show "DHCP Enabled: Yes"

# Fix: Renew DHCP
ipconfig /release
ipconfig /renew
```

### VLAN Connectivity Issues
```bash
# Problem: PCs in same VLAN can't communicate
# Check: Port VLAN assignment
Switch# show vlan brief
Switch# show interfaces Fa0/1 switchport

# Check: Port status
Switch# show interfaces status

# Fix: Verify port in correct VLAN
Switch(config)# interface Fa0/1
Switch(config-if)# switchport access vlan 10
```

---

## 📊 Success Criteria

### Default Gateway Challenge
- [x] All PCs have IP addresses in 192.168.1.0/24
- [x] All PCs have subnet mask 255.255.255.0
- [x] All PCs have default gateway 192.168.1.1
- [x] PCs can ping gateway (192.168.1.1)
- [x] PCs can ping each other

### DHCP Challenge
- [x] Router has DHCP pool configured
- [x] Router interface has IP 192.168.1.1
- [x] PCs obtain IPs in range 192.168.1.100-200
- [x] PCs have gateway 192.168.1.1
- [x] PCs have DNS server 8.8.8.8
- [x] PCs can communicate with each other

### VLAN Challenge
- [x] VLAN 10 (Sales) created
- [x] VLAN 20 (Engineering) created
- [x] Ports Fa0/1-2 in VLAN 10
- [x] Ports Fa0/3-4 in VLAN 20
- [x] Sales PCs have IPs in 192.168.10.0/24
- [x] Engineering PCs have IPs in 192.168.20.0/24
- [x] PCs in same VLAN can communicate
- [x] PCs in different VLANs cannot communicate

---

## 🚀 Quick Start

1. **Select Challenge** from Link Up! menu
2. **Read the Scenario** description
3. **Click Hints** (💡) if you need help
4. **Configure Devices** using CLI or GUI
5. **Test Configuration** with ping/verification commands
6. **Submit Solution** when ready
7. **Review Feedback** and adjust if needed

---

## 📖 Full Documentation

See `COMPLETE_CHALLENGE_GUIDE.md` for:
- ✅ All difficulty levels (Foundation, Novice, Intermediate, Advanced)
- ✅ All challenges with detailed steps
- ✅ Complete CLI command reference
- ✅ Troubleshooting guides
- ✅ Network topology diagrams

---

*Quick Reference Card - October 2025*

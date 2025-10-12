# 🎯 RiddleNet Complete Challenge Guide

## Table of Contents
- [Foundation Learning](#foundation-learning)
- [Novice Level (Easy)](#novice-level-easy)
- [Intermediate Level (Medium)](#intermediate-level-medium)
- [Advanced Level (Hard)](#advanced-level-hard)
- [CLI Commands Reference](#cli-commands-reference)

---

## 🌱 Foundation Learning

### Phase 1: Device Discovery & Basic Connections
**Objective:** Learn to identify and place network devices

**Steps to Complete:**
1. **Drag and Drop Devices**
   - Locate the device palette on the left side
   - Drag a PC onto the canvas
   - Drag a Switch onto the canvas
   - Drag a Router onto the canvas

2. **What You'll Learn:**
   - Difference between PCs, Switches, and Routers
   - How to place devices on the network topology

**CLI Commands:**
```bash
# Not applicable for this phase (GUI-based)
```

---

### Phase 2: Creating Wired Connections
**Objective:** Connect devices using ethernet cables

**Steps to Complete:**
1. Click the "Wired Connection" button (cable icon)
2. Click on the first device (e.g., PC)
3. Click on the second device (e.g., Switch)
4. Connection line appears between devices
5. Create at least 2-3 connections

**What You'll Learn:**
- How to create physical connections
- Understanding ethernet cables
- Point-to-point connections

**CLI Commands:**
```bash
# On a Cisco device, verify physical connections:
Router> show interfaces
Router> show ip interface brief
```

---

### Phase 3: IP Address Configuration
**Objective:** Assign IP addresses to network devices

**Steps to Complete:**
1. Click on a PC device to select it
2. In the properties panel (right side), enter:
   - **IP Address:** `192.168.1.10`
   - **Subnet Mask:** `255.255.255.0`
3. Configure multiple PCs with different IP addresses:
   - PC-1: `192.168.1.10/24`
   - PC-2: `192.168.1.11/24`
   - PC-3: `192.168.1.12/24`

**What You'll Learn:**
- IP addressing basics
- Subnet masks
- Network addressing scheme

**CLI Commands:**
```bash
# Windows PC
ipconfig
ipconfig /all

# Configure IP on Windows:
netsh interface ip set address "Ethernet" static 192.168.1.10 255.255.255.0 192.168.1.1

# Linux PC
ifconfig
ip addr show

# Configure IP on Linux:
sudo ifconfig eth0 192.168.1.10 netmask 255.255.255.0
# OR using ip command:
sudo ip addr add 192.168.1.10/24 dev eth0
```

---

### Phase 4: Testing Connectivity
**Objective:** Verify network connectivity using ping

**Steps to Complete:**
1. Select a PC device
2. Click the "Ping" button
3. Enter the destination IP address (e.g., `192.168.1.11`)
4. Observe ping results
5. Test connectivity between multiple devices

**What You'll Learn:**
- ICMP protocol
- Network troubleshooting basics
- Verifying connectivity

**CLI Commands:**
```bash
# Ping a device (Windows/Linux)
ping 192.168.1.11
ping -c 4 192.168.1.11  # Linux (4 packets)
ping -n 4 192.168.1.11  # Windows (4 packets)

# Continuous ping (Windows)
ping -t 192.168.1.11

# Traceroute
tracert 192.168.1.11   # Windows
traceroute 192.168.1.11  # Linux
```

---

### Phase 5: Building Your First Network
**Objective:** Create a complete small network

**Steps to Complete:**
1. **Place Devices:**
   - 1 Router (center)
   - 1 Switch (connected to router)
   - 3 PCs (connected to switch)

2. **Connect Everything:**
   - Router ↔ Switch
   - Switch ↔ PC-1
   - Switch ↔ PC-2
   - Switch ↔ PC-3

3. **Configure IP Addresses:**
   - Router: `192.168.1.1/24`
   - PC-1: `192.168.1.10/24`
   - PC-2: `192.168.1.11/24`
   - PC-3: `192.168.1.12/24`

4. **Set Default Gateway on PCs:** `192.168.1.1`

5. **Test Connectivity:**
   - Ping from PC-1 to PC-2
   - Ping from PC-1 to Router
   - Ping from PC-2 to PC-3

**What You'll Learn:**
- Complete network topology
- Star topology design
- Default gateway concept

**CLI Commands:**
```bash
# Configure Router Interface
Router> enable
Router# configure terminal
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit
Router(config)# exit

# Verify Router Configuration
Router# show ip interface brief
Router# show running-config

# Configure PC Default Gateway (Windows)
netsh interface ip set address "Ethernet" static 192.168.1.10 255.255.255.0 192.168.1.1

# Configure PC Default Gateway (Linux)
sudo route add default gw 192.168.1.1
# OR
sudo ip route add default via 192.168.1.1
```

---

## 🎓 Novice Level (Easy)

### Challenge 1: VLAN Basics Setup
**Difficulty:** Easy | **ID:** `vlan-basics`

**Objective:** Configure VLANs 10 (Sales) and 20 (Engineering) on the switch

**Scenario:**
- 1 Switch
- 2 Sales PCs (VLAN 10)
- 2 Engineering PCs (VLAN 20)

**Steps to Complete:**
1. **Create VLANs on Switch:**
   - VLAN 10 - Sales Department
   - VLAN 20 - Engineering Department

2. **Assign Ports to VLANs:**
   - Ports Fa0/1-2: VLAN 10 (Sales)
   - Ports Fa0/3-4: VLAN 20 (Engineering)

3. **Configure IP Addresses:**
   - Sales-PC1: `192.168.10.10/24`
   - Sales-PC2: `192.168.10.11/24`
   - Eng-PC1: `192.168.20.10/24`
   - Eng-PC2: `192.168.20.11/24`

4. **Verify:**
   - PCs in same VLAN can communicate
   - PCs in different VLANs cannot communicate (without Layer 3)

**CLI Commands:**
```bash
# Switch Configuration
Switch> enable
Switch# configure terminal

# Create VLANs
Switch(config)# vlan 10
Switch(config-vlan)# name Sales
Switch(config-vlan)# exit

Switch(config)# vlan 20
Switch(config-vlan)# name Engineering
Switch(config-vlan)# exit

# Assign Ports to VLAN 10 (Sales)
Switch(config)# interface range FastEthernet0/1-2
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 10
Switch(config-if-range)# exit

# Assign Ports to VLAN 20 (Engineering)
Switch(config)# interface range FastEthernet0/3-4
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 20
Switch(config-if-range)# exit

# Verify Configuration
Switch# show vlan brief
Switch# show vlan id 10
Switch# show vlan id 20
Switch# show interfaces switchport
```

**Clues:**
- 💡 VLANs segment broadcast domains logically without physical separation
- 🏷️ Use "switchport mode access" then "switchport access vlan <number>"
- 📊 Verify VLANs with "show vlan brief" command
- 🔒 Devices in different VLANs cannot communicate without a Layer 3 device

---

### Challenge 2: Default Gateway Configuration
**Difficulty:** Easy | **ID:** `default-gateway-setup`

**Objective:** Configure PCs with proper default gateway for internet access

**Scenario:**
- 1 Gateway Router (`192.168.1.1/24`)
- 1 LAN Switch
- 3 PCs (need gateway configuration)

**Steps to Complete:**
1. **Router Configuration:**
   - Internal Interface: `192.168.1.1/24`
   - External Interface (WAN): `203.0.113.1/30`

2. **PC Configuration:**
   - PC-1: `192.168.1.10/24`, Gateway: `192.168.1.1`
   - PC-2: `192.168.1.11/24`, Gateway: `192.168.1.1`
   - PC-3: `192.168.1.12/24`, Gateway: `192.168.1.1`

3. **Verify Connectivity:**
   - Ping gateway from each PC
   - Test internet connectivity (if simulated)

**CLI Commands:**
```bash
# Router Configuration
Router> enable
Router# configure terminal

# Configure LAN Interface
Router(config)# interface GigabitEthernet0/0
Router(config-if)# description LAN Interface
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

# Configure WAN Interface
Router(config)# interface GigabitEthernet0/1
Router(config-if)# description WAN Interface
Router(config-if)# ip address 203.0.113.1 255.255.255.252
Router(config-if)# no shutdown
Router(config-if)# exit

# Enable IP Routing
Router(config)# ip routing
Router(config)# exit

# Verify Router Configuration
Router# show ip interface brief
Router# show ip route

# PC Configuration (Windows)
ipconfig
netsh interface ip set address "Ethernet" static 192.168.1.10 255.255.255.0 192.168.1.1

# PC Configuration (Linux)
sudo ifconfig eth0 192.168.1.10 netmask 255.255.255.0
sudo route add default gw 192.168.1.1

# Verify Gateway
ping 192.168.1.1
tracert 8.8.8.8  # Windows
traceroute 8.8.8.8  # Linux

# Check routing table
route print  # Windows
route -n  # Linux
ip route show  # Linux
```

**Clues:**
- 💡 The default gateway is the router interface on your local subnet
- 🌐 PCs need IP address, subnet mask, and default gateway for full connectivity
- 🔍 Use "ipconfig" (Windows) or "ifconfig" (Linux) to verify settings
- 🛣️ Test gateway connectivity with "ping 192.168.1.1" before external tests

---

### Challenge 3: DHCP Client Configuration
**Difficulty:** Easy | **ID:** `dhcp-client-config`

**Objective:** Configure DHCP for automatic IP assignment

**Scenario:**
- 1 DHCP Server Router
- 1 LAN Switch
- 3 PCs using APIPA addresses (169.254.x.x)

**Steps to Complete:**
1. **Configure DHCP on Router:**
   - DHCP Pool: `192.168.1.100 - 192.168.1.200`
   - Network: `192.168.1.0/24`
   - Default Gateway: `192.168.1.1`
   - DNS Server: `8.8.8.8`

2. **Enable DHCP on PCs:**
   - Remove static IP configurations
   - Enable DHCP client
   - Obtain IP address automatically

3. **Verify:**
   - PCs receive IP addresses in range
   - PCs can communicate with each other
   - Gateway and DNS are properly configured

**CLI Commands:**
```bash
# Router DHCP Configuration
Router> enable
Router# configure terminal

# Configure Router Interface
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit

# Create DHCP Pool
Router(config)# ip dhcp pool LAN_POOL
Router(dhcp-config)# network 192.168.1.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.1.1
Router(dhcp-config)# dns-server 8.8.8.8 8.8.4.4
Router(dhcp-config)# exit

# Exclude Router IP from DHCP Range
Router(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.99
Router(config)# exit

# Verify DHCP Configuration
Router# show ip dhcp pool
Router# show ip dhcp binding
Router# show ip dhcp server statistics

# PC Configuration - Enable DHCP (Windows)
ipconfig /release
ipconfig /renew
ipconfig /all

# PC Configuration - Enable DHCP (Linux)
sudo dhclient eth0
# OR
sudo dhcpcd eth0

# Verify DHCP Lease
ipconfig /all  # Windows
cat /var/lib/dhcp/dhclient.leases  # Linux

# Check DNS Configuration
nslookup google.com
```

**Clues:**
- 💡 DHCP automates IP address assignment, eliminating manual configuration
- 🔄 DHCP provides IP address, subnet mask, default gateway, and DNS servers
- 🖥️ Use "ip address dhcp" on router interfaces or enable DHCP client on PCs
- ✅ Verify with "ipconfig /all" (Windows) to see DHCP-assigned configuration

---

## 🔧 Intermediate Level (Medium)

### Challenge 1: Ring Network Failure
**Difficulty:** Medium | **ID:** `ring-network-failure`

**Objective:** Diagnose and fix ring topology link failure

**Scenario:**
- 4 Switches in ring topology
- 2 End-user PCs
- One link in the ring is down

**Steps to Complete:**
1. **Identify the broken link** in the ring
2. **Re-establish the connection** or configure alternate path
3. **Verify** all switches can communicate
4. **Test** end-to-end connectivity between PCs

**CLI Commands:**
```bash
# Check interface status on all switches
Switch# show ip interface brief
Switch# show interfaces status
Switch# show interfaces GigabitEthernet0/1

# Check for down interfaces
Switch# show interfaces description
Switch# show interfaces | include down

# Bring interface up
Switch# configure terminal
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# no shutdown
Switch(config-if)# exit

# Verify STP (Spanning Tree Protocol)
Switch# show spanning-tree
Switch# show spanning-tree summary

# Check MAC address table
Switch# show mac address-table
Switch# clear mac address-table dynamic
```

---

### Challenge 2: Tree VLAN Segmentation
**Difficulty:** Medium | **ID:** `tree-vlan-segmentation`

**Objective:** Configure VLANs in hierarchical tree topology

**Scenario:**
- 1 Core Switch
- 2 Distribution Switches
- 4 Access-layer PCs

**Steps to Complete:**
1. **Configure VLANs** on all switches
2. **Set up trunk links** between Core and Distribution switches
3. **Assign access ports** to appropriate VLANs
4. **Verify VLAN segmentation** works correctly

**CLI Commands:**
```bash
# Core Switch Configuration
CoreSwitch(config)# vlan 10
CoreSwitch(config-vlan)# name Management
CoreSwitch(config-vlan)# vlan 20
CoreSwitch(config-vlan)# name Users
CoreSwitch(config-vlan)# exit

# Configure Trunk Ports
CoreSwitch(config)# interface range GigabitEthernet0/1-2
CoreSwitch(config-if-range)# switchport trunk encapsulation dot1q
CoreSwitch(config-if-range)# switchport mode trunk
CoreSwitch(config-if-range)# switchport trunk allowed vlan 10,20
CoreSwitch(config-if-range)# exit

# Distribution Switch Configuration
DistSwitch(config)# vlan 10
DistSwitch(config-vlan)# vlan 20
DistSwitch(config-vlan)# exit

# Trunk to Core
DistSwitch(config)# interface GigabitEthernet0/1
DistSwitch(config-if)# switchport mode trunk
DistSwitch(config-if)# switchport trunk allowed vlan 10,20
DistSwitch(config-if)# exit

# Access Ports for PCs
DistSwitch(config)# interface FastEthernet0/1
DistSwitch(config-if)# switchport mode access
DistSwitch(config-if)# switchport access vlan 10
DistSwitch(config-if)# exit

# Verify Configuration
Switch# show vlan brief
Switch# show interfaces trunk
Switch# show interfaces switchport
```

---

### Challenge 3: RIP Version Mismatch
**Difficulty:** Medium | **ID:** `rip-version-mismatch`

**Objective:** Resolve RIP routing protocol version conflicts

**Scenario:**
- 4 Routers in partial mesh
- Mixed RIP v1 and RIP v2

**Steps to Complete:**
1. **Identify routers** running different RIP versions
2. **Standardize on RIP v2** (supports VLSM and is more efficient)
3. **Verify routing tables** converge properly
4. **Test connectivity** across all routers

**CLI Commands:**
```bash
# Check current RIP configuration
Router# show ip protocols
Router# show ip rip database

# Remove old RIP configuration
Router(config)# no router rip

# Configure RIP Version 2
Router(config)# router rip
Router(config-router)# version 2
Router(config-router)# network 10.0.0.0
Router(config-router)# network 192.168.1.0
Router(config-router)# no auto-summary
Router(config-router)# exit

# Verify RIP is working
Router# show ip route rip
Router# show ip protocols
Router# debug ip rip  # Use carefully, generates lots of output

# Disable debug
Router# undebug all
```

---

## 🚀 Advanced Level (Hard)

### Challenge 1: MPLS VPN Complex
**Difficulty:** Hard | **ID:** `mpls-vpn-complex`

**Objective:** Configure MPLS VPN with multiple customer sites

**Scenario:**
- Multiple Provider Edge (PE) routers
- Multiple Customer Edge (CE) routers
- Full MPLS VPN setup required

**CLI Commands:**
```bash
# Provider Router (P) - MPLS Configuration
P-Router(config)# ip cef
P-Router(config)# mpls ip
P-Router(config)# mpls label protocol ldp
P-Router(config)# interface GigabitEthernet0/0
P-Router(config-if)# mpls ip
P-Router(config-if)# exit

# Provider Edge Router (PE) - VRF Configuration
PE-Router(config)# ip vrf CUSTOMER_A
PE-Router(config-vrf)# rd 65000:1
PE-Router(config-vrf)# route-target export 65000:1
PE-Router(config-vrf)# route-target import 65000:1
PE-Router(config-vrf)# exit

# Assign Interface to VRF
PE-Router(config)# interface GigabitEthernet0/0
PE-Router(config-if)# ip vrf forwarding CUSTOMER_A
PE-Router(config-if)# ip address 10.1.1.1 255.255.255.0
PE-Router(config-if)# exit

# Configure MP-BGP
PE-Router(config)# router bgp 65000
PE-Router(config-router)# neighbor 10.0.0.2 remote-as 65000
PE-Router(config-router)# neighbor 10.0.0.2 update-source Loopback0
PE-Router(config-router)# address-family vpnv4
PE-Router(config-router-af)# neighbor 10.0.0.2 activate
PE-Router(config-router-af)# exit

# Verify MPLS
PE-Router# show mpls forwarding-table
PE-Router# show ip vrf
PE-Router# show ip route vrf CUSTOMER_A
```

---

### Challenge 2: Datacenter Fabric
**Difficulty:** Hard | **ID:** `datacenter-fabric`

**Objective:** Design and implement spine-leaf datacenter architecture

**Scenario:**
- Multiple Spine switches
- Multiple Leaf switches
- Server redundancy

**CLI Commands:**
```bash
# Spine Switch Configuration
Spine-Switch(config)# feature vpc
Spine-Switch(config)# feature lacp

# Configure vPC domain
Spine-Switch(config)# vpc domain 1
Spine-Switch(config-vpc-domain)# peer-keepalive destination 10.0.0.2 source 10.0.0.1
Spine-Switch(config-vpc-domain)# exit

# Configure port-channel for vPC peer-link
Spine-Switch(config)# interface port-channel1
Spine-Switch(config-if)# switchport mode trunk
Spine-Switch(config-if)# vpc peer-link
Spine-Switch(config-if)# exit

# Leaf Switch Configuration
Leaf-Switch(config)# interface Ethernet1/1
Leaf-Switch(config-if)# channel-group 10 mode active
Leaf-Switch(config-if)# exit

Leaf-Switch(config)# interface port-channel10
Leaf-Switch(config-if)# switchport mode trunk
Leaf-Switch(config-if)# vpc 10
Leaf-Switch(config-if)# exit

# Verify Configuration
Switch# show vpc
Switch# show vpc peer-keepalive
Switch# show port-channel summary
```

---

### Challenge 3: SD-WAN Overlay
**Difficulty:** Hard | **ID:** `sd-wan-overlay`

**Objective:** Configure SD-WAN overlay network

**Scenario:**
- Multiple branch sites
- Central hub
- Application-aware routing

**CLI Commands:**
```bash
# SD-WAN Edge Router Configuration
Router(config)# sdwan
Router(config-sdwan)# interface GigabitEthernet0/0
Router(config-interface-GigabitEthernet0/0)# tunnel-interface
Router(config-tunnel-interface)# encapsulation ipsec
Router(config-tunnel-interface)# color biz-internet
Router(config-tunnel-interface)# allow-service all
Router(config-tunnel-interface)# exit
Router(config-sdwan)# exit

# Configure VPN
Router(config)# vpn 10
Router(config-vpn-10)# interface GigabitEthernet0/1
Router(config-interface-GigabitEthernet0/1)# ip address 192.168.10.1/24
Router(config-interface-GigabitEthernet0/1)# exit

# Application-Aware Routing Policy
Router(config)# policy
Router(config-policy)# sla-class VOICE
Router(config-sla-class)# latency 100
Router(config-sla-class)# jitter 30
Router(config-sla-class)# loss 1
Router(config-sla-class)# exit

# Verify SD-WAN
Router# show sdwan control connections
Router# show sdwan policy summary
Router# show sdwan omp routes
```

---

## 📚 CLI Commands Reference

### Basic Device Configuration

#### Router Basic Setup
```bash
Router> enable
Router# configure terminal
Router(config)# hostname R1
Router(config)# enable secret cisco123
Router(config)# line console 0
Router(config-line)# password console123
Router(config-line)# login
Router(config-line)# logging synchronous
Router(config-line)# exit
Router(config)# line vty 0 4
Router(config-line)# password telnet123
Router(config-line)# login
Router(config-line)# exit
Router(config)# service password-encryption
Router(config)# banner motd # Unauthorized access prohibited #
Router(config)# exit
Router# copy running-config startup-config
```

#### Switch Basic Setup
```bash
Switch> enable
Switch# configure terminal
Switch(config)# hostname SW1
Switch(config)# enable secret cisco123
Switch(config)# line console 0
Switch(config-line)# password console123
Switch(config-line)# login
Switch(config-line)# exit
Switch(config)# interface vlan 1
Switch(config-if)# ip address 192.168.1.2 255.255.255.0
Switch(config-if)# no shutdown
Switch(config-if)# exit
Switch(config)# ip default-gateway 192.168.1.1
Switch(config)# exit
Switch# copy running-config startup-config
```

### Interface Configuration

#### Router Interface
```bash
Router(config)# interface GigabitEthernet0/0
Router(config-if)# description LAN Interface
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit
```

#### Switch Interface
```bash
Switch(config)# interface FastEthernet0/1
Switch(config-if)# description Connection to PC-1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# spanning-tree portfast
Switch(config-if)# no shutdown
Switch(config-if)# exit
```

### VLAN Configuration

```bash
# Create VLAN
Switch(config)# vlan 10
Switch(config-vlan)# name Sales
Switch(config-vlan)# exit

# Assign port to VLAN
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# exit

# Configure trunk port
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport trunk encapsulation dot1q
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,30
Switch(config-if)# exit

# Verify VLANs
Switch# show vlan brief
Switch# show interfaces trunk
```

### Static Routing

```bash
# Add static route
Router(config)# ip route 10.2.2.0 255.255.255.0 10.1.1.2

# Default route
Router(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1

# Verify routes
Router# show ip route
Router# show ip route static
```

### Dynamic Routing - RIP

```bash
# Configure RIP
Router(config)# router rip
Router(config-router)# version 2
Router(config-router)# network 192.168.1.0
Router(config-router)# network 10.0.0.0
Router(config-router)# no auto-summary
Router(config-router)# exit

# Verify RIP
Router# show ip protocols
Router# show ip route rip
```

### Dynamic Routing - OSPF

```bash
# Configure OSPF
Router(config)# router ospf 1
Router(config-router)# router-id 1.1.1.1
Router(config-router)# network 192.168.1.0 0.0.0.255 area 0
Router(config-router)# network 10.1.1.0 0.0.0.255 area 0
Router(config-router)# exit

# Verify OSPF
Router# show ip ospf neighbor
Router# show ip ospf interface
Router# show ip route ospf
```

### DHCP Configuration

```bash
# Configure DHCP Server
Router(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.10
Router(config)# ip dhcp pool LAN_POOL
Router(dhcp-config)# network 192.168.1.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.1.1
Router(dhcp-config)# dns-server 8.8.8.8 8.8.4.4
Router(dhcp-config)# lease 7
Router(dhcp-config)# exit

# Verify DHCP
Router# show ip dhcp pool
Router# show ip dhcp binding
Router# show ip dhcp server statistics
```

### NAT Configuration

```bash
# Configure NAT with overload (PAT)
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip nat inside
Router(config-if)# exit

Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip nat outside
Router(config-if)# exit

Router(config)# access-list 1 permit 192.168.1.0 0.0.0.255
Router(config)# ip nat inside source list 1 interface GigabitEthernet0/1 overload

# Verify NAT
Router# show ip nat translations
Router# show ip nat statistics
Router# clear ip nat translation *
```

### Access Control Lists (ACLs)

```bash
# Standard ACL
Router(config)# access-list 10 permit 192.168.1.0 0.0.0.255
Router(config)# access-list 10 deny any

# Extended ACL
Router(config)# access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 80
Router(config)# access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 443
Router(config)# access-list 100 deny ip any any

# Apply ACL to interface
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip access-group 100 in
Router(config-if)# exit

# Verify ACL
Router# show access-lists
Router# show ip interface GigabitEthernet0/0
```

### Troubleshooting Commands

```bash
# Connectivity tests
ping 192.168.1.1
traceroute 8.8.8.8
telnet 192.168.1.1

# Interface verification
show ip interface brief
show interfaces
show interfaces status
show interfaces description

# Routing verification
show ip route
show ip protocols
show ip route summary

# CDP/LLDP (neighbor discovery)
show cdp neighbors
show cdp neighbors detail
show lldp neighbors

# MAC address table
show mac address-table
show mac address-table dynamic

# Spanning Tree
show spanning-tree
show spanning-tree summary

# System information
show version
show running-config
show startup-config
show flash
show processes cpu
show memory

# Debugging (use with caution)
debug ip icmp
debug ip routing
debug ip rip
undebug all  # Stop all debugging
```

---

## 🎯 Completion Tips

### General Tips:
1. **Read clues carefully** - They provide hints about the solution
2. **Check device configurations** - Click on devices to view/edit properties
3. **Verify connections** - Ensure all cables are properly connected
4. **Test incrementally** - Use ping to test each step
5. **Use CLI commands** - Practice the commands to build muscle memory
6. **Review topology** - Understand the network design before configuring
7. **Save your work** - Backend automatically saves your progress

### Scoring:
- **Foundation:** +15 XP per phase
- **Novice:** +30 XP per challenge
- **Intermediate:** +60 XP per challenge
- **Advanced:** +125 XP per challenge

### Unlocking Progression:
1. Complete **Foundation Learning** to unlock **Novice Level**
2. Complete **3 Novice challenges** to unlock **Intermediate Level**
3. Complete **5 Intermediate challenges** to unlock **Advanced Level**

---

## 📖 Additional Resources

### Learning Paths:
- Start with **Foundation Learning** to build basics
- Progress through **Novice** challenges to practice fundamentals
- Move to **Intermediate** for multi-segment networks
- Tackle **Advanced** for enterprise-level scenarios

### Practice Recommendations:
1. Complete each phase of Foundation Learning in order
2. Master Novice challenges before moving to Intermediate
3. Review CLI commands and practice in a real lab environment
4. Focus on understanding concepts, not just completing challenges

### Need Help?
- Click the **Hints** button (💡) during challenges
- Review the **Clues** section for each challenge
- Check the **Live Performance** sidebar for real-time guidance
- Consult network diagrams and topology guides

---

**Good luck on your networking journey! 🚀**

*Last Updated: October 2025*

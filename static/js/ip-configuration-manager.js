/**
 * IP Configuration Manager for Network Simulation Core
 * Handles IP address assignment, subnet configuration, and validation
 */

class IPConfigurationManager {
    constructor() {
        this.networkConfigs = new Map();
        this.subnetMasks = {
            '/24': '255.255.255.0',
            '/25': '255.255.255.128', 
            '/26': '255.255.255.192',
            '/27': '255.255.255.224',
            '/28': '255.255.255.240',
            '/29': '255.255.255.248',
            '/30': '255.255.255.252'
        };
        this.initializeInterface();
    }

    initializeInterface() {
        // Create IP configuration modal
        this.createConfigModal();
        
        // Add event listeners for device configuration
        this.attachEventListeners();
    }

    createConfigModal() {
        // Prevent creating duplicate modal if script is included multiple times
        if (document.getElementById('ipConfigModal')) {
            return; // Modal already exists
        }
        const modalHTML = `
        <div id="ipConfigModal" class="ip-config-modal" style="display: none;">
            <div class="ip-config-content">
                <div class="ip-config-header">
                    <h3>IP Configuration</h3>
                    <button class="close-btn" onclick="ipManager.closeConfigModal()">&times;</button>
                </div>
                
                <div class="ip-config-body">
                    <div class="device-info">
                        <div class="device-header">
                            <h4 id="configDeviceName">Device Name</h4>
                            <span id="deviceStatus" class="status-indicator">Online</span>
                        </div>
                        <div class="device-details">
                            <div class="detail-row">
                                <span class="label">Type:</span>
                                <span id="configDeviceType">Device Type</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Model:</span>
                                <span id="deviceModel">Unknown</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">MAC Address:</span>
                                <span id="deviceMAC">00:00:00:00:00:00</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Uptime:</span>
                                <span id="deviceUptime">00:00:00</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Connections:</span>
                                <span id="deviceConnections">0 active</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Operating System:</span>
                                <span id="deviceOS">Network OS</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="interface-tabs">
                        <button class="tab-btn active" data-tab="basic">Basic Config</button>
                        <button class="tab-btn" data-tab="advanced">Advanced</button>
                        <button class="tab-btn" data-tab="validation">Validation</button>
                        <button class="tab-btn" data-tab="monitoring">Monitoring</button>
                        <button class="tab-btn" data-tab="security">Security</button>
                    </div>
                    
                    <div id="basicTab" class="tab-content active">
                        <div class="config-section">
                            <label for="interfaceSelect">Interface:</label>
                            <select id="interfaceSelect">
                                <option value="eth0">Ethernet 0 (eth0)</option>
                                <option value="eth1">Ethernet 1 (eth1)</option>
                                <option value="wifi0">WiFi 0 (wifi0)</option>
                                <option value="lo">Loopback (lo)</option>
                            </select>
                        </div>
                        
                        <div class="config-section">
                            <label>IP Configuration Mode:</label>
                            <div class="ip-mode-options">
                                <label><input type="radio" name="ipMode" value="static" checked> Static IP</label>
                                <label><input type="radio" name="ipMode" value="dhcp"> DHCP</label>
                                <label><input type="radio" name="ipMode" value="auto"> Auto-IP</label>
                            </div>
                        </div>
                        
                        <div class="config-section" id="staticIpSection">
                            <label for="deviceIP">IP Address:</label>
                            <input type="text" id="deviceIP" placeholder="192.168.1.1" 
                                   pattern="^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$">
                            <div class="ip-helper">
                                <span class="helper-text">Format: xxx.xxx.xxx.xxx</span>
                                <button type="button" class="suggest-ip-btn" onclick="ipManager.suggestIP()">Suggest IP</button>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label for="subnetMask">Subnet Mask:</label>
                            <select id="subnetMask">
                                <option value="255.255.255.0">/24 - 255.255.255.0 (254 hosts)</option>
                                <option value="255.255.255.128">/25 - 255.255.255.128 (126 hosts)</option>
                                <option value="255.255.255.192">/26 - 255.255.255.192 (62 hosts)</option>
                                <option value="255.255.255.224">/27 - 255.255.255.224 (30 hosts)</option>
                                <option value="255.255.255.240">/28 - 255.255.255.240 (14 hosts)</option>
                                <option value="255.255.255.248">/29 - 255.255.255.248 (6 hosts)</option>
                                <option value="255.255.255.252">/30 - 255.255.255.252 (2 hosts)</option>
                            </select>
                        </div>
                        
                        <div class="config-section">
                            <label for="defaultGateway">Default Gateway:</label>
                            <input type="text" id="defaultGateway" placeholder="192.168.1.254">
                            <div class="gateway-helper">
                                <button type="button" class="detect-gateway-btn" onclick="ipManager.detectGateway()">Auto-detect</button>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label for="dnsServer">DNS Servers:</label>
                            <input type="text" id="dnsServer" placeholder="8.8.8.8, 1.1.1.1">
                            <div class="dns-presets">
                                <button type="button" onclick="ipManager.setDNS('google')">Google DNS</button>
                                <button type="button" onclick="ipManager.setDNS('cloudflare')">Cloudflare DNS</button>
                                <button type="button" onclick="ipManager.setDNS('opendns')">OpenDNS</button>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label for="mtu">MTU Size:</label>
                            <input type="number" id="mtu" min="576" max="9000" value="1500" placeholder="1500">
                            <div class="mtu-helper">
                                <span class="helper-text">Standard: 1500 (Ethernet), 1472 (PPPoE)</span>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label>Connection Quality:</label>
                            <div class="quality-info">
                                <div class="quality-metric">
                                    <span class="metric-label">Link Speed:</span>
                                    <span id="linkSpeed">1000 Mbps</span>
                                </div>
                                <div class="quality-metric">
                                    <span class="metric-label">Duplex:</span>
                                    <span id="duplexMode">Full</span>
                                </div>
                                <div class="quality-metric">
                                    <span class="metric-label">Signal:</span>
                                    <div class="signal-strength">
                                        <div class="signal-bar active"></div>
                                        <div class="signal-bar active"></div>
                                        <div class="signal-bar active"></div>
                                        <div class="signal-bar"></div>
                                        <div class="signal-bar"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="advancedTab" class="tab-content">
                        <div class="config-section">
                            <label for="vlanId">VLAN Configuration:</label>
                            <div class="vlan-config">
                                <input type="number" id="vlanId" min="1" max="4094" placeholder="1">
                                <select id="vlanMode">
                                    <option value="access">Access Port</option>
                                    <option value="trunk">Trunk Port</option>
                                    <option value="hybrid">Hybrid Port</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label>Routing Protocol:</label>
                            <div class="protocol-options">
                                <label><input type="radio" name="routing" value="static" checked> Static</label>
                                <label><input type="radio" name="routing" value="rip"> RIP v2</label>
                                <label><input type="radio" name="routing" value="ospf"> OSPF</label>
                                <label><input type="radio" name="routing" value="eigrp"> EIGRP</label>
                                <label><input type="radio" name="routing" value="bgp"> BGP</label>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label for="ospfArea">OSPF Area (if applicable):</label>
                            <input type="text" id="ospfArea" placeholder="0.0.0.0" disabled>
                        </div>
                        
                        <div class="config-section">
                            <label for="spanningTree">Spanning Tree Protocol:</label>
                            <select id="spanningTree">
                                <option value="disabled">Disabled</option>
                                <option value="stp">Classic STP</option>
                                <option value="rstp">Rapid STP (RSTP)</option>
                                <option value="mstp">Multiple STP (MSTP)</option>
                                <option value="pvst">Per-VLAN STP</option>
                            </select>
                        </div>
                        
                        <div class="config-section">
                            <label>QoS Configuration:</label>
                            <div class="qos-config">
                                <div class="qos-row">
                                    <label for="priorityQueue">Priority Queue:</label>
                                    <select id="priorityQueue">
                                        <option value="0">Best Effort (0)</option>
                                        <option value="1">Background (1)</option>
                                        <option value="2">Standard (2)</option>
                                        <option value="3">Excellent Effort (3)</option>
                                        <option value="4">Controlled Load (4)</option>
                                        <option value="5">Video (5)</option>
                                        <option value="6">Voice (6)</option>
                                        <option value="7">Network Control (7)</option>
                                    </select>
                                </div>
                                <div class="qos-row">
                                    <label for="bandwidthLimit">Bandwidth Limit:</label>
                                    <input type="number" id="bandwidthLimit" placeholder="100" min="1">
                                    <select id="bandwidthUnit">
                                        <option value="mbps">Mbps</option>
                                        <option value="kbps">Kbps</option>
                                        <option value="gbps">Gbps</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label for="portSecurity">Port Security:</label>
                            <div class="port-security">
                                <label><input type="checkbox" id="portSecurityEnabled"> Enable Port Security</label>
                                <div class="port-security-options" style="margin-top: 10px;">
                                    <label for="maxMacAddresses">Max MAC Addresses:</label>
                                    <input type="number" id="maxMacAddresses" min="1" max="256" value="1" disabled>
                                    <label for="violationAction">Violation Action:</label>
                                    <select id="violationAction" disabled>
                                        <option value="shutdown">Shutdown</option>
                                        <option value="restrict">Restrict</option>
                                        <option value="protect">Protect</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label for="interfaceConfig">Custom Interface Commands:</label>
                            <textarea id="interfaceConfig" rows="6" 
                                      placeholder="# Enter custom configuration commands here
# Example:
# no shutdown
# duplex full
# speed 1000"></textarea>
                        </div>
                        
                        <div class="config-section">
                            <label>Power Management:</label>
                            <div class="power-options">
                                <label><input type="checkbox" id="poeEnabled"> Power over Ethernet (PoE)</label>
                                <label><input type="checkbox" id="energyEfficientEthernet"> Energy Efficient Ethernet</label>
                                <label><input type="checkbox" id="wakeOnLan"> Wake on LAN</label>
                            </div>
                        </div>
                    </div>
                    
                    <div id="validationTab" class="tab-content">
                        <div class="validation-results">
                            <h4>Configuration Validation</h4>
                            <div id="validationResults"></div>
                            <div class="validation-actions">
                                <button class="btn-test" onclick="ipManager.pingTest()">Ping Test</button>
                                <button class="btn-test" onclick="ipManager.dnsTest()">DNS Test</button>
                                <button class="btn-test" onclick="ipManager.connectivityTest()">Full Connectivity Test</button>
                            </div>
                        </div>
                        
                        <div class="network-summary">
                            <h4>Network Summary</h4>
                            <div id="networkSummary"></div>
                        </div>
                        
                        <div class="performance-metrics">
                            <h4>Performance Metrics</h4>
                            <div id="performanceMetrics">
                                <div class="metric-item">
                                    <span class="metric-label">Latency:</span>
                                    <span class="metric-value" id="latencyValue">< 1ms</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">Packet Loss:</span>
                                    <span class="metric-value" id="packetLossValue">0%</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">Throughput:</span>
                                    <span class="metric-value" id="throughputValue">1000 Mbps</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">Jitter:</span>
                                    <span class="metric-value" id="jitterValue">< 0.1ms</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="troubleshooting">
                            <h4>Troubleshooting Tools</h4>
                            <div class="troubleshooting-actions">
                                <button class="btn-tool" onclick="ipManager.routeTrace()">Route Trace</button>
                                <button class="btn-tool" onclick="ipManager.arpTable()">ARP Table</button>
                                <button class="btn-tool" onclick="ipManager.interfaceStats()">Interface Stats</button>
                                <button class="btn-tool" onclick="ipManager.portScan()">Port Scan</button>
                            </div>
                        </div>
                    </div>
                    
                    <div id="monitoringTab" class="tab-content">
                        <div class="monitoring-section">
                            <h4>Real-time Statistics</h4>
                            <div class="stats-grid">
                                <div class="stat-card">
                                    <div class="stat-title">Bytes In</div>
                                    <div class="stat-value" id="bytesIn">0 MB</div>
                                    <div class="stat-chart" id="bytesInChart"></div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">Bytes Out</div>
                                    <div class="stat-value" id="bytesOut">0 MB</div>
                                    <div class="stat-chart" id="bytesOutChart"></div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">Packets In</div>
                                    <div class="stat-value" id="packetsIn">0</div>
                                    <div class="stat-chart" id="packetsInChart"></div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">Packets Out</div>
                                    <div class="stat-value" id="packetsOut">0</div>
                                    <div class="stat-chart" id="packetsOutChart"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="monitoring-section">
                            <h4>Device Health</h4>
                            <div class="health-indicators">
                                <div class="health-item">
                                    <span class="health-label">CPU Usage:</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: 25%"></div>
                                    </div>
                                    <span class="health-value">25%</span>
                                </div>
                                <div class="health-item">
                                    <span class="health-label">Memory Usage:</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: 60%"></div>
                                    </div>
                                    <span class="health-value">60%</span>
                                </div>
                                <div class="health-item">
                                    <span class="health-label">Temperature:</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: 45%"></div>
                                    </div>
                                    <span class="health-value">45°C</span>
                                </div>
                                <div class="health-item">
                                    <span class="health-label">Power:</span>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: 80%"></div>
                                    </div>
                                    <span class="health-value">12.5W</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="monitoring-section">
                            <h4>Connection Monitor</h4>
                            <div class="connection-list">
                                <div class="connection-item">
                                    <span class="connection-icon">🔗</span>
                                    <span class="connection-name">Router-1</span>
                                    <span class="connection-status active">Active</span>
                                    <span class="connection-speed">1 Gbps</span>
                                </div>
                                <div class="connection-item">
                                    <span class="connection-icon">💻</span>
                                    <span class="connection-name">PC-2</span>
                                    <span class="connection-status active">Active</span>
                                    <span class="connection-speed">100 Mbps</span>
                                </div>
                                <div class="connection-item">
                                    <span class="connection-icon">📱</span>
                                    <span class="connection-name">Mobile-3</span>
                                    <span class="connection-status inactive">Inactive</span>
                                    <span class="connection-speed">--</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="monitoring-section">
                            <h4>Event Log</h4>
                            <div class="event-log">
                                <div class="log-entry">
                                    <span class="log-time">14:32:15</span>
                                    <span class="log-level info">INFO</span>
                                    <span class="log-message">Interface eth0 link up</span>
                                </div>
                                <div class="log-entry">
                                    <span class="log-time">14:31:02</span>
                                    <span class="log-level warning">WARN</span>
                                    <span class="log-message">High CPU usage detected</span>
                                </div>
                                <div class="log-entry">
                                    <span class="log-time">14:29:45</span>
                                    <span class="log-level info">INFO</span>
                                    <span class="log-message">DHCP lease renewed</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="securityTab" class="tab-content">
                        <div class="security-section">
                            <h4>Access Control</h4>
                            <div class="config-section">
                                <label for="accessMode">Access Mode:</label>
                                <select id="accessMode">
                                    <option value="open">Open Access</option>
                                    <option value="wpa2">WPA2-PSK</option>
                                    <option value="wpa3">WPA3</option>
                                    <option value="8021x">802.1X</option>
                                    <option value="custom">Custom</option>
                                </select>
                            </div>
                            <div class="config-section">
                                <label for="accessPassword">Password/Key:</label>
                                <input type="password" id="accessPassword" placeholder="Enter password">
                                <button type="button" class="toggle-password" onclick="ipManager.togglePassword()">👁️</button>
                            </div>
                        </div>
                        
                        <div class="security-section">
                            <h4>Firewall Rules</h4>
                            <div class="firewall-rules">
                                <div class="rule-item">
                                    <span class="rule-action allow">ALLOW</span>
                                    <span class="rule-protocol">TCP</span>
                                    <span class="rule-port">80</span>
                                    <span class="rule-source">Any</span>
                                    <button class="rule-delete">❌</button>
                                </div>
                                <div class="rule-item">
                                    <span class="rule-action allow">ALLOW</span>
                                    <span class="rule-protocol">TCP</span>
                                    <span class="rule-port">443</span>
                                    <span class="rule-source">Any</span>
                                    <button class="rule-delete">❌</button>
                                </div>
                                <div class="rule-item">
                                    <span class="rule-action deny">DENY</span>
                                    <span class="rule-protocol">TCP</span>
                                    <span class="rule-port">22</span>
                                    <span class="rule-source">External</span>
                                    <button class="rule-delete">❌</button>
                                </div>
                            </div>
                            <button class="btn-add-rule" onclick="ipManager.addFirewallRule()">+ Add Rule</button>
                        </div>
                        
                        <div class="security-section">
                            <h4>Intrusion Detection</h4>
                            <div class="ids-config">
                                <label><input type="checkbox" id="idsEnabled"> Enable IDS/IPS</label>
                                <div class="ids-options">
                                    <label for="idsMode">Detection Mode:</label>
                                    <select id="idsMode">
                                        <option value="passive">Passive Monitoring</option>
                                        <option value="active">Active Blocking</option>
                                        <option value="learning">Learning Mode</option>
                                    </select>
                                </div>
                                <div class="ids-stats">
                                    <div class="ids-stat">
                                        <span class="stat-label">Threats Blocked:</span>
                                        <span class="stat-number">0</span>
                                    </div>
                                    <div class="ids-stat">
                                        <span class="stat-label">Suspicious Activities:</span>
                                        <span class="stat-number">2</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="security-section">
                            <h4>MAC Address Filtering</h4>
                            <div class="mac-filter">
                                <label><input type="checkbox" id="macFilterEnabled"> Enable MAC Filtering</label>
                                <div class="mac-filter-mode">
                                    <label><input type="radio" name="macFilterMode" value="whitelist"> Whitelist (Allow only listed)</label>
                                    <label><input type="radio" name="macFilterMode" value="blacklist"> Blacklist (Block listed)</label>
                                </div>
                                <div class="mac-addresses">
                                    <input type="text" id="newMacAddress" placeholder="00:11:22:33:44:55" pattern="^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$">
                                    <button class="btn-add-mac" onclick="ipManager.addMacAddress()">Add MAC</button>
                                </div>
                                <div class="mac-list">
                                    <!-- MAC addresses will be populated here -->
                                </div>
                            </div>
                        </div>
                        
                        <div class="security-section">
                            <h4>VPN Configuration</h4>
                            <div class="vpn-config">
                                <label for="vpnType">VPN Type:</label>
                                <select id="vpnType">
                                    <option value="none">Disabled</option>
                                    <option value="pptp">PPTP</option>
                                    <option value="l2tp">L2TP/IPSec</option>
                                    <option value="openvpn">OpenVPN</option>
                                    <option value="wireguard">WireGuard</option>
                                </select>
                                <div class="vpn-status">
                                    <span class="vpn-indicator offline">⚫ Disconnected</span>
                                    <button class="btn-vpn-connect">Connect</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="ip-config-footer">
                    <button class="btn-secondary" onclick="ipManager.closeConfigModal()">Cancel</button>
                    <button class="btn-primary" onclick="ipManager.applyConfiguration()">Apply</button>
                    <button class="btn-success" onclick="ipManager.validateConfiguration()">Validate</button>
                </div>
            </div>
        </div>`;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Add CSS styles
        this.addConfigStyles();
    }

    addConfigStyles() {
        // Prevent duplicate style injection
        if (document.getElementById('ip-config-style-tag')) return;

        const styles = `
        <style id="ip-config-style-tag">
        .ip-config-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .ip-config-content {
            background: #2a2a2a;
            border-radius: 12px;
            width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            color: white;
        }
        
        .ip-config-header {
            padding: 20px;
            border-bottom: 1px solid #444;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .ip-config-header h3 {
            margin: 0;
            color: #00d4ff;
        }
        
        .close-btn {
            background: none;
            border: none;
            color: #ccc;
            font-size: 24px;
            cursor: pointer;
        }
        
        .ip-config-body {
            padding: 20px;
        }
        
        .device-info {
            margin-bottom: 20px;
            padding: 15px;
            background: #333;
            border-radius: 8px;
        }
        
        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .device-header h4 {
            margin: 0;
            color: #00d4ff;
        }
        
        .status-indicator {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            background: #28a745;
            color: white;
        }
        
        .status-indicator.offline {
            background: #dc3545;
        }
        
        .device-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
        }
        
        .detail-row .label {
            color: #999;
            font-size: 13px;
        }
        
        .detail-row span:last-child {
            color: #ccc;
            font-size: 13px;
            font-family: 'Courier New', monospace;
        }
        
        .interface-tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #444;
        }
        
        .tab-btn {
            background: none;
            border: none;
            color: #ccc;
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
        }
        
        .tab-btn.active {
            color: #00d4ff;
            border-bottom-color: #00d4ff;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .config-section {
            margin-bottom: 20px;
        }
        
        .config-section label {
            display: block;
            margin-bottom: 8px;
            color: #ccc;
            font-weight: 500;
        }
        
        .config-section input,
        .config-section select,
        .config-section textarea {
            width: 100%;
            padding: 10px;
            background: #444;
            border: 1px solid #666;
            border-radius: 6px;
            color: white;
            font-family: 'Courier New', monospace;
        }
        
        .config-section input:focus,
        .config-section select:focus,
        .config-section textarea:focus {
            outline: none;
            border-color: #00d4ff;
        }
        
        .ip-helper {
            margin-top: 5px;
        }
        
        .helper-text {
            font-size: 12px;
            color: #999;
        }
        
        .protocol-options {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .protocol-options label {
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 0;
        }
        
        .validation-results,
        .network-summary {
            padding: 15px;
            background: #333;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .validation-results h4,
        .network-summary h4 {
            margin: 0 0 10px 0;
            color: #00d4ff;
        }
        
        .ip-config-footer {
            padding: 20px;
            border-top: 1px solid #444;
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        
        .btn-primary, .btn-secondary, .btn-success {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .btn-primary {
            background: #00d4ff;
            color: #000;
        }
        
        .btn-secondary {
            background: #666;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-primary:hover { background: #00b8e6; }
        .btn-secondary:hover { background: #777; }
        .btn-success:hover { background: #218838; }
        
        .validation-error { color: #dc3545; }
        .validation-success { color: #28a745; }
        .validation-warning { color: #ffc107; }
        
        /* Enhanced form elements */
        .ip-mode-options, .protocol-options, .power-options {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .ip-mode-options label, .protocol-options label, .power-options label {
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 0;
        }
        
        .ip-helper {
            margin-top: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .suggest-ip-btn, .detect-gateway-btn {
            background: #444;
            border: 1px solid #666;
            color: #00d4ff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
        }
        
        .dns-presets {
            margin-top: 8px;
            display: flex;
            gap: 8px;
        }
        
        .dns-presets button {
            background: #555;
            border: 1px solid #666;
            color: #ccc;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
        }
        
        .quality-info {
            background: #444;
            padding: 10px;
            border-radius: 6px;
        }
        
        .quality-metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .signal-strength {
            display: flex;
            gap: 2px;
        }
        
        .signal-bar {
            width: 8px;
            height: 12px;
            background: #666;
            border-radius: 1px;
        }
        
        .signal-bar.active {
            background: #28a745;
        }
        
        /* Advanced tab styles */
        .vlan-config {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .vlan-config input {
            flex: 1;
        }
        
        .vlan-config select {
            flex: 1;
        }
        
        .qos-config {
            background: #444;
            padding: 10px;
            border-radius: 6px;
        }
        
        .qos-row {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .qos-row label {
            min-width: 120px;
            margin-bottom: 0;
        }
        
        .port-security {
            background: #444;
            padding: 10px;
            border-radius: 6px;
        }
        
        .port-security-options {
            padding-left: 20px;
        }
        
        /* Validation tab enhancements */
        .validation-actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        
        .btn-test, .btn-tool {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .performance-metrics {
            background: #333;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .performance-metrics h4 {
            margin: 0 0 10px 0;
            color: #00d4ff;
        }
        
        .metric-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .troubleshooting {
            background: #333;
            padding: 15px;
            border-radius: 8px;
        }
        
        .troubleshooting h4 {
            margin: 0 0 10px 0;
            color: #00d4ff;
        }
        
        .troubleshooting-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        /* Monitoring tab styles */
        .monitoring-section {
            margin-bottom: 20px;
            background: #333;
            padding: 15px;
            border-radius: 8px;
        }
        
        .monitoring-section h4 {
            margin: 0 0 15px 0;
            color: #00d4ff;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .stat-card {
            background: #444;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-title {
            color: #999;
            font-size: 12px;
            margin-bottom: 8px;
        }
        
        .stat-value {
            color: #00d4ff;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-chart {
            height: 40px;
            background: #555;
            border-radius: 4px;
        }
        
        .health-indicators {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .health-item {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .health-label {
            min-width: 120px;
            color: #ccc;
        }
        
        .progress-bar {
            flex: 1;
            height: 8px;
            background: #555;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #ffc107, #dc3545);
            transition: width 0.3s ease;
        }
        
        .health-value {
            min-width: 60px;
            text-align: right;
            color: #ccc;
            font-family: 'Courier New', monospace;
        }
        
        .connection-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .connection-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 10px;
            background: #444;
            border-radius: 6px;
        }
        
        .connection-status.active {
            color: #28a745;
        }
        
        .connection-status.inactive {
            color: #dc3545;
        }
        
        .event-log {
            max-height: 200px;
            overflow-y: auto;
            background: #444;
            border-radius: 6px;
            padding: 10px;
        }
        
        .log-entry {
            display: flex;
            gap: 10px;
            margin-bottom: 8px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        
        .log-level.info { color: #17a2b8; }
        .log-level.warning { color: #ffc107; }
        .log-level.error { color: #dc3545; }
        
        /* Security tab styles */
        .security-section {
            margin-bottom: 20px;
            background: #333;
            padding: 15px;
            border-radius: 8px;
        }
        
        .security-section h4 {
            margin: 0 0 15px 0;
            color: #00d4ff;
        }
        
        .toggle-password {
            background: none;
            border: none;
            color: #ccc;
            cursor: pointer;
            padding: 0 5px;
        }
        
        .firewall-rules {
            margin-bottom: 15px;
        }
        
        .rule-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 8px;
            background: #444;
            border-radius: 4px;
            margin-bottom: 8px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        
        .rule-action.allow {
            background: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
        }
        
        .rule-action.deny {
            background: #dc3545;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
        }
        
        .rule-delete {
            background: none;
            border: none;
            cursor: pointer;
            margin-left: auto;
        }
        
        .btn-add-rule {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .ids-config {
            background: #444;
            padding: 15px;
            border-radius: 6px;
        }
        
        .ids-options {
            margin: 15px 0;
        }
        
        .ids-stats {
            display: flex;
            gap: 20px;
        }
        
        .ids-stat {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #00d4ff;
        }
        
        .mac-filter {
            background: #444;
            padding: 15px;
            border-radius: 6px;
        }
        
        .mac-filter-mode {
            margin: 15px 0;
            display: flex;
            gap: 20px;
        }
        
        .mac-addresses {
            display: flex;
            gap: 10px;
            margin: 15px 0;
        }
        
        .btn-add-mac {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .vpn-config {
            background: #444;
            padding: 15px;
            border-radius: 6px;
        }
        
        .vpn-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
        }
        
        .vpn-indicator.offline {
            color: #dc3545;
        }
        
        .vpn-indicator.online {
            color: #28a745;
        }
        
        .btn-vpn-connect {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        </style>`;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    attachEventListeners() {
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                this.switchTab(e.target.dataset.tab);
            }
        });
        
        // Real-time validation
        document.addEventListener('input', (e) => {
            if (e.target.id === 'deviceIP') {
                this.validateIPFormat(e.target.value);
            }
        });

        // IP mode change handling
        document.addEventListener('change', (e) => {
            if (e.target.name === 'ipMode') {
                this.handleIPModeChange(e.target.value);
            }
            if (e.target.name === 'routing') {
                this.handleRoutingProtocolChange(e.target.value);
            }
            if (e.target.id === 'portSecurityEnabled') {
                this.togglePortSecurity(e.target.checked);
            }
        });
    }

    handleIPModeChange(mode) {
        const staticSection = document.getElementById('staticIpSection');
        const ipInput = document.getElementById('deviceIP');
        const subnetSelect = document.getElementById('subnetMask');
        const gatewayInput = document.getElementById('defaultGateway');
        
        if (mode === 'static') {
            staticSection.style.display = 'block';
            ipInput.disabled = false;
            subnetSelect.disabled = false;
            gatewayInput.disabled = false;
        } else if (mode === 'dhcp') {
            staticSection.style.display = 'none';
            ipInput.disabled = true;
            subnetSelect.disabled = true;
            gatewayInput.disabled = true;
            // Show DHCP status
            this.showDHCPStatus();
        } else if (mode === 'auto') {
            staticSection.style.display = 'block';
            ipInput.disabled = true;
            subnetSelect.disabled = true;
            gatewayInput.disabled = true;
            // Auto-configure with link-local address
            this.configureAutoIP();
        }
    }

    handleRoutingProtocolChange(protocol) {
        const ospfArea = document.getElementById('ospfArea');
        ospfArea.disabled = protocol !== 'ospf';
        if (protocol === 'ospf') {
            ospfArea.value = '0.0.0.0';
        }
    }

    togglePortSecurity(enabled) {
        const maxMacInput = document.getElementById('maxMacAddresses');
        const violationSelect = document.getElementById('violationAction');
        
        maxMacInput.disabled = !enabled;
        violationSelect.disabled = !enabled;
    }

    showDHCPStatus() {
        // Simulate DHCP status
        setTimeout(() => {
            alert('DHCP Status: Lease obtained\nIP: 192.168.1.100\nSubnet: 255.255.255.0\nGateway: 192.168.1.1\nDNS: 192.168.1.1');
        }, 500);
    }

    configureAutoIP() {
        // Configure link-local address
        document.getElementById('deviceIP').value = '169.254.' + Math.floor(Math.random() * 255) + '.' + Math.floor(Math.random() * 255);
        document.getElementById('subnetMask').value = '255.255.0.0';
        document.getElementById('defaultGateway').value = '';
    }

    switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(tabName + 'Tab').classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    }

    openConfigModal(device) {
        this.currentDevice = device;
        
        // Populate device information
        document.getElementById('configDeviceName').textContent = device.label || device.name || 'Unknown Device';
        document.getElementById('configDeviceType').textContent = device.type || 'Unknown';
        document.getElementById('deviceModel').textContent = device.model || this.getDeviceModel(device.type);
        document.getElementById('deviceMAC').textContent = device.macAddress || this.generateMacAddress();
        document.getElementById('deviceUptime').textContent = this.getDeviceUptime();
        document.getElementById('deviceConnections').textContent = this.getConnectionCount(device);
        document.getElementById('deviceOS').textContent = this.getDeviceOS(device.type);
        
        // Update device status
        const statusElement = document.getElementById('deviceStatus');
        const isOnline = device.status !== 'offline';
        statusElement.textContent = isOnline ? 'Online' : 'Offline';
        statusElement.className = `status-indicator ${isOnline ? '' : 'offline'}`;
        
        // Load existing configuration
        this.loadDeviceConfig(device);
        
        // Initialize dynamic content
        this.updateInterfaceOptions(device);
        this.updateConnectionQuality(device);
        this.startMonitoringUpdates();
        
        // Show modal (ensure we don't accidentally stack another)
        const modal = document.getElementById('ipConfigModal');
        if (!modal) return; // Safety check
        modal.style.display = 'flex';
    }

    closeConfigModal() {
        // Clear monitoring interval when closing modal
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
        
        document.getElementById('ipConfigModal').style.display = 'none';
        this.currentDevice = null;
    }

    loadDeviceConfig(device) {
        const config = this.networkConfigs.get(device.id) || {};
        
        // Populate basic configuration
        document.getElementById('deviceIP').value = config.ipAddress || '';
        document.getElementById('subnetMask').value = config.subnetMask || '255.255.255.0';
        document.getElementById('defaultGateway').value = config.gateway || '';
        document.getElementById('dnsServer').value = config.dns || '';
        
        // Populate advanced configuration
        document.getElementById('vlanId').value = config.vlanId || '';
        document.getElementById('interfaceConfig').value = config.interfaceConfig || '';
        
        if (config.routingProtocol) {
            const radioBtn = document.querySelector(`input[name="routing"][value="${config.routingProtocol}"]`);
            if (radioBtn) radioBtn.checked = true;
        }
    }

    applyConfiguration() {
        const config = this.gatherConfiguration();
        
        if (this.validateConfig(config)) {
            // Store configuration
            this.networkConfigs.set(this.currentDevice.id, config);
            
            // Update device display
            this.updateDeviceDisplay(this.currentDevice, config);
            
            // Close modal
            this.closeConfigModal();
            
            // Trigger re-validation of network
            this.validateNetworkConfiguration();
            
            console.log('Configuration applied:', config);
        }
    }

    gatherConfiguration() {
        return {
            ipAddress: document.getElementById('deviceIP').value,
            subnetMask: document.getElementById('subnetMask').value,
            gateway: document.getElementById('defaultGateway').value,
            dns: document.getElementById('dnsServer').value,
            vlanId: document.getElementById('vlanId').value,
            interfaceConfig: document.getElementById('interfaceConfig').value,
            routingProtocol: document.querySelector('input[name="routing"]:checked')?.value || 'none'
        };
    }

    validateConfig(config) {
        const errors = [];
        
        // Validate IP address
        if (!this.isValidIP(config.ipAddress)) {
            errors.push('Invalid IP address format');
        }
        
        // Validate gateway (if provided)
        if (config.gateway && !this.isValidIP(config.gateway)) {
            errors.push('Invalid gateway IP address');
        }
        
        // Validate DNS (if provided)
        if (config.dns && !this.isValidIP(config.dns)) {
            errors.push('Invalid DNS server IP address');
        }
        
        // Check for IP conflicts
        if (this.hasIPConflict(config.ipAddress)) {
            errors.push('IP address already in use');
        }
        
        if (errors.length > 0) {
            alert('Configuration errors:\n' + errors.join('\n'));
            return false;
        }
        
        return true;
    }

    validateConfiguration() {
        const config = this.gatherConfiguration();
        const results = this.performValidation(config);
        
        // Display validation results
        this.displayValidationResults(results);
        
        // Switch to validation tab
        this.switchTab('validation');
    }

    performValidation(config) {
        const results = {
            errors: [],
            warnings: [],
            suggestions: [],
            summary: {}
        };
        
        // IP format validation
        if (!this.isValidIP(config.ipAddress)) {
            results.errors.push('Invalid IP address format');
        } else {
            results.summary.ipAddress = config.ipAddress;
        }
        
        // Subnet analysis
        if (config.ipAddress && config.subnetMask) {
            const networkInfo = this.calculateNetworkInfo(config.ipAddress, config.subnetMask);
            results.summary.network = networkInfo;
            
            // Check if IP is in correct subnet range
            if (!this.isIPInSubnet(config.ipAddress, networkInfo.network, config.subnetMask)) {
                results.errors.push('IP address is not in the specified subnet range');
            }
        }
        
        // Gateway validation
        if (config.gateway) {
            if (!this.isValidIP(config.gateway)) {
                results.errors.push('Invalid gateway IP address');
            } else if (!this.isIPInSubnet(config.gateway, config.ipAddress, config.subnetMask)) {
                results.warnings.push('Gateway should typically be in the same subnet');
            }
        }
        
        // Device-specific recommendations
        if (this.currentDevice.type === 'router') {
            if (!config.routingProtocol || config.routingProtocol === 'none') {
                results.suggestions.push('Consider configuring a routing protocol for routers');
            }
        }
        
        if (this.currentDevice.type === 'pc' && !config.gateway) {
            results.suggestions.push('PCs typically need a default gateway for network communication');
        }
        
        return results;
    }

    displayValidationResults(results) {
        const container = document.getElementById('validationResults');
        const summaryContainer = document.getElementById('networkSummary');
        
        let html = '';
        
        // Display errors
        if (results.errors.length > 0) {
            html += '<div class="validation-section"><h5>Errors:</h5>';
            results.errors.forEach(error => {
                html += `<div class="validation-error">❌ ${error}</div>`;
            });
            html += '</div>';
        }
        
        // Display warnings
        if (results.warnings.length > 0) {
            html += '<div class="validation-section"><h5>Warnings:</h5>';
            results.warnings.forEach(warning => {
                html += `<div class="validation-warning">⚠️ ${warning}</div>`;
            });
            html += '</div>';
        }
        
        // Display suggestions
        if (results.suggestions.length > 0) {
            html += '<div class="validation-section"><h5>Suggestions:</h5>';
            results.suggestions.forEach(suggestion => {
                html += `<div class="validation-info">💡 ${suggestion}</div>`;
            });
            html += '</div>';
        }
        
        if (results.errors.length === 0) {
            html += '<div class="validation-success">✅ Configuration is valid!</div>';
        }
        
        container.innerHTML = html;
        
        // Display network summary
        let summaryHTML = '';
        if (results.summary.network) {
            const net = results.summary.network;
            summaryHTML = `
                <div><strong>Network:</strong> ${net.network}</div>
                <div><strong>Broadcast:</strong> ${net.broadcast}</div>
                <div><strong>Available IPs:</strong> ${net.availableIPs}</div>
                <div><strong>Subnet Size:</strong> /${net.cidr}</div>
            `;
        }
        summaryContainer.innerHTML = summaryHTML;
    }

    // Utility functions
    isValidIP(ip) {
        if (!ip) return false;
        const regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return regex.test(ip);
    }

    validateIPFormat(ip) {
        const isValid = this.isValidIP(ip);
        const input = document.getElementById('deviceIP');
        
        if (ip && !isValid) {
            input.style.borderColor = '#dc3545';
        } else {
            input.style.borderColor = '#666';
        }
    }

    hasIPConflict(ip) {
        if (!ip) return false;
        
        for (const [deviceId, config] of this.networkConfigs) {
            if (deviceId !== this.currentDevice.id && config.ipAddress === ip) {
                return true;
            }
        }
        return false;
    }

    calculateNetworkInfo(ip, mask) {
        const ipNum = this.ipToNumber(ip);
        const maskNum = this.ipToNumber(mask);
        const networkNum = ipNum & maskNum;
        const broadcastNum = networkNum | (~maskNum >>> 0);
        
        return {
            network: this.numberToIP(networkNum),
            broadcast: this.numberToIP(broadcastNum),
            availableIPs: (broadcastNum - networkNum - 1),
            cidr: this.maskToCIDR(mask)
        };
    }

    isIPInSubnet(ip, subnet, mask) {
        const ipNum = this.ipToNumber(ip);
        const subnetNum = this.ipToNumber(subnet);
        const maskNum = this.ipToNumber(mask);
        
        return (ipNum & maskNum) === (subnetNum & maskNum);
    }

    ipToNumber(ip) {
        return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet), 0) >>> 0;
    }

    numberToIP(num) {
        return [(num >>> 24) & 255, (num >>> 16) & 255, (num >>> 8) & 255, num & 255].join('.');
    }

    maskToCIDR(mask) {
        const maskNum = this.ipToNumber(mask);
        return (maskNum >>> 0).toString(2).split('1').length - 1;
    }

    updateDeviceDisplay(device, config) {
        // Add visual indicator that device is configured
        if (device.element) {
            device.element.classList.add('configured');
            
            // Add IP address label
            const label = device.element.querySelector('.ip-label') || 
                         document.createElement('div');
            label.className = 'ip-label';
            label.textContent = config.ipAddress;
            
            if (!device.element.querySelector('.ip-label')) {
                device.element.appendChild(label);
            }
        }
        
        // Store configuration in device object
        device.ipConfig = config;
    }

    validateNetworkConfiguration() {
        // Validate entire network topology for consistency
        const issues = [];
        const configs = Array.from(this.networkConfigs.values());
        
        // Check for IP conflicts
        const ips = configs.map(c => c.ipAddress).filter(Boolean);
        const uniqueIPs = new Set(ips);
        if (ips.length !== uniqueIPs.size) {
            issues.push('Duplicate IP addresses detected');
        }
        
        // Check subnet consistency
        const subnets = new Set(configs.map(c => c.subnetMask));
        if (subnets.size > 1) {
            issues.push('Multiple subnet masks detected - verify network design');
        }
        
        // Display validation summary
        this.displayNetworkValidationSummary(issues);
        
        return issues.length === 0;
    }

    displayNetworkValidationSummary(issues) {
        // Create or update validation summary display
        let summaryElement = document.getElementById('networkValidationSummary');
        
        if (!summaryElement) {
            summaryElement = document.createElement('div');
            summaryElement.id = 'networkValidationSummary';
            summaryElement.className = 'network-validation-summary';
            
            // Add to topology interface
            const topologyContainer = document.querySelector('.topology-container') || 
                                    document.querySelector('#canvas').parentElement;
            if (topologyContainer) {
                topologyContainer.appendChild(summaryElement);
            }
        }
        
        let html = '<h4>Network Validation</h4>';
        
        if (issues.length === 0) {
            html += '<div class="validation-success">✅ Network configuration is valid</div>';
        } else {
            html += '<div class="validation-errors">';
            issues.forEach(issue => {
                html += `<div class="validation-error">❌ ${issue}</div>`;
            });
            html += '</div>';
        }
        
        summaryElement.innerHTML = html;
    }

    // Export configuration for saving/loading
    exportConfiguration() {
        const configs = {};
        for (const [deviceId, config] of this.networkConfigs) {
            configs[deviceId] = config;
        }
        return configs;
    }

    importConfiguration(configs) {
        this.networkConfigs.clear();
        for (const [deviceId, config] of Object.entries(configs)) {
            this.networkConfigs.set(deviceId, config);
        }
    }

    // Generate configuration commands (for Cisco-style output)
    generateConfigCommands(device) {
        const config = this.networkConfigs.get(device.id);
        if (!config) return '';
        
        let commands = [];
        
        if (device.type === 'router') {
            commands.push('configure terminal');
            commands.push('interface GigabitEthernet0/0');
            commands.push(`ip address ${config.ipAddress} ${config.subnetMask}`);
            commands.push('no shutdown');
            
            if (config.routingProtocol && config.routingProtocol !== 'none') {
                commands.push(`router ${config.routingProtocol}`);
                if (config.routingProtocol === 'ospf') {
                    commands.push('network 0.0.0.0 255.255.255.255 area 0');
                }
            }
        } else if (device.type === 'switch') {
            commands.push('configure terminal');
            commands.push('interface vlan1');
            commands.push(`ip address ${config.ipAddress} ${config.subnetMask}`);
            commands.push('no shutdown');
            
            if (config.vlanId && config.vlanId !== '1') {
                commands.push(`vlan ${config.vlanId}`);
                commands.push('exit');
            }
        }
        
        commands.push('exit');
        return commands.join('\n');
    }

    // New utility functions for enhanced features
    getDeviceModel(type) {
        const models = {
            'router': 'Cisco ISR 4331',
            'switch': 'Cisco Catalyst 2960',
            'pc': 'Generic Workstation',
            'server': 'Dell PowerEdge R740',
            'firewall': 'Cisco ASA 5516-X',
            'ap': 'Cisco Aironet 9120AX'
        };
        return models[type] || 'Generic Device';
    }

    generateMacAddress() {
        const hexChars = '0123456789ABCDEF';
        let mac = '';
        for (let i = 0; i < 6; i++) {
            if (i > 0) mac += ':';
            mac += hexChars[Math.floor(Math.random() * 16)];
            mac += hexChars[Math.floor(Math.random() * 16)];
        }
        return mac;
    }

    getDeviceUptime() {
        const hours = Math.floor(Math.random() * 24);
        const minutes = Math.floor(Math.random() * 60);
        const seconds = Math.floor(Math.random() * 60);
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    getConnectionCount(device) {
        const count = Math.floor(Math.random() * 5);
        return `${count} active`;
    }

    getDeviceOS(type) {
        const os = {
            'router': 'Cisco IOS XE 16.12',
            'switch': 'Cisco IOS 15.2',
            'pc': 'Windows 11 Pro',
            'server': 'Ubuntu Server 22.04',
            'firewall': 'Cisco ASA OS 9.16',
            'ap': 'Cisco IOS XE 17.6'
        };
        return os[type] || 'Generic OS';
    }

    updateInterfaceOptions(device) {
        const interfaceSelect = document.getElementById('interfaceSelect');
        interfaceSelect.innerHTML = '';
        
        const interfaces = this.getDeviceInterfaces(device.type);
        interfaces.forEach(iface => {
            const option = document.createElement('option');
            option.value = iface.name;
            option.textContent = `${iface.description} (${iface.name})`;
            interfaceSelect.appendChild(option);
        });
    }

    getDeviceInterfaces(type) {
        const interfaces = {
            'router': [
                { name: 'GigabitEthernet0/0', description: 'GigabitEthernet 0/0' },
                { name: 'GigabitEthernet0/1', description: 'GigabitEthernet 0/1' },
                { name: 'Serial0/0/0', description: 'Serial 0/0/0' },
                { name: 'Loopback0', description: 'Loopback 0' }
            ],
            'switch': [
                { name: 'FastEthernet0/1', description: 'FastEthernet 0/1' },
                { name: 'FastEthernet0/2', description: 'FastEthernet 0/2' },
                { name: 'GigabitEthernet0/1', description: 'GigabitEthernet 0/1' },
                { name: 'Vlan1', description: 'VLAN 1' }
            ],
            'pc': [
                { name: 'eth0', description: 'Ethernet 0' },
                { name: 'wifi0', description: 'WiFi Adapter' },
                { name: 'lo', description: 'Loopback' }
            ]
        };
        return interfaces[type] || [{ name: 'eth0', description: 'Ethernet 0' }];
    }

    updateConnectionQuality(device) {
        // Update signal strength randomly for demo
        const signalBars = document.querySelectorAll('.signal-bar');
        const strength = Math.floor(Math.random() * 5) + 1;
        
        signalBars.forEach((bar, index) => {
            if (index < strength) {
                bar.classList.add('active');
            } else {
                bar.classList.remove('active');
            }
        });

        // Update link speed and duplex
        const speeds = ['10 Mbps', '100 Mbps', '1000 Mbps', '10 Gbps'];
        document.getElementById('linkSpeed').textContent = speeds[Math.floor(Math.random() * speeds.length)];
        document.getElementById('duplexMode').textContent = Math.random() > 0.1 ? 'Full' : 'Half';
    }

    startMonitoringUpdates() {
        // Clear any existing interval
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }

        // Update monitoring data every 2 seconds
        this.monitoringInterval = setInterval(() => {
            this.updateMonitoringData();
        }, 2000);
    }

    updateMonitoringData() {
        // Update random statistics for demonstration
        const bytesIn = Math.floor(Math.random() * 1000);
        const bytesOut = Math.floor(Math.random() * 800);
        const packetsIn = Math.floor(Math.random() * 5000);
        const packetsOut = Math.floor(Math.random() * 4000);

        if (document.getElementById('bytesIn')) {
            document.getElementById('bytesIn').textContent = `${bytesIn} MB`;
            document.getElementById('bytesOut').textContent = `${bytesOut} MB`;
            document.getElementById('packetsIn').textContent = packetsIn.toLocaleString();
            document.getElementById('packetsOut').textContent = packetsOut.toLocaleString();
        }

        // Update performance metrics
        const latency = (Math.random() * 5).toFixed(1);
        const packetLoss = (Math.random() * 2).toFixed(1);
        const throughput = Math.floor(Math.random() * 1000);
        const jitter = (Math.random() * 0.5).toFixed(2);

        if (document.getElementById('latencyValue')) {
            document.getElementById('latencyValue').textContent = `${latency}ms`;
            document.getElementById('packetLossValue').textContent = `${packetLoss}%`;
            document.getElementById('throughputValue').textContent = `${throughput} Mbps`;
            document.getElementById('jitterValue').textContent = `${jitter}ms`;
        }
    }

    // DNS preset functions
    setDNS(provider) {
        const dnsInput = document.getElementById('dnsServer');
        const presets = {
            'google': '8.8.8.8, 8.8.4.4',
            'cloudflare': '1.1.1.1, 1.0.0.1',
            'opendns': '208.67.222.222, 208.67.220.220'
        };
        dnsInput.value = presets[provider] || '';
    }

    // IP suggestion function
    suggestIP() {
        const subnetMask = document.getElementById('subnetMask').value;
        const gateway = document.getElementById('defaultGateway').value;
        
        let suggestedIP;
        if (gateway) {
            // Suggest IP in same subnet as gateway
            const gatewayParts = gateway.split('.');
            suggestedIP = `${gatewayParts[0]}.${gatewayParts[1]}.${gatewayParts[2]}.${Math.floor(Math.random() * 50) + 10}`;
        } else {
            // Suggest common private IP ranges
            const ranges = ['192.168.1', '192.168.0', '10.0.0', '172.16.0'];
            const selectedRange = ranges[Math.floor(Math.random() * ranges.length)];
            suggestedIP = `${selectedRange}.${Math.floor(Math.random() * 50) + 10}`;
        }
        
        document.getElementById('deviceIP').value = suggestedIP;
    }

    detectGateway() {
        // Simulate gateway detection
        const commonGateways = ['192.168.1.1', '192.168.0.1', '10.0.0.1', '172.16.0.1'];
        const detectedGateway = commonGateways[Math.floor(Math.random() * commonGateways.length)];
        document.getElementById('defaultGateway').value = detectedGateway;
    }

    // Testing functions
    pingTest() {
        const targetIP = document.getElementById('deviceIP').value || '8.8.8.8';
        
        // Validate IP address format
        const ipRegex = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (!ipRegex.test(targetIP)) {
            this.displayTestResult('ping', `Invalid IP address format: ${targetIP}`);
            return;
        }
        
        // Simulate more realistic ping behavior
        let result = `Pinging ${targetIP}...\n`;
        let success = true;
        
        // Check if it's a local/known address
        if (['192.168.1.1', '192.168.0.1', '10.0.0.1'].includes(targetIP)) {
            result += `Reply from ${targetIP}: bytes=32 time=1ms TTL=64\n`;
            result += `Reply from ${targetIP}: bytes=32 time=2ms TTL=64\n`;
            result += `Reply from ${targetIP}: bytes=32 time=1ms TTL=64\n`;
            result += `Reply from ${targetIP}: bytes=32 time=1ms TTL=64\n\n`;
            result += `Ping statistics for ${targetIP}:\n`;
            result += `    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)\n`;
            result += `Approximate round trip times: Minimum = 1ms, Maximum = 2ms, Average = 1ms`;
        } else if (['8.8.8.8', '1.1.1.1', '208.67.222.222'].includes(targetIP)) {
            const latency = Math.floor(Math.random() * 20) + 15; // 15-35ms for external
            result += `Reply from ${targetIP}: bytes=32 time=${latency}ms TTL=64\n`;
            result += `Reply from ${targetIP}: bytes=32 time=${latency+2}ms TTL=64\n`;
            result += `Reply from ${targetIP}: bytes=32 time=${latency-1}ms TTL=64\n`;
            result += `Reply from ${targetIP}: bytes=32 time=${latency+1}ms TTL=64\n\n`;
            result += `Ping statistics for ${targetIP}:\n`;
            result += `    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)\n`;
            result += `Approximate round trip times: Minimum = ${latency-1}ms, Maximum = ${latency+2}ms, Average = ${latency}ms`;
        } else {
            // Unknown address - simulate failure
            result += `Request timed out.\n`;
            result += `Request timed out.\n`;
            result += `Request timed out.\n`;
            result += `Request timed out.\n\n`;
            result += `Ping statistics for ${targetIP}:\n`;
            result += `    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)`;
            success = false;
        }
        
        this.displayTestResult('ping', result);
    }

    dnsTest() {
        this.displayTestResult('dns', 'DNS resolution test... Success! DNS servers responding normally');
    }

    connectivityTest() {
        this.displayTestResult('connectivity', 'Running full connectivity test...\n✓ Network interface: UP\n✓ IP configuration: Valid\n✓ Gateway reachable\n✓ DNS resolution: Working\n✓ Internet access: Available');
    }

    displayTestResult(testType, result) {
        const resultsContainer = document.getElementById('validationResults');
        const testResult = document.createElement('div');
        testResult.className = 'test-result';
        testResult.innerHTML = `<strong>${testType.toUpperCase()} Test:</strong><br><pre>${result}</pre>`;
        resultsContainer.appendChild(testResult);
    }

    // Troubleshooting functions
    routeTrace() {
        this.displayTestResult('traceroute', 'Traceroute to 8.8.8.8:\n1. 192.168.1.1 (2ms)\n2. 10.0.0.1 (15ms)\n3. 203.0.113.1 (25ms)\n4. 8.8.8.8 (30ms)');
    }

    arpTable() {
        this.displayTestResult('arp', 'ARP Table:\nIP Address       MAC Address       Interface\n192.168.1.1      00:1A:2B:3C:4D:5E  eth0\n192.168.1.100    00:AA:BB:CC:DD:EE  eth0');
    }

    interfaceStats() {
        this.displayTestResult('interface', 'Interface Statistics:\nPackets In: 15,432\nPackets Out: 12,876\nBytes In: 2.4 MB\nBytes Out: 1.8 MB\nErrors: 0\nDropped: 0');
    }

    portScan() {
        this.displayTestResult('portscan', 'Port Scan Results:\nPort 22 (SSH): Closed\nPort 80 (HTTP): Open\nPort 443 (HTTPS): Open\nPort 3389 (RDP): Filtered');
    }

    // Security functions
    togglePassword() {
        const passwordInput = document.getElementById('accessPassword');
        const toggleBtn = document.querySelector('.toggle-password');
        
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleBtn.textContent = '🙈';
        } else {
            passwordInput.type = 'password';
            toggleBtn.textContent = '👁️';
        }
    }

    addFirewallRule() {
        // This would open a dialog to add new firewall rules
        const protocol = prompt('Protocol (TCP/UDP/ICMP):') || 'TCP';
        const port = prompt('Port number:') || '80';
        const action = confirm('Allow this traffic?') ? 'ALLOW' : 'DENY';
        
        if (protocol && port) {
            const rulesContainer = document.querySelector('.firewall-rules');
            const ruleItem = document.createElement('div');
            ruleItem.className = 'rule-item';
            ruleItem.innerHTML = `
                <span class="rule-action ${action.toLowerCase()}">${action}</span>
                <span class="rule-protocol">${protocol}</span>
                <span class="rule-port">${port}</span>
                <span class="rule-source">Any</span>
                <button class="rule-delete" onclick="this.parentElement.remove()">❌</button>
            `;
            rulesContainer.appendChild(ruleItem);
        }
    }

    addMacAddress() {
        const macInput = document.getElementById('newMacAddress');
        const macAddress = macInput.value;
        
        if (this.isValidMacAddress(macAddress)) {
            const macList = document.querySelector('.mac-list');
            const macItem = document.createElement('div');
            macItem.className = 'mac-item';
            macItem.innerHTML = `
                <span>${macAddress}</span>
                <button onclick="this.parentElement.remove()">Remove</button>
            `;
            macList.appendChild(macItem);
            macInput.value = '';
        } else {
            alert('Invalid MAC address format');
        }
    }

    isValidMacAddress(mac) {
        const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
        return macRegex.test(mac);
    }

    closeConfigModal() {
        // Clear monitoring interval when closing modal
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
        
        document.getElementById('ipConfigModal').style.display = 'none';
        this.currentDevice = null;
    }
}

// Initialize IP Configuration Manager
const ipManager = new IPConfigurationManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IPConfigurationManager;
}
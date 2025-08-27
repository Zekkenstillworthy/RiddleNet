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
        const modalHTML = `
        <div id="ipConfigModal" class="ip-config-modal" style="display: none;">
            <div class="ip-config-content">
                <div class="ip-config-header">
                    <h3>IP Configuration</h3>
                    <button class="close-btn" onclick="ipManager.closeConfigModal()">&times;</button>
                </div>
                
                <div class="ip-config-body">
                    <div class="device-info">
                        <h4 id="configDeviceName">Device Name</h4>
                        <p id="configDeviceType">Device Type</p>
                    </div>
                    
                    <div class="interface-tabs">
                        <button class="tab-btn active" data-tab="basic">Basic Config</button>
                        <button class="tab-btn" data-tab="advanced">Advanced</button>
                        <button class="tab-btn" data-tab="validation">Validation</button>
                    </div>
                    
                    <div id="basicTab" class="tab-content active">
                        <div class="config-section">
                            <label for="deviceIP">IP Address:</label>
                            <input type="text" id="deviceIP" placeholder="192.168.1.1" 
                                   pattern="^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$">
                            <div class="ip-helper">
                                <span class="helper-text">Format: xxx.xxx.xxx.xxx</span>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <label for="subnetMask">Subnet Mask:</label>
                            <select id="subnetMask">
                                <option value="255.255.255.0">/24 - 255.255.255.0</option>
                                <option value="255.255.255.128">/25 - 255.255.255.128</option>
                                <option value="255.255.255.192">/26 - 255.255.255.192</option>
                                <option value="255.255.255.224">/27 - 255.255.255.224</option>
                                <option value="255.255.255.240">/28 - 255.255.255.240</option>
                                <option value="255.255.255.248">/29 - 255.255.255.248</option>
                                <option value="255.255.255.252">/30 - 255.255.255.252</option>
                            </select>
                        </div>
                        
                        <div class="config-section">
                            <label for="defaultGateway">Default Gateway:</label>
                            <input type="text" id="defaultGateway" placeholder="192.168.1.254">
                        </div>
                        
                        <div class="config-section">
                            <label for="dnsServer">DNS Server:</label>
                            <input type="text" id="dnsServer" placeholder="8.8.8.8">
                        </div>
                    </div>
                    
                    <div id="advancedTab" class="tab-content">
                        <div class="config-section">
                            <label for="vlanId">VLAN ID:</label>
                            <input type="number" id="vlanId" min="1" max="4094" placeholder="1">
                        </div>
                        
                        <div class="config-section">
                            <label for="interfaceConfig">Interface Configuration:</label>
                            <textarea id="interfaceConfig" rows="4" 
                                      placeholder="Additional interface commands..."></textarea>
                        </div>
                        
                        <div class="config-section">
                            <label>Routing Protocol:</label>
                            <div class="protocol-options">
                                <label><input type="radio" name="routing" value="static"> Static</label>
                                <label><input type="radio" name="routing" value="rip"> RIP</label>
                                <label><input type="radio" name="routing" value="ospf"> OSPF</label>
                                <label><input type="radio" name="routing" value="eigrp"> EIGRP</label>
                            </div>
                        </div>
                    </div>
                    
                    <div id="validationTab" class="tab-content">
                        <div class="validation-results">
                            <h4>Configuration Validation</h4>
                            <div id="validationResults"></div>
                        </div>
                        
                        <div class="network-summary">
                            <h4>Network Summary</h4>
                            <div id="networkSummary"></div>
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
        const styles = `
        <style>
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
        
        .device-info h4 {
            margin: 0 0 5px 0;
            color: #00d4ff;
        }
        
        .device-info p {
            margin: 0;
            color: #ccc;
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
        document.getElementById('configDeviceType').textContent = `Type: ${device.type || 'Unknown'}`;
        
        // Load existing configuration
        this.loadDeviceConfig(device);
        
        // Show modal
        document.getElementById('ipConfigModal').style.display = 'flex';
    }

    closeConfigModal() {
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
}

// Initialize IP Configuration Manager
const ipManager = new IPConfigurationManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IPConfigurationManager;
}
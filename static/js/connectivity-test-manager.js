/**
 * Enhanced Connectivity Testing System
 * Provides realistic network connectivity testing with ping, trace route, and route validation
 */

class ConnectivityTestManager {
    constructor() {
        this.testResults = new Map();
        this.testHistory = [];
        this.isTestingInProgress = false;
        
        this.testTypes = {
            PING: 'ping',
            TRACEROUTE: 'traceroute',
            ROUTE_TABLE: 'route_table',
            ARP_TABLE: 'arp_table',
            DNS_LOOKUP: 'dns_lookup'
        };
        
        this.initializeTestManager();
    }

    initializeTestManager() {
        this.createTestInterface();
        this.attachEventListeners();
    }

    createTestInterface() {
        // Create connectivity test console
        const testConsole = document.createElement('div');
        testConsole.id = 'connectivity-test-console';
        testConsole.innerHTML = `
            <div class="test-console-header">
                <h4><i class="fas fa-terminal"></i> Network Testing Console</h4>
                <div class="console-controls">
                    <button id="clear-console" class="console-btn">
                        <i class="fas fa-eraser"></i> Clear
                    </button>
                    <button id="toggle-console" class="console-btn">
                        <i class="fas fa-window-minimize"></i>
                    </button>
                </div>
            </div>
            
            <div class="test-console-body">
                <div class="test-controls">
                    <div class="test-input-group">
                        <select id="test-source-device" class="test-select">
                            <option value="">Select source device...</option>
                        </select>
                        <select id="test-type" class="test-select">
                            <option value="ping">Ping</option>
                            <option value="traceroute">Trace Route</option>
                            <option value="route_table">Show Routes</option>
                            <option value="arp_table">Show ARP</option>
                            <option value="dns_lookup">DNS Lookup</option>
                        </select>
                        <input type="text" id="test-target" placeholder="Target IP or hostname" class="test-input">
                        <button id="run-test" class="test-run-btn">
                            <i class="fas fa-play"></i> Run
                        </button>
                    </div>
                    
                    <div class="quick-tests">
                        <button class="quick-test-btn" data-test="ping-all">
                            <i class="fas fa-broadcast-tower"></i> Ping All
                        </button>
                        <button class="quick-test-btn" data-test="connectivity-matrix">
                            <i class="fas fa-table"></i> Connectivity Matrix
                        </button>
                        <button class="quick-test-btn" data-test="route-validation">
                            <i class="fas fa-route"></i> Validate Routes
                        </button>
                    </div>
                </div>
                
                <div class="test-output">
                    <div class="output-header">
                        <span>Test Results</span>
                        <div class="output-stats">
                            <span id="test-stats">Ready</span>
                        </div>
                    </div>
                    <div class="output-content" id="test-output-content">
                        <div class="welcome-message">
                            <i class="fas fa-info-circle"></i>
                            Welcome to the Network Testing Console<br>
                            Select a source device and test type to begin testing network connectivity.
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add styles for the test console
        const styles = document.createElement('style');
        styles.textContent = `
            #connectivity-test-console {
                position: fixed;
                bottom: 120px;
                right: 20px;
                width: 480px;
                background: var(--surface);
                border: 1px solid var(--glass-border);
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-lg);
                z-index: 1000;
                color: var(--text-primary);
                max-height: 400px;
                overflow: hidden;
                transition: all 0.3s ease;
            }

            #connectivity-test-console.minimized {
                max-height: 60px;
            }

            .test-console-header {
                background: var(--glass-bg-light);
                padding: 12px 16px;
                border-bottom: 1px solid var(--glass-border);
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
            }

            .test-console-header h4 {
                margin: 0;
                font-size: 14px;
                font-weight: 600;
            }

            .console-controls {
                display: flex;
                gap: 8px;
            }

            .console-btn {
                background: none;
                border: none;
                color: var(--text-secondary);
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .console-btn:hover {
                background: var(--glass-bg-hover);
                color: var(--text-primary);
            }

            .test-console-body {
                padding: 16px;
                max-height: 340px;
                overflow-y: auto;
            }

            .test-controls {
                margin-bottom: 16px;
            }

            .test-input-group {
                display: grid;
                grid-template-columns: 1fr 120px 1fr 60px;
                gap: 8px;
                margin-bottom: 12px;
            }

            .test-select,
            .test-input {
                padding: 8px 10px;
                background: var(--background);
                border: 1px solid var(--glass-border);
                border-radius: 4px;
                color: var(--text-primary);
                font-size: 12px;
            }

            .test-run-btn {
                background: var(--success-color);
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease;
            }

            .test-run-btn:hover {
                background: var(--accent-color);
            }

            .test-run-btn:disabled {
                background: var(--text-muted);
                cursor: not-allowed;
            }

            .quick-tests {
                display: flex;
                gap: 8px;
            }

            .quick-test-btn {
                flex: 1;
                background: var(--glass-bg-light);
                border: 1px solid var(--glass-border);
                color: var(--text-primary);
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 11px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .quick-test-btn:hover {
                background: var(--accent-color);
                color: white;
            }

            .test-output {
                background: var(--background);
                border: 1px solid var(--glass-border);
                border-radius: 6px;
                overflow: hidden;
            }

            .output-header {
                background: var(--glass-bg-light);
                padding: 8px 12px;
                border-bottom: 1px solid var(--glass-border);
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 12px;
                font-weight: 600;
            }

            .output-stats {
                font-size: 11px;
                color: var(--text-secondary);
            }

            .output-content {
                padding: 12px;
                max-height: 200px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.4;
            }

            .welcome-message {
                text-align: center;
                color: var(--text-muted);
                padding: 20px;
                font-family: inherit;
            }

            .test-result {
                margin-bottom: 12px;
                padding: 8px;
                border-radius: 4px;
                border-left: 3px solid var(--accent-color);
            }

            .test-result.success {
                background: rgba(16, 185, 129, 0.1);
                border-left-color: var(--success-color);
            }

            .test-result.failed {
                background: rgba(239, 68, 68, 0.1);
                border-left-color: var(--danger-color);
            }

            .test-result.warning {
                background: rgba(245, 158, 11, 0.1);
                border-left-color: var(--warning-color);
            }

            .test-command {
                color: var(--cyber-glow);
                font-weight: bold;
                margin-bottom: 4px;
            }

            .test-timestamp {
                color: var(--text-muted);
                font-size: 10px;
                float: right;
            }

            .ping-line {
                margin: 2px 0;
            }

            .ping-success {
                color: var(--success-color);
            }

            .ping-timeout {
                color: var(--danger-color);
            }

            .route-entry {
                margin: 2px 0;
                color: var(--text-secondary);
            }

            .connectivity-matrix {
                margin-top: 8px;
            }

            .matrix-header {
                font-weight: bold;
                color: var(--accent-color);
                margin-bottom: 8px;
            }

            .matrix-row {
                margin: 4px 0;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .matrix-device {
                width: 80px;
                color: var(--text-primary);
                font-weight: 500;
            }

            .matrix-result {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                display: inline-block;
            }

            .matrix-result.success {
                background: var(--success-color);
            }

            .matrix-result.failed {
                background: var(--danger-color);
            }

            .matrix-result.pending {
                background: var(--text-muted);
            }
        `;

        document.head.appendChild(styles);
        document.body.appendChild(testConsole);

        // Initialize device list
        this.updateDeviceList();
    }

    updateDeviceList() {
        const sourceSelect = document.getElementById('test-source-device');
        if (!sourceSelect) return;

        sourceSelect.innerHTML = '<option value="">Select source device...</option>';

        if (window.editor && window.editor.devices) {
            window.editor.devices.forEach(device => {
                const config = window.deviceConfigurator?.getDeviceConfiguration(device.id);
                const hasConfig = config && config.ipAddress;
                
                const option = document.createElement('option');
                option.value = device.id;
                option.textContent = `${device.name || device.label} (${device.type})${hasConfig ? ' ✓' : ' ⚠'}`;
                option.disabled = !hasConfig;
                
                sourceSelect.appendChild(option);
            });
        }
    }

    async runTest() {
        const sourceDeviceId = document.getElementById('test-source-device').value;
        const testType = document.getElementById('test-type').value;
        const target = document.getElementById('test-target').value;

        if (!sourceDeviceId) {
            this.addOutput('Error: Please select a source device', 'failed');
            return;
        }

        const sourceDevice = window.editor?.devices?.find(d => d.id === sourceDeviceId);
        if (!sourceDevice) {
            this.addOutput('Error: Source device not found', 'failed');
            return;
        }

        const sourceConfig = window.deviceConfigurator?.getDeviceConfiguration(sourceDeviceId);
        if (!sourceConfig || !sourceConfig.ipAddress) {
            this.addOutput('Error: Source device not configured', 'failed');
            return;
        }

        this.isTestingInProgress = true;
        this.updateTestStats('Running test...');

        try {
            let result;
            switch (testType) {
                case 'ping':
                    result = await this.performPingTest(sourceDevice, sourceConfig, target);
                    break;
                case 'traceroute':
                    result = await this.performTracerouteTest(sourceDevice, sourceConfig, target);
                    break;
                case 'route_table':
                    result = await this.showRouteTable(sourceDevice, sourceConfig);
                    break;
                case 'arp_table':
                    result = await this.showArpTable(sourceDevice, sourceConfig);
                    break;
                case 'dns_lookup':
                    result = await this.performDnsLookup(sourceDevice, sourceConfig, target);
                    break;
                default:
                    result = { success: false, output: 'Unknown test type' };
            }

            this.addOutput(result.output, result.success ? 'success' : 'failed');
            this.recordTestResult(sourceDevice, testType, target, result);

        } catch (error) {
            this.addOutput(`Error: ${error.message}`, 'failed');
        } finally {
            this.isTestingInProgress = false;
            this.updateTestStats('Ready');
        }
    }

    async performPingTest(sourceDevice, sourceConfig, target) {
        const command = `ping ${target}`;
        
        if (!target) {
            return {
                success: false,
                output: `${command}\nError: Target address required`
            };
        }

        // Validate target format
        if (!this.isValidIPAddress(target) && !this.isValidHostname(target)) {
            return {
                success: false,
                output: `${command}\nError: Invalid target format`
            };
        }

        // Resolve target device if it's an IP address
        let targetDevice = null;
        let targetConfig = null;

        if (this.isValidIPAddress(target)) {
            // Find device with this IP
            for (const device of window.editor?.devices || []) {
                const config = window.deviceConfigurator?.getDeviceConfiguration(device.id);
                if (config && config.ipAddress === target) {
                    targetDevice = device;
                    targetConfig = config;
                    break;
                }
            }
        }

        if (!targetDevice) {
            return {
                success: false,
                output: `${command}\nPing request could not find host ${target}. Please check the name and try again.`
            };
        }

        // Check connectivity
        const connectivity = this.checkConnectivity(sourceDevice, sourceConfig, targetDevice, targetConfig);
        
        let output = `${command}\n\nPinging ${target}:\n\n`;
        
        if (connectivity.reachable) {
            // Simulate successful ping
            const latency = this.calculateLatency(sourceDevice, targetDevice);
            for (let i = 1; i <= 4; i++) {
                const variance = Math.floor(Math.random() * 10) - 5;
                const currentLatency = Math.max(1, latency + variance);
                output += `Reply from ${target}: bytes=32 time=${currentLatency}ms TTL=64\n`;
                
                // Add small delay between pings
                await new Promise(resolve => setTimeout(resolve, 200));
                this.updateLastOutputLine(output);
            }
            
            output += `\nPing statistics for ${target}:\n`;
            output += `    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)\n`;
            output += `Approximate round trip times in milli-seconds:\n`;
            output += `    Minimum = ${latency-2}ms, Maximum = ${latency+8}ms, Average = ${latency+2}ms`;
            
            return { success: true, output };
        } else {
            // Simulate failed ping
            for (let i = 1; i <= 4; i++) {
                output += `Request timed out.\n`;
                await new Promise(resolve => setTimeout(resolve, 300));
                this.updateLastOutputLine(output);
            }
            
            output += `\nPing statistics for ${target}:\n`;
            output += `    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)\n`;
            output += `\nReason: ${connectivity.reason}`;
            
            return { success: false, output };
        }
    }

    async performTracerouteTest(sourceDevice, sourceConfig, target) {
        const command = `tracert ${target}`;
        
        if (!target) {
            return {
                success: false,
                output: `${command}\nError: Target address required`
            };
        }

        let output = `${command}\n\nTracing route to ${target}:\n\n`;
        
        // Find target device
        let targetDevice = null;
        let targetConfig = null;

        if (this.isValidIPAddress(target)) {
            for (const device of window.editor?.devices || []) {
                const config = window.deviceConfigurator?.getDeviceConfiguration(device.id);
                if (config && config.ipAddress === target) {
                    targetDevice = device;
                    targetConfig = config;
                    break;
                }
            }
        }

        if (!targetDevice) {
            return {
                success: false,
                output: `${command}\nUnable to resolve target system name ${target}.`
            };
        }

        // Find path to target
        const path = this.findNetworkPath(sourceDevice, targetDevice);
        
        if (path.length === 0) {
            return {
                success: false,
                output: `${command}\nDestination host unreachable.`
            };
        }

        // Simulate traceroute hops
        let hopNumber = 1;
        let cumulativeLatency = 0;
        
        for (const hopDevice of path) {
            const hopConfig = window.deviceConfigurator?.getDeviceConfiguration(hopDevice.id);
            const hopLatency = Math.floor(Math.random() * 20) + 5;
            cumulativeLatency += hopLatency;
            
            if (hopConfig && hopConfig.ipAddress) {
                output += `  ${hopNumber}    ${cumulativeLatency}ms    ${cumulativeLatency+2}ms    ${cumulativeLatency+1}ms  ${hopConfig.ipAddress}\n`;
            } else {
                output += `  ${hopNumber}     *        *        *     Request timed out.\n`;
            }
            
            hopNumber++;
            await new Promise(resolve => setTimeout(resolve, 300));
            this.updateLastOutputLine(output);
        }
        
        output += `\nTrace complete.`;
        
        return { success: true, output };
    }

    async showRouteTable(sourceDevice, sourceConfig) {
        const command = `route print`;
        
        let output = `${command}\n\n`;
        output += `===========================================================================\n`;
        output += `Interface List\n`;
        output += `===========================================================================\n`;
        output += ` 0...........................Loopback\n`;
        output += ` 1...........................Ethernet0\n`;
        
        if (sourceDevice.type === 'router' && sourceConfig.routes) {
            output += `\n===========================================================================\n`;
            output += `IPv4 Route Table\n`;
            output += `===========================================================================\n`;
            output += `Active Routes:\n`;
            output += `Network Destination        Netmask          Gateway       Interface  Metric\n`;
            
            // Add default route if gateway exists
            if (sourceConfig.gateway) {
                output += `          0.0.0.0          0.0.0.0    ${sourceConfig.gateway}  ${sourceConfig.ipAddress}     1\n`;
            }
            
            // Add configured routes
            sourceConfig.routes.forEach(route => {
                const destination = route.destination || '0.0.0.0';
                const netmask = route.netmask || '0.0.0.0';
                const gateway = route.gateway || sourceConfig.gateway;
                const iface = sourceConfig.ipAddress;
                
                output += `        ${destination.padEnd(15)} ${netmask.padEnd(15)} ${gateway.padEnd(12)} ${iface.padEnd(10)}    1\n`;
            });
        } else {
            output += `\n===========================================================================\n`;
            output += `IPv4 Route Table\n`;
            output += `===========================================================================\n`;
            output += `Active Routes:\n`;
            output += `Network Destination        Netmask          Gateway       Interface  Metric\n`;
            
            if (sourceConfig.gateway) {
                output += `          0.0.0.0          0.0.0.0    ${sourceConfig.gateway}  ${sourceConfig.ipAddress}     1\n`;
            }
            
            // Add local network route
            const networkAddr = this.getNetworkAddress(sourceConfig.ipAddress, sourceConfig.subnetMask);
            output += `        ${networkAddr.padEnd(15)} ${sourceConfig.subnetMask.padEnd(15)} ${'On-link'.padEnd(12)} ${sourceConfig.ipAddress.padEnd(10)}    1\n`;
        }
        
        return { success: true, output };
    }

    async showArpTable(sourceDevice, sourceConfig) {
        const command = `arp -a`;
        
        let output = `${command}\n\n`;
        output += `Interface: ${sourceConfig.ipAddress}\n`;
        output += `  Internet Address      Physical Address      Type\n`;
        
        // Find connected devices on same subnet
        const sameSubnetDevices = this.findSameSubnetDevices(sourceDevice, sourceConfig);
        
        sameSubnetDevices.forEach(device => {
            const config = window.deviceConfigurator?.getDeviceConfiguration(device.id);
            if (config && config.ipAddress) {
                const macAddress = this.generateMacAddress(device.id);
                output += `  ${config.ipAddress.padEnd(20)} ${macAddress.padEnd(20)} dynamic\n`;
            }
        });
        
        if (sourceConfig.gateway) {
            const gatewayMac = this.generateMacAddress('gateway');
            output += `  ${sourceConfig.gateway.padEnd(20)} ${gatewayMac.padEnd(20)} dynamic\n`;
        }
        
        return { success: true, output };
    }

    async performDnsLookup(sourceDevice, sourceConfig, target) {
        const command = `nslookup ${target}`;
        
        if (!target) {
            return {
                success: false,
                output: `${command}\nError: Hostname required`
            };
        }

        let output = `${command}\n`;
        
        if (sourceConfig.dnsServer) {
            output += `Server:  ${sourceConfig.dnsServer}\n`;
            output += `Address: ${sourceConfig.dnsServer}\n\n`;
            
            // Simulate DNS lookup
            if (this.isValidHostname(target)) {
                const resolvedIP = this.simulateDnsResolution(target);
                if (resolvedIP) {
                    output += `Name:    ${target}\n`;
                    output += `Address: ${resolvedIP}\n`;
                    return { success: true, output };
                } else {
                    output += `*** ${sourceConfig.dnsServer} can't find ${target}: Non-existent domain\n`;
                    return { success: false, output };
                }
            } else {
                output += `*** Invalid hostname: ${target}\n`;
                return { success: false, output };
            }
        } else {
            output += `*** No DNS servers configured\n`;
            return { success: false, output };
        }
    }

    checkConnectivity(sourceDevice, sourceConfig, targetDevice, targetConfig) {
        // Check if devices are on the same subnet
        if (this.areOnSameSubnet(sourceConfig, targetConfig)) {
            // Check physical connectivity
            if (this.hasPhysicalPath(sourceDevice, targetDevice)) {
                return { reachable: true, reason: 'Direct connection' };
            } else {
                return { reachable: false, reason: 'No physical path' };
            }
        } else {
            // Check if both have gateways configured
            if (sourceConfig.gateway && targetConfig.gateway) {
                // Check if gateways are reachable
                const sourceGateway = this.findDeviceByIP(sourceConfig.gateway);
                const targetGateway = this.findDeviceByIP(targetConfig.gateway);
                
                if (sourceGateway && targetGateway) {
                    return { reachable: true, reason: 'Routed connection' };
                } else {
                    return { reachable: false, reason: 'Gateway unreachable' };
                }
            } else {
                return { reachable: false, reason: 'No gateway configured for inter-subnet communication' };
            }
        }
    }

    findNetworkPath(sourceDevice, targetDevice) {
        // Simple BFS to find path through network devices
        const visited = new Set();
        const queue = [[sourceDevice]];
        
        while (queue.length > 0) {
            const path = queue.shift();
            const currentDevice = path[path.length - 1];
            
            if (currentDevice.id === targetDevice.id) {
                return path;
            }
            
            if (visited.has(currentDevice.id)) continue;
            visited.add(currentDevice.id);
            
            // Find connected devices
            const connectedDevices = this.getConnectedDevices(currentDevice);
            
            for (const nextDevice of connectedDevices) {
                if (!visited.has(nextDevice.id)) {
                    queue.push([...path, nextDevice]);
                }
            }
        }
        
        return [];
    }

    getConnectedDevices(device) {
        const connectedDevices = [];
        
        if (window.editor && window.editor.connections) {
            window.editor.connections.forEach(connection => {
                let connectedDeviceId = null;
                
                if (connection.source === device.id) {
                    connectedDeviceId = connection.target;
                } else if (connection.target === device.id) {
                    connectedDeviceId = connection.source;
                }
                
                if (connectedDeviceId) {
                    const connectedDevice = window.editor.devices.find(d => d.id === connectedDeviceId);
                    if (connectedDevice) {
                        connectedDevices.push(connectedDevice);
                    }
                }
            });
        }
        
        return connectedDevices;
    }

    calculateLatency(sourceDevice, targetDevice) {
        // Base latency depends on device types and distance simulation
        let baseLatency = 1;
        
        // Add latency for each hop
        const path = this.findNetworkPath(sourceDevice, targetDevice);
        baseLatency += (path.length - 1) * 5;
        
        // Add random variance
        baseLatency += Math.floor(Math.random() * 10);
        
        return Math.max(1, baseLatency);
    }

    areOnSameSubnet(config1, config2) {
        if (!config1.ipAddress || !config2.ipAddress || !config1.subnetMask || !config2.subnetMask) {
            return false;
        }
        
        const network1 = this.getNetworkAddress(config1.ipAddress, config1.subnetMask);
        const network2 = this.getNetworkAddress(config2.ipAddress, config2.subnetMask);
        
        return network1 === network2 && config1.subnetMask === config2.subnetMask;
    }

    getNetworkAddress(ip, mask) {
        const ipNum = this.ipToNumber(ip);
        const maskNum = this.ipToNumber(mask);
        const networkNum = ipNum & maskNum;
        return this.numberToIp(networkNum);
    }

    ipToNumber(ip) {
        return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet), 0) >>> 0;
    }

    numberToIp(num) {
        return [(num >>> 24) & 255, (num >>> 16) & 255, (num >>> 8) & 255, num & 255].join('.');
    }

    hasPhysicalPath(sourceDevice, targetDevice) {
        // Use same logic as enhanced validator
        if (!window.editor || !window.editor.connections) return false;
        
        const graph = new Map();
        window.editor.devices.forEach(device => {
            graph.set(device.id, []);
        });
        
        window.editor.connections.forEach(connection => {
            graph.get(connection.source)?.push(connection.target);
            graph.get(connection.target)?.push(connection.source);
        });
        
        const queue = [sourceDevice.id];
        const visited = new Set([sourceDevice.id]);
        
        while (queue.length > 0) {
            const current = queue.shift();
            
            if (current === targetDevice.id) {
                return true;
            }
            
            const neighbors = graph.get(current) || [];
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }
        
        return false;
    }

    findSameSubnetDevices(sourceDevice, sourceConfig) {
        const devices = [];
        
        if (window.editor && window.editor.devices) {
            window.editor.devices.forEach(device => {
                if (device.id === sourceDevice.id) return;
                
                const config = window.deviceConfigurator?.getDeviceConfiguration(device.id);
                if (config && this.areOnSameSubnet(sourceConfig, config)) {
                    devices.push(device);
                }
            });
        }
        
        return devices;
    }

    findDeviceByIP(ipAddress) {
        if (!window.editor || !window.editor.devices) return null;
        
        for (const device of window.editor.devices) {
            const config = window.deviceConfigurator?.getDeviceConfiguration(device.id);
            if (config && config.ipAddress === ipAddress) {
                return device;
            }
        }
        
        return null;
    }

    generateMacAddress(deviceId) {
        // Generate a consistent MAC address based on device ID
        const hash = this.simpleHash(deviceId);
        const mac = [];
        
        for (let i = 0; i < 6; i++) {
            const byte = (hash >>> (i * 4)) & 0xFF;
            mac.push(byte.toString(16).padStart(2, '0').toUpperCase());
        }
        
        return mac.join('-');
    }

    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    }

    simulateDnsResolution(hostname) {
        // Simple hostname to IP simulation
        const commonHosts = {
            'google.com': '8.8.8.8',
            'cloudflare.com': '1.1.1.1',
            'localhost': '127.0.0.1',
            'router': '192.168.1.1',
            'server': '192.168.1.100'
        };
        
        return commonHosts[hostname.toLowerCase()] || null;
    }

    isValidIPAddress(ip) {
        const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipRegex.test(ip);
    }

    isValidHostname(hostname) {
        const hostnameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        return hostnameRegex.test(hostname);
    }

    addOutput(text, type = 'success') {
        const outputContent = document.getElementById('test-output-content');
        if (!outputContent) return;

        // Remove welcome message if present
        const welcomeMessage = outputContent.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const resultDiv = document.createElement('div');
        resultDiv.className = `test-result ${type}`;
        
        const timestamp = new Date().toLocaleTimeString();
        resultDiv.innerHTML = `
            <div class="test-timestamp">${timestamp}</div>
            <pre style="margin: 0; white-space: pre-wrap; font-family: inherit;">${text}</pre>
        `;

        outputContent.appendChild(resultDiv);
        outputContent.scrollTop = outputContent.scrollHeight;

        // Limit number of results to prevent memory issues
        const results = outputContent.querySelectorAll('.test-result');
        if (results.length > 20) {
            results[0].remove();
        }
    }

    updateLastOutputLine(text) {
        const outputContent = document.getElementById('test-output-content');
        if (!outputContent) return;

        const lastResult = outputContent.querySelector('.test-result:last-child pre');
        if (lastResult) {
            lastResult.textContent = text.split('\n')[0] + '\n' + text.split('\n').slice(1).join('\n');
        }
    }

    updateTestStats(status) {
        const statsElement = document.getElementById('test-stats');
        if (statsElement) {
            statsElement.textContent = status;
        }
    }

    recordTestResult(sourceDevice, testType, target, result) {
        const testRecord = {
            timestamp: new Date().toISOString(),
            sourceDevice: sourceDevice.name || sourceDevice.id,
            testType,
            target,
            success: result.success,
            output: result.output
        };

        this.testHistory.push(testRecord);
        
        // Keep only last 50 test results
        if (this.testHistory.length > 50) {
            this.testHistory.shift();
        }
    }

    // Quick test methods
    async runPingAllTest() {
        const devices = window.editor?.devices?.filter(d => {
            const config = window.deviceConfigurator?.getDeviceConfiguration(d.id);
            return config && config.ipAddress;
        }) || [];

        if (devices.length < 2) {
            this.addOutput('Ping All Test\nError: Need at least 2 configured devices', 'failed');
            return;
        }

        this.addOutput('=== PING ALL DEVICES TEST ===\nTesting connectivity between all configured devices...\n', 'success');

        for (let i = 0; i < devices.length; i++) {
            for (let j = i + 1; j < devices.length; j++) {
                const sourceDevice = devices[i];
                const targetDevice = devices[j];
                const sourceConfig = window.deviceConfigurator?.getDeviceConfiguration(sourceDevice.id);
                const targetConfig = window.deviceConfigurator?.getDeviceConfiguration(targetDevice.id);

                if (sourceConfig && targetConfig) {
                    const connectivity = this.checkConnectivity(sourceDevice, sourceConfig, targetDevice, targetConfig);
                    const status = connectivity.reachable ? '✓' : '✗';
                    const reason = connectivity.reachable ? 'Success' : connectivity.reason;

                    this.addOutput(
                        `${status} ${sourceDevice.name} (${sourceConfig.ipAddress}) → ${targetDevice.name} (${targetConfig.ipAddress}): ${reason}`,
                        connectivity.reachable ? 'success' : 'failed'
                    );
                }

                // Small delay to show progress
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }

        this.addOutput('=== PING ALL TEST COMPLETE ===', 'success');
    }

    async runConnectivityMatrix() {
        const devices = window.editor?.devices?.filter(d => {
            const config = window.deviceConfigurator?.getDeviceConfiguration(d.id);
            return config && config.ipAddress;
        }) || [];

        if (devices.length < 2) {
            this.addOutput('Connectivity Matrix\nError: Need at least 2 configured devices', 'failed');
            return;
        }

        let matrixOutput = '=== CONNECTIVITY MATRIX ===\n\n';
        matrixOutput += 'Legend: ✓ = Connected, ✗ = Not Connected\n\n';

        // Create matrix header
        matrixOutput += ''.padEnd(12);
        devices.forEach(device => {
            matrixOutput += (device.name || device.id).substring(0, 8).padEnd(10);
        });
        matrixOutput += '\n';

        // Create matrix rows
        for (const sourceDevice of devices) {
            const sourceConfig = window.deviceConfigurator?.getDeviceConfiguration(sourceDevice.id);
            matrixOutput += (sourceDevice.name || sourceDevice.id).substring(0, 10).padEnd(12);

            for (const targetDevice of devices) {
                if (sourceDevice.id === targetDevice.id) {
                    matrixOutput += '-'.padEnd(10);
                } else {
                    const targetConfig = window.deviceConfigurator?.getDeviceConfiguration(targetDevice.id);
                    const connectivity = this.checkConnectivity(sourceDevice, sourceConfig, targetDevice, targetConfig);
                    const symbol = connectivity.reachable ? '✓' : '✗';
                    matrixOutput += symbol.padEnd(10);
                }
            }
            matrixOutput += '\n';
        }

        this.addOutput(matrixOutput, 'success');
    }

    async runRouteValidation() {
        const routers = window.editor?.devices?.filter(d => d.type === 'router') || [];

        if (routers.length === 0) {
            this.addOutput('Route Validation\nNo routers found in topology', 'warning');
            return;
        }

        this.addOutput('=== ROUTE VALIDATION TEST ===\nValidating routing configuration...\n', 'success');

        for (const router of routers) {
            const config = window.deviceConfigurator?.getDeviceConfiguration(router.id);
            
            if (!config || !config.routes) {
                this.addOutput(`✗ ${router.name}: No routing table configured`, 'failed');
                continue;
            }

            if (config.routes.length === 0) {
                this.addOutput(`⚠ ${router.name}: Empty routing table`, 'warning');
                continue;
            }

            let validRoutes = 0;
            let totalRoutes = config.routes.length;

            for (const route of config.routes) {
                if (route.destination && route.gateway && route.interface) {
                    if (this.isValidIPAddress(route.destination) && this.isValidIPAddress(route.gateway)) {
                        validRoutes++;
                    }
                }
            }

            if (validRoutes === totalRoutes) {
                this.addOutput(`✓ ${router.name}: All ${totalRoutes} routes valid`, 'success');
            } else {
                this.addOutput(`⚠ ${router.name}: ${validRoutes}/${totalRoutes} routes valid`, 'warning');
            }
        }

        this.addOutput('=== ROUTE VALIDATION COMPLETE ===', 'success');
    }

    attachEventListeners() {
        // Update device list when devices change
        document.addEventListener('configurationUpdated', () => {
            this.updateDeviceList();
        });

        // Run test button
        document.getElementById('run-test')?.addEventListener('click', () => {
            if (!this.isTestingInProgress) {
                this.runTest();
            }
        });

        // Quick test buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.quick-test-btn')) {
                const testType = e.target.closest('.quick-test-btn').dataset.test;
                
                if (!this.isTestingInProgress) {
                    switch (testType) {
                        case 'ping-all':
                            this.runPingAllTest();
                            break;
                        case 'connectivity-matrix':
                            this.runConnectivityMatrix();
                            break;
                        case 'route-validation':
                            this.runRouteValidation();
                            break;
                    }
                }
            }
        });

        // Console controls
        document.getElementById('clear-console')?.addEventListener('click', () => {
            const outputContent = document.getElementById('test-output-content');
            if (outputContent) {
                outputContent.innerHTML = '<div class="welcome-message"><i class="fas fa-info-circle"></i>Console cleared. Ready for new tests.</div>';
            }
        });

        document.getElementById('toggle-console')?.addEventListener('click', () => {
            const console = document.getElementById('connectivity-test-console');
            if (console) {
                console.classList.toggle('minimized');
                const icon = document.querySelector('#toggle-console i');
                if (icon) {
                    icon.className = console.classList.contains('minimized') ? 
                        'fas fa-window-maximize' : 'fas fa-window-minimize';
                }
            }
        });

        // Console header click to toggle
        document.querySelector('.test-console-header')?.addEventListener('click', (e) => {
            if (!e.target.closest('.console-controls')) {
                document.getElementById('toggle-console')?.click();
            }
        });

        // Enter key in target input
        document.getElementById('test-target')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isTestingInProgress) {
                this.runTest();
            }
        });
    }

    // Public API
    isAllConnectivityValid() {
        const devices = window.editor?.devices?.filter(d => {
            const config = window.deviceConfigurator?.getDeviceConfiguration(d.id);
            return config && config.ipAddress;
        }) || [];

        if (devices.length < 2) return false;

        for (let i = 0; i < devices.length; i++) {
            for (let j = i + 1; j < devices.length; j++) {
                const sourceDevice = devices[i];
                const targetDevice = devices[j];
                const sourceConfig = window.deviceConfigurator?.getDeviceConfiguration(sourceDevice.id);
                const targetConfig = window.deviceConfigurator?.getDeviceConfiguration(targetDevice.id);

                if (sourceConfig && targetConfig) {
                    const connectivity = this.checkConnectivity(sourceDevice, sourceConfig, targetDevice, targetConfig);
                    if (!connectivity.reachable) {
                        return false;
                    }
                }
            }
        }

        return true;
    }

    getConnectivityReport() {
        const devices = window.editor?.devices?.filter(d => {
            const config = window.deviceConfigurator?.getDeviceConfiguration(d.id);
            return config && config.ipAddress;
        }) || [];

        let totalTests = 0;
        let passedTests = 0;

        for (let i = 0; i < devices.length; i++) {
            for (let j = i + 1; j < devices.length; j++) {
                totalTests++;
                
                const sourceDevice = devices[i];
                const targetDevice = devices[j];
                const sourceConfig = window.deviceConfigurator?.getDeviceConfiguration(sourceDevice.id);
                const targetConfig = window.deviceConfigurator?.getDeviceConfiguration(targetDevice.id);

                if (sourceConfig && targetConfig) {
                    const connectivity = this.checkConnectivity(sourceDevice, sourceConfig, targetDevice, targetConfig);
                    if (connectivity.reachable) {
                        passedTests++;
                    }
                }
            }
        }

        return {
            totalTests,
            passedTests,
            allValid: totalTests > 0 && passedTests === totalTests
        };
    }
}

// Initialize connectivity test manager
document.addEventListener('DOMContentLoaded', () => {
    window.connectivityTester = new ConnectivityTestManager();
    console.log('✓ Connectivity Test Manager initialized');
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConnectivityTestManager;
}

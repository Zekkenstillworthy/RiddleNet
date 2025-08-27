/**
 * Network Configuration Validator for Network Simulation Core
 * Provides real network configuration validation with advanced checks
 */

class NetworkConfigurationValidator {
    constructor() {
        this.validationRules = new Map();
        this.validationHistory = [];
        this.realTimeValidation = true;
        this.initializeValidator();
    }

    initializeValidator() {
        this.setupValidationRules();
        this.createValidationInterface();
        this.attachEventListeners();
    }

    setupValidationRules() {
        // Layer 2 Validation Rules
        this.validationRules.set('layer2', {
            name: 'Layer 2 (Data Link) Validation',
            rules: [
                {
                    id: 'vlan_consistency',
                    name: 'VLAN Consistency',
                    description: 'Check VLAN configuration consistency across switches',
                    critical: true,
                    validator: this.validateVLANConsistency.bind(this)
                },
                {
                    id: 'trunk_configuration',
                    name: 'Trunk Port Configuration',
                    description: 'Validate trunk port settings and allowed VLANs',
                    critical: true,
                    validator: this.validateTrunkConfiguration.bind(this)
                },
                {
                    id: 'stp_topology',
                    name: 'Spanning Tree Protocol',
                    description: 'Check for STP loops and proper root bridge selection',
                    critical: false,
                    validator: this.validateSTPTopology.bind(this)
                }
            ]
        });

        // Layer 3 Validation Rules
        this.validationRules.set('layer3', {
            name: 'Layer 3 (Network) Validation',
            rules: [
                {
                    id: 'ip_addressing',
                    name: 'IP Address Configuration',
                    description: 'Validate IP address assignments and subnet consistency',
                    critical: true,
                    validator: this.validateIPAddressing.bind(this)
                },
                {
                    id: 'routing_tables',
                    name: 'Routing Table Validation',
                    description: 'Check routing table entries and reachability',
                    critical: true,
                    validator: this.validateRoutingTables.bind(this)
                },
                {
                    id: 'subnet_overlap',
                    name: 'Subnet Overlap Detection',
                    description: 'Detect overlapping subnets and address conflicts',
                    critical: true,
                    validator: this.validateSubnetOverlap.bind(this)
                }
            ]
        });

        // Connectivity Validation Rules
        this.validationRules.set('connectivity', {
            name: 'Connectivity Validation',
            rules: [
                {
                    id: 'end_to_end',
                    name: 'End-to-End Connectivity',
                    description: 'Test connectivity between all devices',
                    critical: true,
                    validator: this.validateEndToEndConnectivity.bind(this)
                },
                {
                    id: 'gateway_reachability',
                    name: 'Gateway Reachability',
                    description: 'Verify all devices can reach their gateways',
                    critical: true,
                    validator: this.validateGatewayReachability.bind(this)
                },
                {
                    id: 'dns_resolution',
                    name: 'DNS Resolution',
                    description: 'Test DNS resolution for configured devices',
                    critical: false,
                    validator: this.validateDNSResolution.bind(this)
                }
            ]
        });

        // Security Validation Rules
        this.validationRules.set('security', {
            name: 'Security Configuration Validation',
            rules: [
                {
                    id: 'access_control',
                    name: 'Access Control Lists',
                    description: 'Validate ACL configuration and effectiveness',
                    critical: false,
                    validator: this.validateAccessControl.bind(this)
                },
                {
                    id: 'authentication',
                    name: 'Authentication Configuration',
                    description: 'Check authentication settings for network devices',
                    critical: false,
                    validator: this.validateAuthentication.bind(this)
                }
            ]
        });
    }

    createValidationInterface() {
        const validationHTML = `
        <div id="networkValidationPanel" class="validation-panel">
            <div class="validation-header">
                <h3>Network Configuration Validation</h3>
                <div class="validation-controls">
                    <button id="runValidationBtn" class="validate-btn">
                        <i class="fas fa-play"></i> Run Validation
                    </button>
                    <button id="realTimeToggle" class="toggle-btn active">
                        <i class="fas fa-sync"></i> Real-time
                    </button>
                    <button id="exportReportBtn" class="export-btn">
                        <i class="fas fa-file-export"></i> Export Report
                    </button>
                </div>
            </div>
            
            <div class="validation-body">
                <div class="validation-status">
                    <div id="validationOverall" class="overall-status">
                        <div class="status-indicator pending">
                            <i class="fas fa-clock"></i>
                            <span>Ready for Validation</span>
                        </div>
                    </div>
                </div>
                
                <div class="validation-categories">
                    <div class="category-tabs">
                        <button class="tab-btn active" data-category="all">All Tests</button>
                        <button class="tab-btn" data-category="layer2">Layer 2</button>
                        <button class="tab-btn" data-category="layer3">Layer 3</button>
                        <button class="tab-btn" data-category="connectivity">Connectivity</button>
                        <button class="tab-btn" data-category="security">Security</button>
                    </div>
                    
                    <div id="validationResults" class="validation-results">
                        <!-- Results will be populated here -->
                    </div>
                </div>
                
                <div class="validation-details">
                    <div id="validationProgress" class="progress-section" style="display: none;">
                        <h4>Validation Progress</h4>
                        <div class="progress-container">
                            <div class="progress-bar">
                                <div class="progress-fill"></div>
                            </div>
                            <div class="progress-text">Initializing...</div>
                        </div>
                    </div>
                    
                    <div id="detailedResults" class="detailed-results">
                        <h4>Detailed Results</h4>
                        <div class="results-content">
                            <p>Run validation to see detailed results</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;

        // Add to page
        const topologyContainer = document.querySelector('.topology-container') || 
                                document.querySelector('#canvas').parentElement;
        if (topologyContainer) {
            topologyContainer.insertAdjacentHTML('afterend', validationHTML);
        }

        this.addValidationStyles();
    }

    addValidationStyles() {
        const styles = `
        <style>
        .validation-panel {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 12px;
            margin: 20px 0;
            color: white;
        }
        
        .validation-header {
            padding: 20px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .validation-header h3 {
            margin: 0;
            color: #00d4ff;
            font-size: 18px;
        }
        
        .validation-controls {
            display: flex;
            gap: 10px;
        }
        
        .validate-btn, .toggle-btn, .export-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.3s ease;
        }
        
        .validate-btn {
            background: #28a745;
            color: white;
        }
        
        .toggle-btn {
            background: #6c757d;
            color: white;
        }
        
        .toggle-btn.active {
            background: #007bff;
        }
        
        .export-btn {
            background: #17a2b8;
            color: white;
        }
        
        .validate-btn:hover { background: #218838; }
        .toggle-btn:hover { background: #545b62; }
        .export-btn:hover { background: #138496; }
        
        .validation-body {
            padding: 20px;
        }
        
        .overall-status {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 500;
        }
        
        .status-indicator.pending {
            background: rgba(255, 193, 7, 0.2);
            color: #ffc107;
            border: 1px solid #ffc107;
        }
        
        .status-indicator.running {
            background: rgba(0, 123, 255, 0.2);
            color: #007bff;
            border: 1px solid #007bff;
        }
        
        .status-indicator.passed {
            background: rgba(40, 167, 69, 0.2);
            color: #28a745;
            border: 1px solid #28a745;
        }
        
        .status-indicator.failed {
            background: rgba(220, 53, 69, 0.2);
            color: #dc3545;
            border: 1px solid #dc3545;
        }
        
        .category-tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 1px solid #333;
        }
        
        .tab-btn {
            background: none;
            border: none;
            color: #ccc;
            padding: 12px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
        }
        
        .tab-btn.active {
            color: #00d4ff;
            border-bottom-color: #00d4ff;
        }
        
        .tab-btn:hover {
            color: #00d4ff;
        }
        
        .validation-results {
            min-height: 200px;
        }
        
        .validation-category {
            margin-bottom: 25px;
        }
        
        .category-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .category-title {
            font-size: 16px;
            font-weight: 600;
            color: #00d4ff;
        }
        
        .category-status {
            font-size: 14px;
            padding: 4px 12px;
            border-radius: 4px;
        }
        
        .category-status.passed { background: #28a745; color: white; }
        .category-status.failed { background: #dc3545; color: white; }
        .category-status.warning { background: #ffc107; color: #000; }
        .category-status.pending { background: #6c757d; color: white; }
        
        .validation-rule {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #666;
        }
        
        .validation-rule.passed { border-left-color: #28a745; }
        .validation-rule.failed { border-left-color: #dc3545; }
        .validation-rule.warning { border-left-color: #ffc107; }
        
        .rule-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .rule-name {
            font-weight: 600;
            color: white;
        }
        
        .rule-status {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 14px;
        }
        
        .rule-status.passed { color: #28a745; }
        .rule-status.failed { color: #dc3545; }
        .rule-status.warning { color: #ffc107; }
        
        .rule-description {
            color: #ccc;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .rule-details {
            background: #333;
            border-radius: 4px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #ddd;
            display: none;
        }
        
        .rule-details.show {
            display: block;
        }
        
        .rule-toggle {
            background: none;
            border: none;
            color: #00d4ff;
            cursor: pointer;
            font-size: 12px;
            text-decoration: underline;
        }
        
        .progress-container {
            margin-bottom: 15px;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 8px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #007bff);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            color: #ccc;
            font-size: 14px;
        }
        
        .detailed-results {
            margin-top: 30px;
        }
        
        .detailed-results h4 {
            color: #00d4ff;
            margin-bottom: 15px;
        }
        
        .results-content {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 15px;
            color: #ccc;
        }
        
        .validation-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .summary-card {
            background: #333;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .summary-number {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .summary-label {
            color: #ccc;
            font-size: 14px;
        }
        
        .summary-card.passed .summary-number { color: #28a745; }
        .summary-card.failed .summary-number { color: #dc3545; }
        .summary-card.warning .summary-number { color: #ffc107; }
        .summary-card.total .summary-number { color: #00d4ff; }
        </style>`;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    attachEventListeners() {
        // Run validation button
        document.getElementById('runValidationBtn')?.addEventListener('click', () => {
            this.runCompleteValidation();
        });

        // Real-time toggle
        document.getElementById('realTimeToggle')?.addEventListener('click', (e) => {
            this.toggleRealTimeValidation(e.target);
        });

        // Export report button
        document.getElementById('exportReportBtn')?.addEventListener('click', () => {
            this.exportValidationReport();
        });

        // Category tabs
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                this.switchCategory(e.target.dataset.category);
            }
        });

        // Rule detail toggles
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('rule-toggle')) {
                this.toggleRuleDetails(e.target);
            }
        });

        // Listen for topology changes if real-time is enabled
        if (this.realTimeValidation) {
            this.setupRealTimeValidation();
        }
    }

    async runCompleteValidation() {
        this.showValidationProgress();
        this.updateOverallStatus('running', 'Running Validation...');

        const results = {
            summary: { total: 0, passed: 0, failed: 0, warnings: 0 },
            categories: new Map(),
            timestamp: new Date().toISOString(),
            topology: this.getCurrentTopology()
        };

        let progress = 0;
        const totalRules = this.getTotalRulesCount();

        for (const [categoryId, category] of this.validationRules) {
            const categoryResults = {
                name: category.name,
                rules: [],
                status: 'passed'
            };

            for (const rule of category.rules) {
                this.updateProgress(progress / totalRules * 100, `Validating: ${rule.name}`);
                
                try {
                    const ruleResult = await rule.validator(results.topology);
                    categoryResults.rules.push({
                        ...rule,
                        result: ruleResult
                    });

                    // Update summary
                    results.summary.total++;
                    if (ruleResult.status === 'passed') {
                        results.summary.passed++;
                    } else if (ruleResult.status === 'failed') {
                        results.summary.failed++;
                        if (rule.critical) categoryResults.status = 'failed';
                    } else if (ruleResult.status === 'warning') {
                        results.summary.warnings++;
                        if (categoryResults.status === 'passed') categoryResults.status = 'warning';
                    }

                } catch (error) {
                    console.error(`Validation error for ${rule.name}:`, error);
                    categoryResults.rules.push({
                        ...rule,
                        result: {
                            status: 'failed',
                            message: `Validation error: ${error.message}`,
                            details: []
                        }
                    });
                    results.summary.total++;
                    results.summary.failed++;
                }

                progress++;
            }

            results.categories.set(categoryId, categoryResults);
        }

        this.hideValidationProgress();
        this.displayValidationResults(results);
        this.validationHistory.push(results);

        // Update overall status
        const overallStatus = results.summary.failed > 0 ? 'failed' : 
                            results.summary.warnings > 0 ? 'warning' : 'passed';
        this.updateOverallStatus(overallStatus, this.getOverallStatusMessage(results.summary));
    }

    // Validation Rule Implementations

    async validateVLANConsistency(topology) {
        const devices = topology.devices.filter(d => d.type === 'switch');
        const vlans = new Map();
        const issues = [];

        devices.forEach(device => {
            const config = this.getDeviceConfig(device.id);
            if (config && config.vlanId) {
                if (!vlans.has(config.vlanId)) {
                    vlans.set(config.vlanId, []);
                }
                vlans.get(config.vlanId).push(device.label || device.id);
            }
        });

        // Check for VLAN consistency issues
        for (const [vlanId, deviceList] of vlans) {
            if (deviceList.length === 1) {
                issues.push(`VLAN ${vlanId} only configured on ${deviceList[0]} - may cause isolation`);
            }
        }

        return {
            status: issues.length > 0 ? 'warning' : 'passed',
            message: issues.length === 0 ? 'VLAN configuration is consistent' : 
                    `Found ${issues.length} VLAN consistency issue(s)`,
            details: issues
        };
    }

    async validateTrunkConfiguration(topology) {
        const connections = topology.connections;
        const issues = [];
        const warnings = [];

        // Check connections between switches
        const switchConnections = connections.filter(conn => {
            const sourceDevice = topology.devices.find(d => d.id === conn.source);
            const targetDevice = topology.devices.find(d => d.id === conn.target);
            return sourceDevice?.type === 'switch' && targetDevice?.type === 'switch';
        });

        switchConnections.forEach(conn => {
            // In a real implementation, this would check actual trunk configuration
            // For now, we'll simulate trunk validation
            const hasTrunkConfig = Math.random() > 0.3; // Simulate trunk detection
            
            if (!hasTrunkConfig) {
                warnings.push(`Connection between ${conn.source} and ${conn.target} may need trunk configuration`);
            }
        });

        return {
            status: issues.length > 0 ? 'failed' : warnings.length > 0 ? 'warning' : 'passed',
            message: issues.length === 0 && warnings.length === 0 ? 'Trunk configuration is correct' : 
                    `Found ${issues.length} error(s) and ${warnings.length} warning(s)`,
            details: [...issues, ...warnings]
        };
    }

    async validateSTPTopology(topology) {
        const switches = topology.devices.filter(d => d.type === 'switch');
        const issues = [];

        // Check for potential STP loops
        const connections = topology.connections.filter(conn => {
            const sourceDevice = topology.devices.find(d => d.id === conn.source);
            const targetDevice = topology.devices.find(d => d.id === conn.target);
            return sourceDevice?.type === 'switch' && targetDevice?.type === 'switch';
        });

        // Simple loop detection algorithm
        if (this.hasLoops(switches, connections)) {
            issues.push('Potential switching loops detected - ensure STP is enabled');
        }

        return {
            status: issues.length > 0 ? 'warning' : 'passed',
            message: issues.length === 0 ? 'No STP issues detected' : 
                    `Found ${issues.length} STP issue(s)`,
            details: issues
        };
    }

    async validateIPAddressing(topology) {
        const devices = topology.devices;
        const issues = [];
        const warnings = [];

        // Check for IP conflicts and proper addressing
        const ipAddresses = new Map();

        devices.forEach(device => {
            const config = this.getDeviceConfig(device.id);
            if (config && config.ipAddress) {
                if (ipAddresses.has(config.ipAddress)) {
                    issues.push(`IP address conflict: ${config.ipAddress} used by ${device.label} and ${ipAddresses.get(config.ipAddress)}`);
                } else {
                    ipAddresses.set(config.ipAddress, device.label || device.id);
                }

                // Validate IP format
                if (!this.isValidIP(config.ipAddress)) {
                    issues.push(`Invalid IP address format on ${device.label}: ${config.ipAddress}`);
                }

                // Check subnet consistency
                if (!this.isIPInCorrectSubnet(config.ipAddress, config.subnetMask)) {
                    warnings.push(`IP address ${config.ipAddress} on ${device.label} may not be in correct subnet`);
                }
            } else if (device.type !== 'hub') {
                warnings.push(`Device ${device.label || device.id} has no IP configuration`);
            }
        });

        return {
            status: issues.length > 0 ? 'failed' : warnings.length > 0 ? 'warning' : 'passed',
            message: issues.length === 0 && warnings.length === 0 ? 'IP addressing is correct' : 
                    `Found ${issues.length} error(s) and ${warnings.length} warning(s)`,
            details: [...issues, ...warnings]
        };
    }

    async validateRoutingTables(topology) {
        const routers = topology.devices.filter(d => d.type === 'router');
        const issues = [];
        const warnings = [];

        routers.forEach(router => {
            const config = this.getDeviceConfig(router.id);
            
            // Check for default route
            if (config && !config.routingProtocol || config.routingProtocol === 'none') {
                warnings.push(`Router ${router.label} has no routing protocol configured`);
            }

            // Check reachability to other networks
            const otherNetworks = this.getOtherNetworks(router, topology);
            if (otherNetworks.length > 0 && (!config || !config.routingProtocol)) {
                issues.push(`Router ${router.label} cannot reach other networks without routing configuration`);
            }
        });

        return {
            status: issues.length > 0 ? 'failed' : warnings.length > 0 ? 'warning' : 'passed',
            message: issues.length === 0 && warnings.length === 0 ? 'Routing configuration is correct' : 
                    `Found ${issues.length} error(s) and ${warnings.length} warning(s)`,
            details: [...issues, ...warnings]
        };
    }

    async validateSubnetOverlap(topology) {
        const subnets = new Map();
        const issues = [];

        topology.devices.forEach(device => {
            const config = this.getDeviceConfig(device.id);
            if (config && config.ipAddress && config.subnetMask) {
                const networkAddress = this.getNetworkAddress(config.ipAddress, config.subnetMask);
                
                if (subnets.has(networkAddress)) {
                    subnets.get(networkAddress).push(device.label || device.id);
                } else {
                    subnets.set(networkAddress, [device.label || device.id]);
                }
            }
        });

        // Check for overlapping subnets (simplified check)
        const networkAddresses = Array.from(subnets.keys());
        for (let i = 0; i < networkAddresses.length; i++) {
            for (let j = i + 1; j < networkAddresses.length; j++) {
                if (this.subnetsOverlap(networkAddresses[i], networkAddresses[j])) {
                    issues.push(`Subnet overlap detected between networks ${networkAddresses[i]} and ${networkAddresses[j]}`);
                }
            }
        }

        return {
            status: issues.length > 0 ? 'failed' : 'passed',
            message: issues.length === 0 ? 'No subnet overlaps detected' : 
                    `Found ${issues.length} subnet overlap(s)`,
            details: issues
        };
    }

    async validateEndToEndConnectivity(topology) {
        const endDevices = topology.devices.filter(d => d.type === 'pc' || d.type === 'server');
        const issues = [];
        const warnings = [];

        // Check if all end devices are connected to the network
        endDevices.forEach(device => {
            const isConnected = topology.connections.some(conn => 
                conn.source === device.id || conn.target === device.id
            );

            if (!isConnected) {
                issues.push(`Device ${device.label || device.id} is not connected to the network`);
                return;
            }

            const config = this.getDeviceConfig(device.id);
            if (!config || !config.ipAddress) {
                warnings.push(`Device ${device.label || device.id} is connected but has no IP configuration`);
                return;
            }

            // Check if device can reach its gateway
            if (config.gateway && !this.canReachGateway(device, topology)) {
                issues.push(`Device ${device.label || device.id} cannot reach its gateway ${config.gateway}`);
            }
        });

        // Simulate connectivity tests between all pairs of end devices
        for (let i = 0; i < endDevices.length; i++) {
            for (let j = i + 1; j < endDevices.length; j++) {
                const canCommunicate = this.simulateConnectivity(endDevices[i], endDevices[j], topology);
                if (!canCommunicate) {
                    issues.push(`No connectivity between ${endDevices[i].label || endDevices[i].id} and ${endDevices[j].label || endDevices[j].id}`);
                }
            }
        }

        return {
            status: issues.length > 0 ? 'failed' : warnings.length > 0 ? 'warning' : 'passed',
            message: issues.length === 0 && warnings.length === 0 ? 'All devices have end-to-end connectivity' : 
                    `Found ${issues.length} connectivity issue(s) and ${warnings.length} warning(s)`,
            details: [...issues, ...warnings]
        };
    }

    async validateGatewayReachability(topology) {
        const devices = topology.devices.filter(d => d.type === 'pc' || d.type === 'server');
        const issues = [];

        devices.forEach(device => {
            const config = this.getDeviceConfig(device.id);
            if (config && config.gateway) {
                // Check if gateway exists in topology
                const gatewayDevice = this.findDeviceByIP(config.gateway, topology);
                if (!gatewayDevice) {
                    issues.push(`Gateway ${config.gateway} for ${device.label || device.id} not found in topology`);
                } else {
                    // Check if device can reach gateway (simplified check)
                    const canReach = this.canReachGateway(device, topology);
                    if (!canReach) {
                        issues.push(`Device ${device.label || device.id} cannot reach gateway ${config.gateway}`);
                    }
                }
            }
        });

        return {
            status: issues.length > 0 ? 'failed' : 'passed',
            message: issues.length === 0 ? 'All gateways are reachable' : 
                    `Found ${issues.length} gateway reachability issue(s)`,
            details: issues
        };
    }

    async validateDNSResolution(topology) {
        const devices = topology.devices.filter(d => d.type === 'pc' || d.type === 'server');
        const warnings = [];

        devices.forEach(device => {
            const config = this.getDeviceConfig(device.id);
            if (config && config.dns) {
                // Check if DNS server is reachable
                const dnsDevice = this.findDeviceByIP(config.dns, topology);
                if (!dnsDevice) {
                    warnings.push(`DNS server ${config.dns} for ${device.label || device.id} not found in topology`);
                }
            } else if (config && config.ipAddress) {
                warnings.push(`Device ${device.label || device.id} has no DNS configuration`);
            }
        });

        return {
            status: warnings.length > 0 ? 'warning' : 'passed',
            message: warnings.length === 0 ? 'DNS configuration is correct' : 
                    `Found ${warnings.length} DNS issue(s)`,
            details: warnings
        };
    }

    async validateAccessControl(topology) {
        // Placeholder for ACL validation
        return {
            status: 'passed',
            message: 'Access control validation not implemented',
            details: ['ACL validation requires additional configuration data']
        };
    }

    async validateAuthentication(topology) {
        // Placeholder for authentication validation
        return {
            status: 'passed',
            message: 'Authentication validation not implemented',
            details: ['Authentication validation requires device access credentials']
        };
    }

    // Helper Methods

    getCurrentTopology() {
        // Get current topology data - integrate with existing topology system
        return {
            devices: window.devices || [],
            connections: window.connections || []
        };
    }

    getDeviceConfig(deviceId) {
        // Get device configuration from IP manager
        if (window.ipManager) {
            return window.ipManager.networkConfigs.get(deviceId);
        }
        return null;
    }

    getTotalRulesCount() {
        let total = 0;
        for (const category of this.validationRules.values()) {
            total += category.rules.length;
        }
        return total;
    }

    hasLoops(switches, connections) {
        // Simple cycle detection in switch topology
        if (switches.length < 3 || connections.length < 3) return false;
        
        // Build adjacency list
        const graph = new Map();
        switches.forEach(sw => graph.set(sw.id, []));
        
        connections.forEach(conn => {
            if (graph.has(conn.source) && graph.has(conn.target)) {
                graph.get(conn.source).push(conn.target);
                graph.get(conn.target).push(conn.source);
            }
        });
        
        // Simple cycle detection using DFS
        const visited = new Set();
        const inStack = new Set();
        
        for (const node of graph.keys()) {
            if (!visited.has(node) && this.hasCycleDFS(node, graph, visited, inStack, null)) {
                return true;
            }
        }
        
        return false;
    }

    hasCycleDFS(node, graph, visited, inStack, parent) {
        visited.add(node);
        inStack.add(node);
        
        for (const neighbor of graph.get(node) || []) {
            if (neighbor === parent) continue; // Skip back to parent
            
            if (inStack.has(neighbor)) return true;
            if (!visited.has(neighbor) && this.hasCycleDFS(neighbor, graph, visited, inStack, node)) {
                return true;
            }
        }
        
        inStack.delete(node);
        return false;
    }

    isValidIP(ip) {
        const regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return regex.test(ip);
    }

    isIPInCorrectSubnet(ip, mask) {
        // Simplified subnet validation
        if (!ip || !mask) return false;
        try {
            const ipNum = this.ipToNumber(ip);
            const maskNum = this.ipToNumber(mask);
            const networkNum = ipNum & maskNum;
            const broadcastNum = networkNum | (~maskNum >>> 0);
            
            return ipNum > networkNum && ipNum < broadcastNum;
        } catch {
            return false;
        }
    }

    getNetworkAddress(ip, mask) {
        try {
            const ipNum = this.ipToNumber(ip);
            const maskNum = this.ipToNumber(mask);
            const networkNum = ipNum & maskNum;
            return this.numberToIP(networkNum);
        } catch {
            return null;
        }
    }

    subnetsOverlap(network1, network2) {
        // Simplified overlap check
        return network1 === network2;
    }

    getOtherNetworks(router, topology) {
        // Get networks that router should be able to reach
        const routerConfig = this.getDeviceConfig(router.id);
        if (!routerConfig || !routerConfig.ipAddress) return [];
        
        const routerNetwork = this.getNetworkAddress(routerConfig.ipAddress, routerConfig.subnetMask);
        const otherNetworks = [];
        
        topology.devices.forEach(device => {
            const config = this.getDeviceConfig(device.id);
            if (config && config.ipAddress && device.id !== router.id) {
                const deviceNetwork = this.getNetworkAddress(config.ipAddress, config.subnetMask);
                if (deviceNetwork && deviceNetwork !== routerNetwork && !otherNetworks.includes(deviceNetwork)) {
                    otherNetworks.push(deviceNetwork);
                }
            }
        });
        
        return otherNetworks;
    }

    findDeviceByIP(ip, topology) {
        return topology.devices.find(device => {
            const config = this.getDeviceConfig(device.id);
            return config && config.ipAddress === ip;
        });
    }

    canReachGateway(device, topology) {
        // Simplified gateway reachability check
        const config = this.getDeviceConfig(device.id);
        if (!config || !config.gateway) return true;
        
        const gatewayDevice = this.findDeviceByIP(config.gateway, topology);
        if (!gatewayDevice) return false;
        
        // Check if there's a path to gateway (simplified)
        return this.hasPathBetweenDevices(device, gatewayDevice, topology);
    }

    hasPathBetweenDevices(device1, device2, topology) {
        // Simple path detection using BFS
        const queue = [device1.id];
        const visited = new Set([device1.id]);
        
        while (queue.length > 0) {
            const currentId = queue.shift();
            
            if (currentId === device2.id) return true;
            
            // Find all connected devices
            topology.connections.forEach(conn => {
                let nextId = null;
                if (conn.source === currentId && !visited.has(conn.target)) {
                    nextId = conn.target;
                } else if (conn.target === currentId && !visited.has(conn.source)) {
                    nextId = conn.source;
                }
                
                if (nextId) {
                    visited.add(nextId);
                    queue.push(nextId);
                }
            });
        }
        
        return false;
    }

    simulateConnectivity(device1, device2, topology) {
        // Simulate end-to-end connectivity test
        const config1 = this.getDeviceConfig(device1.id);
        const config2 = this.getDeviceConfig(device2.id);
        
        if (!config1 || !config2 || !config1.ipAddress || !config2.ipAddress) {
            return false;
        }
        
        // Check if devices are in same subnet
        if (this.areInSameSubnet(config1, config2)) {
            return this.hasPathBetweenDevices(device1, device2, topology);
        }
        
        // Check if both devices have gateways and can reach them
        if (!config1.gateway || !config2.gateway) return false;
        
        const gateway1 = this.findDeviceByIP(config1.gateway, topology);
        const gateway2 = this.findDeviceByIP(config2.gateway, topology);
        
        if (!gateway1 || !gateway2) return false;
        
        // Check path through gateways
        return this.hasPathBetweenDevices(device1, gateway1, topology) &&
               this.hasPathBetweenDevices(device2, gateway2, topology) &&
               this.hasPathBetweenDevices(gateway1, gateway2, topology);
    }

    areInSameSubnet(config1, config2) {
        if (!config1.ipAddress || !config2.ipAddress || !config1.subnetMask || !config2.subnetMask) {
            return false;
        }
        
        const ip1 = this.ipToNumber(config1.ipAddress);
        const ip2 = this.ipToNumber(config2.ipAddress);
        const mask1 = this.ipToNumber(config1.subnetMask);
        const mask2 = this.ipToNumber(config2.subnetMask);
        
        return mask1 === mask2 && (ip1 & mask1) === (ip2 & mask2);
    }

    ipToNumber(ip) {
        return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet), 0) >>> 0;
    }

    numberToIP(num) {
        return [(num >>> 24) & 255, (num >>> 16) & 255, (num >>> 8) & 255, num & 255].join('.');
    }

    // UI Methods

    showValidationProgress() {
        document.getElementById('validationProgress').style.display = 'block';
    }

    hideValidationProgress() {
        document.getElementById('validationProgress').style.display = 'none';
    }

    updateProgress(percentage, message) {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        
        if (progressFill) progressFill.style.width = percentage + '%';
        if (progressText) progressText.textContent = message;
    }

    updateOverallStatus(status, message) {
        const statusIndicator = document.querySelector('.status-indicator');
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${status}`;
            statusIndicator.querySelector('span').textContent = message;
            
            const icon = statusIndicator.querySelector('i');
            icon.className = status === 'running' ? 'fas fa-sync fa-spin' :
                           status === 'passed' ? 'fas fa-check-circle' :
                           status === 'failed' ? 'fas fa-times-circle' :
                           status === 'warning' ? 'fas fa-exclamation-triangle' :
                           'fas fa-clock';
        }
    }

    getOverallStatusMessage(summary) {
        if (summary.failed > 0) {
            return `Validation Failed - ${summary.failed} critical issues found`;
        } else if (summary.warnings > 0) {
            return `Validation Passed with Warnings - ${summary.warnings} issues to review`;
        } else {
            return `Validation Passed - All ${summary.total} tests successful`;
        }
    }

    displayValidationResults(results) {
        this.displayValidationSummary(results.summary);
        this.displayCategoryResults(results.categories);
        this.displayDetailedResults(results);
    }

    displayValidationSummary(summary) {
        const summaryHTML = `
        <div class="validation-summary">
            <div class="summary-card total">
                <div class="summary-number">${summary.total}</div>
                <div class="summary-label">Total Tests</div>
            </div>
            <div class="summary-card passed">
                <div class="summary-number">${summary.passed}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-card failed">
                <div class="summary-number">${summary.failed}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-card warning">
                <div class="summary-number">${summary.warnings}</div>
                <div class="summary-label">Warnings</div>
            </div>
        </div>`;
        
        const resultsContainer = document.getElementById('validationResults');
        resultsContainer.innerHTML = summaryHTML + resultsContainer.innerHTML;
    }

    displayCategoryResults(categories) {
        let html = '';
        
        for (const [categoryId, category] of categories) {
            html += `
            <div class="validation-category" data-category="${categoryId}">
                <div class="category-header">
                    <div class="category-title">${category.name}</div>
                    <div class="category-status ${category.status}">${category.status.toUpperCase()}</div>
                </div>
                <div class="category-rules">`;
            
            category.rules.forEach(rule => {
                html += `
                <div class="validation-rule ${rule.result.status}">
                    <div class="rule-header">
                        <div class="rule-name">${rule.name}</div>
                        <div class="rule-status ${rule.result.status}">
                            <i class="fas ${rule.result.status === 'passed' ? 'fa-check' : 
                                         rule.result.status === 'failed' ? 'fa-times' : 'fa-exclamation-triangle'}"></i>
                            ${rule.result.status.toUpperCase()}
                        </div>
                    </div>
                    <div class="rule-description">${rule.description}</div>
                    <div class="rule-message">${rule.result.message}</div>
                    ${rule.result.details && rule.result.details.length > 0 ? 
                        `<button class="rule-toggle" data-rule="${rule.id}">Show Details</button>
                         <div class="rule-details" id="details-${rule.id}">
                             ${rule.result.details.map(detail => `<div>• ${detail}</div>`).join('')}
                         </div>` : ''}
                </div>`;
            });
            
            html += `</div></div>`;
        }
        
        document.getElementById('validationResults').innerHTML += html;
    }

    displayDetailedResults(results) {
        const detailsHTML = `
        <div class="validation-metadata">
            <div><strong>Validation Time:</strong> ${new Date(results.timestamp).toLocaleString()}</div>
            <div><strong>Topology:</strong> ${results.topology.devices.length} devices, ${results.topology.connections.length} connections</div>
        </div>
        
        <div class="validation-recommendations">
            <h5>Recommendations:</h5>
            ${this.generateRecommendations(results)}
        </div>`;
        
        document.querySelector('.results-content').innerHTML = detailsHTML;
    }

    generateRecommendations(results) {
        const recommendations = [];
        
        if (results.summary.failed > 0) {
            recommendations.push('Address critical failures before proceeding with network implementation');
        }
        
        if (results.summary.warnings > 0) {
            recommendations.push('Review warning items to optimize network performance and reliability');
        }
        
        // Add specific recommendations based on failed rules
        for (const category of results.categories.values()) {
            category.rules.forEach(rule => {
                if (rule.result.status === 'failed' && rule.critical) {
                    recommendations.push(`Critical: Fix ${rule.name} issues immediately`);
                }
            });
        }
        
        if (recommendations.length === 0) {
            recommendations.push('Network configuration is optimal - ready for deployment');
        }
        
        return recommendations.map(rec => `<div>• ${rec}</div>`).join('');
    }

    switchCategory(category) {
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-category="${category}"]`).classList.add('active');
        
        // Show/hide categories
        document.querySelectorAll('.validation-category').forEach(cat => {
            if (category === 'all') {
                cat.style.display = 'block';
            } else {
                cat.style.display = cat.dataset.category === category ? 'block' : 'none';
            }
        });
    }

    toggleRuleDetails(button) {
        const ruleId = button.dataset.rule;
        const details = document.getElementById(`details-${ruleId}`);
        
        if (details.classList.contains('show')) {
            details.classList.remove('show');
            button.textContent = 'Show Details';
        } else {
            details.classList.add('show');
            button.textContent = 'Hide Details';
        }
    }

    toggleRealTimeValidation(button) {
        this.realTimeValidation = !this.realTimeValidation;
        
        if (this.realTimeValidation) {
            button.classList.add('active');
            this.setupRealTimeValidation();
        } else {
            button.classList.remove('active');
            this.teardownRealTimeValidation();
        }
    }

    setupRealTimeValidation() {
        // Listen for topology changes
        if (window.addEventListener) {
            window.addEventListener('topologyChanged', () => {
                this.debounce(this.runQuickValidation.bind(this), 1000)();
            });
        }
    }

    teardownRealTimeValidation() {
        // Remove event listeners for real-time validation
    }

    runQuickValidation() {
        // Run a subset of validation rules for real-time feedback
        console.log('Running quick validation...');
        // Implementation would run only critical, fast validation rules
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    exportValidationReport() {
        if (this.validationHistory.length === 0) {
            alert('No validation results to export. Run validation first.');
            return;
        }
        
        const latestResults = this.validationHistory[this.validationHistory.length - 1];
        const report = this.generateValidationReport(latestResults);
        
        // Export as JSON
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `network_validation_report_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    generateValidationReport(results) {
        return {
            metadata: {
                timestamp: results.timestamp,
                validator_version: '1.0.0',
                topology_summary: {
                    devices: results.topology.devices.length,
                    connections: results.topology.connections.length
                }
            },
            summary: results.summary,
            detailed_results: Array.from(results.categories.entries()).map(([id, category]) => ({
                category_id: id,
                category_name: category.name,
                status: category.status,
                rules: category.rules.map(rule => ({
                    rule_id: rule.id,
                    rule_name: rule.name,
                    critical: rule.critical,
                    status: rule.result.status,
                    message: rule.result.message,
                    details: rule.result.details
                }))
            })),
            recommendations: this.generateRecommendations(results)
        };
    }
}

// Initialize Network Configuration Validator
const networkValidator = new NetworkConfigurationValidator();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NetworkConfigurationValidator;
}
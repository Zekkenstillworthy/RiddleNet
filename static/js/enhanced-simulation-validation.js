/**
 * Enhanced Simulation Validation System
 * Enforces configuration requirements, connectivity tests, and device compatibility
 * Consistent across ALL simulation editors
 */

class EnhancedSimulationValidator {
    constructor(simulationId = null) {
        this.simulationId = simulationId || this.extractSimulationId();
        
        this.validationStates = {
            DISCONNECTED: 'disconnected',
            CONFIGURED: 'configured',
            CONNECTED: 'connected',
            VALIDATED: 'validated',
            WORKING: 'working'
        };
        
        this.currentState = this.validationStates.DISCONNECTED;
        this.validationConfig = null;
        this.deviceRequirements = null;
        this.connectionRules = null;
        
        this.requiredConfigurations = new Set();
        this.completedConfigurations = new Set();
        this.connectivityTests = new Map();
        this.deviceConfigs = new Map();
        
        this.initializeValidation();
    }

    extractSimulationId() {
        // Extract simulation ID from URL or data attributes
        const urlMatch = window.location.pathname.match(/\/edit\/(\d+)/);
        if (urlMatch) return parseInt(urlMatch[1]);
        
        const dataAttr = document.querySelector('[data-simulation-id]');
        if (dataAttr) return parseInt(dataAttr.dataset.simulationId);
        
        return null;
    }

    async initializeValidation() {
        this.createValidationInterface();
        await this.loadValidationConfiguration();
        this.setupConfigurationRequirements();
        this.setupConnectivityTests();
        this.attachEventListeners();
        this.startPeriodicValidation();
    }

    createValidationInterface() {
        // Remove existing panel if present
        const existingPanel = document.getElementById('enhanced-validation-panel');
        if (existingPanel) {
            existingPanel.remove();
        }

        // Create validation panel
        const validationPanel = document.createElement('div');
        validationPanel.id = 'enhanced-validation-panel';
        validationPanel.innerHTML = `
            <div class="validation-header">
                <h3><i class="fas fa-check-double"></i> Network Validation</h3>
                <div class="validation-controls">
                    <button class="save-validation-btn" id="save-validation-config" title="Save validation configuration">
                        <i class="fas fa-save"></i> Save Config
                    </button>
                    <div class="validation-status" id="overall-validation-status">
                        <span class="status-text">Not Ready</span>
                        <div class="status-indicator disconnected"></div>
                    </div>
                </div>
            </div>
            
            <div class="validation-sections">
                <!-- State Machine Display -->
                <div class="state-machine" id="state-machine">
                    <div class="state-steps">
                        <div class="state-step" data-state="disconnected">
                            <div class="state-icon"><i class="fas fa-times"></i></div>
                            <span>Disconnected</span>
                        </div>
                        <div class="state-connector"></div>
                        <div class="state-step" data-state="configured">
                            <div class="state-icon"><i class="fas fa-cog"></i></div>
                            <span>Configured</span>
                        </div>
                        <div class="state-connector"></div>
                        <div class="state-step" data-state="connected">
                            <div class="state-icon"><i class="fas fa-link"></i></div>
                            <span>Connected</span>
                        </div>
                        <div class="state-connector"></div>
                        <div class="state-step" data-state="validated">
                            <div class="state-icon"><i class="fas fa-check"></i></div>
                            <span>Validated</span>
                        </div>
                        <div class="state-connector"></div>
                        <div class="state-step" data-state="working">
                            <div class="state-icon"><i class="fas fa-check-double"></i></div>
                            <span>Working</span>
                        </div>
                    </div>
                </div>

                <!-- Configuration Requirements -->
                <div class="validation-section" id="config-section">
                    <div class="section-header">
                        <i class="fas fa-cogs"></i>
                        <span>Configuration Requirements</span>
                        <div class="section-status" id="config-status">0/0</div>
                    </div>
                    <div class="section-content" id="config-requirements"></div>
                </div>

                <!-- Physical Connections -->
                <div class="validation-section" id="physical-section">
                    <div class="section-header">
                        <i class="fas fa-plug"></i>
                        <span>Physical Connections</span>
                        <div class="section-status" id="physical-status">0/0</div>
                    </div>
                    <div class="section-content" id="physical-requirements"></div>
                </div>

                <!-- Connectivity Tests -->
                <div class="validation-section" id="connectivity-section">
                    <div class="section-header">
                        <i class="fas fa-network-wired"></i>
                        <span>Connectivity Tests</span>
                        <div class="section-status" id="connectivity-status">0/0</div>
                    </div>
                    <div class="section-content" id="connectivity-tests"></div>
                </div>
            </div>

            <div class="validation-actions">
                <button id="run-connectivity-tests" class="validation-btn" disabled>
                    <i class="fas fa-play"></i> Run Tests
                </button>
                <button id="reset-validation" class="validation-btn secondary">
                    <i class="fas fa-redo"></i> Reset
                </button>
            </div>
        `;

        // Add comprehensive styles
        const styles = document.createElement('style');
        styles.textContent = `
            #enhanced-validation-panel {
                position: fixed;
                top: 80px;
                right: 20px;
                width: 350px;
                background: var(--glass-bg, rgba(15, 23, 42, 0.9));
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
                border-radius: var(--border-radius, 12px);
                backdrop-filter: blur(12px);
                z-index: 1001;
                color: var(--text-primary, #ffffff);
                box-shadow: var(--shadow-lg, 0 10px 30px rgba(0, 0, 0, 0.3));
                max-height: calc(100vh - 120px);
                overflow-y: auto;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }

            .validation-header {
                padding: 16px;
                border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
            }

            .validation-header h3 {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
                color: var(--cyber-glow, #00D9FF);
            }

            .validation-controls {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .save-validation-btn {
                background: linear-gradient(135deg, var(--primary-color, #3B82F6), var(--accent-color, #8B5CF6));
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 6px;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
            }

            .save-validation-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            }

            .save-validation-btn:active {
                transform: translateY(0);
            }

            .validation-status {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 12px;
                font-weight: 500;
            }

            .status-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                transition: all 0.3s ease;
                box-shadow: 0 0 8px currentColor;
            }

            .status-indicator.disconnected { 
                background: var(--danger-color, #EF4444); 
                box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
            }
            .status-indicator.configured { 
                background: var(--warning-color, #F59E0B); 
                box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
            }
            .status-indicator.connected { 
                background: var(--accent-color, #3B82F6); 
                box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
            }
            .status-indicator.validated { 
                background: var(--network-purple, #8B5CF6); 
                box-shadow: 0 0 8px rgba(139, 92, 246, 0.5);
            }
            .status-indicator.working { 
                background: var(--success-color, #10B981); 
                box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
            }

            .state-machine {
                padding: 16px;
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.02));
                border-radius: 8px;
                margin-bottom: 16px;
            }

            .state-steps {
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 8px;
            }

            .state-step {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 4px;
                opacity: 0.4;
                transition: all 0.3s ease;
                flex: 1;
                min-width: 60px;
            }

            .state-step.active {
                opacity: 1;
                transform: scale(1.1);
            }

            .state-step.completed {
                opacity: 1;
            }

            .state-icon {
                width: 24px;
                height: 24px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.1));
                border: 2px solid transparent;
                transition: all 0.3s ease;
            }

            .state-step.active .state-icon {
                background: var(--accent-color, #3B82F6);
                border-color: var(--cyber-glow, #00D9FF);
                box-shadow: 0 0 12px rgba(59, 130, 246, 0.5);
            }

            .state-step.completed .state-icon {
                background: var(--success-color, #10B981);
                border-color: var(--neon-green, #39FF14);
            }

            .state-step span {
                font-size: 10px;
                font-weight: 500;
                text-align: center;
                line-height: 1.2;
            }

            .state-connector {
                flex: 0 0 8px;
                height: 2px;
                background: var(--glass-border, rgba(255, 255, 255, 0.1));
                margin: 0 4px;
                border-radius: 1px;
            }

            .validation-sections {
                padding: 16px;
            }

            .validation-section {
                margin-bottom: 16px;
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
                border-radius: 8px;
                overflow: hidden;
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.02));
                transition: all 0.3s ease;
            }

            .validation-section:hover {
                border-color: var(--accent-color, #3B82F6);
                box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
            }

            .section-header {
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.05));
                padding: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .section-header:hover {
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.08));
            }

            .section-header i {
                width: 16px;
                color: var(--accent-color, #3B82F6);
            }

            .section-status {
                margin-left: auto;
                background: var(--glass-bg, rgba(15, 23, 42, 0.8));
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                color: var(--cyber-glow, #00D9FF);
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            }

            .section-content {
                padding: 12px;
                display: none;
                border-top: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
                background: var(--background, #020617);
            }

            .section-content.expanded {
                display: block;
                animation: slideDown 0.3s ease;
            }

            @keyframes slideDown {
                from {
                    opacity: 0;
                    max-height: 0;
                }
                to {
                    opacity: 1;
                    max-height: 300px;
                }
            }

            .requirement-item {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px;
                border-radius: 6px;
                margin-bottom: 6px;
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.03));
                transition: all 0.2s ease;
            }

            .requirement-item:hover {
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.06));
            }

            .requirement-status {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                font-weight: bold;
                flex-shrink: 0;
            }

            .requirement-status.pending {
                background: var(--glass-border, rgba(255, 255, 255, 0.2));
                color: var(--text-muted, #94A3B8);
            }

            .requirement-status.valid {
                background: var(--success-color, #10B981);
                color: white;
            }

            .requirement-status.invalid {
                background: var(--danger-color, #EF4444);
                color: white;
            }

            .requirement-text {
                flex: 1;
                font-size: 12px;
                line-height: 1.4;
            }

            .validation-actions {
                padding: 16px;
                border-top: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
                display: flex;
                gap: 12px;
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.02));
            }

            .validation-btn {
                flex: 1;
                padding: 10px 16px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
            }

            .validation-btn:not(.secondary) {
                background: linear-gradient(135deg, var(--success-color, #10B981), var(--neon-green, #39FF14));
                color: white;
                box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
            }

            .validation-btn:not(.secondary):hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
            }

            .validation-btn.secondary {
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.1));
                color: var(--text-primary, #ffffff);
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
            }

            .validation-btn.secondary:hover {
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.15));
                border-color: var(--accent-color, #3B82F6);
            }

            .validation-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none !important;
            }

            .test-result {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px;
                border-radius: 6px;
                margin-bottom: 6px;
                font-size: 12px;
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.03));
            }

            .test-result.pass {
                border-left: 3px solid var(--success-color, #10B981);
            }

            .test-result.fail {
                border-left: 3px solid var(--danger-color, #EF4444);
            }

            .test-result.pending {
                border-left: 3px solid var(--warning-color, #F59E0B);
            }

            .test-icon {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                color: white;
                flex-shrink: 0;
            }

            .test-result.pass .test-icon {
                background: var(--success-color, #10B981);
            }

            .test-result.fail .test-icon {
                background: var(--danger-color, #EF4444);
            }

            .test-result.pending .test-icon {
                background: var(--warning-color, #F59E0B);
            }

            /* Responsive design */
            @media (max-width: 1200px) {
                #enhanced-validation-panel {
                    width: 300px;
                    right: 10px;
                }
            }

            @media (max-width: 768px) {
                #enhanced-validation-panel {
                    position: relative;
                    width: 100%;
                    right: auto;
                    top: auto;
                    margin: 20px 0;
                    max-height: none;
                }
            }
        `;

        document.head.appendChild(styles);
        
        // Add to appropriate container
        const container = this.findValidationContainer();
        container.appendChild(validationPanel);
        
        // Initialize section toggle functionality
        this.initializeSectionToggles();
    }

    findValidationContainer() {
        // Try different container selectors based on editor type
        const containers = [
            document.querySelector('.editor-workspace'),
            document.querySelector('.simulation-editor'),
            document.querySelector('.troubleshooting-editor'),
            document.querySelector('main'),
            document.body
        ];
        
        return containers.find(container => container !== null) || document.body;
    }

    initializeSectionToggles() {
        const sectionHeaders = document.querySelectorAll('#enhanced-validation-panel .section-header');
        sectionHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const content = header.nextElementSibling;
                if (content && content.classList.contains('section-content')) {
                    content.classList.toggle('expanded');
                }
            });
        });
    }

    async loadValidationConfiguration() {
        if (!this.simulationId) {
            console.warn('No simulation ID available for validation configuration');
            return;
        }

        try {
            const response = await fetch(`/admin/simulation/edit/${this.simulationId}/validation/config`);
            if (response.ok) {
                const data = await response.json();
                this.validationConfig = data.validation_config;
                this.deviceRequirements = data.device_requirements;
                this.connectionRules = data.connection_rules;
                console.log('Validation configuration loaded successfully');
            } else {
                console.warn('Failed to load validation configuration, using defaults');
                this.useDefaultConfiguration();
            }
        } catch (error) {
            console.error('Error loading validation configuration:', error);
            this.useDefaultConfiguration();
        }
    }

    useDefaultConfiguration() {
        this.validationConfig = {
            enabled: true,
            state_machine_enabled: true,
            configuration_requirements: {
                require_ip_assignment: true,
                require_device_modes: true,
                require_cable_configuration: true,
                require_interface_config: true
            },
            physical_validation: {
                enforce_compatible_connections: true,
                validate_device_capabilities: true,
                check_cable_types: true,
                max_connection_validation: true
            },
            connectivity_tests: {
                require_ping_tests: true,
                require_route_validation: true,
                require_connectivity_matrix: true,
                auto_generate_tests: true,
                required_tests: []
            }
        };
    }
                cursor: pointer;
            }

            .section-status {
                margin-left: auto;
                background: var(--accent-color);
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
            }

            .section-content {
                padding: 12px;
                font-size: 12px;
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease;
            }

            .section-content.expanded {
                max-height: 300px;
            }

            .requirement-item {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 6px 0;
                border-bottom: 1px solid var(--glass-border);
            }

            .requirement-item:last-child {
                border-bottom: none;
            }

            .requirement-icon {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
            }

            .requirement-icon.pending { background: var(--text-muted); color: white; }
            .requirement-icon.completed { background: var(--success-color); color: white; }
            .requirement-icon.failed { background: var(--danger-color); color: white; }

            .validation-actions {
                padding: 16px;
                border-top: 1px solid var(--glass-border);
                display: flex;
                gap: 8px;
            }

            .validation-btn {
                flex: 1;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                background: var(--accent-color);
                color: white;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .validation-btn:disabled {
                background: var(--text-muted);
                cursor: not-allowed;
            }

            .validation-btn.secondary {
                background: var(--glass-bg-light);
                border: 1px solid var(--glass-border);
            }

            .test-result {
                margin-top: 8px;
                padding: 8px;
                border-radius: 4px;
                font-size: 11px;
            }

            .test-result.success { background: rgba(16, 185, 129, 0.1); border-left: 3px solid var(--success-color); }
            .test-result.failed { background: rgba(239, 68, 68, 0.1); border-left: 3px solid var(--danger-color); }
            .test-result.warning { background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--warning-color); }
        `;
        document.head.appendChild(styles);
        document.body.appendChild(validationPanel);

        // Make sections collapsible
        document.querySelectorAll('.section-header').forEach(header => {
            header.addEventListener('click', () => {
                const content = header.nextElementSibling;
                content.classList.toggle('expanded');
            });
        });
    }

    setupConfigurationRequirements() {
        this.requiredConfigurations.clear();
        
        // Get all devices from the editor
        if (window.editor && window.editor.devices) {
            window.editor.devices.forEach(device => {
                if (this.requiresConfiguration(device)) {
                    this.requiredConfigurations.add(`${device.id}_ip`);
                    this.requiredConfigurations.add(`${device.id}_mode`);
                    
                    if (device.type === 'router') {
                        this.requiredConfigurations.add(`${device.id}_routing`);
                    }
                    
                    if (device.type === 'switch') {
                        this.requiredConfigurations.add(`${device.id}_vlan`);
                    }
                }
            });
        }
        
        this.updateConfigurationDisplay();
    }

    requiresConfiguration(device) {
        const configurableTypes = ['pc', 'server', 'router', 'switch', 'access-point'];
        return configurableTypes.includes(device.type);
    }

    setupConnectivityTests() {
        this.connectivityTests.clear();
        
        if (window.editor && window.editor.devices) {
            const endDevices = window.editor.devices.filter(d => d.type === 'pc' || d.type === 'server');
            
            // Create ping tests between all end devices
            for (let i = 0; i < endDevices.length; i++) {
                for (let j = i + 1; j < endDevices.length; j++) {
                    const testId = `ping_${endDevices[i].id}_${endDevices[j].id}`;
                    this.connectivityTests.set(testId, {
                        type: 'ping',
                        source: endDevices[i],
                        target: endDevices[j],
                        status: 'pending',
                        result: null
                    });
                }
            }
            
            // Add routing tests for routers
            const routers = window.editor.devices.filter(d => d.type === 'router');
            routers.forEach(router => {
                const testId = `routing_${router.id}`;
                this.connectivityTests.set(testId, {
                    type: 'routing',
                    device: router,
                    status: 'pending',
                    result: null
                });
            });
        }
        
        this.updateConnectivityDisplay();
    }

    validatePhysicalConnections() {
        const issues = [];
        const warnings = [];
        
        if (!window.editor || !window.editor.connections) {
            return { valid: false, issues: ['No connections found'], warnings };
        }
        
        window.editor.connections.forEach(connection => {
            const sourceDevice = window.editor.devices.find(d => d.id === connection.source);
            const targetDevice = window.editor.devices.find(d => d.id === connection.target);
            
            if (!sourceDevice || !targetDevice) {
                issues.push(`Invalid connection: device not found`);
                return;
            }
            
            // Check connection type compatibility
            const compatibilityResult = this.checkConnectionCompatibility(sourceDevice, targetDevice, connection);
            if (!compatibilityResult.valid) {
                issues.push(compatibilityResult.message);
            }
            
            // Check for wireless capability requirements
            if (connection.type === 'wireless') {
                if (!this.hasWirelessCapability(sourceDevice) || !this.hasWirelessCapability(targetDevice)) {
                    issues.push(`Wireless connection requires both devices to have wireless capability: ${sourceDevice.name} ↔ ${targetDevice.name}`);
                }
            }
            
            // Check for wired connection realism
            if (connection.type === 'wired' || !connection.type) {
                const endDeviceTypes = ['pc', 'server'];
                if (endDeviceTypes.includes(sourceDevice.type) && endDeviceTypes.includes(targetDevice.type)) {
                    warnings.push(`Direct connection between end devices may require crossover cable: ${sourceDevice.name} ↔ ${targetDevice.name}`);
                }
            }
        });
        
        this.updatePhysicalDisplay(issues, warnings);
        return { valid: issues.length === 0, issues, warnings };
    }

    checkConnectionCompatibility(device1, device2, connection) {
        // Check if devices have appropriate interfaces
        const device1Interfaces = this.getDeviceInterfaces(device1);
        const device2Interfaces = this.getDeviceInterfaces(device2);
        
        const connectionType = connection.type || 'wired';
        
        if (connectionType === 'wireless') {
            if (!device1Interfaces.wireless || !device2Interfaces.wireless) {
                return {
                    valid: false,
                    message: `Wireless connection not supported: ${device1.name} or ${device2.name} lacks wireless capability`
                };
            }
        } else {
            if (!device1Interfaces.wired || !device2Interfaces.wired) {
                return {
                    valid: false,
                    message: `Wired connection not supported: ${device1.name} or ${device2.name} lacks wired interface`
                };
            }
        }
        
        return { valid: true };
    }

    getDeviceInterfaces(device) {
        const defaultInterfaces = {
            pc: { wired: true, wireless: false },
            server: { wired: true, wireless: false },
            router: { wired: true, wireless: false },
            switch: { wired: true, wireless: false },
            'access-point': { wired: true, wireless: true },
            laptop: { wired: true, wireless: true },
            smartphone: { wired: false, wireless: true }
        };
        
        // Check device specs if available
        if (device.specs && device.specs.capabilities) {
            return device.specs.capabilities;
        }
        
        return defaultInterfaces[device.type] || { wired: true, wireless: false };
    }

    hasWirelessCapability(device) {
        const interfaces = this.getDeviceInterfaces(device);
        return interfaces.wireless || device.type === 'access-point';
    }

    async runConnectivityTests() {
        const button = document.getElementById('run-connectivity-tests');
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
        
        let allPassed = true;
        
        for (const [testId, test] of this.connectivityTests) {
            test.status = 'running';
            this.updateTestDisplay(testId, test);
            
            // Simulate test execution
            await new Promise(resolve => setTimeout(resolve, 500));
            
            if (test.type === 'ping') {
                const result = await this.performPingTest(test.source, test.target);
                test.result = result;
                test.status = result.success ? 'passed' : 'failed';
                if (!result.success) allPassed = false;
            } else if (test.type === 'routing') {
                const result = await this.performRoutingTest(test.device);
                test.result = result;
                test.status = result.success ? 'passed' : 'failed';
                if (!result.success) allPassed = false;
            }
            
            this.updateTestDisplay(testId, test);
        }
        
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-play"></i> Run Tests';
        
        this.updateOverallStatus(allPassed);
        return allPassed;
    }

    async performPingTest(sourceDevice, targetDevice) {
        // Check if both devices have IP configuration
        const sourceConfig = this.getDeviceConfiguration(sourceDevice.id);
        const targetConfig = this.getDeviceConfiguration(targetDevice.id);
        
        if (!sourceConfig || !sourceConfig.ipAddress) {
            return {
                success: false,
                message: `Source device ${sourceDevice.name} has no IP configuration`,
                details: 'Device must be configured with an IP address before connectivity testing'
            };
        }
        
        if (!targetConfig || !targetConfig.ipAddress) {
            return {
                success: false,
                message: `Target device ${targetDevice.name} has no IP configuration`,
                details: 'Device must be configured with an IP address before connectivity testing'
            };
        }
        
        // Check physical connectivity
        const hasPath = this.hasPhysicalPath(sourceDevice, targetDevice);
        if (!hasPath) {
            return {
                success: false,
                message: `No physical path between ${sourceDevice.name} and ${targetDevice.name}`,
                details: 'Devices must be connected through network infrastructure'
            };
        }
        
        // Check IP reachability
        const reachable = this.isIPReachable(sourceConfig, targetConfig);
        if (!reachable.success) {
            return {
                success: false,
                message: reachable.message,
                details: reachable.details
            };
        }
        
        return {
            success: true,
            message: `Ping successful: ${sourceDevice.name} → ${targetDevice.name}`,
            details: `${sourceConfig.ipAddress} → ${targetConfig.ipAddress} (${reachable.latency}ms)`
        };
    }

    async performRoutingTest(router) {
        const config = this.getDeviceConfiguration(router.id);
        
        if (!config || !config.ipAddress) {
            return {
                success: false,
                message: `Router ${router.name} has no IP configuration`,
                details: 'Router must be configured before routing tests'
            };
        }
        
        // Check if router has routing table configured
        if (!config.routes || config.routes.length === 0) {
            return {
                success: false,
                message: `Router ${router.name} has no routing table`,
                details: 'Router must have at least one route configured'
            };
        }
        
        // Validate routes
        const routeValidation = this.validateRoutes(config.routes);
        if (!routeValidation.valid) {
            return {
                success: false,
                message: `Invalid routes on ${router.name}`,
                details: routeValidation.message
            };
        }
        
        return {
            success: true,
            message: `Routing table valid on ${router.name}`,
            details: `${config.routes.length} routes configured`
        };
    }

    getDeviceConfiguration(deviceId) {
        // Try to get configuration from IP manager if available
        if (window.ipManager && window.ipManager.networkConfigs) {
            return window.ipManager.networkConfigs.get(deviceId);
        }
        
        // Fall back to device config
        const device = window.editor?.devices?.find(d => d.id === deviceId);
        return device?.config || null;
    }

    hasPhysicalPath(sourceDevice, targetDevice) {
        if (!window.editor || !window.editor.connections) return false;
        
        // Build adjacency list
        const graph = new Map();
        window.editor.devices.forEach(device => {
            graph.set(device.id, []);
        });
        
        window.editor.connections.forEach(connection => {
            graph.get(connection.source)?.push(connection.target);
            graph.get(connection.target)?.push(connection.source);
        });
        
        // BFS to find path
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

    isIPReachable(sourceConfig, targetConfig) {
        const sourceIP = this.parseIP(sourceConfig.ipAddress);
        const targetIP = this.parseIP(targetConfig.ipAddress);
        const sourceMask = this.parseIP(sourceConfig.subnetMask || '255.255.255.0');
        const targetMask = this.parseIP(targetConfig.subnetMask || '255.255.255.0');
        
        // Check if in same subnet
        const sourceNetwork = sourceIP & sourceMask;
        const targetNetwork = targetIP & targetMask;
        
        if (sourceNetwork === targetNetwork) {
            return {
                success: true,
                latency: Math.floor(Math.random() * 10) + 1
            };
        }
        
        // Check if routing is available
        if (sourceConfig.gateway && targetConfig.gateway) {
            return {
                success: true,
                latency: Math.floor(Math.random() * 50) + 10
            };
        }
        
        return {
            success: false,
            message: 'Devices are on different subnets with no gateway configured',
            details: 'Configure gateways for inter-subnet communication'
        };
    }

    parseIP(ipString) {
        const parts = ipString.split('.').map(Number);
        return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3];
    }

    validateRoutes(routes) {
        for (const route of routes) {
            if (!route.destination || !route.gateway || !route.interface) {
                return {
                    valid: false,
                    message: 'Route missing required fields (destination, gateway, interface)'
                };
            }
            
            // Validate IP format
            if (!this.isValidIPFormat(route.destination) || !this.isValidIPFormat(route.gateway)) {
                return {
                    valid: false,
                    message: 'Invalid IP address format in route'
                };
            }
        }
        
        return { valid: true };
    }

    isValidIPFormat(ip) {
        const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipRegex.test(ip);
    }

    checkConfigurationCompletion() {
        this.completedConfigurations.clear();
        
        window.editor?.devices?.forEach(device => {
            if (this.requiresConfiguration(device)) {
                const config = this.getDeviceConfiguration(device.id);
                
                if (config && config.ipAddress) {
                    this.completedConfigurations.add(`${device.id}_ip`);
                }
                
                if (config && config.mode) {
                    this.completedConfigurations.add(`${device.id}_mode`);
                }
                
                if (device.type === 'router' && config && config.routes && config.routes.length > 0) {
                    this.completedConfigurations.add(`${device.id}_routing`);
                }
                
                if (device.type === 'switch' && config && config.vlans) {
                    this.completedConfigurations.add(`${device.id}_vlan`);
                }
            }
        });
        
        this.updateConfigurationDisplay();
    }

    updateConfigurationDisplay() {
        const content = document.getElementById('config-requirements');
        const status = document.getElementById('config-status');
        
        if (!content || !status) return;
        
        const total = this.requiredConfigurations.size;
        const completed = this.completedConfigurations.size;
        
        status.textContent = `${completed}/${total}`;
        
        content.innerHTML = '';
        
        this.requiredConfigurations.forEach(reqId => {
            const isCompleted = this.completedConfigurations.has(reqId);
            const [deviceId, configType] = reqId.split('_');
            const device = window.editor?.devices?.find(d => d.id === deviceId);
            
            const item = document.createElement('div');
            item.className = 'requirement-item';
            item.innerHTML = `
                <div class="requirement-icon ${isCompleted ? 'completed' : 'pending'}">
                    <i class="fas ${isCompleted ? 'fa-check' : 'fa-clock'}"></i>
                </div>
                <span>${device?.name || deviceId}: ${this.getConfigTypeName(configType)}</span>
            `;
            
            content.appendChild(item);
        });
    }

    updatePhysicalDisplay(issues, warnings) {
        const content = document.getElementById('physical-requirements');
        const status = document.getElementById('physical-status');
        
        if (!content || !status) return;
        
        const totalConnections = window.editor?.connections?.length || 0;
        const validConnections = totalConnections - issues.length;
        
        status.textContent = `${validConnections}/${totalConnections}`;
        
        content.innerHTML = '';
        
        if (issues.length === 0 && warnings.length === 0) {
            content.innerHTML = `
                <div class="requirement-item">
                    <div class="requirement-icon completed">
                        <i class="fas fa-check"></i>
                    </div>
                    <span>All connections valid</span>
                </div>
            `;
        } else {
            [...issues, ...warnings].forEach(message => {
                const item = document.createElement('div');
                item.className = 'requirement-item';
                item.innerHTML = `
                    <div class="requirement-icon ${issues.includes(message) ? 'failed' : 'pending'}">
                        <i class="fas ${issues.includes(message) ? 'fa-times' : 'fa-exclamation'}"></i>
                    </div>
                    <span>${message}</span>
                `;
                content.appendChild(item);
            });
        }
    }

    updateConnectivityDisplay() {
        const content = document.getElementById('connectivity-tests');
        const status = document.getElementById('connectivity-status');
        
        if (!content || !status) return;
        
        const total = this.connectivityTests.size;
        const passed = Array.from(this.connectivityTests.values()).filter(t => t.status === 'passed').length;
        
        status.textContent = `${passed}/${total}`;
        
        content.innerHTML = '';
        
        this.connectivityTests.forEach((test, testId) => {
            this.updateTestDisplay(testId, test);
        });
        
        // Update run tests button state
        const runButton = document.getElementById('run-connectivity-tests');
        if (runButton) {
            const allConfigured = this.completedConfigurations.size === this.requiredConfigurations.size;
            const physicalValid = this.validatePhysicalConnections().valid;
            runButton.disabled = !(allConfigured && physicalValid);
        }
    }

    updateTestDisplay(testId, test) {
        const content = document.getElementById('connectivity-tests');
        if (!content) return;
        
        let item = document.getElementById(`test-${testId}`);
        if (!item) {
            item = document.createElement('div');
            item.id = `test-${testId}`;
            item.className = 'requirement-item';
            content.appendChild(item);
        }
        
        const statusIcon = test.status === 'passed' ? 'fa-check' : 
                          test.status === 'failed' ? 'fa-times' : 
                          test.status === 'running' ? 'fa-spinner fa-spin' : 'fa-clock';
        
        const statusClass = test.status === 'passed' ? 'completed' : 
                           test.status === 'failed' ? 'failed' : 'pending';
        
        let testName = '';
        if (test.type === 'ping') {
            testName = `Ping: ${test.source.name} → ${test.target.name}`;
        } else if (test.type === 'routing') {
            testName = `Routing: ${test.device.name}`;
        }
        
        item.innerHTML = `
            <div class="requirement-icon ${statusClass}">
                <i class="fas ${statusIcon}"></i>
            </div>
            <div>
                <span>${testName}</span>
                ${test.result ? `<div class="test-result ${test.status === 'passed' ? 'success' : 'failed'}">
                    ${test.result.message}
                    ${test.result.details ? `<br><small>${test.result.details}</small>` : ''}
                </div>` : ''}
            </div>
        `;
    }

    updateOverallStatus(allTestsPassed) {
        const statusElement = document.getElementById('overall-validation-status');
        if (!statusElement) return;
        
        const statusText = statusElement.querySelector('.status-text');
        const statusIndicator = statusElement.querySelector('.status-indicator');
        
        const allConfigured = this.completedConfigurations.size === this.requiredConfigurations.size;
        const physicalValid = this.validatePhysicalConnections().valid;
        
        if (allTestsPassed && allConfigured && physicalValid) {
            statusText.textContent = 'Working';
            statusIndicator.className = 'status-indicator working';
        } else if (allConfigured && physicalValid) {
            statusText.textContent = 'Ready for Testing';
            statusIndicator.className = 'status-indicator connected';
        } else if (allConfigured) {
            statusText.textContent = 'Configured';
            statusIndicator.className = 'status-indicator configured';
        } else {
            statusText.textContent = 'Not Ready';
            statusIndicator.className = 'status-indicator disconnected';
        }

        // Auto-save validation state changes
        this.autoSaveConfiguration();
    }

    getConfigTypeName(configType) {
        const names = {
            ip: 'IP Configuration',
            mode: 'Device Mode',
            routing: 'Routing Table',
            vlan: 'VLAN Configuration'
        };
        return names[configType] || configType;
    }

    attachEventListeners() {
        // Save validation configuration
        document.getElementById('save-validation-config')?.addEventListener('click', () => {
            this.saveEnhancedValidationConfig();
        });

        // Run connectivity tests
        document.getElementById('run-connectivity-tests')?.addEventListener('click', () => {
            this.runConnectivityTests();
        });
        
        // Reset validation
        document.getElementById('reset-validation')?.addEventListener('click', () => {
            this.resetValidation();
        });
        
        // Listen for editor changes
        if (window.editor) {
            // Override editor methods to trigger validation updates
            const originalAddDevice = window.editor.addDevice;
            if (originalAddDevice) {
                window.editor.addDevice = (...args) => {
                    const result = originalAddDevice.apply(window.editor, args);
                    this.onTopologyChanged();
                    return result;
                };
            }
            
            const originalRemoveDevice = window.editor.removeDevice;
            if (originalRemoveDevice) {
                window.editor.removeDevice = (...args) => {
                    const result = originalRemoveDevice.apply(window.editor, args);
                    this.onTopologyChanged();
                    return result;
                };
            }
        }
        
        // Listen for IP configuration changes
        if (window.ipManager) {
            document.addEventListener('configurationUpdated', () => {
                this.checkConfigurationCompletion();
            });
        }
    }

    onTopologyChanged() {
        setTimeout(() => {
            this.setupConfigurationRequirements();
            this.setupConnectivityTests();
            this.validatePhysicalConnections();
            this.checkConfigurationCompletion();
        }, 100);
    }

    resetValidation() {
        this.connectivityTests.forEach(test => {
            test.status = 'pending';
            test.result = null;
        });
        
        this.updateConnectivityDisplay();
        this.updateOverallStatus(false);
    }

    // Public API for integration with existing simulation system
    isSimulationValid() {
        const allConfigured = this.completedConfigurations.size === this.requiredConfigurations.size;
        const physicalValid = this.validatePhysicalConnections().valid;
        const allTestsPassed = Array.from(this.connectivityTests.values()).every(t => t.status === 'passed');
        
        return allConfigured && physicalValid && allTestsPassed;
    }

    getValidationReport() {
        return {
            configured: this.completedConfigurations.size === this.requiredConfigurations.size,
            physicallyValid: this.validatePhysicalConnections().valid,
            connectivityPassed: Array.from(this.connectivityTests.values()).every(t => t.status === 'passed'),
            totalTests: this.connectivityTests.size,
            passedTests: Array.from(this.connectivityTests.values()).filter(t => t.status === 'passed').length,
            overallValid: this.isSimulationValid()
        };
    }

    // Save enhanced validation configuration to backend
    saveEnhancedValidationConfig() {
        const simulationId = window.simulationId || window.simulation?.id;
        if (!simulationId) {
            console.warn('No simulation ID found for saving enhanced validation config');
            return;
        }

        const enhancedConfig = {
            enhanced_validation: {
                configuration_requirements: {
                    require_ip_assignment: this.requireIPAssignment || true,
                    require_device_modes: this.requireDeviceModes || true,
                    require_cable_configuration: this.requireCableConfiguration || true,
                    enforce_full_configuration: this.enforceFullConfiguration || true
                },
                physical_validation: {
                    enforce_compatible_connections: this.enforceCompatibleConnections || true,
                    validate_device_capabilities: this.validateDeviceCapabilities || true,
                    check_cable_types: this.checkCableTypes || true,
                    connection_rules: this.physicalConnectionRules || []
                },
                connectivity_tests: {
                    require_ping_tests: this.requirePingTests || true,
                    require_route_validation: this.requireRouteValidation || true,
                    require_connectivity_matrix: this.requireConnectivityMatrix || true,
                    required_tests: Array.from(this.connectivityTests.values()).map(test => ({
                        source: test.source,
                        target: test.target,
                        test_type: test.type,
                        expected_result: test.expectedResult,
                        description: test.description
                    }))
                },
                validation_states: {
                    CONFIGURED: {
                        requirements: ['All devices must be configured', 'IP addresses assigned'],
                        validation_criteria: {
                            min_devices_configured: this.minDevicesConfigured || 0,
                            min_connections_validated: 0,
                            min_tests_passed: 0
                        }
                    },
                    CONNECTED: {
                        requirements: ['Physical connections established', 'Cable types validated'],
                        validation_criteria: {
                            min_devices_configured: this.minDevicesConfigured || 0,
                            min_connections_validated: this.minConnectionsValidated || 0,
                            min_tests_passed: 0
                        }
                    },
                    VALIDATED: {
                        requirements: ['Connectivity tests passed', 'Network functionality verified'],
                        validation_criteria: {
                            min_devices_configured: this.minDevicesConfigured || 0,
                            min_connections_validated: this.minConnectionsValidated || 0,
                            min_tests_passed: this.minTestsPassed || 1
                        }
                    },
                    WORKING: {
                        requirements: ['Full network operational', 'All validation criteria met'],
                        validation_criteria: {
                            min_devices_configured: this.minDevicesConfigured || 0,
                            min_connections_validated: this.minConnectionsValidated || 0,
                            min_tests_passed: this.minTestsPassed || 1
                        }
                    }
                }
            }
        };

        const updateData = {
            simulation_config: enhancedConfig,
            validation_rules: {
                enhanced_validation_states: enhancedConfig.enhanced_validation.validation_states
            }
        };

        // Save to backend
        fetch(`/admin/simulation/api/${simulationId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(updateData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Enhanced validation configuration saved successfully');
                this.showNotification('Enhanced validation configuration saved', 'success');
            } else {
                console.error('Failed to save enhanced validation configuration:', data.error);
                this.showNotification('Failed to save configuration: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error saving enhanced validation configuration:', error);
            this.showNotification('Error saving configuration', 'error');
        });
    }

    // Get CSRF token for secure requests
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    // Show notification to user
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `enhanced-validation-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            max-width: 300px;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Auto-save configuration when settings change
    autoSaveConfiguration() {
        // Debounce auto-save to avoid excessive requests
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.saveEnhancedValidationConfig();
        }, 2000); // Save 2 seconds after last change
    }

    // Load enhanced validation configuration from backend
    loadEnhancedValidationConfig() {
        const simulationId = window.simulationId || window.simulation?.id;
        if (!simulationId) {
            console.warn('No simulation ID found for loading enhanced validation config');
            return;
        }

        fetch(`/admin/simulation/api/${simulationId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.simulation) {
                const simulation = data.simulation;
                
                // Load simulation config if it exists
                if (simulation.simulation_config && simulation.simulation_config.enhanced_validation) {
                    const config = simulation.simulation_config.enhanced_validation;
                    
                    // Apply configuration requirements
                    if (config.configuration_requirements) {
                        const req = config.configuration_requirements;
                        this.requireIPAssignment = req.require_ip_assignment !== false;
                        this.requireDeviceModes = req.require_device_modes !== false;
                        this.requireCableConfiguration = req.require_cable_configuration !== false;
                        this.enforceFullConfiguration = req.enforce_full_configuration !== false;
                    }
                    
                    // Apply physical validation settings
                    if (config.physical_validation) {
                        const phy = config.physical_validation;
                        this.enforceCompatibleConnections = phy.enforce_compatible_connections !== false;
                        this.validateDeviceCapabilities = phy.validate_device_capabilities !== false;
                        this.checkCableTypes = phy.check_cable_types !== false;
                        this.physicalConnectionRules = phy.connection_rules || [];
                    }
                    
                    // Apply connectivity test settings
                    if (config.connectivity_tests) {
                        const conn = config.connectivity_tests;
                        this.requirePingTests = conn.require_ping_tests !== false;
                        this.requireRouteValidation = conn.require_route_validation !== false;
                        this.requireConnectivityMatrix = conn.require_connectivity_matrix !== false;
                        
                        // Load required test cases
                        if (conn.required_tests && Array.isArray(conn.required_tests)) {
                            conn.required_tests.forEach(test => {
                                this.connectivityTests.set(`${test.source}-${test.target}`, {
                                    source: test.source,
                                    target: test.target,
                                    type: test.test_type || 'ping',
                                    expectedResult: test.expected_result !== false,
                                    description: test.description || '',
                                    status: 'pending',
                                    result: null
                                });
                            });
                        }
                    }
                    
                    console.log('Enhanced validation configuration loaded successfully');
                    this.refreshValidationInterface();
                } else {
                    console.log('No enhanced validation configuration found, using defaults');
                }
            }
        })
        .catch(error => {
            console.error('Error loading enhanced validation configuration:', error);
        });
    }

    // Refresh the validation interface after loading configuration
    refreshValidationInterface() {
        // Update the validation panel to reflect loaded settings
        this.setupConfigurationRequirements();
        this.setupConnectivityTests();
        this.updateConnectivityDisplay();
        this.onTopologyChanged(); // Trigger validation update
    }
}

// Initialize enhanced validation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for editor to be available
    const initValidator = () => {
        if (window.editor) {
            window.enhancedValidator = new EnhancedSimulationValidator();
            console.log('✓ Enhanced Simulation Validator initialized');
        } else {
            setTimeout(initValidator, 500);
        }
    };
    
    initValidator();
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedSimulationValidator;
}

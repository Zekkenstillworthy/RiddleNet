/**
 * Enhanced Simulation Validation Core
 * Universal validation system for all simulation editors
 */

class UniversalSimulationValidator {
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
        
        this.initialize();
    }

    extractSimulationId() {
        // Extract simulation ID from URL or data attributes
        const urlMatch = window.location.pathname.match(/\/edit\/(\d+)/);
        if (urlMatch) return parseInt(urlMatch[1]);
        
        const dataAttr = document.querySelector('[data-simulation-id]');
        if (dataAttr) return parseInt(dataAttr.dataset.simulationId);
        
        return null;
    }

    async initialize() {
        await this.loadValidationConfiguration();
        this.createValidationInterface();
        this.setupValidationRequirements();
        this.attachEventListeners();
        this.startValidationLoop();
    }

    async loadValidationConfiguration() {
        if (!this.simulationId) {
            console.warn('No simulation ID available, using default configuration');
            this.useDefaultConfiguration();
            return;
        }

        try {
            const response = await fetch(`/admin/simulation/edit/${this.simulationId}/validation/config`);
            if (response.ok) {
                const data = await response.json();
                this.validationConfig = data.validation_config;
                this.deviceRequirements = data.device_requirements;
                this.connectionRules = data.connection_rules;
            } else {
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

    createValidationInterface() {
        // Remove existing panel if present
        const existingPanel = document.getElementById('universal-validation-panel');
        if (existingPanel) {
            existingPanel.remove();
        }

        // Create validation panel with enhanced design
        const validationPanel = document.createElement('div');
        validationPanel.id = 'universal-validation-panel';
        
        validationPanel.innerHTML = `
            <div class="validation-header">
                <h3><i class="fas fa-shield-alt"></i> Network Validation</h3>
                <div class="validation-controls">
                    <button class="save-config-btn" id="save-validation-config">
                        <i class="fas fa-save"></i> Save Config
                    </button>
                    <div class="overall-status" id="overall-status">
                        <span class="status-text">Not Ready</span>
                        <div class="status-indicator disconnected"></div>
                    </div>
                </div>
            </div>
            
            <!-- State Machine Display -->
            <div class="state-machine">
                <div class="state-progress">
                    <div class="state-step" data-state="disconnected">
                        <div class="step-icon"><i class="fas fa-times"></i></div>
                        <span>Disconnected</span>
                    </div>
                    <div class="progress-line"></div>
                    <div class="state-step" data-state="configured">
                        <div class="step-icon"><i class="fas fa-cog"></i></div>
                        <span>Configured</span>
                    </div>
                    <div class="progress-line"></div>
                    <div class="state-step" data-state="connected">
                        <div class="step-icon"><i class="fas fa-link"></i></div>
                        <span>Connected</span>
                    </div>
                    <div class="progress-line"></div>
                    <div class="state-step" data-state="validated">
                        <div class="step-icon"><i class="fas fa-check"></i></div>
                        <span>Validated</span>
                    </div>
                    <div class="progress-line"></div>
                    <div class="state-step" data-state="working">
                        <div class="step-icon"><i class="fas fa-check-double"></i></div>
                        <span>Working</span>
                    </div>
                </div>
            </div>

            <!-- Validation Sections -->
            <div class="validation-content">
                <!-- Configuration Section -->
                <div class="validation-section" id="config-section">
                    <div class="section-header" onclick="this.parentElement.classList.toggle('collapsed')">
                        <i class="fas fa-cogs"></i>
                        <span>Configuration</span>
                        <div class="section-counter" id="config-counter">0/0</div>
                        <i class="fas fa-chevron-down expand-icon"></i>
                    </div>
                    <div class="section-body" id="config-requirements"></div>
                </div>

                <!-- Physical Connections Section -->
                <div class="validation-section" id="physical-section">
                    <div class="section-header" onclick="this.parentElement.classList.toggle('collapsed')">
                        <i class="fas fa-plug"></i>
                        <span>Physical Connections</span>
                        <div class="section-counter" id="physical-counter">0/0</div>
                        <i class="fas fa-chevron-down expand-icon"></i>
                    </div>
                    <div class="section-body" id="physical-requirements"></div>
                </div>

                <!-- Connectivity Tests Section -->
                <div class="validation-section" id="tests-section">
                    <div class="section-header" onclick="this.parentElement.classList.toggle('collapsed')">
                        <i class="fas fa-network-wired"></i>
                        <span>Connectivity Tests</span>
                        <div class="section-counter" id="tests-counter">0/0</div>
                        <i class="fas fa-chevron-down expand-icon"></i>
                    </div>
                    <div class="section-body" id="connectivity-tests"></div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="validation-actions">
                <button id="run-tests-btn" class="action-btn primary" disabled>
                    <i class="fas fa-play"></i> Run Tests
                </button>
                <button id="reset-validation-btn" class="action-btn secondary">
                    <i class="fas fa-redo"></i> Reset
                </button>
            </div>
        `;

        // Add comprehensive styles
        this.addValidationStyles();
        
        // Find appropriate container and add panel
        this.findValidationContainer().appendChild(validationPanel);
        
        console.log('Universal validation interface created');
    }

    addValidationStyles() {
        if (document.getElementById('universal-validation-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'universal-validation-styles';
        styles.textContent = `
            #universal-validation-panel {
                position: fixed;
                top: 80px;
                right: 20px;
                width: 380px;
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9));
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 16px;
                backdrop-filter: blur(20px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(59, 130, 246, 0.2);
                z-index: 10000;
                color: white;
                font-family: 'Segoe UI', system-ui, sans-serif;
                max-height: calc(100vh - 100px);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                animation: slideInRight 0.5s ease-out;
            }

            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            .validation-header {
                padding: 20px;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2));
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .validation-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
                color: #00D9FF;
                text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
            }

            .validation-controls {
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .save-config-btn {
                background: linear-gradient(135deg, #3B82F6, #8B5CF6);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 6px;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }

            .save-config-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
            }

            .overall-status {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 13px;
                font-weight: 600;
            }

            .status-indicator {
                width: 14px;
                height: 14px;
                border-radius: 50%;
                transition: all 0.3s ease;
                box-shadow: 0 0 10px currentColor;
            }

            .status-indicator.disconnected {
                background: #EF4444;
                box-shadow: 0 0 10px rgba(239, 68, 68, 0.6);
            }

            .status-indicator.configured {
                background: #F59E0B;
                box-shadow: 0 0 10px rgba(245, 158, 11, 0.6);
            }

            .status-indicator.connected {
                background: #3B82F6;
                box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
            }

            .status-indicator.validated {
                background: #8B5CF6;
                box-shadow: 0 0 10px rgba(139, 92, 246, 0.6);
            }

            .status-indicator.working {
                background: #10B981;
                box-shadow: 0 0 10px rgba(16, 185, 129, 0.6);
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }

            .state-machine {
                padding: 20px;
                background: rgba(255, 255, 255, 0.02);
            }

            .state-progress {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .state-step {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
                opacity: 0.4;
                transition: all 0.4s ease;
                flex: 1;
            }

            .state-step.active {
                opacity: 1;
                transform: scale(1.1);
            }

            .state-step.completed {
                opacity: 1;
            }

            .step-icon {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.1);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }

            .state-step.active .step-icon {
                background: linear-gradient(135deg, #3B82F6, #8B5CF6);
                border-color: #00D9FF;
                box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
            }

            .state-step.completed .step-icon {
                background: linear-gradient(135deg, #10B981, #39FF14);
                border-color: #39FF14;
            }

            .state-step span {
                font-size: 11px;
                font-weight: 500;
                text-align: center;
                line-height: 1.2;
            }

            .progress-line {
                flex: 1;
                height: 2px;
                background: rgba(255, 255, 255, 0.1);
                margin: 0 8px;
                border-radius: 1px;
                position: relative;
            }

            .progress-line::after {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                background: linear-gradient(90deg, #3B82F6, #8B5CF6);
                border-radius: 1px;
                width: 0%;
                transition: width 0.5s ease;
            }

            .validation-content {
                flex: 1;
                overflow-y: auto;
                padding: 0 20px;
            }

            .validation-section {
                margin-bottom: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.02);
                transition: all 0.3s ease;
            }

            .validation-section:hover {
                border-color: rgba(59, 130, 246, 0.4);
                box-shadow: 0 0 15px rgba(59, 130, 246, 0.1);
            }

            .section-header {
                padding: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                cursor: pointer;
                transition: all 0.2s ease;
                border-radius: 12px 12px 0 0;
            }

            .section-header:hover {
                background: rgba(255, 255, 255, 0.05);
            }

            .section-header i:first-child {
                color: #3B82F6;
                font-size: 16px;
                width: 20px;
            }

            .section-header span {
                flex: 1;
                font-weight: 600;
                font-size: 14px;
            }

            .section-counter {
                background: rgba(59, 130, 246, 0.2);
                color: #00D9FF;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                border: 1px solid rgba(59, 130, 246, 0.3);
            }

            .expand-icon {
                color: #94A3B8;
                font-size: 12px;
                transition: transform 0.3s ease;
            }

            .validation-section.collapsed .expand-icon {
                transform: rotate(-90deg);
            }

            .section-body {
                padding: 0 16px 16px;
                max-height: 300px;
                overflow: hidden;
                transition: all 0.3s ease;
            }

            .validation-section.collapsed .section-body {
                max-height: 0;
                padding: 0 16px;
            }

            .requirement-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                margin-bottom: 8px;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                border-left: 3px solid transparent;
                transition: all 0.2s ease;
            }

            .requirement-item:hover {
                background: rgba(255, 255, 255, 0.06);
            }

            .requirement-item.valid {
                border-left-color: #10B981;
                background: rgba(16, 185, 129, 0.1);
            }

            .requirement-item.invalid {
                border-left-color: #EF4444;
                background: rgba(239, 68, 68, 0.1);
            }

            .requirement-status {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                font-weight: bold;
                flex-shrink: 0;
            }

            .requirement-status.pending {
                background: rgba(156, 163, 175, 0.3);
                color: #9CA3AF;
            }

            .requirement-status.valid {
                background: #10B981;
                color: white;
            }

            .requirement-status.invalid {
                background: #EF4444;
                color: white;
            }

            .requirement-text {
                flex: 1;
            }

            .requirement-title {
                font-weight: 500;
                font-size: 13px;
                line-height: 1.4;
            }

            .requirement-description {
                font-size: 11px;
                color: #94A3B8;
                margin-top: 2px;
            }

            .validation-actions {
                padding: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                gap: 12px;
                background: rgba(255, 255, 255, 0.02);
                border-radius: 0 0 16px 16px;
            }

            .action-btn {
                flex: 1;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }

            .action-btn.primary {
                background: linear-gradient(135deg, #10B981, #39FF14);
                color: white;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            }

            .action-btn.primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
            }

            .action-btn.secondary {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .action-btn.secondary:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(59, 130, 246, 0.5);
            }

            .action-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none !important;
            }

            /* Test Results */
            .test-result {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px;
                margin-bottom: 6px;
                border-radius: 8px;
                font-size: 12px;
                background: rgba(255, 255, 255, 0.03);
                border-left: 3px solid transparent;
                transition: all 0.2s ease;
            }

            .test-result.pass {
                border-left-color: #10B981;
                background: rgba(16, 185, 129, 0.1);
            }

            .test-result.fail {
                border-left-color: #EF4444;
                background: rgba(239, 68, 68, 0.1);
            }

            .test-result.pending {
                border-left-color: #F59E0B;
                background: rgba(245, 158, 11, 0.1);
            }

            .test-icon {
                width: 18px;
                height: 18px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                color: white;
                flex-shrink: 0;
            }

            .test-result.pass .test-icon {
                background: #10B981;
            }

            .test-result.fail .test-icon {
                background: #EF4444;
            }

            .test-result.pending .test-icon {
                background: #F59E0B;
            }

            /* Responsive Design */
            @media (max-width: 1400px) {
                #universal-validation-panel {
                    width: 320px;
                }
            }

            @media (max-width: 1200px) {
                #universal-validation-panel {
                    width: 280px;
                    right: 10px;
                }
            }

            @media (max-width: 768px) {
                #universal-validation-panel {
                    position: relative;
                    width: 100%;
                    right: auto;
                    top: auto;
                    margin: 20px 0;
                    max-height: none;
                    border-radius: 12px;
                }
            }
        `;

        document.head.appendChild(styles);
    }

    findValidationContainer() {
        const containers = [
            document.querySelector('.editor-workspace'),
            document.querySelector('.simulation-editor'),
            document.querySelector('.troubleshooting-editor'),
            document.querySelector('main'),
            document.body
        ];
        
        return containers.find(container => container !== null) || document.body;
    }

    setupValidationRequirements() {
        this.setupConfigurationRequirements();
        this.setupPhysicalRequirements();
        this.setupConnectivityTests();
    }

    setupConfigurationRequirements() {
        const configSection = document.getElementById('config-requirements');
        if (!configSection) return;
        
        configSection.innerHTML = '';
        this.requiredConfigurations.clear();
        
        if (!this.validationConfig) return;
        
        const requirements = this.validationConfig.configuration_requirements;
        
        if (requirements.require_ip_assignment) {
            this.addRequirement('config', 'ip_assignment', 'IP Address Assignment', 'All devices must have valid IP configurations');
        }
        
        if (requirements.require_device_modes) {
            this.addRequirement('config', 'device_modes', 'Device Mode Configuration', 'Devices must be configured with appropriate roles/modes');
        }
        
        if (requirements.require_cable_configuration) {
            this.addRequirement('config', 'cable_config', 'Cable Configuration', 'Physical connections must specify cable types');
        }
        
        if (requirements.require_interface_config) {
            this.addRequirement('config', 'interface_config', 'Interface Configuration', 'Network interfaces must be properly configured');
        }
        
        this.updateSectionCounter('config');
    }

    setupPhysicalRequirements() {
        const physicalSection = document.getElementById('physical-requirements');
        if (!physicalSection) return;
        
        physicalSection.innerHTML = '';
        
        // Physical requirements are dynamic based on current topology
        this.updatePhysicalValidation();
    }

    setupConnectivityTests() {
        const testsSection = document.getElementById('connectivity-tests');
        if (!testsSection) return;
        
        testsSection.innerHTML = '';
        this.connectivityTests.clear();
        
        if (!this.validationConfig) return;
        
        const testConfig = this.validationConfig.connectivity_tests;
        
        if (testConfig.require_ping_tests) {
            this.addTest('ping_tests', 'Basic Ping Tests', 'Test connectivity between end devices');
        }
        
        if (testConfig.require_route_validation) {
            this.addTest('route_validation', 'Route Validation', 'Verify routing table entries');
        }
        
        if (testConfig.require_connectivity_matrix) {
            this.addTest('connectivity_matrix', 'Full Connectivity Matrix', 'Test all possible device pairs');
        }
        
        this.updateSectionCounter('tests');
    }

    addRequirement(section, id, title, description) {
        const sectionElement = document.getElementById(`${section}-requirements`);
        if (!sectionElement) return;
        
        this.requiredConfigurations.add(id);
        
        const reqElement = document.createElement('div');
        reqElement.className = 'requirement-item';
        reqElement.id = `req-${id}`;
        reqElement.innerHTML = `
            <div class="requirement-status pending" id="status-${id}">
                <i class="fas fa-clock"></i>
            </div>
            <div class="requirement-text">
                <div class="requirement-title">${title}</div>
                <div class="requirement-description">${description}</div>
            </div>
        `;
        
        sectionElement.appendChild(reqElement);
    }

    addTest(id, title, description) {
        const testsSection = document.getElementById('connectivity-tests');
        if (!testsSection) return;
        
        const testElement = document.createElement('div');
        testElement.className = 'test-result pending';
        testElement.id = `test-${id}`;
        testElement.innerHTML = `
            <div class="test-icon">
                <i class="fas fa-clock"></i>
            </div>
            <div class="test-details">
                <div class="test-title">${title}</div>
                <div class="test-description">${description}</div>
            </div>
        `;
        
        testsSection.appendChild(testElement);
        this.connectivityTests.set(id, { status: 'pending', result: null });
    }

    attachEventListeners() {
        // Save configuration
        document.getElementById('save-validation-config')?.addEventListener('click', () => {
            this.saveValidationConfiguration();
        });

        // Run tests
        document.getElementById('run-tests-btn')?.addEventListener('click', () => {
            this.runConnectivityTests();
        });
        
        // Reset validation
        document.getElementById('reset-validation-btn')?.addEventListener('click', () => {
            this.resetValidation();
        });
        
        // Hook into editor changes
        this.hookIntoEditorEvents();
    }

    hookIntoEditorEvents() {
        // Hook into existing editor systems
        if (window.editor) {
            const originalMethods = ['addDevice', 'removeDevice', 'addConnection', 'removeConnection', 'updateDevice'];
            
            originalMethods.forEach(method => {
                if (window.editor[method]) {
                    const original = window.editor[method];
                    window.editor[method] = (...args) => {
                        const result = original.apply(window.editor, args);
                        this.onTopologyChanged();
                        return result;
                    };
                }
            });
        }

        // Listen for DOM changes in canvas area
        const observer = new MutationObserver(() => {
            this.onTopologyChanged();
        });

        const canvasArea = this.findCanvasArea();
        if (canvasArea) {
            observer.observe(canvasArea, { 
                childList: true, 
                subtree: true, 
                attributes: true 
            });
        }
    }

    findCanvasArea() {
        const selectors = [
            '.canvas-area',
            '.editor-canvas',
            '#simulation-canvas',
            '.network-canvas',
            '.topology-canvas'
        ];
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) return element;
        }
        
        return null;
    }

    startValidationLoop() {
        // Run validation every 3 seconds
        setInterval(() => {
            this.performValidation();
        }, 3000);
        
        // Initial validation
        setTimeout(() => {
            this.performValidation();
        }, 1000);
    }

    async onTopologyChanged() {
        // Debounce topology changes
        clearTimeout(this.topologyTimeout);
        this.topologyTimeout = setTimeout(() => {
            this.performValidation();
        }, 500);
    }

    async performValidation() {
        if (!this.simulationId) return;
        
        const topologyData = this.extractTopologyData();
        await this.validateSimulationState(topologyData);
    }

    extractTopologyData() {
        const topology = {
            devices: [],
            connections: []
        };

        // Try multiple methods to extract topology
        if (window.editor && window.editor.devices) {
            topology.devices = window.editor.devices.map(device => ({
                id: device.id,
                name: device.name || device.id,
                type: device.type,
                config: device.config || {},
                x: device.x || 0,
                y: device.y || 0
            }));
        }

        if (window.editor && window.editor.connections) {
            topology.connections = window.editor.connections.map(conn => ({
                source: conn.source,
                target: conn.target,
                cable_type: conn.cable_type || conn.type || 'ethernet'
            }));
        }

        // Fallback: extract from DOM
        if (topology.devices.length === 0) {
            const deviceElements = document.querySelectorAll('[data-device-id], .device, .network-device');
            deviceElements.forEach(el => {
                const deviceId = el.dataset.deviceId || el.id;
                const deviceType = el.dataset.deviceType || this.inferDeviceType(el);
                
                if (deviceId && deviceType) {
                    topology.devices.push({
                        id: deviceId,
                        name: el.dataset.deviceName || deviceId,
                        type: deviceType,
                        config: {},
                        x: parseInt(el.style.left) || 0,
                        y: parseInt(el.style.top) || 0
                    });
                }
            });
        }

        return topology;
    }

    inferDeviceType(element) {
        const classList = element.className.toLowerCase();
        const typeMap = {
            'pc': 'pc',
            'computer': 'pc',
            'server': 'server',
            'router': 'router',
            'switch': 'switch',
            'access-point': 'access-point',
            'ap': 'access-point'
        };
        
        for (const [key, type] of Object.entries(typeMap)) {
            if (classList.includes(key)) return type;
        }
        
        return 'unknown';
    }

    async validateSimulationState(topologyData) {
        if (!this.simulationId) return;

        try {
            const response = await fetch(`/admin/simulation/edit/${this.simulationId}/validation/state`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(topologyData)
            });

            if (response.ok) {
                const result = await response.json();
                this.updateValidationDisplay(result.validation_results);
            }
        } catch (error) {
            console.error('Error validating simulation state:', error);
        }
    }

    updateValidationDisplay(validationResults) {
        // Update overall state
        this.currentState = validationResults.overall_state;
        this.updateOverallStatus();
        this.updateStateMachine();

        // Update individual sections
        this.updateConfigurationStatus(validationResults);
        this.updatePhysicalStatus(validationResults);
        this.updateTestsStatus(validationResults);

        // Enable/disable run tests button
        const runTestsBtn = document.getElementById('run-tests-btn');
        if (runTestsBtn) {
            runTestsBtn.disabled = !validationResults.configuration_valid || !validationResults.physical_valid;
        }
    }

    updateOverallStatus() {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        
        if (statusIndicator && statusText) {
            // Remove all state classes
            Object.values(this.validationStates).forEach(state => {
                statusIndicator.classList.remove(state);
            });
            
            statusIndicator.classList.add(this.currentState);
            
            const stateLabels = {
                disconnected: 'Not Ready',
                configured: 'Configured',
                connected: 'Connected',
                validated: 'Validated',
                working: 'Working'
            };
            
            statusText.textContent = stateLabels[this.currentState] || 'Unknown';
        }
    }

    updateStateMachine() {
        const stateSteps = document.querySelectorAll('.state-step');
        const states = ['disconnected', 'configured', 'connected', 'validated', 'working'];
        const currentIndex = states.indexOf(this.currentState);
        
        stateSteps.forEach((step, index) => {
            step.classList.remove('active', 'completed');
            
            if (index < currentIndex) {
                step.classList.add('completed');
            } else if (index === currentIndex) {
                step.classList.add('active');
            }
        });
        
        // Update progress lines
        const progressLines = document.querySelectorAll('.progress-line');
        progressLines.forEach((line, index) => {
            const percentage = Math.min(100, Math.max(0, (currentIndex - index) * 100));
            line.style.setProperty('--progress', `${percentage}%`);
        });
    }

    updateConfigurationStatus(validationResults) {
        // Update section counter
        const total = this.requiredConfigurations.size;
        const completed = validationResults.configuration_valid ? total : 0;
        this.updateSectionCounter('config', completed, total);

        // Update individual requirements
        this.requiredConfigurations.forEach(reqId => {
            const statusElement = document.getElementById(`status-${reqId}`);
            const reqElement = document.getElementById(`req-${reqId}`);
            
            if (statusElement && reqElement) {
                const isValid = validationResults.configuration_valid;
                statusElement.className = `requirement-status ${isValid ? 'valid' : 'pending'}`;
                statusElement.innerHTML = `<i class="fas fa-${isValid ? 'check' : 'clock'}"></i>`;
                reqElement.className = `requirement-item ${isValid ? 'valid' : ''}`;
            }
        });
    }

    updatePhysicalStatus(validationResults) {
        const connectionStatuses = validationResults.connection_statuses || {};
        const total = Object.keys(connectionStatuses).length;
        const valid = Object.values(connectionStatuses).filter(status => status.valid).length;
        
        this.updateSectionCounter('physical', valid, total);
        this.updatePhysicalRequirements(connectionStatuses);
    }

    updatePhysicalRequirements(connectionStatuses) {
        const physicalSection = document.getElementById('physical-requirements');
        if (!physicalSection) return;
        
        physicalSection.innerHTML = '';
        
        Object.entries(connectionStatuses).forEach(([connId, status]) => {
            const reqElement = document.createElement('div');
            reqElement.className = `requirement-item ${status.valid ? 'valid' : 'invalid'}`;
            reqElement.innerHTML = `
                <div class="requirement-status ${status.valid ? 'valid' : 'invalid'}">
                    <i class="fas fa-${status.valid ? 'check' : 'times'}"></i>
                </div>
                <div class="requirement-text">
                    <div class="requirement-title">Connection: ${connId}</div>
                    <div class="requirement-description">${status.errors.join(', ') || 'Valid connection'}</div>
                </div>
            `;
            physicalSection.appendChild(reqElement);
        });
    }

    updateTestsStatus(validationResults) {
        const testResults = validationResults.test_results || {};
        const total = Object.keys(testResults).length;
        const passed = Object.values(testResults).filter(result => result.result === 'pass').length;
        
        this.updateSectionCounter('tests', passed, total);
    }

    updateSectionCounter(section, completed = 0, total = 0) {
        const counter = document.getElementById(`${section}-counter`);
        if (counter) {
            counter.textContent = `${completed}/${total}`;
        }
    }

    async runConnectivityTests() {
        if (!this.simulationId) return;
        
        const topologyData = this.extractTopologyData();
        const testConfig = this.validationConfig?.connectivity_tests || {};
        
        try {
            const response = await fetch(`/admin/simulation/edit/${this.simulationId}/validation/tests`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topology: topologyData,
                    test_config: testConfig
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayTestResults(result.test_results);
                this.showToast('Connectivity tests completed', 'success');
            }
        } catch (error) {
            console.error('Error running connectivity tests:', error);
            this.showToast('Error running tests', 'error');
        }
    }

    displayTestResults(testResults) {
        const testsSection = document.getElementById('connectivity-tests');
        if (!testsSection) return;
        
        testsSection.innerHTML = '';
        
        Object.entries(testResults).forEach(([testId, result]) => {
            const testElement = document.createElement('div');
            testElement.className = `test-result ${result.result}`;
            testElement.innerHTML = `
                <div class="test-icon">
                    <i class="fas fa-${result.result === 'pass' ? 'check' : result.result === 'fail' ? 'times' : 'clock'}"></i>
                </div>
                <div class="test-details">
                    <div class="test-title">${result.type}: ${result.source} → ${result.target}</div>
                    <div class="test-description">${result.message}</div>
                </div>
            `;
            testsSection.appendChild(testElement);
        });
    }

    async saveValidationConfiguration() {
        if (!this.simulationId || !this.validationConfig) return;

        try {
            const response = await fetch(`/admin/simulation/edit/${this.simulationId}/validation/config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.validationConfig)
            });

            if (response.ok) {
                this.showToast('Validation configuration saved', 'success');
            } else {
                this.showToast('Failed to save configuration', 'error');
            }
        } catch (error) {
            console.error('Error saving validation configuration:', error);
            this.showToast('Error saving configuration', 'error');
        }
    }

    resetValidation() {
        this.completedConfigurations.clear();
        this.connectivityTests.clear();
        this.currentState = this.validationStates.DISCONNECTED;
        
        this.updateOverallStatus();
        this.updateStateMachine();
        this.setupValidationRequirements();
        
        this.showToast('Validation reset', 'info');
    }

    showToast(message, type = 'info') {
        // Try existing toast systems first
        if (window.editor && window.editor.showToast) {
            window.editor.showToast(message, type);
            return;
        }
        
        // Create enhanced toast
        const toast = document.createElement('div');
        toast.className = `universal-toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : type === 'warning' ? 'exclamation' : 'info'}"></i>
            </div>
            <span>${message}</span>
        `;
        
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            warning: '#F59E0B',
            info: '#3B82F6'
        };
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 420px;
            background: linear-gradient(135deg, ${colors[type]}, ${colors[type]}CC);
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            z-index: 10001;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: center;
            gap: 8px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    getValidationReport() {
        return {
            currentState: this.currentState,
            configured: this.completedConfigurations.size === this.requiredConfigurations.size,
            physicallyValid: true, // Updated by validation results
            connectivityPassed: Array.from(this.connectivityTests.values()).every(test => test.status === 'pass'),
            totalTests: this.connectivityTests.size,
            passedTests: Array.from(this.connectivityTests.values()).filter(test => test.status === 'pass').length,
            overallValid: this.currentState === this.validationStates.WORKING
        };
    }
}

// Global initialization
window.universalValidator = null;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (!window.universalValidator) {
            window.universalValidator = new UniversalSimulationValidator();
            console.log('Universal Simulation Validator initialized');
        }
    }, 2000);
});

// Manual initialization function
window.initializeUniversalValidator = function(simulationId) {
    if (window.universalValidator) {
        window.universalValidator = null;
    }
    window.universalValidator = new UniversalSimulationValidator(simulationId);
    return window.universalValidator;
};

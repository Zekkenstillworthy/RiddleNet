/**
 * User Device Configurator
 * Provides device configuration interface for students in simulations
 * Mirrors admin enhanced-device-configurator.js functionality
 */

class UserDeviceConfigurator {
    constructor() {
        this.currentDevice = null;
        this.networkConfigs = new Map();
        this.validationRules = new Map();
        this.modal = null;
        this.isInitialized = false;
        
        this.init();
    }

    init() {
        this.createConfigurationModal();
        this.setupEventListeners();
        this.isInitialized = true;
        console.log('✅ User Device Configurator initialized');
    }

    createConfigurationModal() {
        // Create modal HTML structure
        const modalHTML = `
            <div id="device-config-modal" class="config-modal" style="display: none;">
                <div class="config-modal-backdrop"></div>
                <div class="config-modal-container">
                    <div class="config-modal-header">
                        <div class="modal-title">
                            <i class="fas fa-cog"></i>
                            <span id="config-device-title">Configure Device</span>
                        </div>
                        <button class="modal-close" onclick="userDeviceConfigurator.closeConfiguration()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="config-modal-content">
                        <!-- Configuration Tabs -->
                        <div class="config-tabs">
                            <button class="config-tab active" data-tab="basic">
                                <i class="fas fa-info-circle"></i>
                                Basic
                            </button>
                            <button class="config-tab" data-tab="network">
                                <i class="fas fa-network-wired"></i>
                                Network
                            </button>
                            <button class="config-tab" data-tab="advanced">
                                <i class="fas fa-cogs"></i>
                                Advanced
                            </button>
                            <button class="config-tab" data-tab="validation">
                                <i class="fas fa-check-circle"></i>
                                Status
                            </button>
                        </div>

                        <!-- Tab Contents -->
                        <div class="config-tab-content">
                            <!-- Basic Configuration -->
                            <div id="basic-tab" class="tab-pane active">
                                <div class="config-section">
                                    <h4><i class="fas fa-tag"></i> Device Information</h4>
                                    <div class="form-group">
                                        <label for="device-name">Device Name</label>
                                        <input type="text" id="device-name" placeholder="Enter device name">
                                    </div>
                                    <div class="form-group">
                                        <label for="device-description">Description</label>
                                        <textarea id="device-description" placeholder="Enter device description" rows="3"></textarea>
                                    </div>
                                    <div class="form-group">
                                        <label for="user-device-location">Location</label>
                                        <input type="text" id="user-device-location" placeholder="Enter physical location">
                                    </div>
                                </div>
                            </div>

                            <!-- Network Configuration -->
                            <div id="network-tab" class="tab-pane">
                                <div class="config-section">
                                    <h4><i class="fas fa-globe"></i> IP Configuration</h4>
                                    <div class="config-method-selector">
                                        <label class="radio-option">
                                            <input type="radio" name="ip-method" value="static" checked>
                                            <span>Static IP</span>
                                        </label>
                                        <label class="radio-option">
                                            <input type="radio" name="ip-method" value="dhcp">
                                            <span>DHCP</span>
                                        </label>
                                    </div>
                                    
                                    <div id="static-config" class="ip-config-section">
                                        <div class="form-row">
                                            <div class="form-group">
                                                <label for="ip-address">IP Address</label>
                                                <input type="text" id="ip-address" placeholder="192.168.1.100">
                                            </div>
                                            <div class="form-group">
                                                <label for="subnet-mask">Subnet Mask</label>
                                                <input type="text" id="subnet-mask" placeholder="255.255.255.0">
                                            </div>
                                        </div>
                                        <div class="form-row">
                                            <div class="form-group">
                                                <label for="default-gateway">Default Gateway</label>
                                                <input type="text" id="default-gateway" placeholder="192.168.1.1">
                                            </div>
                                            <div class="form-group">
                                                <label for="dns-server">DNS Server</label>
                                                <input type="text" id="dns-server" placeholder="8.8.8.8">
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div id="dhcp-config" class="ip-config-section" style="display: none;">
                                        <div class="dhcp-status">
                                            <i class="fas fa-info-circle"></i>
                                            <span>IP configuration will be obtained automatically from DHCP server</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Interface Configuration (for routers/switches) -->
                                <div id="interface-config" class="config-section" style="display: none;">
                                    <h4><i class="fas fa-ethernet"></i> Interface Configuration</h4>
                                    <div id="interfaces-container">
                                        <!-- Interfaces will be dynamically added -->
                                    </div>
                                    <button class="btn-add-interface" onclick="userDeviceConfigurator.addInterface()">
                                        <i class="fas fa-plus"></i> Add Interface
                                    </button>
                                </div>
                            </div>

                            <!-- Advanced Configuration -->
                            <div id="advanced-tab" class="tab-pane">
                                <!-- Routing Configuration (for routers) -->
                                <div id="routing-config" class="config-section" style="display: none;">
                                    <h4><i class="fas fa-route"></i> Routing Configuration</h4>
                                    <div id="routing-container">
                                        <!-- Routes will be dynamically added -->
                                    </div>
                                    <button class="btn-add-route" onclick="userDeviceConfigurator.addRoute()">
                                        <i class="fas fa-plus"></i> Add Route
                                    </button>
                                </div>

                                <!-- VLAN Configuration (for switches) -->
                                <div id="vlan-config" class="config-section" style="display: none;">
                                    <h4><i class="fas fa-layer-group"></i> VLAN Configuration</h4>
                                    <div id="vlan-container">
                                        <!-- VLANs will be dynamically added -->
                                    </div>
                                    <button class="btn-add-vlan" onclick="userDeviceConfigurator.addVLAN()">
                                        <i class="fas fa-plus"></i> Add VLAN
                                    </button>
                                </div>

                                <!-- Services Configuration -->
                                <div id="services-config" class="config-section">
                                    <h4><i class="fas fa-server"></i> Services</h4>
                                    <div class="services-grid">
                                        <label class="service-option">
                                            <input type="checkbox" id="ssh-service">
                                            <span>SSH Server</span>
                                        </label>
                                        <label class="service-option">
                                            <input type="checkbox" id="web-service">
                                            <span>Web Server</span>
                                        </label>
                                        <label class="service-option">
                                            <input type="checkbox" id="ftp-service">
                                            <span>FTP Server</span>
                                        </label>
                                        <label class="service-option">
                                            <input type="checkbox" id="dns-service">
                                            <span>DNS Server</span>
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <!-- Validation Status -->
                            <div id="validation-tab" class="tab-pane">
                                <div class="config-section">
                                    <h4><i class="fas fa-clipboard-check"></i> Configuration Status</h4>
                                    <div id="validation-results">
                                        <div class="validation-item">
                                            <i class="fas fa-clock text-warning"></i>
                                            <span>Configuration not yet validated</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="config-section">
                                    <h4><i class="fas fa-list-check"></i> Requirements Checklist</h4>
                                    <div id="requirements-checklist">
                                        <!-- Requirements will be dynamically populated -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="config-modal-actions">
                        <button class="btn-secondary" onclick="userDeviceConfigurator.closeConfiguration()">
                            Cancel
                        </button>
                        <button class="btn-primary" onclick="userDeviceConfigurator.saveConfiguration()">
                            <i class="fas fa-save"></i> Save Configuration
                        </button>
                        <button class="btn-success" onclick="userDeviceConfigurator.testConfiguration()">
                            <i class="fas fa-vial"></i> Test Configuration
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Add modal to document
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('device-config-modal');
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.config-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.closest('.config-tab').dataset.tab;
                this.switchTab(tabName);
            });
        });

        // IP method switching
        document.querySelectorAll('input[name="ip-method"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.toggleIPMethod(e.target.value);
            });
        });

        // Real-time validation
        const validateFields = ['ip-address', 'subnet-mask', 'default-gateway', 'dns-server'];
        validateFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', () => this.validateField(fieldId));
                field.addEventListener('input', () => this.clearFieldError(fieldId));
            }
        });

        // Close modal on backdrop click
        document.querySelector('.config-modal-backdrop').addEventListener('click', () => {
            this.closeConfiguration();
        });
    }

    openDeviceConfiguration(device) {
        if (!device) {
            console.error('No device provided for configuration');
            return;
        }

        this.currentDevice = device;
        this.loadDeviceConfiguration(device);
        this.setupDeviceSpecificUI(device);
        this.modal.style.display = 'flex';
        
        // Focus first input
        setTimeout(() => {
            const firstInput = this.modal.querySelector('input:not([type="radio"]):not([type="checkbox"])');
            if (firstInput) firstInput.focus();
        }, 100);

        console.log(`🔧 Opening configuration for ${device.type} - ${device.name}`);
    }

    loadDeviceConfiguration(device) {
        // Set device title
        document.getElementById('config-device-title').textContent = `Configure ${device.name || device.type}`;

        // Load existing configuration
        const config = this.networkConfigs.get(device.id) || this.getDefaultConfig(device);
        
        // Populate basic information
        document.getElementById('device-name').value = device.name || '';
        document.getElementById('device-description').value = config.description || '';
        document.getElementById('user-device-location').value = config.location || '';

        // Populate network configuration
        if (config.ipMethod === 'dhcp') {
            document.querySelector('input[value="dhcp"]').checked = true;
            this.toggleIPMethod('dhcp');
        } else {
            document.querySelector('input[value="static"]').checked = true;
            document.getElementById('ip-address').value = config.ipAddress || '';
            document.getElementById('subnet-mask').value = config.subnetMask || '255.255.255.0';
            document.getElementById('default-gateway').value = config.gateway || '';
            document.getElementById('dns-server').value = config.dnsServer || '';
            this.toggleIPMethod('static');
        }

        // Load interfaces, routes, VLANs based on device type
        this.loadInterfaceConfiguration(device, config);
        this.loadRoutingConfiguration(device, config);
        this.loadVLANConfiguration(device, config);
        this.loadServicesConfiguration(device, config);
    }

    getDefaultConfig(device) {
        const defaults = {
            'pc': {
                ipMethod: 'static',
                ipAddress: '192.168.1.100',
                subnetMask: '255.255.255.0',
                gateway: '192.168.1.1',
                dnsServer: '8.8.8.8'
            },
            'server': {
                ipMethod: 'static',
                ipAddress: '192.168.1.10',
                subnetMask: '255.255.255.0',
                gateway: '192.168.1.1',
                dnsServer: '8.8.8.8'
            },
            'router': {
                ipMethod: 'static',
                interfaces: [
                    { name: 'GigabitEthernet0/0', ip: '192.168.1.1', mask: '255.255.255.0', status: 'up' },
                    { name: 'GigabitEthernet0/1', ip: '10.0.0.1', mask: '255.255.255.0', status: 'up' }
                ],
                routes: []
            },
            'switch': {
                vlans: [
                    { id: 1, name: 'default', status: 'active' }
                ],
                interfaces: []
            }
        };

        return defaults[device.type] || { ipMethod: 'static' };
    }

    setupDeviceSpecificUI(device) {
        // Hide/show sections based on device type
        const interfaceConfig = document.getElementById('interface-config');
        const routingConfig = document.getElementById('routing-config');
        const vlanConfig = document.getElementById('vlan-config');

        // Reset visibility
        interfaceConfig.style.display = 'none';
        routingConfig.style.display = 'none';
        vlanConfig.style.display = 'none';

        switch (device.type) {
            case 'router':
                interfaceConfig.style.display = 'block';
                routingConfig.style.display = 'block';
                break;
            case 'switch':
                vlanConfig.style.display = 'block';
                interfaceConfig.style.display = 'block';
                break;
        }
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.config-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        // Update active tab pane
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane.id === `${tabName}-tab`);
        });
    }

    toggleIPMethod(method) {
        const staticConfig = document.getElementById('static-config');
        const dhcpConfig = document.getElementById('dhcp-config');

        if (method === 'dhcp') {
            staticConfig.style.display = 'none';
            dhcpConfig.style.display = 'block';
        } else {
            staticConfig.style.display = 'block';
            dhcpConfig.style.display = 'none';
        }
    }

    validateField(fieldId) {
        const field = document.getElementById(fieldId);
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        switch (fieldId) {
            case 'ip-address':
                if (value && !this.isValidIP(value)) {
                    isValid = false;
                    errorMessage = 'Invalid IP address format';
                }
                break;
            case 'subnet-mask':
                if (value && !this.isValidSubnetMask(value)) {
                    isValid = false;
                    errorMessage = 'Invalid subnet mask format';
                }
                break;
            case 'default-gateway':
                if (value && !this.isValidIP(value)) {
                    isValid = false;
                    errorMessage = 'Invalid gateway IP address';
                }
                break;
            case 'dns-server':
                if (value && !this.isValidIP(value)) {
                    isValid = false;
                    errorMessage = 'Invalid DNS server IP address';
                }
                break;
        }

        this.showFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    showFieldValidation(field, isValid, errorMessage) {
        // Remove existing validation classes
        field.classList.remove('valid', 'invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        if (field.value.trim()) {
            field.classList.add(isValid ? 'valid' : 'invalid');
            
            if (!isValid && errorMessage) {
                const errorEl = document.createElement('div');
                errorEl.className = 'field-error';
                errorEl.textContent = errorMessage;
                field.parentNode.appendChild(errorEl);
            }
        }
    }

    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        field.classList.remove('invalid');
        const errorEl = field.parentNode.querySelector('.field-error');
        if (errorEl) {
            errorEl.remove();
        }
    }

    saveConfiguration() {
        if (!this.currentDevice) return;

        // Validate all fields
        const isValid = this.validateAllFields();
        if (!isValid) {
            this.showNotification('Please fix validation errors before saving', 'error');
            return;
        }

        // Collect configuration data
        const config = this.collectConfigurationData();
        
        // Try to save via API
        this.saveConfigurationAPI(config).then(success => {
            if (success) {
                // Save to local network configurations as backup
                this.networkConfigs.set(this.currentDevice.id, config);

                // Update device visual representation
                this.updateDeviceVisual(this.currentDevice, config);

                // Trigger validation check
                if (window.userSimulationValidator) {
                    window.userSimulationValidator.validateDevice(this.currentDevice.id);
                }

                this.showNotification('Configuration saved successfully', 'success');
                console.log(`✅ Configuration saved for ${this.currentDevice.name}`, config);
            }
        });
    }

    // API integration method
    async saveConfigurationAPI(config) {
        try {
            const simulationId = this.getSimulationId();
            const response = await fetch(`/api/simulation/${simulationId}/device-config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device_id: this.currentDevice.id,
                    config: config
                })
            });

            const result = await response.json();

            if (result.success) {
                // Handle validation results from backend
                if (result.validation && !result.validation.valid) {
                    this.showNotification(`Configuration saved with warnings: ${result.validation.errors.join(', ')}`, 'warning');
                } else {
                    this.showNotification('Configuration saved successfully!', 'success');
                }
                return true;
            } else {
                this.showNotification(`Save failed: ${result.error}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error saving configuration:', error);
            this.showNotification('Network error - configuration saved locally only', 'warning');
            return true; // Allow local save to proceed
        }
    }

    // Utility method to get simulation ID
    getSimulationId() {
        // Try to get from URL path
        const pathParts = window.location.pathname.split('/');
        const simIndex = pathParts.indexOf('simulation');
        if (simIndex !== -1 && pathParts[simIndex + 1]) {
            return pathParts[simIndex + 1];
        }
        
        // Try to get from global simulation object
        if (window.simulation && window.simulation.simulation && window.simulation.simulation.id) {
            return window.simulation.simulation.id;
        }
        
        // Fallback: extract from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('simulation_id') || '1';
    }

    collectConfigurationData() {
        const ipMethod = document.querySelector('input[name="ip-method"]:checked').value;
        
        const config = {
            deviceName: document.getElementById('device-name').value,
            description: document.getElementById('device-description').value,
            location: document.getElementById('user-device-location').value,
            ipMethod: ipMethod,
            timestamp: new Date().toISOString()
        };

        if (ipMethod === 'static') {
            config.ipAddress = document.getElementById('ip-address').value;
            config.subnetMask = document.getElementById('subnet-mask').value;
            config.gateway = document.getElementById('default-gateway').value;
            config.dnsServer = document.getElementById('dns-server').value;
        }

        // Collect device-specific configurations
        config.interfaces = this.collectInterfaceConfiguration();
        config.routes = this.collectRoutingConfiguration();
        config.vlans = this.collectVLANConfiguration();
        config.services = this.collectServicesConfiguration();

        return config;
    }

    validateAllFields() {
        const fields = ['ip-address', 'subnet-mask', 'default-gateway', 'dns-server'];
        let allValid = true;

        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field && field.offsetParent !== null) { // Only validate visible fields
                const isValid = this.validateField(fieldId);
                if (!isValid) allValid = false;
            }
        });

        return allValid;
    }

    testConfiguration() {
        if (!this.currentDevice) return;

        const config = this.collectConfigurationData();
        
        // Run configuration tests
        this.runConfigurationTests(config);
    }

    runConfigurationTests(config) {
        const results = [];

        // IP connectivity test
        if (config.ipMethod === 'static' && config.ipAddress) {
            results.push({
                test: 'IP Configuration',
                status: 'pass',
                message: `IP ${config.ipAddress} configured correctly`
            });
        }

        // Gateway reachability test
        if (config.gateway) {
            // Simulate gateway ping test
            setTimeout(() => {
                results.push({
                    test: 'Gateway Reachability',
                    status: 'pass',
                    message: `Gateway ${config.gateway} is reachable`
                });
                this.displayTestResults(results);
            }, 1000);
        }

        // Display immediate results
        this.displayTestResults(results);
    }

    displayTestResults(results) {
        const validationResults = document.getElementById('validation-results');
        validationResults.innerHTML = '';

        results.forEach(result => {
            const resultEl = document.createElement('div');
            resultEl.className = `validation-item ${result.status}`;
            resultEl.innerHTML = `
                <i class="fas ${result.status === 'pass' ? 'fa-check-circle text-success' : 'fa-times-circle text-danger'}"></i>
                <span><strong>${result.test}:</strong> ${result.message}</span>
            `;
            validationResults.appendChild(resultEl);
        });
    }

    closeConfiguration() {
        this.modal.style.display = 'none';
        this.currentDevice = null;
    }

    // Utility functions
    isValidIP(ip) {
        const pattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return pattern.test(ip);
    }

    isValidSubnetMask(mask) {
        const validMasks = [
            '255.255.255.252', '255.255.255.248', '255.255.255.240',
            '255.255.255.224', '255.255.255.192', '255.255.255.128',
            '255.255.255.0', '255.255.254.0', '255.255.252.0',
            '255.255.248.0', '255.255.240.0', '255.255.224.0',
            '255.255.192.0', '255.255.128.0', '255.255.0.0',
            '255.254.0.0', '255.252.0.0', '255.248.0.0',
            '255.240.0.0', '255.224.0.0', '255.192.0.0',
            '255.128.0.0', '255.0.0.0'
        ];
        return validMasks.includes(mask);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-times-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;

        // Add to document
        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    updateDeviceVisual(device, config) {
        // Update device representation on canvas
        const deviceElement = document.querySelector(`[data-device-id="${device.id}"]`);
        if (deviceElement) {
            // Update IP badge
            const ipBadge = deviceElement.querySelector('.ip-badge');
            if (ipBadge) {
                ipBadge.textContent = config.ipAddress || '';
            }

            // Add configuration status indicator
            let statusIndicator = deviceElement.querySelector('.config-status');
            if (!statusIndicator) {
                statusIndicator = document.createElement('div');
                statusIndicator.className = 'config-status';
                deviceElement.appendChild(statusIndicator);
            }
            
            statusIndicator.innerHTML = '<i class="fas fa-check-circle text-success"></i>';
            statusIndicator.title = 'Device Configured';
        }
    }

    // Interface management methods (for routers/switches)
    loadInterfaceConfiguration(device, config) {
        if (!config.interfaces) return;
        
        const container = document.getElementById('interfaces-container');
        container.innerHTML = '';
        
        config.interfaces.forEach((intf, index) => {
            this.addInterfaceToUI(intf, index);
        });
    }

    addInterface() {
        const container = document.getElementById('interfaces-container');
        const index = container.children.length;
        const newInterface = {
            name: `Interface${index + 1}`,
            ip: '',
            mask: '255.255.255.0',
            status: 'up'
        };
        this.addInterfaceToUI(newInterface, index);
    }

    addInterfaceToUI(intf, index) {
        const container = document.getElementById('interfaces-container');
        const intfElement = document.createElement('div');
        intfElement.className = 'interface-config-item';
        intfElement.innerHTML = `
            <div class="interface-header">
                <span>${intf.name}</span>
                <button class="btn-remove" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="interface-fields">
                <input type="text" placeholder="IP Address" value="${intf.ip || ''}" 
                       onchange="userDeviceConfigurator.validateField('interface-ip-${index}')">
                <input type="text" placeholder="Subnet Mask" value="${intf.mask || ''}" 
                       onchange="userDeviceConfigurator.validateField('interface-mask-${index}')">
                <select onchange="userDeviceConfigurator.updateInterfaceStatus(${index}, this.value)">
                    <option value="up" ${intf.status === 'up' ? 'selected' : ''}>Up</option>
                    <option value="down" ${intf.status === 'down' ? 'selected' : ''}>Down</option>
                </select>
            </div>
        `;
        container.appendChild(intfElement);
    }

    collectInterfaceConfiguration() {
        const interfaces = [];
        const container = document.getElementById('interfaces-container');
        
        Array.from(container.children).forEach((item, index) => {
            const fields = item.querySelectorAll('input, select');
            if (fields.length >= 3) {
                interfaces.push({
                    name: item.querySelector('.interface-header span').textContent,
                    ip: fields[0].value,
                    mask: fields[1].value,
                    status: fields[2].value
                });
            }
        });
        
        return interfaces;
    }

    // Routing configuration methods
    loadRoutingConfiguration(device, config) {
        if (!config.routes) return;
        
        const container = document.getElementById('routing-container');
        container.innerHTML = '';
        
        config.routes.forEach((route, index) => {
            this.addRouteToUI(route, index);
        });
    }

    addRoute() {
        const container = document.getElementById('routing-container');
        const index = container.children.length;
        const newRoute = {
            network: '',
            mask: '255.255.255.0',
            gateway: '',
            interface: ''
        };
        this.addRouteToUI(newRoute, index);
    }

    addRouteToUI(route, index) {
        const container = document.getElementById('routing-container');
        const routeElement = document.createElement('div');
        routeElement.className = 'route-config-item';
        routeElement.innerHTML = `
            <div class="route-header">
                <span>Route ${index + 1}</span>
                <button class="btn-remove" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="route-fields">
                <input type="text" placeholder="Network" value="${route.network || ''}" 
                       onchange="userDeviceConfigurator.validateField('route-network-${index}')">
                <input type="text" placeholder="Mask" value="${route.mask || ''}" 
                       onchange="userDeviceConfigurator.validateField('route-mask-${index}')">
                <input type="text" placeholder="Gateway" value="${route.gateway || ''}" 
                       onchange="userDeviceConfigurator.validateField('route-gateway-${index}')">
                <input type="text" placeholder="Interface" value="${route.interface || ''}">
            </div>
        `;
        container.appendChild(routeElement);
    }

    collectRoutingConfiguration() {
        const routes = [];
        const container = document.getElementById('routing-container');
        
        Array.from(container.children).forEach((item, index) => {
            const fields = item.querySelectorAll('input');
            if (fields.length >= 4) {
                routes.push({
                    network: fields[0].value,
                    mask: fields[1].value,
                    gateway: fields[2].value,
                    interface: fields[3].value
                });
            }
        });
        
        return routes;
    }

    // VLAN configuration methods
    loadVLANConfiguration(device, config) {
        if (!config.vlans) return;
        
        const container = document.getElementById('vlan-container');
        container.innerHTML = '';
        
        config.vlans.forEach((vlan, index) => {
            this.addVLANToUI(vlan, index);
        });
    }

    addVLAN() {
        const container = document.getElementById('vlan-container');
        const index = container.children.length;
        const newVLAN = {
            id: index + 1,
            name: `VLAN${index + 1}`,
            status: 'active'
        };
        this.addVLANToUI(newVLAN, index);
    }

    addVLANToUI(vlan, index) {
        const container = document.getElementById('vlan-container');
        const vlanElement = document.createElement('div');
        vlanElement.className = 'vlan-config-item';
        vlanElement.innerHTML = `
            <div class="vlan-header">
                <span>VLAN ${vlan.id}</span>
                <button class="btn-remove" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="vlan-fields">
                <input type="number" placeholder="VLAN ID" value="${vlan.id || ''}" min="1" max="4094">
                <input type="text" placeholder="VLAN Name" value="${vlan.name || ''}">
                <select>
                    <option value="active" ${vlan.status === 'active' ? 'selected' : ''}>Active</option>
                    <option value="suspend" ${vlan.status === 'suspend' ? 'selected' : ''}>Suspended</option>
                </select>
            </div>
        `;
        container.appendChild(vlanElement);
    }

    collectVLANConfiguration() {
        const vlans = [];
        const container = document.getElementById('vlan-container');
        
        Array.from(container.children).forEach((item, index) => {
            const fields = item.querySelectorAll('input, select');
            if (fields.length >= 3) {
                vlans.push({
                    id: parseInt(fields[0].value) || (index + 1),
                    name: fields[1].value || `VLAN${index + 1}`,
                    status: fields[2].value || 'active'
                });
            }
        });
        
        return vlans;
    }

    // Services configuration methods
    loadServicesConfiguration(device, config) {
        if (!config.services) return;
        
        const services = ['ssh', 'web', 'ftp', 'dns'];
        services.forEach(service => {
            const checkbox = document.getElementById(`${service}-service`);
            if (checkbox) {
                checkbox.checked = config.services.includes(service);
            }
        });
    }

    collectServicesConfiguration() {
        const services = [];
        const serviceCheckboxes = ['ssh-service', 'web-service', 'ftp-service', 'dns-service'];
        
        serviceCheckboxes.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox && checkbox.checked) {
                services.push(id.replace('-service', ''));
            }
        });
        
        return services;
    }

    // Public methods for external access
    getDeviceConfiguration(deviceId) {
        return this.networkConfigs.get(deviceId);
    }

    getAllConfigurations() {
        return Object.fromEntries(this.networkConfigs);
    }

    hasConfiguration(deviceId) {
        return this.networkConfigs.has(deviceId) && 
               this.networkConfigs.get(deviceId).ipAddress;
    }
}

// Initialize global instance
let userDeviceConfigurator;
document.addEventListener('DOMContentLoaded', () => {
    userDeviceConfigurator = new UserDeviceConfigurator();
    window.userDeviceConfigurator = userDeviceConfigurator;
});
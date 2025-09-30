/**
 * Enhanced Device Configuration Interface
 * Provides comprehensive device configuration with validation integration
 */

class EnhancedDeviceConfigurator {
    constructor() {
        this.deviceConfigs = new Map();
        this.configurationRequirements = {
            'pc': ['ip', 'subnet', 'gateway'],
            'server': ['ip', 'subnet', 'gateway', 'services'],
            'router': ['ip', 'subnet', 'routing', 'interfaces'],
            'switch': ['vlans', 'interfaces', 'stp'],
            'access-point': ['ssid', 'security', 'ip', 'subnet']
        };
        
        this.initializeConfigurator();
    }

    initializeConfigurator() {
        this.createConfigurationInterface();
        this.attachEventListeners();
    }

    createConfigurationInterface() {
        // Enhanced configuration modal
        const modal = document.createElement('div');
        modal.id = 'enhanced-device-config-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-cogs"></i> Device Configuration</h3>
                    <!-- Use global instance method to avoid invalid 'this' context -->
                    <button class="modal-close" onclick="window.deviceConfigurator?.closeConfigModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <div class="device-info">
                        <div class="device-icon-display"></div>
                        <div class="device-details">
                            <h4 id="config-device-name">Device Name</h4>
                            <p id="config-device-type">Device Type</p>
                        </div>
                    </div>

                    <div class="configuration-tabs">
                        <button class="tab-btn active" data-tab="basic">Basic</button>
                        <button class="tab-btn" data-tab="network">Network</button>
                        <button class="tab-btn" data-tab="advanced">Advanced</button>
                        <button class="tab-btn" data-tab="validation">Validation</button>
                    </div>

                    <!-- NOTE: Using a unique container class to avoid collisions with global .tab-content styles on admin pages -->
                    <div class="tab-content device-config-tab-wrapper">
                        <!-- Basic Configuration -->
                        <div class="tab-panel active" id="basic-panel">
                            <div class="config-section">
                                <h5>Basic Settings</h5>
                                <div class="form-group">
                                    <label>Device Name</label>
                                    <input type="text" id="device-name-input" placeholder="Enter device name">
                                </div>
                                <div class="form-group">
                                    <label>Operating Mode</label>
                                    <select id="device-mode">
                                        <option value="">Select mode...</option>
                                        <option value="client">Client Mode</option>
                                        <option value="server">Server Mode</option>
                                        <option value="router">Router Mode</option>
                                        <option value="switch">Switch Mode</option>
                                        <option value="ap">Access Point Mode</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Status</label>
                                    <select id="device-status">
                                        <option value="up">Up</option>
                                        <option value="down">Down</option>
                                        <option value="maintenance">Maintenance</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Network Configuration -->
                        <div class="tab-panel" id="network-panel">
                            <div class="config-section">
                                <h5>IP Configuration</h5>
                                <div class="form-group">
                                    <label>IP Address *</label>
                                    <input type="text" id="ip-address" placeholder="192.168.1.100" required>
                                    <small class="validation-hint">Required for connectivity tests</small>
                                </div>
                                <div class="form-group">
                                    <label>Subnet Mask *</label>
                                    <select id="subnet-mask">
                                        <option value="255.255.255.0">/24 (255.255.255.0)</option>
                                        <option value="255.255.255.128">/25 (255.255.255.128)</option>
                                        <option value="255.255.255.192">/26 (255.255.255.192)</option>
                                        <option value="255.255.255.224">/27 (255.255.255.224)</option>
                                        <option value="255.255.0.0">/16 (255.255.0.0)</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Default Gateway</label>
                                    <input type="text" id="device-default-gateway" placeholder="192.168.1.1">
                                    <small class="validation-hint">Required for inter-subnet communication</small>
                                </div>
                                <div class="form-group">
                                    <label>DNS Server</label>
                                    <input type="text" id="dns-server" placeholder="8.8.8.8">
                                </div>
                            </div>

                            <div class="config-section" id="interface-config" style="display: none;">
                                <h5>Interface Configuration</h5>
                                <div id="interfaces-list"></div>
                                <button type="button" class="add-interface-btn">
                                    <i class="fas fa-plus"></i> Add Interface
                                </button>
                            </div>
                        </div>

                        <!-- Advanced Configuration -->
                        <div class="tab-panel" id="advanced-panel">
                            <div class="config-section" id="routing-config" style="display: none;">
                                <h5>Routing Configuration</h5>
                                <div id="routing-table">
                                    <div class="routing-header">
                                        <span>Destination</span>
                                        <span>Gateway</span>
                                        <span>Interface</span>
                                        <span>Actions</span>
                                    </div>
                                    <div id="routes-list"></div>
                                </div>
                                <button type="button" class="add-route-btn">
                                    <i class="fas fa-plus"></i> Add Route
                                </button>
                            </div>

                            <div class="config-section" id="vlan-config" style="display: none;">
                                <h5>VLAN Configuration</h5>
                                <div id="vlans-list"></div>
                                <button type="button" class="add-vlan-btn">
                                    <i class="fas fa-plus"></i> Add VLAN
                                </button>
                            </div>

                            <div class="config-section" id="wireless-config" style="display: none;">
                                <h5>Wireless Configuration</h5>
                                <div class="form-group">
                                    <label>SSID</label>
                                    <input type="text" id="wireless-ssid" placeholder="NetworkName">
                                </div>
                                <div class="form-group">
                                    <label>Security</label>
                                    <select id="wireless-security">
                                        <option value="open">Open</option>
                                        <option value="wep">WEP</option>
                                        <option value="wpa">WPA</option>
                                        <option value="wpa2">WPA2</option>
                                        <option value="wpa3">WPA3</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Password</label>
                                    <input type="password" id="wireless-password" placeholder="********">
                                </div>
                            </div>

                            <div class="config-section" id="services-config" style="display: none;">
                                <h5>Services Configuration</h5>
                                <div class="services-checkboxes">
                                    <label><input type="checkbox" value="dhcp"> DHCP Server</label>
                                    <label><input type="checkbox" value="dns"> DNS Server</label>
                                    <label><input type="checkbox" value="web"> Web Server</label>
                                    <label><input type="checkbox" value="ftp"> FTP Server</label>
                                    <label><input type="checkbox" value="ssh"> SSH Server</label>
                                </div>
                            </div>
                        </div>

                        <!-- Validation Panel -->
                        <div class="tab-panel" id="validation-panel">
                            <div class="config-section">
                                <h5>Configuration Validation</h5>
                                <div id="device-validation-results">
                                    <div class="validation-item">
                                        <div class="validation-status pending" id="ip-validation">
                                            <i class="fas fa-clock"></i>
                                        </div>
                                        <span>IP Address Configuration</span>
                                    </div>
                                    <div class="validation-item">
                                        <div class="validation-status pending" id="connectivity-validation">
                                            <i class="fas fa-clock"></i>
                                        </div>
                                        <span>Network Connectivity</span>
                                    </div>
                                    <div class="validation-item">
                                        <div class="validation-status pending" id="reachability-validation">
                                            <i class="fas fa-clock"></i>
                                        </div>
                                        <span>Gateway Reachability</span>
                                    </div>
                                </div>
                                
                                <button type="button" id="validate-device-config" class="validation-btn">
                                    <i class="fas fa-check"></i> Validate Configuration
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn secondary" onclick="this.closeConfigModal()">Cancel</button>
                    <button type="button" class="btn primary" id="save-device-config">
                        <i class="fas fa-save"></i> Save Configuration
                    </button>
                </div>
            </div>
        `;

        // Add enhanced styles
        const styles = document.createElement('style');
        styles.textContent = `
            #enhanced-device-config-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 2000;
                display: none;
            }

            #enhanced-device-config-modal.active {
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .modal-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(4px);
            }

            .modal-content {
                position: relative;
                background: var(--surface);
                border: 1px solid var(--glass-border);
                border-radius: var(--border-radius);
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow: hidden;
                box-shadow: var(--shadow-lg);
                color: var(--text-primary);
            }

            .modal-header {
                padding: 20px;
                border-bottom: 1px solid var(--glass-border);
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: var(--glass-bg-light);
            }

            .modal-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
            }

            .modal-close {
                background: none;
                border: none;
                color: var(--text-secondary);
                font-size: 20px;
                cursor: pointer;
                padding: 5px;
                border-radius: 4px;
                transition: all 0.3s ease;
            }

            .modal-close:hover {
                background: var(--glass-bg-hover);
                color: var(--text-primary);
            }

            .modal-body {
                padding: 20px;
                max-height: calc(90vh - 140px);
                overflow-y: auto;
            }

            .device-info {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 20px;
                padding: 15px;
                background: var(--glass-bg-light);
                border-radius: 8px;
            }

            .device-icon-display {
                width: 48px;
                height: 48px;
                background: var(--accent-color);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: white;
            }

            .device-details h4 {
                margin: 0 0 5px 0;
                font-size: 16px;
                font-weight: 600;
            }

            .device-details p {
                margin: 0;
                color: var(--text-secondary);
                font-size: 14px;
            }

            .configuration-tabs {
                display: flex;
                gap: 2px;
                margin-bottom: 20px;
                background: var(--glass-bg-light);
                border-radius: 8px;
                padding: 4px;
            }

            .tab-btn {
                flex: 1;
                padding: 10px 15px;
                background: none;
                border: none;
                color: var(--text-secondary);
                font-size: 14px;
                font-weight: 500;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .tab-btn.active {
                background: var(--accent-color);
                color: white;
            }

            .tab-btn:hover:not(.active) {
                background: var(--glass-bg-hover);
                color: var(--text-primary);
            }

            /* Ensure embedded configurator content isn't suppressed by global admin .tab-content styles */
            #enhanced-device-config-modal .tab-content { display: block !important; }

            .tab-panel {
                display: none;
            }

            .tab-panel.active {
                display: block;
            }

            .config-section {
                margin-bottom: 25px;
                padding: 20px;
                background: var(--glass-bg-light);
                border-radius: 8px;
                border: 1px solid var(--glass-border);
            }

            .config-section h5 {
                margin: 0 0 15px 0;
                font-size: 16px;
                font-weight: 600;
                color: var(--text-primary);
                border-bottom: 1px solid var(--glass-border);
                padding-bottom: 10px;
            }

            .form-group {
                margin-bottom: 15px;
            }

            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-size: 14px;
                font-weight: 500;
                color: var(--text-primary);
            }

            .form-group input,
            .form-group select {
                width: 100%;
                padding: 10px 12px;
                background: var(--background);
                border: 1px solid var(--glass-border);
                border-radius: 6px;
                color: var(--text-primary);
                font-size: 14px;
                transition: all 0.3s ease;
            }

            .form-group input:focus,
            .form-group select:focus {
                outline: none;
                border-color: var(--accent-color);
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
            }

            .validation-hint {
                display: block;
                margin-top: 5px;
                font-size: 12px;
                color: var(--text-muted);
                font-style: italic;
            }

            .routing-header {
                display: grid;
                grid-template-columns: 1fr 1fr 100px 80px;
                gap: 10px;
                padding: 10px;
                background: var(--background);
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                color: var(--text-secondary);
                margin-bottom: 10px;
            }

            .route-row {
                display: grid;
                grid-template-columns: 1fr 1fr 100px 80px;
                gap: 10px;
                padding: 8px 10px;
                background: var(--background);
                border-radius: 6px;
                margin-bottom: 8px;
                align-items: center;
            }

            .route-row input {
                padding: 6px 8px;
                font-size: 12px;
            }

            .add-route-btn,
            .add-interface-btn,
            .add-vlan-btn {
                background: var(--glass-bg-hover);
                border: 1px solid var(--glass-border);
                color: var(--text-primary);
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .add-route-btn:hover,
            .add-interface-btn:hover,
            .add-vlan-btn:hover {
                background: var(--accent-color);
                color: white;
            }

            .services-checkboxes {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
            }

            .services-checkboxes label {
                display: flex !important;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                background: var(--background);
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .services-checkboxes label:hover {
                background: var(--glass-bg-hover);
            }

            .validation-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px;
                margin-bottom: 8px;
                background: var(--background);
                border-radius: 6px;
            }

            .validation-status {
                width: 24px;
                height: 24px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
            }

            .validation-status.pending {
                background: var(--text-muted);
                color: white;
            }

            .validation-status.valid {
                background: var(--success-color);
                color: white;
            }

            .validation-status.invalid {
                background: var(--danger-color);
                color: white;
            }

            .validation-btn {
                width: 100%;
                background: var(--accent-color);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 15px;
            }

            .validation-btn:hover {
                background: var(--network-purple);
            }

            .modal-footer {
                padding: 20px;
                border-top: 1px solid var(--glass-border);
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                background: var(--glass-bg-light);
            }

            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .btn.secondary {
                background: var(--glass-bg-hover);
                color: var(--text-primary);
                border: 1px solid var(--glass-border);
            }

            .btn.primary {
                background: var(--success-color);
                color: white;
            }

            .btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }

            .remove-btn {
                background: var(--danger-color);
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
            }
        `;

        document.head.appendChild(styles);
        document.body.appendChild(modal);
    }

    openDeviceConfiguration(device) {
        const modal = document.getElementById('enhanced-device-config-modal');
        if (!modal) return;

        this.currentDevice = device;
        this.loadDeviceConfiguration(device);
        modal.classList.add('active');

        // Focus first input
        setTimeout(() => {
            const firstInput = modal.querySelector('input');
            if (firstInput) firstInput.focus();
        }, 100);
    }

    closeConfigModal() {
        const modal = document.getElementById('enhanced-device-config-modal');
        if (modal) {
            modal.classList.remove('active');
        }
        this.currentDevice = null;
    }

    loadDeviceConfiguration(device) {
        // Update device info display
        document.getElementById('config-device-name').textContent = device.name || device.label || 'Unnamed Device';
        document.getElementById('config-device-type').textContent = device.type.charAt(0).toUpperCase() + device.type.slice(1);

        // Set device icon
        const iconDisplay = document.querySelector('.device-icon-display');
        iconDisplay.innerHTML = this.getDeviceIcon(device.type);

        // Load existing configuration
        const config = this.deviceConfigs.get(device.id) || {};

        // Basic settings
        document.getElementById('device-name-input').value = config.name || device.name || '';
        document.getElementById('device-mode').value = config.mode || '';
        document.getElementById('device-status').value = config.status || 'up';

        // Network settings
        document.getElementById('ip-address').value = config.ipAddress || '';
        document.getElementById('subnet-mask').value = config.subnetMask || '255.255.255.0';
        document.getElementById('device-default-gateway').value = config.gateway || '';
        document.getElementById('dns-server').value = config.dnsServer || '';

        // Show/hide sections based on device type
        this.updateVisibleSections(device.type);

        // Load advanced configurations
        this.loadRoutingConfig(config.routes || []);
        this.loadVLANConfig(config.vlans || []);
        this.loadWirelessConfig(config.wireless || {});
        this.loadServicesConfig(config.services || []);
    }

    getDeviceIcon(deviceType) {
        const icons = {
            'pc': '<i class="fas fa-desktop"></i>',
            'server': '<i class="fas fa-server"></i>',
            'router': '<i class="fas fa-route"></i>',
            'switch': '<i class="fas fa-network-wired"></i>',
            'access-point': '<i class="fas fa-wifi"></i>',
            'laptop': '<i class="fas fa-laptop"></i>',
            'smartphone': '<i class="fas fa-mobile-alt"></i>'
        };
        return icons[deviceType] || '<i class="fas fa-microchip"></i>';
    }

    updateVisibleSections(deviceType) {
        // Hide all advanced sections first
        document.getElementById('interface-config').style.display = 'none';
        document.getElementById('routing-config').style.display = 'none';
        document.getElementById('vlan-config').style.display = 'none';
        document.getElementById('wireless-config').style.display = 'none';
        document.getElementById('services-config').style.display = 'none';

        // Show relevant sections based on device type
        switch (deviceType) {
            case 'router':
                document.getElementById('interface-config').style.display = 'block';
                document.getElementById('routing-config').style.display = 'block';
                break;
            case 'switch':
                document.getElementById('interface-config').style.display = 'block';
                document.getElementById('vlan-config').style.display = 'block';
                break;
            case 'access-point':
                document.getElementById('wireless-config').style.display = 'block';
                break;
            case 'server':
                document.getElementById('services-config').style.display = 'block';
                break;
        }
    }

    loadRoutingConfig(routes) {
        const routesList = document.getElementById('routes-list');
        routesList.innerHTML = '';

        routes.forEach((route, index) => {
            this.addRouteRow(route, index);
        });
    }

    addRouteRow(route = {}, index = -1) {
        const routesList = document.getElementById('routes-list');
        const routeId = index >= 0 ? index : routesList.children.length;

        const routeRow = document.createElement('div');
        routeRow.className = 'route-row';
        routeRow.innerHTML = `
            <input type="text" placeholder="0.0.0.0/0" value="${route.destination || ''}" data-field="destination">
            <input type="text" placeholder="192.168.1.1" value="${route.gateway || ''}" data-field="gateway">
            <input type="text" placeholder="eth0" value="${route.interface || ''}" data-field="interface">
            <button type="button" class="remove-btn" onclick="this.parentElement.remove()">
                <i class="fas fa-trash"></i>
            </button>
        `;

        routesList.appendChild(routeRow);
    }

    loadVLANConfig(vlans) {
        const vlansList = document.getElementById('vlans-list');
        vlansList.innerHTML = '';

        vlans.forEach(vlan => {
            this.addVLANRow(vlan);
        });
    }

    addVLANRow(vlan = {}) {
        const vlansList = document.getElementById('vlans-list');

        const vlanRow = document.createElement('div');
        vlanRow.className = 'route-row';
        vlanRow.innerHTML = `
            <input type="number" placeholder="VLAN ID" value="${vlan.id || ''}" data-field="id" min="1" max="4094">
            <input type="text" placeholder="VLAN Name" value="${vlan.name || ''}" data-field="name">
            <select data-field="type">
                <option value="access" ${vlan.type === 'access' ? 'selected' : ''}>Access</option>
                <option value="trunk" ${vlan.type === 'trunk' ? 'selected' : ''}>Trunk</option>
            </select>
            <button type="button" class="remove-btn" onclick="this.parentElement.remove()">
                <i class="fas fa-trash"></i>
            </button>
        `;

        vlansList.appendChild(vlanRow);
    }

    loadWirelessConfig(wireless) {
        document.getElementById('wireless-ssid').value = wireless.ssid || '';
        document.getElementById('wireless-security').value = wireless.security || 'wpa2';
        document.getElementById('wireless-password').value = wireless.password || '';
    }

    loadServicesConfig(services) {
        const checkboxes = document.querySelectorAll('.services-checkboxes input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = services.includes(checkbox.value);
        });
    }

    saveDeviceConfiguration() {
        if (!this.currentDevice) return;

        const config = {
            // Basic configuration
            name: document.getElementById('device-name-input').value,
            mode: document.getElementById('device-mode').value,
            status: document.getElementById('device-status').value,

            // Network configuration
            ipAddress: document.getElementById('ip-address').value,
            subnetMask: document.getElementById('subnet-mask').value,
            gateway: document.getElementById('device-default-gateway').value,
            dnsServer: document.getElementById('dns-server').value,

            // Advanced configurations
            routes: this.collectRoutes(),
            vlans: this.collectVLANs(),
            wireless: this.collectWirelessConfig(),
            services: this.collectServices(),

            // Metadata
            deviceType: this.currentDevice.type,
            configuredAt: new Date().toISOString()
        };

        // Validate configuration
        const validation = this.validateDeviceConfig(config);
        if (!validation.valid) {
            this.showConfigError(validation.message);
            return;
        }

        // Save to local storage and update device
        this.deviceConfigs.set(this.currentDevice.id, config);
        
        // Update device object
        this.currentDevice.config = config;
        if (config.name) {
            this.currentDevice.name = config.name;
        }

        // Notify validation system
        this.notifyConfigurationChange();

        // Close modal and show success
        this.closeConfigModal();
        this.showConfigSuccess('Device configuration saved successfully');

        // Update device display in editor
        this.updateDeviceDisplay(this.currentDevice);
    }

    collectRoutes() {
        const routes = [];
        const routeRows = document.querySelectorAll('#routes-list .route-row');

        routeRows.forEach(row => {
            const destination = row.querySelector('[data-field="destination"]').value;
            const gateway = row.querySelector('[data-field="gateway"]').value;
            const iface = row.querySelector('[data-field="interface"]').value;

            if (destination && gateway && iface) {
                routes.push({ destination, gateway, interface: iface });
            }
        });

        return routes;
    }

    collectVLANs() {
        const vlans = [];
        const vlanRows = document.querySelectorAll('#vlans-list .route-row');

        vlanRows.forEach(row => {
            const id = row.querySelector('[data-field="id"]').value;
            const name = row.querySelector('[data-field="name"]').value;
            const type = row.querySelector('[data-field="type"]').value;

            if (id && name) {
                vlans.push({ id: parseInt(id), name, type });
            }
        });

        return vlans;
    }

    collectWirelessConfig() {
        return {
            ssid: document.getElementById('wireless-ssid').value,
            security: document.getElementById('wireless-security').value,
            password: document.getElementById('wireless-password').value
        };
    }

    collectServices() {
        const services = [];
        const checkboxes = document.querySelectorAll('.services-checkboxes input[type="checkbox"]:checked');
        
        checkboxes.forEach(checkbox => {
            services.push(checkbox.value);
        });

        return services;
    }

    validateDeviceConfig(config) {
        const errors = [];

        // IP address validation
        if (config.ipAddress && !this.isValidIP(config.ipAddress)) {
            errors.push('Invalid IP address format');
        }

        // Gateway validation
        if (config.gateway && !this.isValidIP(config.gateway)) {
            errors.push('Invalid gateway IP address format');
        }

        // DNS server validation
        if (config.dnsServer && !this.isValidIP(config.dnsServer)) {
            errors.push('Invalid DNS server IP address format');
        }

        // Device-specific validation
        if (config.deviceType === 'router' && config.routes.length === 0) {
            errors.push('Router must have at least one route configured');
        }

        if (config.deviceType === 'access-point' && !config.wireless.ssid) {
            errors.push('Access point must have SSID configured');
        }

        return {
            valid: errors.length === 0,
            message: errors.join(', ')
        };
    }

    isValidIP(ip) {
        const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipRegex.test(ip);
    }

    validateCurrentDeviceConfig() {
        if (!this.currentDevice) return;

        const config = {
            ipAddress: document.getElementById('ip-address').value,
            subnetMask: document.getElementById('subnet-mask').value,
            gateway: document.getElementById('device-default-gateway').value,
            dnsServer: document.getElementById('dns-server').value
        };

        // IP validation
        const ipValid = config.ipAddress && this.isValidIP(config.ipAddress);
        this.updateValidationStatus('ip-validation', ipValid);

        // Connectivity validation (simplified)
        const connectivityValid = ipValid && config.subnetMask;
        this.updateValidationStatus('connectivity-validation', connectivityValid);

        // Gateway reachability
        const gatewayValid = !config.gateway || this.isValidIP(config.gateway);
        this.updateValidationStatus('reachability-validation', gatewayValid);

        return ipValid && connectivityValid && gatewayValid;
    }

    updateValidationStatus(elementId, isValid) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.className = `validation-status ${isValid ? 'valid' : 'invalid'}`;
        element.innerHTML = isValid ? '<i class="fas fa-check"></i>' : '<i class="fas fa-times"></i>';
    }

    notifyConfigurationChange() {
        // Notify enhanced validation system
        if (window.enhancedValidator) {
            window.enhancedValidator.checkConfigurationCompletion();
        }

        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('configurationUpdated', {
            detail: {
                deviceId: this.currentDevice.id,
                config: this.deviceConfigs.get(this.currentDevice.id)
            }
        }));
    }

    updateDeviceDisplay(device) {
        // Update device visual in the editor
        const deviceElement = document.querySelector(`[data-device-id="${device.id}"]`);
        if (deviceElement) {
            const config = this.deviceConfigs.get(device.id);
            
            // Add configuration indicator
            let indicator = deviceElement.querySelector('.config-indicator');
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.className = 'config-indicator';
                deviceElement.appendChild(indicator);
            }

            const hasBasicConfig = config && config.ipAddress;
            indicator.innerHTML = hasBasicConfig ? 
                '<i class="fas fa-check-circle" style="color: var(--success-color);"></i>' :
                '<i class="fas fa-exclamation-circle" style="color: var(--warning-color);"></i>';

            // Update device name display
            const nameElement = deviceElement.querySelector('.device-name');
            if (nameElement && config && config.name) {
                nameElement.textContent = config.name;
            }
        }
    }

    showConfigError(message) {
        // Simple error display - can be enhanced with toast system
        alert('Configuration Error: ' + message);
    }

    showConfigSuccess(message) {
        // Simple success display - can be enhanced with toast system
        if (window.editor && window.editor.showToast) {
            window.editor.showToast(message, 'success');
        }
    }

    attachEventListeners() {
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            }
        });

        // Add route button
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-route-btn')) {
                this.addRouteRow();
            }
        });

        // Add VLAN button
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-vlan-btn')) {
                this.addVLANRow();
            }
        });

        // Save configuration
        document.addEventListener('click', (e) => {
            if (e.target.id === 'save-device-config' || e.target.closest('#save-device-config')) {
                this.saveDeviceConfiguration();
            }
        });

        // Validate device config
        document.addEventListener('click', (e) => {
            if (e.target.id === 'validate-device-config' || e.target.closest('#validate-device-config')) {
                this.validateCurrentDeviceConfig();
            }
        });

        // Real-time IP validation
        document.addEventListener('input', (e) => {
            if (e.target.id === 'ip-address' || e.target.id === 'device-default-gateway' || e.target.id === 'dns-server') {
                setTimeout(() => this.validateCurrentDeviceConfig(), 300);
            }
        });

        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeConfigModal();
            }
        });

        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.getElementById('enhanced-device-config-modal').classList.contains('active')) {
                this.closeConfigModal();
            }
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `${tabName}-panel`);
        });
    }

    // Public API for device configuration
    getDeviceConfiguration(deviceId) {
        return this.deviceConfigs.get(deviceId);
    }

    setDeviceConfiguration(deviceId, config) {
        this.deviceConfigs.set(deviceId, config);
        this.notifyConfigurationChange();
    }

    hasDeviceConfiguration(deviceId) {
        const config = this.deviceConfigs.get(deviceId);
        return config && config.ipAddress;
    }

    exportConfigurations() {
        const configs = {};
        this.deviceConfigs.forEach((config, deviceId) => {
            configs[deviceId] = config;
        });
        return configs;
    }

    importConfigurations(configs) {
        Object.entries(configs).forEach(([deviceId, config]) => {
            this.deviceConfigs.set(deviceId, config);
        });
        this.notifyConfigurationChange();
    }
}

// Initialize enhanced device configurator
document.addEventListener('DOMContentLoaded', () => {
    window.deviceConfigurator = new EnhancedDeviceConfigurator();
    console.log('✓ Enhanced Device Configurator initialized');
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedDeviceConfigurator;
}

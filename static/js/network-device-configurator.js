/**
 * Enhanced Device Configurator for Network Simulation
 * Provides comprehensive device configuration similar to admin simulation editor
 */

class NetworkDeviceConfigurator {
    constructor() {
        this.currentDevice = null;
        this.configHistory = [];
        this.validationRules = {};
        
        // Device configuration templates
        this.configTemplates = {
            router: {
                hostname: 'Router1',
                interfaces: {
                    'FastEthernet0/0': { ip: '192.168.1.1', mask: '255.255.255.0', status: 'up' },
                    'FastEthernet0/1': { ip: '192.168.2.1', mask: '255.255.255.0', status: 'up' }
                },
                routes: [],
                services: ['dhcp', 'nat', 'routing'],
                security: {
                    accessLists: [],
                    firewall: false
                }
            },
            switch: {
                hostname: 'Switch1',
                vlans: {
                    1: { name: 'default', ports: [] },
                    10: { name: 'data', ports: [] },
                    20: { name: 'voice', ports: [] }
                },
                interfaces: {},
                spanningTree: {
                    enabled: true,
                    priority: 32768
                },
                security: {
                    portSecurity: false,
                    stormControl: false
                }
            },
            server: {
                hostname: 'Server1',
                os: 'Linux',
                services: ['web', 'dns', 'dhcp'],
                network: {
                    ip: '192.168.1.10',
                    mask: '255.255.255.0',
                    gateway: '192.168.1.1'
                },
                applications: []
            }
        };
        
        this.init();
    }
    
    init() {
        this.createConfigModal();
        this.setupValidation();
        this.loadTemplates();
        
        console.log('🔧 Device Configurator initialized');
    }
    
    createConfigModal() {
        // Check if modal already exists
        if (document.getElementById('network-device-config-modal')) {
            return;
        }
        
        const modal = document.createElement('div');
        modal.id = 'network-device-config-modal';
        modal.className = 'device-config-modal';
        modal.innerHTML = `
            <div class="modal-backdrop" onclick="networkDeviceConfigurator.closeConfigPanel()"></div>
            <div class="modal-container">
                <div class="modal-header">
                    <h3 class="modal-title">
                        <i class="fas fa-cog"></i>
                        Device Configuration
                    </h3>
                    <button class="close-btn" onclick="networkDeviceConfigurator.closeConfigPanel()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <div class="config-tabs">
                        <button class="tab-btn active" data-tab="general">
                            <i class="fas fa-info-circle"></i>
                            General
                        </button>
                        <button class="tab-btn" data-tab="network">
                            <i class="fas fa-network-wired"></i>
                            Network
                        </button>
                        <button class="tab-btn" data-tab="interfaces">
                            <i class="fas fa-ethernet"></i>
                            Interfaces
                        </button>
                        <button class="tab-btn" data-tab="routing">
                            <i class="fas fa-route"></i>
                            Routing
                        </button>
                        <button class="tab-btn" data-tab="security">
                            <i class="fas fa-shield-alt"></i>
                            Security
                        </button>
                        <button class="tab-btn" data-tab="services">
                            <i class="fas fa-server"></i>
                            Services
                        </button>
                        <button class="tab-btn" data-tab="cli">
                            <i class="fas fa-terminal"></i>
                            CLI
                        </button>
                    </div>
                    
                    <div class="tab-content">
                        <!-- General Tab -->
                        <div class="tab-panel active" data-tab="general">
                            <div class="form-grid">
                                <div class="form-group">
                                    <label>Device Type</label>
                                    <input type="text" id="device-type" readonly />
                                </div>
                                <div class="form-group">
                                    <label>Hostname</label>
                                    <input type="text" id="device-hostname" placeholder="Enter hostname" />
                                </div>
                                <div class="form-group">
                                    <label>Description</label>
                                    <input type="text" id="device-description" placeholder="Device description" />
                                </div>
                                <div class="form-group">
                                    <label>Location</label>
                                    <input type="text" id="device-location" placeholder="Physical location" />
                                </div>
                                <div class="form-group">
                                    <label>Administrative Status</label>
                                    <select id="device-admin-status">
                                        <option value="up">Up</option>
                                        <option value="down">Down</option>
                                        <option value="testing">Testing</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Model</label>
                                    <input type="text" id="device-model" placeholder="Device model" />
                                </div>
                            </div>
                        </div>
                        
                        <!-- Network Tab -->
                        <div class="tab-panel" data-tab="network">
                            <div class="form-grid">
                                <div class="form-group">
                                    <label>Management IP</label>
                                    <input type="text" id="mgmt-ip" placeholder="192.168.1.1" />
                                </div>
                                <div class="form-group">
                                    <label>Subnet Mask</label>
                                    <input type="text" id="mgmt-mask" placeholder="255.255.255.0" />
                                </div>
                                <div class="form-group">
                                    <label>Default Gateway</label>
                                    <input type="text" id="mgmt-gateway" placeholder="192.168.1.1" />
                                </div>
                                <div class="form-group">
                                    <label>DNS Server</label>
                                    <input type="text" id="mgmt-dns" placeholder="8.8.8.8" />
                                </div>
                                <div class="form-group">
                                    <label>DHCP Client</label>
                                    <select id="dhcp-client">
                                        <option value="false">Static IP</option>
                                        <option value="true">DHCP</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Domain Name</label>
                                    <input type="text" id="domain-name" placeholder="example.com" />
                                </div>
                            </div>
                        </div>
                        
                        <!-- Interfaces Tab -->
                        <div class="tab-panel" data-tab="interfaces">
                            <div class="interface-header">
                                <h4>Network Interfaces</h4>
                                <button class="btn btn-sm btn-primary" onclick="networkDeviceConfigurator.addInterface()">
                                    <i class="fas fa-plus"></i>
                                    Add Interface
                                </button>
                            </div>
                            <div id="interfaces-container">
                                <!-- Interfaces will be populated here -->
                            </div>
                        </div>
                        
                        <!-- Routing Tab -->
                        <div class="tab-panel" data-tab="routing">
                            <div class="routing-header">
                                <h4>Routing Configuration</h4>
                                <button class="btn btn-sm btn-primary" onclick="networkDeviceConfigurator.addRoute()">
                                    <i class="fas fa-plus"></i>
                                    Add Route
                                </button>
                            </div>
                            <div class="routing-protocols">
                                <h5>Routing Protocols</h5>
                                <div class="protocol-checkboxes">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="rip-enabled">
                                        <span>RIP</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="ospf-enabled">
                                        <span>OSPF</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="eigrp-enabled">
                                        <span>EIGRP</span>
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="bgp-enabled">
                                        <span>BGP</span>
                                    </label>
                                </div>
                            </div>
                            <div id="routing-table">
                                <!-- Static routes will be populated here -->
                            </div>
                        </div>
                        
                        <!-- Security Tab -->
                        <div class="tab-panel" data-tab="security">
                            <div class="security-sections">
                                <div class="security-section">
                                    <h5>Access Control</h5>
                                    <div class="form-group">
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="enable-acl">
                                            <span>Enable Access Control Lists</span>
                                        </label>
                                    </div>
                                    <div id="acl-container">
                                        <!-- ACL rules will be populated here -->
                                    </div>
                                </div>
                                
                                <div class="security-section">
                                    <h5>Authentication</h5>
                                    <div class="form-group">
                                        <label>Console Password</label>
                                        <input type="password" id="console-password" />
                                    </div>
                                    <div class="form-group">
                                        <label>Enable Password</label>
                                        <input type="password" id="enable-password" />
                                    </div>
                                    <div class="form-group">
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="enable-ssh">
                                            <span>Enable SSH</span>
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Services Tab -->
                        <div class="tab-panel" data-tab="services">
                            <div class="services-grid">
                                <div class="service-category">
                                    <h5>Network Services</h5>
                                    <div class="service-checkboxes">
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="dhcp-service">
                                            <span>DHCP Server</span>
                                        </label>
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="dns-service">
                                            <span>DNS Server</span>
                                        </label>
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="ntp-service">
                                            <span>NTP Client</span>
                                        </label>
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="snmp-service">
                                            <span>SNMP</span>
                                        </label>
                                    </div>
                                </div>
                                
                                <div class="service-category">
                                    <h5>Application Services</h5>
                                    <div class="service-checkboxes">
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="web-service">
                                            <span>Web Server</span>
                                        </label>
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="ftp-service">
                                            <span>FTP Server</span>
                                        </label>
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="mail-service">
                                            <span>Mail Server</span>
                                        </label>
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="database-service">
                                            <span>Database Server</span>
                                        </label>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="service-configuration" id="service-config">
                                <!-- Service-specific configuration will appear here -->
                            </div>
                        </div>
                        
                        <!-- CLI Tab -->
                        <div class="tab-panel" data-tab="cli">
                            <div class="cli-section">
                                <div class="cli-header">
                                    <h5>Command Line Interface</h5>
                                    <div class="cli-controls">
                                        <button class="btn btn-sm btn-secondary" onclick="networkDeviceConfigurator.clearCLI()">
                                            <i class="fas fa-eraser"></i>
                                            Clear
                                        </button>
                                        <button class="btn btn-sm btn-primary" onclick="networkDeviceConfigurator.saveCLIConfig()">
                                            <i class="fas fa-save"></i>
                                            Save Config
                                        </button>
                                    </div>
                                </div>
                                <div class="cli-terminal" id="device-cli-terminal">
                                    <div class="cli-output" id="device-cli-output">
                                        <div class="cli-prompt">Device> <span class="cursor">_</span></div>
                                    </div>
                                    <div class="cli-input-container">
                                        <span class="cli-prompt">Device> </span>
                                        <input type="text" class="cli-input" id="device-cli-input" 
                                               placeholder="Enter command..." 
                                               onkeydown="networkDeviceConfigurator.handleCLICommand(event)" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="modal-footer">
                    <div class="footer-actions">
                        <button class="btn btn-secondary" onclick="networkDeviceConfigurator.resetConfig()">
                            <i class="fas fa-undo"></i>
                            Reset
                        </button>
                        <button class="btn btn-warning" onclick="networkDeviceConfigurator.loadTemplate()">
                            <i class="fas fa-file-import"></i>
                            Load Template
                        </button>
                        <button class="btn btn-info" onclick="networkDeviceConfigurator.validateConfig()">
                            <i class="fas fa-check-circle"></i>
                            Validate
                        </button>
                        <button class="btn btn-success" onclick="networkDeviceConfigurator.applyConfig()">
                            <i class="fas fa-check"></i>
                            Apply Configuration
                        </button>
                        <button class="btn btn-primary" onclick="networkDeviceConfigurator.saveConfig()">
                            <i class="fas fa-save"></i>
                            Save
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        this.setupModalEventListeners();
        
        console.log('🎨 Device config modal created');
    }
    
    setupModalEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.tab-btn').dataset.tab);
            });
        });
        
        // Form validation on input
        document.querySelectorAll('#network-device-config-modal input, #network-device-config-modal select').forEach(input => {
            input.addEventListener('change', () => this.validateField(input));
            input.addEventListener('blur', () => this.validateField(input));
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isModalOpen()) {
                this.closeConfigPanel();
            }
        });
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            }
        });
        
        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
            if (panel.dataset.tab === tabName) {
                panel.classList.add('active');
            }
        });
        
        // Load tab-specific data
        this.loadTabData(tabName);
    }
    
    loadTabData(tabName) {
        if (!this.currentDevice) return;
        
        switch (tabName) {
            case 'interfaces':
                this.populateInterfaces();
                break;
            case 'routing':
                this.populateRouting();
                break;
            case 'security':
                this.populateSecurity();
                break;
            case 'services':
                this.populateServices();
                break;
            case 'cli':
                this.initializeCLI();
                break;
        }
    }
    
    openConfigPanel(device) {
        this.currentDevice = device;
        const modal = document.getElementById('network-device-config-modal');
        
        if (!modal) {
            console.error('❌ Config modal not found');
            return;
        }
        
        // Populate form with device data
        this.populateConfigForm(device);
        
        // Show modal
        modal.classList.add('active');
        
        // Focus first input
        setTimeout(() => {
            const firstInput = modal.querySelector('input:not([readonly])');
            if (firstInput) firstInput.focus();
        }, 100);
        
        console.log('⚙️ Opened config panel for:', device.id);
    }
    
    closeConfigPanel() {
        const modal = document.getElementById('network-device-config-modal');
        if (modal) {
            modal.classList.remove('active');
        }
        
        this.currentDevice = null;
        console.log('❌ Closed config panel');
    }
    
    isModalOpen() {
        const modal = document.getElementById('network-device-config-modal');
        return modal && modal.classList.contains('active');
    }
    
    populateConfigForm(device) {
        // General tab
        document.getElementById('device-type').value = device.type;
        document.getElementById('device-hostname').value = device.config.hostname || device.label;
        document.getElementById('device-description').value = device.config.description || '';
        document.getElementById('device-location').value = device.config.location || '';
        document.getElementById('device-admin-status').value = device.state || 'up';
        document.getElementById('device-model').value = device.config.model || '';
        
        // Network tab
        document.getElementById('mgmt-ip').value = device.config.ipAddress || '';
        document.getElementById('mgmt-mask').value = device.config.subnetMask || '255.255.255.0';
        document.getElementById('mgmt-gateway').value = device.config.gateway || '';
        document.getElementById('mgmt-dns').value = device.config.dns || '8.8.8.8';
        document.getElementById('dhcp-client').value = device.config.dhcpClient || 'false';
        document.getElementById('domain-name').value = device.config.domainName || '';
        
        // Load other tabs dynamically
        this.loadTabData('general');
    }
    
    populateInterfaces() {
        const container = document.getElementById('interfaces-container');
        container.innerHTML = '';
        
        if (!this.currentDevice.interfaces) {
            this.currentDevice.interfaces = {};
        }
        
        Object.entries(this.currentDevice.interfaces).forEach(([name, config]) => {
            this.addInterfaceRow(name, config);
        });
        
        // Add empty interface if none exist
        if (Object.keys(this.currentDevice.interfaces).length === 0) {
            this.addInterface();
        }
    }
    
    addInterfaceRow(name, config) {
        const container = document.getElementById('interfaces-container');
        const interfaceDiv = document.createElement('div');
        interfaceDiv.className = 'interface-row';
        interfaceDiv.innerHTML = `
            <div class="interface-header">
                <h6>${name}</h6>
                <button class="btn btn-sm btn-danger" onclick="this.closest('.interface-row').remove()">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="interface-config">
                <div class="form-row">
                    <div class="form-group">
                        <label>IP Address</label>
                        <input type="text" value="${config.ipAddress || ''}" data-field="ipAddress" />
                    </div>
                    <div class="form-group">
                        <label>Subnet Mask</label>
                        <input type="text" value="${config.subnetMask || ''}" data-field="subnetMask" />
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select data-field="status">
                            <option value="up" ${config.status === 'up' ? 'selected' : ''}>Up</option>
                            <option value="down" ${config.status === 'down' ? 'selected' : ''}>Down</option>
                            <option value="admin-down" ${config.status === 'admin-down' ? 'selected' : ''}>Admin Down</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>VLAN</label>
                        <input type="number" value="${config.vlan || 1}" data-field="vlan" min="1" max="4094" />
                    </div>
                    <div class="form-group">
                        <label>Duplex</label>
                        <select data-field="duplex">
                            <option value="auto" ${config.duplex === 'auto' ? 'selected' : ''}>Auto</option>
                            <option value="full" ${config.duplex === 'full' ? 'selected' : ''}>Full</option>
                            <option value="half" ${config.duplex === 'half' ? 'selected' : ''}>Half</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Speed</label>
                        <select data-field="speed">
                            <option value="auto" ${config.speed === 'auto' ? 'selected' : ''}>Auto</option>
                            <option value="10" ${config.speed === '10' ? 'selected' : ''}>10 Mbps</option>
                            <option value="100" ${config.speed === '100' ? 'selected' : ''}>100 Mbps</option>
                            <option value="1000" ${config.speed === '1000' ? 'selected' : ''}>1 Gbps</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(interfaceDiv);
    }
    
    addInterface() {
        if (!this.currentDevice) return;
        
        const interfaceCount = Object.keys(this.currentDevice.interfaces).length;
        const newName = `eth${interfaceCount}`;
        
        this.currentDevice.interfaces[newName] = {
            name: newName,
            ipAddress: '',
            subnetMask: '255.255.255.0',
            status: 'up',
            vlan: 1,
            duplex: 'auto',
            speed: 'auto'
        };
        
        this.addInterfaceRow(newName, this.currentDevice.interfaces[newName]);
    }
    
    populateRouting() {
        if (!this.currentDevice.config.routingTable) {
            this.currentDevice.config.routingTable = [];
        }
        
        // Populate routing protocols
        const protocols = this.currentDevice.config.routingProtocols || {};
        document.getElementById('rip-enabled').checked = protocols.rip || false;
        document.getElementById('ospf-enabled').checked = protocols.ospf || false;
        document.getElementById('eigrp-enabled').checked = protocols.eigrp || false;
        document.getElementById('bgp-enabled').checked = protocols.bgp || false;
        
        // Populate static routes
        this.renderRoutingTable();
    }
    
    renderRoutingTable() {
        const container = document.getElementById('routing-table');
        container.innerHTML = '<h5>Static Routes</h5>';
        
        this.currentDevice.config.routingTable.forEach((route, index) => {
            this.addRouteRow(route, index);
        });
    }
    
    addRoute() {
        if (!this.currentDevice.config.routingTable) {
            this.currentDevice.config.routingTable = [];
        }
        
        const newRoute = {
            network: '0.0.0.0',
            mask: '0.0.0.0',
            gateway: '192.168.1.1',
            interface: 'eth0',
            metric: 1
        };
        
        this.currentDevice.config.routingTable.push(newRoute);
        this.addRouteRow(newRoute, this.currentDevice.config.routingTable.length - 1);
    }
    
    addRouteRow(route, index) {
        const container = document.getElementById('routing-table');
        const routeDiv = document.createElement('div');
        routeDiv.className = 'route-row';
        routeDiv.innerHTML = `
            <div class="route-config">
                <div class="form-row">
                    <div class="form-group">
                        <label>Network</label>
                        <input type="text" value="${route.network}" data-field="network" />
                    </div>
                    <div class="form-group">
                        <label>Netmask</label>
                        <input type="text" value="${route.mask}" data-field="mask" />
                    </div>
                    <div class="form-group">
                        <label>Gateway</label>
                        <input type="text" value="${route.gateway}" data-field="gateway" />
                    </div>
                    <div class="form-group">
                        <label>Interface</label>
                        <input type="text" value="${route.interface}" data-field="interface" />
                    </div>
                    <div class="form-group">
                        <label>Metric</label>
                        <input type="number" value="${route.metric}" data-field="metric" min="1" />
                    </div>
                    <div class="form-group">
                        <button class="btn btn-sm btn-danger" onclick="this.closest('.route-row').remove()">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(routeDiv);
    }
    
    populateSecurity() {
        const security = this.currentDevice.config.security || {};
        
        // Populate security settings
        document.getElementById('enable-acl').checked = security.aclEnabled || false;
        document.getElementById('console-password').value = security.consolePassword || '';
        document.getElementById('enable-password').value = security.enablePassword || '';
        document.getElementById('enable-ssh').checked = security.sshEnabled || false;
    }
    
    populateServices() {
        const services = this.currentDevice.config.services || [];
        
        // Network services
        document.getElementById('dhcp-service').checked = services.includes('dhcp');
        document.getElementById('dns-service').checked = services.includes('dns');
        document.getElementById('ntp-service').checked = services.includes('ntp');
        document.getElementById('snmp-service').checked = services.includes('snmp');
        
        // Application services
        document.getElementById('web-service').checked = services.includes('web');
        document.getElementById('ftp-service').checked = services.includes('ftp');
        document.getElementById('mail-service').checked = services.includes('mail');
        document.getElementById('database-service').checked = services.includes('database');
    }
    
    initializeCLI() {
        const output = document.getElementById('device-cli-output');
        const input = document.getElementById('device-cli-input');
        
        if (!this.currentDevice.cliHistory) {
            this.currentDevice.cliHistory = [];
        }
        
        // Clear and initialize CLI
        output.innerHTML = `
            <div class="cli-welcome">
                <div class="cli-banner">
                    ==========================================
                    ${this.currentDevice.config.hostname} Network Device CLI
                    ==========================================
                    Type 'help' for available commands
                </div>
                <div class="cli-prompt">${this.currentDevice.config.hostname}> <span class="cursor">_</span></div>
            </div>
        `;
        
        // Set up input
        if (input) {
            input.focus();
        }
    }
    
    handleCLICommand(event) {
        if (event.key === 'Enter') {
            const input = event.target;
            const command = input.value.trim();
            
            if (command) {
                this.executeCLICommand(command);
                input.value = '';
            }
        } else if (event.key === 'Tab') {
            event.preventDefault();
            this.autoCompleteCLICommand(event.target);
        }
    }
    
    executeCLICommand(command) {
        const output = document.getElementById('device-cli-output');
        const hostname = this.currentDevice.config.hostname;
        
        // Add command to history
        this.currentDevice.cliHistory.push(command);
        
        // Add command line to output
        const commandLine = document.createElement('div');
        commandLine.className = 'cli-command';
        commandLine.innerHTML = `${hostname}> ${command}`;
        output.appendChild(commandLine);
        
        // Process command
        const response = this.processCLICommand(command);
        
        // Add response to output
        if (response) {
            const responseLine = document.createElement('div');
            responseLine.className = 'cli-response';
            responseLine.innerHTML = response;
            output.appendChild(responseLine);
        }
        
        // ✅ TASK ASSIGNMENT: Dispatch event for CLI command tracking
        console.log('📋 [CLI→TASK] Configurator dispatching cli-command-executed event:', { device: this.currentDevice.id, command });
        document.dispatchEvent(new CustomEvent('cli-command-executed', {
            detail: {
                device_id: this.currentDevice.id,
                command: command,
                output: response || '',
                timestamp: new Date().toISOString()
            }
        }));
        
        // Add new prompt
        const prompt = document.createElement('div');
        prompt.className = 'cli-prompt';
        prompt.innerHTML = `${hostname}> <span class="cursor">_</span>`;
        output.appendChild(prompt);
        
        // Scroll to bottom
        output.scrollTop = output.scrollHeight;
    }
    
    processCLICommand(command) {
        const cmd = command.toLowerCase().split(' ');
        
        switch (cmd[0]) {
            case 'help':
                return this.getHelpText();
            case 'show':
                return this.executeShowCommand(cmd.slice(1));
            case 'config':
            case 'configure':
                return this.enterConfigMode();
            case 'ping':
                return this.executePing(cmd[1]);
            case 'traceroute':
                return this.executeTraceroute(cmd[1]);
            case 'clear':
                return this.clearCLI();
            case 'exit':
                return 'Goodbye!';
            default:
                return `% Invalid command: ${command}`;
        }
    }
    
    getHelpText() {
        return `
Available Commands:
  help                   - Show this help
  show <option>          - Display information
    interfaces           - Show interface configuration
    ip route            - Show routing table
    version             - Show device version
    running-config      - Show running configuration
  ping <ip>              - Test connectivity
  traceroute <ip>        - Trace route to destination
  config                 - Enter configuration mode
  clear                  - Clear screen
  exit                   - Exit CLI
        `;
    }
    
    executeShowCommand(args) {
        if (args.length === 0) return '% Incomplete command';
        
        switch (args[0]) {
            case 'interfaces':
                return this.showInterfaces();
            case 'ip':
                if (args.length > 1) {
                    if (args[1] === 'route') return this.showRoutes();
                    if (args[1] === 'interface') {
                        if (args.length > 2 && args[2] === 'brief') {
                            return this.showIPInterfaceBrief();
                        } else {
                            return this.showIPInterface();
                        }
                    }
                }
                return '% Incomplete command. Available: ip route, ip interface [brief]';
            case 'version':
                return this.showVersion();
            case 'running-config':
                return this.showRunningConfig();
        }
        
        return `% Invalid show command: ${args.join(' ')}`;
    }
    
    showInterfaces() {
        let output = 'Interface                  IP-Address      OK? Method Status                Protocol\n';
        Object.entries(this.currentDevice.interfaces).forEach(([name, config]) => {
            const ip = config.ipAddress || 'unassigned';
            const status = config.status || 'administratively down';
            const protocol = status === 'up' ? 'up' : 'down';
            const method = ip !== 'unassigned' ? 'manual' : 'unset';
            const okStatus = ip !== 'unassigned' ? 'YES' : 'NO';
            
            output += `${name.padEnd(25)} ${ip.padEnd(15)} ${okStatus.padEnd(3)} ${method.padEnd(6)} ${status.padEnd(20)} ${protocol}\n`;
        });
        return output;
    }
    
    showIPInterface() {
        let output = '';
        Object.entries(this.currentDevice.interfaces).forEach(([name, config]) => {
            const ip = config.ipAddress || 'unassigned';
            const status = config.status || 'administratively down';
            const protocol = status === 'up' ? 'up' : 'down';
            
            output += `${name} is ${status}, line protocol is ${protocol}\n`;
            if (ip !== 'unassigned') {
                output += `  Internet address is ${ip}\n`;
                output += `  Broadcast address is 255.255.255.255\n`;
            } else {
                output += `  Internet protocol processing disabled\n`;
            }
            output += `  MTU is 1500 bytes\n`;
            output += `  Helper address is not set\n`;
            output += `  Directed broadcast forwarding is disabled\n\n`;
        });
        return output;
    }
    
    showIPInterfaceBrief() {
        let output = 'Interface                  IP-Address      OK? Method Status                Protocol\n';
        Object.entries(this.currentDevice.interfaces).forEach(([name, config]) => {
            const ip = config.ipAddress || 'unassigned';
            const status = config.status || 'administratively down';
            const protocol = status === 'up' ? 'up' : 'down';
            const method = ip !== 'unassigned' ? 'manual' : 'unset';
            const okStatus = ip !== 'unassigned' ? 'YES' : 'NO';
            
            output += `${name.padEnd(25)} ${ip.padEnd(15)} ${okStatus.padEnd(3)} ${method.padEnd(6)} ${status.padEnd(20)} ${protocol}\n`;
        });
        return output;
    }
    
    showRoutes() {
        let output = 'Routing Table:\n';
        if (this.currentDevice.config.routingTable) {
            this.currentDevice.config.routingTable.forEach(route => {
                output += `${route.network}/${route.mask} via ${route.gateway} [${route.metric}]\n`;
            });
        }
        return output || 'No routes configured';
    }
    
    showVersion() {
        return `
Device: ${this.currentDevice.type}
Hostname: ${this.currentDevice.config.hostname}
Model: ${this.currentDevice.config.model || 'Generic'}
OS Version: NetworkOS 1.0
Uptime: 0 days, 0 hours, 0 minutes
        `;
    }
    
    showRunningConfig() {
        return this.generateRunningConfig();
    }
    
    generateRunningConfig() {
        let config = `!\n! Running configuration\n!\n`;
        config += `hostname ${this.currentDevice.config.hostname}\n`;
        config += `!\n`;
        
        // Interfaces
        Object.entries(this.currentDevice.interfaces).forEach(([name, iface]) => {
            config += `interface ${name}\n`;
            if (iface.ipAddress) {
                config += ` ip address ${iface.ipAddress} ${iface.subnetMask}\n`;
            }
            config += ` ${iface.status === 'up' ? 'no shutdown' : 'shutdown'}\n`;
            config += `!\n`;
        });
        
        // Routes
        if (this.currentDevice.config.routingTable) {
            this.currentDevice.config.routingTable.forEach(route => {
                config += `ip route ${route.network} ${route.mask} ${route.gateway}\n`;
            });
        }
        
        config += `!\nend\n`;
        return config;
    }
    
    executePing(target) {
        if (!target) return '% Usage: ping <ip-address>';
        
        // Validate IP address format
        const ipRegex = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (!ipRegex.test(target)) {
            return `% Invalid IP address: ${target}`;
        }
        
        // Check if target device exists
        let targetExists = false;
        if (window.editor && window.editor.devices) {
            for (const device of window.editor.devices) {
                if (window.deviceConfigurator) {
                    const config = window.deviceConfigurator.getDeviceConfiguration(device.id);
                    if (config && config.ipAddress === target) {
                        targetExists = true;
                        break;
                    }
                }
            }
        }
        
        // Generate realistic ping output
        const delay = Math.floor(Math.random() * 5) + 1;
        
        if (targetExists || ['8.8.8.8', '1.1.1.1', '208.67.222.222'].includes(target)) {
            return `
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to ${target}, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = ${delay}/${delay+1}/${delay+3} ms
            `.trim();
        } else {
            return `
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to ${target}, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)
            `.trim();
        }
    }
    
    clearCLI() {
        const output = document.getElementById('device-cli-output');
        if (output) {
            this.initializeCLI();
        }
        return '';
    }
    
    validateField(field) {
        const value = field.value;
        const fieldType = field.type;
        let isValid = true;
        let errorMessage = '';
        
        // Clear previous validation
        field.classList.remove('invalid', 'valid');
        
        // Validate based on field type and content
        if (fieldType === 'text' && field.id.includes('ip')) {
            isValid = this.isValidIP(value) || value === '';
            errorMessage = 'Invalid IP address format';
        } else if (field.id.includes('mask')) {
            isValid = this.isValidSubnetMask(value) || value === '';
            errorMessage = 'Invalid subnet mask';
        } else if (field.id.includes('hostname')) {
            isValid = /^[a-zA-Z0-9-_.]+$/.test(value) || value === '';
            errorMessage = 'Invalid hostname format';
        }
        
        // Apply validation styling
        if (value !== '') {
            field.classList.add(isValid ? 'valid' : 'invalid');
            
            if (!isValid) {
                this.showFieldError(field, errorMessage);
            }
        }
        
        return isValid;
    }
    
    isValidIP(ip) {
        const regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return regex.test(ip);
    }
    
    isValidSubnetMask(mask) {
        const validMasks = [
            '255.255.255.255', '255.255.255.254', '255.255.255.252', '255.255.255.248',
            '255.255.255.240', '255.255.255.224', '255.255.255.192', '255.255.255.128',
            '255.255.255.0', '255.255.254.0', '255.255.252.0', '255.255.248.0',
            '255.255.240.0', '255.255.224.0', '255.255.192.0', '255.255.128.0',
            '255.255.0.0', '255.254.0.0', '255.252.0.0', '255.248.0.0',
            '255.240.0.0', '255.224.0.0', '255.192.0.0', '255.128.0.0', '255.0.0.0'
        ];
        return validMasks.includes(mask);
    }
    
    showFieldError(field, message) {
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }
    
    validateConfig() {
        const errors = [];
        const warnings = [];
        
        // Validate hostname
        if (!this.currentDevice.config.hostname) {
            errors.push('Hostname is required');
        }
        
        // Validate interfaces
        Object.entries(this.currentDevice.interfaces).forEach(([name, config]) => {
            if (config.ipAddress && !this.isValidIP(config.ipAddress)) {
                errors.push(`Invalid IP address on interface ${name}`);
            }
            if (config.subnetMask && !this.isValidSubnetMask(config.subnetMask)) {
                errors.push(`Invalid subnet mask on interface ${name}`);
            }
        });
        
        // Validate routes
        if (this.currentDevice.config.routingTable) {
            this.currentDevice.config.routingTable.forEach((route, index) => {
                if (!this.isValidIP(route.network)) {
                    errors.push(`Invalid network address in route ${index + 1}`);
                }
                if (!this.isValidIP(route.gateway)) {
                    errors.push(`Invalid gateway address in route ${index + 1}`);
                }
            });
        }
        
        // Show validation results
        this.showValidationResults(errors, warnings);
        
        return errors.length === 0;
    }
    
    showValidationResults(errors, warnings) {
        // Create validation modal or update existing one
        let modal = document.getElementById('validation-results-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'validation-results-modal';
            modal.className = 'validation-modal';
            document.body.appendChild(modal);
        }
        
        let content = '<h4>Configuration Validation</h4>';
        
        if (errors.length === 0 && warnings.length === 0) {
            content += '<div class="validation-success"><i class="fas fa-check-circle"></i> Configuration is valid!</div>';
        } else {
            if (errors.length > 0) {
                content += '<div class="validation-errors"><h5>Errors:</h5><ul>';
                errors.forEach(error => content += `<li>${error}</li>`);
                content += '</ul></div>';
            }
            
            if (warnings.length > 0) {
                content += '<div class="validation-warnings"><h5>Warnings:</h5><ul>';
                warnings.forEach(warning => content += `<li>${warning}</li>`);
                content += '</ul></div>';
            }
        }
        
        content += '<button onclick="this.parentElement.remove()">Close</button>';
        modal.innerHTML = content;
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (modal.parentElement) {
                modal.remove();
            }
        }, 5000);
    }
    
    collectFormData() {
        const config = {
            // General
            hostname: document.getElementById('device-hostname').value,
            description: document.getElementById('device-description').value,
            location: document.getElementById('device-location').value,
            adminStatus: document.getElementById('device-admin-status').value,
            model: document.getElementById('device-model').value,
            
            // Network
            ipAddress: document.getElementById('mgmt-ip').value,
            subnetMask: document.getElementById('mgmt-mask').value,
            gateway: document.getElementById('mgmt-gateway').value,
            dns: document.getElementById('mgmt-dns').value,
            dhcpClient: document.getElementById('dhcp-client').value === 'true',
            domainName: document.getElementById('domain-name').value,
            
            // Interfaces
            interfaces: this.collectInterfaceData(),
            
            // Routing
            routingTable: this.collectRoutingData(),
            routingProtocols: {
                rip: document.getElementById('rip-enabled').checked,
                ospf: document.getElementById('ospf-enabled').checked,
                eigrp: document.getElementById('eigrp-enabled').checked,
                bgp: document.getElementById('bgp-enabled').checked
            },
            
            // Security
            security: {
                aclEnabled: document.getElementById('enable-acl').checked,
                consolePassword: document.getElementById('console-password').value,
                enablePassword: document.getElementById('enable-password').value,
                sshEnabled: document.getElementById('enable-ssh').checked
            },
            
            // Services
            services: this.collectServicesData()
        };
        
        return config;
    }
    
    collectInterfaceData() {
        const interfaces = {};
        document.querySelectorAll('.interface-row').forEach(row => {
            const name = row.querySelector('h6').textContent;
            const config = {};
            
            row.querySelectorAll('input, select').forEach(input => {
                const field = input.dataset.field;
                if (field) {
                    config[field] = input.type === 'number' ? 
                        parseInt(input.value) : input.value;
                }
            });
            
            interfaces[name] = config;
        });
        
        return interfaces;
    }
    
    collectRoutingData() {
        const routes = [];
        document.querySelectorAll('.route-row').forEach(row => {
            const route = {};
            
            row.querySelectorAll('input').forEach(input => {
                const field = input.dataset.field;
                if (field) {
                    route[field] = input.type === 'number' ? 
                        parseInt(input.value) : input.value;
                }
            });
            
            routes.push(route);
        });
        
        return routes;
    }
    
    collectServicesData() {
        const services = [];
        
        // Network services
        if (document.getElementById('dhcp-service').checked) services.push('dhcp');
        if (document.getElementById('dns-service').checked) services.push('dns');
        if (document.getElementById('ntp-service').checked) services.push('ntp');
        if (document.getElementById('snmp-service').checked) services.push('snmp');
        
        // Application services
        if (document.getElementById('web-service').checked) services.push('web');
        if (document.getElementById('ftp-service').checked) services.push('ftp');
        if (document.getElementById('mail-service').checked) services.push('mail');
        if (document.getElementById('database-service').checked) services.push('database');
        
        return services;
    }
    
    saveConfig() {
        if (!this.validateConfig()) {
            alert('Please fix validation errors before saving');
            return;
        }
        
        // Collect form data
        const newConfig = this.collectFormData();
        
        // Update device configuration
        Object.assign(this.currentDevice.config, newConfig);
        this.currentDevice.label = newConfig.hostname;
        this.currentDevice.interfaces = newConfig.interfaces;
        
        // Save to history
        this.configHistory.push({
            timestamp: new Date(),
            config: JSON.parse(JSON.stringify(newConfig))
        });
        
        console.log('💾 Configuration saved for device:', this.currentDevice.id);
        
        // Send to backend API
        this.saveToBackend(newConfig);
        
        // Show success message
        this.showSaveSuccess();
    }
    
    async saveToBackend(config) {
        try {
            const response = await fetch(`/dynamic/api/simulation/${this.getSimulationId()}/device-config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    deviceId: this.currentDevice.id,
                    config: config
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('✅ Config saved to backend:', result);
            
        } catch (error) {
            console.error('❌ Failed to save config to backend:', error);
        }
    }
    
    getSimulationId() {
        // Extract simulation ID from URL or global variable
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }
    
    showSaveSuccess() {
        const toast = document.createElement('div');
        toast.className = 'config-toast success';
        toast.innerHTML = `
            <i class="fas fa-check-circle"></i>
            Configuration saved successfully!
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    applyConfig() {
        this.saveConfig();
        
        // Apply configuration immediately
        if (window.networkSimEngine) {
            window.networkSimEngine.applyDeviceConfiguration(this.currentDevice);
        }
        
        this.closeConfigPanel();
    }
    
    resetConfig() {
        if (confirm('Are you sure you want to reset the configuration? This will restore default values.')) {
            const template = this.configTemplates[this.currentDevice.type];
            if (template) {
                this.currentDevice.config = JSON.parse(JSON.stringify(template));
                this.populateConfigForm(this.currentDevice);
            }
        }
    }
    
    loadTemplate() {
        const template = this.configTemplates[this.currentDevice.type];
        if (template && confirm('Load default template? This will overwrite current configuration.')) {
            this.currentDevice.config = JSON.parse(JSON.stringify(template));
            this.populateConfigForm(this.currentDevice);
        }
    }
    
    setupValidation() {
        this.validationRules = {
            ipAddress: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
            hostname: /^[a-zA-Z0-9-_.]+$/,
            port: /^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$/
        };
    }
    
    loadTemplates() {
        // Templates are already defined in constructor
        console.log('📋 Configuration templates loaded');
    }
}

// Initialize global configurator
window.networkDeviceConfigurator = new NetworkDeviceConfigurator();
console.log('🚀 Network Device Configurator ready');
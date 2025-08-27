/**
 * Enhanced Network Simulation Core Integration
 * Integrates IP configuration, realistic device behavior, and validation with existing topology system
 */

class EnhancedNetworkSimulationCore {
    constructor() {
        this.version = '2.0.0';
        this.features = {
            ipConfiguration: true,
            deviceSpecifications: true,
            networkValidation: true,
            realTimeValidation: true
        };
        
        this.initializeCore();
    }

    initializeCore() {
        // Initialize all components
        this.setupEventIntegration();
        this.enhanceTopologyInterface();
        this.setupFeatureToggle();
        
        console.log('Enhanced Network Simulation Core v2.0.0 initialized');
        console.log('New features:', this.features);
    }

    setupEventIntegration() {
        // Integrate with existing topology events
        this.setupDeviceEvents();
        this.setupConnectionEvents();
        this.setupTopologyEvents();
    }

    setupDeviceEvents() {
        // Enhanced device creation with IP configuration option
        document.addEventListener('deviceAdded', (event) => {
            const device = event.detail;
            this.onDeviceAdded(device);
        });

        // Double-click to configure IP
        document.addEventListener('deviceDoubleClick', (event) => {
            const device = event.detail;
            if (window.ipManager) {
                window.ipManager.openConfigModal(device);
            }
        });

        // Right-click context menu for device actions
        document.addEventListener('deviceRightClick', (event) => {
            const device = event.detail;
            this.showDeviceContextMenu(device, event);
        });
    }

    setupConnectionEvents() {
        // Enhanced connection validation
        document.addEventListener('connectionAdded', (event) => {
            const connection = event.detail;
            this.onConnectionAdded(connection);
        });

        document.addEventListener('connectionRemoved', (event) => {
            const connection = event.detail;
            this.onConnectionRemoved(connection);
        });
    }

    setupTopologyEvents() {
        // Topology change notifications for real-time validation
        document.addEventListener('topologyChanged', (event) => {
            this.onTopologyChanged(event.detail);
        });

        // Enhanced topology save/load with new features
        document.addEventListener('topologySaved', (event) => {
            this.onTopologySaved(event.detail);
        });

        document.addEventListener('topologyLoaded', (event) => {
            this.onTopologyLoaded(event.detail);
        });
    }

    onDeviceAdded(device) {
        // Add device configuration button
        this.addDeviceConfigButton(device);
        
        // Trigger validation if real-time is enabled
        if (window.networkValidator && window.networkValidator.realTimeValidation) {
            window.networkValidator.runQuickValidation();
        }
    }

    onConnectionAdded(connection) {
        // Validate connection compatibility
        this.validateConnectionCompatibility(connection);
        
        // Update network topology view
        this.updateNetworkView();
    }

    onConnectionRemoved(connection) {
        // Check for network isolation
        this.checkNetworkIsolation();
        
        // Update network topology view
        this.updateNetworkView();
    }

    onTopologyChanged(changeData) {
        // Broadcast topology change event
        const event = new CustomEvent('topologyChanged', { 
            detail: changeData 
        });
        window.dispatchEvent(event);
        
        // Update validation if enabled
        if (window.networkValidator && window.networkValidator.realTimeValidation) {
            window.networkValidator.runQuickValidation();
        }
    }

    onTopologySaved(saveData) {
        // Include IP configurations in save data
        if (window.ipManager) {
            saveData.ipConfigurations = window.ipManager.exportConfiguration();
        }
        
        // Include validation results
        if (window.networkValidator && window.networkValidator.validationHistory.length > 0) {
            saveData.lastValidation = window.networkValidator.validationHistory[
                window.networkValidator.validationHistory.length - 1
            ];
        }
    }

    onTopologyLoaded(loadData) {
        // Restore IP configurations
        if (loadData.ipConfigurations && window.ipManager) {
            window.ipManager.importConfiguration(loadData.ipConfigurations);
        }
        
        // Run validation on loaded topology
        if (window.networkValidator) {
            setTimeout(() => {
                window.networkValidator.runCompleteValidation();
            }, 1000);
        }
    }

    enhanceTopologyInterface() {
        this.addFeatureButtons();
        this.addStatusIndicators();
        this.addQuickActions();
    }

    addFeatureButtons() {
        const toolbar = document.querySelector('.topology-toolbar') || 
                       document.querySelector('#canvas').parentElement;
        
        if (toolbar) {
            const featureButtonsHTML = `
            <div class="enhanced-features-toolbar">
                <div class="feature-group">
                    <button id="ipConfigToggle" class="feature-btn" title="IP Configuration">
                        <i class="fas fa-network-wired"></i>
                        <span>IP Config</span>
                    </button>
                    <button id="networkValidation" class="feature-btn" title="Network Validation">
                        <i class="fas fa-check-circle"></i>
                        <span>Validate</span>
                    </button>
                </div>
                
                <div class="feature-group">
                    <button id="quickActions" class="feature-btn dropdown" title="Quick Actions">
                        <i class="fas fa-bolt"></i>
                        <span>Quick Actions</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                </div>
            </div>`;
            
            toolbar.insertAdjacentHTML('beforeend', featureButtonsHTML);
            this.attachFeatureButtonEvents();
        }
    }

    addStatusIndicators() {
        const statusHTML = `
        <div class="network-status-panel">
            <div class="status-group">
                <div class="status-item" id="ipConfigStatus">
                    <i class="fas fa-circle status-dot"></i>
                    <span class="status-label">IP Config</span>
                    <span class="status-value">0/0</span>
                </div>
                <div class="status-item" id="connectivityStatus">
                    <i class="fas fa-circle status-dot"></i>
                    <span class="status-label">Connectivity</span>
                    <span class="status-value">Unknown</span>
                </div>
                <div class="status-item" id="validationStatus">
                    <i class="fas fa-circle status-dot"></i>
                    <span class="status-label">Validation</span>
                    <span class="status-value">Ready</span>
                </div>
            </div>
        </div>`;
        
        const container = document.querySelector('.topology-container') || 
                         document.querySelector('#canvas').parentElement;
        if (container) {
            container.insertAdjacentHTML('afterbegin', statusHTML);
        }
    }

    addQuickActions() {
        const quickActionsHTML = `
    <div id="quickActionsMenu" class="quick-actions-menu" style="display: none;">
            <div class="quick-action" data-action="configureAllIPs">
                <i class="fas fa-magic"></i>
                <span>Auto-Configure IPs</span>
            </div>
            <div class="quick-action" data-action="validateTopology">
                <i class="fas fa-check"></i>
                <span>Quick Validation</span>
            </div>
            <div class="quick-action" data-action="generateReport">
                <i class="fas fa-file-alt"></i>
                <span>Generate Report</span>
            </div>
            <div class="quick-action" data-action="resetNetwork">
                <i class="fas fa-undo"></i>
                <span>Reset Network</span>
            </div>
        </div>`;
        
        document.body.insertAdjacentHTML('beforeend', quickActionsHTML);
    }

    attachFeatureButtonEvents() {
        // IP Configuration toggle
        document.getElementById('ipConfigToggle')?.addEventListener('click', () => {
            this.toggleIPConfigurationPanel();
        });

        // Network Validation
        document.getElementById('networkValidation')?.addEventListener('click', () => {
            this.showValidationPanel();
        });

        // Quick Actions dropdown
        document.getElementById('quickActions')?.addEventListener('click', () => {
            this.toggleQuickActionsMenu();
        });

        // Quick action handlers
        document.addEventListener('click', (e) => {
            if (e.target.closest('.quick-action')) {
                const action = e.target.closest('.quick-action').dataset.action;
                this.executeQuickAction(action);
            }
        });
    }

    addDeviceConfigButton(device) {
        // Add IP configuration button to device
        if (device.element) {
            const configBtn = document.createElement('button');
            configBtn.className = 'device-config-btn';
            configBtn.innerHTML = '<i class="fas fa-cog"></i>';
            configBtn.title = 'Configure IP Address';
            configBtn.onclick = (e) => {
                e.stopPropagation();
                if (window.ipManager) {
                    window.ipManager.openConfigModal(device);
                }
            };
            
            device.element.appendChild(configBtn);
        }
    }

    validateConnectionCompatibility(connection) {
        // Check if connection is compatible
        const sourceDevice = this.findDeviceById(connection.source);
        const targetDevice = this.findDeviceById(connection.target);
        
        if (sourceDevice && targetDevice) {
            const compatibility = this.checkDeviceCompatibility(sourceDevice.type, targetDevice.type);
            
            if (!compatibility.compatible) {
                this.showCompatibilityWarning(connection, compatibility.reason);
            }
        }
    }

    checkDeviceCompatibility(type1, type2) {
        const incompatiblePairs = [
            ['pc', 'pc'], // PCs shouldn't connect directly
            ['server', 'server'] // Servers shouldn't connect directly
        ];
        
        const pairKey = [type1, type2].sort().join('-');
        const isIncompatible = incompatiblePairs.some(pair => 
            pair.sort().join('-') === pairKey
        );
        
        return {
            compatible: !isIncompatible,
            reason: isIncompatible ? `${type1} and ${type2} typically shouldn't connect directly` : ''
        };
    }

    showCompatibilityWarning(connection, reason) {
        // Show warning message
        const warning = document.createElement('div');
        warning.className = 'compatibility-warning';
        warning.innerHTML = `
            <div class="warning-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Connection Warning: ${reason}</span>
                <button onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        document.body.appendChild(warning);
        
        setTimeout(() => {
            if (warning.parentElement) {
                warning.parentElement.removeChild(warning);
            }
        }, 5000);
    }

    updateNetworkView() {
        this.updateStatusIndicators();
        this.updateDeviceLabels();
    }

    updateStatusIndicators() {
        // Update IP configuration status
        const totalDevices = (window.devices || []).length;
        const configuredDevices = window.ipManager ? 
            window.ipManager.networkConfigs.size : 0;
        
        const ipConfigStatus = document.getElementById('ipConfigStatus');
        if (ipConfigStatus) {
            const statusValue = ipConfigStatus.querySelector('.status-value');
            const statusDot = ipConfigStatus.querySelector('.status-dot');
            
            statusValue.textContent = `${configuredDevices}/${totalDevices}`;
            
            if (configuredDevices === 0) {
                statusDot.style.color = '#dc3545'; // Red
            } else if (configuredDevices === totalDevices) {
                statusDot.style.color = '#28a745'; // Green
            } else {
                statusDot.style.color = '#ffc107'; // Yellow
            }
        }
        
        // Update connectivity status
        const connectivityStatus = document.getElementById('connectivityStatus');
        if (connectivityStatus) {
            const statusValue = connectivityStatus.querySelector('.status-value');
            const statusDot = connectivityStatus.querySelector('.status-dot');
            
            const connectivity = this.assessConnectivity();
            statusValue.textContent = connectivity.status;
            statusDot.style.color = connectivity.color;
        }
    }

    assessConnectivity() {
        const devices = window.devices || [];
        const connections = window.connections || [];
        
        if (devices.length === 0) {
            return { status: 'No devices', color: '#6c757d' };
        }
        
        if (connections.length === 0) {
            return { status: 'Isolated', color: '#dc3545' };
        }
        
        // Simple connectivity check
        const connectedDevices = new Set();
        connections.forEach(conn => {
            connectedDevices.add(conn.source);
            connectedDevices.add(conn.target);
        });
        
        const connectedRatio = connectedDevices.size / devices.length;
        
        if (connectedRatio === 1) {
            return { status: 'Full', color: '#28a745' };
        } else if (connectedRatio > 0.5) {
            return { status: 'Partial', color: '#ffc107' };
        } else {
            return { status: 'Limited', color: '#dc3545' };
        }
    }

    updateDeviceLabels() {
        // Update device labels to show IP addresses
        if (window.devices && window.ipManager) {
            window.devices.forEach(device => {
                const config = window.ipManager.networkConfigs.get(device.id);
                if (config && config.ipAddress && device.element) {
                    let ipLabel = device.element.querySelector('.ip-address-label');
                    
                    if (!ipLabel) {
                        ipLabel = document.createElement('div');
                        ipLabel.className = 'ip-address-label';
                        device.element.appendChild(ipLabel);
                    }
                    
                    ipLabel.textContent = config.ipAddress;
                    ipLabel.style.cssText = `
                        position: absolute;
                        bottom: -20px;
                        left: 50%;
                        transform: translateX(-50%);
                        background: rgba(0, 0, 0, 0.8);
                        color: #00d4ff;
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-size: 12px;
                        font-family: monospace;
                        white-space: nowrap;
                    `;
                }
            });
        }
    }

    checkNetworkIsolation() {
        // Check for isolated devices after connection removal
        const isolatedDevices = this.findIsolatedDevices();
        
        if (isolatedDevices.length > 0) {
            this.showIsolationWarning(isolatedDevices);
        }
    }

    findIsolatedDevices() {
        const devices = window.devices || [];
        const connections = window.connections || [];
        
        return devices.filter(device => {
            return !connections.some(conn => 
                conn.source === device.id || conn.target === device.id
            );
        });
    }

    showIsolationWarning(isolatedDevices) {
        const deviceNames = isolatedDevices.map(d => d.label || d.id).join(', ');
        
        const warning = document.createElement('div');
        warning.className = 'isolation-warning';
        warning.innerHTML = `
            <div class="warning-content">
                <i class="fas fa-exclamation-circle"></i>
                <span>Warning: ${deviceNames} ${isolatedDevices.length === 1 ? 'is' : 'are'} now isolated</span>
                <button onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        document.body.appendChild(warning);
        
        setTimeout(() => {
            if (warning.parentElement) {
                warning.parentElement.removeChild(warning);
            }
        }, 5000);
    }

    // Feature Panel Toggles

    toggleIPConfigurationPanel() {
        const panel = document.getElementById('ipConfigurationPanel');
        if (panel) {
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }
    }

    // PKT integration removed

    showValidationPanel() {
        const panel = document.getElementById('networkValidationPanel');
        if (panel) {
            panel.scrollIntoView({ behavior: 'smooth' });
            
            // Run validation if not already done
            if (window.networkValidator && window.networkValidator.validationHistory.length === 0) {
                window.networkValidator.runCompleteValidation();
            }
        }
    }

    toggleQuickActionsMenu() {
        const menu = document.getElementById('quickActionsMenu');
        if (menu) {
            const isVisible = menu.style.display === 'block';
            menu.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                // Position menu
                const btn = document.getElementById('quickActions');
                const rect = btn.getBoundingClientRect();
                menu.style.cssText += `
                    position: fixed;
                    top: ${rect.bottom + 5}px;
                    left: ${rect.left}px;
                `;
            }
        }
    }

    executeQuickAction(action) {
        document.getElementById('quickActionsMenu').style.display = 'none';
        
        switch (action) {
            case 'configureAllIPs':
                this.autoConfigureAllIPs();
                break;
            case 'validateTopology':
                if (window.networkValidator) {
                    window.networkValidator.runCompleteValidation();
                }
                break;
            case 'generateReport':
                this.generateNetworkReport();
                break;
            case 'resetNetwork':
                this.resetNetwork();
                break;
        }
    }

    autoConfigureAllIPs() {
        if (!window.ipManager || !window.devices) return;
        
        const devices = window.devices.filter(d => d.type !== 'hub');
        if (devices.length === 0) return;
        
        // Auto-assign IP addresses in 192.168.1.0/24 network
        const baseNetwork = '192.168.1';
        const subnetMask = '255.255.255.0';
        const gateway = '192.168.1.1';
        
        devices.forEach((device, index) => {
            const ipAddress = `${baseNetwork}.${index + 1}`;
            
            const config = {
                ipAddress: ipAddress,
                subnetMask: subnetMask,
                gateway: device.type === 'router' ? '' : gateway,
                dns: '8.8.8.8'
            };
            
            window.ipManager.networkConfigs.set(device.id, config);
            window.ipManager.updateDeviceDisplay(device, config);
        });
        
        this.updateNetworkView();
        
        // Show success message
        this.showSuccessMessage(`Auto-configured IP addresses for ${devices.length} devices`);
    }

    generateNetworkReport() {
        const report = {
            metadata: {
                timestamp: new Date().toISOString(),
                topology: {
                    devices: (window.devices || []).length,
                    connections: (window.connections || []).length
                }
            },
            ip_configurations: window.ipManager ? window.ipManager.exportConfiguration() : {},
            validation_results: window.networkValidator && window.networkValidator.validationHistory.length > 0 ?
                window.networkValidator.validationHistory[window.networkValidator.validationHistory.length - 1] : null,
            recommendations: this.generateRecommendations()
        };
        
        // Export report as JSON
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `network_report_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showSuccessMessage('Network report exported successfully');
    }

    generateRecommendations() {
        const recommendations = [];
        
        // Check device count
        const deviceCount = (window.devices || []).length;
        if (deviceCount === 0) {
            recommendations.push('Add network devices to begin building your topology');
        } else if (deviceCount === 1) {
            recommendations.push('Add more devices and connections to create a functional network');
        }
        
        // Check connections
        const connectionCount = (window.connections || []).length;
        if (connectionCount === 0 && deviceCount > 1) {
            recommendations.push('Connect your devices to enable network communication');
        }
        
        // Check IP configuration
        const configuredCount = window.ipManager ? window.ipManager.networkConfigs.size : 0;
        if (configuredCount === 0 && deviceCount > 0) {
            recommendations.push('Configure IP addresses for your devices');
        } else if (configuredCount < deviceCount) {
            recommendations.push('Complete IP configuration for remaining devices');
        }
        
        return recommendations;
    }

    resetNetwork() {
        if (confirm('Are you sure you want to reset the entire network? This action cannot be undone.')) {
            // Clear devices and connections
            if (window.devices) window.devices.length = 0;
            if (window.connections) window.connections.length = 0;
            
            // Clear IP configurations
            if (window.ipManager) window.ipManager.networkConfigs.clear();
            
            // Clear validation history
            if (window.networkValidator) window.networkValidator.validationHistory.length = 0;
            
            // Update displays
            this.updateNetworkView();
            
            // Clear canvas
            const canvas = document.querySelector('#canvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
            
            this.showSuccessMessage('Network reset successfully');
        }
    }

    showSuccessMessage(message) {
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.parentElement.removeChild(notification);
                    }
                }, 300);
            }
        }, 3000);
    }

    setupFeatureToggle() {
        // Add CSS animations
        const animationStyles = `
        <style>
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        .enhanced-features-toolbar {
            display: flex;
            gap: 20px;
            padding: 15px;
            background: #2a2a2a;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .feature-group {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .feature-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 15px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .feature-btn:hover {
            background: #0056b3;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        
        .network-status-panel {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .status-group {
            display: flex;
            gap: 30px;
            justify-content: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #ccc;
        }
        
        .status-dot {
            font-size: 8px;
        }
        
        .status-label {
            font-weight: 500;
        }
        
        .status-value {
            font-family: monospace;
            font-weight: bold;
        }
        
        .device-config-btn {
            position: absolute;
            top: -5px;
            right: -5px;
            width: 20px;
            height: 20px;
            background: #007bff;
            border: none;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            font-size: 10px;
            display: none;
        }
        
        .device:hover .device-config-btn {
            display: block;
        }
        
        .compatibility-warning,
        .isolation-warning {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #dc3545;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }
        
        .warning-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .warning-content button {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
            margin-left: 10px;
        }
        
        .quick-actions-menu {
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 5px;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .quick-action {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 15px;
            color: #ccc;
            cursor: pointer;
            border-radius: 4px;
            transition: background 0.2s ease;
        }
        
        .quick-action:hover {
            background: #3a3a3a;
            color: white;
        }
        
    /* PKT integration fully removed */
        </style>`;
        
        document.head.insertAdjacentHTML('beforeend', animationStyles);
    }

    findDeviceById(id) {
        return (window.devices || []).find(device => device.id === id);
    }
}

// Initialize Enhanced Network Simulation Core
document.addEventListener('DOMContentLoaded', () => {
    // Wait for other components to initialize
    setTimeout(() => {
        window.enhancedNetworkCore = new EnhancedNetworkSimulationCore();
    }, 1000);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedNetworkSimulationCore;
}
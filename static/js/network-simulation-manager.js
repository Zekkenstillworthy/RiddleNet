/**
 * Network Simulation Main Initializer
 * Coordinates initialization of all network simulation components
 */

class NetworkSimulationManager {
    constructor() {
        this.components = {};
        this.isInitialized = false;
        this.initializationOrder = [
            'ipManager',
            'networkValidator',
            'enhancedCore'
        ];
        
        this.initializeSimulation();
    }

    async initializeSimulation() {
        console.log('🚀 Starting Network Simulation System...');
        
        try {
            // Initialize components in order
            await this.initializeIPManager();
            await this.initializeNetworkValidator();
            await this.initializeEnhancedCore();
            
            // Setup global event handlers
            this.setupGlobalEvents();
            
            // Setup auto-save
            this.setupAutoSave();
            
            // Mark as initialized
            this.isInitialized = true;
            
            console.log('✅ Network Simulation System initialized successfully');
            this.showInitializationComplete();
            
        } catch (error) {
            console.error('❌ Network Simulation initialization failed:', error);
            this.showInitializationError(error);
        }
    }

    async initializeIPManager() {
        if (typeof IPConfigurationManager !== 'undefined') {
            this.components.ipManager = new IPConfigurationManager();
            window.ipManager = this.components.ipManager;
            console.log('✓ IP Configuration Manager initialized');
        } else {
            console.warn('⚠️ IP Configuration Manager not found');
        }
    }

    // PKT integration removed

    async initializeNetworkValidator() {
        if (typeof NetworkConfigurationValidator !== 'undefined') {
            this.components.networkValidator = new NetworkConfigurationValidator();
            window.networkValidator = this.components.networkValidator;
            console.log('✓ Network Configuration Validator initialized');
        } else {
            console.warn('⚠️ Network Configuration Validator not found');
        }
    }

    async initializeEnhancedCore() {
        if (typeof EnhancedNetworkSimulationCore !== 'undefined') {
            this.components.enhancedCore = new EnhancedNetworkSimulationCore();
            window.enhancedNetworkCore = this.components.enhancedCore;
            console.log('✓ Enhanced Network Simulation Core initialized');
        } else {
            console.warn('⚠️ Enhanced Network Simulation Core not found');
        }
    }

    setupGlobalEvents() {
        // Setup global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key.toLowerCase()) {
                    case 'i':
                        e.preventDefault();
                        this.openIPConfiguration();
                        break;
                    case 'v':
                        e.preventDefault();
                        this.runValidation();
                        break;
                    case 's':
                        e.preventDefault();
                        this.saveTopology();
                        break;
                    case 'o':
                        e.preventDefault();
                        this.loadTopology();
                        break;
                }
            }
        });

        // Setup global click handlers for topology
        document.addEventListener('click', (e) => {
            // Close open menus when clicking outside
            this.closeOpenMenus(e);
        });

        // Setup window resize handler
        window.addEventListener('resize', () => {
            this.handleWindowResize();
        });

        // Setup beforeunload handler for unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }

    setupAutoSave() {
        // Auto-save every 5 minutes
        setInterval(() => {
            this.autoSave();
        }, 5 * 60 * 1000); // 5 minutes

        // Save on topology changes
        document.addEventListener('topologyChanged', () => {
            clearTimeout(this.autoSaveTimeout);
            this.autoSaveTimeout = setTimeout(() => {
                this.autoSave();
            }, 30000); // 30 seconds after last change
        });
    }

    // Global Action Handlers

    openIPConfiguration() {
        if (this.components.ipManager) {
            const selectedDevice = this.getSelectedDevice();
            if (selectedDevice) {
                this.components.ipManager.openConfigModal(selectedDevice);
            } else {
                this.components.ipManager.openDeviceSelectionModal();
            }
        }
    }

    // PKT menu removed

    runValidation() {
        if (this.components.networkValidator) {
            this.components.networkValidator.runCompleteValidation();
        }
    }

    saveTopology() {
        const topologyData = this.exportTopologyData();
        
        // Save to localStorage
        localStorage.setItem('network_topology_autosave', JSON.stringify(topologyData));
        
        // Show save notification
        this.showNotification('Topology saved', 'success');
    }

    loadTopology() {
        const savedData = localStorage.getItem('network_topology_autosave');
        if (savedData) {
            try {
                const topologyData = JSON.parse(savedData);
                this.importTopologyData(topologyData);
                this.showNotification('Topology loaded', 'success');
            } catch (error) {
                console.error('Error loading topology:', error);
                this.showNotification('Error loading topology', 'error');
            }
        } else {
            this.showNotification('No saved topology found', 'warning');
        }
    }

    autoSave() {
        if (this.hasUnsavedChanges()) {
            this.saveTopology();
            console.log('🔄 Auto-saved topology');
        }
    }

    // Utility Methods

    getSelectedDevice() {
        // Return currently selected device if any
        const selectedElements = document.querySelectorAll('.device.selected');
        if (selectedElements.length > 0) {
            const deviceElement = selectedElements[0];
            return this.findDeviceByElement(deviceElement);
        }
        return null;
    }

    findDeviceByElement(element) {
        const deviceId = element.dataset.deviceId || element.id;
        return (window.devices || []).find(device => device.id === deviceId);
    }

    closeOpenMenus(e) {
        // Close quick actions menu
        const quickActionsMenu = document.getElementById('quickActionsMenu');
        if (quickActionsMenu && !e.target.closest('#quickActions') && !e.target.closest('#quickActionsMenu')) {
            quickActionsMenu.style.display = 'none';
        }

    // PKT quick menus removed
    }

    handleWindowResize() {
        // Reposition floating panels and menus
        const canvas = document.querySelector('#canvas');
        if (canvas) {
            // Update canvas size if needed
            this.updateCanvasSize();
        }

        // Update modal positions
        this.updateModalPositions();
    }

    updateCanvasSize() {
        const canvas = document.querySelector('#canvas');
        if (canvas) {
            const container = canvas.parentElement;
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            
            // Redraw topology
            this.redrawTopology();
        }
    }

    updateModalPositions() {
        // Center any open modals
        const modals = document.querySelectorAll('.modal:not([style*="display: none"])');
        modals.forEach(modal => {
            modal.style.left = '50%';
            modal.style.top = '50%';
            modal.style.transform = 'translate(-50%, -50%)';
        });
    }

    redrawTopology() {
        // Redraw all devices and connections
        if (window.devices && window.connections) {
            // Trigger redraw event
            const event = new CustomEvent('topologyRedraw', {
                detail: {
                    devices: window.devices,
                    connections: window.connections
                }
            });
            document.dispatchEvent(event);
        }
    }

    hasUnsavedChanges() {
        // Check if there are unsaved changes
        const currentData = this.exportTopologyData();
        const savedData = localStorage.getItem('network_topology_autosave');
        
        if (!savedData) return true;
        
        try {
            const parsedSaved = JSON.parse(savedData);
            return JSON.stringify(currentData) !== JSON.stringify(parsedSaved);
        } catch {
            return true;
        }
    }

    exportTopologyData() {
        const data = {
            timestamp: new Date().toISOString(),
            version: '2.0.0',
            devices: window.devices || [],
            connections: window.connections || [],
            ipConfigurations: this.components.ipManager ? 
                this.components.ipManager.exportConfiguration() : {},
            validationHistory: this.components.networkValidator ? 
                this.components.networkValidator.validationHistory : [],
            metadata: {
                deviceCount: (window.devices || []).length,
                connectionCount: (window.connections || []).length,
                configuredDevices: this.components.ipManager ? 
                    this.components.ipManager.networkConfigs.size : 0
            }
        };
        
        return data;
    }

    importTopologyData(data) {
        try {
            // Clear current topology
            if (window.devices) window.devices.length = 0;
            if (window.connections) window.connections.length = 0;
            
            // Import devices
            if (data.devices) {
                window.devices = window.devices || [];
                window.devices.push(...data.devices);
            }
            
            // Import connections
            if (data.connections) {
                window.connections = window.connections || [];
                window.connections.push(...data.connections);
            }
            
            // Import IP configurations
            if (data.ipConfigurations && this.components.ipManager) {
                this.components.ipManager.importConfiguration(data.ipConfigurations);
            }
            
            // Import validation history
            if (data.validationHistory && this.components.networkValidator) {
                this.components.networkValidator.validationHistory = data.validationHistory;
            }
            
            // Trigger topology loaded event
            const event = new CustomEvent('topologyLoaded', { detail: data });
            document.dispatchEvent(event);
            
            // Redraw topology
            this.redrawTopology();
            
        } catch (error) {
            console.error('Error importing topology data:', error);
            throw error;
        }
    }

    showInitializationComplete() {
        const notification = document.createElement('div');
        notification.className = 'initialization-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-check-circle"></i>
                <div class="notification-text">
                    <strong>Network Simulation Ready!</strong>
                    <div class="notification-details">
                        All components loaded successfully. Press Ctrl+I for IP config, Ctrl+V for validation.
                    </div>
                </div>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            max-width: 350px;
            animation: slideInRight 0.5s ease;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            .notification-content {
                display: flex;
                align-items: flex-start;
                gap: 15px;
            }
            
            .notification-content i {
                font-size: 24px;
                margin-top: 2px;
            }
            
            .notification-text strong {
                display: block;
                font-size: 16px;
                margin-bottom: 5px;
            }
            
            .notification-details {
                font-size: 13px;
                opacity: 0.9;
                line-height: 1.3;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.5s ease';
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.parentElement.removeChild(notification);
                    }
                }, 500);
            }
        }, 8000);
    }

    showInitializationError(error) {
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-exclamation-triangle"></i>
                <div class="notification-text">
                    <strong>Initialization Error</strong>
                    <div class="notification-details">
                        ${error.message || 'Failed to initialize network simulation components'}
                    </div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            max-width: 350px;
            animation: slideInRight 0.5s ease;
        `;
        
        document.body.appendChild(notification);
    }

    showNotification(message, type = 'info') {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#007bff'
        };
        
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        const notification = document.createElement('div');
        notification.className = `${type}-notification`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${icons[type]}"></i>
                <span>${message}</span>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: ${colors[type]};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.parentElement.removeChild(notification);
                    }
                }, 300);
            }
        }, 3000);
    }

    // Public API for external use
    getStatus() {
        return {
            initialized: this.isInitialized,
            components: Object.keys(this.components),
            deviceCount: (window.devices || []).length,
            connectionCount: (window.connections || []).length,
            configuredDevices: this.components.ipManager ? 
                this.components.ipManager.networkConfigs.size : 0
        };
    }

    exportNetworkData() {
        return this.exportTopologyData();
    }

    importNetworkData(data) {
        return this.importTopologyData(data);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for all scripts to load
    setTimeout(() => {
        window.networkSimulationManager = new NetworkSimulationManager();
    }, 500);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NetworkSimulationManager;
}
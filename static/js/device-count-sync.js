/**
 * Device Count Synchronization Script
 * Ensures consistent device counts between Admin Edit and Dynamic Simulation pages
 */

class DeviceCountSynchronizer {
    constructor(simulationId) {
        this.simulationId = simulationId;
        this.isAdminPage = window.location.pathname.includes('/admin/simulation/edit');
        this.isDynamicPage = window.location.pathname.includes('/dynamic/simulation');
        this.syncEnabled = true;
        this.lastKnownCount = 0;
        
        this.init();
    }
    
    init() {
        console.log(`🔄 Device Count Synchronizer initialized for simulation ${this.simulationId}`);
        console.log(`📍 Page type: ${this.isAdminPage ? 'Admin Edit' : this.isDynamicPage ? 'Dynamic Simulation' : 'Unknown'}`);
        
        if (this.isAdminPage) {
            this.initAdminSync();
        } else if (this.isDynamicPage) {
            this.initDynamicSync();
        }
        
        // Set up periodic consistency checks
        this.startConsistencyMonitoring();
    }
    
    initAdminSync() {
        console.log('📊 [ADMIN] Initializing device count sync for admin edit page');
        
        // Get the current canonical device count and update UI
        this.fetchCanonicalDeviceCount().then(result => {
            if (result.success) {
                console.log(`📊 [ADMIN] Canonical device count: ${result.canonical_device_count}`);
                this.updateAdminDeviceCountDisplay(result.canonical_device_count);
                this.lastKnownCount = result.canonical_device_count;
            }
        });
        
        // Set up real-time sync listener
        this.setupAdminSyncListener();
    }
    
    initDynamicSync() {
        console.log('🎮 [DYNAMIC] Initializing device count sync for dynamic simulation page');
        
        // Monitor device count changes in dynamic simulation
        this.monitorDynamicDeviceChanges();
        
        // Send initial device count to admin if there are devices
        this.sendDeviceCountToAdmin();
    }
    
    async fetchCanonicalDeviceCount() {
        try {
            const response = await fetch(`/admin/api/device-sync/simulation/${this.simulationId}/canonical-count`);
            return await response.json();
        } catch (error) {
            console.error('❌ Error fetching canonical device count:', error);
            return { success: false, error: error.message };
        }
    }
    
    async syncDeviceCountToAdmin(deviceCount, devices = null) {
        if (!this.syncEnabled) return;
        
        try {
            const syncData = {
                device_count: deviceCount,
                source_page: this.isDynamicPage ? 'dynamic_simulation' : 'admin_edit',
                devices: devices
            };
            
            const response = await fetch(`/admin/api/device-sync/simulation/${this.simulationId}/sync-devices`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(syncData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log(`✅ Device count synced successfully: ${deviceCount} devices`);
                this.lastKnownCount = deviceCount;
                
                // Emit custom event for other scripts to listen to
                window.dispatchEvent(new CustomEvent('deviceCountSynced', {
                    detail: { simulationId: this.simulationId, deviceCount: deviceCount }
                }));
            } else {
                console.error('❌ Device count sync failed:', result.error);
            }
            
            return result;
        } catch (error) {
            console.error('❌ Error syncing device count:', error);
            return { success: false, error: error.message };
        }
    }
    
    updateAdminDeviceCountDisplay(deviceCount) {
        // Update various UI elements that show device count in admin page
        const deviceCountElements = [
            '.device-count-display',
            '[data-device-count]',
            '.simulation-device-count',
            '#deviceCountLabel'
        ];
        
        deviceCountElements.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (element) {
                    if (element.tagName === 'INPUT') {
                        element.value = deviceCount;
                    } else {
                        element.textContent = `${deviceCount} devices`;
                    }
                    element.setAttribute('data-synced-count', deviceCount);
                    console.log(`📊 [ADMIN] Updated ${selector} with device count: ${deviceCount}`);
                }
            });
        });
        
        // Update metadata display
        this.updateDeviceCountMetadata(deviceCount, 'synced_from_dynamic');
    }
    
    updateDeviceCountMetadata(count, source) {
        const timestamp = new Date().toLocaleString();
        const metadataElement = document.querySelector('.device-sync-metadata');
        
        if (metadataElement) {
            metadataElement.innerHTML = `
                <small class="text-muted">
                    Device count: <strong>${count}</strong> | 
                    Source: ${source} | 
                    Last sync: ${timestamp}
                </small>
            `;
        }
    }
    
    monitorDynamicDeviceChanges() {
        // Hook into existing dynamic simulation device management
        const originalAddDevice = window.addNetworkDevice || function() {};
        const originalRemoveDevice = window.removeNetworkDevice || function() {};
        
        window.addNetworkDevice = (...args) => {
            const result = originalAddDevice.apply(this, args);
            this.onDynamicDeviceCountChange();
            return result;
        };
        
        window.removeNetworkDevice = (...args) => {
            const result = originalRemoveDevice.apply(this, args);
            this.onDynamicDeviceCountChange();
            return result;
        };
        
        // Also monitor localStorage changes for device restoration
        window.addEventListener('storage', (e) => {
            if (e.key && e.key.includes('topology') || e.key.includes('device')) {
                this.onDynamicDeviceCountChange();
            }
        });
        
        // Monitor custom device change events
        window.addEventListener('networkDeviceAdded', () => this.onDynamicDeviceCountChange());
        window.addEventListener('networkDeviceRemoved', () => this.onDynamicDeviceCountChange());
        window.addEventListener('topologyLoaded', () => this.onDynamicDeviceCountChange());
        
        console.log('🎮 [DYNAMIC] Device change monitoring active');
    }
    
    onDynamicDeviceCountChange() {
        // Debounce rapid changes
        clearTimeout(this.deviceChangeTimeout);
        this.deviceChangeTimeout = setTimeout(() => {
            this.sendDeviceCountToAdmin();
        }, 1000);
    }
    
    sendDeviceCountToAdmin() {
        // Get current device count from various sources in dynamic simulation
        let deviceCount = 0;
        let devices = null;
        
        // Try to get from global simulation state
        if (window.simulationState && window.simulationState.networkDevices) {
            deviceCount = window.simulationState.networkDevices.length;
            devices = window.simulationState.networkDevices;
        }
        // Try to get from canvas or other sources
        else if (window.networkDevices) {
            deviceCount = window.networkDevices.length;
            devices = window.networkDevices;
        }
        // Try to get from simulation engine
        else if (window.networkSimulationEngine && window.networkSimulationEngine.getDeviceCount) {
            deviceCount = window.networkSimulationEngine.getDeviceCount();
        }
        
        if (deviceCount > 0 && deviceCount !== this.lastKnownCount) {
            console.log(`🎮 [DYNAMIC] Device count changed: ${this.lastKnownCount} → ${deviceCount}`);
            this.syncDeviceCountToAdmin(deviceCount, devices);
        }
    }
    
    setupAdminSyncListener() {
        // Listen for device count updates from other tabs/windows
        window.addEventListener('deviceCountSynced', (event) => {
            if (event.detail.simulationId === this.simulationId) {
                console.log(`📊 [ADMIN] Received device count sync: ${event.detail.deviceCount}`);
                this.updateAdminDeviceCountDisplay(event.detail.deviceCount);
            }
        });
        
        // Listen for WebSocket updates (if available)
        if (window.socket) {
            window.socket.on('admin_simulation_updated', (data) => {
                if (data.simulation_id === this.simulationId && data.device_count) {
                    console.log(`📊 [ADMIN] WebSocket device count update: ${data.device_count}`);
                    this.updateAdminDeviceCountDisplay(data.device_count);
                }
            });
        }
    }
    
    async checkConsistency() {
        try {
            const response = await fetch(`/admin/api/device-sync/simulation/${this.simulationId}/device-consistency-check`);
            const result = await response.json();
            
            if (result.success) {
                console.log(`🔍 [CONSISTENCY] Check result:`, result.consistency_check);
                
                if (!result.consistency_check.is_consistent) {
                    console.warn(`⚠️ [CONSISTENCY] Device count inconsistency detected:`, result.consistency_check);
                    
                    // Auto-fix inconsistency if enabled
                    if (this.syncEnabled) {
                        const canonicalCount = result.consistency_check.canonical_count;
                        if (this.isAdminPage) {
                            this.updateAdminDeviceCountDisplay(canonicalCount);
                        }
                    }
                }
                
                return result;
            }
        } catch (error) {
            console.error('❌ Error checking device consistency:', error);
        }
        
        return null;
    }
    
    startConsistencyMonitoring() {
        // Check consistency every 30 seconds
        this.consistencyInterval = setInterval(() => {
            this.checkConsistency();
        }, 30000);
        
        console.log('🕒 [MONITOR] Consistency monitoring started (30s intervals)');
    }
    
    destroy() {
        if (this.consistencyInterval) {
            clearInterval(this.consistencyInterval);
        }
        if (this.deviceChangeTimeout) {
            clearTimeout(this.deviceChangeTimeout);
        }
        
        console.log('🔄 Device Count Synchronizer destroyed');
    }
}

// Auto-initialize if simulation ID is available
(function() {
    // Try to get simulation ID from various sources
    let simulationId = null;
    
    // From URL path
    const pathMatch = window.location.pathname.match(/simulation\/(?:edit\/)?(\d+)/);
    if (pathMatch) {
        simulationId = parseInt(pathMatch[1]);
    }
    
    // From page data attributes
    if (!simulationId) {
        const dataElement = document.querySelector('[data-simulation-id]');
        if (dataElement) {
            simulationId = parseInt(dataElement.getAttribute('data-simulation-id'));
        }
    }
    
    // From global variables
    if (!simulationId && typeof window.currentSimulationId !== 'undefined') {
        simulationId = parseInt(window.currentSimulationId);
    }
    
    if (simulationId) {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                window.deviceCountSync = new DeviceCountSynchronizer(simulationId);
            });
        } else {
            window.deviceCountSync = new DeviceCountSynchronizer(simulationId);
        }
    } else {
        console.log('⚠️ Could not determine simulation ID for device count synchronization');
    }
})();
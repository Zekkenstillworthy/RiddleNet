
/**
 * Integration Bridge for Network Simulation Engine
 * Connects the new comprehensive network simulation engine with existing dynamic simulation
 */

class SimulationEngineIntegration {
    constructor() {
        this.isEngineReady = false;
        this.existingSimulation = null;
        this.engineInstance = null;
        
        this.init();
    }
    
    init() {
        // Wait for DOM and existing simulation to be ready
        document.addEventListener('DOMContentLoaded', () => {
            this.waitForComponents();
        });
        
        console.log('🔗 Simulation Engine Integration initialized');
    }
    
    async waitForComponents() {
        // Wait for existing simulation
        let attempts = 0;
        const maxAttempts = 50;
        
        const waitForSim = () => {
            if (window.simulation || attempts >= maxAttempts) {
                this.existingSimulation = window.simulation;
                this.initializeEngine();
                return;
            }
            attempts++;
            setTimeout(waitForSim, 100);
        };
        
        waitForSim();
    }
    
    initializeEngine() {
        // Check if canvas exists - try multiple canvas selectors
        const canvasSelectors = ['#Canvas', '#network-canvas', '#simulation-canvas', '#networkCanvas'];
        let canvas = null;
        
        for (const selector of canvasSelectors) {
            const element = document.querySelector(selector);
            if (element && element.tagName && element.tagName.toLowerCase() === 'canvas') {
                canvas = element;
                console.log(`✅ Found canvas: ${selector}`);
                break;
            }
        }
        
        if (!canvas) {
            console.warn('⚠️ Network canvas not found, engine initialization skipped');
            return;
        }
        
        // If the legacy SimulationEngine is already running on the found canvas (common id: 'Canvas'),
        // create a dedicated canvas for the NetworkSimulationEngine to prevent double rendering / stacked drawings.
        // This fixes the "double canvas of devices when holding click" issue caused by two engines sharing one <canvas>.
        if (canvas && canvas.id === 'Canvas') {
            // Only create a new canvas if we don't already have one
            let existingNew = document.getElementById('network-canvas');
            if (!existingNew) {
                const newCanvas = document.createElement('canvas');
                newCanvas.id = 'network-canvas';
                if (canvas.width) newCanvas.width = canvas.width;
                if (canvas.height) newCanvas.height = canvas.height;
                // Ensure the new canvas carries the common styling class
                const existingClass = canvas.className ? canvas.className + ' ' : '';
                newCanvas.className = `${existingClass}network-engine-canvas network-sim-canvas`.trim();
                canvas.parentElement.insertBefore(newCanvas, canvas.nextSibling);
                console.log('🧹 Created dedicated network canvas and removing legacy canvas');
                // Remove the legacy canvas entirely
                try {
                    canvas.remove();
                } catch (remErr) {
                    console.warn('⚠️ Could not remove legacy canvas cleanly:', remErr);
                    canvas.style.display = 'none';
                }
            }
            canvas = document.getElementById('network-canvas');
        }

        // Initialize the comprehensive network engine
        try {
            // Find the canvas and get its ID
            // Ensure the active canvas has the shared styling class
            try { canvas.classList.add('network-sim-canvas'); } catch(_) {}
            let canvasId = canvas.id;
            if (!canvasId) {
                // Generate a temporary ID if none exists
                canvasId = 'network-canvas-temp';
                canvas.id = canvasId;
            }
            
            this.engineInstance = new NetworkSimulationEngine(canvasId);

            // Attempt to gracefully stop legacy SimulationEngine if present to reduce event noise
            if (window.simulationEngine && typeof window.simulationEngine.destroy === 'function') {
                try {
                    window.simulationEngine.destroy();
                    console.log('🛑 Legacy SimulationEngine destroyed after network engine init');
                } catch (e) {
                    console.warn('⚠️ Failed to fully destroy legacy SimulationEngine (non-fatal):', e);
                }
            }
            
            // Connect with existing simulation data if available
            if (this.existingSimulation) {
                this.bridgeExistingData();
            }
            
            // Override existing device configuration methods
            this.overrideConfigurationMethods();
            
            // Set up event bridges
            this.setupEventBridges();
            
            this.isEngineReady = true;
            
            console.log('✅ Network Simulation Engine integrated successfully');
            
            // Trigger integration complete event
            this.dispatchIntegrationEvent();

            // --- Robust double-click configuration fallback wrapper ---
            try {
                const engine = this.engineInstance;
                if (engine && typeof engine.openDeviceConfig === 'function' && !engine.__configWrapperApplied) {
                    const originalOpenDeviceConfig = engine.openDeviceConfig.bind(engine);
                    engine.openDeviceConfig = function(device) {
                        let primaryError = null;
                        try {
                            originalOpenDeviceConfig(device);
                        } catch (err) {
                            primaryError = err;
                            console.warn('⚠️ Primary openDeviceConfig threw - will attempt fallbacks:', err);
                        }
                        // If modal already visible, skip fallback
                        const existingModal = document.getElementById('device-config-modal');
                        const visible = existingModal && (existingModal.style.display === 'flex' || existingModal.classList.contains('active'));
                        if (visible) return; // already opened successfully
                        if (!device) return;
                        // Infrastructure types should prefer the network (admin) configurator UI for richer interface settings
                        const infraTypes = new Set(['router','switch','firewall','access-point','load-balancer','gateway','bridge','hub']);
                        if (infraTypes.has(device.type) && window.networkDeviceConfigurator?.openConfigPanel) {
                            try {
                                window.networkDeviceConfigurator.openConfigPanel(device);
                                return;
                            } catch (e) {
                                console.warn('⚠️ Infra preferred networkDeviceConfigurator failed, continuing:', e);
                            }
                        }
                        // Preferred student configurator
                        if (window.userDeviceConfigurator?.openDeviceConfiguration) {
                            try {
                                window.userDeviceConfigurator.openDeviceConfiguration(device);
                                return;
                            } catch (e) {
                                console.warn('⚠️ Student configurator fallback failed:', e);
                            }
                        }
                        // Network (admin) configurator fallback
                        if (window.networkDeviceConfigurator?.openConfigPanel) {
                            try { window.networkDeviceConfigurator.openConfigPanel(device); return; } catch (e) { console.warn('⚠️ NetworkDeviceConfigurator fallback failed:', e); }
                        }
                        // Built-in minimal modal if exposed
                        if (typeof engine.showDeviceConfigModal === 'function') {
                            try { engine.showDeviceConfigModal(device); return; } catch (e) { console.warn('⚠️ Built-in modal fallback failed:', e); }
                        }
                        if (primaryError) {
                            console.error('❌ All configuration popup strategies failed.', primaryError);
                        } else {
                            console.error('❌ Unable to open configuration popup; no strategies succeeded.');
                        }
                    };
                    engine.__configWrapperApplied = true;
                    console.log('🛡️ Applied robust configuration popup fallback wrapper');
                }
            } catch (wrapErr) {
                console.warn('⚠️ Failed to apply configuration fallback wrapper (non-fatal):', wrapErr);
            }

            // MVP Camera Controller (hold + sway + drag + inertia)
            this.setupMVPCameraController(canvas);
            
            // After engine init, monitor for DynamicSimulation instance replacement
            // Some pages set window.simulation to JSON first, then later replace with a class instance.
            // We adopt the instance when it appears and bridge its in-memory devices.
            this.monitorDynamicSimulationInstance();
            
        } catch (error) {
            console.error('❌ Failed to initialize network simulation engine:', error);
        }
    }

    monitorDynamicSimulationInstance() {
        if (this._monitoringSimInstance) return;
        this._monitoringSimInstance = true;
        let checks = 0;
        const maxChecks = 60; // ~6s at 100ms
        const timer = setInterval(() => {
            checks++;
            const sim = window.simulation;
            const looksLikeInstance = sim && (Array.isArray(sim.networkDevices) || typeof sim.addNetworkDevice === 'function');
            if (looksLikeInstance && sim !== this.existingSimulation) {
                console.log('🔁 Detected DynamicSimulation instance, adopting for integration');
                this.existingSimulation = sim;
                try { this.bridgeExistingData(); } catch (e) { console.warn('⚠️ Re-bridge from instance failed:', e); }
                try { this.overrideConfigurationMethods(); } catch (e) { console.warn('⚠️ Re-override config methods failed:', e); }
                clearInterval(timer);
            } else if (checks >= maxChecks) {
                clearInterval(timer);
            }
        }, 100);
    }

    // ================= MVP CAMERA CONTROLLER =================
    setupMVPCameraController(canvas) {
        if (!canvas || !this.engineInstance || this._mvpCameraReady) return;

        const engine = this.engineInstance;
        // Guard: ensure panOffset exists
        if (!engine.panOffset) {
            engine.panOffset = { x: 0, y: 0 };
        }

        // State
        let isPanning = false;
        let panStart = { x: 0, y: 0 };
        let lastPointer = { x: 0, y: 0 };
        let panVelocity = { x: 0, y: 0 };
        let inertiaFrame = null;
        let holdSway = false;
        let holdSwayRAF = null;
        let holdOriginPan = { x: 0, y: 0 };
        let hasPanMoved = false;
        const HOLD_SWAY_DELAY = 180; // ms
        const SWAY_AMPLITUDE = 6; // px
        const SWAY_SPEED_X = 1.2; // radians/sec factor
        const SWAY_SPEED_Y = 1.6;
        const INERTIA_DAMPING = 0.92;
        const MIN_VELOCITY = 0.25;

        const stopInertia = () => {
            if (inertiaFrame) cancelAnimationFrame(inertiaFrame);
            inertiaFrame = null;
        };

        const renderIfNeeded = () => {
            engine.needsRender = true; // engine render loop will pick this up
        };

        const startHoldSway = () => {
            holdSway = true;
            holdOriginPan = { x: engine.panOffset.x, y: engine.panOffset.y };
            const start = performance.now();
            const swayLoop = () => {
                if (!holdSway) return;
                const t = (performance.now() - start) / 1000;
                engine.panOffset.x = holdOriginPan.x + Math.sin(t * SWAY_SPEED_X) * SWAY_AMPLITUDE;
                engine.panOffset.y = holdOriginPan.y + Math.cos(t * SWAY_SPEED_Y) * SWAY_AMPLITUDE;
                renderIfNeeded();
                holdSwayRAF = requestAnimationFrame(swayLoop);
            };
            swayLoop();
        };

        const stopHoldSway = () => {
            holdSway = false;
            if (holdSwayRAF) cancelAnimationFrame(holdSwayRAF);
            holdSwayRAF = null;
            // Snap back to original pan
            engine.panOffset.x = holdOriginPan.x;
            engine.panOffset.y = holdOriginPan.y;
            renderIfNeeded();
        };

        const startInertia = () => {
            const step = () => {
                engine.panOffset.x += panVelocity.x;
                engine.panOffset.y += panVelocity.y;
                panVelocity.x *= INERTIA_DAMPING;
                panVelocity.y *= INERTIA_DAMPING;
                renderIfNeeded();
                if (Math.abs(panVelocity.x) > MIN_VELOCITY || Math.abs(panVelocity.y) > MIN_VELOCITY) {
                    inertiaFrame = requestAnimationFrame(step);
                } else {
                    inertiaFrame = null;
                }
            };
            step();
        };

        const isPointerOnDevice = (canvasX, canvasY) => {
            // Convert to world coords (inverse of render transforms)
            const worldX = (canvasX / engine.zoom) - engine.panOffset.x;
            const worldY = (canvasY / engine.zoom) - engine.panOffset.y;
            if (typeof engine.getDeviceAt === 'function') {
                return !!engine.getDeviceAt(worldX, worldY);
            }
            return false;
        };

        canvas.addEventListener('mousedown', (e) => {
            if (e.button !== 0) return;
            const rect = canvas.getBoundingClientRect();
            const canvasX = e.clientX - rect.left;
            const canvasY = e.clientY - rect.top;
            if (isPointerOnDevice(canvasX, canvasY)) return; // let engine handle device drag

            stopInertia();
            isPanning = true;
            panStart = { x: canvasX, y: canvasY };
            lastPointer = { x: canvasX, y: canvasY };
            panVelocity = { x: 0, y: 0 };
            hasPanMoved = false;

            setTimeout(() => {
                if (isPanning && !hasPanMoved) {
                    startHoldSway();
                }
            }, HOLD_SWAY_DELAY);
        });

        canvas.addEventListener('mousemove', (e) => {
            if (!isPanning) return;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const dx = (x - lastPointer.x) / engine.zoom;
            const dy = (y - lastPointer.y) / engine.zoom;

            if (Math.abs(x - panStart.x) > 3 || Math.abs(y - panStart.y) > 3) {
                if (holdSway) stopHoldSway();
                hasPanMoved = true;
            }

            if (!holdSway) {
                engine.panOffset.x += dx;
                engine.panOffset.y += dy;
                panVelocity.x = dx;
                panVelocity.y = dy;
                renderIfNeeded();
            }

            lastPointer = { x, y };
        });

        const endPan = () => {
            if (!isPanning) return;
            isPanning = false;
            if (holdSway) {
                stopHoldSway();
                return; // no inertia after pure hold
            }
            if (Math.abs(panVelocity.x) > 0.5 || Math.abs(panVelocity.y) > 0.5) {
                startInertia();
            }
        };

        canvas.addEventListener('mouseup', endPan);
        canvas.addEventListener('mouseleave', endPan);

        // Touch support basic MVP
        canvas.addEventListener('touchstart', (e) => {
            if (e.touches.length !== 1) return;
            const t = e.touches[0];
            canvas.dispatchEvent(new MouseEvent('mousedown', { clientX: t.clientX, clientY: t.clientY, button: 0 }));
        }, { passive: false });

        canvas.addEventListener('touchmove', (e) => {
            if (e.touches.length !== 1) return;
            const t = e.touches[0];
            canvas.dispatchEvent(new MouseEvent('mousemove', { clientX: t.clientX, clientY: t.clientY, button: 0 }));
            e.preventDefault();
        }, { passive: false });

        canvas.addEventListener('touchend', () => {
            canvas.dispatchEvent(new MouseEvent('mouseup', { button: 0 }));
        }, { passive: false });

        // Stop sway/inertia when window loses focus (nice-to-have for MVP stability)
        window.addEventListener('blur', () => {
            if (holdSway) stopHoldSway();
            stopInertia();
            isPanning = false;
        });

        this._mvpCameraReady = true;
        console.log('🎥 MVP camera controller active (hold + sway + drag + inertia)');
    }
    
    bridgeExistingData() {
        if (!this.existingSimulation || !this.engineInstance) return;
        
        try {
            // Transfer existing simulation data to new engine
            const existingData = this.existingSimulation.data || this.existingSimulation.simulation || {};
            const existingProgress = this.existingSimulation.progress || {};

            const importedIds = new Set((this.engineInstance.devices || []).map(d => String(d.id)));
            const importDeviceOnce = (dev) => {
                if (!dev) return;
                const key = String(dev.id || dev.label || dev.name || Math.random());
                if (importedIds.has(key)) return;
                const created = this.engineInstance.importDevice(dev);
                if (created && created.id) importedIds.add(String(created.id));
            };

            // A) From JSON topology (preferred)
            const topo = existingData.topology || existingData.simulation_config || null;
            if (topo && topo.devices) {
                const devsArr = Array.isArray(topo.devices) ? topo.devices : Object.values(topo.devices);
                devsArr.forEach(importDeviceOnce);
            }
            // Connections from JSON topology
            const rawLinks = topo ? (topo.links || topo.connections || []) : [];
            const linksArr = Array.isArray(rawLinks) ? rawLinks : Object.values(rawLinks);
            linksArr.forEach(link => this.engineInstance.importConnection(link));

            // B) From running DynamicSimulation instance state (networkDevices/networkConnections)
            const ds = this.existingSimulation;
            if (Array.isArray(ds.networkDevices) && ds.networkDevices.length) {
                ds.networkDevices.forEach(importDeviceOnce);
            }
            if (Array.isArray(ds.networkConnections) && ds.networkConnections.length) {
                ds.networkConnections.forEach(conn => this.engineInstance.importConnection(conn));
            }

            // Transfer progress data
            if (existingProgress.currentStep) {
                this.engineInstance.setCurrentStep(existingProgress.currentStep);
            }

            // Helpful viewport fit for MVP
            if ((this.engineInstance.devices || []).length) {
                try { this.engineInstance.zoomToFit(); } catch(_) {}
            }

            console.log(`🔄 Bridged data → devices: ${(this.engineInstance.devices||[]).length}, connections: ${(this.engineInstance.connections||[]).length}`);
            
        } catch (error) {
            console.error('❌ Failed to bridge existing data:', error);
        }
    }
    
    overrideConfigurationMethods() {
        if (!this.existingSimulation || !this.engineInstance) return;
        
        // Store original methods
        const original = {
            openConfigPanel: this.existingSimulation.openConfigPanel?.bind(this.existingSimulation),
            configureDevice: this.existingSimulation.configureDevice?.bind(this.existingSimulation),
            updateDeviceConfig: this.existingSimulation.updateDeviceConfig?.bind(this.existingSimulation)
        };
        
        // Override with enhanced versions
        if (this.existingSimulation.openConfigPanel) {
            this.existingSimulation.openConfigPanel = (deviceId) => {
                const device = this.engineInstance.getDevice(deviceId);
                if (device && window.networkDeviceConfigurator) {
                    window.networkDeviceConfigurator.openConfigPanel(device);
                } else if (original.openConfigPanel) {
                    original.openConfigPanel(deviceId);
                }
            };
        }
        
        if (this.existingSimulation.configureDevice) {
            this.existingSimulation.configureDevice = (deviceId, config) => {
                const device = this.engineInstance.getDevice(deviceId);
                if (device) {
                    this.engineInstance.updateDeviceConfiguration(deviceId, config);
                } else if (original.configureDevice) {
                    original.configureDevice(deviceId, config);
                }
            };
        }
        
        console.log('🔧 Configuration methods enhanced with new engine capabilities');
    }
    
    setupEventBridges() {
        if (!this.engineInstance) return;
        
        // Check if engine has event system, if not, skip event bridging
        if (typeof this.engineInstance.on !== 'function') {
            console.log('ℹ️ Engine does not support events, skipping event bridging');
            return;
        }
        
        // Bridge engine events to existing simulation
        this.engineInstance.on('device-added', (device) => {
            // Keep DynamicSimulation arrays in sync (UI counters, legacy renderers)
            if (this.existingSimulation && Array.isArray(this.existingSimulation.networkDevices)) {
                const already = this.existingSimulation.networkDevices.some(d => String(d.id) === String(device.id));
                if (!already) {
                    this.existingSimulation.networkDevices.push({
                        id: device.id,
                        type: device.type,
                        x: device.x,
                        y: device.y,
                        label: device.label,
                        config: device.config
                    });
                }
            }
            if (this.existingSimulation && this.existingSimulation.emit) {
                this.existingSimulation.emit('device-added', device);
            }
            this.updateProgressTracking('device-added', device);
        });
        
        this.engineInstance.on('device-configured', (device) => {
            if (this.existingSimulation && this.existingSimulation.emit) {
                this.existingSimulation.emit('device-configured', device);
            }
            this.updateProgressTracking('device-configured', device);
        });
        
        this.engineInstance.on('connection-created', (connection) => {
            // Mirror into DynamicSimulation's networkConnections if present
            if (this.existingSimulation && Array.isArray(this.existingSimulation.networkConnections)) {
                const from = connection.device1?.id || connection.from || connection.a;
                const to = connection.device2?.id || connection.to || connection.b;
                const exists = this.existingSimulation.networkConnections.some(c =>
                    (c.from === from && c.to === to) || (c.from === to && c.to === from)
                );
                if (!exists && from && to) {
                    this.existingSimulation.networkConnections.push({
                        id: connection.id,
                        from,
                        to,
                        type: connection.type || 'ethernet',
                        status: connection.status || 'up'
                    });
                }
            }
            if (this.existingSimulation && this.existingSimulation.emit) {
                this.existingSimulation.emit('connection-created', connection);
            }
            this.updateProgressTracking('connection-created', connection);
        });
        
        this.engineInstance.on('simulation-validated', (results) => {
            if (this.existingSimulation && this.existingSimulation.emit) {
                this.existingSimulation.emit('simulation-validated', results);
            }
            this.updateProgressTracking('simulation-validated', results);
        });
        
        // Bridge existing simulation events to engine
        if (this.existingSimulation && this.existingSimulation.on) {
            this.existingSimulation.on('step-completed', (stepData) => {
                this.engineInstance.handleStepCompletion(stepData);
            });
            
            this.existingSimulation.on('hint-requested', (context) => {
                this.engineInstance.provideContextualHint(context);
            });
        }
        
        console.log('🌉 Event bridges established between systems');
    }
    
    updateProgressTracking(eventType, data) {
        // Update progress tracking based on engine events
        try {
            const progressData = {
                eventType,
                timestamp: new Date().toISOString(),
                data
            };
            
            // Send to backend if available
            if (window.simulation && window.simulation.sendProgress) {
                window.simulation.sendProgress(progressData);
            }
            
            // Update local progress
            this.updateLocalProgress(eventType, data);
            
        } catch (error) {
            console.error('❌ Failed to update progress tracking:', error);
        }
    }
    
    updateLocalProgress(eventType, data) {
        // Update step completion status based on engine events
        const stepGuidance = document.querySelector('.step-guidance-panel');
        if (!stepGuidance) return;
        
        const currentStep = stepGuidance.querySelector('.step.active');
        if (!currentStep) return;
        
        const stepType = currentStep.dataset.stepType;
        const stepRequirements = JSON.parse(currentStep.dataset.requirements || '{}');
        
        // Check if this event satisfies step requirements
        let isStepComplete = false;
        
        switch (stepType) {
            case 'add-device':
                if (eventType === 'device-added') {
                    isStepComplete = this.checkDeviceRequirements(data, stepRequirements);
                }
                break;
                
            case 'configure-device':
                if (eventType === 'device-configured') {
                    isStepComplete = this.checkConfigurationRequirements(data, stepRequirements);
                }
                break;
                
            case 'create-connection':
                if (eventType === 'connection-created') {
                    isStepComplete = this.checkConnectionRequirements(data, stepRequirements);
                }
                break;
                
            case 'validate-network':
                if (eventType === 'simulation-validated') {
                    isStepComplete = data.isValid && !data.hasErrors;
                }
                break;
        }
        
        if (isStepComplete) {
            this.markStepComplete(currentStep);
        }
    }
    
    checkDeviceRequirements(device, requirements) {
        if (!requirements.deviceType) return true;
        return device.type === requirements.deviceType;
    }
    
    checkConfigurationRequirements(device, requirements) {
        if (!requirements.configFields) return true;
        
        return requirements.configFields.every(field => {
            return device.config && device.config[field] !== undefined && device.config[field] !== '';
        });
    }
    
    checkConnectionRequirements(connection, requirements) {
        if (!requirements.connectionType) return true;
        return connection.type === requirements.connectionType;
    }
    
    markStepComplete(stepElement) {
        stepElement.classList.add('completed');
        stepElement.querySelector('.step-status').innerHTML = '<i class="fas fa-check-circle"></i>';
        
        // Move to next step after delay
        setTimeout(() => {
            this.advanceToNextStep();
        }, 1500);
    }
    
    advanceToNextStep() {
        const currentStep = document.querySelector('.step.active');
        const nextStep = currentStep ? currentStep.nextElementSibling : null;
        
        if (nextStep && nextStep.classList.contains('step')) {
            currentStep.classList.remove('active');
            nextStep.classList.add('active');
            
            // Scroll to next step
            nextStep.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Update progress bar
            this.updateProgressBar();
            
            // Show step-specific guidance
            this.showStepGuidance(nextStep);
        }
    }
    
    updateProgressBar() {
        const steps = document.querySelectorAll('.step');
        const completedSteps = document.querySelectorAll('.step.completed');
        const progress = (completedSteps.length / steps.length) * 100;
        
        const progressBar = document.querySelector('.progress-fill');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        const progressText = document.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${completedSteps.length}/${steps.length} Steps Completed`;
        }
    }
    
    showStepGuidance(stepElement) {
        const stepType = stepElement.dataset.stepType;
        const stepData = JSON.parse(stepElement.dataset.stepData || '{}');
        
        if (this.engineInstance && this.engineInstance.showStepGuidance) {
            this.engineInstance.showStepGuidance(stepType, stepData);
        }
    }
    
    dispatchIntegrationEvent() {
        const event = new CustomEvent('simulation-engine-ready', {
            detail: {
                engine: this.engineInstance,
                integration: this,
                timestamp: new Date().toISOString()
            }
        });
        
        document.dispatchEvent(event);
        console.log('📡 Integration complete event dispatched');
    }
    
    // Public API methods for external access
    getEngine() {
        return this.engineInstance;
    }
    
    getExistingSimulation() {
        return this.existingSimulation;
    }
    
    isReady() {
        return this.isEngineReady && this.engineInstance && this.existingSimulation;
    }
    
    // Enhanced methods that leverage both systems
    async saveSimulation() {
        if (!this.isReady()) return null;
        
        try {
            // Get data from new engine
            const engineData = this.engineInstance.exportSimulation();
            
            // Merge with existing simulation data
            const existingData = this.existingSimulation.data || {};
            const mergedData = {
                ...existingData,
                topology: engineData.topology,
                devices: engineData.devices,
                connections: engineData.connections,
                configuration: engineData.configuration,
                timestamp: new Date().toISOString()
            };
            
            // Save through existing simulation's save method
            if (this.existingSimulation.saveSimulation) {
                return await this.existingSimulation.saveSimulation(mergedData);
            }
            
            return mergedData;
            
        } catch (error) {
            console.error('❌ Failed to save integrated simulation:', error);
            return null;
        }
    }
    
    async validateSimulation() {
        if (!this.isReady()) return null;
        
        try {
            // Use new engine's validation
            const engineValidation = await this.engineInstance.validateNetworkConfiguration();
            
            // Enhance with existing simulation's validation if available
            let existingValidation = null;
            if (this.existingSimulation.validateConfiguration) {
                existingValidation = await this.existingSimulation.validateConfiguration();
            }
            
            // Combine validation results
            return {
                engine: engineValidation,
                existing: existingValidation,
                combined: {
                    isValid: engineValidation.isValid && (existingValidation ? existingValidation.isValid : true),
                    errors: [
                        ...(engineValidation.errors || []),
                        ...(existingValidation?.errors || [])
                    ],
                    warnings: [
                        ...(engineValidation.warnings || []),
                        ...(existingValidation?.warnings || [])
                    ]
                }
            };
            
        } catch (error) {
            console.error('❌ Failed to validate integrated simulation:', error);
            return null;
        }
    }
    
    resetSimulation() {
        if (!this.isReady()) return;
        
        try {
            // Reset both systems
            this.engineInstance.reset();
            
            if (this.existingSimulation.reset) {
                this.existingSimulation.reset();
            }
            
            console.log('🔄 Integrated simulation reset');
            
        } catch (error) {
            console.error('❌ Failed to reset integrated simulation:', error);
        }
    }
}

// Global integration bridge instance
window.simulationEngineIntegration = new SimulationEngineIntegration();

// Enhanced global methods that use the integration
window.enhancedSimulationAPI = {
    save: () => window.simulationEngineIntegration.saveSimulation(),
    validate: () => window.simulationEngineIntegration.validateSimulation(),
    reset: () => window.simulationEngineIntegration.resetSimulation(),
    getEngine: () => window.simulationEngineIntegration.getEngine(),
    isReady: () => window.simulationEngineIntegration.isReady()
};

console.log('🚀 Simulation Engine Integration Bridge ready');
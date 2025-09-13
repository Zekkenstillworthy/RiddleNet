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
                newCanvas.className = canvas.className ? canvas.className + ' network-engine-canvas' : 'network-engine-canvas';
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
            
        } catch (error) {
            console.error('❌ Failed to initialize network simulation engine:', error);
        }
    }
    
    bridgeExistingData() {
        if (!this.existingSimulation || !this.engineInstance) return;
        
        try {
            // Transfer existing simulation data to new engine
            const existingData = this.existingSimulation.data || {};
            const existingProgress = this.existingSimulation.progress || {};
            
            // Map existing devices to new engine format
            if (existingData.topology && existingData.topology.devices) {
                Object.values(existingData.topology.devices).forEach(device => {
                    this.engineInstance.importDevice(device);
                });
            }
            
            // Map existing connections
            if (existingData.topology && existingData.topology.connections) {
                Object.values(existingData.topology.connections).forEach(connection => {
                    this.engineInstance.importConnection(connection);
                });
            }
            
            // Transfer progress data
            if (existingProgress.currentStep) {
                this.engineInstance.setCurrentStep(existingProgress.currentStep);
            }
            
            console.log('🔄 Existing simulation data bridged to new engine');
            
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
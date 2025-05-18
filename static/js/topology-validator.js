/**
 * Topology Validation and Scoring System
 * This module handles validation and scoring of user-created network topologies
 */

class TopologyValidator {
    constructor() {
        this.scoringMetrics = {};
        this.deviceRequirements = {};
        this.topologyConfig = {};
    }

    // Load configuration for a specific topology type
    async loadTopologyConfig(topologyType) {
        try {
            // First check if we have the data from the server already (through Jinja variables)
            if (typeof SERVER_TOPOLOGY_DATA !== 'undefined' && SERVER_TOPOLOGY_DATA[topologyType]) {
                console.log(`Loading topology config for ${topologyType} from server data`);
                const config = SERVER_TOPOLOGY_DATA[topologyType];
                this.topologyConfig = config;
                this.deviceRequirements = config.device_requirements || this.getDefaultDeviceRequirements(topologyType);
                this.validationRules = config.validation_rules || { rules: [] };
                this.scoringMetrics = config.scoring_metrics || this.getDefaultScoringMetrics();
                return;
            }
            
            // If not available from server, fetch from API
            const response = await fetch(`/api/topology/config/${topologyType}`);
            if (!response.ok) {
                // Fallback to default configuration
                console.warn(`Could not load topology config for ${topologyType}, using defaults`);
                this.topologyConfig = this.getDefaultConfig(topologyType);
                return;
            }
            
            this.topologyConfig = await response.json();
            this.scoringMetrics = this.topologyConfig.scoring_metrics || this.getDefaultScoringMetrics();
            this.deviceRequirements = this.topologyConfig.device_requirements || this.getDefaultDeviceRequirements(topologyType);
            this.validationRules = this.topologyConfig.validation_rules || { rules: [] };
        } catch (error) {
            console.error("Error loading topology configuration:", error);
            // Fallback to defaults
            this.topologyConfig = this.getDefaultConfig(topologyType);
        }
    }
    
    // Get default scoring metrics if server doesn't provide them
    getDefaultScoringMetrics() {
        return {
            time_efficiency: 10,
            config_process: 25,
            design_layout: 20,
            completeness: 20,
            correctness: 25
        };
    }
    
    // Get default device requirements based on topology type
    getDefaultDeviceRequirements(topologyType) {
        const defaults = {
            'point-to-point': { pc: 2, router: 0, switch: 0, server: 0 },
            'star': { pc: 3, router: 0, switch: 1, server: 0 },
            'mesh': { pc: 0, router: 4, switch: 0, server: 0 },
            'bus': { pc: 4, router: 0, switch: 0, server: 0 },
            'ring': { pc: 0, router: 0, switch: 4, server: 0 },
            'tree': { pc: 4, router: 1, switch: 2, server: 0 },
            'hybrid': { pc: 3, router: 1, switch: 2, server: 1 }
        };
        
        return defaults[topologyType] || { pc: 2, router: 0, switch: 0, server: 0 };
    }
    
    // Get default configuration
    getDefaultConfig(topologyType) {
        return {
            topology_type: topologyType,
            base_score: 10,
            time_bonus: 5,
            perfect_match_bonus: 5,
            scoring_metrics: this.getDefaultScoringMetrics(),
            device_requirements: this.getDefaultDeviceRequirements(topologyType),
            validation_rules: { rules: [] }
        };
    }
    
    // Validate a user-created topology
    validateTopology(topologyType, devices, connections) {
        // First check device requirements
        const deviceCounts = this.countDeviceTypes(devices);
        const requirements = this.deviceRequirements;
        
        const missingDevices = [];
        let allRequirementsMet = true;
        
        for (const type in requirements) {
            const required = requirements[type] || 0;
            const actual = deviceCounts[type] || 0;
            
            if (actual < required) {
                allRequirementsMet = false;
                missingDevices.push(`${required - actual} more ${type}${required - actual !== 1 ? 's' : ''}`);
            }
        }
        
        if (!allRequirementsMet) {
            return {
                valid: false,
                message: `Missing required devices: ${missingDevices.join(', ')}`
            };
        }
        
        // Check any custom validation rules
        if (this.validationRules && this.validationRules.rules && this.validationRules.rules.length > 0) {
            for (const rule of this.validationRules.rules) {
                const ruleResult = this.evaluateRule(rule, devices, connections);
                if (!ruleResult.valid) {
                    return ruleResult;
                }
            }
        }
        
        // Then check topology-specific validation
        const validationFn = this.getTopologyValidationFunction(topologyType);
        const topologyValid = validationFn(devices, connections);
        
        if (!topologyValid.valid) {
            return {
                valid: false,
                message: topologyValid.message
            };
        }
        
        return {
            valid: true,
            message: "Great job! Your topology meets all the requirements."
        };
    }
    
    // Evaluate a single validation rule
    evaluateRule(rule, devices, connections) {
        if (!rule.type) {
            return { valid: true };
        }
        
        switch (rule.type) {
            case 'connection-count':
                if (connections.length < (rule.min || 0)) {
                    return {
                        valid: false,
                        message: rule.message || `At least ${rule.min} connections are required`
                    };
                }
                if (rule.max && connections.length > rule.max) {
                    return {
                        valid: false,
                        message: rule.message || `No more than ${rule.max} connections are allowed`
                    };
                }
                break;
                
            case 'device-type-connection':
                // Example: all PCs must be connected to a switch
                if (rule.sourceType && rule.targetType) {
                    const sourceDevices = devices.filter(d => d.type.toLowerCase() === rule.sourceType.toLowerCase());
                    const targetDevices = devices.filter(d => d.type.toLowerCase() === rule.targetType.toLowerCase());
                    
                    for (const src of sourceDevices) {
                        let connected = false;
                        for (const conn of connections) {
                            const targetDevice = devices.find(d => d.id === conn.target || d.id === conn.device2.id);
                            
                            if ((conn.source === src.id || conn.device1.id === src.id) && 
                                targetDevice && targetDevice.type.toLowerCase() === rule.targetType.toLowerCase()) {
                                connected = true;
                                break;
                            }
                        }
                        
                        if (!connected) {
                            return {
                                valid: false,
                                message: rule.message || `Each ${rule.sourceType} must be connected to at least one ${rule.targetType}`
                            };
                        }
                    }
                }
                break;
                
            default:
                // Unknown rule type, skip it
                break;
        }
        
        return { valid: true };
    }
    
    // Count device types in user's topology
    countDeviceTypes(devices) {
        return devices.reduce((counts, device) => {
            const type = device.type.toLowerCase();
            counts[type] = (counts[type] || 0) + 1;
            return counts;
        }, {});
    }
    
    // Calculate score based on time taken and topology correctness
    calculateScore(timeTaken, isCorrect) {
        if (!isCorrect) return 0;
        
        const baseScore = this.topologyConfig.base_score || 10;
        let timeBonus = 0;
        
        // Calculate time efficiency bonus
        const timeMetric = this.scoringMetrics.time_efficiency || 10;
        if (timeTaken < 60) { // Less than 1 minute
            timeBonus = timeMetric;
        } else if (timeTaken < 120) { // Less than 2 minutes
            timeBonus = Math.floor(timeMetric * 0.8);
        } else if (timeTaken < 180) { // Less than 3 minutes
            timeBonus = Math.floor(timeMetric * 0.6);
        } else if (timeTaken < 300) { // Less than 5 minutes
            timeBonus = Math.floor(timeMetric * 0.4);
        } else {
            timeBonus = Math.floor(timeMetric * 0.2);
        }
        
        // Calculate other metrics (in a real system, these would be evaluated separately)
        // For this example, we'll assign full points for these metrics if the topology is correct
        const configProcess = this.scoringMetrics.config_process || 25;
        const designLayout = this.scoringMetrics.design_layout || 20;
        const completeness = this.scoringMetrics.completeness || 20;
        const correctness = this.scoringMetrics.correctness || 25;
        
        const totalScore = baseScore + timeBonus + configProcess + designLayout + completeness + correctness;
        
        // Add perfect match bonus if applicable (would be determined by more specific criteria)
        const perfectMatchBonus = this.topologyConfig.perfect_match_bonus || 0;
        
        return totalScore + perfectMatchBonus;
    }
    
    // Get validation function for specific topology type
    getTopologyValidationFunction(topologyType) {
        const validators = {
            'point-to-point': (devices, connections) => {
                if (devices.length < 2) {
                    return { valid: false, message: "Point-to-point topology requires at least 2 devices" };
                }
                if (connections.length !== 1) {
                    return { valid: false, message: "Point-to-point topology should have exactly 1 connection" };
                }
                return { valid: true, message: "Valid point-to-point topology" };
            },
            'mesh': (devices, connections) => {
                if (devices.length < 3) {
                    return { valid: false, message: "Mesh topology requires at least 3 devices" };
                }
                
                // Create a connection map to check if each device is connected to all others
                const connectionMap = {};
                devices.forEach(device => {
                    connectionMap[device.label] = new Set();
                });
                
                connections.forEach(connection => {
                    connectionMap[connection.device1.label].add(connection.device2.label);
                    connectionMap[connection.device2.label].add(connection.device1.label);
                });
                
                // Check if each device is connected to all other devices
                for (const device of devices) {
                    if (connectionMap[device.label].size !== devices.length - 1) {
                        return { 
                            valid: false, 
                            message: "In a mesh topology, each device must be connected to every other device" 
                        };
                    }
                }
                
                return { valid: true, message: "Valid mesh topology" };
            },
            'star': (devices, connections) => {
                if (devices.length < 3) {
                    return { valid: false, message: "Star topology requires at least 3 devices" };
                }
                
                // Count connections per device to find the center
                const connectionCount = {};
                devices.forEach(device => {
                    connectionCount[device.label] = 0;
                });
                
                connections.forEach(connection => {
                    connectionCount[connection.device1.label]++;
                    connectionCount[connection.device2.label]++;
                });
                
                // In a star, one device should be connected to all others
                const centerExists = Object.values(connectionCount).some(count => count === devices.length - 1);
                
                if (!centerExists) {
                    return { 
                        valid: false, 
                        message: "Star topology requires one central device connected to all others" 
                    };
                }
                
                return { valid: true, message: "Valid star topology" };
            },
            // Add other topology validators as needed
            'default': (devices, connections) => {
                // Basic validation - just ensure devices are connected
                if (devices.length < 2) {
                    return { valid: false, message: "Topology requires at least 2 devices" };
                }
                if (connections.length === 0) {
                    return { valid: false, message: "Topology requires at least one connection" };
                }
                return { valid: true, message: "Valid topology" };
            }
        };
        
        return validators[topologyType] || validators.default;
    }
}

// Export the validator
window.TopologyValidator = TopologyValidator;

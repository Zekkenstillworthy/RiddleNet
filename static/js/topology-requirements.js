// File: topology-requirements.js
// This file defines the device requirements and scoring metrics for different topology types

const topologyRequirements = {
    "point-to-point": {
        // Device requirements: minimum number of each device type required
        devices: {
            pc: 2,
            router: 0,
            switch: 0
        },
        // Scoring metrics: percentage weight of each criterion
        scoring: {
            time_efficiency: 10,
            config_process: 25,
            design_layout: 20,
            completeness: 20,
            correctness: 25
        },
        // Validation function: checks if the topology meets point-to-point requirements
        validate: function(devices, connections) {
            // Must have exactly 2 devices
            if (devices.length !== 2) return false;
            
            // Must have exactly 1 connection
            if (connections.length !== 1) return false;
            
            return true;
        }
    },
    "star": {
        devices: {
            pc: 2,
            router: 0,
            switch: 1
        },
        scoring: {
            time_efficiency: 15,
            config_process: 20,
            design_layout: 25,
            completeness: 20,
            correctness: 20
        },
        validate: function(devices, connections) {
            // Must have at least 3 devices for a star topology
            if (devices.length < 3) return false;
            
            // Count connections for each device
            const connectionCounts = devices.reduce((map, device) => {
                map[device.label] = 0;
                return map;
            }, {});
            
            connections.forEach(conn => {
                connectionCounts[conn.device1.label]++;
                connectionCounts[conn.device2.label]++;
            });
            
            // One device should be connected to all other devices (central node)
            const centralDevice = Object.values(connectionCounts).filter(
                count => count === devices.length - 1
            ).length === 1;
            
            // Total connections should be n-1 (where n is number of devices)
            const correctConnectionCount = connections.length === devices.length - 1;
            
            return centralDevice && correctConnectionCount;
        }
    },
    "mesh": {
        devices: {
            pc: 0,
            router: 3,
            switch: 0
        },
        scoring: {
            time_efficiency: 20,
            config_process: 20,
            design_layout: 20,
            completeness: 20,
            correctness: 20
        },
        validate: function(devices, connections) {
            // Must have at least 3 devices for a mesh
            if (devices.length < 3) return false;
            
            // Every device must be connected to every other device
            const connectionMap = {};
            
            // Initialize
            devices.forEach(device => {
                connectionMap[device.label] = new Set();
            });
            
            // Populate connections
            connections.forEach(connection => {
                const device1 = connection.device1.label;
                const device2 = connection.device2.label;
                
                connectionMap[device1].add(device2);
                connectionMap[device2].add(device1);
            });
            
            // Check if each device is connected to all others
            for (let device of devices) {
                if (connectionMap[device.label].size !== devices.length - 1) {
                    return false;
                }
            }
            
            return true;
        }
    },
    "bus": {
        devices: {
            pc: 3,
            router: 0,
            switch: 0
        },
        scoring: {
            time_efficiency: 15,
            config_process: 25,
            design_layout: 20,
            completeness: 20,
            correctness: 20
        },
        validate: function(devices, connections) {
            // Must have at least 3 devices for a bus
            if (devices.length < 3) return false;
            
            // All devices must connect to a common bus
            // In this simplified case, we check that total connections = devices - 1
            return connections.length === devices.length - 1;
        }
    },
    "ring": {
        devices: {
            pc: 0,
            router: 0,
            switch: 4
        },
        scoring: {
            time_efficiency: 15,
            config_process: 20,
            design_layout: 25,
            completeness: 20,
            correctness: 20
        },
        validate: function(devices, connections) {
            // Must have at least 3 devices for a ring
            if (devices.length < 3) return false;
            
            // Each device must have exactly 2 connections
            const connectionCounts = devices.reduce((map, device) => {
                map[device.label] = 0;
                return map;
            }, {});
            
            connections.forEach(conn => {
                connectionCounts[conn.device1.label]++;
                connectionCounts[conn.device2.label]++;
            });
            
            // All devices must have exactly 2 connections
            const allHaveTwoConnections = Object.values(connectionCounts).every(count => count === 2);
            
            // Total connections should equal number of devices (for a ring)
            const correctConnectionCount = connections.length === devices.length;
            
            return allHaveTwoConnections && correctConnectionCount;
        }
    },
    "tree": {
        devices: {
            pc: 4,
            router: 1,
            switch: 2
        },
        scoring: {
            time_efficiency: 20,
            config_process: 15,
            design_layout: 30,
            completeness: 15,
            correctness: 20
        },
        validate: function(devices, connections) {
            // Must have at least 3 devices for a tree
            if (devices.length < 3) return false;
            
            // Count connections for each device
            const connectionCounts = devices.reduce((map, device) => {
                map[device.label] = 0;
                return map;
            }, {});
            
            connections.forEach(conn => {
                connectionCounts[conn.device1.label]++;
                connectionCounts[conn.device2.label]++;
            });
            
            // At least one node must have more than 1 connection (root/branch)
            const hasRoot = Object.values(connectionCounts).filter(val => val > 1).length >= 1;
            
            // In a tree, connections = devices - 1
            const correctConnectionCount = connections.length === devices.length - 1;
            
            return hasRoot && correctConnectionCount;
        }
    },
    "hybrid": {
        devices: {
            pc: 4,
            router: 1,
            switch: 2,
            server: 1
        },
        scoring: {
            time_efficiency: 10,
            config_process: 20,
            design_layout: 25,
            completeness: 20,
            correctness: 25
        },
        validate: function(devices, connections) {
            // Must have at least 4 devices for a hybrid
            if (devices.length < 4) return false;
            
            // In a hybrid, we just check if it has enough connections
            // And doesn't match any of the other patterns perfectly
            return connections.length >= devices.length - 1;
        }
    }
};

// Function to check if the current topology meets device requirements
function checkDeviceRequirements(topologyType, devices) {
    // If we don't have requirements for this topology type, return true
    if (!topologyRequirements[topologyType]) return true;
    
    const requirements = topologyRequirements[topologyType].devices;
    const deviceCounts = countDeviceTypes(devices);
    
    // Check if we have at least the minimum required devices of each type
    for (const type in requirements) {
        if (deviceCounts[type] < requirements[type]) {
            return false;
        }
    }
    
    return true;
}

// Helper to count device types
function countDeviceTypes(devices) {
    const counts = {
        pc: 0,
        router: 0,
        switch: 0,
        server: 0
    };
    
    devices.forEach(device => {
        if (counts.hasOwnProperty(device.type)) {
            counts[device.type]++;
        }
    });
    
    return counts;
}

// Function to validate a topology configuration
function validateTopology(topologyType, devices, connections) {
    // First check device requirements
    if (!checkDeviceRequirements(topologyType, devices)) {
        return {
            valid: false,
            message: `This topology requires at least: ${formatRequirements(topologyType)}`
        };
    }
    
    // Then validate the topology structure
    const isValid = topologyRequirements[topologyType].validate(devices, connections);
    
    return {
        valid: isValid,
        message: isValid ? 
            "Correct topology!" : 
            "Incorrect topology structure. Check your connections."
    };
}

// Enhanced validation function with detailed feedback
function validateTopologyDetailed(topologyType, devices, connections) {
    return getTopologyFeedback(topologyType, devices, connections);
}

// Helper to format requirements for display
function formatRequirements(topologyType) {
    const req = topologyRequirements[topologyType].devices;
    const parts = [];
    
    for (const type in req) {
        if (req[type] > 0) {
            parts.push(`${req[type]} ${type}${req[type] > 1 ? 's' : ''}`);
        }
    }
    
    return parts.join(', ');
}

// Function to display device requirements for a topology
function displayRequirements(topologyType) {
    if (!topologyRequirements[topologyType]) {
        return "No specific device requirements.";
    }
    
    return `Required devices: ${formatRequirements(topologyType)}`;
}

// Calculate score based on topology setup
function calculateScore(topologyType, timeTaken, isCorrect) {
    if (!topologyRequirements[topologyType]) {
        return 100; // Default score if no requirements defined
    }
    
    const scoring = topologyRequirements[topologyType].scoring;
    let score = 0;
    
    // Base score for correctness
    if (isCorrect) {
        score += scoring.correctness;
        score += scoring.completeness;
    } else {
        return 0; // No score if the topology is incorrect
    }
    
    // Time efficiency score (inversely proportional to time taken)
    // Assuming a 5 minute (300 seconds) expected completion time
    const expectedTime = 300;
    const timeRatio = Math.min(expectedTime / timeTaken, 2); // Cap at 2x bonus
    score += scoring.time_efficiency * timeRatio;
    
    // Configuration process and design layout are subjective
    // Would typically be assigned by an instructor
    score += scoring.config_process; // Assume perfect for automatic scoring
    score += scoring.design_layout; // Assume perfect for automatic scoring
    
    return Math.round(score);
}

// Get detailed feedback on why a topology might be invalid
function getTopologyFeedback(topologyType, devices, connections) {
    // Check device requirements first
    const deviceCounts = countDeviceTypes(devices);
    const requirements = topologyRequirements[topologyType].devices;
    
    let missingDevices = [];
    for (const type in requirements) {
        if (deviceCounts[type] < requirements[type]) {
            let count = requirements[type] - deviceCounts[type];
            missingDevices.push(`${count} more ${type}${count > 1 ? 's' : ''}`);
        }
    }
    
    if (missingDevices.length > 0) {
        return {
            valid: false,
            message: `Missing required devices: ${missingDevices.join(', ')}`,
            issue: 'device_count'
        };
    }
    
    // Check topology structure
    const isValid = topologyRequirements[topologyType].validate(devices, connections);
    if (!isValid) {
        // Provide specific feedback based on topology type
        let structureMessage = "";
        
        switch(topologyType) {
            case 'point-to-point':
                structureMessage = "A point-to-point topology needs exactly 2 devices with 1 connection between them.";
                break;
            case 'star':
                structureMessage = "A star topology needs one central device connected to all other devices.";
                break;
            case 'mesh':
                structureMessage = "A mesh topology needs every device to be connected to every other device.";
                break;
            case 'bus':
                structureMessage = "A bus topology should form a single line with each device connected to the next one.";
                break;
            case 'ring':
                structureMessage = "A ring topology needs each device to have exactly 2 connections, forming a closed loop.";
                break;
            case 'tree':
                structureMessage = "A tree topology needs a hierarchical structure with branch points.";
                break;
            case 'hybrid':
                structureMessage = "Your hybrid topology doesn't follow a recognizable pattern.";
                break;
            default:
                structureMessage = "The connections don't match the expected topology pattern.";
        }
        
        return {
            valid: false,
            message: `Incorrect topology structure. ${structureMessage}`,
            issue: 'structure'
        };
    }
    
    return {
        valid: true,
        message: "Correct topology! Your network design matches the expected pattern.",
        issue: null
    };
}

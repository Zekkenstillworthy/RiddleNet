/**
 * Clear localStorage cache for simulation device data
 * Run this script in browser console to clear stale cached devices
 */

function clearSimulationCache(simulationId) {
    const keys = [
        `simulation_${simulationId}_progress`,
        `topology_sim_${simulationId}`,
        `riddlenet_simulation_${simulationId}`,
        `simulation_${simulationId}_state`
    ];
    
    console.log(`🧹 Clearing localStorage cache for simulation ${simulationId}...`);
    
    keys.forEach(key => {
        if (localStorage.getItem(key)) {
            localStorage.removeItem(key);
            console.log(`✅ Cleared: ${key}`);
        } else {
            console.log(`ℹ️ Not found: ${key}`);
        }
    });
    
    console.log('🎯 Cache cleared! Reload the page to load fresh topology from admin configuration.');
}

// Clear cache for simulation 1
clearSimulationCache(1);

// Clear all simulation caches (optional)
function clearAllSimulationCaches() {
    const allKeys = Object.keys(localStorage);
    const simulationKeys = allKeys.filter(key => 
        key.includes('simulation_') || 
        key.includes('topology_sim_') || 
        key.includes('riddlenet_simulation_')
    );
    
    console.log(`🧹 Clearing all simulation caches (${simulationKeys.length} items)...`);
    
    simulationKeys.forEach(key => {
        localStorage.removeItem(key);
        console.log(`✅ Cleared: ${key}`);
    });
    
    console.log('🎯 All simulation caches cleared!');
}

// Uncomment to clear all simulation caches:
// clearAllSimulationCaches();
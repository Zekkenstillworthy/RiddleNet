/**
 * Browser Debug Script for Simulation Creation
 * 
 * USAGE:
 * 1. Open browser console (F12)
 * 2. Copy and paste this entire script
 * 3. Press Enter
 * 4. Try creating a simulation
 * 5. Check the detailed console output
 */

console.log('%c🔧 SIMULATION DEBUG SCRIPT LOADED', 'color: #00ff00; font-size: 16px; font-weight: bold');

// Override the createNewSimulation function to add detailed logging
if (typeof window.createNewSimulation === 'function') {
    const originalCreateNewSimulation = window.createNewSimulation;
    
    window.createNewSimulation = function() {
        console.log('%c═══════════════════════════════════════', 'color: cyan; font-weight: bold');
        console.log('%c🚀 SIMULATION CREATION DEBUG START', 'color: cyan; font-size: 14px; font-weight: bold');
        console.log('%c═══════════════════════════════════════', 'color: cyan; font-weight: bold');
        
        // Log timestamp
        console.log('⏰ Timestamp:', new Date().toISOString());
        
        // Check HTML version
        const metaVersion = document.querySelector('meta[http-equiv="Cache-Control"]');
        console.log('📄 Page has cache-busting meta tags:', !!metaVersion);
        
        // Check script version
        const collaborationScript = document.querySelector('script[src*="collaboration-manager.js"]');
        if (collaborationScript) {
            console.log('📜 Collaboration script src:', collaborationScript.src);
        }
        
        // Check input value
        const titleInput = document.getElementById('simTitle');
        console.log('📝 Title input element:', titleInput);
        console.log('📝 Title value:', titleInput ? titleInput.value : 'NOT FOUND');
        
        // Call original function
        console.log('🔄 Calling original createNewSimulation...');
        const result = originalCreateNewSimulation.apply(this, arguments);
        
        return result;
    };
    
    console.log('✅ createNewSimulation function wrapped with debug logging');
} else {
    console.error('❌ createNewSimulation function NOT FOUND - may not be loaded yet');
}

// Intercept fetch to log the actual payload being sent
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const url = args[0];
    const options = args[1] || {};
    
    // Only log simulation creation requests
    if (url && url.includes('/instructor/simulation/api/create')) {
        console.log('%c═══════════════════════════════════════', 'color: yellow; font-weight: bold');
        console.log('%c📡 FETCH INTERCEPTED', 'color: yellow; font-size: 14px; font-weight: bold');
        console.log('%c═══════════════════════════════════════', 'color: yellow; font-weight: bold');
        console.log('🌐 URL:', url);
        console.log('⚙️ Method:', options.method);
        console.log('📋 Headers:', options.headers);
        
        if (options.body) {
            try {
                const bodyData = JSON.parse(options.body);
                console.log('📦 RAW BODY:', options.body);
                console.log('📦 PARSED BODY:', bodyData);
                console.log('🔍 Body keys:', Object.keys(bodyData));
                console.log('🔍 Has "type":', 'type' in bodyData, '=', bodyData.type);
                console.log('🔍 Has "difficulty":', 'difficulty' in bodyData, '=', bodyData.difficulty);
                console.log('🔍 Has "title":', 'title' in bodyData, '=', bodyData.title);
                console.log('🔍 Has "simulation_type" (old):', 'simulation_type' in bodyData, '=', bodyData.simulation_type);
                
                // Check if old field is being used
                if ('simulation_type' in bodyData && !('type' in bodyData)) {
                    console.error('%c⚠️ WARNING: Using OLD "simulation_type" field!', 'color: red; font-size: 16px; font-weight: bold');
                    console.error('This means the CACHED version of the page is still loading!');
                    console.error('👉 Solution: Press Ctrl+Shift+R to hard refresh');
                }
            } catch (e) {
                console.error('❌ Failed to parse body:', e);
                console.log('📦 RAW BODY:', options.body);
            }
        }
    }
    
    // Call original fetch and log response
    return originalFetch.apply(this, args).then(response => {
        if (url && url.includes('/instructor/simulation/api/create')) {
            console.log('%c═══════════════════════════════════════', 'color: magenta; font-weight: bold');
            console.log('%c📥 RESPONSE RECEIVED', 'color: magenta; font-size: 14px; font-weight: bold');
            console.log('%c═══════════════════════════════════════', 'color: magenta; font-weight: bold');
            console.log('📊 Status:', response.status, response.statusText);
            console.log('✅ OK:', response.ok);
            
            // Clone response to read it without consuming
            const clonedResponse = response.clone();
            clonedResponse.json().then(data => {
                console.log('📦 Response data:', data);
                if (!response.ok) {
                    console.error('%c❌ REQUEST FAILED', 'color: red; font-size: 14px; font-weight: bold');
                    console.error('Error:', data.error || 'Unknown error');
                }
            }).catch(e => {
                console.error('Failed to parse response JSON:', e);
            });
        }
        return response;
    });
};

console.log('✅ Fetch interceptor installed');

// Add a manual test function
window.testSimulationPayload = function() {
    const testPayload = {
        title: 'Test Simulation',
        description: 'Interactive simulation: Test Simulation',
        type: 'network',
        difficulty: 'medium',
        estimated_duration: 30,
        learning_objectives: [],
        is_published: true,
        is_active: true
    };
    
    console.log('%c🧪 MANUAL TEST PAYLOAD', 'color: lime; font-size: 14px; font-weight: bold');
    console.log('This is what SHOULD be sent:');
    console.log(testPayload);
    console.log('Keys:', Object.keys(testPayload));
    console.log('JSON:', JSON.stringify(testPayload, null, 2));
};

console.log('✅ Manual test function created: testSimulationPayload()');
console.log('%c═══════════════════════════════════════', 'color: #00ff00; font-weight: bold');
console.log('%c✅ DEBUG SCRIPT READY', 'color: #00ff00; font-size: 16px; font-weight: bold');
console.log('%cNow try creating a simulation and watch the console output', 'color: #00ff00');
console.log('%c═══════════════════════════════════════', 'color: #00ff00; font-weight: bold');

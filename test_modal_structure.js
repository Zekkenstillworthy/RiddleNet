// Test script to verify Create Lobby Modal structure
console.log('🔍 Testing Create Lobby Modal Structure...');

// Test when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 DOM Content Loaded - Testing Modal Elements:');
    
    // Test all required elements exist
    const requiredElements = [
        'createLobbyModal',
        'createLobbyForm',
        'lobbyName',
        'scenarioType', 
        'scenarioId',
        'maxParticipants'
    ];
    
    let allElementsFound = true;
    
    requiredElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            console.log(`✅ ${id}: Found (${element.tagName})`);
            // Check if element is visible
            const styles = window.getComputedStyle(element);
            console.log(`   Display: ${styles.display}, Visibility: ${styles.visibility}`);
        } else {
            console.error(`❌ ${id}: NOT FOUND`);
            allElementsFound = false;
        }
    });
    
    if (allElementsFound) {
        console.log('✅ All required modal elements found!');
        
        // Test opening the modal
        setTimeout(() => {
            console.log('🧪 Testing modal opening...');
            try {
                if (typeof showCreateLobby === 'function') {
                    console.log('✅ showCreateLobby function exists');
                    // Don't actually open it, just test that it exists
                } else {
                    console.error('❌ showCreateLobby function not found');
                }
            } catch (error) {
                console.error('❌ Error testing modal:', error);
            }
        }, 1000);
    } else {
        console.error('❌ Some required elements are missing!');
    }
});

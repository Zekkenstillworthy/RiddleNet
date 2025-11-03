// Admin WebSocket Enabler
// This script ensures WebSocket functionality is enabled for admin pages
// Place this script early in admin page loading to override any disable flags

(function() {
    'use strict';
    
    // Guard against multiple initializations
    if (window.adminSocketInitialized) {
        console.log('🔒 Admin WebSocket Enabler already initialized, skipping');
        return;
    }
    
    console.log('🔧 Admin WebSocket Enabler initializing...');
    
    // Mark as initialized
    window.adminSocketInitialized = true;
    
    // Check if we're on an admin page
    const isAdminPage = window.location.pathname.includes('/admin') || 
                       document.body.classList.contains('admin-page') ||
                       document.querySelector('.admin-header') !== null;
    
    if (isAdminPage) {
        console.log('🏛️ Admin page detected - enabling WebSocket functionality');
        
        // Override any WebSocket disable flags
        window.DISABLE_WEBSOCKET = false;
        window.ENABLE_ADMIN_WEBSOCKET = true;
        window.isAdmin = true;
        window.currentUserRole = 'admin';
        
        // Set admin context for all WebSocket managers
        window.adminWebSocketContext = {
            enabled: true,
            userRole: 'admin',
            pageType: 'admin',
            enabledAt: new Date().toISOString(),
            overriddenFlags: ['DISABLE_WEBSOCKET']
        };
        
        // Create a global function to check admin WebSocket status
        window.checkAdminWebSocketStatus = function() {
            const status = {
                isAdminPage: isAdminPage,
                websocketDisabled: window.DISABLE_WEBSOCKET,
                adminWebSocketEnabled: window.ENABLE_ADMIN_WEBSOCKET,
                isAdmin: window.isAdmin,
                currentUserRole: window.currentUserRole,
                adminWebSocketManager: typeof window.adminWebSocketManager !== 'undefined',
                socketIOAvailable: typeof io !== 'undefined'
            };
            
            console.table(status);
            return status;
        };
        
        // Monitor for any attempts to disable WebSocket
        let disableWebSocketAttempts = 0;
        const originalDefineProperty = Object.defineProperty;
        
        Object.defineProperty = function(obj, prop, descriptor) {
            if (prop === 'DISABLE_WEBSOCKET' && obj === window) {
                disableWebSocketAttempts++;
                console.warn(`⚠️ Attempt ${disableWebSocketAttempts} to set DISABLE_WEBSOCKET blocked for admin page`);
                
                // Allow setting to false, but block setting to true
                if (descriptor.value === true) {
                    console.log('🛡️ Preventing WebSocket disable on admin page');
                    descriptor.value = false;
                }
            }
            return originalDefineProperty.call(this, obj, prop, descriptor);
        };
        
        // Provide a function to manually enable admin WebSocket if needed
        window.forceEnableAdminWebSocket = function() {
            console.log('🔧 Force enabling admin WebSocket...');
            
            window.DISABLE_WEBSOCKET = false;
            window.ENABLE_ADMIN_WEBSOCKET = true;
            
            // Try to initialize AdminWebSocketManager if it exists
            if (window.AdminWebSocketManager && !window.adminWebSocketManager) {
                console.log('🚀 Initializing AdminWebSocketManager...');
                try {
                    window.adminWebSocketManager = new window.AdminWebSocketManager();
                    console.log('✅ AdminWebSocketManager initialized successfully');
                } catch (error) {
                    console.error('❌ Failed to initialize AdminWebSocketManager:', error);
                }
            }
            
            // Check status after force enable
            return window.checkAdminWebSocketStatus();
        };
        
        // Wait for DOM and other scripts to load, then ensure WebSocket is properly enabled
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                console.log('🔍 Checking admin WebSocket status after page load...');
                const status = window.checkAdminWebSocketStatus();
                
                if (!status.adminWebSocketManager && window.AdminWebSocketManager) {
                    console.log('🚀 Auto-initializing AdminWebSocketManager...');
                    window.forceEnableAdminWebSocket();
                }
                
                // Emit a custom event to notify other scripts that admin WebSocket is ready
                const event = new CustomEvent('adminWebSocketReady', {
                    detail: {
                        enabled: true,
                        timestamp: Date.now(),
                        status: status
                    }
                });
                document.dispatchEvent(event);
                
            }, 1000); // Wait 1 second for other scripts to load
        }, { once: true }); // Use once: true to prevent duplicate listeners
        
        console.log('✅ Admin WebSocket Enabler setup complete');
        
    } else {
        console.log('👤 Non-admin page detected - WebSocket enabler not applied');
    }
    
})();

// Export status check function globally
window.getWebSocketStatus = function() {
    return {
        isAdminPage: window.location.pathname.includes('/admin'),
        disableWebSocket: window.DISABLE_WEBSOCKET,
        enableAdminWebSocket: window.ENABLE_ADMIN_WEBSOCKET,
        isAdmin: window.isAdmin,
        adminWebSocketManager: typeof window.adminWebSocketManager,
        socketIOAvailable: typeof io !== 'undefined',
        collaborationManager: typeof window.collaborationManager,
        timestamp: new Date().toISOString()
    };
};

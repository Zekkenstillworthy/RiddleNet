/**
 * Admin WebSocket Debug Utilities
 * Add this script to admin dashboard to debug WebSocket authentication issues
 */

// Global debug utilities for admin WebSocket troubleshooting
window.AdminSocketDebug = {
    
    /**
     * Test WebSocket authentication without decorators
     */
    testAuthentication: function() {
        console.log('🧪 Testing WebSocket authentication...');
        
        if (window.socketClient && window.socketClient.connected) {
            // Emit test event to check authentication
            window.socketClient.emit('test_admin_auth', {});
            
            // Listen for response
            window.socketClient.on('admin_auth_test_result', (result) => {
                console.log('🔍 Authentication Test Results:', result);
                
                // Show results in a more readable format
                console.group('🔐 Authentication Details');
                console.log('Is Authenticated:', result.is_authenticated);
                console.log('User ID:', result.user_id);
                console.log('Username:', result.username);
                console.log('User Type:', result.user_type);
                console.log('Session Exists:', result.session_exists);
                console.groupEnd();
                
                if (result.admin_checks) {
                    console.group('🎯 Admin Status Checks');
                    Object.entries(result.admin_checks).forEach(([check, value]) => {
                        console.log(`${check}:`, value);
                    });
                    console.groupEnd();
                }
                
                // Provide recommendations
                console.group('💡 Recommendations');
                if (!result.is_authenticated) {
                    console.warn('❌ User not authenticated. Please ensure you are logged in.');
                } else if (result.admin_checks) {
                    const checks = result.admin_checks;
                    if (!checks.isinstance_admin && !checks.tablename_is_admins && !checks.found_in_admin_table) {
                        console.warn('❌ User authenticated but not recognized as admin.');
                        console.log('Try these solutions:');
                        console.log('1. Check if admin user exists in database');
                        console.log('2. Verify admin login process');
                        console.log('3. Check Flask-Login user_loader configuration');
                    } else {
                        console.log('✅ Admin authentication appears to be working');
                    }
                }
                console.groupEnd();
            });
            
        } else {
            console.error('❌ WebSocket not connected. Please check connection.');
        }
    },
    
    /**
     * Test getting active users (admin-only function)
     */
    testGetActiveUsers: function() {
        console.log('👥 Testing get_active_users function...');
        
        if (window.socketClient && window.socketClient.connected) {
            // Listen for responses
            window.socketClient.on('active_users_update', (data) => {
                console.log('✅ Active users received:', data);
            });
            
            window.socketClient.on('error', (error) => {
                console.error('❌ Error received:', error);
            });
            
            // Emit request
            window.socketClient.emit('get_active_users', {});
            
        } else {
            console.error('❌ WebSocket not connected. Please check connection.');
        }
    },
    
    /**
     * Get detailed debug information about current user
     */
    debugCurrentUser: function() {
        console.log('🔍 Getting detailed user debug info...');
        
        if (window.socketClient && window.socketClient.connected) {
            // Listen for response
            window.socketClient.on('debug_admin_response', (data) => {
                console.log('📊 Debug Admin Response:', data);
                
                console.group('👤 Current User Details');
                console.log('User ID:', data.user_id);
                console.log('Username:', data.username);
                console.log('User Type:', data.user_type);
                console.log('Is Authenticated:', data.is_authenticated);
                console.log('Table Name:', data.tablename);
                console.groupEnd();
                
                console.group('🔐 Admin Attributes');
                console.log('Has is_admin:', data.has_is_admin);
                console.log('is_admin Value:', data.is_admin_value);
                console.log('Has role:', data.has_role);
                console.log('Role Value:', data.role_value);
                console.groupEnd();
                
                console.group('💾 Database Lookup');
                console.log('Exists in Admin Table:', data.exists_in_admin_table);
                console.log('Admin Table ID:', data.admin_table_id);
                console.log('Admin Table Role:', data.admin_table_role);
                if (data.admin_table_error) {
                    console.error('Admin Table Error:', data.admin_table_error);
                }
                console.groupEnd();
            });
            
            // Emit debug request
            window.socketClient.emit('debug_admin_status', {});
            
        } else {
            console.error('❌ WebSocket not connected. Please check connection.');
        }
    },
    
    /**
     * Check WebSocket connection status and cookies
     */
    checkConnection: function() {
        console.log('🔌 Checking WebSocket connection...');
        
        console.group('Connection Status');
        if (window.socketClient) {
            console.log('Socket Client Exists:', true);
            console.log('Connected:', window.socketClient.connected);
            if (window.socketClient.socket) {
                console.log('Socket ID:', window.socketClient.socket.id);
                console.log('Transport:', window.socketClient.socket.io.engine.transport.name);
            }
        } else {
            console.log('Socket Client Exists:', false);
        }
        console.groupEnd();
        
        console.group('🍪 Cookies');
        console.log('All Cookies:', document.cookie);
        
        // Check for session cookies
        const cookies = document.cookie.split(';');
        const sessionCookies = cookies.filter(cookie => 
            cookie.trim().toLowerCase().includes('session') ||
            cookie.trim().toLowerCase().includes('auth') ||
            cookie.trim().toLowerCase().includes('login')
        );
        console.log('Session/Auth Cookies:', sessionCookies);
        console.groupEnd();
        
        console.group('🌐 Network Info');
        console.log('Current URL:', window.location.href);
        console.log('Protocol:', window.location.protocol);
        console.log('Host:', window.location.host);
        console.log('Port:', window.location.port);
        console.groupEnd();
    },
    
    /**
     * Run all diagnostic tests
     */
    runFullDiagnostic: function() {
        console.log('🚀 Running full WebSocket diagnostic...');
        
        console.group('=== WebSocket Admin Diagnostic ===');
        
        // Run tests in sequence
        this.checkConnection();
        
        setTimeout(() => {
            this.testAuthentication();
        }, 1000);
        
        setTimeout(() => {
            this.debugCurrentUser();
        }, 2000);
        
        setTimeout(() => {
            this.testGetActiveUsers();
        }, 3000);
        
        setTimeout(() => {
            console.groupEnd();
            console.log('✅ Diagnostic complete. Check results above.');
        }, 4000);
    }
};

// Auto-run basic diagnostic when loaded if this is an admin page
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (window.location.pathname.includes('/admin')) {
            console.log('👑 Admin page detected - WebSocket debug utilities available');
            console.log('Run AdminSocketDebug.runFullDiagnostic() to troubleshoot WebSocket issues');
        }
    });
} else {
    if (window.location.pathname.includes('/admin')) {
        console.log('👑 Admin page detected - WebSocket debug utilities available');
        console.log('Run AdminSocketDebug.runFullDiagnostic() to troubleshoot WebSocket issues');
    }
}

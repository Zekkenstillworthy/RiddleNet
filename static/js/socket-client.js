/**
 * WebSocket connection management for RiddleNet
 * Non-disruptive real-time features that preserve template rendering
 */

// Helper for getting the current host with the correct protocol
function getHostUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = window.location.port;
    return `${protocol}//${host}:${port}`;
}

class SocketClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.eventHandlers = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000; // Start with 2 seconds
        this.healthCheckInterval = null;
        
        // Initialize video optimization when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.optimizeVideoLoading();
            });
        } else {
            this.optimizeVideoLoading();
        }
    }
    
    /**
     * Optimize video loading to prevent connection issues
     * Load video backgrounds quickly while ensuring WebSocket connection priority
     */
    optimizeVideoLoading() {
        // Find all videos on the page
        const videos = document.querySelectorAll('video');
        
        videos.forEach(video => {
            // For background videos, load immediately with low priority
            if (video.classList.contains('video-background')) {
                // Create placeholder until video is loaded
                const placeholder = document.createElement('div');
                placeholder.className = 'video-placeholder';
                placeholder.style.cssText = 'width: 100%; height: 100%; background-color: #000;';
                if (video.parentNode) {
                    video.parentNode.insertBefore(placeholder, video);
                }
                
                // Use requestIdleCallback to load video when browser is idle
                // This prioritizes more important tasks like WebSocket connection
                // Falls back to a minimal delay for browsers without requestIdleCallback
                if (window.requestIdleCallback) {
                    requestIdleCallback(() => {
                        this.loadVideoSource(video, placeholder);
                    }, { timeout: 500 }); // timeout ensures it runs within 500ms max
                } else {
                    // Minimal delay fallback for older browsers - 500ms instead of 3000ms
                    setTimeout(() => {
                        this.loadVideoSource(video, placeholder);
                    }, 500);
                }
            }
        });
    }
    
    /**
     * Helper method to load video source
     */
    loadVideoSource(video, placeholder) {
        // Remove placeholder
        if (placeholder && placeholder.parentNode) {
            placeholder.parentNode.removeChild(placeholder);
        }
        
        // Load video source
        const sources = video.querySelectorAll('source');
        if (sources.length > 0) {
            sources.forEach(source => {
                const src = source.dataset.src || source.src;
                if (src) {
                    source.src = src;
                }
            });
            video.load();
        } else if (video.dataset.src) {
            // Handle videos without source elements
            video.src = video.dataset.src;
            video.load();
        }
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        // Check if WebSocket is explicitly disabled
        if (window.DISABLE_WEBSOCKET) {
            console.log('🔌 WebSocket initialization disabled for this page');
            return;
        }

        if (this.socket && this.connected) {
            console.log('Already connected to WebSocket server');
            return;
        }

        if (this.socket) {
            console.log('Connection in progress...');
            return;
        }        // Check if we're in an environment where WebSocket should be available
        if (typeof window === 'undefined') {
            console.warn('Not in browser environment, skipping WebSocket connection');
            return;
        }

        // Load socket.io client from CDN if not already loaded
        if (!window.io) {
            console.log('Loading socket.io client...');
            const script = document.createElement('script');
            script.src = 'https://cdn.socket.io/4.6.1/socket.io.min.js';
            script.onload = () => {
                console.log('✅ Socket.io client loaded successfully');
                // Add a small delay to ensure the script is fully loaded
                setTimeout(() => this.initializeSocket(), 100);
            };
            script.onerror = (err) => {
                console.error('❌ Error loading socket.io client:', err);
                console.log('⚠️ WebSocket features will be unavailable');
                // Graceful fallback - continue without WebSocket
            };
            document.head.appendChild(script);
        } else {
            console.log('✅ Socket.io client already available');
            this.initializeSocket();
        }
    }

    /**
     * Initialize the Socket.IO connection
     */
    initializeSocket() {
        console.log('Initializing socket connection...');
        
        const url = getHostUrl();
        
        // Enhanced configuration for admin authentication
        this.socket = io(url, {
            transports: ['websocket', 'polling'],
            withCredentials: true, // This is crucial for admin sessions
            reconnection: true,
            reconnectionDelay: this.reconnectDelay,
            reconnectionDelayMax: 10000,
            timeout: 20000,
            forceNew: false,
            autoConnect: true,
            upgrade: true,
            rememberUpgrade: false,
            auth: {
                // Include any additional auth data if needed
                userAgent: navigator.userAgent,
                timestamp: Date.now()
            },
            extraHeaders: {
                // Include CSRF token if available
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        // Set up event handlers with better error handling
        this.socket.on('connect', () => {
            console.log('✅ Connected to WebSocket server');
            this.connected = true;
            this.reconnectAttempts = 0;
            this.reconnectDelay = 2000; // Reset delay
            this.trigger('connected');
            
            // Start health check
            this.startHealthCheck();
            
            // For admin pages, automatically test authentication
            if (window.location.pathname.includes('/admin') && window.AdminSocketDebug) {
                setTimeout(() => {
                    console.log('🔍 Admin page detected - running authentication check...');
                    window.AdminSocketDebug.testAuthentication();
                }, 1000);
            }
        });

        this.socket.on('disconnect', (reason) => {
            console.log('🔌 Disconnected from WebSocket server:', reason);
            this.connected = false;
            this.stopHealthCheck();
            this.trigger('disconnected', reason);
        });

        this.socket.on('connect_error', (error) => {
            console.warn('⚠️ WebSocket connection error:', error.message || error);
            this.reconnectAttempts++;
            
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                console.log('❌ Maximum reconnect attempts reached');
            } else {
                console.log(`🔄 Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                this.reconnectDelay = Math.min(this.reconnectDelay * 1.2, 10000);
            }
            
            this.trigger('connection_error', error);
        });

        // Handle general errors more gracefully
        this.socket.on('error', (error) => {
            // Improved error logging for debugging
            if (error && (error.message || error.msg)) {
                console.warn('⚠️ WebSocket general error:', error.message || error.msg, error);
            } else {
                console.warn('⚠️ WebSocket general error:', error);
            }
            // Don't trigger disconnect for general errors, just log them
            this.trigger('socket_error', error);
        });

        // Handle pong responses for health checks
        this.socket.on('pong', (data) => {
            if (data && data.client_time) {
                const roundTripTime = Date.now() - data.client_time;
                console.debug(`💓 WebSocket health: ${roundTripTime}ms latency`);
                
                if (roundTripTime > 1000) {
                    console.warn(`🐌 High WebSocket latency: ${roundTripTime}ms`);
                }
            }
        });

        // Handle health status responses
        this.socket.on('health_status', (data) => {
            console.debug('💓 Health status:', data);
        });
        
        // Set up handlers for application-specific events
        this.setupEventHandlers();
    }

    /**
     * Set up handlers for application events
     */
    setupEventHandlers() {
        // Add error handling wrapper for all event handlers
        const safeHandler = (eventName, handler) => {
            return (data) => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in ${eventName} handler:`, error);
                }
            };
        };

        // Topology-related events
        this.socket.on('topology_completed', safeHandler('topology_completed', (data) => {
            console.log('🎯 Topology completed:', data);
            this.trigger('topology_completed', data);
            
            if (data.score !== undefined) {
                this.showNotification('Topology Completed', 
                    `You've completed the ${data.topology_type} topology with a score of ${data.score}!`,
                    'success');
            }
        }));
        
        this.socket.on('topology_progress_updated', safeHandler('topology_progress_updated', (data) => {
            console.log('📊 Topology progress updated:', data);
            this.trigger('topology_progress_updated', data);
        }));
        
        this.socket.on('topology_state_updated', safeHandler('topology_state_updated', (data) => {
            console.log('🔄 Topology state updated:', data);
            this.trigger('topology_state_updated', data);
        }));
        
        // Essay-related events
        this.socket.on('essay_submitted', safeHandler('essay_submitted', (data) => {
            console.log('📝 Essay submitted:', data);
            this.trigger('essay_submitted', data);
            
            this.showNotification('Essay Submitted', 
                data.message || 'Your essay has been submitted for review', 'success');
        }));
        

        // User Authentication Events
        this.socket.on('login_success', safeHandler('login_success', (data) => {
            console.log('✅ Login successful:', data);
            this.trigger('login_success', data);
            
            this.showNotification('Login Successful', 
                data.message || 'Welcome back! You have been successfully logged in.', 'success');
        }));
        
        this.socket.on('logout_complete', safeHandler('logout_complete', (data) => {
            console.log('👋 Logout complete:', data);
            this.trigger('logout_complete', data);
            
            this.showNotification('Logout Complete', 
                data.message || 'You have been successfully logged out. See you next time!', 'info');
        }));

        // OTP-related Events
        this.socket.on('otp_request_received', safeHandler('otp_request_received', (data) => {
            console.log('📧 OTP request received:', data);
            this.trigger('otp_request_received', data);
            
            this.showNotification('OTP Requested', 
                'Processing your OTP request...', 'info', 3000);
        }));
        
        this.socket.on('otp_email_sent', safeHandler('otp_email_sent', (data) => {
            console.log('📧 OTP email sent:', data);
            this.trigger('otp_email_sent', data);
            
            this.showNotification('OTP Sent', 
                'OTP has been sent to your email. Please check your inbox and enter the code.', 'success');
        }));
        
        this.socket.on('otp_email_failed', safeHandler('otp_email_failed', (data) => {
            console.log('❌ OTP email failed:', data);
            this.trigger('otp_email_failed', data);
            
            this.showNotification('OTP Delivery Failed', 
                data.message || 'Failed to send OTP email. Please try again or contact support.', 'error');
        }));

        // ===== COLLABORATIVE TROUBLESHOOTING EVENTS =====
        // Lobby Management Events
        this.socket.on('lobby_created', safeHandler('lobby_created', (data) => {
            console.log('🏢 Lobby created:', data);
            this.trigger('lobby_created', data);
            
            if (data.success) {
                this.showNotification('Session Created', 
                    `Collaborative troubleshooting session "${data.lobby.name}" created successfully!`, 'success');
            }
        }));
        
        this.socket.on('lobby_joined', safeHandler('lobby_joined', (data) => {
            console.log('🚪 Lobby joined:', data);
            this.trigger('lobby_joined', data);
            
            if (data.success) {
                this.showNotification('Session Joined', 
                    `You've joined the collaborative session "${data.lobby.name}"`, 'success');
            }
        }));
        
        this.socket.on('lobby_left', safeHandler('lobby_left', (data) => {
            console.log('🚪 Lobby left:', data);
            this.trigger('lobby_left', data);
            
            if (data.success) {
                this.showNotification('Session Left', 
                    'You have left the collaborative session', 'info');
            }
        }));
        
        this.socket.on('public_lobbies', safeHandler('public_lobbies', (data) => {
            console.log('📋 Public lobbies:', data);
            this.trigger('public_lobbies', data);
        }));
        
        this.socket.on('my_lobby', safeHandler('my_lobby', (data) => {
            console.log('🏠 My lobby:', data);
            this.trigger('my_lobby', data);
        }));
        
        this.socket.on('new_lobby_available', safeHandler('new_lobby_available', (data) => {
            console.log('🆕 New lobby available:', data);
            this.trigger('new_lobby_available', data);
            
            this.showNotification('New Session Available', 
                `"${data.lobby.name}" is now available to join!`, 'info');
        }));

        // Real-time Collaboration Events
        this.socket.on('participant_joined', safeHandler('participant_joined', (data) => {
            console.log('👋 Participant joined:', data);
            this.trigger('participant_joined', data);
            
            this.showNotification('User Joined', 
                `${data.username} joined the session`, 'info', 3000);
        }));
        
        this.socket.on('participant_left', safeHandler('participant_left', (data) => {
            console.log('👋 Participant left:', data);
            this.trigger('participant_left', data);
            
            this.showNotification('User Left', 
                `${data.username} left the session`, 'info', 3000);
        }));
        
        this.socket.on('cursor_moved', safeHandler('cursor_moved', (data) => {
            console.debug('🖱️ Cursor moved:', data);
            this.trigger('cursor_moved', data);
        }));
        
        this.socket.on('network_topology_updated', safeHandler('network_topology_updated', (data) => {
            console.log('🔄 Network topology updated:', data);
            this.trigger('network_topology_updated', data);
        }));
        
        this.socket.on('network_state_sync', safeHandler('network_state_sync', (data) => {
            console.log('🔄 Network state sync:', data);
            this.trigger('network_state_sync', data);
        }));
        
        this.socket.on('lobby_chat_message', safeHandler('lobby_chat_message', (data) => {
            console.log('💬 Lobby chat message:', data);
            this.trigger('lobby_chat_message', data);
        }));
        
        this.socket.on('troubleshooting_progress_updated', safeHandler('troubleshooting_progress_updated', (data) => {
            console.log('📊 Troubleshooting progress updated:', data);
            this.trigger('troubleshooting_progress_updated', data);
        }));
        
        this.socket.on('lobby_state_sync', safeHandler('lobby_state_sync', (data) => {
            console.log('🔄 Lobby state sync:', data);
            this.trigger('lobby_state_sync', data);
        }));
        
        this.socket.on('lobby_closed_by_admin', safeHandler('lobby_closed_by_admin', (data) => {
            console.log('⚠️ Lobby closed by admin:', data);
            this.trigger('lobby_closed_by_admin', data);
            
            this.showNotification('Session Closed', 
                data.message || 'This session has been closed by an administrator', 'warning');
        }));

        // Lobby Browser Events
        this.socket.on('joined_lobby_browser', safeHandler('joined_lobby_browser', (data) => {
            console.log('📋 Joined lobby browser:', data);
            this.trigger('joined_lobby_browser', data);
        }));
        
        this.socket.on('left_lobby_browser', safeHandler('left_lobby_browser', (data) => {
            console.log('📋 Left lobby browser:', data);
            this.trigger('left_lobby_browser', data);
        }));

        // Notification System Events
        this.socket.on('new_announcement', safeHandler('new_announcement', (data) => {
            console.log('📢 New announcement received:', data);
            this.trigger('new_announcement', data);
            
            // Dispatch custom event for dashboard to avoid duplicate handlers
            if (typeof window !== 'undefined') {
                window.dispatchEvent(new CustomEvent('announcement-received', { 
                    detail: data 
                }));
            }
            
            // Show browser notification
            this.showNotification(
                data.title || 'New Announcement', 
                data.message || data.content || 'Check the announcements section', 
                'info'
            );
        }));
        
        this.socket.on('notification', safeHandler('notification', (data) => {
            console.log('🔔 Notification received:', data);
            this.trigger('notification', data);
            
            // Show browser notification
            this.showNotification(
                data.title || 'Notification', 
                data.message || 'You have a new notification', 
                data.type || 'info'
            );
        }));
    }

    /**
     * Show a notification to the user
     * @param {string} title - The notification title
     * @param {string} message - The notification message
     * @param {string} type - The notification type (info, success, warning, error)
     * @param {number} duration - How long to show the notification in ms
     */
    showNotification(title, message, type = 'info', duration = 5000) {
        // Check if browser supports notifications
        if ('Notification' in window) {
            // First check if we already have permission
            if (Notification.permission === 'granted') {
                new Notification(title, { body: message });
            } 
            // Otherwise, ask for permission
            else if (Notification.permission !== 'denied') {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        new Notification(title, { body: message });
                    }
                });
            }
        }
        
        // Create notification container if it doesn't exist
        let container = document.getElementById('notification-area');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-area';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.right = '20px';
            container.style.zIndex = '10000';
            document.body.appendChild(container);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `in-app-notification ${type}`;
        notification.style.cssText = `
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        
        // Add header with title and close button
        const header = document.createElement('div');
        header.className = 'notification-header';
        header.innerHTML = `
            <h4 style="margin: 0 0 8px 0; color: #333;">${title}</h4>
            <button class="close-notification" style="float: right; border: none; background: none; font-size: 18px; cursor: pointer;">&times;</button>
        `;
        
        // Add message body
        const body = document.createElement('div');
        body.className = 'notification-body';
        body.innerHTML = `<p style="margin: 0; color: #666;">${message}</p>`;
        
        // Add event listener to close button
        notification.appendChild(header);
        notification.appendChild(body);
        container.appendChild(notification);

        // Close button functionality
        header.querySelector('.close-notification').addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto-close after specified duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
        
        // Add CSS animation if not already present
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .in-app-notification.show {
                    opacity: 1;
                    transform: translateX(0);
                }
                .in-app-notification {
                    opacity: 0;
                    transform: translateX(100%);
                    transition: all 0.3s ease;
                }
            `;
            document.head.appendChild(style);
        }
        
        return notification;
    }

    /**
     * Start health check to monitor connection
     */
    startHealthCheck() {
        // Clear any existing health check
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        
        // Start periodic health check
        this.healthCheckInterval = setInterval(() => {
            if (this.connected && this.socket) {
                const timestamp = Date.now();
                this.socket.emit('ping', { client_time: timestamp });
            }
        }, 30000); // Check every 30 seconds
    }

    /**
     * Stop health check
     */
    stopHealthCheck() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }
    }

    /**
     * Send an event to the server with error handling
     */
    emit(event, data) {
        if (!this.socket) {
            console.warn('⚠️ Cannot emit event, socket not initialized');
            // Try to reconnect if not already connecting
            if (!this.connected && this.reconnectAttempts < this.maxReconnectAttempts) {
                console.log('🔄 Attempting to reconnect...');
                this.connect();
            }
            return false;
        }
        
        if (!this.connected) {
            console.warn('⚠️ Cannot emit event, not connected to WebSocket server');
            return false;
        }
        
        try {
            this.socket.emit(event, data);
            console.debug(`📤 Emitted ${event}:`, data);
            return true;
        } catch (error) {
            console.error(`❌ Error emitting ${event}:`, error);
            return false;
        }
    }

    /**
     * Register an event handler
     */
    on(event, callback) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(callback);
    }

    /**
     * Trigger event handlers for an event
     */
    trigger(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(callback => {
                try {
                    callback(data);
                } catch (err) {
                    console.error(`Error in ${event} event handler:`, err);
                }
            });
        }
    }

    /**
     * Join a topology room
     */
    joinTopology(topologyId) {
        return this.emit('join_topology', topologyId);
    }

    /**
     * Join a troubleshooting room
     */
    joinTroubleshooting(scenarioId) {
        return this.emit('join_troubleshooting', scenarioId);
    }

    /**
     * Send a topology network update
     */
    updateTopologyNetwork(topologyId, networkState) {
        return this.emit('topology_network_update', {
            topology_id: topologyId,
            network_state: networkState
        });
    }

    /**
     * Send a troubleshooting progress update
     */
    updateTroubleshootingProgress(scenarioId, currentStep, completedSteps) {
        return this.emit('troubleshooting_progress', {
            scenario_id: scenarioId,
            current_step: currentStep,
            completed_steps: completedSteps
        });
    }

    // ===== COLLABORATIVE TROUBLESHOOTING METHODS =====
    
    /**
     * Create a new collaborative troubleshooting lobby
     */
    createTroubleshootingLobby(lobbyConfig) {
        return this.emit('create_troubleshooting_lobby', lobbyConfig);
    }
    
    /**
     * Join an existing troubleshooting lobby
     */
    joinTroubleshootingLobby(lobbyId) {
        return this.emit('join_troubleshooting_lobby', {
            lobby_id: lobbyId
            // Removed password parameter - all lobbies are now public
        });
    }
    
    /**
     * Leave current troubleshooting lobby
     */
    leaveTroubleshootingLobby() {
        return this.emit('leave_troubleshooting_lobby');
    }
    
    /**
     * Get list of public lobbies
     */
    getPublicLobbies() {
        return this.emit('get_public_lobbies');
    }
    
    /**
     * Get current user's lobby
     */
    getMyLobby() {
        return this.emit('get_my_lobby');
    }
    
    /**
     * Join the lobby browser room
     */
    joinLobbyBrowser() {
        return this.emit('join_lobby_browser');
    }
    
    /**
     * Leave the lobby browser room
     */
    leaveLobbyBrowser() {
        return this.emit('leave_lobby_browser');
    }
    
    /**
     * Update cursor position for real-time collaboration
     */
    updateCursorPosition(x, y) {
        return this.emit('update_cursor_position', { x, y });
    }
    
    /**
     * Update network topology in collaborative session
     */
    updateNetworkTopology(changes) {
        return this.emit('update_network_topology', changes);
    }
    
    /**
     * Send a chat message in lobby
     */
    sendLobbyChat(message, type = 'text') {
        return this.emit('send_lobby_chat', {
            message: message,
            type: type
        });
    }
    
    /**
     * Update troubleshooting progress in collaborative session
     */
    updateCollaborativeTroubleshootingProgress(progressData) {
        return this.emit('update_troubleshooting_progress', progressData);
    }
    
    /**
     * Request full lobby state synchronization
     */
    requestLobbySync() {
        return this.emit('request_full_sync');
    }

    // === DEVICE AND CONNECTION MANAGEMENT ===
    
    /**
     * Add a device in collaborative session
     */
    addDevice(deviceData) {
        return this.emit('add_device', { device: deviceData });
    }
    
    /**
     * Remove a device in collaborative session
     */
    removeDevice(deviceId) {
        return this.emit('remove_device', { device_id: deviceId });
    }
    
    /**
     * Add a connection in collaborative session
     */
    addConnection(device1Id, device2Id, connectionType = 'ethernet') {
        return this.emit('add_connection', {
            device1_id: device1Id,
            device2_id: device2Id,
            type: connectionType
        });
    }
    
    /**
     * Remove a connection in collaborative session
     */
    removeConnection(device1Id, device2Id, connectionId = null) {
        return this.emit('remove_connection', {
            connection_id: connectionId,
            device1_id: device1Id,
            device2_id: device2Id
        });
    }
    
    /**
     * Update device configuration in collaborative session
     */
    updateDeviceConfig(deviceId, configUpdates) {
        return this.emit('update_device_config', {
            device_id: deviceId,
            config: configUpdates
        });
    }
    
    /**
     * Move a device in collaborative session
     */
    moveDevice(deviceId, position) {
        return this.emit('move_device', {
            device_id: deviceId,
            position: position
        });
    }
    
    /**
     * Lock a device for editing in collaborative session
     */
    lockDevice(deviceId) {
        return this.emit('lock_device', { device_id: deviceId });
    }
    
    /**
     * Unlock a device in collaborative session
     */
    unlockDevice(deviceId) {
        return this.emit('unlock_device', { device_id: deviceId });
    }
    
    /**
     * Execute CLI command in collaborative session
     */
    executeCliCommand(deviceId, command) {
        return this.emit('execute_cli_command', {
            device_id: deviceId,
            command: command
        });
    }
    
    /**
     * Update scenario progress in collaborative session
     */
    updateScenarioProgress(progressData) {
        return this.emit('update_scenario_progress', {
            progress: progressData
        });
    }
}

// Ensure we only create one instance with better error handling
if (typeof window !== 'undefined' && typeof window.SocketClient === 'undefined') {
    window.SocketClient = SocketClient;
}

if (typeof window !== 'undefined' && typeof window.socketClient === 'undefined') {
    // Check if WebSocket is disabled before creating the client
    if (window.DISABLE_WEBSOCKET) {
        console.log('🔌 WebSocket creation disabled for this page');
        window.socketClient = {
            connected: false,
            connect: () => console.log('WebSocket disabled'),
            emit: () => {},
            on: () => {},
            off: () => {}
        };
    } else {
        window.socketClient = new window.SocketClient();
        
        // Connect with better timing and error handling
        const connectWhenReady = () => {
            try {
                // Wait for DOM and other critical scripts to load
                setTimeout(() => {
                    console.log('🔌 Initiating WebSocket connection...');
                    window.socketClient.connect();
                }, 1000); // Reduced delay but still sufficient
            } catch (error) {
                console.error('Error during WebSocket initialization:', error);
            }
        };
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', connectWhenReady);
        } else {
            connectWhenReady();
        }
        
        console.log('✅ SocketClient initialized and ready');
    }
} else if (typeof window !== 'undefined') {
    console.log('ℹ️ SocketClient already exists, skipping initialization');
}

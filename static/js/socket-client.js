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
        if (this.socket && this.connected) {
            console.log('Already connected to WebSocket server');
            return;
        }

        if (this.socket) {
            console.log('Connection in progress...');
            return;
        }

        // Check if we're in an environment where WebSocket should be available
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
                // Add a small delay to ensure the script is fully loaded
                setTimeout(() => this.initializeSocket(), 100);
            };
            script.onerror = (err) => {
                console.error('Error loading socket.io client:', err);
                // Graceful fallback - continue without WebSocket
                this.showConnectionStatus(false, true);
            };
            document.head.appendChild(script);
        } else {
            this.initializeSocket();
        }
    }

    /**
     * Initialize the Socket.IO connection
     */
    initializeSocket() {
        console.log('Initializing socket connection...');
        
        const url = getHostUrl();
        
        this.socket = io(url, {
            transports: ['websocket', 'polling'],
            withCredentials: true,
            reconnection: true,
            reconnectionDelay: this.reconnectDelay,
            reconnectionDelayMax: 10000,
            timeout: 20000,
            forceNew: false,
            autoConnect: true,
            upgrade: true,
            rememberUpgrade: false
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
            
            // Display connection status
            this.showConnectionStatus(true);
        });

        this.socket.on('disconnect', (reason) => {
            console.log('🔌 Disconnected from WebSocket server:', reason);
            this.connected = false;
            this.trigger('disconnected', reason);
            
            // Clear health check interval
            if (this.healthCheckInterval) {
                clearInterval(this.healthCheckInterval);
                this.healthCheckInterval = null;
            }
            
            // Display connection status only if not a planned disconnect
            if (reason !== 'io client disconnect') {
                this.showConnectionStatus(false);
            }
        });

        this.socket.on('connect_error', (error) => {
            console.warn('⚠️ WebSocket connection error:', error.message || error);
            this.reconnectAttempts++;
            
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                console.log('❌ Maximum reconnect attempts reached');
                this.showConnectionStatus(false, true);
            } else {
                console.log(`🔄 Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                this.reconnectDelay = Math.min(this.reconnectDelay * 1.2, 10000);
            }
            
            this.trigger('connection_error', error);
        });

        // Handle general errors more gracefully
        this.socket.on('error', (error) => {
            console.warn('⚠️ WebSocket general error:', error);
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
     * Display a connection status indicator
     */
    showConnectionStatus(connected, failed = false) {
        // Remove any existing status element
        const existingStatus = document.getElementById('socket-connection-status');
        if (existingStatus) {
            existingStatus.remove();
        }
        
        if (failed) {
            // Permanently failed - show a more prominent error
            const errorDiv = document.createElement('div');
            errorDiv.id = 'socket-connection-status';
            errorDiv.className = 'socket-error';
            errorDiv.innerHTML = `
                <i class="bx bx-error-circle"></i>
                <span>Real-time updates unavailable</span>
                <button onclick="socketClient.connect()">Retry</button>
            `;
            document.body.appendChild(errorDiv);
            return;
        }
        
        // Create status indicator
        const statusDiv = document.createElement('div');
        statusDiv.id = 'socket-connection-status';
        statusDiv.className = connected ? 'socket-connected' : 'socket-disconnected';
        statusDiv.innerHTML = connected ? 
            '<i class="bx bx-wifi"></i> <span>Connected</span>' : 
            '<i class="bx bx-wifi-off"></i> <span>Reconnecting...</span>';
        
        // Add to page
        document.body.appendChild(statusDiv);
        
        // Hide after a delay if connected
        if (connected) {
            setTimeout(() => {
                statusDiv.className += ' fade-out';
                setTimeout(() => statusDiv.remove(), 1000);
            }, 3000);
        }
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
        
        // Admin messages
        this.socket.on('admin_message', safeHandler('admin_message', (data) => {
            console.log('👤 Admin message received:', data);
            this.trigger('admin_message', data);
            
            this.showNotification('Message from Admin', 
                data.message || 'You have a new message', 'info');
        }));
        
        // User connection events (for admin dashboard)
        this.socket.on('user_connected', safeHandler('user_connected', (data) => {
            console.log('👋 User connected:', data);
            this.trigger('user_connected', data);
        }));
        
        this.socket.on('user_disconnected', safeHandler('user_disconnected', (data) => {
            console.log('👋 User disconnected:', data);
            this.trigger('user_disconnected', data);
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

    /**
     * Start a health check to ensure connection is maintained
     */
    startHealthCheck() {
        // Clear any existing interval
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        
        // Send a ping every 60 seconds (reduced frequency to minimize server load)
        this.healthCheckInterval = setInterval(() => {
            if (this.connected && this.socket) {
                try {
                    // Use a simple emit instead of relying on server timestamp functions
                    this.socket.emit('ping', { 
                        client_time: Date.now(),
                        client_id: this.socket.id 
                    });
                } catch (error) {
                    console.warn('Health check ping failed:', error);
                    // Don't treat this as a fatal error, just log it
                }
            }
        }, 60000); // Changed from 30000 to 60000 (60 seconds)
    }

    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    }
}

// Ensure we only create one instance with better error handling
if (typeof window !== 'undefined' && typeof window.SocketClient === 'undefined') {
    window.SocketClient = SocketClient;
}

if (typeof window !== 'undefined' && typeof window.socketClient === 'undefined') {
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
} else if (typeof window !== 'undefined') {
    console.log('ℹ️ SocketClient already exists, skipping initialization');
}

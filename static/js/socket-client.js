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
        if (this.socket) {
            console.log('Already connected or connecting to WebSocket server');
            return;
        }

        // Load socket.io client from CDN if not already loaded
        if (!window.io) {
            console.log('Loading socket.io client...');
            const script = document.createElement('script');
            script.src = 'https://cdn.socket.io/4.6.1/socket.io.min.js';
            script.onload = () => this.initializeSocket();
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
            transports: ['websocket', 'polling'],  // Try WebSocket first, then polling
            withCredentials: true,
            reconnection: true,
            reconnectionDelay: this.reconnectDelay,
            reconnectionDelayMax: 10000,
            timeout: 20000,  // Increased timeout
            forceNew: false,
            autoConnect: true
        });

        // Set up event handlers
        this.socket.on('connect', () => {
            console.log('Connected to WebSocket server');
            this.connected = true;
            this.reconnectAttempts = 0;
            this.trigger('connected');
            
            // Start health check
            this.startHealthCheck();
            
            // Display connection status
            this.showConnectionStatus(true);
        });

        this.socket.on('disconnect', (reason) => {
            console.log('Disconnected from WebSocket server:', reason);
            this.connected = false;
            this.trigger('disconnected', reason);
            
            // Clear health check interval
            if (this.healthCheckInterval) {
                clearInterval(this.healthCheckInterval);
                this.healthCheckInterval = null;
            }
            
            // Display connection status
            this.showConnectionStatus(false);
            
            if (reason === 'io server disconnect') {
                // Server initiated disconnect, try to reconnect manually
                setTimeout(() => this.connect(), this.reconnectDelay);
            }
        });

        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.reconnectAttempts++;
            
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                console.log('Maximum reconnect attempts reached, stopping reconnect');
                this.socket.disconnect();
                this.showConnectionStatus(false, true);
            } else {
                // Increase delay on each attempt (exponential backoff)
                this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 10000);
            }
            
            this.trigger('connection_error', error);
        });

        // Handle pong responses for health checks
        this.socket.on('pong', (data) => {
            const roundTripTime = Date.now() - data.client_time;
            console.debug(`WebSocket health: ${roundTripTime}ms latency`);
            
            // Update connection quality indicator if latency is too high
            if (roundTripTime > 500) {
                console.warn(`High WebSocket latency: ${roundTripTime}ms`);
            }
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
        // Topology-related events
        this.socket.on('topology_completed', (data) => {
            console.log('Topology completed:', data);
            this.trigger('topology_completed', data);
            
            // Show notification
            this.showNotification('Topology Completed', 
                `You've completed the ${data.topology_type} topology with a score of ${data.score}!`);
        });
        
        this.socket.on('topology_progress_updated', (data) => {
            console.log('Topology progress updated:', data);
            this.trigger('topology_progress_updated', data);
        });
        
        this.socket.on('topology_state_updated', (data) => {
            console.log('Topology state updated:', data);
            this.trigger('topology_state_updated', data);
        });
        
        // Essay-related events
        this.socket.on('essay_submitted', (data) => {
            console.log('Essay submitted:', data);
            this.trigger('essay_submitted', data);
            
            // Show notification
            this.showNotification('Essay Submitted', data.message);
        });
        
        // Admin messages
        this.socket.on('admin_message', (data) => {
            console.log('Admin message received:', data);
            this.trigger('admin_message', data);
            
            // Show notification
            this.showNotification('Message from Admin', data.message);
        });
        
        // Error events
        this.socket.on('error', (data) => {
            console.error('WebSocket error:', data);
            this.trigger('error', data);
        });
    }

    /**
     * Show a notification to the user
     */
    showNotification(title, message, type = 'info', duration = 5000) {
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
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Send an event to the server
     */
    emit(event, data) {
        if (!this.socket || !this.connected) {
            console.warn('Cannot emit event, not connected to WebSocket server');
            return false;
        }
        
        this.socket.emit(event, data);
        return true;
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
     * Disconnect from the WebSocket server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    }

    /**
     * Start a health check to ensure connection is maintained
     */
    startHealthCheck() {
        // Clear any existing interval
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        
        // Send a ping every 20 seconds
        this.healthCheckInterval = setInterval(() => {
            if (this.connected) {
                this.emit('ping', { timestamp: Date.now() });
            }
        }, 20000);
    }
}

// Create a global instance
const socketClient = new SocketClient();

// Connect when the page loads (with delay to ensure page loads fully)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => socketClient.connect(), 500);
    });
} else {
    setTimeout(() => socketClient.connect(), 500);
}

// Make it available globally
window.socketClient = socketClient;

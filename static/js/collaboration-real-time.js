/**
 * RiddleNet Collaboration Real-Time Module
 * Handles team sessions, real-time synchronization, chat functionality, and collaboration features
 */

class CollaborationRealTime {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentSession = null;
        this.currentUser = null;
        this.teamMembers = new Map();
        this.deviceLocks = new Map();
        this.chatHistory = [];
        this.networkState = {};
        
        // UI Elements
        this.chatContainer = null;
        this.chatInput = null;
        this.participantsList = null;
        this.sessionStatus = null;
        
        // Event handlers
        this.eventHandlers = new Map();
        this.networkUpdateHandlers = [];
        this.chatMessageHandlers = [];
        this.deviceLockHandlers = [];
        
        // Configuration
        this.config = {
            autoReconnect: true,
            maxReconnectAttempts: 5,
            reconnectInterval: 3000,
            heartbeatInterval: 30000,
            chatMaxMessages: 100,
            cursorUpdateThrottle: 100
        };
        
        // State
        this.reconnectAttempts = 0;
        this.lastHeartbeat = null;
        this.cursorUpdateThrottleTimer = null;
    // Track processed chat message IDs to prevent duplicates
    this._processedChatIds = new Set();
    this._lastChatPrune = Date.now();
        
        this.init();
    }
    
    /**
     * Initialize the collaboration system
     */
    init() {
        console.log('🤝 Initializing Collaboration Real-Time System');
        
        this.setupSocketConnection();
        this.setupUIElements();
        this.setupEventListeners();
        this.loadCurrentUser();
        
        // Check if user is already in a session
        this.checkExistingSession();
        
        console.log('✅ Collaboration system initialized');
    }
    
    /**
     * Setup Socket.IO connection
     */
    setupSocketConnection() {
        if (!window.io) {
            console.error('❌ Socket.IO not available');
            return;
        }
        
        this.socket = window.io();
        
        // Connection events
        this.socket.on('connect', () => {
            console.log('✅ Connected to collaboration server');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.startHeartbeat();
            this.emit('connected');
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from collaboration server');
            this.isConnected = false;
            this.stopHeartbeat();
            this.emit('disconnected');
            
            if (this.config.autoReconnect) {
                this.attemptReconnect();
            }
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('❌ Connection error:', error);
            this.emit('connection_error', error);
        });
        
        // Team session events
        this.setupTeamSessionEvents();
        
        // Real-time collaboration events
        this.setupCollaborationEvents();
        
        // Chat events
        this.setupChatEvents();
        
        // Admin events
        this.setupAdminEvents();
    }
    
    /**
     * Setup team session WebSocket events
     */
    setupTeamSessionEvents() {
        // Session management
        this.socket.on('team_session_created', (data) => {
            console.log('🤝 Team session created:', data);
            if (data.success) {
                this.handleSessionCreated(data);
            } else {
                this.emit('session_error', data.error);
            }
        });
        
        this.socket.on('team_session_joined', (data) => {
            console.log('🤝 Team session joined:', data);
            if (data.success) {
                this.handleSessionJoined(data);
            } else {
                this.emit('session_error', data.error);
            }
        });
        
        this.socket.on('team_session_left', (data) => {
            console.log('🤝 Team session left:', data);
            this.handleSessionLeft(data);
        });
        
        this.socket.on('team_session_status', (data) => {
            if (data.success && data.in_session) {
                this.currentSession = data.session;
                this.emit('session_status_updated', data.session);
            }
        });
        
        // Team member events
        this.socket.on('team_member_joined', (data) => {
            console.log('👥 Team member joined:', data);
            this.handleMemberJoined(data);
        });
        
        this.socket.on('team_member_left', (data) => {
            console.log('👥 Team member left:', data);
            this.handleMemberLeft(data);
        });
        
        // Session invitations
        this.socket.on('team_session_invitation', (data) => {
            console.log('📧 Team session invitation:', data);
            this.handleSessionInvitation(data);
        });
        
        // Admin session management
        this.socket.on('team_session_ended_by_admin', (data) => {
            console.log('🛑 Session ended by admin:', data);
            this.handleSessionEndedByAdmin(data);
        });
    }
    
    /**
     * Setup real-time collaboration WebSocket events
     */
    setupCollaborationEvents() {
        // Network updates
        this.socket.on('team_network_updated', (data) => {
            console.log('🔄 Network updated by team member:', data);
            this.handleNetworkUpdate(data);
        });
        
        this.socket.on('team_network_update_result', (data) => {
            if (!data.success) {
                console.error('❌ Network update failed:', data.error);
                this.emit('network_update_error', data.error);
            }
        });
        
        // Device locking
        this.socket.on('team_device_locked', (data) => {
            console.log('🔒 Device locked by team member:', data);
            this.handleDeviceLocked(data);
        });
        
        this.socket.on('team_device_unlocked', (data) => {
            console.log('🔓 Device unlocked by team member:', data);
            this.handleDeviceUnlocked(data);
        });
        
        this.socket.on('team_device_lock_result', (data) => {
            this.emit('device_lock_result', data);
        });
        
        this.socket.on('team_device_unlock_result', (data) => {
            this.emit('device_unlock_result', data);
        });
        
        // CLI commands
        this.socket.on('team_cli_executed', (data) => {
            console.log('💻 CLI command executed by team member:', data);
            this.handleCLIExecuted(data);
        });
        
        this.socket.on('team_cli_result', (data) => {
            this.emit('cli_result', data);
        });
        
        // Progress updates
        this.socket.on('team_progress_updated', (data) => {
            console.log('📈 Progress updated by team member:', data);
            this.handleProgressUpdate(data);
        });
        
        // Cursor updates
        this.socket.on('team_cursor_moved', (data) => {
            this.handleCursorUpdate(data);
        });
    }
    
    /**
     * Setup chat WebSocket events
     */
    setupChatEvents() {
        this.socket.on('team_chat_message', (data) => {
            console.log('💬 Team chat message:', data);
            this.handleChatMessage(data);
        });
        
        this.socket.on('collaboration_chat_message', (data) => {
            console.log('💬 Collaboration chat message:', data);
            if (data.success && data.message) {
                this.handleChatMessage(data.message);
            }
        });
        
        this.socket.on('lobby_chat_message', (data) => {
            console.log('💬 Lobby chat message:', data);
            this.handleChatMessage(data);
        });
        
        this.socket.on('collaboration_session_joined', (data) => {
            console.log('🤝 Collaboration session joined:', data);
            if (data.chat_history && Array.isArray(data.chat_history)) {
                data.chat_history.forEach(message => {
                    this.handleChatMessage(message);
                });
            }
        });
        
        this.socket.on('collaboration_participant_joined', (data) => {
            console.log('👋 Participant joined session:', data);
            this.handleChatMessage({
                id: 'join_' + Date.now(),
                user_id: 'system',
                username: 'System',
                message: `${data.username} joined the session`,
                timestamp: new Date().toISOString(),
                message_type: 'system'
            });
        });
        
        this.socket.on('collaboration_participant_left', (data) => {
            console.log('👋 Participant left session:', data);
            this.handleChatMessage({
                id: 'leave_' + Date.now(),
                user_id: 'system',
                username: 'System',
                message: `${data.username} left the session`,
                timestamp: new Date().toISOString(),
                message_type: 'system'
            });
        });
        
        this.socket.on('team_chat_sent', (data) => {
            if (!data.success) {
                console.error('❌ Failed to send chat message:', data.error);
                this.emit('chat_error', data.error);
                this.showChatError(data.error);
            }
        });
        
        this.socket.on('team_chat_error', (data) => {
            console.error('❌ Chat error:', data.error);
            this.emit('chat_error', data.error);
            this.showChatError(data.error);
        });
        
        this.socket.on('collaboration_chat_error', (data) => {
            console.error('❌ Collaboration chat error:', data.error);
            this.showChatError(data.error);
        });
    }

    /**
     * Setup admin WebSocket events
     */
    setupAdminEvents() {
        this.socket.on('admin_team_sessions', (data) => {
            this.emit('admin_sessions_updated', data);
        });
        
        this.socket.on('admin_team_session_ended', (data) => {
            this.emit('admin_session_ended', data);
        });
    }
    
    /**
     * Setup UI elements
     */
    setupUIElements() {
        // Chat elements
        this.chatContainer = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('collaboration-chat-input');
        
        // Participants list
        this.participantsList = document.getElementById('participants-list');
        
        // Session status
        this.sessionStatus = document.getElementById('session-status');
        
        // Create UI if elements don't exist
        if (!this.chatContainer) {
            this.createChatUI();
        }
    }
    
    /**
     * Create chat UI if it doesn't exist
     */
    createChatUI() {
        // This will be called by the main templates to create UI elements
        console.log('🎨 Chat UI elements not found - should be created by template');
    }
    
    /**
     * Setup DOM event listeners
     */
    setupEventListeners() {
        // Chat input handling with proper key event management
    // Support multiple possible chat input IDs for backward compatibility
    const chatInput = document.getElementById('collaboration-chat-input') ||
              document.getElementById('team-chat-input') ||
              document.getElementById('chat-input');
        
        if (chatInput) {
            // Use keydown for Enter key only, let all other keys work normally
            const handleChatKeydown = (e) => {
                // If default was already prevented by another listener, do nothing (let native behavior happen)
                // Respect text editing keys (Backspace/Delete) – do not prevent them
                // Only intercept plain Enter (no shift) to send
                // Only intercept Enter key for sending messages
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.sendChatMessage(chatInput.value.trim());
                    chatInput.value = '';
                }
                // All other keys (backspace, delete, arrows, typing) work normally
            };
            
            // Remove any existing listeners first
            chatInput.removeEventListener('keydown', handleChatKeydown);
            chatInput.addEventListener('keydown', handleChatKeydown);
        }
        
        // Add send button listener
        const sendBtn = document.getElementById('collaboration-send-chat-btn') || 
                       document.getElementById('team-chat-send-btn');
        
        if (sendBtn) {
            const handleSendClick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (chatInput) {
                    this.sendChatMessage(chatInput.value.trim());
                    chatInput.value = '';
                    chatInput.focus();
                }
            };
            
            sendBtn.removeEventListener('click', handleSendClick);
            sendBtn.addEventListener('click', handleSendClick);
        }
        
        // Window unload - cleanup
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        // Mouse movement for cursor tracking (throttled)
        document.addEventListener('mousemove', (e) => {
            this.throttledCursorUpdate(e);
        });
    }
    
    /**
     * Load current user information
     */
    loadCurrentUser() {
        // Try to get user from various sources
        if (window.currentUser) {
            this.currentUser = window.currentUser;
        } else if (window.sessionUser) {
            this.currentUser = window.sessionUser;
        } else {
            // Try to extract from DOM or session
            const userElement = document.querySelector('[data-user-id]');
            if (userElement) {
                this.currentUser = {
                    id: userElement.dataset.userId,
                    username: userElement.dataset.username || 'Unknown'
                };
            }
        }
        
        console.log('👤 Current user loaded:', this.currentUser);
    }
    
    /**
     * Check if user is already in a session
     */
    checkExistingSession() {
        if (this.isConnected) {
            this.socket.emit('get_team_session_status');
        }
    }
    
    // ===== SESSION MANAGEMENT =====
    
    /**
     * Create a new team session
     */
    createTeamSession(simulationId, teamMembers, settings = null) {
        if (!this.isConnected) {
            this.emit('session_error', 'Not connected to server');
            return;
        }
        
        console.log('🤝 Creating team session:', { simulationId, teamMembers, settings });
        
        this.socket.emit('create_team_session', {
            simulation_id: simulationId,
            team_members: teamMembers,
            settings: settings
        });
    }
    
    /**
     * Join an existing team session
     */
    joinTeamSession(sessionId) {
        if (!this.isConnected) {
            this.emit('session_error', 'Not connected to server');
            return;
        }
        
        console.log('🤝 Joining team session:', sessionId);
        
        this.socket.emit('join_team_session', {
            session_id: sessionId
        });
    }
    
    /**
     * Leave current team session
     */
    leaveTeamSession() {
        if (!this.isConnected) {
            return;
        }
        
        console.log('🤝 Leaving team session');
        
        this.socket.emit('leave_team_session');
    }
    
    /**
     * Get current session status
     */
    getSessionStatus() {
        if (this.isConnected) {
            this.socket.emit('get_team_session_status');
        }
        return this.currentSession;
    }
    
    // ===== NETWORK COLLABORATION =====
    
    /**
     * Update network state
     */
    updateNetworkState(changes) {
        if (!this.isConnected || !this.currentSession) {
            console.warn('⚠️ Cannot update network: not in session');
            return;
        }
        
        this.socket.emit('team_network_update', {
            changes: changes
        });
        
        // Update local state optimistically
        this.applyNetworkChanges(changes);
    }
    
    /**
     * Apply network changes locally
     */
    applyNetworkChanges(changes) {
        if (changes.devices) {
            this.networkState.devices = { ...this.networkState.devices, ...changes.devices };
        }
        
        if (changes.connections) {
            this.networkState.connections = [...(this.networkState.connections || []), ...changes.connections];
        }
        
        if (changes.removed_devices) {
            changes.removed_devices.forEach(deviceId => {
                if (this.networkState.devices) {
                    delete this.networkState.devices[deviceId];
                }
            });
        }
        
        if (changes.removed_connections) {
            if (this.networkState.connections) {
                this.networkState.connections = this.networkState.connections.filter(
                    conn => !changes.removed_connections.includes(conn.id)
                );
            }
        }
    }
    
    /**
     * Lock a device for exclusive editing
     */
    lockDevice(deviceId) {
        if (!this.isConnected || !this.currentSession) {
            return Promise.reject('Not in session');
        }
        
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject('Lock request timeout');
            }, 5000);
            
            const handler = (data) => {
                clearTimeout(timeout);
                this.off('device_lock_result', handler);
                
                if (data.success) {
                    resolve(data);
                } else {
                    reject(data.error);
                }
            };
            
            this.on('device_lock_result', handler);
            
            this.socket.emit('team_device_lock', {
                device_id: deviceId
            });
        });
    }
    
    /**
     * Unlock a device
     */
    unlockDevice(deviceId) {
        if (!this.isConnected || !this.currentSession) {
            return Promise.reject('Not in session');
        }
        
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject('Unlock request timeout');
            }, 5000);
            
            const handler = (data) => {
                clearTimeout(timeout);
                this.off('device_unlock_result', handler);
                
                if (data.success) {
                    resolve(data);
                } else {
                    reject(data.error);
                }
            };
            
            this.on('device_unlock_result', handler);
            
            this.socket.emit('team_device_unlock', {
                device_id: deviceId
            });
        });
    }
    
    /**
     * Execute CLI command
     */
    executeCLICommand(deviceId, command) {
        if (!this.isConnected || !this.currentSession) {
            return Promise.reject('Not in session');
        }
        
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject('CLI command timeout');
            }, 10000);
            
            const handler = (data) => {
                clearTimeout(timeout);
                this.off('cli_result', handler);
                
                if (data.success) {
                    resolve(data);
                } else {
                    reject(data.error);
                }
            };
            
            this.on('cli_result', handler);
            
            this.socket.emit('team_cli_command', {
                device_id: deviceId,
                command: command
            });
        });
    }
    
    // ===== CHAT FUNCTIONALITY =====
    
    /**
     * Send a chat message
     */
    sendChatMessage(message) {
        if (!message) return;
        if (!this.isConnected || !this.currentSession) {
            console.warn('⚠️ Cannot send message: not in session');
            if (window.simulation && typeof window.simulation.showToast === 'function') {
                window.simulation.showToast('Join a collaboration session before chatting', 'warning');
            } else if (window.showNotification) {
                window.showNotification('Join a collaboration session before chatting', 'warning');
            }
            return;
        }
        
        const messageData = {
            message: message,
            session_id: this.currentSession.id,
            timestamp: new Date().toISOString(),
            user_id: this.currentUser?.id || 'unknown',
            username: this.currentUser?.username || 'Anonymous'
        };
        
        console.log('💬 Sending chat message:', messageData);
        // Send to server (don't render locally, wait for server response)
        this.socket.emit('collaboration_chat_message', messageData);
    }
    
    /**
     * Handle chat message
     */
    handleChatMessage(data) {
        console.log('💬 Received chat message:', data);

        // Deduplicate: if message has an id we've already processed, skip
        const msgId = data.id || (data.timestamp + '_' + data.user_id + '_' + (data.message||data.content||''));
        if (this._processedChatIds.has(msgId)) {
            console.log('💬 Skipping duplicate message:', msgId);
            return;
        }
        this._recordChatId(msgId);
        
        // Add to local chat history first
        this.addChatMessage(data);
        
        // Update team session manager chat if available
        if (window.teamSessionManager && typeof window.teamSessionManager.addTeamChatMessage === 'function') {
            window.teamSessionManager.addTeamChatMessage(data);
        }
        
        // Update enhanced team session manager if available
        if (window.enhancedTeamSessionManager && typeof window.enhancedTeamSessionManager.addChatMessage === 'function') {
            window.enhancedTeamSessionManager.addChatMessage(data);
        }
        
        // Emit chat event for other components
        this.emit('chat_message', data);
    }

    /**
     * Internal helper to record processed chat IDs with periodic pruning
     */
    _recordChatId(id) {
        this._processedChatIds.add(id);
        // Prune every 2 minutes to avoid unbounded growth
        const now = Date.now();
        if (now - this._lastChatPrune > 120000 && this._processedChatIds.size > 500) {
            this._processedChatIds = new Set(Array.from(this._processedChatIds).slice(-300));
            this._lastChatPrune = now;
        }
    }

    /**
     * Re-render currently visible chat containers from chatHistory
     */
    reloadVisibleChatContainers() {
        const chatContainers = [
            'chat-messages-container',
            'team-chat-messages',
            'enhanced-chat-messages',
            'collaboration-chat-messages'
        ];
        chatContainers.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = '';
                this.chatHistory.forEach(m => this.addMessageToContainer(el, m));
            }
        });
        this.updateChatMessageCounter();
    }
    
    /**
     * Add chat message to local history and UI
     */
    addChatMessage(data) {
        // Add to chat history
        this.chatHistory.push(data);
        
        // Limit chat history size
        if (this.chatHistory.length > this.config.chatMaxMessages) {
            this.chatHistory.shift();
        }
        
        // Update chat UI
        this.updateChatUI(data);
    }
    
    /**
     * Show chat error to user
     */
    showChatError(error) {
        if (window.simulation && typeof window.simulation.showToast === 'function') {
            window.simulation.showToast(`Chat error: ${error}`, 'error');
        } else if (window.showNotification) {
            window.showNotification(`Chat error: ${error}`, 'error');
        }
    }

    /**
     * Load chat history into UI
     */
    loadChatHistory() {
        if (!this.chatContainer) return;
        
        this.chatContainer.innerHTML = '';
        this.chatHistory.forEach(message => {
            this.addMessageToContainer(this.chatContainer, message);
        });
    }
    
    /**
     * Display chat message in UI containers
     */
    displayChatMessage(data) {
        // Find chat containers and update them
        const chatContainers = [
            'chat-messages-container',
            'team-chat-messages', 
            'enhanced-chat-messages',
            'collaboration-chat-messages'
        ];
        
        chatContainers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                this.addMessageToContainer(container, data);
            }
        });
    }
    
    /**
     * Add message to a specific container with unified styling
     */
    addMessageToContainer(container, data) {
        const messageDiv = document.createElement('div');
        
        // Determine message type and ownership for unified styling
        let messageClass = 'unified-chat-message';
        if (data.isOwnMessage || (this.currentUser && data.user_id === this.currentUser.id)) {
            messageClass += ' own-message';
        } else if (data.message_type === 'system') {
            messageClass += ' system-message';
        } else {
            messageClass += ' other-message';
        }
        
        messageDiv.className = messageClass;
        
        const timestamp = data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        }) : 'now';
        
        messageDiv.innerHTML = `
            <div class="unified-message-header">
                <span class="unified-message-author">${data.username || 'Unknown'}</span>
                <span class="unified-message-time">${timestamp}</span>
            </div>
            <div class="unified-message-content">${data.message || data.content || ''}</div>
        `;
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    /**
     * Update chat UI with new message
     */
    updateChatUI(data) {
        // Find chat containers and update them
        const chatContainers = [
            'chat-messages-container',
            'team-chat-messages',
            'enhanced-chat-messages',
            'collaboration-chat-messages'
        ];
        
        chatContainers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                this.addMessageToContainer(container, data);
            }
        });
        
        // Update chat message counter if available
        this.updateChatMessageCounter();
    }
    
    /**
     * Update chat message counter
     */
    updateChatMessageCounter() {
        const counter = document.querySelector('.chat-message-counter');
        if (counter) {
            counter.textContent = this.chatHistory.length;
        }
    }
    
    /**
     * Clear chat history and UI
     */
    clearChat() {
        this.chatHistory = [];
        
        const chatContainers = [
            'chat-messages-container',
            'team-chat-messages',
            'enhanced-chat-messages', 
            'collaboration-chat-messages'
        ];
        
        chatContainers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = '';
            }
        });
        
        this.updateChatMessageCounter();
    }

    // ===== PROGRESS TRACKING =====
    
    /**
     * Update progress
     */
    updateProgress(progressData) {
        if (!this.isConnected || !this.currentSession) {
            return;
        }
        
        this.socket.emit('team_progress_update', {
            progress: progressData
        });
    }
    
    // ===== CURSOR TRACKING =====
    
    /**
     * Update cursor position (throttled)
     */
    throttledCursorUpdate(event) {
        if (!this.currentSession) return;
        
        if (this.cursorUpdateThrottleTimer) {
            clearTimeout(this.cursorUpdateThrottleTimer);
        }
        
        this.cursorUpdateThrottleTimer = setTimeout(() => {
            this.updateCursorPosition({
                x: event.clientX,
                y: event.clientY
            });
        }, this.config.cursorUpdateThrottle);
    }
    
    /**
     * Update cursor position
     */
    updateCursorPosition(position) {
        if (!this.isConnected || !this.currentSession) {
            return;
        }
        
        this.socket.emit('team_cursor_update', {
            position: position
        });
    }

    
    // ===== EVENT HANDLERS =====
    
    /**
     * Handle session created
     */
    handleSessionCreated(data) {
        this.currentSession = data.session || { session_id: data.session_id };
        this.emit('session_created', data);
    }
    
    /**
     * Handle session joined
     */
    handleSessionJoined(data) {
        this.currentSession = data.session;
        this.networkState = data.session?.network_state || {};
        
        // Load existing chat history
        if (data.session?.recent_chat) {
            this.chatHistory = data.session.recent_chat;
            this.loadChatHistory();
        }
        
        // Load team members
        if (data.session?.participants) {
            this.updateTeamMembers(data.session.participants);
        }
        
        this.emit('session_joined', data);
    }
    
    /**
     * Handle session left
     */
    handleSessionLeft(data) {
        this.currentSession = null;
        this.networkState = {};
        this.teamMembers.clear();
        this.deviceLocks.clear();
        this.clearChat();
        
        this.emit('session_left', data);
    }
    
    /**
     * Handle team member joined
     */
    handleMemberJoined(data) {
        this.teamMembers.set(data.user_id, {
            id: data.user_id,
            username: data.username,
            status: 'online'
        });
        
        this.updateParticipantsUI();
        this.emit('member_joined', data);
        
        // Show notification
        this.showNotification(`${data.username} joined the session`, 'info');
    }
    
    /**
     * Handle team member left
     */
    handleMemberLeft(data) {
        this.teamMembers.delete(data.user_id);
        
        // Remove any device locks held by this member
        for (const [deviceId, userId] of this.deviceLocks.entries()) {
            if (userId === data.user_id) {
                this.deviceLocks.delete(deviceId);
            }
        }
        
        this.updateParticipantsUI();
        this.emit('member_left', data);
        
        // Show notification
        this.showNotification(`${data.username} left the session`, 'info');
    }
    
    /**
     * Handle session invitation
     */
    handleSessionInvitation(data) {
        this.emit('session_invitation', data);
        
        // Show invitation modal/notification
        this.showSessionInvitation(data);
    }
    
    /**
     * Handle session ended by admin
     */
    handleSessionEndedByAdmin(data) {
        this.showNotification(`Session ended by ${data.admin_name}`, 'warning');
        this.handleSessionLeft(data);
        this.emit('session_ended_by_admin', data);
    }
    
    /**
     * Handle network update from team member
     */
    handleNetworkUpdate(data) {
        console.log('🔄 Applying network changes from:', data.username);
        
        // Apply changes to local state
        if (data.network_state) {
            this.networkState = data.network_state;
        } else if (data.changes) {
            this.applyNetworkChanges(data.changes);
        }
        
        // Notify listeners
        this.networkUpdateHandlers.forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error('❌ Error in network update handler:', error);
            }
        });
        
        this.emit('network_updated', data);
    }
    
    /**
     * Handle device locked
     */
    handleDeviceLocked(data) {
        this.deviceLocks.set(data.device_id, data.locked_by);
        
        this.deviceLockHandlers.forEach(handler => {
            try {
                handler({
                    deviceId: data.device_id,
                    lockedBy: data.locked_by,
                    username: data.username,
                    action: 'locked'
                });
            } catch (error) {
                console.error('❌ Error in device lock handler:', error);
            }
        });
        
        this.emit('device_locked', data);
    }
    
    /**
     * Handle device unlocked
     */
    handleDeviceUnlocked(data) {
        this.deviceLocks.delete(data.device_id);
        
        this.deviceLockHandlers.forEach(handler => {
            try {
                handler({
                    deviceId: data.device_id,
                    username: data.username,
                    action: 'unlocked'
                });
            } catch (error) {
                console.error('❌ Error in device unlock handler:', error);
            }
        });
        
        this.emit('device_unlocked', data);
    }
    
    /**
     * Handle CLI command executed
     */
    handleCLIExecuted(data) {
        console.log(`💻 ${data.username} executed: ${data.command} on ${data.device_id}`);
        this.emit('cli_executed', data);
    }
    
    /**
     * Handle progress update
     */
    handleProgressUpdate(data) {
        console.log(`📈 Progress updated by ${data.username}`);
        this.emit('progress_updated', data);
    }
    
    /**
     * Handle cursor update
     */
    handleCursorUpdate(data) {
        this.emit('cursor_updated', data);
    }
    


    // ===== UI UPDATES =====
    
    /**
     * Update team members in participants list
     */
    updateTeamMembers(participants) {
        this.teamMembers.clear();
        
        for (const [userId, userData] of Object.entries(participants)) {
            this.teamMembers.set(userId, userData);
        }
        
        this.updateParticipantsUI();
    }
    
    /**
     * Update participants UI
     */
    updateParticipantsUI() {
        if (!this.participantsList) return;
        
        this.participantsList.innerHTML = '';
        
        this.teamMembers.forEach((member, userId) => {
            const memberElement = document.createElement('div');
            memberElement.className = 'participant-item';
            memberElement.innerHTML = `
                <div class="participant-info">
                    <span class="participant-name">${member.username}</span>
                    <span class="participant-status ${member.status}">${member.status}</span>
                </div>
            `;
            this.participantsList.appendChild(memberElement);
        });
    }
    
    /**
     * Show session invitation dialog
     */
    showSessionInvitation(data) {
        // This would show a modal or notification
        // Implementation depends on the UI framework being used
        console.log('📧 Session invitation:', data);
        
        const accept = confirm(`${data.created_by} invited you to join a collaboration session. Accept?`);
        if (accept) {
            this.joinTeamSession(data.session_id);
        }
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        
        // Try to use existing notification system
        if (window.showNotification) {
            window.showNotification(message, type);
        } else if (window.showToast) {
            window.showToast(message, type);
        } else {
            // Fallback to console
            console.log(`Notification [${type}]: ${message}`);
        }
    }
    
    // ===== EVENT SYSTEM =====
    
    /**
     * Add event listener
     */
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }
    
    /**
     * Remove event listener
     */
    off(event, handler) {
        if (!this.eventHandlers.has(event)) return;
        
        const handlers = this.eventHandlers.get(event);
        const index = handlers.indexOf(handler);
        if (index > -1) {
            handlers.splice(index, 1);
        }
    }
    
    /**
     * Emit event
     */
    emit(event, data) {
        if (!this.eventHandlers.has(event)) return;
        
        this.eventHandlers.get(event).forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`❌ Error in event handler for ${event}:`, error);
            }
        });
    }
    
    // ===== HANDLER REGISTRATION =====
    
    /**
     * Register network update handler
     */
    onNetworkUpdate(handler) {
        this.networkUpdateHandlers.push(handler);
    }
    
    /**
     * Register chat message handler
     */
    onChatMessage(handler) {
        this.chatMessageHandlers.push(handler);
    }
    
    /**
     * Register device lock handler
     */
    onDeviceLock(handler) {
        this.deviceLockHandlers.push(handler);
    }
    
    // ===== CONNECTION MANAGEMENT =====
    
    /**
     * Start heartbeat to maintain connection
     */
    startHeartbeat() {
        this.stopHeartbeat();
        
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.lastHeartbeat = Date.now();
                // Heartbeat is handled automatically by Socket.IO
            }
        }, this.config.heartbeatInterval);
    }
    
    /**
     * Stop heartbeat
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    /**
     * Attempt to reconnect
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            this.emit('reconnect_failed');
            return;
        }
        
        this.reconnectAttempts++;
        console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.socket.connect();
            }
        }, this.config.reconnectInterval);
    }
    
    // ===== UTILITY METHODS =====
    
    /**
     * Check if device is locked
     */
    isDeviceLocked(deviceId) {
        return this.deviceLocks.has(deviceId);
    }
    
    /**
     * Check if current user has device locked
     */
    hasDeviceLocked(deviceId) {
        return this.deviceLocks.get(deviceId) === this.currentUser?.id;
    }
    
    /**
     * Get device lock owner
     */
    getDeviceLockOwner(deviceId) {
        const userId = this.deviceLocks.get(deviceId);
        if (userId) {
            const member = this.teamMembers.get(userId);
            return member ? member.username : 'Unknown';
        }
        return null;
    }
    
    /**
     * Check if user is in a session
     */
    isInSession() {
        return this.currentSession !== null;
    }
    
    /**
     * Get session info
     */
    getSessionInfo() {
        return {
            session: this.currentSession,
            networkState: this.networkState,
            teamMembers: Array.from(this.teamMembers.values()),
            deviceLocks: Array.from(this.deviceLocks.entries()),
            chatHistory: this.chatHistory
        };
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        console.log('🧹 Cleaning up collaboration system');
        
        this.stopHeartbeat();
        
        if (this.cursorUpdateThrottleTimer) {
            clearTimeout(this.cursorUpdateThrottleTimer);
        }
        
        if (this.currentSession) {
            this.leaveTeamSession();
        }
        
        if (this.socket) {
            this.socket.disconnect();
        }
        
        this.eventHandlers.clear();
        this.networkUpdateHandlers = [];
        this.chatMessageHandlers = [];
        this.deviceLockHandlers = [];
        
        console.log('✅ Collaboration cleanup complete');
    }
}

// ===== GLOBAL INTEGRATION =====

// Create global instance
window.collaborationRealTime = new CollaborationRealTime();

// Expose convenience methods
window.createTeamSession = (simulationId, teamMembers, settings) => {
    return window.collaborationRealTime.createTeamSession(simulationId, teamMembers, settings);
};

window.joinTeamSession = (sessionId) => {
    return window.collaborationRealTime.joinTeamSession(sessionId);
};

window.leaveTeamSession = () => {
    return window.collaborationRealTime.leaveTeamSession();
};

window.sendTeamChatMessage = (message) => {
    return window.collaborationRealTime.sendChatMessage(message);
};

window.lockDevice = (deviceId) => {
    return window.collaborationRealTime.lockDevice(deviceId);
};

window.unlockDevice = (deviceId) => {
    return window.collaborationRealTime.unlockDevice(deviceId);
};

window.isDeviceLocked = (deviceId) => {
    return window.collaborationRealTime.isDeviceLocked(deviceId);
};

window.hasDeviceLocked = (deviceId) => {
    return window.collaborationRealTime.hasDeviceLocked(deviceId);
};

// ===== INTEGRATION WITH EXISTING SYSTEMS =====

// Integration with Dynamic Simulation
if (window.DynamicSimulation && window.DynamicSimulation.prototype) {
    // Extend DynamicSimulation with collaboration features
    const originalUpdateNetworkState = window.DynamicSimulation.prototype.updateNetworkState;
    
    window.DynamicSimulation.prototype.updateNetworkState = function(changes) {
        // Call original method
        if (originalUpdateNetworkState) {
            originalUpdateNetworkState.call(this, changes);
        }
        
        // Send to collaboration system
        if (window.collaborationRealTime.isInSession()) {
            window.collaborationRealTime.updateNetworkState(changes);
        }
    };
}

// Integration with Device Configurator
if (window.deviceConfigurator) {
    // Override device operations to include locking
    const originalConfigureDevice = window.deviceConfigurator.configureDevice;
    
    window.deviceConfigurator.configureDevice = async function(deviceId, config) {
        if (window.collaborationRealTime.isInSession()) {
            try {
                await window.collaborationRealTime.lockDevice(deviceId);
                const result = await originalConfigureDevice.call(this, deviceId, config);
                await window.collaborationRealTime.unlockDevice(deviceId);
                return result;
            } catch (error) {
                console.error('❌ Device configuration failed:', error);
                throw error;
            }
        } else {
            return originalConfigureDevice.call(this, deviceId, config);
        }
    };
}

console.log('✅ Collaboration Real-Time Module loaded successfully');

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CollaborationRealTime;
}
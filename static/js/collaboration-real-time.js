/**
 * RiddleNet Collaboration Real-Time Module
 * Handles team sessions, real-time synchronization, chat functionality, and collaboration features
 */

class CollaborationRealTime {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentSession = null;
    this.sessionId = null;
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
        
        // Cursor tracking
        this.cursors = new Map(); // Map of userId -> cursor DOM element
        this.cursorContainer = null;
        this.lastCursorUpdate = Date.now();
        
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
            cursorUpdateThrottle: 8 // Ultra-smooth 120fps (1000ms / 120 = 8.33ms)
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
        console.log('🤝 [DEBUG] ============================================');
        console.log('🤝 [DEBUG] Initializing Collaboration Real-Time System');
        console.log('🤝 [DEBUG] ============================================');
        
        this.setupSocketConnection();
        this.setupUIElements();
        this.setupEventListeners();
        this.loadCurrentUser();
        this.initializeCursorTracking(); // Initialize cursor tracking
        
        console.log('🤝 [DEBUG] After loadCurrentUser - this.currentUser:', this.currentUser);
        
        // Check if user is already in a session
        this.checkExistingSession();
        
        console.log('✅ [DEBUG] Collaboration system initialized');
        console.log('🤝 [DEBUG] ============================================');
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
                const sessionPayload = data.session || { session_id: data.session_id };
                this.updateSessionContext(sessionPayload, 'status_event');
                this.emit('session_status_updated', this.currentSession);
            } else if (data.success && !data.in_session) {
                this.clearSessionContext('status_event');
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
        this.socket.on('cursor_moved', (data) => {
            console.log('🖱️ ============================================');
            console.log('🖱️ [SOCKET] Cursor moved event received from backend!');
            console.log('🖱️ [SOCKET] Incoming cursor data:', data);
            console.log('🖱️ [SOCKET] User:', data.username, '| ID:', data.user_id);
            console.log('🖱️ [SOCKET] Position:', data.position);
            console.log('🖱️ ============================================');
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
            
            // Remove cursor for the user who left
            if (data.user_id) {
                this.removeCursor(data.user_id);
            }
            
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
        
        // NOTE: Mouse movement listener is set up in initializeCursorTracking()
        // No need for duplicate listener here
    }
    
    /**
     * Load current user information
     */
    loadCurrentUser() {
        console.log('🔍 [DEBUG] Loading current user...');
        console.log('🔍 [DEBUG] window.currentUser:', window.currentUser);
        console.log('🔍 [DEBUG] window.sessionUser:', window.sessionUser);
        
        // Try to get user from various sources
        if (window.currentUser) {
            this.currentUser = window.currentUser;
            console.log('✅ [DEBUG] Current user loaded from window.currentUser:', this.currentUser);
        } else if (window.sessionUser) {
            this.currentUser = window.sessionUser;
            console.log('✅ [DEBUG] Current user loaded from window.sessionUser:', this.currentUser);
        } else {
            // Try to extract from DOM or session
            const userElement = document.querySelector('[data-user-id]');
            if (userElement) {
                this.currentUser = {
                    id: userElement.dataset.userId,
                    username: userElement.dataset.username || 'Unknown'
                };
                console.log('✅ [DEBUG] Current user loaded from DOM element:', this.currentUser);
                console.log('🔍 [DEBUG] DOM element:', userElement);
            } else {
                console.error('❌ [DEBUG] No user element found with [data-user-id]');
            }
        }
        
        console.log('👤 [DEBUG] Final current user loaded:', this.currentUser);
    }
    
    /**
     * Check if user is already in a session
     */
    checkExistingSession() {
        console.log('🔍 [DEBUG] Checking existing session...');
        console.log('🔍 [DEBUG] Current user before session check:', this.currentUser);
        
        if (this.isConnected) {
            this.socket.emit('get_team_session_status');
        }
        
        // Set up periodic user verification to prevent session poisoning
        this.startUserVerification();
    }
    
    /**
     * Start periodic user verification to prevent session poisoning
     */
    startUserVerification() {
        // Verify user information every 5 seconds
        this.userVerificationInterval = setInterval(() => {
            const previousUser = this.currentUser ? {...this.currentUser} : null;
            this.loadCurrentUser();
            
            // Check if user changed
            if (previousUser && this.currentUser) {
                if (String(previousUser.id) !== String(this.currentUser.id) || 
                    previousUser.username !== this.currentUser.username) {
                    console.warn('⚠️ [DEBUG] USER CHANGED DETECTED!');
                    console.warn('⚠️ [DEBUG] Previous user:', previousUser);
                    console.warn('⚠️ [DEBUG] Current user:', this.currentUser);
                    
                    // Emit user changed event
                    this.emit('user_changed', {
                        previous: previousUser,
                        current: this.currentUser
                    });
                }
            }
        }, 5000);
    }
    
    /**
     * Stop user verification
     */
    stopUserVerification() {
        if (this.userVerificationInterval) {
            clearInterval(this.userVerificationInterval);
            this.userVerificationInterval = null;
        }
    }
    
    /**
     * Determine canonical session identifier from payload
     */
    extractSessionId(sessionData) {
        if (!sessionData) {
            return null;
        }
        const candidates = [
            sessionData.id,
            sessionData.session_id,
            sessionData.sessionId,
            sessionData.code,
            sessionData.session_code
        ];
        const sessionId = candidates.find((value) => value !== undefined && value !== null && value !== '');
        if (!sessionId) {
            console.warn('⚠️ [SESSION DEBUG] Session identifier missing in payload:', sessionData);
        }
        return sessionId || null;
    }

    /**
     * Update local session context with server payload
     */
    updateSessionContext(sessionData, source = 'unknown') {
        if (!sessionData) {
            this.clearSessionContext(source);
            return;
        }

        const mergedSession = {
            ...(this.currentSession || {}),
            ...sessionData
        };

        const sessionId = this.extractSessionId(mergedSession);
        if (sessionId) {
            mergedSession.id = mergedSession.id || sessionId;
            this.sessionId = sessionId;
            console.log(`✅ [SESSION DEBUG] Session ID set (${source}):`, this.sessionId);
        } else {
            console.warn(`⚠️ [SESSION DEBUG] Unable to resolve session ID (${source})`);
        }

        this.currentSession = mergedSession;
    }

    /**
     * Clear local session context and reset tracking
     */
    clearSessionContext(source = 'unknown') {
        if (this.sessionId || this.currentSession) {
            console.log(`🧹 [SESSION DEBUG] Clearing session context (${source})`);
        }
        this.sessionId = null;
        this.currentSession = null;
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
        
        console.log('🔍 [DEBUG] Preparing to send chat message...');
        console.log('🔍 [DEBUG] Current user:', this.currentUser);
        console.log('🔍 [DEBUG] Current session:', this.currentSession);
        
        const messageData = {
            message: message,
            session_id: this.currentSession.id,
            timestamp: new Date().toISOString(),
            user_id: this.currentUser?.id || 'unknown',
            username: this.currentUser?.username || 'Anonymous'
        };
        
        console.log('💬 [DEBUG] Sending chat message:', messageData);
        console.log('🔍 [DEBUG] User ID type:', typeof messageData.user_id);
        console.log('🔍 [DEBUG] Username:', messageData.username);
        
        // Send to server (don't render locally, wait for server response)
        this.socket.emit('collaboration_chat_message', messageData);
    }
    
    /**
     * Handle chat message
     */
    handleChatMessage(data) {
        console.log('💬 [DEBUG] Received chat message:', data);
        console.log('🔍 [DEBUG] Message user_id:', data.user_id, '(type:', typeof data.user_id, ')');
        console.log('🔍 [DEBUG] Message username:', data.username);
        console.log('🔍 [DEBUG] Current user:', this.currentUser);
        console.log('🔍 [DEBUG] Current user ID:', this.currentUser?.id, '(type:', typeof this.currentUser?.id, ')');

        // Deduplicate: if message has an id we've already processed, skip
        const msgId = data.id || (data.timestamp + '_' + data.user_id + '_' + (data.message||data.content||''));
        if (this._processedChatIds.has(msgId)) {
            console.log('💬 [DEBUG] Skipping duplicate message:', msgId);
            return;
        }
        this._recordChatId(msgId);
        
        console.log('🔍 [DEBUG] Processing new message ID:', msgId);
        
        // If sidebar chat (teamSessionManager) handles UI, avoid double-render
        const sidebarChatAvailable = (window.teamSessionManager && typeof window.teamSessionManager.addTeamChatMessage === 'function');
        console.log('🔍 [DEBUG] Sidebar chat available:', sidebarChatAvailable);
        
        if (sidebarChatAvailable) {
            // Update local history only (no UI)
            this.chatHistory.push(data);
            if (this.chatHistory.length > this.config.chatMaxMessages) {
                this.chatHistory.shift();
            }
            this.updateChatMessageCounter();
            // Render via sidebar chat
            console.log('🔍 [DEBUG] Delegating to teamSessionManager.addTeamChatMessage');
            window.teamSessionManager.addTeamChatMessage(data);
        } else {
            // Fallback to local UI rendering
            console.log('🔍 [DEBUG] Using fallback local UI rendering');
            this.addChatMessage(data);
        }
        
        // Enhanced manager UI disabled in MVP; sidebar chat handles rendering
        
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
            'chat-messages',
            'chat-messages-container',
            'team-chat-messages',
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
            'chat-messages',
            'chat-messages-container',
            'team-chat-messages', 
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
        console.log('🔍 [DEBUG] addMessageToContainer called');
        console.log('🔍 [DEBUG] Message data:', data);
        console.log('🔍 [DEBUG] Message user_id:', data.user_id, '(type:', typeof data.user_id, ')');
        console.log('🔍 [DEBUG] Current user ID:', this.currentUser?.id, '(type:', typeof this.currentUser?.id, ')');
        
        const messageDiv = document.createElement('div');
        
        // Determine message type and ownership for unified styling
        let messageClass = 'unified-chat-message';
        // Convert both IDs to strings for proper comparison (handles string vs number mismatch)
        const currentUserId = this.currentUser ? String(this.currentUser.id) : null;
        const messageUserId = data.user_id ? String(data.user_id) : null;
        
        console.log('🔍 [DEBUG] Comparing IDs - Current:', currentUserId, 'Message:', messageUserId);
        console.log('🔍 [DEBUG] IDs match:', currentUserId === messageUserId);
        console.log('🔍 [DEBUG] isOwnMessage flag:', data.isOwnMessage);
        
        if (data.isOwnMessage || (currentUserId && messageUserId && currentUserId === messageUserId)) {
            messageClass += ' own-message';
            console.log('✅ [DEBUG] This is OWN message - adding own-message class');
        } else if (data.message_type === 'system') {
            messageClass += ' system-message';
            console.log('✅ [DEBUG] This is SYSTEM message');
        } else {
            messageClass += ' other-message';
            console.log('✅ [DEBUG] This is OTHER user message - adding other-message class');
        }
        
        messageDiv.className = messageClass;
        
        const timestamp = data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        }) : 'now';
        
        // Display "You" for current user's messages, otherwise show username
        const displayName = (currentUserId && messageUserId && currentUserId === messageUserId) ? 'You' : (data.username || 'Unknown');
        
        console.log('🔍 [DEBUG] Display name will be:', displayName);
        console.log('🔍 [DEBUG] Message class:', messageClass);
        
        messageDiv.innerHTML = `
            <div class="unified-message-header">
                <span class="unified-message-author">${displayName}</span>
                <span class="unified-message-time">${timestamp}</span>
            </div>
            <div class="unified-message-content">${data.message || data.content || ''}</div>
        `;
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
        
        console.log('✅ [DEBUG] Message added to container');
    }
    
    /**
     * Update chat UI with new message
     */
    updateChatUI(data) {
        // Find chat containers and update them
        const chatContainers = [
            'chat-messages',
            'chat-messages-container',
            'team-chat-messages',
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
            'chat-messages',
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
     * Update cursor position
     */
    updateCursorPosition(position) {
        if (!this.isConnected || !this.currentSession) {
            return;
        }
        
        this.socket.emit('update_cursor_position', {
            x: position.x,
            y: position.y
        });
    }

    
    // ===== EVENT HANDLERS =====
    
    /**
     * Handle session created
     */
    handleSessionCreated(data) {
        const sessionPayload = data.session || { session_id: data.session_id };
        this.updateSessionContext(sessionPayload, 'session_created');
        this.emit('session_created', data);
    }
    
    /**
     * Handle session joined
     */
    handleSessionJoined(data) {
        const sessionPayload = data.session || { session_id: data.session_id };
        this.updateSessionContext(sessionPayload, 'session_joined');
        this.networkState = this.currentSession?.network_state || {};
        
        // Load existing chat history
        if (this.currentSession?.recent_chat) {
            this.chatHistory = this.currentSession.recent_chat;
            this.loadChatHistory();
        }
        
        // Load team members
        if (this.currentSession?.participants) {
            this.updateTeamMembers(this.currentSession.participants);
        }
        
        this.emit('session_joined', data);
    }
    
    /**
     * Handle session left
     */
    handleSessionLeft(data) {
        this.clearSessionContext('session_left');
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
        console.log('🖱️ [CURSOR DEBUG] ============================================');
        console.log('🖱️ [CURSOR DEBUG] Handling cursor update');
        console.log('🖱️ [CURSOR DEBUG] Raw data received:', data);
        
        // Backend sends: {user_id, username, position: {x, y}, color, profile_image}
        // Normalize to: {user_id, username, x, y, color, profile_image}
        const normalizedData = {
            user_id: data.user_id,
            username: data.username,
            x: data.position?.x || data.x || 0,
            y: data.position?.y || data.y || 0,
            color: data.color,
            profile_image: data.profile_image
        };
        
        console.log('🖱️ [CURSOR DEBUG] Normalized data:', normalizedData);
        console.log('🖱️ [CURSOR DEBUG] Current user ID:', this.currentUser?.id);
        console.log('🖱️ [CURSOR DEBUG] Is own cursor?', String(normalizedData.user_id) === String(this.currentUser?.id));
        
        this.updateCursorPosition(normalizedData.user_id, normalizedData);
        this.emit('cursor_updated', normalizedData);
        
        console.log('🖱️ [CURSOR DEBUG] ============================================');
    }

    // ===== CURSOR TRACKING METHODS =====

    /**
     * Initialize cursor tracking system
     */
    initializeCursorTracking() {
        console.log('🖱️ [CURSOR DEBUG] ============================================');
        console.log('🖱️ [CURSOR DEBUG] Initializing cursor tracking system');
        console.log('🖱️ [CURSOR DEBUG] Current user:', this.currentUser);
        console.log('🖱️ [CURSOR DEBUG] Session ID:', this.sessionId);
        console.log('🖱️ [CURSOR DEBUG] ============================================');
        
        // Create cursor container
        this.setupCursorContainer();
        
        // Setup mouse move tracking with throttling
        let lastEmit = 0;
        const throttle = 8; // Ultra-smooth 120fps (1000ms / 120 = 8.33ms)
        
        console.log('🖱️ [CURSOR DEBUG] Setting up mousemove listener with throttle:', throttle + 'ms');
        
        document.addEventListener('mousemove', (e) => {
            const now = Date.now();
            if (now - lastEmit < throttle) return;
            
            lastEmit = now;
            console.log('🖱️ [CURSOR DEBUG] Mouse moved to:', e.clientX, e.clientY);
            this.throttledCursorUpdate(e.clientX, e.clientY);
        });
        
        // Setup scroll tracking to update viewport
        let lastScrollEmit = 0;
        const scrollThrottle = 500; // Update viewport less frequently
        
        console.log('👁️ [VIEWPORT DEBUG] Setting up scroll listener with throttle:', scrollThrottle + 'ms');
        
        window.addEventListener('scroll', () => {
            const now = Date.now();
            if (now - lastScrollEmit < scrollThrottle) return;
            
            lastScrollEmit = now;
            console.log('👁️ [VIEWPORT DEBUG] Scroll detected, updating viewport');
            
            // Get current mouse position (use last known position)
            const lastX = this.lastMouseX || 0;
            const lastY = this.lastMouseY || 0;
            
            this.throttledCursorUpdate(lastX, lastY);
        }, { passive: true });
        
        // Track last mouse position for scroll updates
        document.addEventListener('mousemove', (e) => {
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
        }, { passive: true });
        
        console.log('✅ [CURSOR DEBUG] Cursor tracking initialized successfully');
    }

    /**
     * Setup cursor container in DOM
     */
    setupCursorContainer() {
        console.log('🖱️ [CURSOR DEBUG] Setting up cursor container...');
        
        // Check if container already exists
        if (this.cursorContainer) {
            console.log('🖱️ [CURSOR DEBUG] Container already exists:', this.cursorContainer);
            return;
        }
        
        // Create container
        this.cursorContainer = document.createElement('div');
        this.cursorContainer.id = 'collaboration-cursors';
        this.cursorContainer.style.position = 'fixed';
        this.cursorContainer.style.top = '0';
        this.cursorContainer.style.left = '0';
        this.cursorContainer.style.width = '100%';
        this.cursorContainer.style.height = '100%';
        this.cursorContainer.style.pointerEvents = 'none';
        this.cursorContainer.style.zIndex = '9999';
        
        document.body.appendChild(this.cursorContainer);
        
        console.log('✅ [CURSOR DEBUG] Cursor container created and appended to body');
        console.log('🖱️ [CURSOR DEBUG] Container element:', this.cursorContainer);
        console.log('🖱️ [CURSOR DEBUG] Container in DOM:', document.getElementById('collaboration-cursors'));
    }

    /**
     * Create cursor element for a user
     * @param {Number} userId - User ID
     * @param {String} username - Username to display
     * @param {String} color - Color scheme (user-1 through user-6)
     */
    createCursor(userId, username, color = 'user-1') {
        console.log('🖱️ [CURSOR DEBUG] ============================================');
        console.log('🖱️ [CURSOR DEBUG] Creating cursor for user:', userId);
        console.log('🖱️ [CURSOR DEBUG] Username:', username);
        console.log('🖱️ [CURSOR DEBUG] Color class:', color);
        
        // Create cursor wrapper
        const cursor = document.createElement('div');
        cursor.className = `collaboration-cursor ${color}`;
        cursor.id = `cursor-${userId}`;
        cursor.style.position = 'absolute';
        cursor.style.willChange = 'transform';
        cursor.dataset.userId = userId;
        
        console.log('🖱️ [CURSOR DEBUG] Cursor element created:', cursor);
        
        // Create avatar circle
        const avatar = document.createElement('div');
        avatar.className = 'cursor-avatar';
        avatar.dataset.user = this.getUserColorIndex(userId);
        
        console.log('🖱️ [CURSOR DEBUG] Avatar element created:', avatar);
        
        // Create username label
        const label = document.createElement('div');
        label.className = 'cursor-username';
        label.textContent = username;
        
        console.log('🖱️ [CURSOR DEBUG] Username label created:', label);
        
        // Assemble cursor
        cursor.appendChild(avatar);
        cursor.appendChild(label);
        
        // Store in map
        this.cursors.set(userId, cursor);
        console.log('🖱️ [CURSOR DEBUG] Cursor stored in map. Total cursors:', this.cursors.size);
        
        // Add to container
        if (!this.cursorContainer) {
            console.error('❌ [CURSOR DEBUG] Cursor container not found! Re-creating...');
            this.setupCursorContainer();
        }
        
        this.cursorContainer.appendChild(cursor);
        
        console.log('✅ [CURSOR DEBUG] Cursor added to container');
        console.log('🖱️ [CURSOR DEBUG] Container children count:', this.cursorContainer.children.length);
        console.log('🖱️ [CURSOR DEBUG] ============================================');
        
        return cursor;
    }

    /**
     * Get color index for user (1-6)
     * @param {Number} userId - User ID
     * @returns {Number} Color index (1-6)
     */
    getUserColorIndex(userId) {
        return ((userId - 1) % 6) + 1;
    }

    /**
     * Load user avatar image
     * @param {Number} userId - User ID
     * @param {HTMLElement} avatarElement - Avatar element to populate
     * @param {String} profileImage - Optional profile image URL
     * @param {String} username - Username for fallback
     */
    async loadUserAvatar(userId, avatarElement, profileImage = null, username = null) {
        console.log('🖱️ [CURSOR DEBUG] ============================================');
        console.log('🖱️ [CURSOR DEBUG] Loading avatar for user:', userId);
        console.log('🖱️ [CURSOR DEBUG] Profile image provided?', !!profileImage, profileImage);
        console.log('🖱️ [CURSOR DEBUG] Avatar element:', avatarElement);
        
        try {
            // If profile image provided directly, use it
            if (profileImage) {
                console.log('🖱️ [CURSOR DEBUG] Using provided profile image...');
                const img = document.createElement('img');
                img.className = 'cursor-profile-img';
                img.src = profileImage;
                img.alt = username || 'User Avatar';
                
                img.onload = () => {
                    console.log('✅ [CURSOR DEBUG] Profile image loaded successfully');
                    avatarElement.innerHTML = '';
                    avatarElement.appendChild(img);
                };
                
                img.onerror = () => {
                    console.log('❌ [CURSOR DEBUG] Profile image failed to load, using fallback');
                    this.setAvatarFallback(avatarElement, username, userId);
                };
                
                // Show loading state briefly
                avatarElement.innerHTML = '<div class="cursor-fallback-avatar">...</div>';
                
                console.log('🖱️ [CURSOR DEBUG] ============================================');
                return;
            }
            
            // Try to fetch user profile picture from API
            console.log('🖱️ [CURSOR DEBUG] No profile image provided, fetching from API...');
            console.log('🖱️ [CURSOR DEBUG] Fetching:', `/api/user/${userId}/avatar`);
            const response = await fetch(`/api/user/${userId}/avatar`);
            
            console.log('🖱️ [CURSOR DEBUG] API response status:', response.status);
            console.log('🖱️ [CURSOR DEBUG] API response OK?', response.ok);
            
            if (response.ok) {
                const data = await response.json();
                console.log('🖱️ [CURSOR DEBUG] API response data:', data);
                
                if (data.avatar_url) {
                    console.log('🖱️ [CURSOR DEBUG] Avatar URL found:', data.avatar_url);
                    const img = document.createElement('img');
                    img.className = 'cursor-profile-img';
                    img.src = data.avatar_url;
                    img.alt = data.username || username || 'User';
                    
                    img.onload = () => {
                        console.log('✅ [CURSOR DEBUG] Avatar loaded from API');
                        avatarElement.innerHTML = '';
                        avatarElement.appendChild(img);
                    };
                    
                    img.onerror = () => {
                        console.log('❌ [CURSOR DEBUG] API avatar failed to load, using fallback');
                        this.setAvatarFallback(avatarElement, data.username || username, userId);
                    };
                    
                    console.log('🖱️ [CURSOR DEBUG] ============================================');
                    return;
                }
            }
            
            // Fallback: Use first letter of username
            console.log('⚠️ [CURSOR DEBUG] No avatar available, using letter fallback');
            this.setAvatarFallback(avatarElement, username, userId);
            console.log('🖱️ [CURSOR DEBUG] ============================================');
            
        } catch (error) {
            console.warn('❌ [CURSOR DEBUG] Error loading avatar for user', userId, ':', error);
            this.setAvatarFallback(avatarElement, username, userId);
            console.log('🖱️ [CURSOR DEBUG] ============================================');
        }
    }
    
    /**
     * Set avatar fallback with first letter
     * @param {HTMLElement} avatarElement - Avatar element
     * @param {String} username - Username
     * @param {Number} userId - User ID
     */
    setAvatarFallback(avatarElement, username, userId) {
        const firstLetter = (username || '?')[0].toUpperCase();
        const fallback = document.createElement('div');
        fallback.className = 'cursor-fallback-avatar';
        fallback.textContent = firstLetter;
        fallback.dataset.user = this.getUserColorIndex(userId);
        
        avatarElement.innerHTML = '';
        avatarElement.appendChild(fallback);
        
        console.log('🖱️ [CURSOR DEBUG] Fallback letter set to:', firstLetter);
    }

    /**
     * Update cursor position for a user
     * @param {Number} userId - User ID
     * @param {Object} data - Cursor data {x, y, username, color, profile_image, viewport}
     */
    updateCursorPosition(userId, data) {
        console.log('🖱️ [CURSOR DEBUG] ============================================');
        console.log('🖱️ [CURSOR DEBUG] Updating cursor position for user:', userId);
        console.log('🖱️ [CURSOR DEBUG] Position data:', { x: data.x, y: data.y });
        console.log('🖱️ [CURSOR DEBUG] Viewport data:', data.viewport);
        console.log('🖱️ [CURSOR DEBUG] Current user ID:', this.currentUser?.id);
        
        // Skip own cursor
        if (userId === this.currentUser?.id || String(userId) === String(this.currentUser?.id)) {
            console.log('🖱️ [CURSOR DEBUG] Skipping own cursor (matched user ID)');
            console.log('🖱️ [CURSOR DEBUG] ============================================');
            return;
        }
        
        console.log('🖱️ [CURSOR DEBUG] This is NOT own cursor - proceeding');
        
        let cursor = this.cursors.get(userId);
        console.log('🖱️ [CURSOR DEBUG] Cursor exists in map?', !!cursor);
        
        // Create cursor if it doesn't exist
        if (!cursor) {
            console.log('🖱️ [CURSOR DEBUG] Cursor does not exist - creating new one');
            const colorClass = data.color ? `user-${data.color}` : this.getUserColorClass(userId);
            console.log('🖱️ [CURSOR DEBUG] Color class to use:', colorClass);
            
            cursor = this.createCursor(userId, data.username, colorClass);
            
            // Load profile image after cursor is created
            const avatar = cursor.querySelector('.cursor-avatar');
            this.loadUserAvatar(userId, avatar, data.profile_image, data.username);
        } else {
            // Update profile image if cursor already exists but image might have changed
            const avatar = cursor.querySelector('.cursor-avatar');
            const existingImg = avatar.querySelector('.cursor-profile-img');
            
            // If profile image provided and different from current, update it
            if (data.profile_image && (!existingImg || existingImg.src !== data.profile_image)) {
                console.log('🖱️ [CURSOR DEBUG] Updating profile image for existing cursor');
                this.loadUserAvatar(userId, avatar, data.profile_image, data.username);
            }
        }
        
        // Update position with smooth transform (no translate offset, handled by CSS)
        const transformValue = `translate(${data.x}px, ${data.y}px)`;
        cursor.style.transform = transformValue;
        
        console.log('🖱️ [CURSOR DEBUG] Cursor transform set to:', transformValue);
        
        // Update username if changed
        const label = cursor.querySelector('.cursor-username');
        if (label && label.textContent !== data.username) {
            console.log('🖱️ [CURSOR DEBUG] Updating username from', label.textContent, 'to', data.username);
            label.textContent = data.username;
        }
        
        // Update or create viewport indicator
        if (data.viewport) {
            this.updateViewportIndicator(userId, data.viewport, data.username);
        }
        
        console.log('✅ [CURSOR DEBUG] Cursor position updated successfully');
        console.log('🖱️ [CURSOR DEBUG] ============================================');
    }
    
    /**
     * Update or create viewport indicator for a user
     * @param {Number} userId - User ID
     * @param {Object} viewport - Viewport data {x, y, width, height}
     * @param {String} username - Username
     */
    updateViewportIndicator(userId, viewport, username) {
        console.log('👁️ [VIEWPORT DEBUG] Updating viewport for user:', userId, username);
        console.log('👁️ [VIEWPORT DEBUG] Viewport data:', viewport);
        
        if (!this.viewportIndicators) {
            this.viewportIndicators = new Map();
        }
        
        let indicator = this.viewportIndicators.get(userId);
        
        // Create viewport indicator if it doesn't exist
        if (!indicator) {
            console.log('👁️ [VIEWPORT DEBUG] Creating new viewport indicator');
            indicator = document.createElement('div');
            indicator.className = 'viewport-indicator';
            indicator.dataset.userId = userId;
            
            // Add username label
            const label = document.createElement('div');
            label.className = 'viewport-label';
            label.textContent = `${username}'s view`;
            indicator.appendChild(label);
            
            this.cursorContainer.appendChild(indicator);
            this.viewportIndicators.set(userId, indicator);
            
            console.log('✅ [VIEWPORT DEBUG] Viewport indicator created');
        }
        
        // Update viewport position and size
        indicator.style.left = `${viewport.x}px`;
        indicator.style.top = `${viewport.y}px`;
        indicator.style.width = `${viewport.width}px`;
        indicator.style.height = `${viewport.height}px`;
        
        // Get color class from cursor
        const cursor = this.cursors.get(userId);
        if (cursor) {
            const colorClass = cursor.className.match(/user-\d+/)?.[0] || 'user-1';
            indicator.className = `viewport-indicator ${colorClass}`;
        }
        
        console.log('✅ [VIEWPORT DEBUG] Viewport indicator updated');
    }

    /**
     * Remove cursor for a user
     * @param {Number} userId - User ID
     */
    removeCursor(userId) {
        console.log('🖱️ [CURSOR DEBUG] ============================================');
        console.log('🖱️ [CURSOR DEBUG] Removing cursor for user:', userId);
        
        const cursor = this.cursors.get(userId);
        console.log('🖱️ [CURSOR DEBUG] Cursor found in map?', !!cursor);
        
        if (cursor) {
            console.log('🖱️ [CURSOR DEBUG] Cursor element:', cursor);
            console.log('🖱️ [CURSOR DEBUG] Cursor parent:', cursor.parentElement);
            console.log('🖱️ [CURSOR DEBUG] Removing cursor from DOM...');
            
            cursor.remove();
            this.cursors.delete(userId);
            
            console.log('✅ [CURSOR DEBUG] Cursor removed successfully');
            console.log('🖱️ [CURSOR DEBUG] Remaining cursors:', this.cursors.size);
        } else {
            console.log('⚠️ [CURSOR DEBUG] No cursor found for user ID:', userId);
        }
        
        // Also remove viewport indicator
        if (this.viewportIndicators) {
            const viewport = this.viewportIndicators.get(userId);
            if (viewport) {
                console.log('👁️ [VIEWPORT DEBUG] Removing viewport indicator for user:', userId);
                viewport.remove();
                this.viewportIndicators.delete(userId);
                console.log('✅ [VIEWPORT DEBUG] Viewport indicator removed');
            }
        }
        
        console.log('🖱️ [CURSOR DEBUG] ============================================');
    }

    /**
     * Get color class for user
     * @param {Number} userId - User ID
     * @returns {String} Color class (user-1 through user-6)
     */
    getUserColorClass(userId) {
        console.log('🖱️ [CURSOR DEBUG] Getting color class for user:', userId);
        
        // Cycle through 6 color options
        const colorIndex = ((userId - 1) % 6) + 1;
        const colorClass = `user-${colorIndex}`;
        
        console.log('🖱️ [CURSOR DEBUG] Calculated color index:', colorIndex);
        console.log('🖱️ [CURSOR DEBUG] Color class:', colorClass);
        
        return colorClass;
    }

    /**
     * Throttled cursor update (called on mouse move)
     */
    throttledCursorUpdate(x, y) {
        console.log('🖱️ [CURSOR DEBUG] Throttled cursor update called');
        console.log('🖱️ [CURSOR DEBUG] Position: x=', x, 'y=', y);
        console.log('🖱️ [CURSOR DEBUG] Session ID:', this.sessionId);
        
        if (!this.sessionId) {
            console.log('⚠️ [CURSOR DEBUG] No session ID - not emitting cursor position');
            return; // Not in a session
        }
        
        const now = Date.now();
        const timeSinceLastUpdate = now - this.lastCursorUpdate;
        
        console.log('🖱️ [CURSOR DEBUG] Time since last update:', timeSinceLastUpdate, 'ms');
        console.log('🖱️ [CURSOR DEBUG] Throttle threshold:', this.config.cursorUpdateThrottle, 'ms');
        
        if (timeSinceLastUpdate < this.config.cursorUpdateThrottle) {
            console.log('🖱️ [CURSOR DEBUG] Update throttled (too soon)');
            return; // Throttle
        }
        
        this.lastCursorUpdate = now;
        
        // Get viewport information
        const viewport = this.getViewportInfo();
        
        const emitData = {
            session_id: this.sessionId,
            x: x,
            y: y,
            username: this.currentUser?.username || 'Unknown',
            user_id: this.currentUser?.id,
            viewport: viewport // Add viewport data
        };
        
        console.log('✅ [CURSOR DEBUG] Emitting cursor position to server:');
        console.log('🖱️ [CURSOR DEBUG] Emit data:', emitData);
        
        // Emit cursor position to other users
        this.socket.emit('update_cursor_position', emitData);
    }
    
    /**
     * Get current viewport information
     */
    getViewportInfo() {
        return {
            x: window.scrollX || window.pageXOffset,
            y: window.scrollY || window.pageYOffset,
            width: window.innerWidth,
            height: window.innerHeight,
            scrollWidth: document.documentElement.scrollWidth,
            scrollHeight: document.documentElement.scrollHeight
        };
    }

    /**
     * Clean up all cursors (when leaving session)
     */
    cleanupCursors() {
        console.log('🧹 Cleaning up all cursors');
        
        for (const [userId, cursor] of this.cursors.entries()) {
            cursor.remove();
        }
        
        this.cursors.clear();
        
        // Also clean up viewport indicators
        if (this.viewportIndicators) {
            console.log('🧹 Cleaning up all viewport indicators');
            for (const [userId, viewport] of this.viewportIndicators.entries()) {
                viewport.remove();
            }
            this.viewportIndicators.clear();
        }
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
        console.log('🧹 [DEBUG] Cleaning up collaboration system');
        
        this.stopHeartbeat();
        this.stopUserVerification();
        
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
        
        console.log('✅ [DEBUG] Collaboration cleanup complete');
    }
}

// ===== GLOBAL INTEGRATION =====

// Create global instance
window.collaborationRealTime = new CollaborationRealTime();

// ===== DEBUG CONSOLE COMMANDS =====

// Debug: Check current user info
window.debugUserInfo = function() {
    console.log('🔍 [DEBUG] ============= USER INFO DEBUG =============');
    console.log('🔍 [DEBUG] window.currentUser:', window.currentUser);
    console.log('🔍 [DEBUG] window.sessionUser:', window.sessionUser);
    console.log('🔍 [DEBUG] collaborationRealTime.currentUser:', window.collaborationRealTime.currentUser);
    
    const sessionDataElement = document.getElementById('session-data');
    if (sessionDataElement) {
        console.log('🔍 [DEBUG] session-data element found:');
        console.log('🔍 [DEBUG]   - userId:', sessionDataElement.dataset.userId);
        console.log('🔍 [DEBUG]   - username:', sessionDataElement.dataset.username);
    } else {
        console.error('❌ [DEBUG] session-data element NOT found');
    }
    
    const userElements = document.querySelectorAll('[data-user-id]');
    console.log('🔍 [DEBUG] Found', userElements.length, 'elements with [data-user-id]');
    userElements.forEach((el, idx) => {
        console.log(`🔍 [DEBUG] Element ${idx}:`, {
            id: el.id,
            userId: el.dataset.userId,
            username: el.dataset.username,
            element: el
        });
    });
    
    console.log('🔍 [DEBUG] ==========================================');
};

// Debug: Refresh current user
window.debugRefreshUser = function() {
    console.log('🔄 [DEBUG] Manually refreshing current user...');
    window.collaborationRealTime.loadCurrentUser();
    console.log('✅ [DEBUG] User refreshed. New value:', window.collaborationRealTime.currentUser);
};

// Debug: Check chat history
window.debugChatHistory = function() {
    console.log('🔍 [DEBUG] ============= CHAT HISTORY DEBUG =============');
    console.log('🔍 [DEBUG] Total messages:', window.collaborationRealTime.chatHistory.length);
    window.collaborationRealTime.chatHistory.forEach((msg, idx) => {
        console.log(`🔍 [DEBUG] Message ${idx}:`, {
            user_id: msg.user_id,
            username: msg.username,
            message: msg.message || msg.content,
            timestamp: msg.timestamp,
            isOwn: String(msg.user_id) === String(window.collaborationRealTime.currentUser?.id)
        });
    });
    console.log('🔍 [DEBUG] ==========================================');
};

// Debug: Force user ID comparison
window.debugUserComparison = function(messageUserId) {
    const currentUserId = window.collaborationRealTime.currentUser?.id;
    console.log('🔍 [DEBUG] ============= USER ID COMPARISON =============');
    console.log('🔍 [DEBUG] Current User ID:', currentUserId, '(type:', typeof currentUserId, ')');
    console.log('🔍 [DEBUG] Message User ID:', messageUserId, '(type:', typeof messageUserId, ')');
    console.log('🔍 [DEBUG] String Current:', String(currentUserId));
    console.log('🔍 [DEBUG] String Message:', String(messageUserId));
    console.log('🔍 [DEBUG] Match (===):', currentUserId === messageUserId);
    console.log('🔍 [DEBUG] Match (String):', String(currentUserId) === String(messageUserId));
    console.log('🔍 [DEBUG] ==========================================');
};

// Debug: Test send message
window.debugSendTestMessage = function(text = 'Test message') {
    console.log('🔍 [DEBUG] Sending test message:', text);
    window.collaborationRealTime.sendChatMessage(text);
};

// Expose to console
console.log('✅ [DEBUG] Debug console commands available:');
console.log('  - debugUserInfo(): Check current user information');
console.log('  - debugRefreshUser(): Refresh current user from DOM');
console.log('  - debugChatHistory(): View all chat messages');
console.log('  - debugUserComparison(messageUserId): Compare user IDs');
console.log('  - debugSendTestMessage(text): Send a test message');

// ===== END DEBUG CONSOLE COMMANDS =====

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
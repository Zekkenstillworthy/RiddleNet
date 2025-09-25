/**
 * Real-time Collaboration System for RiddleNet
 * Handles real-time collaboration for both admin class content management and student simulations
 */

class CollaborationRealTime {
    constructor(options = {}) {
        this.socket = io();
        this.sessionType = options.sessionType || 'simulation'; // 'admin_class_content' or 'simulation'
        this.sessionId = options.sessionId || null;
        this.currentUser = options.currentUser || null;
        this.isInitialized = false;
        this.collaborators = new Map();
        this.isCollaborationEnabled = options.enableCollaboration !== false;
        
        // UI elements
        this.collaborationPanel = null;
        this.chatContainer = null;
        this.usersList = null;
        
        // Callbacks
        this.onContentUpdate = options.onContentUpdate || (() => {});
        this.onUserJoined = options.onUserJoined || (() => {});
        this.onUserLeft = options.onUserLeft || (() => {});
        
        if (this.isCollaborationEnabled) {
            this.init();
        }
    }
    
    init() {
        if (this.isInitialized) return;
        
        console.log('🤝 Initializing real-time collaboration system...');
        
        this.setupSocketEvents();
        this.createCollaborationUI();
        this.joinCollaborationSession();
        
        // Auto-leave on page unload
        window.addEventListener('beforeunload', () => {
            this.leaveCollaborationSession();
        });
        
        this.isInitialized = true;
        console.log('✅ Collaboration system initialized');
    }
    
    setupSocketEvents() {
        // Join/leave events
        this.socket.on('collaboration_session_joined', (data) => {
            console.log('👥 Joined collaboration session:', data);
            this.updateCollaboratorsList(data.current_users);
            this.showNotification(`You joined the collaboration session`, 'info');
        });
        
        this.socket.on('user_joined_collaboration', (data) => {
            console.log('👤 User joined:', data.user.username);
            this.addCollaborator(data.user);
            this.showNotification(`${data.user.username} joined the session`, 'info');
            this.onUserJoined(data.user);
        });
        
        this.socket.on('user_left_collaboration', (data) => {
            console.log('👋 User left:', data.user.username);
            this.removeCollaborator(data.user.user_id);
            this.showNotification(`${data.user.username} left the session`, 'warning');
            this.onUserLeft(data.user);
        });
        
        // Content synchronization
        this.socket.on('collaboration_content_update', (data) => {
            console.log('📝 Content update from:', data.username);
            this.handleContentUpdate(data);
        });
        
        this.socket.on('collaboration_simulation_state_update', (data) => {
            console.log('🔄 Simulation state update from:', data.username);
            this.handleSimulationStateUpdate(data);
        });
        
        this.socket.on('collaboration_admin_content_update', (data) => {
            console.log('📋 Admin content update from:', data.username);
            this.handleAdminContentUpdate(data);
        });
        
        // Chat messages
        this.socket.on('collaboration_chat_message', (data) => {
            console.log('💬 Chat message from:', data.username);
            this.displayChatMessage(data);
        });
        
        // Cursor and selection tracking
        this.socket.on('collaboration_cursor_update', (data) => {
            this.updateCollaboratorCursor(data);
        });
        
        this.socket.on('collaboration_selection_update', (data) => {
            this.updateCollaboratorSelection(data);
        });
        
        // Typing indicators
        this.socket.on('collaboration_typing_indicator', (data) => {
            this.updateTypingIndicator(data);
        });
        
        // Error handling
        this.socket.on('collaboration_error', (data) => {
            console.error('❌ Collaboration error:', data.error);
            this.showNotification(`Collaboration error: ${data.error}`, 'error');
        });
    }
    
    createCollaborationUI() {
        // Create collaboration panel
        this.collaborationPanel = document.createElement('div');
        this.collaborationPanel.className = 'collaboration-panel';
        this.collaborationPanel.innerHTML = `
            <div class="collaboration-header">
                <h4><i class="fas fa-users"></i> Live Collaboration</h4>
                <button class="collapse-btn" onclick="this.closest('.collaboration-panel').classList.toggle('collapsed')">
                    <i class="fas fa-chevron-down"></i>
                </button>
            </div>
            
            <div class="collaboration-content">
                <div class="collaborators-section">
                    <h5>Active Users (<span class="user-count">0</span>)</h5>
                    <div class="users-list"></div>
                </div>
                
                <div class="chat-section">
                    <h5>Team Chat</h5>
                    <div class="chat-messages"></div>
                    <div class="chat-input-container">
                        <input type="text" class="chat-input" placeholder="Type a message..." maxlength="500">
                        <button class="send-message-btn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(this.collaborationPanel);
        
        // Get references
        this.usersList = this.collaborationPanel.querySelector('.users-list');
        this.chatContainer = this.collaborationPanel.querySelector('.chat-messages');
        this.chatInput = this.collaborationPanel.querySelector('.chat-input');
        this.sendBtn = this.collaborationPanel.querySelector('.send-message-btn');
        this.userCount = this.collaborationPanel.querySelector('.user-count');
        
        // Setup chat functionality
        this.setupChatHandlers();
        
        // Add CSS
        this.addCollaborationCSS();
    }
    
    addCollaborationCSS() {
        const style = document.createElement('style');
        style.textContent = `
            .collaboration-panel {
                position: fixed;
                top: 80px;
                right: 20px;
                width: 350px;
                max-height: 70vh;
                background: var(--glass-bg, rgba(15, 23, 42, 0.95));
                border: 1px solid var(--glass-border, rgba(59, 130, 246, 0.3));
                border-radius: 16px;
                backdrop-filter: blur(10px);
                z-index: 1000;
                transition: all 0.3s ease;
                overflow: hidden;
            }
            
            .collaboration-panel.collapsed .collaboration-content {
                display: none;
            }
            
            .collaboration-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
                background: var(--primary-color, #0F172A);
            }
            
            .collaboration-header h4 {
                color: var(--text-primary, #F8FAFC);
                margin: 0;
                font-size: 14px;
                font-weight: 600;
            }
            
            .collaboration-header h4 i {
                color: var(--accent-color, #3B82F6);
                margin-right: 8px;
            }
            
            .collapse-btn {
                background: none;
                border: none;
                color: var(--text-secondary, #CBD5E1);
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s;
            }
            
            .collapse-btn:hover {
                background: var(--surface-hover, rgba(255, 255, 255, 0.1));
                color: var(--accent-color, #3B82F6);
            }
            
            .collaboration-content {
                padding: 20px;
                max-height: calc(70vh - 60px);
                overflow-y: auto;
            }
            
            .collaborators-section, .chat-section {
                margin-bottom: 20px;
            }
            
            .collaborators-section h5, .chat-section h5 {
                color: var(--text-primary, #F8FAFC);
                margin: 0 0 10px 0;
                font-size: 12px;
                text-transform: uppercase;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            
            .user-item {
                display: flex;
                align-items: center;
                padding: 8px 12px;
                margin: 4px 0;
                background: var(--surface, rgba(30, 41, 59, 0.5));
                border-radius: 8px;
                border-left: 3px solid var(--accent-color, #3B82F6);
                position: relative;
            }
            
            .user-item.admin {
                border-left-color: var(--warning-color, #F59E0B);
            }
            
            .user-item.current-user {
                background: var(--accent-color, #3B82F6);
                color: white;
            }
            
            .user-avatar {
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background: var(--accent-color, #3B82F6);
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 8px;
                font-size: 10px;
                font-weight: 600;
            }
            
            .user-info {
                flex: 1;
                min-width: 0;
            }
            
            .user-name {
                font-weight: 500;
                font-size: 13px;
                color: var(--text-primary, #F8FAFC);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .user-status {
                font-size: 10px;
                color: var(--text-muted, #64748B);
                margin-top: 2px;
            }
            
            .typing-indicator {
                position: absolute;
                right: 8px;
                top: 50%;
                transform: translateY(-50%);
                color: var(--success-color, #10B981);
                font-size: 10px;
                animation: pulse 1.5s infinite;
            }
            
            .chat-messages {
                max-height: 200px;
                overflow-y: auto;
                background: var(--surface, rgba(30, 41, 59, 0.3));
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 12px;
            }
            
            .chat-message {
                margin-bottom: 12px;
                padding: 8px 12px;
                background: var(--glass-bg-light, rgba(255, 255, 255, 0.05));
                border-radius: 8px;
                border-left: 3px solid var(--accent-color, #3B82F6);
            }
            
            .chat-message.own {
                background: var(--accent-color, #3B82F6);
                color: white;
                margin-left: 20px;
                border-left-color: white;
            }
            
            .chat-message.admin {
                border-left-color: var(--warning-color, #F59E0B);
            }
            
            .message-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 4px;
            }
            
            .message-author {
                font-weight: 600;
                font-size: 11px;
                color: var(--text-secondary, #CBD5E1);
            }
            
            .message-time {
                font-size: 10px;
                color: var(--text-muted, #64748B);
            }
            
            .message-content {
                font-size: 13px;
                line-height: 1.4;
                color: var(--text-primary, #F8FAFC);
                word-wrap: break-word;
            }
            
            .chat-input-container {
                display: flex;
                gap: 8px;
            }
            
            .chat-input {
                flex: 1;
                padding: 8px 12px;
                background: var(--surface, rgba(30, 41, 59, 0.5));
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
                border-radius: 8px;
                color: var(--text-primary, #F8FAFC);
                font-size: 13px;
                outline: none;
            }
            
            .chat-input:focus {
                border-color: var(--accent-color, #3B82F6);
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
            }
            
            .send-message-btn {
                padding: 8px 12px;
                background: var(--accent-color, #3B82F6);
                border: none;
                border-radius: 8px;
                color: white;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .send-message-btn:hover {
                background: var(--cyber-glow, #00D9FF);
                transform: translateY(-1px);
            }
            
            .collaboration-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 16px;
                border-radius: 8px;
                color: white;
                font-size: 13px;
                z-index: 1001;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
            }
            
            .collaboration-notification.show {
                opacity: 1;
                transform: translateX(0);
            }
            
            .collaboration-notification.info {
                background: var(--accent-color, #3B82F6);
            }
            
            .collaboration-notification.warning {
                background: var(--warning-color, #F59E0B);
            }
            
            .collaboration-notification.error {
                background: var(--danger-color, #EF4444);
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            /* Scrollbar styling */
            .chat-messages::-webkit-scrollbar,
            .collaboration-content::-webkit-scrollbar {
                width: 4px;
            }
            
            .chat-messages::-webkit-scrollbar-track,
            .collaboration-content::-webkit-scrollbar-track {
                background: var(--surface, rgba(30, 41, 59, 0.3));
                border-radius: 2px;
            }
            
            .chat-messages::-webkit-scrollbar-thumb,
            .collaboration-content::-webkit-scrollbar-thumb {
                background: var(--accent-color, #3B82F6);
                border-radius: 2px;
            }
        `;
        document.head.appendChild(style);
    }
    
    setupChatHandlers() {
        const sendMessage = () => {
            const message = this.chatInput.value.trim();
            if (message) {
                this.sendChatMessage(message);
                this.chatInput.value = '';
            }
        };
        
        this.sendBtn.addEventListener('click', sendMessage);
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Typing indicators
        let typingTimer;
        this.chatInput.addEventListener('input', () => {
            this.sendTypingIndicator(true, 'chat');
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                this.sendTypingIndicator(false, 'chat');
            }, 1000);
        });
    }
    
    joinCollaborationSession() {
        if (!this.sessionId) return;
        
        this.socket.emit('join_collaboration_session', {
            session_type: this.sessionType,
            session_id: this.sessionId,
            user_info: this.currentUser
        });
    }
    
    leaveCollaborationSession() {
        if (!this.sessionId) return;
        
        this.socket.emit('leave_collaboration_session', {
            session_type: this.sessionType,
            session_id: this.sessionId
        });
    }
    
    updateCollaboratorsList(users) {
        this.usersList.innerHTML = '';
        this.userCount.textContent = users.length;
        
        users.forEach(user => {
            this.addCollaboratorToList(user);
        });
    }
    
    addCollaborator(user) {
        this.collaborators.set(user.user_id, user);
        this.addCollaboratorToList(user);
        this.userCount.textContent = this.collaborators.size + 1; // +1 for current user
    }
    
    removeCollaborator(userId) {
        this.collaborators.delete(userId);
        const userElement = this.usersList.querySelector(`[data-user-id="${userId}"]`);
        if (userElement) {
            userElement.remove();
        }
        this.userCount.textContent = this.collaborators.size + 1;
    }
    
    addCollaboratorToList(user) {
        const userElement = document.createElement('div');
        userElement.className = `user-item ${user.is_admin ? 'admin' : ''}`;
        userElement.setAttribute('data-user-id', user.user_id);
        
        const initials = user.username.substring(0, 2).toUpperCase();
        
        userElement.innerHTML = `
            <div class="user-avatar">${initials}</div>
            <div class="user-info">
                <div class="user-name">${user.username} ${user.is_admin ? '(Admin)' : ''}</div>
                <div class="user-status">Online</div>
            </div>
            <div class="typing-indicator" style="display: none;">
                <i class="fas fa-circle"></i>
            </div>
        `;
        
        this.usersList.appendChild(userElement);
    }
    
    sendChatMessage(message) {
        this.socket.emit('collaboration_chat_message', {
            session_type: this.sessionType,
            session_id: this.sessionId,
            message: message
        });
    }
    
    displayChatMessage(messageData) {
        const messageElement = document.createElement('div');
        const isOwn = this.currentUser && messageData.user_id === this.currentUser.id;
        
        messageElement.className = `chat-message ${isOwn ? 'own' : ''} ${messageData.is_admin ? 'admin' : ''}`;
        
        const time = new Date(messageData.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageElement.innerHTML = `
            <div class="message-header">
                <span class="message-author">${messageData.username}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">${this.escapeHtml(messageData.message)}</div>
        `;
        
        this.chatContainer.appendChild(messageElement);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    sendTypingIndicator(isTyping, fieldId) {
        this.socket.emit('collaboration_typing_indicator', {
            session_type: this.sessionType,
            session_id: this.sessionId,
            is_typing: isTyping,
            field_id: fieldId
        });
    }
    
    updateTypingIndicator(data) {
        const userElement = this.usersList.querySelector(`[data-user-id="${data.user_id}"]`);
        if (userElement) {
            const indicator = userElement.querySelector('.typing-indicator');
            indicator.style.display = data.is_typing ? 'block' : 'none';
        }
    }
    
    handleContentUpdate(data) {
        console.log('📝 Processing content update:', data);
        this.onContentUpdate(data);
    }
    
    handleSimulationStateUpdate(data) {
        console.log('🔄 Processing simulation state update:', data);
        if (this.sessionType === 'simulation' && window.networkSimulation) {
            // Update simulation state based on the received data
            if (data.state_data.deviceStates) {
                window.networkSimulation.updateDeviceStates(data.state_data.deviceStates);
            }
            if (data.state_data.topology) {
                window.networkSimulation.updateTopology(data.state_data.topology);
            }
        }
    }
    
    handleAdminContentUpdate(data) {
        console.log('📋 Processing admin content update:', data);
        if (this.sessionType === 'admin_class_content') {
            // Refresh content based on update type
            switch (data.sync_type) {
                case 'assignments':
                    this.refreshAssignments(data.content_data);
                    break;
                case 'modules':
                    this.refreshModules(data.content_data);
                    break;
                case 'simulations':
                    this.refreshSimulations(data.content_data);
                    break;
                default:
                    this.refreshAllContent(data.content_data);
            }
        }
    }
    
    syncContentChange(changeData) {
        this.socket.emit('collaboration_content_change', {
            session_type: this.sessionType,
            session_id: this.sessionId,
            change_data: changeData
        });
    }
    
    syncSimulationState(stateData, syncType = 'full') {
        if (this.sessionType === 'simulation') {
            this.socket.emit('collaboration_simulation_state_sync', {
                simulation_id: this.sessionId,
                state_data: stateData,
                sync_type: syncType
            });
        }
    }
    
    syncAdminContent(contentData, syncType = 'full') {
        if (this.sessionType === 'admin_class_content') {
            this.socket.emit('collaboration_admin_content_sync', {
                class_id: this.sessionId,
                content_data: contentData,
                sync_type: syncType
            });
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `collaboration-notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    }
    
    refreshAssignments(data) {
        // Implement assignment refresh logic
        if (window.location.pathname.includes('class-content-selector')) {
            // Refresh assignments section
            console.log('🔄 Refreshing assignments section');
        }
    }
    
    refreshModules(data) {
        // Implement modules refresh logic
        console.log('🔄 Refreshing modules section');
    }
    
    refreshSimulations(data) {
        // Implement simulations refresh logic  
        console.log('🔄 Refreshing simulations section');
    }
    
    refreshAllContent(data) {
        // Implement full content refresh logic
        console.log('🔄 Refreshing all content');
        if (typeof window.refreshClassContent === 'function') {
            window.refreshClassContent();
        }
    }
    
    updateCollaboratorCursor(data) {
        // Implement cursor tracking if needed
        console.log('👆 Cursor update from:', data.username);
    }
    
    updateCollaboratorSelection(data) {
        // Implement selection tracking if needed
        console.log('📋 Selection update from:', data.username);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    destroy() {
        this.leaveCollaborationSession();
        if (this.collaborationPanel) {
            this.collaborationPanel.remove();
        }
        this.isInitialized = false;
    }
}

// Global collaboration instance
window.CollaborationRealTime = CollaborationRealTime;

// Auto-initialize for specific pages
document.addEventListener('DOMContentLoaded', () => {
    // Auto-initialize for simulation pages (only for non-admin users)
    if (window.location.pathname.includes('/dynamic/simulation/')) {
        const simulationId = window.location.pathname.match(/\/dynamic\/simulation\/(\d+)/)?.[1];
        if (simulationId && window.currentUser) {
            // Check if the current user is an admin - if so, disable collaboration panel
            const isAdmin = window.currentUser?.is_admin || 
                            window.currentUser?.user_type === 'admin' || 
                            window.currentUser?.role === 'admin' ||
                            window.location.pathname.includes('/admin/');
            
            if (!isAdmin) {
                window.collaborationSystem = new CollaborationRealTime({
                    sessionType: 'simulation',
                    sessionId: simulationId,
                    currentUser: window.currentUser,
                    enableCollaboration: true
                });
            } else {
                console.log('🔐 Admin user detected - collaboration panel disabled for admins');
            }
        }
    }
    
    // DISABLED: Admin collaboration panel removed
    // Admins should manage collaboration sessions, not join them
    /*
    if (window.location.pathname.includes('/admin/class-content-selector')) {
        const classId = new URLSearchParams(window.location.search).get('class_id');
        if (classId && window.currentUser) {
            window.collaborationSystem = new CollaborationRealTime({
                sessionType: 'admin_class_content',
                sessionId: classId,
                currentUser: window.currentUser,
                enableCollaboration: true
            });
        }
    }
    */
});

// Enhanced Admin WebSocket Integration System
// Provides real-time functionality across all admin pages

class AdminWebSocketManager {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.currentPage = this.detectPage();
        this.adminRooms = new Set();
        this.eventHandlers = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.init();
    }

    init() {
        console.log('🔌 Initializing Admin WebSocket Manager...');
        
        // Check if WebSocket is disabled - but allow admin override
        if (window.DISABLE_WEBSOCKET && !this.shouldEnableForAdmin()) {
            console.log('🚫 WebSocket disabled for admin interface');
            this.showWebSocketStatus('disabled', 'WebSocket functionality is disabled');
            return;
        }

        // Override disable flag for admin pages when ENABLE_ADMIN_WEBSOCKET is set
        if (this.shouldEnableForAdmin() || window.ENABLE_ADMIN_WEBSOCKET) {
            console.log('🔓 Enabling WebSocket for admin interface (overriding DISABLE_WEBSOCKET)');
            window.DISABLE_WEBSOCKET = false;
            window.ENABLE_ADMIN_WEBSOCKET = true;
        }

        this.initializeSocket();
        this.setupAdminEventHandlers();
        this.joinAdminRooms();
        this.setupPageSpecificEvents();
        this.setupUIIndicators();
    }

    shouldEnableForAdmin() {
        // Enable WebSocket for admin pages regardless of global flag
        const isAdminPage = window.location.pathname.includes('/admin');
        const isAdminUser = document.body.classList.contains('admin-interface') || 
                           document.querySelector('.admin-header') !== null ||
                           document.querySelector('[data-admin="true"]') !== null;
        
        // Check if we have admin authentication indicators
        const hasAdminAuth = window.currentUserRole === 'admin' || 
                            window.isAdmin === true ||
                            localStorage.getItem('userRole') === 'admin';
        
        console.log('🔍 Admin check:', { isAdminPage, isAdminUser, hasAdminAuth });
        
        return isAdminPage || isAdminUser || hasAdminAuth;
    }

    detectPage() {
        const path = window.location.pathname;
        if (path.includes('dashboard')) return 'dashboard';
        if (path.includes('class-content') || path.includes('module')) return 'content-management';
        if (path.includes('simulation-builder')) return 'simulation-builder';
        if (path.includes('user-management')) return 'user-management';
        if (path.includes('notification')) return 'notifications';
        if (path.includes('analytics')) return 'analytics';
        if (path.includes('websocket')) return 'websocket-debug';
        return 'general-admin';
    }

    initializeSocket() {
        try {
            // Use global socketClient if available, otherwise create new connection
            if (window.socketClient && window.socketClient.socket) {
                this.socket = window.socketClient.socket;
                this.connected = window.socketClient.connected;
                console.log('🔗 Using existing global socket connection');
            } else {
                // Create new socket connection for admin
                this.socket = io({
                    transports: ['websocket', 'polling'],
                    withCredentials: true,
                    reconnection: true,
                    reconnectionDelay: 2000,
                    reconnectionDelayMax: 10000,
                    timeout: 20000,
                    auth: {
                        userType: 'admin',
                        page: this.currentPage,
                        timestamp: Date.now()
                    }
                });
                console.log('🆕 Created new admin socket connection');
            }

            this.setupConnectionHandlers();
        } catch (error) {
            console.error('❌ Failed to initialize admin WebSocket:', error);
            this.showWebSocketStatus('error', 'Failed to initialize WebSocket connection');
        }
    }

    setupConnectionHandlers() {
        this.socket.on('connect', () => {
            console.log('✅ Admin WebSocket connected');
            this.connected = true;
            this.reconnectAttempts = 0;
            this.showWebSocketStatus('connected', 'Real-time features active');
            this.joinAdminRooms();
            this.emitAdminPresence();
        });

        this.socket.on('disconnect', (reason) => {
            console.log('🔌 Admin WebSocket disconnected:', reason);
            this.connected = false;
            this.showWebSocketStatus('disconnected', `Disconnected: ${reason}`);
        });

        this.socket.on('connect_error', (error) => {
            console.error('❌ Admin WebSocket connection error:', error);
            this.reconnectAttempts++;
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.showWebSocketStatus('error', 'Connection failed after multiple attempts');
            }
        });

        this.socket.on('reconnect', () => {
            console.log('🔄 Admin WebSocket reconnected');
            this.showWebSocketStatus('connected', 'Reconnected successfully');
            this.joinAdminRooms();
        });
    }

    setupAdminEventHandlers() {
        // Global admin events
        this.socket.on('admin_notification', (data) => {
            this.handleAdminNotification(data);
        });

        this.socket.on('user_activity_update', (data) => {
            this.handleUserActivityUpdate(data);
        });

        this.socket.on('system_alert', (data) => {
            this.handleSystemAlert(data);
        });

        this.socket.on('admin_broadcast', (data) => {
            this.handleAdminBroadcast(data);
        });

        // Content management events
        this.socket.on('content_updated', (data) => {
            this.handleContentUpdate(data);
        });

        this.socket.on('student_progress_update', (data) => {
            this.handleStudentProgressUpdate(data);
        });

        this.socket.on('assignment_submitted', (data) => {
            this.handleAssignmentSubmission(data);
        });

        // Class management events
        this.socket.on('student_joined_class', (data) => {
            this.handleStudentJoinedClass(data);
        });

        this.socket.on('student_left_class', (data) => {
            this.handleStudentLeftClass(data);
        });

        this.socket.on('class_activity_update', (data) => {
            this.handleClassActivityUpdate(data);
        });

        // Real-time collaboration events
        this.socket.on('collaboration_started', (data) => {
            this.handleCollaborationStarted(data);
        });

        this.socket.on('collaboration_ended', (data) => {
            this.handleCollaborationEnded(data);
        });

        // Module and lesson events
        this.socket.on('module_created', (data) => {
            this.handleModuleCreated(data);
        });

        this.socket.on('module_updated', (data) => {
            this.handleModuleUpdated(data);
        });

        this.socket.on('module_deleted', (data) => {
            this.handleModuleDeleted(data);
        });

        this.socket.on('lesson_completed', (data) => {
            this.handleLessonCompleted(data);
        });

        // Simulation events
        this.socket.on('simulation_started', (data) => {
            this.handleSimulationStarted(data);
        });

        this.socket.on('simulation_completed', (data) => {
            this.handleSimulationCompleted(data);
        });

        this.socket.on('topology_submitted', (data) => {
            this.handleTopologySubmitted(data);
        });

        // Analytics and performance events
        this.socket.on('performance_stats_update', (data) => {
            this.handlePerformanceStatsUpdate(data);
        });

        this.socket.on('server_health_update', (data) => {
            this.handleServerHealthUpdate(data);
        });
    }

    joinAdminRooms() {
        if (!this.connected) return;

        // Join main admin room
        this.socket.emit('join_admin_room');
        this.adminRooms.add('admin_room');

        // Join page-specific rooms
        switch (this.currentPage) {
            case 'dashboard':
                this.socket.emit('join_admin_dashboard');
                this.adminRooms.add('admin_dashboard');
                break;
            case 'content-management':
                this.socket.emit('join_module_builder');
                this.adminRooms.add('module_builder');
                break;
            case 'user-management':
                this.socket.emit('join_user_management');
                this.adminRooms.add('user_management');
                break;
            case 'notifications':
                this.socket.emit('join_notification_center');
                this.adminRooms.add('notification_center');
                break;
            case 'analytics':
                this.socket.emit('join_analytics_room');
                this.adminRooms.add('analytics_room');
                break;
            case 'websocket-debug':
                this.socket.emit('join_admin_collaboration_monitoring');
                this.adminRooms.add('admin_collaboration_monitoring');
                break;
        }

        console.log(`🏠 Joined admin rooms:`, Array.from(this.adminRooms));
    }

    setupPageSpecificEvents() {
        switch (this.currentPage) {
            case 'dashboard':
                this.setupDashboardEvents();
                break;
            case 'content-management':
                this.setupContentManagementEvents();
                break;
            case 'simulation-builder':
                this.setupSimulationBuilderEvents();
                break;
            case 'user-management':
                this.setupUserManagementEvents();
                break;
            case 'notifications':
                this.setupNotificationEvents();
                break;
            case 'analytics':
                this.setupAnalyticsEvents();
                break;
            case 'websocket-debug':
                this.setupWebSocketDebugEvents();
                break;
        }
    }

    setupDashboardEvents() {
        // Real-time dashboard updates
        this.socket.on('dashboard_stats_update', (data) => {
            this.updateDashboardStats(data);
        });

        this.socket.on('active_users_update', (data) => {
            this.updateActiveUsers(data);
        });

        this.socket.on('recent_activity_update', (data) => {
            this.addActivityToFeed(data);
        });
    }

    setupContentManagementEvents() {
        // Content creation and editing
        this.socket.on('content_auto_saved', (data) => {
            this.showAutoSaveIndicator(data);
        });

        this.socket.on('concurrent_edit_warning', (data) => {
            this.showConcurrentEditWarning(data);
        });

        this.socket.on('content_published', (data) => {
            this.handleContentPublished(data);
        });
    }

    setupSimulationBuilderEvents() {
        // Real-time simulation building
        this.socket.on('simulation_auto_saved', (data) => {
            this.showSimulationAutoSave(data);
        });

        this.socket.on('simulation_validated', (data) => {
            this.showSimulationValidation(data);
        });

        this.socket.on('component_library_updated', (data) => {
            this.updateComponentLibrary(data);
        });
    }

    setupUserManagementEvents() {
        // User activity monitoring
        this.socket.on('user_login', (data) => {
            this.handleUserLogin(data);
        });

        this.socket.on('user_logout', (data) => {
            this.handleUserLogout(data);
        });

        this.socket.on('user_progress_milestone', (data) => {
            this.handleProgressMilestone(data);
        });
    }

    setupNotificationEvents() {
        // Notification management
        this.socket.on('notification_delivered', (data) => {
            this.updateNotificationStatus(data);
        });

        this.socket.on('notification_read', (data) => {
            this.markNotificationRead(data);
        });

        this.socket.on('notification_stats_update', (data) => {
            this.updateNotificationStats(data);
        });
    }

    setupAnalyticsEvents() {
        // Real-time analytics
        this.socket.on('analytics_data_update', (data) => {
            this.updateAnalyticsCharts(data);
        });

        this.socket.on('performance_alert', (data) => {
            this.showPerformanceAlert(data);
        });
    }

    setupWebSocketDebugEvents() {
        // WebSocket debugging and monitoring
        this.socket.on('websocket_stats_update', (data) => {
            this.updateWebSocketStats(data);
        });

        this.socket.on('connection_diagnostic', (data) => {
            this.showConnectionDiagnostic(data);
        });
    }

    // Event Handlers
    handleAdminNotification(data) {
        console.log('📢 Admin notification:', data);
        this.showNotificationToast(data.title, data.message, data.type || 'info');
        
        // Update notification counter if element exists
        this.updateNotificationCounter();
    }

    handleUserActivityUpdate(data) {
        console.log('👤 User activity update:', data);
        
        // Update user status indicators
        const userElement = document.querySelector(`[data-user-id="${data.user_id}"]`);
        if (userElement) {
            this.updateUserStatus(userElement, data.status);
        }
    }

    handleSystemAlert(data) {
        console.log('🚨 System alert:', data);
        this.showSystemAlert(data.title, data.message, data.severity);
    }

    handleAdminBroadcast(data) {
        console.log('📡 Admin broadcast:', data);
        this.showBroadcastMessage(data);
    }

    handleContentUpdate(data) {
        console.log('📝 Content updated:', data);
        
        // Refresh content if on relevant page
        if (this.currentPage === 'content-management') {
            this.refreshContentList(data.class_id);
        }
    }

    handleStudentProgressUpdate(data) {
        console.log('📊 Student progress update:', data);
        
        // Update progress indicators
        this.updateProgressIndicators(data);
    }

    handleAssignmentSubmission(data) {
        console.log('📋 Assignment submitted:', data);
        
        // Show notification and update counters
        this.showNotificationToast(
            'New Submission',
            `${data.student_name} submitted ${data.assignment_title}`,
            'success'
        );
        
        this.updateSubmissionCounter();
    }

    handleStudentJoinedClass(data) {
        console.log('🎓 Student joined class:', data);
        
        // Update class roster if viewing that class
        if (this.isViewingClass(data.class_id)) {
            this.addStudentToRoster(data);
        }
        
        this.showNotificationToast(
            'Student Joined',
            `${data.student_name} joined ${data.class_name}`,
            'success'
        );
    }

    handleStudentLeftClass(data) {
        console.log('👋 Student left class:', data);
        
        // Update class roster
        if (this.isViewingClass(data.class_id)) {
            this.removeStudentFromRoster(data);
        }
    }

    handleModuleCreated(data) {
        console.log('📚 Module created:', data);
        
        if (this.currentPage === 'content-management') {
            this.addModuleToList(data);
        }
        
        this.showNotificationToast(
            'Module Created',
            `New module "${data.module_name}" created`,
            'success'
        );
    }

    handleModuleUpdated(data) {
        console.log('📝 Module updated:', data);
        
        if (this.currentPage === 'content-management') {
            this.updateModuleInList(data);
        }
    }

    handleModuleDeleted(data) {
        console.log('🗑️ Module deleted:', data);
        
        if (this.currentPage === 'content-management') {
            this.removeModuleFromList(data);
        }
    }

    handleSimulationStarted(data) {
        console.log('🚀 Simulation started:', data);
        this.updateSimulationStats(data, 'started');
    }

    handleSimulationCompleted(data) {
        console.log('✅ Simulation completed:', data);
        this.updateSimulationStats(data, 'completed');
        
        this.showNotificationToast(
            'Simulation Complete',
            `${data.student_name} completed ${data.simulation_name}`,
            'success'
        );
    }

    // Utility Methods
    emitAdminPresence() {
        if (!this.connected) return;
        
        this.socket.emit('admin_presence', {
            page: this.currentPage,
            timestamp: Date.now(),
            user_agent: navigator.userAgent
        });
    }

    showWebSocketStatus(status, message) {
        // Create or update WebSocket status indicator
        let statusIndicator = document.getElementById('websocket-status');
        
        if (!statusIndicator) {
            statusIndicator = document.createElement('div');
            statusIndicator.id = 'websocket-status';
            statusIndicator.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                z-index: 10000;
                transition: all 0.3s ease;
                min-width: 150px;
                text-align: center;
            `;
            document.body.appendChild(statusIndicator);
        }

        const statusColors = {
            connected: '#10b981',
            disconnected: '#f59e0b',
            error: '#ef4444',
            disabled: '#6b7280'
        };

        statusIndicator.style.backgroundColor = statusColors[status] || '#6b7280';
        statusIndicator.style.color = '#ffffff';
        statusIndicator.textContent = message;

        // Auto-hide after success
        if (status === 'connected') {
            setTimeout(() => {
                statusIndicator.style.opacity = '0.7';
            }, 3000);
        }
    }

    showNotificationToast(title, message, type = 'info', duration = 5000) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'admin-websocket-toast';
        toast.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f4c75 100%);
            color: #ffffff;
            padding: 15px 20px;
            border-radius: 8px;
            border-left: 4px solid ${this.getTypeColor(type)};
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            z-index: 10001;
            animation: slideInRight 0.3s ease;
        `;

        toast.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px;">${title}</div>
            <div style="font-size: 14px; opacity: 0.9;">${message}</div>
            <button onclick="this.parentElement.remove()" style="
                position: absolute;
                top: 5px;
                right: 8px;
                background: none;
                border: none;
                color: #ffffff;
                font-size: 16px;
                cursor: pointer;
                opacity: 0.7;
            ">&times;</button>
        `;

        document.body.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    getTypeColor(type) {
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        return colors[type] || colors.info;
    }

    setupUIIndicators() {
        // Add CSS animations
        if (!document.getElementById('admin-websocket-animations')) {
            const style = document.createElement('style');
            style.id = 'admin-websocket-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
                
                .websocket-indicator {
                    position: relative;
                }
                
                .websocket-indicator::after {
                    content: '';
                    position: absolute;
                    top: -2px;
                    right: -2px;
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #10b981;
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Page-specific helper methods
    updateDashboardStats(data) {
        // Update dashboard statistics
        const elements = {
            activeUsers: document.getElementById('active-users-count'),
            totalClasses: document.getElementById('total-classes-count'),
            pendingSubmissions: document.getElementById('pending-submissions-count'),
            systemLoad: document.getElementById('system-load-indicator')
        };

        Object.entries(data).forEach(([key, value]) => {
            if (elements[key]) {
                elements[key].textContent = value;
            }
        });
    }

    updateActiveUsers(data) {
        const usersList = document.getElementById('active-users-list');
        if (usersList) {
            usersList.innerHTML = data.users.map(user => `
                <div class="user-item ${user.status}">
                    <span class="user-name">${user.name}</span>
                    <span class="user-status">${user.status}</span>
                </div>
            `).join('');
        }
    }

    addActivityToFeed(data) {
        const activityFeed = document.getElementById('activity-feed');
        if (activityFeed) {
            const activityItem = document.createElement('div');
            activityItem.className = 'activity-item';
            activityItem.innerHTML = `
                <div class="activity-time">${new Date(data.timestamp).toLocaleTimeString()}</div>
                <div class="activity-description">${data.description}</div>
                <div class="activity-user">${data.user}</div>
            `;
            activityFeed.insertBefore(activityItem, activityFeed.firstChild);
            
            // Keep only latest 50 items
            while (activityFeed.children.length > 50) {
                activityFeed.removeChild(activityFeed.lastChild);
            }
        }
    }

    isViewingClass(classId) {
        const currentClassId = this.getCurrentClassId();
        return currentClassId && currentClassId.toString() === classId.toString();
    }

    getCurrentClassId() {
        // Try to get class ID from URL, data attributes, or global variables
        const urlMatch = window.location.pathname.match(/class[\/\-](\d+)/);
        if (urlMatch) return urlMatch[1];
        
        const classSelector = document.getElementById('classSelector');
        if (classSelector) return classSelector.value;
        
        return window.currentClassId || null;
    }

    // Public API methods
    emit(event, data) {
        if (this.connected && this.socket) {
            this.socket.emit(event, data);
        } else {
            console.warn('Cannot emit event: WebSocket not connected');
        }
    }

    on(event, callback) {
        if (this.socket) {
            this.socket.on(event, callback);
        }
    }

    off(event, callback) {
        if (this.socket) {
            this.socket.off(event, callback);
        }
    }

    // Cleanup method
    destroy() {
        if (this.socket) {
            this.adminRooms.forEach(room => {
                this.socket.emit('leave_room', room);
            });
            
            if (this.socket !== window.socketClient?.socket) {
                this.socket.disconnect();
            }
        }
        
        // Remove UI indicators
        const statusIndicator = document.getElementById('websocket-status');
        if (statusIndicator) statusIndicator.remove();
        
        const toasts = document.querySelectorAll('.admin-websocket-toast');
        toasts.forEach(toast => toast.remove());
    }
}

// Initialize Admin WebSocket Manager
let adminWebSocketManager = null;

// Auto-initialize on admin pages
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on an admin page
    if (window.location.pathname.includes('/admin')) {
        // Wait a bit for other scripts to load
        setTimeout(() => {
            adminWebSocketManager = new AdminWebSocketManager();
            window.adminWebSocketManager = adminWebSocketManager;
            console.log('🔌 Admin WebSocket Manager initialized');
        }, 1000);
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (adminWebSocketManager) {
        adminWebSocketManager.destroy();
    }
});

// Export for global use
window.AdminWebSocketManager = AdminWebSocketManager;

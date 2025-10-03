// Enhanced Collaboration Management for Admin Activities
class CollaborationManager {
    constructor() {
        // Guard against multiple instances
        if (window.collaborationManagerInstance) {
            console.log('🔒 CollaborationManager already exists, returning existing instance');
            return window.collaborationManagerInstance;
        }
        
        console.log('🔧 Initializing new CollaborationManager...');
        this.collaborationSettings = new Map();
        this.activeCollaborations = new Map();
        this.isInitialized = false;
        
        // Store this instance globally
        window.collaborationManagerInstance = this;
        
        this.init();
    }

    init() {
        // Prevent double initialization
        if (this.isInitialized) {
            console.log('🔒 CollaborationManager already initialized, skipping');
            return;
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeCollaborationControls();
            this.loadExistingSettings();
        }, { once: true }); // Use once: true to prevent duplicate listeners
        
        this.isInitialized = true;
        console.log('✅ CollaborationManager initialized');
    }

    // Initialize collaboration controls for activities
    initializeCollaborationControls() {
        // Add collaboration toggles to assignment creation forms
        this.addCollaborationControls();
        
        // Add real-time collaboration monitoring
        this.setupCollaborationMonitoring();
    }

    addCollaborationControls() {
        // Find assignment and activity creation forms
        const forms = document.querySelectorAll('#createAssignmentForm, .activity-form, .simulation-form');
        
        forms.forEach(form => {
            this.addCollaborationSection(form);
        });
    }

    addCollaborationSection(form) {
        // Create collaboration settings section
        const collaborationSection = document.createElement('div');
        collaborationSection.className = 'collaboration-section';
        collaborationSection.innerHTML = `
            <div class="section-header">
                <h4><i class="fas fa-users"></i> Collaboration Settings</h4>
                <span class="help-icon" data-tooltip="Configure how students can work together on this activity" data-tooltip-position="top">?</span>
            </div>
            
            <div class="form-group">
                <label class="form-label">Collaboration Type</label>
                <select class="form-select collaboration-type" data-enhance="true">
                    <option value="individual" data-type="individual">Individual Work</option>
                    <option value="pairs" data-type="pairs">Pair Programming</option>
                    <option value="small-groups" data-type="small-groups">Small Groups (3-4)</option>
                    <option value="large-groups" data-type="large-groups">Large Groups (5+)</option>
                    <option value="class-wide" data-type="class-wide">Class-wide Collaboration</option>
                    <option value="simulation-teams" data-type="simulation-teams">Simulation Teams (Admin Managed)</option>
                </select>
            </div>
            
            <div class="collaboration-options" style="display: none;">
                <div class="form-group">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="allowRealTimeChat" checked>
                        <label class="form-check-label" for="allowRealTimeChat">
                            Enable Real-time Chat
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="allowScreenSharing">
                        <label class="form-check-label" for="allowScreenSharing">
                            Allow Screen Sharing
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="allowFileSharing" checked>
                        <label class="form-check-label" for="allowFileSharing">
                            Enable File Sharing
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="trackIndividualProgress" checked>
                        <label class="form-check-label" for="trackIndividualProgress">
                            Track Individual Contributions
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Max Group Size</label>
                    <input type="number" class="form-control" id="maxGroupSize" min="2" max="10" value="4">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Collaboration Duration (minutes)</label>
                    <input type="number" class="form-control" id="collaborationDuration" min="5" max="180" value="60">
                </div>
                
                <!-- Simulation-specific options -->
                <div class="simulation-collaboration-options" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">Target Class for Team Assignment</label>
                        <select class="form-control" id="targetSimulationClass">
                            <option value="">Select a class...</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="autoCreateTeams">
                            <label class="form-check-label" for="autoCreateTeams">
                                Automatically create teams when simulation starts
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="preserveTeamsAcrossSessions" checked>
                            <label class="form-check-label" for="preserveTeamsAcrossSessions">
                                Keep same teams across multiple simulation sessions
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="admin-controls">
                <div class="form-group">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="enableAdminMonitoring" checked>
                        <label class="form-check-label" for="enableAdminMonitoring">
                            Enable Admin Monitoring
                            <span class="help-icon" data-tooltip="Allows teachers to view collaboration sessions in real-time" data-tooltip-position="top">?</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="saveCollaborationLogs">
                        <label class="form-check-label" for="saveCollaborationLogs">
                            Save Collaboration Logs
                            <span class="help-icon" data-tooltip="Keep records of group interactions for assessment" data-tooltip-position="top">?</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="allowAdminJoin" checked>
                        <label class="form-check-label" for="allowAdminJoin">
                            Allow Admin to Join Sessions
                            <span class="help-icon" data-tooltip="Permits teachers to join active collaboration sessions" data-tooltip-position="top">?</span>
                        </label>
                    </div>
                </div>
            </div>
        `;

        // Insert before the submit buttons
        const submitSection = form.querySelector('.modal-footer, .form-actions, .submit-section');
        if (submitSection) {
            submitSection.parentNode.insertBefore(collaborationSection, submitSection);
        } else {
            form.appendChild(collaborationSection);
        }

        // Bind events
        this.bindCollaborationEvents(collaborationSection);
        
        // Load available classes for simulation teams
        this.loadAvailableClassesForCollaboration();
    }

    bindCollaborationEvents(section) {
        const typeSelect = section.querySelector('.collaboration-type');
        const optionsDiv = section.querySelector('.collaboration-options');
        const simulationOptions = section.querySelector('.simulation-collaboration-options');
        
        typeSelect.addEventListener('change', (e) => {
            const value = e.target.value;
            if (value === 'individual') {
                optionsDiv.style.display = 'none';
                if (simulationOptions) simulationOptions.style.display = 'none';
            } else {
                optionsDiv.style.display = 'block';
                this.updateCollaborationOptions(value, optionsDiv);
                
                // Show simulation-specific options for simulation teams
                if (simulationOptions) {
                    simulationOptions.style.display = value === 'simulation-teams' ? 'block' : 'none';
                }
            }
        });
    }

    loadAvailableClassesForCollaboration() {
        const classSelect = document.getElementById('targetSimulationClass');
        if (!classSelect) return;
        
        // Add error handling and fail-fast
        fetch('/admin/api/collaboration/classes')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.classes) {
                    classSelect.innerHTML = '<option value="">Select a class...</option>';
                    data.classes.forEach(cls => {
                        const option = document.createElement('option');
                        option.value = cls.id;
                        option.textContent = `${cls.name} (${cls.student_count} students)`;
                        classSelect.appendChild(option);
                    });
                } else {
                    classSelect.innerHTML = '<option value="">No classes available</option>';
                }
            })
            .catch(error => {
                console.error('Error loading classes:', error.message);
                classSelect.innerHTML = '<option value="">Error loading classes</option>';
            });
    }

    // Method to create a collaboration session for a specific simulation
    createSimulationCollaboration(simulationId, collaborationSettings) {
        return fetch('/admin/api/collaboration/simulation-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                simulation_id: simulationId,
                collaboration_settings: collaborationSettings,
                admin_created: true
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Simulation collaboration session created:', data.session_id);
                return data;
            } else {
                throw new Error(data.error || 'Failed to create collaboration session');
            }
        });
    }

    // Method to join a student to a simulation collaboration team
    assignStudentToSimulationTeam(sessionId, studentId, teamId) {
        return fetch(`/admin/api/collaboration/session/${sessionId}/assign`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                student_id: studentId,
                team_id: teamId
            })
        })
        .then(response => response.json());
    }

    // Method to get collaboration settings for a simulation
    getSimulationCollaborationSettings(simulationId) {
        return fetch(`/admin/api/collaboration/simulation/${simulationId}/collaboration`)
            .then(async response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                // Attempt JSON parse safely
                const text = await response.text();
                try { return JSON.parse(text); } catch (e) { throw new Error('Invalid JSON in collaboration settings response'); }
            })
            .then(data => {
                if (data.success) {
                    return data.collaboration_settings || data.settings || {};
                } else {
                    throw new Error(data.error || 'Failed to load collaboration settings');
                }
            })
            .catch(err => {
                console.warn('Collaboration settings load failed:', err.message);
                return {}; // graceful fallback
            });
    }

    // Method to save collaboration settings for a simulation
    saveSimulationCollaborationSettings(simulationId, settings) {
        return fetch(`/admin/api/collaboration/simulation/${simulationId}/collaboration`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                collaboration_settings: settings
            })
        })
        .then(async response => {
            const text = await response.text();
            let data;
            try { data = JSON.parse(text); } catch { throw new Error('Invalid JSON saving collaboration settings'); }
            if (response.ok && data.success) {
                console.log('Collaboration settings saved for simulation:', simulationId);
                return data;
            }
            throw new Error(data && data.error ? data.error : `Save failed (HTTP ${response.status})`);
        })
        .catch(err => {
            console.error('Save collaboration settings error:', err.message);
            throw err;
        });
    }

    updateCollaborationOptions(type, optionsDiv) {
        const maxGroupSizeInput = optionsDiv.querySelector('#maxGroupSize');
        const durationInput = optionsDiv.querySelector('#collaborationDuration');
        
        switch (type) {
            case 'pairs':
                maxGroupSizeInput.value = 2;
                maxGroupSizeInput.max = 2;
                durationInput.value = 30;
                break;
            case 'small-groups':
                maxGroupSizeInput.value = 4;
                maxGroupSizeInput.max = 4;
                durationInput.value = 60;
                break;
            case 'large-groups':
                maxGroupSizeInput.value = 6;
                maxGroupSizeInput.max = 10;
                durationInput.value = 90;
                break;
            case 'class-wide':
                maxGroupSizeInput.value = 30;
                maxGroupSizeInput.max = 50;
                durationInput.value = 120;
                break;
        }
    }

    // Setup real-time collaboration monitoring
    setupCollaborationMonitoring() {
        // Create monitoring dashboard
        this.createMonitoringDashboard();
        
        // Setup WebSocket connection for real-time updates
        this.setupWebSocketConnection();
    }

    createMonitoringDashboard() {
        // Check if we're on a page that should have monitoring
        if (!document.querySelector('.admin-dashboard, .class-content')) return;
        
        const dashboard = document.createElement('div');
        dashboard.className = 'collaboration-monitoring-dashboard';
        dashboard.innerHTML = `
            <div class="dashboard-header">
                <h3><i class="fas fa-eye"></i> Live Collaboration Monitoring</h3>
                <button class="btn btn-sm btn-secondary" onclick="collaborationManager.toggleMonitoring()">
                    <i class="fas fa-pause"></i> Pause Monitoring
                </button>
            </div>
            
            <div class="active-collaborations">
                <div class="collaboration-stats">
                    <div class="stat-item">
                        <span class="stat-number" id="activeGroups">0</span>
                        <span class="stat-label">Active Groups</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number" id="totalParticipants">0</span>
                        <span class="stat-label">Participants</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number" id="avgDuration">0m</span>
                        <span class="stat-label">Avg Duration</span>
                    </div>
                </div>
                
                <div class="collaboration-list" id="collaborationList">
                    <!-- Active collaborations will be populated here -->
                </div>
            </div>
        `;

        // Add to sidebar or main content area
        const sidebar = document.querySelector('.sidebar, .admin-sidebar');
        if (sidebar) {
            sidebar.appendChild(dashboard);
        } else {
            const mainContent = document.querySelector('.main-content, .content-area');
            if (mainContent) {
                mainContent.insertBefore(dashboard, mainContent.firstChild);
            }
        }
    }

    setupWebSocketConnection() {
        // Check if WebSocket is disabled, but allow admin override
        if (window.DISABLE_WEBSOCKET && !window.ENABLE_ADMIN_WEBSOCKET && !window.isAdmin) {
            // Check if AdminWebSocketManager can enable for admin
            if (window.adminWebSocketManager && typeof window.adminWebSocketManager.shouldEnableForAdmin === 'function' && window.adminWebSocketManager.shouldEnableForAdmin()) {
                console.log('🔓 Admin WebSocket override enabled for collaboration manager');
                window.ENABLE_ADMIN_WEBSOCKET = true;
            } else {
                console.log('🚫 WebSocket disabled for collaboration manager - using polling mode');
                this.fallbackToPolling();
                return;
            }
        }
        
        // Connect to actual WebSocket server for real-time collaboration updates
        try {
            if (typeof io !== 'undefined') {
                this.socket = io('/');
                
                this.socket.on('connect', () => {
                    console.log('✅ Connected to collaboration WebSocket');
                    // Join the admin collaboration monitoring room
                    this.socket.emit('join_admin_collaboration_monitoring');
                });
                \
                this.socket.on('joined_collaboration_monitoring', (data) => {
                    console.log('✅ Joined collaboration monitoring room:', data.message);
                });
                
                this.socket.on('collaboration_started', (data) => {
                    console.log('New collaboration started:', data);
                    this.updateCollaborationStats();
                    this.addCollaborationToList(data);
                });
                
                this.socket.on('collaboration_ended', (data) => {
                    console.log('Collaboration ended:', data);
                    this.updateCollaborationStats();
                    this.removeCollaborationFromList(data.id);
                });
                
                this.socket.on('collaboration_updated', (data) => {
                    console.log('Collaboration updated:', data);
                    this.updateCollaborationInList(data);
                });
                
                this.socket.on('stats_updated', (data) => {
                    this.updateStatsDisplay(data);
                });
                
                this.socket.on('collaboration_list_update', (collaborations) => {
                    this.updateCollaborationListDirect(collaborations);
                });
                
                // Handle connection errors
                this.socket.on('disconnect', () => {
                    console.warn('⚠️ Disconnected from collaboration WebSocket');
                });
                
                this.socket.on('connect_error', (error) => {
                    console.error('WebSocket connection error:', error);
                    this.fallbackToPolling();
                });
                
                this.socket.on('collaboration_monitoring_error', (error) => {
                    console.error('Collaboration monitoring error:', error);
                });
                
            } else {
                console.warn('Socket.IO not available, falling back to polling');
                this.fallbackToPolling();
            }
        } catch (error) {
            console.error('Failed to setup WebSocket:', error);
            this.fallbackToPolling();
        }
    }
    
    updateStatsDisplay(data) {
        const activeGroups = document.getElementById('activeGroups');
        const totalParticipants = document.getElementById('totalParticipants');
        const avgDuration = document.getElementById('avgDuration');
        
        if (activeGroups && data.activeGroups !== undefined) {
            activeGroups.textContent = data.activeGroups;
        }
        if (totalParticipants && data.totalParticipants !== undefined) {
            totalParticipants.textContent = data.totalParticipants;
        }
        if (avgDuration && data.avgDuration !== undefined) {
            avgDuration.textContent = data.avgDuration;
        }
    }
    
    fallbackToPolling() {
        // Fallback to polling when WebSocket is not available
        console.log('Using polling for collaboration updates');
        this.pollingInterval = setInterval(() => {
            this.updateCollaborationStats();
        }, 10000); // Poll every 10 seconds
    }
    
    // Real-time collaboration list management
    addCollaborationToList(collaboration) {
        const list = document.getElementById('collaborationList');
        if (!list) return;
        
        const collaborationElement = this.createCollaborationElement(collaboration);
        list.appendChild(collaborationElement);
    }
    
    removeCollaborationFromList(collaborationId) {
        const element = document.querySelector(`[data-collaboration-id="${collaborationId}"]`);
        if (element) {
            element.remove();
        }
    }
    
    updateCollaborationInList(collaboration) {
        const element = document.querySelector(`[data-collaboration-id="${collaboration.id}"]`);
        if (element) {
            // Update participant list
            const participantsElement = element.querySelector('.participants');
            if (participantsElement && collaboration.participant_names) {
                participantsElement.innerHTML = `
                    <i class="fas fa-users"></i>
                    ${collaboration.participant_names.join(', ')}
                `;
            }
        }
    }
    
    updateCollaborationListDirect(collaborations) {
        const list = document.getElementById('collaborationList');
        if (!list) return;
        
        if (collaborations && collaborations.length > 0) {
            list.innerHTML = collaborations.map(collab => `
                <div class="collaboration-item ${collab.status}" data-collaboration-id="${collab.id}">
                    <div class="collaboration-info">
                        <div class="activity-name">${collab.activity_name}</div>
                        <div class="participants">
                            <i class="fas fa-users"></i>
                            ${collab.participants.join(', ')}
                        </div>
                        <div class="duration">
                            <i class="fas fa-clock"></i>
                            ${collab.duration}
                        </div>
                    </div>
                    <div class="collaboration-actions">
                        <button class="btn-action" onclick="collaborationManager.viewCollaboration(${collab.id})" title="View Session">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-action" onclick="collaborationManager.joinCollaboration(${collab.id})" title="Join Session">
                            <i class="fas fa-sign-in-alt"></i>
                        </button>
                        <button class="btn-action" onclick="collaborationManager.endCollaboration(${collab.id})" title="End Session">
                            <i class="fas fa-stop"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            list.innerHTML = `
                <div class="no-collaborations">
                    <i class="fas fa-users-slash"></i>
                    <p>No active collaboration sessions</p>
                </div>
            `;
        }
    }
    
    createCollaborationElement(collaboration) {
        const element = document.createElement('div');
        element.className = `collaboration-item ${collaboration.status}`;
        element.setAttribute('data-collaboration-id', collaboration.id);
        element.innerHTML = `
            <div class="collaboration-info">
                <div class="activity-name">${collaboration.activity_name}</div>
                <div class="participants">
                    <i class="fas fa-users"></i>
                    ${collaboration.participants.join(', ')}
                </div>
                <div class="duration">
                    <i class="fas fa-clock"></i>
                    ${collaboration.duration}
                </div>
            </div>
            <div class="collaboration-actions">
                <button class="btn-action" onclick="collaborationManager.viewCollaboration(${collaboration.id})" title="View Session">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-action" onclick="collaborationManager.joinCollaboration(${collaboration.id})" title="Join Session">
                    <i class="fas fa-sign-in-alt"></i>
                </button>
                <button class="btn-action" onclick="collaborationManager.endCollaboration(${collaboration.id})" title="End Session">
                    <i class="fas fa-stop"></i>
                </button>
            </div>
        `;
        return element;
    }

    updateCollaborationStats() {
        // Fetch real-time collaboration statistics from API
        fetch('/admin/api/collaboration/stats')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const activeGroups = document.getElementById('activeGroups');
                const totalParticipants = document.getElementById('totalParticipants');
                const avgDuration = document.getElementById('avgDuration');
                
                if (activeGroups) {
                    activeGroups.textContent = data.activeGroups || 0;
                }
                if (totalParticipants) {
                    totalParticipants.textContent = data.totalParticipants || 0;
                }
                if (avgDuration) {
                    avgDuration.textContent = data.avgDuration || '0m';
                }
                
                // Update collaboration list with real data
                this.updateCollaborationList();
            })
            .catch(error => {
                console.warn('Failed to fetch collaboration stats:', error.message);
                // Fallback to show no active collaborations
                const activeGroups = document.getElementById('activeGroups');
                const totalParticipants = document.getElementById('totalParticipants');
                const avgDuration = document.getElementById('avgDuration');
                
                if (activeGroups) activeGroups.textContent = '0';
                if (totalParticipants) totalParticipants.textContent = '0';
                if (avgDuration) avgDuration.textContent = '0m';
                
                this.updateCollaborationList();
            });
    }

    updateCollaborationList() {
        const list = document.getElementById('collaborationList');
        if (!list) return;
        
        // Fetch active collaboration sessions from API
        fetch('/admin/api/collaboration/active')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(collaborations => {
                if (collaborations && collaborations.length > 0) {
                    list.innerHTML = collaborations.map(collab => `
                        <div class="collaboration-item ${collab.status}">
                            <div class="collaboration-info">
                                <div class="activity-name">${collab.activity_name}</div>
                                <div class="participants">
                                    <i class="fas fa-users"></i>
                                    ${collab.participants.join(', ')}
                                </div>
                                <div class="duration">
                                    <i class="fas fa-clock"></i>
                                    ${collab.duration}
                                </div>
                            </div>
                            <div class="collaboration-actions">
                                <button class="btn-action" onclick="collaborationManager.viewCollaboration(${collab.id})" title="View Session">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn-action" onclick="collaborationManager.joinCollaboration(${collab.id})" title="Join Session">
                                    <i class="fas fa-sign-in-alt"></i>
                                </button>
                                <button class="btn-action" onclick="collaborationManager.endCollaboration(${collab.id})" title="End Session">
                                    <i class="fas fa-stop"></i>
                                </button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    list.innerHTML = `
                        <div class="no-collaborations">
                            <i class="fas fa-users-slash"></i>
                            <p>No active collaboration sessions</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.warn('Failed to fetch active collaborations:', error.message);
                list.innerHTML = `
                    <div class="no-collaborations">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Unable to load collaboration sessions</p>
                    </div>
                `;
            });
    }

    // Admin action methods
    viewCollaboration(id) {
        // Open collaboration viewer with real data
        console.log(`Viewing collaboration ${id}`);
        this.showCollaborationViewer(id);
    }

    joinCollaboration(id) {
        // Allow admin to join collaboration session
        console.log(`Joining collaboration ${id}`);
        fetch(`/admin/api/collaboration/${id}/join`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ admin_join: true })
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Redirect to collaboration interface
                window.open(data.collaboration_url, '_blank');
            } else {
                alert('Failed to join collaboration session');
            }
        })
        .catch(error => {
            console.error('Failed to join collaboration:', error);
            alert('Unable to join collaboration session');
        });
    }

    endCollaboration(id) {
        // End collaboration session
        if (confirm('Are you sure you want to end this collaboration session?')) {
            console.log(`Ending collaboration ${id}`);
            fetch(`/admin/api/collaboration/${id}/end`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Refresh collaboration list
                    this.updateCollaborationList();
                    // Show success message
                    if (typeof moduleBuilder !== 'undefined' && moduleBuilder.showToast) {
                        moduleBuilder.showToast('Collaboration session ended', 'success');
                    }
                } else {
                    alert('Failed to end collaboration session');
                }
            })
            .catch(error => {
                console.error('Failed to end collaboration:', error);
                alert('Unable to end collaboration session');
            });
        }
    }

    showCollaborationViewer(id) {
        // Fetch collaboration session details from API
        fetch(`/admin/api/collaboration/${id}/details`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(collaboration => {
                this.renderCollaborationViewer(id, collaboration);
            })
            .catch(error => {
                console.error('Failed to fetch collaboration details:', error);
                // Show error modal
                this.showErrorModal('Unable to load collaboration session details');
            });
    }
    
    renderCollaborationViewer(id, collaboration) {
        // Create modal viewer for collaboration session
        const modal = document.createElement('div');
        modal.className = 'modal fade collaboration-viewer';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Collaboration Session: ${collaboration.activity_name}</h5>
                        <div class="session-info">
                            <span class="badge bg-${collaboration.status === 'active' ? 'success' : 'secondary'}">
                                ${collaboration.status}
                            </span>
                            <span class="participants-count">
                                <i class="fas fa-users"></i> ${collaboration.participants.length} participants
                            </span>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="collaboration-viewer-content">
                            <div class="viewer-tabs">
                                <button class="tab-btn active" onclick="collaborationManager.showViewerTab('chat')">Chat</button>
                                <button class="tab-btn" onclick="collaborationManager.showViewerTab('screen')">Screen</button>
                                <button class="tab-btn" onclick="collaborationManager.showViewerTab('files')">Files</button>
                                <button class="tab-btn" onclick="collaborationManager.showViewerTab('progress')">Progress</button>
                            </div>
                            
                            <div class="viewer-content">
                                <div id="chat-view" class="view-pane active">
                                    <div class="chat-messages" id="chatMessages-${id}">
                                        <div class="loading-messages">Loading chat history...</div>
                                    </div>
                                </div>
                                
                                <div id="screen-view" class="view-pane">
                                    <div class="screen-share-preview" id="screenShare-${id}">
                                        <div class="loading-screen">Loading screen share...</div>
                                    </div>
                                </div>
                                
                                <div id="files-view" class="view-pane">
                                    <div class="shared-files" id="sharedFiles-${id}">
                                        <div class="loading-files">Loading shared files...</div>
                                    </div>
                                </div>
                                
                                <div id="progress-view" class="view-pane">
                                    <div class="progress-tracking" id="progressTracking-${id}">
                                        <div class="loading-progress">Loading progress data...</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Load content for each tab
        this.loadChatHistory(id);
        this.loadScreenShare(id);
        this.loadSharedFiles(id);
        this.loadProgressTracking(id);
        
        // Clean up when closed
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    loadChatHistory(id) {
        fetch(`/admin/api/collaboration/${id}/chat`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(messages => {
                const chatContainer = document.getElementById(`chatMessages-${id}`);
                if (chatContainer) {
                    if (messages && messages.length > 0) {
                        chatContainer.innerHTML = messages.map(msg => `
                            <div class="message" data-timestamp="${msg.timestamp}">
                                <span class="message-time">${new Date(msg.timestamp).toLocaleTimeString()}</span>
                                <strong>${msg.user_name}:</strong> ${msg.message}
                            </div>
                        `).join('');
                    } else {
                        chatContainer.innerHTML = '<div class="no-messages">No chat messages yet</div>';
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load chat history:', error);
                const chatContainer = document.getElementById(`chatMessages-${id}`);
                if (chatContainer) {
                    chatContainer.innerHTML = '<div class="error-message">Failed to load chat history</div>';
                }
            });
    }
    
    loadScreenShare(id) {
        fetch(`/admin/api/collaboration/${id}/screen`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(screenData => {
                const screenContainer = document.getElementById(`screenShare-${id}`);
                if (screenContainer) {
                    if (screenData && screenData.active) {
                        screenContainer.innerHTML = `
                            <div class="screen-share-active">
                                <img src="${screenData.preview_url}" alt="Screen share preview" class="screen-preview">
                                <div class="screen-info">
                                    <span>Shared by: ${screenData.shared_by}</span>
                                    <span>Quality: ${screenData.quality}</span>
                                </div>
                            </div>
                        `;
                    } else {
                        screenContainer.innerHTML = '<div class="no-screen-share">No active screen sharing</div>';
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load screen share:', error);
                const screenContainer = document.getElementById(`screenShare-${id}`);
                if (screenContainer) {
                    screenContainer.innerHTML = '<div class="error-message">Failed to load screen share</div>';
                }
            });
    }
    
    loadSharedFiles(id) {
        fetch(`/admin/api/collaboration/${id}/files`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(files => {
                const filesContainer = document.getElementById(`sharedFiles-${id}`);
                if (filesContainer) {
                    if (files && files.length > 0) {
                        filesContainer.innerHTML = files.map(file => `
                            <div class="file-item">
                                <i class="fas fa-${this.getFileIcon(file.type)}"></i>
                                <span class="file-name">${file.name}</span>
                                <span class="file-size">${file.size}</span>
                                <span class="shared-by">by ${file.shared_by}</span>
                                <button class="btn-download" onclick="collaborationManager.downloadFile('${file.id}')">
                                    <i class="fas fa-download"></i>
                                </button>
                            </div>
                        `).join('');
                    } else {
                        filesContainer.innerHTML = '<div class="no-files">No files shared yet</div>';
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load shared files:', error);
                const filesContainer = document.getElementById(`sharedFiles-${id}`);
                if (filesContainer) {
                    filesContainer.innerHTML = '<div class="error-message">Failed to load shared files</div>';
                }
            });
    }
    
    loadProgressTracking(id) {
        fetch(`/admin/api/collaboration/${id}/progress`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(progress => {
                const progressContainer = document.getElementById(`progressTracking-${id}`);
                if (progressContainer) {
                    if (progress && progress.participants) {
                        progressContainer.innerHTML = `
                            <h6>Individual Progress</h6>
                            ${progress.participants.map(participant => `
                                <div class="progress-item">
                                    <span>${participant.name}: ${participant.completion}% complete</span>
                                    <div class="progress-bar">
                                        <div class="progress" style="width: ${participant.completion}%"></div>
                                    </div>
                                    <div class="progress-details">
                                        <small>Last activity: ${new Date(participant.last_activity).toLocaleTimeString()}</small>
                                    </div>
                                </div>
                            `).join('')}
                        `;
                    } else {
                        progressContainer.innerHTML = '<div class="no-progress">No progress data available</div>';
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load progress tracking:', error);
                const progressContainer = document.getElementById(`progressTracking-${id}`);
                if (progressContainer) {
                    progressContainer.innerHTML = '<div class="error-message">Failed to load progress data</div>';
                }
            });
    }
    
    getFileIcon(fileType) {
        const iconMap = {
            'image': 'image',
            'document': 'file-alt',
            'video': 'video',
            'audio': 'music',
            'archive': 'file-archive',
            'code': 'code'
        };
        return iconMap[fileType] || 'file';
    }
    
    downloadFile(fileId) {
        window.open(`/admin/api/collaboration/files/${fileId}/download`, '_blank');
    }
    
    showErrorModal(message) {
        const errorModal = document.createElement('div');
        errorModal.className = 'modal fade';
        errorModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Error</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i>
                            ${message}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(errorModal);
        const bootstrapModal = new bootstrap.Modal(errorModal);
        bootstrapModal.show();
        
        errorModal.addEventListener('hidden.bs.modal', () => {
            errorModal.remove();
        });
    }

    showViewerTab(tabName) {
        // Switch tabs in collaboration viewer
        document.querySelectorAll('.viewer-tabs .tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.view-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        event.target.classList.add('active');
        document.getElementById(`${tabName}-view`).classList.add('active');
    }

    toggleMonitoring() {
        // Toggle monitoring on/off
        const btn = event.target.closest('button');
        const icon = btn.querySelector('i');
        
        if (icon.classList.contains('fa-pause')) {
            icon.className = 'fas fa-play';
            btn.innerHTML = '<i class="fas fa-play"></i> Resume Monitoring';
        } else {
            icon.className = 'fas fa-pause';
            btn.innerHTML = '<i class="fas fa-pause"></i> Pause Monitoring';
        }
    }

    // Save collaboration settings
    saveCollaborationSettings(activityId, settings) {
        this.collaborationSettings.set(activityId, settings);
        
        // Save to backend
        fetch('/admin/api/collaboration/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ activityId, settings })
        }).catch(error => console.error('Failed to save collaboration settings:', error));
    }

    loadExistingSettings() {
        // Load existing collaboration settings from backend
        fetch('/admin/api/collaboration/settings')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.settings) {
                    data.settings.forEach(item => {
                        this.collaborationSettings.set(item.activityId, item.settings);
                    });
                }
            })
            .catch(error => {
                console.warn('Collaboration API not available, using local mode:', error.message);
                // Initialize with empty settings for now
            });
    }
    
    // Cleanup method
    destroy() {
        // Clean up WebSocket connection
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        
        // Clear polling interval
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        
        // Clear settings
        this.collaborationSettings.clear();
        this.activeCollaborations.clear();
    }
}

// Initialize collaboration manager with singleton pattern
if (!window.collaborationManager) {
    const collaborationManager = new CollaborationManager();
    window.collaborationManager = collaborationManager;
} else {
    console.log('🔒 CollaborationManager already exists, using existing instance');
}

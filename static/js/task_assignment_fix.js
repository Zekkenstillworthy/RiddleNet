/**
 * Task Assignment Fix - Enhanced Activity Tracking
 * Fixes path issues and adds comprehensive activity tracking
 */

(function() {
    'use strict';

    console.log('📋 [TASK FIX] Task Assignment activity tracker loading...');

    // Store original TaskAssignmentManager if it exists
    const OriginalTaskAssignmentManager = window.TaskAssignmentManager;

    class EnhancedTaskAssignmentManager {
        constructor() {
            this.taskConfig = null;
            this.assignment = null;
            this.userProgress = {
                devices_placed: [],
                devices_configured: {},
                connections_made: [],
                cli_history: [],
                activity_log: []
            };
            this.simulationId = this.getSimulationId();
            this.activityTrackingEnabled = true;
            this.lastSaveTime = null;
            this.autoSaveInterval = null;
            
            console.log(`📋 [TASK FIX] Initializing for simulation: ${this.simulationId}`);
            this.init();
        }

        getSimulationId() {
            // Extract simulation ID from URL
            const pathParts = window.location.pathname.split('/');
            const simIndex = pathParts.indexOf('simulation');
            if (simIndex !== -1 && pathParts[simIndex + 1]) {
                return parseInt(pathParts[simIndex + 1]);
            }
            return window.simulation?.id || null;
        }

        async init() {
            console.log('📋 [TASK FIX] Initializing Enhanced Task Assignment Manager');
            
            if (!this.simulationId) {
                console.warn('📋 [TASK FIX] No simulation ID found, disabling task tracking');
                return;
            }

            await this.loadTaskConfig();
            await this.loadUserAssignment();
            this.setupEventListeners();
            this.setupActivityTracking();
            this.startAutoSave();
            this.updateUI();
            
            console.log('✅ [TASK FIX] Task Assignment Manager ready');
        }

        async loadTaskConfig() {
            try {
                const url = `/dynamic/api/simulation/${this.simulationId}/task-config`;
                console.log(`📋 [TASK FIX] Loading task config from: ${url}`);
                
                const response = await fetch(url);
                const result = await response.json();
                
                if (result.success && result.task_config) {
                    this.taskConfig = result.task_config;
                    console.log('✅ [TASK FIX] Task config loaded:', {
                        enabled: this.taskConfig.enabled,
                        devices: this.taskConfig.device_requirements?.length || 0,
                        connections: this.taskConfig.connection_requirements?.length || 0,
                        cli_requirements: Object.keys(this.taskConfig.cli_requirements || {}).length
                    });
                    this.renderTaskRequirements();
                } else {
                    console.log('📋 [TASK FIX] No task configuration found for this simulation');
                    this.taskConfig = { enabled: false };
                }
            } catch (error) {
                console.error('❌ [TASK FIX] Error loading task config:', error);
                this.taskConfig = { enabled: false };
            }
        }

        async loadUserAssignment() {
            try {
                const url = `/dynamic/api/simulation/${this.simulationId}/task-assignment`;
                console.log(`📋 [TASK FIX] Loading user assignment from: ${url}`);
                
                const response = await fetch(url);
                const result = await response.json();
                
                if (result.success && result.assignment) {
                    this.assignment = result.assignment;
                    this.userProgress = {
                        devices_placed: result.assignment.devices_placed || [],
                        devices_configured: result.assignment.devices_configured || {},
                        connections_made: result.assignment.connections_made || [],
                        cli_history: result.assignment.cli_history || [],
                        activity_log: result.assignment.activity_log || []
                    };
                    console.log('✅ [TASK FIX] User assignment loaded:', {
                        id: this.assignment.id,
                        status: this.assignment.status,
                        completion: this.assignment.completion_percentage
                    });
                    this.updateProgressUI();
                } else {
                    console.log('📋 [TASK FIX] No existing assignment, will create on first action');
                }
                
                // Sync existing devices and connections from the network engine
                this.syncExistingNetworkState();
            } catch (error) {
                console.error('❌ [TASK FIX] Error loading user assignment:', error);
            }
        }

        syncExistingNetworkState() {
            console.log('🔍 [TASK FIX DEBUG] Starting syncExistingNetworkState...');
            console.log('🔍 [TASK FIX DEBUG] taskConfig:', this.taskConfig);
            console.log('🔍 [TASK FIX DEBUG] window.networkEngine:', window.networkEngine);
            
            if (!this.taskConfig?.enabled) {
                console.warn('⚠️ [TASK FIX DEBUG] Task config not enabled, skipping sync');
                return;
            }
            if (!window.networkEngine) {
                console.warn('⚠️ [TASK FIX DEBUG] Network engine not available, skipping sync');
                return;
            }

            console.log('🔄 [TASK FIX] Syncing existing network state...');

            // Sync devices
            if (window.networkEngine.devices) {
                console.log('🔍 [TASK FIX DEBUG] Network engine devices:', window.networkEngine.devices);
                const existingDevices = Array.from(window.networkEngine.devices.values());
                console.log(`🔍 [TASK FIX DEBUG] Found ${existingDevices.length} existing devices:`, existingDevices);
                console.log('🔍 [TASK FIX DEBUG] Current devices_placed:', this.userProgress.devices_placed);
                
                existingDevices.forEach(device => {
                    console.log(`🔍 [TASK FIX DEBUG] Checking device: ${device.id}`, device);
                    if (!this.userProgress.devices_placed.includes(device.id)) {
                        console.log(`📍 [TASK FIX] Syncing existing device: ${device.id}`);
                        this.userProgress.devices_placed.push(device.id);
                    } else {
                        console.log(`ℹ️ [TASK FIX DEBUG] Device ${device.id} already tracked`);
                    }
                });
            } else {
                console.warn('⚠️ [TASK FIX DEBUG] No devices found in network engine');
            }

            // Sync connections
            if (window.networkEngine.connections) {
                console.log('🔍 [TASK FIX DEBUG] Network engine connections:', window.networkEngine.connections);
                const existingConnections = Array.from(window.networkEngine.connections.values());
                console.log(`🔍 [TASK FIX DEBUG] Found ${existingConnections.length} existing connections:`, existingConnections);
                console.log('🔍 [TASK FIX DEBUG] Current connections_made:', this.userProgress.connections_made);
                
                existingConnections.forEach(conn => {
                    console.log(`🔍 [TASK FIX DEBUG] Checking connection:`, conn);
                    
                    // Check if connection already tracked
                    const alreadyTracked = this.userProgress.connections_made.some(tracked => 
                        tracked.id === conn.id || 
                        (tracked.source_device === conn.device1?.id && tracked.target_device === conn.device2?.id)
                    );
                    
                    console.log(`🔍 [TASK FIX DEBUG] Connection already tracked: ${alreadyTracked}`);
                    
                    if (!alreadyTracked) {
                        console.log(`🔗 [TASK FIX] Syncing existing connection: ${conn.device1?.id} → ${conn.device2?.id}`);
                        const connectionData = {
                            id: conn.id,
                            source_device: conn.device1?.id || conn.source,
                            target_device: conn.device2?.id || conn.target,
                            source_interface: conn.port1 || conn.source_interface,
                            target_interface: conn.port2 || conn.target_interface,
                            connection_type: conn.type || 'ethernet',
                            status: conn.status || 'up',
                            created_at: new Date().toISOString()
                        };
                        console.log(`🔍 [TASK FIX DEBUG] Created connection data:`, connectionData);
                        this.userProgress.connections_made.push(connectionData);
                    }
                });
            } else {
                console.warn('⚠️ [TASK FIX DEBUG] No connections found in network engine');
            }

            // Save and update UI
            console.log('🔍 [TASK FIX DEBUG] Final progress state:', {
                devices_placed: this.userProgress.devices_placed,
                connections_made: this.userProgress.connections_made
            });
            
            if (this.userProgress.devices_placed.length > 0 || this.userProgress.connections_made.length > 0) {
                console.log(`✅ [TASK FIX] Synced ${this.userProgress.devices_placed.length} devices and ${this.userProgress.connections_made.length} connections`);
                this.saveProgress();
                this.updateProgressUI();
            } else {
                console.warn('⚠️ [TASK FIX DEBUG] No devices or connections to sync');
            }
        }

        renderTaskRequirements() {
            if (!this.taskConfig || !this.taskConfig.enabled) {
                console.log('📋 [TASK FIX] Task mode not enabled, skipping requirements render');
                return;
            }

            console.log('📋 [TASK FIX] Rendering task requirements in performance panel...');
            this.renderDeviceRequirements();
            this.renderConnectionRequirements();
            this.renderCLIRequirements();
        }

        renderDeviceRequirements() {
            const container = document.getElementById('device-requirements-list');
            if (!container) {
                console.warn('📋 [TASK FIX] Device requirements container not found');
                return;
            }

            const devices = this.taskConfig.device_requirements || [];
            if (devices.length === 0) {
                container.innerHTML = '<li class="text-muted">No device requirements</li>';
                return;
            }

            container.innerHTML = devices.map((device, index) => `
                <li class="task-requirement-item" data-device-id="${device.id}">
                    <i class="fas fa-circle requirement-status"></i>
                    <span class="requirement-label">${device.label || device.id}</span>
                    <small class="requirement-type">(${device.type})</small>
                </li>
            `).join('');

            console.log(`✅ [TASK FIX] Rendered ${devices.length} device requirements`);
        }

        renderConnectionRequirements() {
            const container = document.getElementById('connection-requirements-list');
            if (!container) {
                console.warn('📋 [TASK FIX] Connection requirements container not found');
                return;
            }

            const connections = this.taskConfig.connection_requirements || [];
            if (connections.length === 0) {
                container.innerHTML = '<li class="text-muted">No connection requirements</li>';
                return;
            }

            container.innerHTML = connections.map((conn, index) => {
                const connectionType = conn.type || 'ethernet';
                const typeIcon = connectionType === 'wireless' ? 'fa-wifi' : 'fa-network-wired';
                const typeLabel = connectionType === 'wireless' ? 'Wireless' : 'Wired';
                const typeColor = connectionType === 'wireless' ? '#8B5CF6' : '#00D9FF';
                
                return `
                    <li class="task-requirement-item" data-connection-index="${index}" data-connection-type="${connectionType}">
                        <i class="fas fa-circle requirement-status"></i>
                        <span class="requirement-label">${conn.source_device} → ${conn.target_device}</span>
                        <i class="fas ${typeIcon}" style="color: ${typeColor}; margin-left: 6px; font-size: 0.85em;" title="${typeLabel}"></i>
                    </li>
                `;
            }).join('');

            console.log(`✅ [TASK FIX] Rendered ${connections.length} connection requirements`);
        }

        renderCLIRequirements() {
            const container = document.getElementById('cli-requirements-container');
            if (!container) {
                console.warn('📋 [TASK FIX] CLI requirements container not found');
                return;
            }

            const cliReqs = this.taskConfig.cli_requirements || {};
            const totalCommands = Object.values(cliReqs).reduce((sum, cmds) => sum + cmds.length, 0);
            
            if (totalCommands === 0) {
                container.innerHTML = `
                    <div class="empty-state" style="text-align: center; padding: 2rem 1rem; color: var(--text-muted); background: rgba(255, 255, 255, 0.03); border-radius: 8px;">
                        <i class="fas fa-info-circle" style="font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.5;"></i>
                        <p style="margin: 0; font-size: 0.9rem;">No CLI command requirements defined</p>
                    </div>
                `;
                return;
            }

            const html = Object.entries(cliReqs).map(([deviceId, commands]) => `
                <li class="task-device-cli">
                    <strong>${deviceId}</strong>
                    <ol>
                        ${commands.map((cmd, i) => `
                            <li class="task-requirement-item" data-device-id="${deviceId}" data-cmd-index="${i}">
                                <i class="fas fa-circle requirement-status"></i>
                                <code>${cmd.command}</code>
                            </li>
                        `).join('')}
                    </ol>
                </li>
            `).join('');

            container.innerHTML = `<ul class="requirements-list">${html}</ul>`;
            console.log(`✅ [TASK FIX] Rendered ${totalCommands} CLI requirements`);
        }

        setupEventListeners() {
            console.log('📋 [TASK FIX] Setting up event listeners...');

            // Listen for network engine events
            if (window.networkEngine) {
                window.networkEngine.on('device-added', (device) => this.trackDevicePlacement(device));
                window.networkEngine.on('device-configured', (device) => this.trackDeviceConfiguration(device));
                window.networkEngine.on('connection-created', (conn) => this.trackConnection(conn));
                console.log('✅ [TASK FIX] Network engine listeners attached');
            }

            // Listen for CLI events
            document.addEventListener('cli-command-executed', (e) => this.trackCLICommand(e.detail));

            // Submit button
            const submitBtn = document.getElementById('submit-task-btn');
            if (submitBtn) {
                submitBtn.addEventListener('click', () => this.submitTask());
            }
        }

        setupActivityTracking() {
            if (!this.activityTrackingEnabled) return;

            console.log('🎯 [TASK FIX] Activity tracking enabled');

            // Track canvas interactions
            document.addEventListener('mousedown', (e) => this.logActivity('canvas_interaction', {
                x: e.clientX,
                y: e.clientY
            }));

            // Track device palette usage
            const devicePalette = document.getElementById('device-palette');
            if (devicePalette) {
                devicePalette.addEventListener('click', (e) => {
                    const deviceItem = e.target.closest('[data-device-type]');
                    if (deviceItem) {
                        this.logActivity('device_palette_click', {
                            device_type: deviceItem.dataset.deviceType
                        });
                    }
                });
            }

            // Track sidebar interactions
            document.addEventListener('click', (e) => {
                if (e.target.closest('.performance-sidebar')) {
                    this.logActivity('sidebar_interaction', {
                        target: e.target.tagName
                    });
                }
            });
        }

        trackDevicePlacement(device) {
            if (!this.taskConfig?.enabled) return;

            console.log('📍 [TASK FIX] Device placed:', device.id);
            
            if (!this.userProgress.devices_placed.includes(device.id)) {
                this.userProgress.devices_placed.push(device.id);
                this.logActivity('device_placed', {
                    device_id: device.id,
                    device_type: device.type,
                    position: device.position
                });
                this.saveProgress();
                this.updateProgressUI();
            }
            
            // 📡 BROADCAST TO COLLABORATORS (always, even if already tracked)
            if (window.collaborationRealTime && window.collaborationRealTime.socket) {
                const simulationId = this.simulationId || window.simulationId;
                window.collaborationRealTime.socket.emit('simulation_device_added', {
                    simulation_id: simulationId,
                    device: {
                        id: device.id,
                        type: device.type,
                        label: device.label || device.id,
                        x: device.x,
                        y: device.y,
                        config: device.config
                    }
                });
                console.log(`📡 [COLLAB] Broadcasted device to collaborators: ${device.label || device.id}`);
            } else {
                console.warn('⚠️ [COLLAB] Collaboration socket not available for device broadcast');
            }
        }

        trackDeviceConfiguration(device) {
            if (!this.taskConfig?.enabled) return;

            console.log('⚙️ [TASK FIX] Device configured:', device.id);
            
            this.userProgress.devices_configured[device.id] = {
                hostname: device.hostname,
                interfaces: device.interfaces,
                configured_at: new Date().toISOString()
            };
            
            this.logActivity('device_configured', {
                device_id: device.id,
                configuration: device.config
            });
            
            this.saveProgress();
            this.updateProgressUI();
        }

        trackConnection(connection) {
            if (!this.taskConfig?.enabled) return;

            console.log('🔗 [TASK FIX] Connection created:', connection);
            
            // Enhanced connection tracking with type (wired/wireless)
            const connectionData = {
                id: connection.id,
                source_device: connection.device1?.id || connection.source,
                target_device: connection.device2?.id || connection.target,
                source_interface: connection.port1 || connection.source_interface,
                target_interface: connection.port2 || connection.target_interface,
                connection_type: connection.type || 'ethernet', // Track wired vs wireless
                status: connection.status || 'up',
                created_at: new Date().toISOString()
            };
            
            this.userProgress.connections_made.push(connectionData);
            
            console.log('✅ [TASK FIX] Connection tracked:', connectionData);
            
            this.logActivity('connection_created', connectionData);
            this.saveProgress();
            this.updateProgressUI();
            
            // 📡 BROADCAST TO COLLABORATORS
            if (window.collaborationRealTime && window.collaborationRealTime.socket) {
                const simulationId = this.simulationId || window.simulationId;
                window.collaborationRealTime.socket.emit('simulation_connection_added', {
                    simulation_id: simulationId,
                    connection: {
                        id: connection.id,
                        device1_id: connection.device1?.id || connection.source,
                        device2_id: connection.device2?.id || connection.target,
                        port1: connection.port1 || connection.source_interface,
                        port2: connection.port2 || connection.target_interface,
                        type: connection.type || 'ethernet'
                    }
                });
                console.log(`📡 [COLLAB] Broadcasted connection to collaborators: ${connectionData.source_device} <-> ${connectionData.target_device}`);
            } else {
                console.warn('⚠️ [COLLAB] Collaboration socket not available for connection broadcast');
            }
        }

        trackCLICommand(detail) {
            if (!this.taskConfig?.enabled) return;

            console.log('💻 [TASK FIX] CLI command executed:', detail.command);
            
            this.userProgress.cli_history.push({
                device_id: detail.device_id,
                command: detail.command,
                output: detail.output,
                executed_at: new Date().toISOString()
            });
            
            this.logActivity('cli_command', {
                device_id: detail.device_id,
                command: detail.command
            });
            
            this.saveProgress();
            this.updateProgressUI();
        }

        logActivity(activity_type, data = {}) {
            if (!this.activityTrackingEnabled) return;

            const activity = {
                type: activity_type,
                timestamp: new Date().toISOString(),
                data: data
            };

            if (!this.userProgress.activity_log) {
                this.userProgress.activity_log = [];
            }

            this.userProgress.activity_log.push(activity);
            
            console.log(`📊 [TASK FIX] Activity logged: ${activity_type}`, data);

            // Emit to server via socket for real-time tracking
            if (window.socket && window.socket.connected) {
                window.socket.emit('task_activity', {
                    simulation_id: this.simulationId,
                    activity: activity
                });
            }
        }

        async saveProgress() {
            try {
                console.log('💾 [TASK FIX DEBUG] Saving progress...');
                console.log('💾 [TASK FIX DEBUG] Progress data:', {
                    devices_placed: this.userProgress.devices_placed,
                    devices_configured: this.userProgress.devices_configured,
                    connections_made: this.userProgress.connections_made,
                    cli_history: this.userProgress.cli_history,
                    activity_log_count: this.userProgress.activity_log?.length || 0
                });
                
                const url = `/dynamic/api/simulation/${this.simulationId}/task-progress`;
                console.log('💾 [TASK FIX DEBUG] Sending to:', url);
                
                const payload = {
                    devices_placed: this.userProgress.devices_placed,
                    devices_configured: this.userProgress.devices_configured,
                    connections_made: this.userProgress.connections_made,
                    cli_history: this.userProgress.cli_history,
                    activity_log: this.userProgress.activity_log
                };
                
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                console.log('💾 [TASK FIX DEBUG] Response status:', response.status);
                const result = await response.json();
                console.log('💾 [TASK FIX DEBUG] Response data:', result);
                
                if (result.success) {
                    this.lastSaveTime = new Date();
                    console.log('✅ [TASK FIX] Progress saved successfully');
                    if (!this.assignment) {
                        this.assignment = {};
                    }
                    if (typeof result.completion_percentage === 'number') {
                        this.assignment.completion_percentage = result.completion_percentage;
                        console.log(`📊 [TASK FIX DEBUG] Completion: ${result.completion_percentage}%`);
                    }
                    if (result.validation) {
                        console.log('📊 [TASK FIX DEBUG] Validation results:', result.validation);
                    }
                    this.updateProgressUI();
                } else {
                    console.error('❌ [TASK FIX DEBUG] Save failed:', result);
                }
            } catch (error) {
                console.error('❌ [TASK FIX] Error saving progress:', error);
            }
        }

        startAutoSave() {
            // Auto-save every 30 seconds
            this.autoSaveInterval = setInterval(() => {
                if (this.taskConfig?.enabled && this.userProgress.activity_log.length > 0) {
                    this.saveProgress();
                }
            }, 30000);

            console.log('⏱️ [TASK FIX] Auto-save started (30s interval)');
        }

        updateProgressUI() {
            if (!this.taskConfig?.enabled) return;

            const deviceTotal = this.taskConfig.device_requirements?.length || 0;
            const deviceCompleted = this.userProgress.devices_placed.length;
            const deviceBadge = document.getElementById('device-count-badge');
            if (deviceBadge) {
                deviceBadge.textContent = `${Math.min(deviceCompleted, deviceTotal)}/${deviceTotal}`;
            }

            const connectionTotal = this.taskConfig.connection_requirements?.length || 0;
            const connectionCompleted = this.userProgress.connections_made.length;
            const connectionBadge = document.getElementById('connection-count-badge');
            if (connectionBadge) {
                connectionBadge.textContent = `${Math.min(connectionCompleted, connectionTotal)}/${connectionTotal}`;
            }

            const cliRequirements = this.taskConfig.cli_requirements || {};
            const cliTotal = Object.values(cliRequirements).reduce((sum, cmds) => sum + cmds.length, 0);
            const cliCompleted = this.userProgress.cli_history.length;
            const cliBadge = document.getElementById('cli-count-badge');
            if (cliBadge) {
                cliBadge.textContent = `${Math.min(cliCompleted, cliTotal)}/${cliTotal}`;
            }

            const progressPercent = this.assignment?.completion_percentage ?? this.calculateCompletionFallback({
                deviceTotal,
                deviceCompleted,
                connectionTotal,
                connectionCompleted,
                cliTotal,
                cliCompleted
            });
            const percent = Math.min(Math.round(progressPercent || 0), 100);

            const progressLabel = document.getElementById('task-progress-percentage');
            if (progressLabel) {
                progressLabel.textContent = `${percent}%`;
            }

            const progressFill = document.getElementById('task-progress-fill');
            if (progressFill) {
                progressFill.style.width = `${percent}%`;
            }

            // Update device checkboxes
            this.userProgress.devices_placed.forEach(deviceId => {
                const item = document.querySelector(`#device-requirements-list .task-requirement-item[data-device-id="${deviceId}"] .requirement-status`);
                if (item) {
                    item.classList.add('completed');
                    item.classList.remove('fa-circle');
                    item.classList.add('fa-check-circle');
                }
            });

            // Update connection checkboxes - enhanced to match connection type
            const connectionReqs = this.taskConfig.connection_requirements || [];
            connectionReqs.forEach((reqConn, index) => {
                // Find matching connection in user progress
                const matchingConn = this.userProgress.connections_made.find(userConn => {
                    const sourceMatch = (userConn.source_device === reqConn.source_device || 
                                       userConn.source_device === reqConn.target_device);
                    const targetMatch = (userConn.target_device === reqConn.target_device || 
                                        userConn.target_device === reqConn.source_device);
                    const typeMatch = !reqConn.type || (userConn.connection_type === reqConn.type);
                    
                    return (sourceMatch && targetMatch && typeMatch);
                });

                if (matchingConn) {
                    const item = document.querySelector(`#connection-requirements-list .task-requirement-item[data-connection-index="${index}"] .requirement-status`);
                    if (item) {
                        item.classList.add('completed');
                        item.classList.remove('fa-circle');
                        item.classList.add('fa-check-circle');
                    }
                }
            });

            // Update CLI checkboxes
            this.userProgress.cli_history.forEach(cli => {
                // Match CLI items by device and command
                const items = document.querySelectorAll(`#cli-requirements-container .task-requirement-item[data-device-id="${cli.device_id}"] code`);
                items.forEach(codeEl => {
                    if (codeEl.textContent.includes(cli.command)) {
                        const status = codeEl.closest('.task-requirement-item')?.querySelector('.requirement-status');
                        if (status) {
                            status.classList.add('completed');
                            status.classList.remove('fa-circle');
                            status.classList.add('fa-check-circle');
                        }
                    }
                });
            });

            const submitBtn = document.getElementById('submit-task-btn');
            if (submitBtn) {
                submitBtn.disabled = !this.isTaskComplete({
                    deviceTotal,
                    deviceCompleted,
                    connectionTotal,
                    connectionCompleted,
                    cliTotal,
                    cliCompleted
                });
            }

            console.log('🎨 [TASK FIX] Progress UI updated');
        }

        calculateCompletionFallback(metrics) {
            const { deviceTotal, deviceCompleted, connectionTotal, connectionCompleted, cliTotal, cliCompleted } = metrics;
            const totals = [deviceTotal, connectionTotal, cliTotal].filter(total => total > 0);
            if (totals.length === 0) {
                return 0;
            }

            const percentages = [];
            if (deviceTotal > 0) {
                percentages.push(deviceCompleted / deviceTotal);
            }
            if (connectionTotal > 0) {
                percentages.push(connectionCompleted / connectionTotal);
            }
            if (cliTotal > 0) {
                percentages.push(cliCompleted / cliTotal);
            }

            const average = percentages.reduce((sum, value) => sum + value, 0) / percentages.length;
            return average * 100;
        }

        isTaskComplete(metrics) {
            const { deviceTotal, deviceCompleted, connectionTotal, connectionCompleted, cliTotal, cliCompleted } = metrics;
            const deviceDone = deviceTotal === 0 || deviceCompleted >= deviceTotal;
            const connectionDone = connectionTotal === 0 || connectionCompleted >= connectionTotal;
            const cliDone = cliTotal === 0 || cliCompleted >= cliTotal;
            return deviceDone && connectionDone && cliDone;
        }

        async submitTask() {
            if (!confirm('Submit task for grading? This will lock your assignment.')) {
                return;
            }

            try {
                console.log('📤 [TASK FIX] Submitting task...');
                console.log('📊 [TASK FIX] Submission data:', {
                    devices_placed: this.userProgress.devices_placed,
                    devices_configured: this.userProgress.devices_configured,
                    connections_made: this.userProgress.connections_made,
                    cli_history: this.userProgress.cli_history,
                    required_devices: this.taskConfig.device_requirements?.map(d => d.id),
                    required_connections: this.taskConfig.connection_requirements
                });
                
                const url = `/simulation/api/${this.simulationId}/submit-task`;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        devices_placed: this.userProgress.devices_placed,
                        devices_configured: this.userProgress.devices_configured,
                        connections_made: this.userProgress.connections_made,
                        cli_history: this.userProgress.cli_history
                    })
                });

                const result = await response.json();
                
                if (result.success) {
                    this.showGradingModal(result);
                    this.assignment = result.assignment;
                    this.updateProgressUI();
                } else {
                    this.showErrorModal(result.error || 'Failed to submit task');
                }
            } catch (error) {
                console.error('❌ [TASK FIX] Error submitting task:', error);
                this.showErrorModal('Failed to submit task. Please try again.');
            }
        }

        showGradingModal(result) {
            // Create modal HTML
            const modalHTML = `
                <div id="grading-result-modal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); display: flex; align-items: center; justify-content: center; z-index: 10000; animation: fadeIn 0.3s ease; padding: 1rem; overflow-y: auto;">
                    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; padding: 2rem; max-width: 500px; width: 90%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0, 217, 255, 0.3); border: 2px solid rgba(0, 217, 255, 0.3); animation: slideUp 0.3s ease; margin: auto;">
                        <div style="text-align: center; margin-bottom: 1.5rem;">
                            <div style="width: 80px; height: 80px; margin: 0 auto 1rem; background: linear-gradient(135deg, #00d9ff 0%, #0084ff 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(0, 217, 255, 0.4);">
                                <i class="fas fa-check-circle" style="font-size: 3rem; color: white;"></i>
                            </div>
                            <h2 style="color: #00d9ff; margin: 0; font-size: 1.8rem; font-weight: 700;">Task Submitted!</h2>
                        </div>
                        
                        <div style="background: rgba(0, 217, 255, 0.1); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid rgba(0, 217, 255, 0.2);">
                            <div style="text-align: center; margin-bottom: 1rem;">
                                <div style="font-size: 3rem; font-weight: 800; color: #00d9ff; text-shadow: 0 0 20px rgba(0, 217, 255, 0.5);">
                                    ${result.auto_grade_score}<span style="font-size: 1.5rem; color: #8b9dc3;">/100</span>
                                </div>
                                <div style="color: #8b9dc3; font-size: 0.9rem; margin-top: 0.5rem;">Auto-Grade Score</div>
                            </div>
                            
                            <div style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; padding: 0.75rem; margin-top: 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <span style="color: #8b9dc3; font-size: 0.9rem;">Completion Progress</span>
                                    <span style="color: #00d9ff; font-weight: 600;">${result.completion_percentage}%</span>
                                </div>
                                <div style="background: rgba(0, 0, 0, 0.5); border-radius: 6px; height: 8px; overflow: hidden;">
                                    <div style="background: linear-gradient(90deg, #00d9ff 0%, #0084ff 100%); height: 100%; width: ${result.completion_percentage}%; transition: width 0.5s ease;"></div>
                                </div>
                            </div>
                        </div>
                        
                        ${this.getValidationBreakdown(result.validation)}
                        
                        <button onclick="document.getElementById('grading-result-modal').remove()" style="width: 100%; padding: 0.875rem; background: linear-gradient(135deg, #00d9ff 0%, #0084ff 100%); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0, 217, 255, 0.4);">
                            <i class="fas fa-check"></i> Close
                        </button>
                    </div>
                </div>
                <style>
                    @keyframes fadeIn {
                        from { opacity: 0; }
                        to { opacity: 1; }
                    }
                    @keyframes slideUp {
                        from { transform: translateY(30px); opacity: 0; }
                        to { transform: translateY(0); opacity: 1; }
                    }
                </style>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        getValidationBreakdown(validation) {
            if (!validation) return '';
            
            const categories = [
                { key: 'device_placement', label: 'Device Placement', icon: 'fa-network-wired' },
                { key: 'device_configuration', label: 'Device Configuration', icon: 'fa-cog' },
                { key: 'connections', label: 'Network Connections', icon: 'fa-project-diagram' },
                { key: 'cli_commands', label: 'CLI Commands', icon: 'fa-terminal' }
            ];
            
            const items = categories.map(cat => {
                const data = validation[cat.key];
                if (!data) return '';
                
                const score = Math.round(data.score || 0);
                const color = score >= 80 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#ef4444';
                
                return `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: rgba(0, 0, 0, 0.2); border-radius: 6px; margin-bottom: 0.5rem;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <i class="fas ${cat.icon}" style="color: ${color}; font-size: 1.1rem;"></i>
                            <span style="color: #e2e8f0; font-size: 0.9rem;">${cat.label}</span>
                        </div>
                        <span style="color: ${color}; font-weight: 600; font-size: 0.95rem;">${score}%</span>
                    </div>
                `;
            }).join('');
            
            return `
                <div style="margin-bottom: 1.5rem;">
                    <div style="color: #8b9dc3; font-size: 0.85rem; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">Score Breakdown</div>
                    ${items}
                </div>
            `;
        }

        showErrorModal(errorMessage) {
            const modalHTML = `
                <div id="error-modal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); display: flex; align-items: center; justify-content: center; z-index: 10000; animation: fadeIn 0.3s ease; padding: 1rem; overflow-y: auto;">
                    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #2d1b1b 100%); border-radius: 16px; padding: 2rem; max-width: 400px; width: 90%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(239, 68, 68, 0.3); border: 2px solid rgba(239, 68, 68, 0.3); animation: slideUp 0.3s ease; margin: auto;">
                        <div style="text-align: center;">
                            <div style="width: 80px; height: 80px; margin: 0 auto 1rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(239, 68, 68, 0.4);">
                                <i class="fas fa-exclamation-circle" style="font-size: 3rem; color: white;"></i>
                            </div>
                            <h2 style="color: #ef4444; margin: 0 0 1rem 0; font-size: 1.5rem; font-weight: 700;">Submission Error</h2>
                            <p style="color: #8b9dc3; margin-bottom: 1.5rem; line-height: 1.5;">${errorMessage}</p>
                            <button onclick="document.getElementById('error-modal').remove()" style="width: 100%; padding: 0.875rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);">
                                <i class="fas fa-times"></i> Close
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        updateUI() {
            // Show/hide task panel based on config
            const taskPanel = document.getElementById('task-assignment-panel');
            if (taskPanel) {
                taskPanel.style.display = this.taskConfig?.enabled ? 'block' : 'none';
            }
        }

        destroy() {
            if (this.autoSaveInterval) {
                clearInterval(this.autoSaveInterval);
            }
            console.log('📋 [TASK FIX] Task Assignment Manager destroyed');
        }
    }

    // Replace global TaskAssignmentManager
    window.TaskAssignmentManager = EnhancedTaskAssignmentManager;

    // Auto-initialize if on simulation page
    if (window.location.pathname.includes('/dynamic/simulation/')) {
        document.addEventListener('DOMContentLoaded', () => {
            if (!window.taskAssignmentManager) {
                window.taskAssignmentManager = new EnhancedTaskAssignmentManager();
                console.log('✅ [TASK FIX] Auto-initialized task assignment manager');
            }
        });
    }

    console.log('✅ [TASK FIX] Task Assignment Fix module loaded');

})();

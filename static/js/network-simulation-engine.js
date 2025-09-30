/**
 * Comprehensive Network Simulation Engine
 * Based on troubleshoot.html, topology.html, and admin simulation editor
 * Provides full feature parity with admin simulation capabilities
 */

class NetworkSimulationEngine {
    constructor(canvasId) {
        this.canvasId = canvasId;
        this.canvas = null;
        this.ctx = null;
        
        // Network State Management
        this.devices = [];
        this.connections = [];
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.deviceIdCounter = 1;
        this.connectionIdCounter = 1;
        
        // Interaction State
        this.currentTool = 'select';
        this.isConnecting = false;
        this.isDragging = false;
        this.dragDevice = null;
        this.dragOffset = { x: 0, y: 0 };
        this.connectionStart = null;
        this.connectionPreview = null;
        
        // MVP Presenter State
        this.currentConfigDevice = null;
        
        // Viewport Management
        this.zoom = 1.0;
        this.panOffset = { x: 0, y: 0 };
        this.showGrid = true;
        this.showLabels = true;
        
        // Device Type Definitions (from troubleshoot.html)
        this.deviceTypes = {
            router: { 
                icon: 'fas fa-project-diagram', 
                color: '#3B82F6', 
                defaultPorts: 4,
                canRoute: true,
                hasConsole: true 
            },
            switch: { 
                icon: 'fas fa-ethernet', 
                color: '#10B981', 
                defaultPorts: 24,
                canRoute: false,
                hasConsole: true 
            },
            hub: { 
                icon: 'fas fa-circle-nodes', 
                color: '#F59E0B', 
                defaultPorts: 8,
                canRoute: false,
                hasConsole: false 
            },
            'access-point': { 
                icon: 'fas fa-wifi', 
                color: '#8B5CF6', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: true 
            },
            firewall: { 
                icon: 'fas fa-shield-alt', 
                color: '#EF4444', 
                defaultPorts: 2,
                canRoute: true,
                hasConsole: true 
            },
            computer: { 
                icon: 'fas fa-desktop', 
                color: '#6B7280', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: false 
            },
            laptop: { 
                icon: 'fas fa-laptop', 
                color: '#6B7280', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: false 
            },
            server: { 
                icon: 'fas fa-server', 
                color: '#1F2937', 
                defaultPorts: 2,
                canRoute: false,
                hasConsole: true 
            },
            printer: { 
                icon: 'fas fa-print', 
                color: '#7C3AED', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: false 
            },
            cloud: { 
                icon: 'fas fa-cloud', 
                color: '#3B82F6', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: false 
            },
            internet: { 
                icon: 'fas fa-globe', 
                color: '#10B981', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: false 
            },
            // Mobile & Communication Devices
            phone: { 
                icon: 'fas fa-phone', 
                color: '#10B981', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: false 
            },
            tablet: { 
                icon: 'fas fa-tablet-alt', 
                color: '#8B5CF6', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: false 
            },
            mobile: { 
                icon: 'fas fa-mobile-alt', 
                color: '#F59E0B', 
                defaultPorts: 1,
                canRoute: false,
                hasConsole: false 
            }
        };
        
        // Animation and Rendering
        this.animationFrame = null;
        this.needsRender = true;

        // Simple event system for integration bridge
        this._events = {};
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Network Simulation Engine');
        
        this.canvas = document.getElementById(this.canvasId);
        if (!this.canvas) {
            console.error('❌ Canvas not found:', this.canvasId);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.setupCanvas();
        this.setupEventListeners();
        this.startRenderLoop();
        
        console.log('✅ Network Simulation Engine initialized');
    }
    
    // ===== LIGHTWEIGHT EVENT EMITTER =====
    on(event, handler) {
        if (!this._events[event]) this._events[event] = [];
        this._events[event].push(handler);
    }

    off(event, handler) {
        if (!this._events[event]) return;
        this._events[event] = this._events[event].filter(h => h !== handler);
    }

    emit(event, payload) {
        (this._events[event] || []).forEach(h => {
            try { h(payload); } catch (e) { console.warn('Event handler error for', event, e); }
        });
    }

    setupCanvas() {
        // Set canvas size to fill container
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        this.canvas.width = Math.max(800, rect.width - 4);
        this.canvas.height = Math.max(600, rect.height - 34); // Account for status bar
        
        // Enable high DPI rendering
        const devicePixelRatio = window.devicePixelRatio || 1;
        const context = this.ctx;
        
        this.canvas.width = Math.floor(this.canvas.width * devicePixelRatio);
        this.canvas.height = Math.floor(this.canvas.height * devicePixelRatio);
        this.canvas.style.width = Math.floor(this.canvas.width / devicePixelRatio) + 'px';
        this.canvas.style.height = Math.floor(this.canvas.height / devicePixelRatio) + 'px';
        
        context.scale(devicePixelRatio, devicePixelRatio);
        
        console.log('📐 Canvas configured:', this.canvas.width / devicePixelRatio, 'x', this.canvas.height / devicePixelRatio);
    }
    
    setupEventListeners() {
        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('dblclick', (e) => this.handleDoubleClick(e));
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
        this.canvas.addEventListener('contextmenu', (e) => this.handleContextMenu(e));
        
        // Drag and drop events
        this.canvas.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.canvas.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Tool button events
        this.setupToolListeners();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Window resize
        window.addEventListener('resize', () => this.handleResize());
        
        console.log('⚡ Event listeners configured');
    }
    
    setupToolListeners() {
        // Canvas tool buttons
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tool = btn.dataset.tool;
                if (tool) this.setTool(tool);
            });
        });
        
        // Palette actions
        document.querySelectorAll('.device-item[data-action]').forEach(item => {
            item.addEventListener('click', () => {
                const action = item.dataset.action;
                this.executeAction(action);
            });
        });
        
        // Device palette drag setup
        document.querySelectorAll('.device-item[data-device-type]').forEach(item => {
            item.draggable = true;
            item.addEventListener('dragstart', (e) => this.handleDeviceDragStart(e));
        });
    }
    
    // ===== TOOL MANAGEMENT =====
    
    setTool(tool) {
        // Update tool state
        // If leaving connect mode, cancel any in-progress connection
        if (this.currentTool === 'connect' && tool !== 'connect') {
            this.cancelConnection?.();
        }
        this.currentTool = tool;
        // Do NOT mark isConnecting just by selecting the tool.
        // isConnecting should become true only after first device click.
        this.isConnecting = false;
        
        // Update UI
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.tool === tool) {
                btn.classList.add('active');
            }
        });
        
        // Update cursor
        this.updateCursor();
        
        // Update status
        this.updateCanvasMode(tool);
        
        console.log('🔧 Tool changed to:', tool);
    }
    
    updateCursor() {
        switch (this.currentTool) {
            case 'select':
                this.canvas.style.cursor = 'default';
                break;
            case 'move':
                this.canvas.style.cursor = 'move';
                break;
            case 'connect':
                this.canvas.style.cursor = 'crosshair';
                break;
            case 'delete':
                this.canvas.style.cursor = 'not-allowed';
                break;
            default:
                this.canvas.style.cursor = 'default';
        }
    }
    
    executeAction(action) {
        switch (action) {
            case 'connect-mode':
                this.setTool('connect');
                break;
            case 'configure-mode':
                if (this.selectedDevice) {
                    this.presentDeviceConfiguration(this.selectedDevice);
                }
                break;
            case 'terminal-mode':
                this.toggleCLI();
                break;
            case 'test-mode':
                this.runNetworkTests();
                break;
            case 'reset':
                this.resetNetwork();
                break;
            case 'save':
                this.saveTopology();
                break;
            case 'zoom-in':
                this.zoomIn();
                break;
            case 'zoom-out':
                this.zoomOut();
                break;
        }
    }
    
    // ===== DEVICE MANAGEMENT =====
    
    handleDeviceDragStart(e) {
        const deviceType = e.target.closest('.device-item').dataset.deviceType;
        e.dataTransfer.setData('text/plain', deviceType);
        e.dataTransfer.effectAllowed = 'copy';
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    }
    
    handleDrop(e) {
        e.preventDefault();
        const deviceType = e.dataTransfer.getData('text/plain');
        
        if (deviceType && this.deviceTypes[deviceType]) {
            const rect = this.canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) / this.zoom - this.panOffset.x;
            const y = (e.clientY - rect.top) / this.zoom - this.panOffset.y;
            
            this.createDevice(deviceType, x, y);
        }
    }
    
    createDevice(type, x, y) {
        const typeInfo = this.deviceTypes[type];
        if (!typeInfo) return null;
        
        const device = {
            id: `${type}_${this.deviceIdCounter++}`,
            type: type,
            x: x,
            y: y,
            width: 60,
            height: 60,
            label: `${type.charAt(0).toUpperCase() + type.slice(1)} ${this.deviceIdCounter - 1}`,
            // Provide a name alias for configurators expecting device.name
            name: `${type.charAt(0).toUpperCase() + type.slice(1)} ${this.deviceIdCounter - 1}`,
            icon: typeInfo.icon,
            color: typeInfo.color,
            selected: false,
            config: this.getDefaultDeviceConfig(type),
            interfaces: this.generateInterfaces(typeInfo.defaultPorts, type),
            connections: []
        };
        
        this.devices.push(device);
        this.selectDevice(device);
        this.updateDeviceCount();
        this.needsRender = true;
        
        console.log('✅ Created device:', device.id);
        this.emit('device-added', device);
        return device;
    }
    
    getDefaultDeviceConfig(type) {
        const typeInfo = this.deviceTypes[type];
        
        return {
            hostname: `${type}${this.deviceIdCounter - 1}`,
            ipAddress: this.generateIPAddress(),
            subnetMask: '255.255.255.0',
            gateway: '192.168.1.1',
            vlan: 1,
            enabledServices: [],
            interfaces: {},
            routingTable: [],
            staticRoutes: [],
            accessLists: []
        };
    }
    
    generateInterfaces(count, type) {
        const interfaces = {};
        const typeInfo = this.deviceTypes[type];
        
        if (typeInfo && typeInfo.canRoute) {
            // Router/Firewall interfaces
            for (let i = 0; i < count; i++) {
                interfaces[`FastEthernet0/${i}`] = {
                    name: `FastEthernet0/${i}`,
                    type: 'ethernet',
                    ipAddress: '',
                    subnetMask: '',
                    status: 'up',
                    connected: false
                };
            }
        } else {
            // Switch/Hub interfaces
            for (let i = 1; i <= count; i++) {
                interfaces[`Port${i}`] = {
                    name: `Port${i}`,
                    type: 'ethernet',
                    vlan: 1,
                    status: 'up',
                    connected: false
                };
            }
        }
        
        return interfaces;
    }
    
    generateIPAddress() {
        const subnet = '192.168.1.';
        const host = Math.floor(Math.random() * 200) + 10;
        return subnet + host;
    }
    
    // ===== CONNECTION MANAGEMENT =====
    
    createConnection(device1, device2, port1 = null, port2 = null) {
        // Prevent duplicate connections
        const existingConnection = this.connections.find(conn => 
            (conn.device1.id === device1.id && conn.device2.id === device2.id) ||
            (conn.device1.id === device2.id && conn.device2.id === device1.id)
        );
        
        if (existingConnection) {
            console.warn('⚠️ Connection already exists between devices');
            return null;
        }
        
        // Find available ports
        const availablePort1 = port1 || this.findAvailablePort(device1);
        const availablePort2 = port2 || this.findAvailablePort(device2);
        
        if (!availablePort1 || !availablePort2) {
            console.warn('⚠️ No available ports for connection');
            return null;
        }
        
        const connection = {
            id: `conn_${this.connectionIdCounter++}`,
            device1: device1,
            device2: device2,
            port1: availablePort1,
            port2: availablePort2,
            type: 'ethernet',
            status: 'up',
            selected: false
        };
        
        this.connections.push(connection);
        
        // Mark ports as connected
        if (device1.interfaces[availablePort1]) {
            device1.interfaces[availablePort1].connected = true;
        }
        if (device2.interfaces[availablePort2]) {
            device2.interfaces[availablePort2].connected = true;
        }
        
        // Update device connections list
        device1.connections.push(connection);
        device2.connections.push(connection);
        
        this.updateConnectionCount();
        this.needsRender = true;
        
        console.log('🔗 Created connection:', connection.id);
        this.emit('connection-created', connection);
        return connection;
    }
    
    findAvailablePort(device) {
        const interfaces = Object.keys(device.interfaces);
        return interfaces.find(port => !device.interfaces[port].connected);
    }
    
    deleteConnection(connection) {
        // Mark ports as disconnected
        if (connection.device1.interfaces[connection.port1]) {
            connection.device1.interfaces[connection.port1].connected = false;
        }
        if (connection.device2.interfaces[connection.port2]) {
            connection.device2.interfaces[connection.port2].connected = false;
        }
        
        // Remove from device connections
        connection.device1.connections = connection.device1.connections.filter(c => c.id !== connection.id);
        connection.device2.connections = connection.device2.connections.filter(c => c.id !== connection.id);
        
        // Remove from connections array
        this.connections = this.connections.filter(c => c.id !== connection.id);
        
        this.updateConnectionCount();
        this.needsRender = true;
        
        console.log('🗑️ Deleted connection:', connection.id);
        this.emit('connection-deleted', connection);
    }
    
    // ===== MOUSE INTERACTION HANDLERS =====
    
    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) / this.zoom - this.panOffset.x;
        const mouseY = (e.clientY - rect.top) / this.zoom - this.panOffset.y;
        
        const clickedDevice = this.getDeviceAt(mouseX, mouseY);
        const clickedConnection = this.getConnectionAt(mouseX, mouseY);
        
        if (this.currentTool === 'select' || this.currentTool === 'move') {
            if (clickedDevice) {
                this.selectDevice(clickedDevice);
                if (this.currentTool === 'move' || e.button === 0) {
                    this.isDragging = true;
                    this.dragDevice = clickedDevice;
                    this.dragOffset = {
                        x: mouseX - clickedDevice.x,
                        y: mouseY - clickedDevice.y
                    };
                }
            } else if (clickedConnection) {
                this.selectConnection(clickedConnection);
            } else {
                this.clearSelection();
            }
        } else if (this.currentTool === 'connect') {
            if (clickedDevice && !this.isConnecting) {
                this.startConnection(clickedDevice, mouseX, mouseY);
            } else if (clickedDevice && this.isConnecting && this.connectionStart && clickedDevice !== this.connectionStart.device) {
                this.completeConnection(clickedDevice);
            }
        } else if (this.currentTool === 'delete') {
            if (clickedDevice) {
                this.deleteDevice(clickedDevice);
            } else if (clickedConnection) {
                this.deleteConnection(clickedConnection);
            }
        }
        
        this.needsRender = true;
    }
    
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) / this.zoom - this.panOffset.x;
        const mouseY = (e.clientY - rect.top) / this.zoom - this.panOffset.y;
        
        // Update coordinates display
        this.updateCanvasCoords(Math.round(mouseX), Math.round(mouseY));
        
        if (this.isDragging && this.dragDevice) {
            this.dragDevice.x = mouseX - this.dragOffset.x;
            this.dragDevice.y = mouseY - this.dragOffset.y;
            this.needsRender = true;
        }
        
        if (this.currentTool === 'connect' && this.isConnecting && this.connectionStart) {
            this.connectionPreview = { x: mouseX, y: mouseY };
            this.needsRender = true;
        }
    }
    
    handleMouseUp(e) {
        this.isDragging = false;
        this.dragDevice = null;
        this.dragOffset = { x: 0, y: 0 };
    }
    
    handleDoubleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) / this.zoom - this.panOffset.x;
        const mouseY = (e.clientY - rect.top) / this.zoom - this.panOffset.y;
        
        const clickedDevice = this.getDeviceAt(mouseX, mouseY);
        
        if (clickedDevice) {
            // Show MVP Device Interfaces popup
            this.showMVPDeviceInterfacesPopup(clickedDevice);
        }
    }
    
    handleClick(e) {
        // Prevent default click behavior after drag
        if (this.isDragging) {
            e.preventDefault();
        }
    }
    
    handleContextMenu(e) {
        e.preventDefault();
        // TODO: Implement context menu
    }
    
    handleWheel(e) {
        e.preventDefault();
        
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
        const newZoom = Math.max(0.1, Math.min(3.0, this.zoom * zoomFactor));
        
        if (newZoom !== this.zoom) {
            const zoomDiff = newZoom / this.zoom;
            this.panOffset.x = (this.panOffset.x - mouseX / this.zoom) * zoomDiff + mouseX / newZoom;
            this.panOffset.y = (this.panOffset.y - mouseY / this.zoom) * zoomDiff + mouseY / newZoom;
            this.zoom = newZoom;
            this.needsRender = true;
        }
    }
    
    handleKeyDown(e) {
        // Guard: ignore global shortcuts when focus is inside any CLI/input element
        const active = document.activeElement;
        const isFormEl = active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable);
        const inMVPOverlay = !!(active && active.closest && active.closest('#mvp-device-interfaces'));
        const isCLI = isFormEl && (
            active.classList.contains('cli-input') ||
            active.classList.contains('mvp-cli-input') ||
            active.id === 'mvp-cli-input' ||
            (active.id && active.id.startsWith('cli-input-'))
        );
        const isConfigInput = isFormEl && inMVPOverlay && active.classList.contains('mvp-input');

        if (isCLI || isConfigInput) {
            // Allow full native editing including Backspace/Delete/Arrows.
            // Only intercept our explicit Ctrl+ shortcuts if desired.
            if (e.ctrlKey) {
                if (e.key === 's') { e.preventDefault(); this.setTool('select'); }
                if (e.key === 'm') { e.preventDefault(); this.setTool('move'); }
                // NOTE: Don't hijack Ctrl+C/X/V inside CLI
            }
            return; // Never process further while typing in CLI
        } else if (isFormEl) {
            // In other generic inputs, preserve copy/paste; only custom shortcuts if safe
            if (e.ctrlKey && e.key === 's') { e.preventDefault(); this.setTool('select'); }
            return;
        }
        
        // Normal keyboard shortcuts when not typing
        switch (e.key) {
            case 'Delete':
                if (this.selectedDevice) {
                    this.deleteDevice(this.selectedDevice);
                } else if (this.selectedConnection) {
                    this.deleteConnection(this.selectedConnection);
                }
                break;
            case 'Escape':
                this.cancelConnection();
                this.clearSelection();
                break;
            case 's':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.setTool('select');
                }
                break;
            case 'c':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.setTool('connect');
                }
                break;
            case 'm':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.setTool('move');
                }
                break;
        }
    }
    
    handleResize() {
        this.setupCanvas();
        this.needsRender = true;
    }
    
    // ===== DEVICE INTERACTION =====
    
    getDeviceAt(x, y) {
        // Check devices in reverse order (top device first)
        for (let i = this.devices.length - 1; i >= 0; i--) {
            const device = this.devices[i];
            if (x >= device.x - device.width / 2 &&
                x <= device.x + device.width / 2 &&
                y >= device.y - device.height / 2 &&
                y <= device.y + device.height / 2) {
                return device;
            }
        }
        return null;
    }
    
    getConnectionAt(x, y) {
        const tolerance = 5;
        
        for (const connection of this.connections) {
            const dist = this.distanceToLine(
                x, y,
                connection.device1.x, connection.device1.y,
                connection.device2.x, connection.device2.y
            );
            
            if (dist <= tolerance) {
                return connection;
            }
        }
        
        return null;
    }
    
    distanceToLine(px, py, x1, y1, x2, y2) {
        const A = px - x1;
        const B = py - y1;
        const C = x2 - x1;
        const D = y2 - y1;
        
        const dot = A * C + B * D;
        const lenSq = C * C + D * D;
        
        if (lenSq === 0) return Math.sqrt(A * A + B * B);
        
        let t = Math.max(0, Math.min(1, dot / lenSq));
        
        const projection = {
            x: x1 + t * C,
            y: y1 + t * D
        };
        
        const dx = px - projection.x;
        const dy = py - projection.y;
        
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    selectDevice(device) {
        this.clearSelection();
        device.selected = true;
        this.selectedDevice = device;
        this.needsRender = true;
        
        console.log('📱 Selected device:', device.id, '(Double-click to open MVP Device Interfaces)');
        
        // Optional: Show a brief notification or tooltip about double-click
        this.showDeviceSelectionHint(device);
    }
    
    selectConnection(connection) {
        this.clearSelection();
        connection.selected = true;
        this.selectedConnection = connection;
        this.needsRender = true;
        
        console.log('🔗 Selected connection:', connection.id);
    }
    
    clearSelection() {
        this.devices.forEach(device => device.selected = false);
        this.connections.forEach(connection => connection.selected = false);
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.needsRender = true;
    }
    
    deleteDevice(device) {
        // Remove all connections to this device
        const connectionsToRemove = this.connections.filter(conn => 
            conn.device1.id === device.id || conn.device2.id === device.id
        );
        
        connectionsToRemove.forEach(conn => this.deleteConnection(conn));
        
        // Remove device
        this.devices = this.devices.filter(d => d.id !== device.id);
        
        if (this.selectedDevice === device) {
            this.selectedDevice = null;
        }
        
        this.updateDeviceCount();
        this.needsRender = true;
        
        console.log('🗑️ Deleted device:', device.id);
        this.emit('device-deleted', device);
    }
    
    // ===== CONNECTION INTERACTION =====
    
    startConnection(device, x, y) {
        this.isConnecting = true;
        this.connectionStart = { device, x, y };
        this.connectionPreview = null;
        
        console.log('🔗 Started connection from:', device.id);
    }
    
    completeConnection(endDevice) {
        if (this.connectionStart && endDevice !== this.connectionStart.device) {
            this.createConnection(this.connectionStart.device, endDevice);
        }
        
        this.cancelConnection();
    }
    
    cancelConnection() {
        this.isConnecting = false;
        this.connectionStart = null;
        this.connectionPreview = null;
        this.needsRender = true;
    }
    
    // ===== RENDERING SYSTEM =====
    
    startRenderLoop() {
        const render = () => {
            if (this.needsRender) {
                this.render();
                this.needsRender = false;
            }
            this.animationFrame = requestAnimationFrame(render);
        };
        render();
    }
    
    render() {
        this.ctx.save();
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Apply zoom and pan
        this.ctx.scale(this.zoom, this.zoom);
        this.ctx.translate(this.panOffset.x, this.panOffset.y);
        
        // Render grid
        if (this.showGrid) {
            this.renderGrid();
        }
        
        // Render connections
        this.renderConnections();
        
        // Render connection preview
        if (this.connectionPreview && this.connectionStart) {
            this.renderConnectionPreview();
        }
        
        // Render devices
        this.renderDevices();
        
        this.ctx.restore();
    }
    
    renderGrid() {
        const gridSize = 20;
        const startX = Math.floor(-this.panOffset.x / gridSize) * gridSize;
        const startY = Math.floor(-this.panOffset.y / gridSize) * gridSize;
        const endX = startX + (this.canvas.width / this.zoom) + gridSize;
        const endY = startY + (this.canvas.height / this.zoom) + gridSize;
        
        this.ctx.strokeStyle = 'rgba(0, 217, 255, 0.1)';
        this.ctx.lineWidth = 1 / this.zoom;
        this.ctx.beginPath();
        
        for (let x = startX; x <= endX; x += gridSize) {
            this.ctx.moveTo(x, startY);
            this.ctx.lineTo(x, endY);
        }
        
        for (let y = startY; y <= endY; y += gridSize) {
            this.ctx.moveTo(startX, y);
            this.ctx.lineTo(endX, y);
        }
        
        this.ctx.stroke();
    }
    
    renderConnections() {
        this.ctx.lineWidth = 3 / this.zoom;
        
        this.connections.forEach(connection => {
            const color = connection.selected ? '#39FF14' : '#00D9FF';
            const alpha = connection.status === 'up' ? 1.0 : 0.5;
            
            this.ctx.strokeStyle = color;
            this.ctx.globalAlpha = alpha;
            
            this.ctx.beginPath();
            this.ctx.moveTo(connection.device1.x, connection.device1.y);
            this.ctx.lineTo(connection.device2.x, connection.device2.y);
            this.ctx.stroke();
            
            // Connection status indicator
            if (connection.selected) {
                const midX = (connection.device1.x + connection.device2.x) / 2;
                const midY = (connection.device1.y + connection.device2.y) / 2;
                
                this.ctx.fillStyle = color;
                this.ctx.beginPath();
                this.ctx.arc(midX, midY, 4 / this.zoom, 0, Math.PI * 2);
                this.ctx.fill();
            }
            
            this.ctx.globalAlpha = 1.0;
        });
    }
    
    renderConnectionPreview() {
        if (!this.connectionStart || !this.connectionPreview) return;
        
        this.ctx.strokeStyle = 'rgba(0, 217, 255, 0.6)';
        this.ctx.lineWidth = 3 / this.zoom;
        this.ctx.setLineDash([5 / this.zoom, 5 / this.zoom]);
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.connectionStart.device.x, this.connectionStart.device.y);
        this.ctx.lineTo(this.connectionPreview.x, this.connectionPreview.y);
        this.ctx.stroke();
        
        this.ctx.setLineDash([]);
    }
    
    renderDevices() {
        this.devices.forEach(device => {
            this.renderDevice(device);
        });
    }
    
    renderDevice(device) {
        const x = device.x;
        const y = device.y;
        const size = Math.max(device.width, device.height);
        
        // Device background
        this.ctx.fillStyle = device.selected ? 
            'rgba(57, 255, 20, 0.2)' : 'rgba(15, 23, 42, 0.9)';
        this.ctx.strokeStyle = device.selected ? '#39FF14' : device.color;
        this.ctx.lineWidth = device.selected ? 3 / this.zoom : 2 / this.zoom;
        
        this.ctx.fillRect(x - size/2, y - size/2, size, size);
        this.ctx.strokeRect(x - size/2, y - size/2, size, size);
        
        // Device icon (using text as placeholder for FontAwesome icons)
        this.ctx.fillStyle = device.selected ? '#39FF14' : '#F8FAFC';
        this.ctx.font = `${20 / this.zoom}px "Font Awesome 6 Free"`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        // Get icon character based on device type
        let iconChar = this.getIconChar(device.type);
        this.ctx.fillText(iconChar, x, y);
        
        // Device label
        if (this.showLabels) {
            this.ctx.font = `${12 / this.zoom}px "Inter", sans-serif`;
            this.ctx.fillStyle = '#CBD5E1';
            this.ctx.fillText(device.label, x, y + size/2 + 15/this.zoom);
        }
        
        // Connection points (when selected or connecting)
        if (device.selected || (this.currentTool === 'connect' && this.isConnecting)) {
            this.renderConnectionPoints(device);
        }
    }
    
    getIconChar(deviceType) {
        // FontAwesome icon characters (simplified mapping)
        const iconMap = {
            router: '🔀',
            switch: '🔌',
            hub: '⚡',
            'access-point': '📶',
            firewall: '🛡️',
            computer: '🖥️',
            laptop: '💻',
            server: '🖥️',
            printer: '🖨️',
            cloud: '☁️',
            internet: '🌐',
            // Mobile & Communication devices
            phone: '📞',
            tablet: '📱',
            mobile: '📱'
        };
        
        return iconMap[deviceType] || '📦';
    }
    
    renderConnectionPoints(device) {
        const pointSize = 6 / this.zoom;
        const positions = [
            { x: device.x, y: device.y - device.height/2 }, // top
            { x: device.x + device.width/2, y: device.y }, // right
            { x: device.x, y: device.y + device.height/2 }, // bottom
            { x: device.x - device.width/2, y: device.y }  // left
        ];
        
        this.ctx.fillStyle = '#00D9FF';
        positions.forEach(pos => {
            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y, pointSize, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }
    
    // ===== UTILITY METHODS =====
    
    updateDeviceCount() {
        const counter = document.getElementById('device-count');
        if (counter) {
            counter.textContent = `Devices: ${this.devices.length}`;
        }
    }
    
    updateConnectionCount() {
        const counter = document.getElementById('connection-count');
        if (counter) {
            counter.textContent = `Connections: ${this.connections.length}`;
        }
    }
    
    updateCanvasCoords(x, y) {
        const coords = document.getElementById('canvas-coords');
        if (coords) {
            coords.textContent = `Cursor: (${x}, ${y})`;
        }
    }
    
    updateCanvasMode(mode) {
        const modeDisplay = document.getElementById('canvas-mode');
        if (modeDisplay) {
            const modeNames = {
                select: 'Select',
                move: 'Move',
                connect: 'Connect',
                delete: 'Delete'
            };
            modeDisplay.textContent = `Mode: ${modeNames[mode] || mode}`;
        }
    }
    
    // ===== ADVANCED FEATURES =====
    
    // ===== MVP (MODEL-VIEW-PRESENTER) PATTERN IMPLEMENTATION =====
    
    /**
     * Presenter method for device configuration
     * Manages the Model-View-Presenter pattern properly
     * 
     * MVP Flow:
     * 1. User interaction (double-click, button click) goes to Presenter
     * 2. Presenter clears existing Views to prevent duplicates  
     * 3. Presenter loads appropriate View for the Model (device)
     * 4. View handles user input and communicates back through Presenter
     */
    presentDeviceConfiguration(device) {
        console.log('⚙️ Presenter: Opening device config for:', device.id);
        
        // Store current device in Presenter state
        this.currentConfigDevice = device;
        
        // Clear any existing Views first (MVP pattern)
        this.clearExistingDeviceViews();
        
        // Route to appropriate View through Presenter
        this.openDeviceConfig(device);
    }
    
    /**
     * Presenter method to close device configuration Views
     * Properly manages View state without breaking reinitialization
     */
    closeDeviceConfiguration() {
        console.log('🔒 Presenter: Closing device configuration Views');
        
        // Hide all device configuration Views but keep them in DOM for reuse
        const modalSelectors = [
            '#device-config-modal',
            '#enhanced-device-config-modal', 
            '#network-device-config-modal',
            '#ipConfigModal',
            '#device-interface-panel'
        ];
        
        modalSelectors.forEach(selector => {
            const modal = document.querySelector(selector);
            if (modal) {
                // Hide View but preserve it for reuse
                modal.classList.remove('active', 'show');
                modal.style.display = 'none';
                
                // Clear any device-specific data
                if (modal.dataset.deviceId) {
                    delete modal.dataset.deviceId;
                }
                
                // Only remove interface panels since they're dynamically created
                if (selector === '#device-interface-panel') {
                    modal.remove();
                }
            }
        });
        
        // Reset Presenter state
        this.currentConfigDevice = null;
        
        console.log('✅ Presenter: Device configuration Views closed and ready for reuse');
    }
    
    /**
     * Clear existing device configuration Views to prevent duplicates
     * Part of MVP Presenter responsibility
     */
    clearExistingDeviceViews() {
        // Hide existing device config modals (but keep them for reuse)
        const existingModals = [
            '#device-config-modal',
            '#enhanced-device-config-modal', 
            '#network-device-config-modal',
            '#ipConfigModal'
        ];
        
        // Always remove interface panels since they're recreated each time
        const panelsToRemove = ['#device-interface-panel'];
        
        existingModals.forEach(selector => {
            const modal = document.querySelector(selector);
            if (modal) {
                // Hide View but preserve for reuse
                modal.classList.remove('active', 'show');
                modal.style.display = 'none';
            }
        });
        
        panelsToRemove.forEach(selector => {
            const panel = document.querySelector(selector);
            if (panel) {
                panel.remove(); // These are recreated each time
            }
        });
        
        console.log('🧹 Presenter: Hidden existing device Views (preserved for reuse)');
    }
    
    /**
     * Check if any device configuration Views are currently open
     * Useful for Presenter state management
     */
    hasOpenDeviceViews() {
        const modalSelectors = [
            '#device-config-modal',
            '#enhanced-device-config-modal', 
            '#network-device-config-modal',
            '#ipConfigModal',
            '#device-interface-panel'
        ];
        
        return modalSelectors.some(selector => {
            const modal = document.querySelector(selector);
            return modal && (modal.classList.contains('active') || modal.classList.contains('show') || modal.style.display === 'flex');
        });
    }
    
    /**
     * Test method to verify Presenter can reopen Views after closing
     * Useful for debugging MVP pattern issues
     */
    testDeviceViewReinitialization() {
        console.log('🧪 Testing device View reinitialization...');
        
        // Find a test device
        const testDevice = this.devices.length > 0 ? this.devices[0] : null;
        if (!testDevice) {
            console.warn('⚠️ No devices available for testing');
            return false;
        }
        
        // Test 1: Open device config
        console.log('📋 Test 1: Opening device config');
        this.presentDeviceConfiguration(testDevice);
        
        setTimeout(() => {
            // Test 2: Close device config
            console.log('📋 Test 2: Closing device config');
            this.closeDeviceConfiguration();
            
            setTimeout(() => {
                // Test 3: Reopen device config
                console.log('📋 Test 3: Reopening device config');
                this.presentDeviceConfiguration(testDevice);
                
                console.log('✅ Device View reinitialization test completed');
            }, 500);
        }, 1000);
        
        return true;
    }
    
    /**
     * Presenter method to check and reinitialize Views if needed
     * Ensures Views are available for reuse
     */
    ensureViewsAvailable() {
        // Check if the main device config modal exists, create if not
        if (!document.getElementById('device-config-modal')) {
            console.log('🔄 Presenter: Reinitializing device config modal');
            this.createDeviceConfigModal();
        }
        
        // Note: Other configurators (enhanced, network, etc.) create their own modals
        // Interface panels are always recreated, so no need to check for them
        
        return true;
    }
    
    openDeviceConfig(device) {
        console.log('⚙️ Opening device config for:', device.id);
        
        // Use new MVP Device Interfaces popup
        this.showMVPDeviceInterfacesPopup(device);
    }

    // ===== NEW MVP DEVICE INTERFACES IMPLEMENTATION =====
    
    /**
     * Show the MVP Device Interfaces popup with Config and CLI tabs
     */
    showMVPDeviceInterfacesPopup(device) {
        console.log(`🖥️ MVP: Opening Device Interfaces for ${device.label || device.name}`);
        
        // Clear any existing device popups first (MVP pattern)
        this.clearExistingDeviceViews();
        
        // Create the new MVP Device Interfaces popup
        const modalHtml = this.createMVPDeviceInterfacesHTML(device);
        
        // Add to DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Store current device reference in Presenter state
        this.currentConfigDevice = device;
        
        // Setup event listeners for the new popup
        this.setupMVPInterfacesEventListeners(device);
        
        // Initialize with Config tab active
        this.switchMVPDeviceTab('config');
        
        // Focus first input after animation completes
        setTimeout(() => {
            const firstInput = document.querySelector('#mvp-device-interfaces input:first-of-type');
            if (firstInput) firstInput.focus();
        }, 300);
    }
    
    /**
     * Generate the HTML for the MVP Device Interfaces popup
     */
    createMVPDeviceInterfacesHTML(device) {
        const deviceIcon = this.getIconChar(device.type);
        const interfaces = device.interfaces || {};
        const interfaceKeys = Object.keys(interfaces);
        const totalInterfaces = interfaceKeys.length;
        const activeInterfaces = interfaceKeys.filter(key => 
            interfaces[key].status === 'up' || (!interfaces[key].status && interfaces[key].connected)
        ).length;
        const connectedInterfaces = interfaceKeys.filter(key => interfaces[key].connected).length;
        
        // Calculate health status
        let healthStatus = 'Excellent';
        let healthColor = '#10B981';
        const healthRatio = totalInterfaces > 0 ? activeInterfaces / totalInterfaces : 1;
        if (healthRatio < 0.8) {
            healthStatus = 'Good';
            healthColor = '#F59E0B';
        }
        if (healthRatio < 0.6) {
            healthStatus = 'Fair';
            healthColor = '#F97316';
        }
        if (healthRatio < 0.3) {
            healthStatus = 'Poor';
            healthColor = '#EF4444';
        }
        
        return `
        <div id="mvp-device-interfaces" class="mvp-device-interfaces-overlay">
            <div class="mvp-device-interfaces-backdrop" onclick="window.networkEngine.closeMVPDeviceInterfaces()"></div>
            <div class="mvp-device-interfaces-modal">
                <div class="mvp-interfaces-header">
                    <div class="mvp-interfaces-title">
                        <div class="mvp-device-icon">${deviceIcon}</div>
                        <div class="mvp-title-text">
                            <h3>Device Interfaces</h3>
                            <span class="mvp-device-subtitle">${device.label || device.name} • ${device.type.charAt(0).toUpperCase() + device.type.slice(1)}</span>
                        </div>
                    </div>
                    <div class="mvp-interfaces-controls">
                        <button class="mvp-btn mvp-btn-info" onclick="window.networkEngine.refreshMVPInterfaces()" title="Refresh">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        <button class="mvp-btn mvp-btn-secondary" onclick="window.networkEngine.closeMVPDeviceInterfaces()" title="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <div class="mvp-interfaces-tabs">
                    <button class="mvp-tab-btn mvp-tab-active" data-tab="config" onclick="window.networkEngine.switchMVPDeviceTab('config')">
                        <i class="fas fa-cogs"></i>
                        <span>Configure</span>
                    </button>
                    <button class="mvp-tab-btn" data-tab="cli" onclick="window.networkEngine.switchMVPDeviceTab('cli')">
                        <i class="fas fa-terminal"></i>
                        <span>CLI</span>
                    </button>
                </div>
                
                <div class="mvp-interfaces-content">
                    <!-- Config Tab Content -->
                    <div id="mvp-config-tab" class="mvp-tab-content mvp-tab-active">
                        <div class="mvp-device-overview">
                            <h4><i class="fas fa-info-circle"></i> Device Overview</h4>
                            <div class="mvp-overview-grid">
                                <div class="mvp-stat-card">
                                    <div class="mvp-stat-icon">
                                        <i class="fas fa-ethernet"></i>
                                    </div>
                                    <div class="mvp-stat-content">
                                        <div class="mvp-stat-value">${totalInterfaces}</div>
                                        <div class="mvp-stat-label">Total Interfaces</div>
                                    </div>
                                </div>
                                <div class="mvp-stat-card">
                                    <div class="mvp-stat-icon mvp-stat-active">
                                        <i class="fas fa-arrow-up"></i>
                                    </div>
                                    <div class="mvp-stat-content">
                                        <div class="mvp-stat-value">${activeInterfaces}</div>
                                        <div class="mvp-stat-label">Active</div>
                                    </div>
                                </div>
                                <div class="mvp-stat-card">
                                    <div class="mvp-stat-icon mvp-stat-connected">
                                        <i class="fas fa-link"></i>
                                    </div>
                                    <div class="mvp-stat-content">
                                        <div class="mvp-stat-value">${connectedInterfaces}</div>
                                        <div class="mvp-stat-label">Connected</div>
                                    </div>
                                </div>
                                <div class="mvp-stat-card">
                                    <div class="mvp-stat-icon mvp-stat-health" style="color: ${healthColor}">
                                        <i class="fas fa-heartbeat"></i>
                                    </div>
                                    <div class="mvp-stat-content">
                                        <div class="mvp-stat-value" style="color: ${healthColor}">${healthStatus}</div>
                                        <div class="mvp-stat-label">Health</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mvp-device-config">
                            <h4><i class="fas fa-cog"></i> Device Configuration</h4>
                            <div class="mvp-config-form">
                                <div class="mvp-form-row">
                                    <div class="mvp-form-group">
                                        <label>Hostname</label>
                                        <input type="text" id="mvp-hostname" value="${device.config?.hostname || device.label || device.name}" class="mvp-input">
                                    </div>
                                    <div class="mvp-form-group">
                                        <label>IP Address</label>
                                        <input type="text" id="mvp-ip-address" value="${device.config?.ipAddress || ''}" class="mvp-input" placeholder="192.168.1.1">
                                    </div>
                                </div>
                                <div class="mvp-form-row">
                                    <div class="mvp-form-group">
                                        <label>Subnet Mask</label>
                                        <input type="text" id="mvp-subnet-mask" value="${device.config?.subnetMask || ''}" class="mvp-input" placeholder="255.255.255.0">
                                    </div>
                                    <div class="mvp-form-group">
                                        <label>Default Gateway</label>
                                        <input type="text" id="mvp-gateway" value="${device.config?.gateway || ''}" class="mvp-input" placeholder="192.168.1.1">
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mvp-interfaces-list">
                            <h4><i class="fas fa-list"></i> Interface Details</h4>
                            ${this.generateMVPInterfacesList(device)}
                        </div>
                        
                        <div class="mvp-config-actions">
                            <button class="mvp-btn mvp-btn-primary" onclick="window.networkEngine.saveMVPDeviceConfig()">
                                <i class="fas fa-save"></i>
                                Save Configuration
                            </button>
                            <button class="mvp-btn mvp-btn-secondary" onclick="window.networkEngine.resetMVPDeviceConfig()">
                                <i class="fas fa-undo"></i>
                                Reset
                            </button>
                        </div>
                    </div>
                    
                    <!-- CLI Tab Content -->
                    <div id="mvp-cli-tab" class="mvp-tab-content">
                        <div class="mvp-cli-container">
                            <div class="mvp-cli-header">
                                <div class="mvp-cli-info">
                                    <span class="mvp-cli-hostname">${device.label || device.name || 'Device'}</span>
                                    <span class="mvp-cli-status">Connected</span>
                                </div>
                                <div class="mvp-cli-actions">
                                    <button class="mvp-btn mvp-btn-sm" onclick="window.networkEngine.clearMVPCLI()" title="Clear">
                                        <i class="fas fa-broom"></i>
                                    </button>
                                    <button class="mvp-btn mvp-btn-sm" onclick="window.networkEngine.saveMVPCLIConfig()" title="Save Config">
                                        <i class="fas fa-save"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="mvp-cli-output" id="mvp-cli-output">
                                <div class="mvp-cli-welcome">
                                    Welcome to ${device.label || device.name} CLI<br>
                                    RiddleNet Device Simulator v1.0<br>
                                    Type 'help' for available commands.<br><br>
                                </div>
                            </div>
                            <div class="mvp-cli-input-container">
                                <span class="mvp-cli-prompt">${device.label || device.name}#</span>
                                <input type="text" class="mvp-cli-input" id="mvp-cli-input" 
                                       onkeydown="window.networkEngine.handleMVPCLIInput(event)"
                                       placeholder="Enter command..." autocomplete="off" spellcheck="false">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    }
    
    /**
     * Generate the interfaces list HTML for the Config tab
     */
    generateMVPInterfacesList(device) {
        const interfaces = device.interfaces || {};
        const interfaceKeys = Object.keys(interfaces);
        
        if (interfaceKeys.length === 0) {
            return '<p class="mvp-no-interfaces">No interfaces configured</p>';
        }
        
        let html = '<div class="mvp-interfaces-grid">';
        
        interfaceKeys.forEach(intName => {
            const intData = interfaces[intName];
            const status = intData.status || (intData.connected ? 'up' : 'down');
            const speed = this.getInterfaceSpeed(device.type, intName);
            const lastChange = this.getRandomLastChange();
            
            html += `
            <div class="mvp-interface-card mvp-interface-${status}">
                <div class="mvp-interface-header">
                    <span class="mvp-interface-name">${intName}</span>
                    <span class="mvp-interface-status mvp-status-${status}">${status.toUpperCase()}</span>
                </div>
                <div class="mvp-interface-details">
                    <div class="mvp-interface-detail">
                        <strong>IP:</strong> ${intData.ipAddress || 'Not assigned'}
                    </div>
                    <div class="mvp-interface-detail">
                        <strong>Subnet:</strong> ${intData.subnetMask || 'Not configured'}
                    </div>
                    <div class="mvp-interface-detail">
                        <strong>Speed:</strong> ${speed}
                    </div>
                    <div class="mvp-interface-detail">
                        <strong>Link:</strong> ${intData.connected ? 'Connected' : 'Disconnected'}
                    </div>
                    <div class="mvp-interface-detail">
                        <strong>Last Change:</strong> ${lastChange}
                    </div>
                </div>
                <div class="mvp-interface-actions">
                    <button class="mvp-btn mvp-btn-sm mvp-toggle-${status === 'up' ? 'down' : 'up'}" 
                            onclick="window.networkEngine.toggleMVPInterface('${intName}')">
                        ${status === 'up' ? 'Shutdown' : 'No Shut'}
                    </button>
                    <button class="mvp-btn mvp-btn-sm" onclick="window.networkEngine.configureMVPInterface('${intName}')">
                        Configure
                    </button>
                </div>
            </div>`;
        });
        
        html += '</div>';
        return html;
    }
    
    /**
     * Setup event listeners for the MVP Device Interfaces popup
     */
    setupMVPInterfacesEventListeners(device) {
        // Close on Escape key
        document.addEventListener('keydown', this.handleMVPEscapeKey.bind(this), { once: true });
        
        // Auto-save configuration changes
        const inputs = document.querySelectorAll('#mvp-device-interfaces input');
        inputs.forEach(input => {
            input.addEventListener('change', () => this.autoSaveMVPConfig());
            if (input.classList.contains('mvp-input')) {
                input.addEventListener('keydown', (ev) => this.handleConfigInputKeyDown(ev));
            }
        });

        this.installGlobalKeyLogger();
    }
    
    /**
     * Handle Escape key to close the popup
     */
    handleMVPEscapeKey(event) {
        if (event.key === 'Escape') {
            this.closeMVPDeviceInterfaces();
        }
    }
    
    /**
     * Switch between Config and CLI tabs
     */
    switchMVPDeviceTab(tabName) {
        console.log(`📑 MVP: Switching to ${tabName} tab`);
        
        // Update tab buttons
        document.querySelectorAll('.mvp-tab-btn').forEach(btn => {
            btn.classList.remove('mvp-tab-active');
            if (btn.getAttribute('data-tab') === tabName) {
                btn.classList.add('mvp-tab-active');
            }
        });
        
        // Update tab content
        document.querySelectorAll('.mvp-tab-content').forEach(content => {
            content.classList.remove('mvp-tab-active');
        });
        
        const activeContent = document.getElementById(`mvp-${tabName}-tab`);
        if (activeContent) {
            activeContent.classList.add('mvp-tab-active');
        }
        
        // Focus CLI input when switching to CLI tab
        if (tabName === 'cli') {
            setTimeout(() => {
                const cliInput = document.getElementById('mvp-cli-input');
                if (cliInput) {
                    cliInput.focus();
                }
            }, 100);
        }
    }
    
    /**
     * Close the MVP Device Interfaces popup
     */
    closeMVPDeviceInterfaces() {
        console.log('🚪 MVP: Closing Device Interfaces');
        const modal = document.getElementById('mvp-device-interfaces');
        if (modal) {
            modal.remove();
        }
        this.currentConfigDevice = null;
    }
    
    /**
     * Refresh interface data
     */
    refreshMVPInterfaces() {
        if (!this.currentConfigDevice) return;
        
        console.log(`🔄 MVP: Refreshing interfaces for ${this.currentConfigDevice.label}`);
        
        // Regenerate interfaces list
        const interfacesList = document.querySelector('.mvp-interfaces-list');
        if (interfacesList) {
            const newHTML = `
                <h4><i class="fas fa-list"></i> Interface Details</h4>
                ${this.generateMVPInterfacesList(this.currentConfigDevice)}
            `;
            interfacesList.innerHTML = newHTML;
        }
        
        // Update overview statistics
        this.updateMVPOverviewStats();
        
        this.showToast?.('Interfaces refreshed', 'success');
    }
    
    /**
     * Update overview statistics in the Config tab
     */
    updateMVPOverviewStats() {
        if (!this.currentConfigDevice) return;
        
        const interfaces = this.currentConfigDevice.interfaces || {};
        const interfaceKeys = Object.keys(interfaces);
        const totalInterfaces = interfaceKeys.length;
        const activeInterfaces = interfaceKeys.filter(key => 
            interfaces[key].status === 'up' || (!interfaces[key].status && interfaces[key].connected)
        ).length;
        const connectedInterfaces = interfaceKeys.filter(key => interfaces[key].connected).length;
        
        // Update stat values
        const statValues = document.querySelectorAll('.mvp-stat-value');
        if (statValues[0]) statValues[0].textContent = totalInterfaces;
        if (statValues[1]) statValues[1].textContent = activeInterfaces;
        if (statValues[2]) statValues[2].textContent = connectedInterfaces;
        
        // Update health status
        if (statValues[3]) {
            const healthRatio = totalInterfaces > 0 ? activeInterfaces / totalInterfaces : 1;
            let healthStatus = 'Excellent';
            let healthColor = '#10B981';
            if (healthRatio < 0.8) {
                healthStatus = 'Good';
                healthColor = '#F59E0B';
            }
            if (healthRatio < 0.6) {
                healthStatus = 'Fair';
                healthColor = '#F97316';
            }
            if (healthRatio < 0.3) {
                healthStatus = 'Poor';
                healthColor = '#EF4444';
            }
            statValues[3].textContent = healthStatus;
            statValues[3].style.color = healthColor;
        }
    }
    showInterfacePanel(device) {
        // Presenter ensures no duplicate Views exist
        this.clearExistingDeviceViews();
        
        let panel = document.getElementById('device-interface-panel');
        if (!panel) {
            panel = this.createInterfacePanel();
        }
        this.populateInterfacePanel(panel, device);
        panel.classList.add('active');
    }

    createInterfacePanel() {
        // Ensure we don't create multiple panels
        const existingPanel = document.getElementById('device-interface-panel');
        if (existingPanel) {
            existingPanel.remove();
        }
        
        const panel = document.createElement('div');
        panel.id = 'device-interface-panel';
        panel.className = 'device-interface-panel';
        panel.innerHTML = `
            <div class="dip-backdrop"></div>
            <div class="dip-container">
                <div class="dip-header">
                    <div class="dip-header-info">
                        <h3 id="dip-title"><i class="fas fa-network-wired"></i> Device Interfaces</h3>
                        <div class="dip-device-info">
                            <span id="dip-device-name">Device Name</span>
                            <span id="dip-device-type">Device Type</span>
                        </div>
                    </div>
                    <div class="dip-actions">
                        <button id="dip-refresh" class="btn btn-info btn-sm" title="Refresh Interfaces">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        <button id="dip-open-config" class="btn btn-primary btn-sm">
                            <i class="fas fa-cog"></i> Configure
                        </button>
                        <button id="dip-close" class="btn btn-secondary btn-sm">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <div class="dip-body">
                    <!-- Device Overview Section -->
                    <div class="dip-overview-section">
                        <div class="dip-section-title">
                            <i class="fas fa-info-circle"></i>
                            <span>Device Overview</span>
                        </div>
                        <div class="dip-overview-grid">
                            <div class="dip-stat-card">
                                <div class="dip-stat-icon">
                                    <i class="fas fa-ethernet"></i>
                                </div>
                                <div class="dip-stat-content">
                                    <div class="dip-stat-value" id="dip-total-interfaces">0</div>
                                    <div class="dip-stat-label">Total Interfaces</div>
                                </div>
                            </div>
                            <div class="dip-stat-card">
                                <div class="dip-stat-icon active">
                                    <i class="fas fa-arrow-up"></i>
                                </div>
                                <div class="dip-stat-content">
                                    <div class="dip-stat-value" id="dip-active-interfaces">0</div>
                                    <div class="dip-stat-label">Active</div>
                                </div>
                            </div>
                            <div class="dip-stat-card">
                                <div class="dip-stat-icon connected">
                                    <i class="fas fa-link"></i>
                                </div>
                                <div class="dip-stat-content">
                                    <div class="dip-stat-value" id="dip-connected-interfaces">0</div>
                                    <div class="dip-stat-label">Connected</div>
                                </div>
                            </div>
                            <div class="dip-stat-card">
                                <div class="dip-stat-icon device-health">
                                    <i class="fas fa-heartbeat"></i>
                                </div>
                                <div class="dip-stat-content">
                                    <div class="dip-stat-value" id="dip-device-health">Good</div>
                                    <div class="dip-stat-label">Health</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Interface List Section -->
                    <div class="dip-interfaces-section">
                        <div class="dip-section-title">
                            <i class="fas fa-list"></i>
                            <span>Interface Details</span>
                            <div class="dip-section-actions">
                                <button class="dip-filter-btn active" data-filter="all">All</button>
                                <button class="dip-filter-btn" data-filter="up">Active</button>
                                <button class="dip-filter-btn" data-filter="down">Inactive</button>
                                <button class="dip-filter-btn" data-filter="connected">Connected</button>
                            </div>
                        </div>
                        <div id="dip-interface-list" class="dip-interface-list"></div>
                    </div>
                </div>
            </div>`;
        document.body.appendChild(panel);
        
        // Event listeners
        panel.querySelector('#dip-close').addEventListener('click', () => {
            this.closeDeviceConfiguration();
        });
        panel.querySelector('#dip-refresh').addEventListener('click', () => {
            const deviceId = panel.dataset.deviceId;
            const device = this.devices.find(d => d.id === deviceId);
            if (device) {
                this.populateInterfacePanel(panel, device);
            }
        });
        panel.querySelector('#dip-open-config').addEventListener('click', () => {
            const deviceId = panel.dataset.deviceId;
            const device = this.devices.find(d => d.id === deviceId);
            // Close current View through Presenter
            this.closeDeviceConfiguration();
            // Open new View through Presenter
            this.presentDeviceConfiguration(device);
        });
        panel.querySelector('.dip-backdrop').addEventListener('click', () => {
            this.closeDeviceConfiguration();
        });

        // Add CSS styles
        if (!document.getElementById('dip-styles')) {
            const style = document.createElement('style');
            style.id = 'dip-styles';
            style.textContent = `
                /* Device Interface Panel Base Styles */
                .device-interface-panel { 
                    position: fixed; 
                    inset: 0; 
                    display: none; 
                    z-index: 2100; 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                }
                .device-interface-panel.active { 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    animation: fadeIn 0.3s ease-out;
                }
                .device-interface-panel .dip-backdrop { 
                    position: absolute; 
                    inset: 0; 
                    background: rgba(0, 0, 0, 0.65); 
                    backdrop-filter: blur(8px); 
                    -webkit-backdrop-filter: blur(8px);
                }
                
                /* Main Container */
                .dip-container {
                    position: relative; 
                    width: 900px; 
                    max-width: 95vw; 
                    max-height: 85vh; 
                    background: linear-gradient(145deg, #0F172A 0%, #1E293B 100%);
                    border: 1px solid rgba(59, 130, 246, 0.2); 
                    border-radius: 20px; 
                    box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.8), 
                                0 0 0 1px rgba(255, 255, 255, 0.05);
                    overflow: hidden;
                    transform: scale(0.9);
                    animation: modalSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
                }
                
                /* Header Styles */
                .dip-header { 
                    display: flex; 
                    align-items: center; 
                    justify-content: space-between; 
                    padding: 20px 24px; 
                    background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
                }
                .dip-header-info h3 { 
                    margin: 0 0 4px 0; 
                    font-size: 1.25rem; 
                    display: flex; 
                    gap: 10px; 
                    align-items: center; 
                    font-weight: 700; 
                    color: #F8FAFC; 
                    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
                }
                .dip-device-info {
                    display: flex;
                    gap: 12px;
                    font-size: 0.85rem;
                    color: #94A3B8;
                }
                .dip-device-info span {
                    padding: 2px 8px;
                    background: rgba(255, 255, 255, 0.08);
                    border-radius: 6px;
                    font-weight: 500;
                }
                .dip-actions { 
                    display: flex; 
                    gap: 8px; 
                }
                .dip-actions .btn {
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 0.85rem;
                    transition: all 0.2s ease;
                    border: none;
                    cursor: pointer;
                }
                .dip-actions .btn:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }
                
                /* Body Styles */
                .dip-body { 
                    padding: 24px; 
                    overflow-y: auto; 
                    max-height: calc(85vh - 90px);
                }
                
                /* Section Styles */
                .dip-overview-section,
                .dip-interfaces-section {
                    margin-bottom: 24px;
                }
                .dip-section-title {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 16px;
                    font-size: 1rem;
                    font-weight: 600;
                    color: #E2E8F0;
                }
                .dip-section-title i {
                    margin-right: 8px;
                    color: #3B82F6;
                }
                
                /* Overview Grid */
                .dip-overview-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                    margin-bottom: 24px;
                }
                .dip-stat-card {
                    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 16px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    transition: all 0.3s ease;
                }
                .dip-stat-card:hover {
                    background: rgba(255, 255, 255, 0.08);
                    border-color: rgba(59, 130, 246, 0.3);
                    transform: translateY(-2px);
                }
                .dip-stat-icon {
                    width: 40px;
                    height: 40px;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: rgba(59, 130, 246, 0.2);
                    color: #3B82F6;
                    font-size: 1.1rem;
                }
                .dip-stat-icon.active {
                    background: rgba(16, 185, 129, 0.2);
                    color: #10B981;
                }
                .dip-stat-icon.connected {
                    background: rgba(139, 92, 246, 0.2);
                    color: #8B5CF6;
                }
                .dip-stat-icon.device-health {
                    background: rgba(245, 158, 11, 0.2);
                    color: #F59E0B;
                }
                .dip-stat-value {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #F8FAFC;
                    line-height: 1;
                }
                .dip-stat-label {
                    font-size: 0.8rem;
                    color: #94A3B8;
                    font-weight: 500;
                }
                
                /* Filter Buttons */
                .dip-section-actions {
                    display: flex;
                    gap: 6px;
                }
                .dip-filter-btn {
                    padding: 4px 12px;
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    color: #94A3B8;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                .dip-filter-btn:hover {
                    background: rgba(255, 255, 255, 0.12);
                    color: #F8FAFC;
                }
                .dip-filter-btn.active {
                    background: rgba(59, 130, 246, 0.2);
                    border-color: #3B82F6;
                    color: #3B82F6;
                }
                
                /* Interface List */
                .dip-interface-list { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
                    gap: 16px; 
                }
                .dip-iface-card { 
                    background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.02) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.12); 
                    border-radius: 12px; 
                    padding: 16px; 
                    position: relative; 
                    display: flex; 
                    flex-direction: column; 
                    gap: 8px; 
                    transition: all 0.3s ease;
                }
                .dip-iface-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                }
                .dip-iface-card.up { 
                    border-color: #10B981; 
                    box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.3), 0 4px 16px rgba(16, 185, 129, 0.15); 
                }
                .dip-iface-card.down { 
                    border-color: #EF4444; 
                    box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.3), 0 4px 16px rgba(239, 68, 68, 0.15); 
                    opacity: 0.85;
                }
                .dip-iface-header { 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    margin-bottom: 8px;
                }
                .dip-iface-name { 
                    font-size: 0.9rem; 
                    font-weight: 700; 
                    color: #F8FAFC; 
                }
                .dip-meta { 
                    font-size: 0.75rem; 
                    line-height: 1.4; 
                    color: #94A3B8; 
                    margin-bottom: 4px;
                }
                .dip-meta strong {
                    color: #E2E8F0;
                }
                .dip-status-chip { 
                    padding: 4px 8px; 
                    border-radius: 6px; 
                    font-size: 0.65rem; 
                    font-weight: 700; 
                    letter-spacing: 0.5px; 
                    text-transform: uppercase;
                }
                .dip-status-chip.up { 
                    background: rgba(16, 185, 129, 0.2); 
                    color: #10B981; 
                    border: 1px solid rgba(16, 185, 129, 0.3);
                }
                .dip-status-chip.down { 
                    background: rgba(239, 68, 68, 0.2); 
                    color: #EF4444; 
                    border: 1px solid rgba(239, 68, 68, 0.3);
                }
                .dip-actions-row { 
                    display: flex; 
                    gap: 8px; 
                    margin-top: 12px; 
                }
                .dip-btn-mini { 
                    flex: 1; 
                    background: rgba(255, 255, 255, 0.08); 
                    border: 1px solid rgba(255, 255, 255, 0.15); 
                    border-radius: 6px; 
                    padding: 6px 8px; 
                    font-size: 0.7rem; 
                    cursor: pointer; 
                    color: #F8FAFC; 
                    font-weight: 600; 
                    transition: all 0.2s ease; 
                }
                .dip-btn-mini:hover { 
                    background: rgba(255, 255, 255, 0.15); 
                    transform: translateY(-1px);
                }
                .dip-btn-mini.toggle-up { 
                    border-color: #10B981; 
                    color: #10B981;
                }
                .dip-btn-mini.toggle-down { 
                    border-color: #EF4444; 
                    color: #EF4444;
                }
                
                /* Animations */
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes modalSlideIn {
                    from { 
                        transform: scale(0.9) translateY(-20px); 
                        opacity: 0; 
                    }
                    to { 
                        transform: scale(1) translateY(0); 
                        opacity: 1; 
                    }
                }
                
                /* Responsive Design */
                @media (max-width: 768px) { 
                    .dip-container { 
                        width: 95vw; 
                        margin: 20px;
                    }
                    .dip-header {
                        padding: 16px 20px;
                        flex-direction: column;
                        gap: 12px;
                        align-items: flex-start;
                    }
                    .dip-body {
                        padding: 20px;
                    }
                    .dip-interface-list { 
                        grid-template-columns: 1fr; 
                    }
                    .dip-overview-grid {
                        grid-template-columns: repeat(2, 1fr);
                    }
                    .dip-section-title {
                        flex-direction: column;
                        align-items: flex-start;
                        gap: 8px;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        return panel;
    }

   

    populateInterfacePanel(panel, device) {
        panel.dataset.deviceId = device.id;
        
        // Update header information
        const title = panel.querySelector('#dip-title');
        if (title) title.innerHTML = `<i class="fas fa-network-wired"></i> Device Interfaces`;
        
        const deviceName = panel.querySelector('#dip-device-name');
        if (deviceName) deviceName.textContent = device.label || device.name;
        
        const deviceType = panel.querySelector('#dip-device-type');
        if (deviceType) deviceType.textContent = device.type.charAt(0).toUpperCase() + device.type.slice(1);
        
        // Calculate interface statistics
        const interfaces = device.interfaces || {};
        const interfaceKeys = Object.keys(interfaces);
        const totalInterfaces = interfaceKeys.length;
        const activeInterfaces = interfaceKeys.filter(key => 
            interfaces[key].status === 'up' || (!interfaces[key].status && interfaces[key].connected)
        ).length;
        const connectedInterfaces = interfaceKeys.filter(key => interfaces[key].connected).length;
        
        // Update overview statistics
        const totalEl = panel.querySelector('#dip-total-interfaces');
        if (totalEl) totalEl.textContent = totalInterfaces;
        
        const activeEl = panel.querySelector('#dip-active-interfaces');
        if (activeEl) activeEl.textContent = activeInterfaces;
        
        const connectedEl = panel.querySelector('#dip-connected-interfaces');
        if (connectedEl) connectedEl.textContent = connectedInterfaces;
        
        const healthEl = panel.querySelector('#dip-device-health');
        if (healthEl) {
            const healthRatio = totalInterfaces > 0 ? activeInterfaces / totalInterfaces : 1;
            if (healthRatio >= 0.8) {
                healthEl.textContent = 'Excellent';
                healthEl.style.color = '#10B981';
            } else if (healthRatio >= 0.6) {
                healthEl.textContent = 'Good';
                healthEl.style.color = '#F59E0B';
            } else if (healthRatio >= 0.3) {
                healthEl.textContent = 'Fair';
                healthEl.style.color = '#F97316';
            } else {
                healthEl.textContent = 'Poor';
                healthEl.style.color = '#EF4444';
            }
        }
        
        // Populate interface list
        const container = panel.querySelector('#dip-interface-list');
        if (!container) return;
        container.innerHTML = '';
        
        interfaceKeys.forEach(intName => {
            const intData = interfaces[intName];
            const status = intData.status || (intData.connected ? 'up' : 'down');
            const card = document.createElement('div');
            card.className = `dip-iface-card ${status}`;
            card.dataset.filter = status;
            if (intData.connected) card.dataset.filter += ' connected';
            
            // Generate additional interface details
            const speed = this.getInterfaceSpeed(device.type, intName);
            const duplex = intData.duplex || 'Full';
            const mtu = intData.mtu || '1500';
            const lastChange = this.getRandomLastChange();
            const packetsIn = this.generateTrafficStats();
            const packetsOut = this.generateTrafficStats();
            
            card.innerHTML = `
                <div class="dip-iface-header">
                    <span class="dip-iface-name">${intName}</span>
                    <span class="dip-status-chip ${status}">${status.toUpperCase()}</span>
                </div>
                <div class="dip-meta"><strong>IP:</strong> ${intData.ipAddress || 'Not assigned'}</div>
                <div class="dip-meta"><strong>Subnet:</strong> ${intData.subnetMask || 'Not configured'}</div>
                <div class="dip-meta"><strong>VLAN:</strong> ${intData.vlan || (device.type === 'switch' ? '1' : 'N/A')}</div>
                <div class="dip-meta"><strong>Speed:</strong> ${speed}</div>
                <div class="dip-meta"><strong>Duplex:</strong> ${duplex}</div>
                <div class="dip-meta"><strong>MTU:</strong> ${mtu} bytes</div>
                <div class="dip-meta"><strong>Link:</strong> ${intData.connected ? 'Connected' : 'Disconnected'}</div>
                <div class="dip-meta"><strong>Last Change:</strong> ${lastChange}</div>
                <div class="dip-meta"><strong>In:</strong> ${packetsIn.packets} pkts (${packetsIn.bytes})</div>
                <div class="dip-meta"><strong>Out:</strong> ${packetsOut.packets} pkts (${packetsOut.bytes})</div>
                <div class="dip-actions-row">
                    <button class="dip-btn-mini toggle-${status === 'up' ? 'down' : 'up'}" data-action="toggle" data-int="${intName}">
                        ${status === 'up' ? 'Shutdown' : 'No Shut'}
                    </button>
                    <button class="dip-btn-mini" data-action="details" data-int="${intName}">Details</button>
                    <button class="dip-btn-mini" data-action="stats" data-int="${intName}">Stats</button>
                </div>`;
            container.appendChild(card);
        });

        // Add filter functionality
        this.setupInterfaceFilters(panel);

        // Setup interface action handlers
        this.setupInterfaceActions(panel, device);
    }
    
    getInterfaceSpeed(deviceType, interfaceName) {
        const speedMap = {
            'router': '100 Mbps',
            'switch': '1 Gbps',
            'hub': '10 Mbps',
            'access-point': '300 Mbps',
            'firewall': '1 Gbps',
            'computer': '100 Mbps',
            'laptop': '100 Mbps',
            'server': '1 Gbps',
            'tablet': '300 Mbps',
            'mobile': '150 Mbps',
            'phone': '100 Mbps'
        };
        return speedMap[deviceType] || '100 Mbps';
    }
    
    getRandomLastChange() {
        const timeUnits = ['seconds', 'minutes', 'hours', 'days'];
        const randomTime = Math.floor(Math.random() * 60) + 1;
        const randomUnit = timeUnits[Math.floor(Math.random() * timeUnits.length)];
        return `${randomTime} ${randomUnit} ago`;
    }
    
    generateTrafficStats() {
        const packets = Math.floor(Math.random() * 10000) + 100;
        const bytes = Math.floor(packets * (Math.random() * 1000 + 64));
        const formattedBytes = bytes > 1024 * 1024 ? 
            `${(bytes / (1024 * 1024)).toFixed(1)}MB` : 
            bytes > 1024 ? 
                `${(bytes / 1024).toFixed(1)}KB` : 
                `${bytes}B`;
        return { packets, bytes: formattedBytes };
    }
    
    setupInterfaceFilters(panel) {
        const filterButtons = panel.querySelectorAll('.dip-filter-btn');
        const interfaceCards = panel.querySelectorAll('.dip-iface-card');
        
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class from all buttons
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filter = btn.dataset.filter;
                
                interfaceCards.forEach(card => {
                    if (filter === 'all' || card.dataset.filter.includes(filter)) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }
    
    setupInterfaceActions(panel, device) {
        const container = panel.querySelector('#dip-interface-list');
        if (!container) return;

        // Interaction handlers for toggle buttons
        container.querySelectorAll('button[data-action="toggle"]').forEach(btn => {
            btn.addEventListener('click', () => {
                const intName = btn.dataset.int;
                const iface = device.interfaces[intName];
                if (!iface) return;
                // Toggle status
                iface.status = (iface.status === 'up') ? 'down' : 'up';
                // Re-render
                this.populateInterfacePanel(panel, device);
                this.needsRender = true;
            });
        });

        // Interaction handlers for details and stats buttons
        container.querySelectorAll('button[data-action="details"]').forEach(btn => {
            btn.addEventListener('click', () => {
                // Get device and close current View through Presenter
                const deviceId = panel.dataset.deviceId;
                const dev = this.devices.find(d => d.id === deviceId);
                this.closeDeviceConfiguration();
                // Open new View through Presenter
                this.presentDeviceConfiguration(dev);
            });
        });

        container.querySelectorAll('button[data-action="stats"]').forEach(btn => {
            btn.addEventListener('click', () => {
                const intName = btn.dataset.int;
                this.showInterfaceStats(device, intName);
            });
        });
    }
    
    showInterfaceStats(device, interfaceName) {
        const intData = device.interfaces[interfaceName];
        if (!intData) return;
        
        // Create a simple stats popup
        const statsModal = document.createElement('div');
        statsModal.className = 'interface-stats-modal';
        statsModal.innerHTML = `
            <div class="stats-backdrop"></div>
            <div class="stats-content">
                <div class="stats-header">
                    <h4><i class="fas fa-chart-line"></i> ${interfaceName} Statistics</h4>
                    <button class="stats-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="stats-body">
                    <div class="stat-row">
                        <span>Status:</span>
                        <span class="stat-value ${intData.status || 'down'}">${(intData.status || 'down').toUpperCase()}</span>
                    </div>
                    <div class="stat-row">
                        <span>Link Status:</span>
                        <span class="stat-value">${intData.connected ? 'Connected' : 'Disconnected'}</span>
                    </div>
                    <div class="stat-row">
                        <span>Speed:</span>
                        <span class="stat-value">${this.getInterfaceSpeed(device.type, interfaceName)}</span>
                    </div>
                    <div class="stat-row">
                        <span>Duplex:</span>
                        <span class="stat-value">${intData.duplex || 'Full'}</span>
                    </div>
                    <div class="stat-row">
                        <span>MTU:</span>
                        <span class="stat-value">${intData.mtu || '1500'} bytes</span>
                    </div>
                    <div class="stat-row">
                        <span>Packets In:</span>
                        <span class="stat-value">${Math.floor(Math.random() * 10000) + 100}</span>
                    </div>
                    <div class="stat-row">
                        <span>Packets Out:</span>
                        <span class="stat-value">${Math.floor(Math.random() * 10000) + 100}</span>
                    </div>
                    <div class="stat-row">
                        <span>Errors:</span>
                        <span class="stat-value">${Math.floor(Math.random() * 10)}</span>
                    </div>
                </div>
            </div>
        `;
        
        // Add styles if not exist
        if (!document.getElementById('stats-modal-styles')) {
            const style = document.createElement('style');
            style.id = 'stats-modal-styles';
            style.textContent = `
                .interface-stats-modal { position: fixed; inset: 0; z-index: 2200; display: flex; align-items: center; justify-content: center; }
                .stats-backdrop { position: absolute; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); }
                .stats-content { position: relative; background: #1E293B; border: 1px solid rgba(59,130,246,0.3); border-radius: 12px; width: 400px; max-width: 90vw; }
                .stats-header { padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; }
                .stats-header h4 { margin: 0; color: #F8FAFC; font-size: 1rem; display: flex; gap: 8px; align-items: center; }
                .stats-close { background: none; border: none; color: #94A3B8; cursor: pointer; padding: 4px; }
                .stats-body { padding: 20px; }
                .stat-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
                .stat-row:last-child { border-bottom: none; }
                .stat-row span:first-child { color: #94A3B8; }
                .stat-value { color: #F8FAFC; font-weight: 600; }
                .stat-value.up { color: #10B981; }
                .stat-value.down { color: #EF4444; }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(statsModal);
        
        // Event listeners
        statsModal.querySelector('.stats-close').addEventListener('click', () => statsModal.remove());
        statsModal.querySelector('.stats-backdrop').addEventListener('click', () => statsModal.remove());
    }
    
    showDeviceConfigModal(device) {
        // Presenter ensures clean View state
        this.clearExistingDeviceViews();
        
        // Ensure modal exists and is available for reuse
        let modal = document.getElementById('device-config-modal');
        if (!modal) {
            modal = this.createDeviceConfigModal();
        }
        
        // Reset modal to clean state
        modal.classList.remove('active');
        modal.style.display = 'none';
        
        // Populate modal with device data
        this.populateDeviceConfigModal(modal, device);
        
        // Show modal
        modal.classList.add('active');
        modal.style.display = 'flex';
        
        // Store current device reference in Presenter
        this.currentConfigDevice = device;
    }
    
    createDeviceConfigModal() {
        // Ensure we don't create duplicate modals
        const existingModal = document.getElementById('device-config-modal');
        if (existingModal) {
            console.log('♻️ Reusing existing device config modal');
            return existingModal;
        }
        
        const modal = document.createElement('div');
        modal.id = 'device-config-modal';
        modal.className = 'device-config-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Device Configuration</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="config-form">
                        <div class="form-group">
                            <label>Hostname</label>
                            <input type="text" id="device-hostname" />
                        </div>
                        <div class="form-group">
                            <label>IP Address</label>
                            <input type="text" id="device-ip" />
                        </div>
                        <div class="form-group">
                            <label>Subnet Mask</label>
                            <input type="text" id="device-subnet" />
                        </div>
                        <div class="form-group">
                            <label>Default Gateway</label>
                            <input type="text" id="device-gateway" />
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary cancel-btn">Cancel</button>
                    <button class="btn btn-primary save-btn">Save</button>
                </div>
            </div>
        `;
        
        // Add event listeners using Presenter pattern
        modal.querySelector('.close-btn').addEventListener('click', () => this.closeDeviceConfiguration());
        modal.querySelector('.cancel-btn').addEventListener('click', () => this.closeDeviceConfiguration());
        modal.querySelector('.save-btn').addEventListener('click', () => this.saveDeviceConfig());
        modal.querySelector('.modal-backdrop').addEventListener('click', () => this.closeDeviceConfiguration());
        
        document.body.appendChild(modal);
        
        console.log('✅ Created new device config modal with Presenter event handlers');
        return modal;
    }
    
    populateDeviceConfigModal(modal, device) {
        modal.querySelector('#device-hostname').value = device.config.hostname;
        modal.querySelector('#device-ip').value = device.config.ipAddress;
        modal.querySelector('#device-subnet').value = device.config.subnetMask;
        modal.querySelector('#device-gateway').value = device.config.gateway;
        
        // Store current device reference
        modal.dataset.deviceId = device.id;
    }
    
    closeDeviceConfigModal() {
        // Route through Presenter instead of direct View manipulation
        this.closeDeviceConfiguration();
    }
    
    saveDeviceConfig() {
        const modal = document.getElementById('device-config-modal');
        const deviceId = modal.dataset.deviceId;
        const device = this.devices.find(d => d.id === deviceId);
        
        if (device) {
            device.config.hostname = modal.querySelector('#device-hostname').value;
            device.config.ipAddress = modal.querySelector('#device-ip').value;
            device.config.subnetMask = modal.querySelector('#device-subnet').value;
            device.config.gateway = modal.querySelector('#device-gateway').value;
            
            console.log('💾 Saved device config:', device.id);
        }
        
        this.closeDeviceConfigModal();
    }
    
    toggleCLI() {
        const terminal = document.getElementById('cli-terminal-container');
        if (terminal) {
            terminal.classList.toggle('active');
        }
    }
    
    runNetworkTests() {
        console.log('🧪 Running network connectivity tests...');
        
        // Implement ping, traceroute, etc.
        this.pingAllDevices();
        this.checkConnectivity();
        this.validateConfiguration();
    }
    
    pingAllDevices() {
        this.devices.forEach(device => {
            if (device.config.ipAddress) {
                console.log(`📡 Ping ${device.config.hostname} (${device.config.ipAddress}): Success`);
            }
        });
    }
    
    checkConnectivity() {
        this.connections.forEach(connection => {
            const reachable = connection.device1.connections.length > 0 && 
                            connection.device2.connections.length > 0;
            console.log(`🔗 Connection ${connection.id}: ${reachable ? 'Reachable' : 'Unreachable'}`);
        });
    }
    
    validateConfiguration() {
        let validDevices = 0;
        let configuredDevices = 0;
        
        this.devices.forEach(device => {
            if (device.config.ipAddress && device.config.subnetMask) {
                configuredDevices++;
                if (this.isValidIP(device.config.ipAddress)) {
                    validDevices++;
                }
            }
        });
        
        console.log(`✅ Network validation: ${validDevices}/${configuredDevices} devices properly configured`);
        
        return {
            totalDevices: this.devices.length,
            configuredDevices,
            validDevices,
            connections: this.connections.length
        };
    }
    
    isValidIP(ip) {
        const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipRegex.test(ip);
    }
    
    resetNetwork() {
        if (confirm('Are you sure you want to reset the entire network? This action cannot be undone.')) {
            this.devices = [];
            this.connections = [];
            this.clearSelection();
            this.deviceIdCounter = 1;
            this.connectionIdCounter = 1;
            this.updateDeviceCount();
            this.updateConnectionCount();
            this.needsRender = true;
            
            console.log('🔄 Network reset complete');
        }
    }
    
    saveTopology() {
        const topology = {
            devices: this.devices,
            connections: this.connections,
            metadata: {
                created: new Date().toISOString(),
                deviceCount: this.devices.length,
                connectionCount: this.connections.length
            }
        };
        
        console.log('💾 Saving topology:', topology);
        
        // Save to localStorage as backup
        localStorage.setItem('network_topology_backup', JSON.stringify(topology));
        
        // TODO: Send to backend API
        return topology;
    }
    
    loadTopology(topology) {
        if (topology.devices && topology.connections) {
            this.devices = topology.devices;
            this.connections = topology.connections;
            this.deviceIdCounter = Math.max(...this.devices.map(d => 
                parseInt(d.id.split('_')[1]) || 0
            )) + 1;
            this.connectionIdCounter = Math.max(...this.connections.map(c => 
                parseInt(c.id.split('_')[1]) || 0
            )) + 1;
            
            this.updateDeviceCount();
            this.updateConnectionCount();
            this.needsRender = true;
            
            console.log('📂 Topology loaded successfully');
        }
    }
    
    zoomIn() {
        this.zoom = Math.min(3.0, this.zoom * 1.2);
        this.needsRender = true;
    }
    
    zoomOut() {
        this.zoom = Math.max(0.1, this.zoom * 0.8);
        this.needsRender = true;
    }
    
    zoomToFit() {
        if (this.devices.length === 0) return;
        
        const bounds = this.getDeviceBounds();
        const padding = 50;
        
        const canvasWidth = this.canvas.width / window.devicePixelRatio;
        const canvasHeight = this.canvas.height / window.devicePixelRatio;
        
        const scaleX = (canvasWidth - padding * 2) / bounds.width;
        const scaleY = (canvasHeight - padding * 2) / bounds.height;
        
        this.zoom = Math.min(scaleX, scaleY, 1.0);
        this.panOffset.x = -(bounds.minX + bounds.width / 2 - canvasWidth / 2 / this.zoom);
        this.panOffset.y = -(bounds.minY + bounds.height / 2 - canvasHeight / 2 / this.zoom);
        
        this.needsRender = true;
    }
    
    getDeviceBounds() {
        if (this.devices.length === 0) {
            return { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0 };
        }
        
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        
        this.devices.forEach(device => {
            minX = Math.min(minX, device.x - device.width / 2);
            minY = Math.min(minY, device.y - device.height / 2);
            maxX = Math.max(maxX, device.x + device.width / 2);
            maxY = Math.max(maxY, device.y + device.height / 2);
        });
        
        return {
            minX, minY, maxX, maxY,
            width: maxX - minX,
            height: maxY - minY
        };
    }
    
    // Clean up
    destroy() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        
        // Presenter cleanup - remove all managed Views
        this.clearExistingDeviceViews();
        
        this.devices = [];
        this.connections = [];
        this.ctx = null;
        this.canvas = null;
        
        console.log('🗑️ Network Simulation Engine destroyed');
    }

    // ===== INTEGRATION HELPERS (Bridge compatibility) =====

    /**
     * Get device by id, label/name, or return the object if already a device
     */
    getDevice(idOrObj) {
        if (!idOrObj) return null;
        if (typeof idOrObj === 'object' && idOrObj.id) {
            // Try to find the engine instance for the same id
            const found = this.devices.find(d => d.id === idOrObj.id) || null;
            return found || idOrObj;
        }
        const id = String(idOrObj);
        return this.devices.find(d => d.id === id || d.label === id || d.name === id) || null;
    }

    /**
     * Import an external device shape into the engine
     */
    importDevice(external) {
        if (!external) return null;
        const type = external.type || 'computer';
        const x = typeof external.x === 'number' ? external.x : 100;
        const y = typeof external.y === 'number' ? external.y : 100;
        const device = this.createDevice(type, x, y);
        if (!device) return null;

        // Preserve identifiers/labels when provided
        if (external.id) device.id = String(external.id);
        if (external.label) device.label = external.label;
        if (external.name) device.name = external.name;
        // Preserve simple config if present
        if (external.config) {
            device.config = { ...device.config, ...external.config };
        }
        // Width/height fallback
        device.width = external.width || device.width || 60;
        device.height = external.height || device.height || 60;
        this.needsRender = true;
        return device;
    }

    /**
     * Import a connection between two devices using many possible shapes
     */
    importConnection(external) {
        if (!external) return null;
        const aRef = external.from ?? external.source ?? external.device1 ?? external.a ?? null;
        const bRef = external.to ?? external.target ?? external.device2 ?? external.b ?? null;
        const devA = this.getDevice(aRef);
        const devB = this.getDevice(bRef);
        if (!devA || !devB) {
            console.warn('⚠️ importConnection: devices not found', external);
            return null;
        }
        const port1 = external.port1 ?? null;
        const port2 = external.port2 ?? null;
        return this.createConnection(devA, devB, port1, port2);
    }

    /**
     * Export current simulation data in a generic shape
     */
    exportSimulation() {
        return {
            topology: {
                devices: this.devices.map(d => ({ ...d })),
                connections: this.connections.map(c => ({
                    id: c.id,
                    device1: c.device1.id,
                    device2: c.device2.id,
                    port1: c.port1,
                    port2: c.port2,
                    type: c.type,
                    status: c.status
                }))
            },
            devices: this.devices.map(d => ({ ...d })),
            connections: this.connections.map(c => ({ ...c })),
            configuration: {}
        };
    }

    /**
     * Update device configuration by id
     */
    updateDeviceConfiguration(deviceId, config) {
        const dev = this.getDevice(deviceId);
        if (!dev) return false;
        dev.config = { ...dev.config, ...(config || {}) };
        this.needsRender = true;
        this.emit('device-configured', dev);
        return true;
    }

    /**
     * Optional compatibility wrappers
     */
    setCurrentStep(_step) { /* no-op for now */ }
    handleStepCompletion(_data) { /* no-op for now */ }
    showStepGuidance(_type, _data) { /* no-op for now */ }

    validateNetworkConfiguration() {
        // Reuse existing validateConfiguration and adapt result
        const res = this.validateConfiguration();
        return Promise.resolve({
            isValid: res.validDevices === res.configuredDevices,
            errors: [],
            warnings: [],
            summary: res
        });
    }

    reset() {
        // Alias for integration bridge
        this.resetNetwork();
    }

    // ===== MVP CLI FUNCTIONALITY =====
    
    /**
     * Handle CLI input in the MVP popup
     */
    handleMVPCLIInput(event) {
        // Robust Backspace fallback: if another listener blocks native deletion,
        // we detect no value change and manually remove characters.
        if (event.key === 'Backspace') {
            const input = event.target;
            if (input && (input.classList.contains('mvp-cli-input'))) {
                const before = input.value;
                const selStart = input.selectionStart;
                const selEnd = input.selectionEnd;
                // Allow default first
                setTimeout(() => {
                    if (!input.isConnected) return;
                    const after = input.value;
                    if (after === before && before.length > 0 && document.activeElement === input) {
                        let newVal;
                        if (selStart !== selEnd) {
                            newVal = before.slice(0, selStart) + before.slice(selEnd);
                            input.value = newVal;
                            input.selectionStart = input.selectionEnd = selStart;
                        } else if (selStart > 0) {
                            newVal = before.slice(0, selStart - 1) + before.slice(selEnd);
                            input.value = newVal;
                            input.selectionStart = input.selectionEnd = selStart - 1;
                        }
                        if (newVal !== undefined) {
                            console.warn('⚠️ Applied Backspace fallback (MVP CLI) — another handler blocked native deletion');
                        }
                    }
                }, 0);
            }
            // Do not return; let normal processing continue for other keys below if needed
        }
        if (event.key === 'Enter') {
            event.preventDefault();
            const input = event.target;
            const command = input.value.trim();
            
            if (command) {
                console.log(`💻 MVP: Executing CLI command "${command}"`);
                this.executeMVPCLICommand(command);
                input.value = '';
            }
        } else if (event.key === 'ArrowUp') {
            // TODO: Implement command history navigation
            event.preventDefault();
        } else if (event.key === 'ArrowDown') {
            // TODO: Implement command history navigation
            event.preventDefault();
        } else if (event.key === 'Tab') {
            // TODO: Implement command auto-completion
            event.preventDefault();
        } else if (event.key === 'Escape') {
            // Clear the input
            event.preventDefault();
            event.target.value = '';
        } else if (event.key === 'Backspace') {
            // Debug log to verify Backspace is reaching handler (should not prevent default)
            console.debug('🔑 MVP CLI Backspace detected');
        }
        // Allow all other keys (including Backspace, Delete, etc.) to work normally
        // by not preventing default behavior
    }

    handleConfigInputKeyDown(event) {
        if (event.key !== 'Backspace') return;
        const input = event.target;
        if (!input || !input.classList.contains('mvp-input')) return;
        const before = input.value;
        const selStart = input.selectionStart;
        const selEnd = input.selectionEnd;
        setTimeout(() => {
            if (!input.isConnected) return;
            const after = input.value;
            if (after === before && before.length > 0 && document.activeElement === input) {
                let newVal;
                if (selStart !== selEnd) {
                    newVal = before.slice(0, selStart) + before.slice(selEnd);
                    input.value = newVal;
                    input.selectionStart = input.selectionEnd = selStart;
                } else if (selStart > 0) {
                    newVal = before.slice(0, selStart - 1) + before.slice(selEnd);
                    input.value = newVal;
                    input.selectionStart = input.selectionEnd = selStart - 1;
                }
                if (newVal !== undefined) {
                    console.warn('⚠️ Applied Backspace fallback (Configure input) — another handler blocked native deletion');
                }
            }
        }, 0);
    }

    installGlobalKeyLogger() {
        if (window.__mvpKeyLoggerInstalled) return;
        window.__mvpKeyLoggerInstalled = true;
        window.__MVP_KEY_DEBUG = false; // opt-in via enableMVPKeyDebug
        document.addEventListener('keydown', (ev) => {
            if (!window.__MVP_KEY_DEBUG) return;
            if (ev.key === 'Backspace') {
                const tgt = ev.target;
                const info = {
                    key: ev.key,
                    defaultPrevented: ev.defaultPrevented,
                    tag: tgt.tagName,
                    id: tgt.id,
                    classes: tgt.className,
                    inMVPOverlay: !!(tgt.closest && tgt.closest('#mvp-device-interfaces')),
                    valueLength: tgt.value?.length,
                    selection: [tgt.selectionStart, tgt.selectionEnd]
                };
                console.log('🛑 [KeyCapture] Backspace event', info);
            }
        }, true);
        console.log('🔍 MVP capture-phase key logger installed. Enable with window.networkEngine.enableMVPKeyDebug(true)');
    }

    enableMVPKeyDebug(on = true) {
        window.__MVP_KEY_DEBUG = !!on;
        console.log(`🧪 MVP key debug ${on ? 'ENABLED' : 'disabled'}`);
    }
    
    /**
     * Execute a CLI command in the MVP popup
     */
    executeMVPCLICommand(command) {
        const outputDiv = document.getElementById('mvp-cli-output');
        if (!outputDiv) return;
        
        const device = this.currentConfigDevice;
        const hostname = device?.label || device?.name || 'Device';
        
        // Add command to output
        const commandLine = document.createElement('div');
        commandLine.className = 'mvp-cli-command-line';
        commandLine.innerHTML = `<span class="mvp-cli-prompt">${hostname}#</span> ${command}`;
        outputDiv.appendChild(commandLine);
        
        // Process command and show response
        const response = this.processMVPCLICommand(command);
        if (response) {
            const responseLine = document.createElement('div');
            responseLine.className = 'mvp-cli-response';
            responseLine.innerHTML = response.replace(/\n/g, '<br>');
            outputDiv.appendChild(responseLine);
        }
        
        // Scroll to bottom
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }
    
    /**
     * Process CLI command and return response
     */
    processMVPCLICommand(command) {
        const cmd = command.toLowerCase().trim();
        const device = this.currentConfigDevice;
        const hostname = device?.label || device?.name || 'Device';
        
        if (cmd === 'help' || cmd === '?') {
            return `Available commands:
  show interfaces       - Display interface status
  show running-config   - Display running configuration  
  show version         - Display system version
  show ip route        - Display routing table
  ping <ip>            - Test connectivity
  configure terminal   - Enter configuration mode
  hostname <name>      - Set device hostname
  interface <name>     - Configure interface
  ip route <network>   - Add static route
  write memory         - Save configuration
  reload              - Restart device
  clear               - Clear screen
  exit                - Exit CLI
  help                - Show this help message`;
            
        } else if (cmd === 'show interfaces') {
            return this.generateMVPShowInterfaces();
            
        } else if (cmd === 'show running-config') {
            return this.generateMVPRunningConfig();
            
        } else if (cmd === 'show version') {
            return `RiddleNet Device Simulator
Software Version: 1.0.0
Hardware: Virtual ${device?.type || 'Device'}
Device: ${hostname}
Uptime: ${this.getRandomUptime()}
Configuration register: 0x2102`;

        } else if (cmd === 'show ip route') {
            return this.generateMVPRoutingTable();
            
        } else if (cmd.startsWith('ping ')) {
            const target = cmd.split(' ')[1];
            if (!target) {
                return 'Usage: ping <ip_address>';
            }
            return this.simulateMVPPing(target);
            
        } else if (cmd === 'configure terminal' || cmd === 'conf t') {
            return 'Entering configuration mode...\n' + hostname + '(config)#';
            
        } else if (cmd.startsWith('hostname ')) {
            const newHostname = command.split(' ').slice(1).join(' ');
            if (device) {
                device.label = device.name = newHostname;
                if (device.config) device.config.hostname = newHostname;
                // Update the display
                setTimeout(() => this.updateMVPHostnameDisplay(newHostname), 100);
            }
            return `Hostname changed to: ${newHostname}`;
            
        } else if (cmd.startsWith('interface ')) {
            const intName = command.split(' ').slice(1).join(' ');
            return `Entering interface configuration mode for ${intName}...\n${hostname}(config-if)#`;
            
        } else if (cmd === 'write memory' || cmd === 'write' || cmd === 'wr') {
            return 'Building configuration...\nConfiguration saved to NVRAM\n[OK]';
            
        } else if (cmd === 'reload') {
            return `Proceed with reload? [confirm] 
System configuration has been modified. Save? [yes/no]: yes
Building configuration...
Reloading device...`;

        } else if (cmd === 'clear' || cmd === 'cls') {
            // Clear CLI output
            const outputDiv = document.getElementById('mvp-cli-output');
            if (outputDiv) {
                outputDiv.innerHTML = '<div class="mvp-cli-welcome">CLI cleared.</div>';
            }
            return '';
            
        } else if (cmd === 'exit' || cmd === 'quit') {
            return 'Goodbye!';
            
        } else {
            return `% Invalid input detected at '^' marker.\n% Unknown command: ${command}\nType 'help' for available commands.`;
        }
    }
    
    /**
     * Generate show interfaces output
     */
    generateMVPShowInterfaces() {
        const device = this.currentConfigDevice;
        if (!device || !device.interfaces) {
            return 'No interfaces configured.';
        }
        
        let output = '';
        Object.keys(device.interfaces).forEach(intName => {
            const intData = device.interfaces[intName];
            const status = intData.status || (intData.connected ? 'up' : 'down');
            const protocol = intData.connected ? 'up' : 'down';
            const ip = intData.ipAddress || 'unassigned';
            const speed = this.getInterfaceSpeed(device.type, intName);
            
            output += `${intName} is ${status}, line protocol is ${protocol}\n`;
            output += `  Internet address is ${ip}\n`;
            output += `  MTU ${intData.mtu || '1500'} bytes, BW ${speed}\n`;
            output += `  Encapsulation ARPA, loopback not set\n`;
            output += `  Last clearing of "show interface" counters never\n\n`;
        });
        
        return output;
    }
    
    /**
     * Generate running configuration output
     */
    generateMVPRunningConfig() {
        const device = this.currentConfigDevice;
        const hostname = device?.label || device?.name || 'Device';
        
        let config = `Building configuration...\n\nCurrent configuration :\n!\nversion 15.1\n!\nhostname ${hostname}\n!\n`;
        
        if (device && device.interfaces) {
            Object.keys(device.interfaces).forEach(intName => {
                const intData = device.interfaces[intName];
                config += `!\ninterface ${intName}\n`;
                
                if (intData.ipAddress) {
                    config += ` ip address ${intData.ipAddress} ${intData.subnetMask || '255.255.255.0'}\n`;
                } else {
                    config += ` no ip address\n`;
                }
                
                if (intData.status === 'down') {
                    config += ` shutdown\n`;
                } else {
                    config += ` no shutdown\n`;
                }
            });
        }
        
        config += '!\nend\n';
        return config;
    }
    
    /**
     * Generate routing table output
     */
    generateMVPRoutingTable() {
        return `Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       
Gateway of last resort is not set

      192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks
C        192.168.1.0/24 is directly connected, Ethernet0/0
L        192.168.1.1/32 is directly connected, Ethernet0/0`;
    }
    
    /**
     * Simulate ping command
     */
    simulateMVPPing(target) {
        return `PING ${target}: 56 data bytes
64 bytes from ${target}: icmp_seq=0 ttl=255 time=1 ms
64 bytes from ${target}: icmp_seq=1 ttl=255 time=1 ms
64 bytes from ${target}: icmp_seq=2 ttl=255 time=1 ms
64 bytes from ${target}: icmp_seq=3 ttl=255 time=1 ms

--- ${target} ping statistics ---
4 packets transmitted, 4 packets received, 0.00% packet loss
round-trip min/avg/max = 1/1/1 ms`;
    }
    
    /**
     * Get random uptime for show version
     */
    getRandomUptime() {
        const days = Math.floor(Math.random() * 30) + 1;
        const hours = Math.floor(Math.random() * 24);
        const minutes = Math.floor(Math.random() * 60);
        return `${days} days, ${hours} hours, ${minutes} minutes`;
    }
    
    /**
     * Update hostname display in popup
     */
    updateMVPHostnameDisplay(newHostname) {
        // Update CLI prompt
        const prompts = document.querySelectorAll('.mvp-cli-prompt');
        prompts.forEach(prompt => {
            prompt.textContent = newHostname + '#';
        });
        
        // Update header subtitle
        const subtitle = document.querySelector('.mvp-device-subtitle');
        if (subtitle) {
            const parts = subtitle.textContent.split(' • ');
            if (parts.length >= 2) {
                subtitle.textContent = newHostname + ' • ' + parts[1];
            }
        }
        
        // Update CLI hostname display
        const cliHostname = document.querySelector('.mvp-cli-hostname');
        if (cliHostname) {
            cliHostname.textContent = newHostname;
        }
    }
    
    /**
     * Clear CLI output
     */
    clearMVPCLI() {
        console.log('🧹 MVP: Clearing CLI output');
        const outputDiv = document.getElementById('mvp-cli-output');
        if (outputDiv) {
            const device = this.currentConfigDevice;
            const hostname = device?.label || device?.name || 'Device';
            outputDiv.innerHTML = `
                <div class="mvp-cli-welcome">
                    Welcome to ${hostname} CLI<br>
                    RiddleNet Device Simulator v1.0<br>
                    Type 'help' for available commands.<br><br>
                </div>`;
        }
    }
    
    /**
     * Save CLI configuration
     */
    saveMVPCLIConfig() {
        console.log('💾 MVP: Saving CLI configuration');
        this.executeMVPCLICommand('write memory');
        this.showToast?.('Configuration saved', 'success');
    }

    // ===== MVP CONFIG FUNCTIONALITY =====
    
    /**
     * Save device configuration from the Config tab
     */
    saveMVPDeviceConfig() {
        if (!this.currentConfigDevice) return;
        
        const device = this.currentConfigDevice;
        
        // Get values from form
        const hostname = document.getElementById('mvp-hostname')?.value;
        const ipAddress = document.getElementById('mvp-ip-address')?.value;
        const subnetMask = document.getElementById('mvp-subnet-mask')?.value;
        const gateway = document.getElementById('mvp-gateway')?.value;
        
        // Validate inputs
        if (ipAddress && !this.isValidIP(ipAddress)) {
            this.showToast?.('Invalid IP address', 'error');
            return;
        }
        
        if (subnetMask && !this.isValidIP(subnetMask)) {
            this.showToast?.('Invalid subnet mask', 'error');
            return;
        }
        
        if (gateway && !this.isValidIP(gateway)) {
            this.showToast?.('Invalid gateway address', 'error');
            return;
        }
        
        // Update device configuration
        if (hostname) {
            device.label = device.name = hostname;
            if (!device.config) device.config = {};
            device.config.hostname = hostname;
        }
        
        if (ipAddress) {
            if (!device.config) device.config = {};
            device.config.ipAddress = ipAddress;
        }
        
        if (subnetMask) {
            if (!device.config) device.config = {};
            device.config.subnetMask = subnetMask;
        }
        
        if (gateway) {
            if (!device.config) device.config = {};
            device.config.gateway = gateway;
        }
        
        // Mark as configured and trigger re-render
        device.configured = true;
        this.needsRender = true;
        
        console.log(`💾 Saved configuration for ${device.label}:`, device.config);
        this.showToast?.(`Configuration saved for ${device.label}`, 'success');
    }
    
    /**
     * Reset device configuration to defaults
     */
    resetMVPDeviceConfig() {
        if (!this.currentConfigDevice) return;
        
        const device = this.currentConfigDevice;
        
        // Reset form fields to original values
        const hostnameInput = document.getElementById('mvp-hostname');
        const ipInput = document.getElementById('mvp-ip-address');
        const subnetInput = document.getElementById('mvp-subnet-mask');
        const gatewayInput = document.getElementById('mvp-gateway');
        
        if (hostnameInput) hostnameInput.value = device.label || device.name || '';
        if (ipInput) ipInput.value = device.config?.ipAddress || '';
        if (subnetInput) subnetInput.value = device.config?.subnetMask || '';
        if (gatewayInput) gatewayInput.value = device.config?.gateway || '';
        
        this.showToast?.('Configuration reset', 'info');
    }
    
    /**
     * Auto-save configuration changes
     */
    autoSaveMVPConfig() {
        // Debounced auto-save functionality
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }
        
        this.autoSaveTimeout = setTimeout(() => {
            this.saveMVPDeviceConfig();
        }, 2000);
    }
    
    /**
     * Toggle interface status
     */
    toggleMVPInterface(interfaceName) {
        if (!this.currentConfigDevice) return;
        
        const device = this.currentConfigDevice;
        const interfaces = device.interfaces || {};
        const intData = interfaces[interfaceName];
        
        if (intData) {
            // Toggle status
            intData.status = (intData.status === 'up') ? 'down' : 'up';
            
            // Re-render interfaces list
            this.refreshMVPInterfaces();
            
            console.log(`🔄 Toggled ${interfaceName} to ${intData.status}`);
            this.showToast?.(`${interfaceName} ${intData.status}`, 'info');
        }
    }
    
    /**
     * Configure specific interface
     */
    configureMVPInterface(interfaceName) {
        console.log(`⚙️ Configuring interface ${interfaceName}`);
        
        // Switch to CLI tab and pre-populate interface command
        this.switchMVPDeviceTab('cli');
        
        setTimeout(() => {
            const cliInput = document.getElementById('mvp-cli-input');
            if (cliInput) {
                cliInput.value = `interface ${interfaceName}`;
                cliInput.focus();
                // Move cursor to end
                cliInput.setSelectionRange(cliInput.value.length, cliInput.value.length);
            }
        }, 100);
    }

    /**
     * Show hint for device selection (MVP pattern)
     * @param {Object} device - The selected device
     */
    showDeviceSelectionHint(device) {
        // Create temporary tooltip/notification
        const existingHint = document.getElementById('mvp-device-hint');
        if (existingHint) {
            existingHint.remove();
        }

        const hint = document.createElement('div');
        hint.id = 'mvp-device-hint';
        hint.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #1E293B, #334155);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
                padding: 16px 20px;
                color: #F8FAFC;
                font-size: 0.9rem;
                font-weight: 600;
                z-index: 1000;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
                animation: mvpHintSlideIn 0.3s ease-out forwards;
                max-width: 280px;
                backdrop-filter: blur(10px);
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                    <i class="${this.deviceTypes[device.type]?.icon || 'fas fa-cube'}" style="color: #3B82F6; font-size: 1.2rem;"></i>
                    <span style="color: #CBD5E1;">Device Selected</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.8rem; line-height: 1.4;">
                    <strong style="color: #E2E8F0;">${device.name}</strong><br>
                    Double-click to open MVP Device Interfaces
                </div>
                <div style="
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    cursor: pointer;
                    color: #64748B;
                    font-size: 0.8rem;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: all 0.2s ease;
                " onclick="this.parentElement.parentElement.remove()" title="Close">
                    ×
                </div>
            </div>
            <style>
                @keyframes mvpHintSlideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            </style>
        `;

        document.body.appendChild(hint);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (hint && hint.parentNode) {
                hint.style.animation = 'mvpHintSlideIn 0.3s ease-in reverse';
                setTimeout(() => {
                    if (hint && hint.parentNode) {
                        hint.remove();
                    }
                }, 300);
            }
        }, 4000);
    }
}

// Export for use in other modules
window.NetworkSimulationEngine = NetworkSimulationEngine;

// Create global instance for easy access
window.networkEngine = null;
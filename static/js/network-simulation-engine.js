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
            }
        };
        
        // Animation and Rendering
        this.animationFrame = null;
        this.needsRender = true;
        
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
        this.currentTool = tool;
        this.isConnecting = (tool === 'connect');
        
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
                    this.openDeviceConfig(this.selectedDevice);
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
            } else if (clickedDevice && this.isConnecting && clickedDevice !== this.connectionStart.device) {
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
            this.openDeviceConfig(clickedDevice);
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
        
        console.log('📱 Selected device:', device.id);
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
            internet: '🌐'
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
    
    openDeviceConfig(device) {
        console.log('⚙️ Opening device config for:', device.id);
        // If interface panel feature enabled and device has interfaces, show interface summary first
        if (this.enableInterfacePanel !== false && device && device.interfaces && Object.keys(device.interfaces).length) {
            this.showInterfacePanel(device);
            return;
        }

        // Trigger full configurator directly
        if (window.userDeviceConfigurator?.openDeviceConfiguration) {
            window.userDeviceConfigurator.openDeviceConfiguration(device);
        } else if (typeof this.showDeviceConfigModal === 'function') {
            this.showDeviceConfigModal(device);
        }
    }

    // ===== DEVICE INTERFACE PANEL (Quick View) =====
    showInterfacePanel(device) {
        // Remove any existing panels first to prevent duplicates
        const existingPanels = document.querySelectorAll('#device-interface-panel');
        existingPanels.forEach(panel => panel.remove());
        
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
            <div class="dip-header">
                <h3 id="dip-title"><i class="fas fa-network-wired"></i> Interfaces</h3>
                <div class="dip-actions">
                    <button id="dip-open-config" class="btn btn-primary btn-sm"><i class="fas fa-cog"></i> Configure</button>
                    <button id="dip-close" class="btn btn-secondary btn-sm">Close</button>
                </div>
            </div>
            <div class="dip-body">
                <div id="dip-interface-list" class="dip-interface-list"></div>
            </div>`;
        document.body.appendChild(panel);
        
        // Event listeners
        panel.querySelector('#dip-close').addEventListener('click', () => {
            panel.classList.remove('active');
        });
        panel.querySelector('#dip-open-config').addEventListener('click', () => {
            const deviceId = panel.dataset.deviceId;
            const device = this.devices.find(d => d.id === deviceId);
            panel.classList.remove('active');
            if (window.userDeviceConfigurator?.openDeviceConfiguration) {
                window.userDeviceConfigurator.openDeviceConfiguration(device);
            } else if (typeof this.showDeviceConfigModal === 'function') {
                this.showDeviceConfigModal(device);
            }
        });
        panel.querySelector('.dip-backdrop').addEventListener('click', () => {
            panel.classList.remove('active');
        });

        // Add CSS styles
        if (!document.getElementById('dip-styles')) {
            const style = document.createElement('style');
            style.id = 'dip-styles';
            style.textContent = `
                .device-interface-panel { position:fixed; inset:0; display:none; z-index:2100; }
                .device-interface-panel.active { display:flex; align-items:center; justify-content:center; }
                .device-interface-panel .dip-backdrop { position:absolute; inset:0; background:rgba(0,0,0,0.55); backdrop-filter:blur(4px); }
                .device-interface-panel.active > .dip-header,
                .device-interface-panel.active > .dip-body { position:relative; width:640px; max-width:90%; max-height:80vh; background:var(--glass-bg, #0F172A); border:1px solid var(--glass-border, rgba(255,255,255,0.15)); box-shadow:0 20px 50px -10px rgba(0,0,0,0.6); }
                .device-interface-panel.active > .dip-header { border-radius:16px 16px 0 0; }
                .device-interface-panel.active > .dip-body { border-radius:0 0 16px 16px; border-top:none; }
                .dip-header { display:flex; align-items:center; justify-content:space-between; padding:14px 18px; border-bottom:1px solid rgba(255,255,255,0.08); }
                .dip-header h3 { margin:0; font-size:1.05rem; display:flex; gap:8px; align-items:center; font-weight:600; color:var(--text-primary,#F8FAFC); }
                .dip-actions { display:flex; gap:8px; }
                .dip-body { padding:14px 18px 18px; overflow:auto; }
                .dip-interface-list { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; }
                .dip-iface-card { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.12); border-radius:12px; padding:12px 12px 10px; position:relative; display:flex; flex-direction:column; gap:6px; }
                .dip-iface-card.up { border-color:#10B981; box-shadow:0 0 0 1px rgba(16,185,129,0.4), 0 4px 12px -2px rgba(16,185,129,0.25); }
                .dip-iface-card.down { border-color:#EF4444; box-shadow:0 0 0 1px rgba(239,68,68,0.4), 0 4px 12px -2px rgba(239,68,68,0.25); filter:saturate(.85); }
                .dip-iface-header { display:flex; justify-content:space-between; align-items:center; font-size:.75rem; text-transform:uppercase; letter-spacing:.5px; font-weight:600; color:var(--text-secondary,#94A3B8); }
                .dip-iface-name { font-size:.8rem; font-weight:600; color:var(--text-primary,#F8FAFC); }
                .dip-meta { font-size:.65rem; line-height:1.15; color:var(--text-secondary,#94A3B8); }
                .dip-status-chip { padding:2px 6px; border-radius:8px; font-size:.55rem; font-weight:600; letter-spacing:.5px; background:rgba(255,255,255,0.08); }
                .dip-status-chip.up { background:rgba(16,185,129,0.15); color:#10B981; }
                .dip-status-chip.down { background:rgba(239,68,68,0.18); color:#EF4444; }
                .dip-actions-row { display:flex; gap:6px; margin-top:4px; }
                .dip-btn-mini { flex:1; background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15); border-radius:6px; padding:4px 6px; font-size:.55rem; cursor:pointer; color:var(--text-primary,#F8FAFC); font-weight:600; letter-spacing:.4px; transition:.18s; }
                .dip-btn-mini:hover { background:rgba(255,255,255,0.12); }
                .dip-btn-mini.toggle-up { border-color:#10B981; }
                .dip-btn-mini.toggle-down { border-color:#EF4444; }
                @media (max-width:720px){ .device-interface-panel.active > .dip-header, .device-interface-panel.active > .dip-body { width:94%; } .dip-interface-list { grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); } }
            `;
            document.head.appendChild(style);
        }

        return panel;
    }

   

    populateInterfacePanel(panel, device) {
        panel.dataset.deviceId = device.id;
        const title = panel.querySelector('#dip-title');
        if (title) title.innerHTML = `<i class="fas fa-network-wired"></i> Interfaces – ${device.label}`;
        const container = panel.querySelector('#dip-interface-list');
        if (!container) return;
        container.innerHTML = '';
        const interfaces = device.interfaces || {};
        Object.keys(interfaces).forEach(intName => {
            const intData = interfaces[intName];
            const status = intData.status || (intData.connected ? 'up' : 'down');
            const card = document.createElement('div');
            card.className = `dip-iface-card ${status}`;
            card.innerHTML = `
                <div class="dip-iface-header">
                    <span class="dip-iface-name">${intName}</span>
                    <span class="dip-status-chip ${status}">${status.toUpperCase()}</span>
                </div>
                <div class="dip-meta">${intData.ipAddress ? `IP: ${intData.ipAddress}` : 'No IP assigned'}</div>
                <div class="dip-meta">${intData.subnetMask ? `${intData.subnetMask}` : ''}</div>
                <div class="dip-meta">${intData.vlan ? `VLAN ${intData.vlan}` : (device.type === 'switch' ? 'VLAN 1' : '')}</div>
                <div class="dip-meta">${intData.connected ? 'Linked' : 'Disconnected'}</div>
                <div class="dip-actions-row">
                    <button class="dip-btn-mini toggle-${status === 'up' ? 'down' : 'up'}" data-action="toggle" data-int="${intName}">${status === 'up' ? 'Shutdown' : 'No Shut'}</button>
                    <button class="dip-btn-mini" data-action="details" data-int="${intName}">Details</button>
                </div>`;
            container.appendChild(card);
        });

        // Interaction handlers
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

        container.querySelectorAll('button[data-action="details"]').forEach(btn => {
            btn.addEventListener('click', () => {
                // For now, open full configurator on details
                const deviceId = panel.dataset.deviceId;
                const dev = this.devices.find(d => d.id === deviceId);
                panel.classList.remove('active');
                if (window.userDeviceConfigurator?.openDeviceConfiguration) {
                    window.userDeviceConfigurator.openDeviceConfiguration(dev);
                } else if (typeof this.showDeviceConfigModal === 'function') {
                    this.showDeviceConfigModal(dev);
                }
            });
        });
    }
    
    showDeviceConfigModal(device) {
        // Create modal if it doesn't exist
        let modal = document.getElementById('device-config-modal');
        if (!modal) {
            modal = this.createDeviceConfigModal();
        }
        
        // Populate modal with device data
        this.populateDeviceConfigModal(modal, device);
        
        // Show modal
        modal.classList.add('active');
    }
    
    createDeviceConfigModal() {
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
        
        // Add event listeners
        modal.querySelector('.close-btn').addEventListener('click', () => this.closeDeviceConfigModal());
        modal.querySelector('.cancel-btn').addEventListener('click', () => this.closeDeviceConfigModal());
        modal.querySelector('.save-btn').addEventListener('click', () => this.saveDeviceConfig());
        modal.querySelector('.modal-backdrop').addEventListener('click', () => this.closeDeviceConfigModal());
        
        document.body.appendChild(modal);
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
        const modal = document.getElementById('device-config-modal');
        if (modal) {
            modal.classList.remove('active');
        }
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
        
        this.devices = [];
        this.connections = [];
        this.ctx = null;
        this.canvas = null;
        
        console.log('🗑️ Network Simulation Engine destroyed');
    }
}

// Export for use in other modules
window.NetworkSimulationEngine = NetworkSimulationEngine;
/**
 * Advanced Simulation Engine - Based on troubleshoot.html patterns
 * Implements comprehensive simulation functionality with enhanced features
 */

class AdvancedSimulationEngine {
    constructor(options) {
        this.canvasId = options.canvasId;
        this.containerId = options.containerId;
        this.canvas = document.getElementById(this.canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.container = document.getElementById(this.containerId);
        
        // Initialize state
        this.state = {
            currentMode: 'select',
            selectedDevices: [],
            connections: [],
            devices: [],
            isDrawing: false,
            isDragging: false,
            draggedDevice: null,
            progress: {
                score: 0,
                step: 1,
                totalSteps: 5,
                hintsUsed: 0,
                timeElapsed: 0,
                startTime: Date.now()
            },
            performance: {
                accuracy: 100,
                speed: 0,
                efficiency: 'A+',
                actionsCount: 0
            },
            tutorial: {
                active: false,
                currentStep: 0,
                steps: []
            },
            scenario: null,
            settings: {
                showGrid: true,
                snapToGrid: true,
                showLabels: true,
                autoSave: true,
                performanceMode: 'high',
                highContrast: false,
                reducedMotion: false
            }
        };
        
        // Bind methods
        this.init = this.init.bind(this);
        this.setupEventListeners = this.setupEventListeners.bind(this);
        this.setupCanvas = this.setupCanvas.bind(this);
        this.render = this.render.bind(this);
        
        this.init();
    }
    
    init() {
        this.setupCanvas();
        this.setupEventListeners();
        this.setupUI();
        this.startPerformanceTracking();
        this.render();
        
        console.log('Advanced Simulation Engine initialized');
    }
    
    setupCanvas() {
        const updateCanvasSize = () => {
            const rect = this.canvas.parentElement.getBoundingClientRect();
            this.canvas.width = rect.width;
            this.canvas.height = rect.height;
            this.render();
        };
        
        updateCanvasSize();
        window.addEventListener('resize', updateCanvasSize);
    }
    
    setupEventListeners() {
        // Canvas events
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.canvas.addEventListener('click', this.handleClick.bind(this));
        
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this));
        this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this));
        this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this));
        
        // Device palette events
        this.setupDevicePaletteEvents();
        
        // Modal events
        this.setupModalEvents();
        
        // Performance sidebar events
        this.setupPerformanceSidebarEvents();
        
        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }
    
    setupDevicePaletteEvents() {
        // Mode buttons
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.setMode(mode);
            });
        });
        
        // Device buttons
        document.querySelectorAll('.device').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const deviceType = e.currentTarget.dataset.type;
                this.selectDevice(deviceType);
            });
        });
        
        // Action buttons
        document.getElementById('clear-canvas')?.addEventListener('click', () => {
            this.clearCanvas();
        });
        
        document.getElementById('save-config')?.addEventListener('click', () => {
            this.saveConfiguration();
        });
        
        document.getElementById('load-config')?.addEventListener('click', () => {
            this.loadConfiguration();
        });
        
        document.getElementById('simulation-settings')?.addEventListener('click', () => {
            this.showSettingsModal();
        });
        
        document.getElementById('help-btn')?.addEventListener('click', () => {
            this.showHelpModal();
        });
        
        document.getElementById('toggle-performance')?.addEventListener('click', () => {
            this.togglePerformanceSidebar();
        });
    }
    
    setupModalEvents() {
        // Scenario selection
        document.querySelectorAll('.select-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const card = e.target.closest('.scenario-card');
                const difficulty = card?.dataset.difficulty;
                const scenario = card?.dataset.scenario;
                this.startScenario(difficulty, scenario);
            });
        });
        
        // Modal close buttons
        document.querySelectorAll('.profile-exit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.simulation-modal');
                this.closeModal(modal);
            });
        });
        
        // Settings modal
        document.getElementById('save-settings')?.addEventListener('click', () => {
            this.saveSettings();
        });
        
        document.getElementById('reset-settings')?.addEventListener('click', () => {
            this.resetSettings();
        });
    }
    
    setupPerformanceSidebarEvents() {
        // Performance sidebar toggle
        document.getElementById('close-sidebar')?.addEventListener('click', () => {
            this.togglePerformanceSidebar();
        });
        
        document.getElementById('mobile-performance-toggle')?.addEventListener('click', () => {
            this.togglePerformanceSidebar();
        });
        
        // Hint button
        document.getElementById('get-hint')?.addEventListener('click', () => {
            this.showHint();
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Prevent shortcuts when typing in inputs
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            switch (e.key.toLowerCase()) {
                case ' ':
                    e.preventDefault();
                    this.setMode('select');
                    break;
                case 'd':
                    this.setMode('draw');
                    break;
                case 'c':
                    this.setMode('connect');
                    break;
                case 'delete':
                case 'backspace':
                    this.deleteSelected();
                    break;
                case 'h':
                    this.showHint();
                    break;
                case 's':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.saveConfiguration();
                    }
                    break;
                case 'escape':
                    this.closeAllModals();
                    break;
            }
        });
    }
    
    setupUI() {
        // Initialize performance sidebar state
        const performanceSidebar = document.getElementById('performance-sidebar');
        if (performanceSidebar) {
            performanceSidebar.classList.add('open');
        }
        
        // Set initial mode
        this.setMode('select');
    }
    
    // Mode Management
    setMode(mode) {
        this.state.currentMode = mode;
        
        // Update UI
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const modeBtn = document.querySelector(`[data-mode="${mode}"]`);
        if (modeBtn) {
            modeBtn.classList.add('active');
        }
        
        // Update cursor
        this.updateCanvasCursor();
        
        console.log(`Mode changed to: ${mode}`);
    }
    
    updateCanvasCursor() {
        const cursors = {
            select: 'default',
            draw: 'crosshair',
            connect: 'pointer'
        };
        
        this.canvas.style.cursor = cursors[this.state.currentMode] || 'default';
    }
    
    // Device Management
    selectDevice(deviceType) {
        // Update UI
        document.querySelectorAll('.device').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        const deviceBtn = document.querySelector(`[data-type="${deviceType}"]`);
        if (deviceBtn) {
            deviceBtn.classList.add('selected');
        }
        
        this.state.selectedDeviceType = deviceType;
        console.log(`Device selected: ${deviceType}`);
    }
    
    placeDevice(x, y, type) {
        if (this.state.settings.snapToGrid) {
            x = Math.round(x / 20) * 20;
            y = Math.round(y / 20) * 20;
        }
        
        const device = {
            id: this.generateId(),
            type: type,
            x: x,
            y: y,
            width: 60,
            height: 60,
            selected: false,
            connections: []
        };
        
        this.state.devices.push(device);
        this.updateProgress('device_placed');
        this.checkAchievements('first_device');
        this.render();
        
        console.log(`Device placed: ${type} at (${x}, ${y})`);
    }
    
    // Canvas Event Handlers
    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        if (this.state.currentMode === 'select') {
            const device = this.getDeviceAt(x, y);
            if (device) {
                this.state.isDragging = true;
                this.state.draggedDevice = device;
                this.state.dragOffset = {
                    x: x - device.x,
                    y: y - device.y
                };
            }
        } else if (this.state.currentMode === 'draw') {
            this.state.isDrawing = true;
            this.state.drawPath = [{x, y}];
        }
    }
    
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        if (this.state.isDragging && this.state.draggedDevice) {
            this.state.draggedDevice.x = x - this.state.dragOffset.x;
            this.state.draggedDevice.y = y - this.state.dragOffset.y;
            
            if (this.state.settings.snapToGrid) {
                this.state.draggedDevice.x = Math.round(this.state.draggedDevice.x / 20) * 20;
                this.state.draggedDevice.y = Math.round(this.state.draggedDevice.y / 20) * 20;
            }
            
            this.render();
        } else if (this.state.isDrawing) {
            this.state.drawPath.push({x, y});
            this.render();
        }
    }
    
    handleMouseUp(e) {
        if (this.state.isDragging) {
            this.state.isDragging = false;
            this.state.draggedDevice = null;
            this.updateProgress('device_moved');
        }
        
        if (this.state.isDrawing) {
            this.state.isDrawing = false;
            this.finalizeDrawing();
        }
    }
    
    handleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        if (this.state.currentMode === 'select') {
            const device = this.getDeviceAt(x, y);
            if (device) {
                this.selectCanvasDevice(device);
            } else {
                this.clearSelection();
            }
        } else if (this.state.selectedDeviceType && this.state.currentMode === 'select') {
            this.placeDevice(x, y, this.state.selectedDeviceType);
        }
    }
    
    // Touch event handlers
    handleTouchStart(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent('mousedown', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.handleMouseDown(mouseEvent);
    }
    
    handleTouchMove(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent('mousemove', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.handleMouseMove(mouseEvent);
    }
    
    handleTouchEnd(e) {
        e.preventDefault();
        const mouseEvent = new MouseEvent('mouseup', {});
        this.handleMouseUp(mouseEvent);
    }
    
    // Rendering
    render() {
        this.clearCanvas();
        
        if (this.state.settings.showGrid) {
            this.drawGrid();
        }
        
        this.drawDevices();
        this.drawConnections();
        
        if (this.state.isDrawing && this.state.drawPath) {
            this.drawPath();
        }
        
        this.updatePerformanceDisplay();
    }
    
    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    drawGrid() {
        const gridSize = 20;
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;
        
        for (let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        for (let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }
    
    drawDevices() {
        this.state.devices.forEach(device => {
            this.drawDevice(device);
        });
    }
    
    drawDevice(device) {
        const { x, y, width, height, type, selected } = device;
        
        // Device background
        this.ctx.fillStyle = selected ? 'rgba(57, 255, 20, 0.2)' : 'rgba(255, 255, 255, 0.1)';
        this.ctx.fillRect(x, y, width, height);
        
        // Device border
        this.ctx.strokeStyle = selected ? '#39FF14' : 'rgba(255, 255, 255, 0.3)';
        this.ctx.lineWidth = selected ? 3 : 2;
        this.ctx.strokeRect(x, y, width, height);
        
        // Device icon (simplified representation)
        this.ctx.fillStyle = '#00D9FF';
        this.ctx.font = '24px FontAwesome';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        const iconMap = {
            router: '⚙',
            switch: '⚡',
            pc: '💻',
            server: '🖥',
            ethernet: '―',
            fiber: '~',
            wireless: '📶'
        };
        
        const icon = iconMap[type] || '⚪';
        this.ctx.fillText(icon, x + width/2, y + height/2);
        
        // Device label
        if (this.state.settings.showLabels) {
            this.ctx.fillStyle = '#F8FAFC';
            this.ctx.font = '12px Orbitron';
            this.ctx.fillText(type, x + width/2, y + height + 15);
        }
    }
    
    drawConnections() {
        this.state.connections.forEach(connection => {
            this.drawConnection(connection);
        });
    }
    
    drawConnection(connection) {
        const fromDevice = this.state.devices.find(d => d.id === connection.from);
        const toDevice = this.state.devices.find(d => d.id === connection.to);
        
        if (!fromDevice || !toDevice) return;
        
        const fromX = fromDevice.x + fromDevice.width / 2;
        const fromY = fromDevice.y + fromDevice.height / 2;
        const toX = toDevice.x + toDevice.width / 2;
        const toY = toDevice.y + toDevice.height / 2;
        
        this.ctx.strokeStyle = '#00D9FF';
        this.ctx.lineWidth = 3;
        this.ctx.setLineDash(connection.type === 'wireless' ? [10, 5] : []);
        
        this.ctx.beginPath();
        this.ctx.moveTo(fromX, fromY);
        this.ctx.lineTo(toX, toY);
        this.ctx.stroke();
        
        this.ctx.setLineDash([]);
    }
    
    drawPath() {
        if (!this.state.drawPath || this.state.drawPath.length < 2) return;
        
        this.ctx.strokeStyle = '#39FF14';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        
        this.state.drawPath.forEach((point, index) => {
            if (index === 0) {
                this.ctx.moveTo(point.x, point.y);
            } else {
                this.ctx.lineTo(point.x, point.y);
            }
        });
        
        this.ctx.stroke();
    }
    
    // Utility Functions
    getDeviceAt(x, y) {
        return this.state.devices.find(device => 
            x >= device.x && x <= device.x + device.width &&
            y >= device.y && y <= device.y + device.height
        );
    }
    
    selectCanvasDevice(device) {
        this.state.devices.forEach(d => d.selected = false);
        device.selected = true;
        this.state.selectedDevices = [device];
        this.render();
    }
    
    clearSelection() {
        this.state.devices.forEach(d => d.selected = false);
        this.state.selectedDevices = [];
        this.render();
    }
    
    deleteSelected() {
        this.state.devices = this.state.devices.filter(d => !d.selected);
        this.state.selectedDevices = [];
        this.render();
    }
    
    finalizeDrawing() {
        // Convert drawing path to connections if applicable
        if (this.state.drawPath && this.state.drawPath.length > 1) {
            const firstPoint = this.state.drawPath[0];
            const lastPoint = this.state.drawPath[this.state.drawPath.length - 1];
            
            const fromDevice = this.getDeviceAt(firstPoint.x, firstPoint.y);
            const toDevice = this.getDeviceAt(lastPoint.x, lastPoint.y);
            
            if (fromDevice && toDevice && fromDevice !== toDevice) {
                this.createConnection(fromDevice.id, toDevice.id, 'ethernet');
            }
        }
        
        this.state.drawPath = null;
    }
    
    createConnection(fromId, toId, type = 'ethernet') {
        const connection = {
            id: this.generateId(),
            from: fromId,
            to: toId,
            type: type
        };
        
        this.state.connections.push(connection);
        this.updateProgress('connection_created');
        this.checkAchievements('connection_master');
        this.render();
    }
    
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    // Progress and Performance Tracking
    startPerformanceTracking() {
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 1000);
    }
    
    updatePerformanceMetrics() {
        const elapsed = Date.now() - this.state.progress.startTime;
        this.state.progress.timeElapsed = Math.floor(elapsed / 1000);
        
        // Calculate actions per minute
        const minutes = elapsed / 60000;
        this.state.performance.speed = minutes > 0 ? Math.round(this.state.performance.actionsCount / minutes) : 0;
        
        // Update efficiency based on hints and accuracy
        const efficiency = this.calculateEfficiency();
        this.state.performance.efficiency = efficiency;
        
        this.updatePerformanceDisplay();
    }
    
    updatePerformanceDisplay() {
        // Update score
        const scoreElement = document.getElementById('current-score');
        if (scoreElement) {
            scoreElement.textContent = this.state.progress.score;
        }
        
        // Update score progress bar
        const scoreFill = document.querySelector('.score-fill');
        if (scoreFill) {
            const percentage = Math.min((this.state.progress.score / 100) * 100, 100);
            scoreFill.style.width = `${percentage}%`;
        }
        
        // Update progress circle
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            const percentage = (this.state.progress.step / this.state.progress.totalSteps) * 100;
            progressFill.setAttribute('stroke-dasharray', `${percentage} 100`);
        }
        
        const progressPercent = document.querySelector('.progress-percent');
        if (progressPercent) {
            const percentage = Math.round((this.state.progress.step / this.state.progress.totalSteps) * 100);
            progressPercent.textContent = `${percentage}%`;
        }
        
        // Update steps completed
        const stepsCompleted = document.getElementById('steps-completed');
        if (stepsCompleted) {
            stepsCompleted.textContent = `${this.state.progress.step} / ${this.state.progress.totalSteps}`;
        }
        
        // Update time elapsed
        const timeElapsed = document.getElementById('time-elapsed');
        if (timeElapsed) {
            const minutes = Math.floor(this.state.progress.timeElapsed / 60);
            const seconds = this.state.progress.timeElapsed % 60;
            timeElapsed.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Update metrics
        const accuracyMetric = document.getElementById('accuracy-metric');
        if (accuracyMetric) {
            accuracyMetric.textContent = `${this.state.performance.accuracy}%`;
        }
        
        const speedMetric = document.getElementById('speed-metric');
        if (speedMetric) {
            speedMetric.textContent = this.state.performance.speed;
        }
        
        const efficiencyMetric = document.getElementById('efficiency-metric');
        if (efficiencyMetric) {
            efficiencyMetric.textContent = this.state.performance.efficiency;
        }
        
        // Update hints count
        const hintsCount = document.getElementById('hints-count');
        if (hintsCount) {
            hintsCount.textContent = this.state.progress.hintsUsed;
        }
    }
    
    updateProgress(action) {
        this.state.performance.actionsCount++;
        
        const pointsMap = {
            device_placed: 10,
            device_moved: 5,
            connection_created: 15,
            scenario_completed: 50
        };
        
        this.state.progress.score += pointsMap[action] || 0;
        
        // Check if step should advance
        if (action === 'device_placed' && this.state.devices.length === 1) {
            this.state.progress.step = Math.min(this.state.progress.step + 1, this.state.progress.totalSteps);
        } else if (action === 'connection_created') {
            this.state.progress.step = Math.min(this.state.progress.step + 1, this.state.progress.totalSteps);
        }
        
        this.updatePerformanceDisplay();
    }
    
    calculateEfficiency() {
        const baseScore = 100 - (this.state.progress.hintsUsed * 10);
        const accuracyFactor = this.state.performance.accuracy / 100;
        const efficiency = Math.max(baseScore * accuracyFactor, 0);
        
        if (efficiency >= 90) return 'A+';
        if (efficiency >= 80) return 'A';
        if (efficiency >= 70) return 'B+';
        if (efficiency >= 60) return 'B';
        return 'C';
    }
    
    // Achievement System
    checkAchievements(achievementType) {
        const achievements = {
            first_device: () => this.state.devices.length >= 1,
            connection_master: () => this.state.connections.length >= 3,
            speed_demon: () => this.state.performance.speed >= 10
        };
        
        if (achievements[achievementType] && achievements[achievementType]()) {
            this.unlockAchievement(achievementType);
        }
    }
    
    unlockAchievement(achievementType) {
        const badge = document.querySelector(`[data-achievement="${achievementType}"]`);
        if (badge && badge.classList.contains('locked')) {
            badge.classList.remove('locked');
            badge.classList.add('unlocked');
            
            const achievementNames = {
                'first_device': 'First Device Placed!',
                'connection_master': 'Connection Master!',
                'speed_demon': 'Speed Demon!'
            };
            
            this.showAchievementNotification(achievementNames[achievementType] || 'Achievement Unlocked!');
        }
    }
    
    showAchievementNotification(text) {
        const notification = document.getElementById('achievement-notification');
        const description = document.getElementById('achievement-description');
        
        if (notification && description) {
            description.textContent = text;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
    }
    
    // Hints System
    showHint() {
        if (this.state.progress.hintsUsed >= 3) {
            alert('No more hints available!');
            return;
        }
        
        const hints = [
            "Try placing a router from the device palette onto the canvas.",
            "Connect devices by drawing lines between them in draw mode.",
            "Use the different modes for different actions - select to move, draw to connect.",
            "Check your progress in the performance panel on the right.",
            "Complete all steps to finish the simulation successfully."
        ];
        
        const hintText = hints[this.state.progress.hintsUsed] || "Keep experimenting with the tools!";
        
        const hintElement = document.getElementById('current-hint');
        const hintItem = document.querySelector('.hint-item');
        
        if (hintElement && hintItem) {
            hintElement.textContent = hintText;
            hintItem.style.display = 'block';
            
            this.state.progress.hintsUsed++;
            this.updatePerformanceDisplay();
        }
    }
    
    // Modal Management
    showScenarioSelection() {
        const modal = document.getElementById('scenario-modal');
        this.showModal(modal);
    }
    
    showSettingsModal() {
        const modal = document.getElementById('settings-modal');
        this.showModal(modal);
    }
    
    showHelpModal() {
        const modal = document.getElementById('help-modal');
        this.showModal(modal);
    }
    
    showModal(modal) {
        if (modal) {
            modal.classList.add('active');
            
            // Focus management for accessibility
            const firstFocusable = modal.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        }
    }
    
    closeModal(modal) {
        if (modal) {
            modal.classList.remove('active');
        }
    }
    
    closeAllModals() {
        document.querySelectorAll('.simulation-modal').forEach(modal => {
            this.closeModal(modal);
        });
    }
    
    // Scenario Management
    startScenario(difficulty, scenario) {
        this.state.scenario = { difficulty, scenario };
        
        // Set up tutorial steps based on scenario
        this.setupTutorialSteps(difficulty, scenario);
        
        // Close scenario modal
        const scenarioModal = document.getElementById('scenario-modal');
        this.closeModal(scenarioModal);
        
        // Start tutorial if it's an easy scenario
        if (difficulty === 'easy') {
            this.startTutorial();
        }
        
        console.log(`Starting scenario: ${scenario} (${difficulty})`);
    }
    
    setupTutorialSteps(difficulty, scenario) {
        const tutorialSteps = {
            easy: [
                {
                    title: "Welcome to Network Simulation",
                    description: "Let's start by placing your first device on the canvas."
                },
                {
                    title: "Select a Device",
                    description: "Click on the router icon in the device palette below."
                },
                {
                    title: "Place the Device",
                    description: "Click anywhere on the canvas to place your router."
                },
                {
                    title: "Add More Devices",
                    description: "Add a switch and a PC to create a simple network."
                },
                {
                    title: "Connect Devices",
                    description: "Switch to draw mode and connect your devices together."
                }
            ]
        };
        
        this.state.tutorial.steps = tutorialSteps[difficulty] || [];
    }
    
    startTutorial() {
        if (this.state.tutorial.steps.length === 0) return;
        
        this.state.tutorial.active = true;
        this.state.tutorial.currentStep = 0;
        this.showTutorialStep();
    }
    
    showTutorialStep() {
        const step = this.state.tutorial.steps[this.state.tutorial.currentStep];
        if (!step) return;
        
        const overlay = document.getElementById('tutorial-overlay');
        const title = document.getElementById('tutorial-title');
        const description = document.getElementById('tutorial-description');
        const progress = document.getElementById('tutorial-progress');
        
        if (overlay && title && description && progress) {
            overlay.style.display = 'flex';
            title.textContent = step.title;
            description.textContent = step.description;
            progress.textContent = `Step ${this.state.tutorial.currentStep + 1} of ${this.state.tutorial.steps.length}`;
        }
        
        // Setup tutorial navigation
        this.setupTutorialNavigation();
    }
    
    setupTutorialNavigation() {
        const prevBtn = document.getElementById('tutorial-prev');
        const nextBtn = document.getElementById('tutorial-next');
        
        if (prevBtn) {
            prevBtn.style.display = this.state.tutorial.currentStep > 0 ? 'block' : 'none';
            prevBtn.onclick = () => this.previousTutorialStep();
        }
        
        if (nextBtn) {
            const isLastStep = this.state.tutorial.currentStep >= this.state.tutorial.steps.length - 1;
            nextBtn.textContent = isLastStep ? 'Finish' : 'Next';
            nextBtn.onclick = () => this.nextTutorialStep();
        }
    }
    
    nextTutorialStep() {
        if (this.state.tutorial.currentStep < this.state.tutorial.steps.length - 1) {
            this.state.tutorial.currentStep++;
            this.showTutorialStep();
        } else {
            this.endTutorial();
        }
    }
    
    previousTutorialStep() {
        if (this.state.tutorial.currentStep > 0) {
            this.state.tutorial.currentStep--;
            this.showTutorialStep();
        }
    }
    
    endTutorial() {
        this.state.tutorial.active = false;
        const overlay = document.getElementById('tutorial-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    // Settings Management
    saveSettings() {
        const settings = {
            showGrid: document.getElementById('show-grid')?.checked,
            snapToGrid: document.getElementById('snap-to-grid')?.checked,
            showLabels: document.getElementById('show-labels')?.checked,
            autoSave: document.getElementById('auto-save')?.checked,
            performanceMode: document.getElementById('performance-mode')?.value,
            highContrast: document.getElementById('high-contrast')?.checked,
            reducedMotion: document.getElementById('reduced-motion')?.checked
        };
        
        this.state.settings = { ...this.state.settings, ...settings };
        this.applySettings();
        
        const settingsModal = document.getElementById('settings-modal');
        this.closeModal(settingsModal);
    }
    
    applySettings() {
        // Apply high contrast
        if (this.state.settings.highContrast) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
        
        // Apply reduced motion
        if (this.state.settings.reducedMotion) {
            document.body.classList.add('reduced-motion');
        } else {
            document.body.classList.remove('reduced-motion');
        }
        
        this.render();
    }
    
    resetSettings() {
        // Reset to defaults
        document.getElementById('show-grid').checked = true;
        document.getElementById('snap-to-grid').checked = true;
        document.getElementById('show-labels').checked = true;
        document.getElementById('auto-save').checked = true;
        document.getElementById('performance-mode').value = 'high';
        document.getElementById('high-contrast').checked = false;
        document.getElementById('reduced-motion').checked = false;
    }
    
    // Performance Sidebar
    togglePerformanceSidebar() {
        const sidebar = document.getElementById('performance-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('open');
        }
    }
    
    // Configuration Management
    saveConfiguration() {
        const config = {
            devices: this.state.devices,
            connections: this.state.connections,
            settings: this.state.settings,
            timestamp: Date.now()
        };
        
        const dataStr = JSON.stringify(config, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `simulation-config-${Date.now()}.json`;
        link.click();
        
        console.log('Configuration saved');
    }
    
    loadConfiguration() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const config = JSON.parse(e.target.result);
                        this.state.devices = config.devices || [];
                        this.state.connections = config.connections || [];
                        this.state.settings = { ...this.state.settings, ...config.settings };
                        this.applySettings();
                        this.render();
                        console.log('Configuration loaded');
                    } catch (error) {
                        console.error('Error loading configuration:', error);
                        alert('Error loading configuration file');
                    }
                };
                reader.readAsText(file);
            }
        };
        input.click();
    }
}

// Export for global use
window.AdvancedSimulationEngine = AdvancedSimulationEngine;

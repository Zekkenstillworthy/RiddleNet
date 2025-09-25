/**
 * Gamified Topology System
 * ========================
 * 
 * Enhanced topology simulation with:
 * - Difficulty-based progression (Easy/Medium/Hard)
 * - Achievement system
 * - Real-time scoring
 * - Interactive tutorials
 * - Progress tracking
 */

class GamifiedTopologyApp {
    constructor() {
        this.currentScenario = null;
        this.startTime = null;
        this.timer = null;
        this.currentScore = 0;
        this.isConnecting = false;
        this.selectedDevice = null;
        this.devices = [];
        this.connections = [];
        this.canvas = null;
        this.ctx = null;
        this.tutorialStep = 0;
        this.tutorialSteps = [];
        this.hintsUsed = 0;
        
        // Device images
        this.deviceImages = {};
        this.loadDeviceImages();
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }
    
    async loadDeviceImages() {
        const imageUrls = {
            pc: '/static/img/PC.png',
            router: '/static/img/Router.png',
            switch: '/static/img/Switch.png',
            server: '/static/img/Server.png'
        };
        
        for (const [type, url] of Object.entries(imageUrls)) {
            const img = new Image();
            img.src = url;
            await new Promise(resolve => {
                img.onload = resolve;
                img.onerror = resolve;
            });
            this.deviceImages[type] = img;
        }
    }
    
    initialize() {
        console.log('Initializing Gamified Topology App');
        
        this.setupCanvas();
        this.setupEventListeners();
        this.populateScenarios();
        this.updateProgressDisplay();
        
        // Show welcome message initially
        this.showWelcomeMessage();
    }
    
    setupCanvas() {
        this.canvas = document.getElementById('Canvas');
        if (!this.canvas) {
            console.error('Canvas element not found');
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.resizeCanvas();
        
        // Setup canvas event listeners
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('dragover', (e) => e.preventDefault());
        this.canvas.addEventListener('drop', (e) => this.handleCanvasDrop(e));
        
        // Window resize handler
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    resizeCanvas() {
        const container = document.getElementById('canvas-container');
        if (!container || !this.canvas) return;
        
        const rect = container.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        
        this.redrawCanvas();
    }
    
    setupEventListeners() {
        // Device drag and drop
        document.querySelectorAll('.device').forEach(device => {
            device.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', device.dataset.type);
            });
        });
        
        // Tool buttons
        document.getElementById('connection-mode-btn')?.addEventListener('click', () => {
            this.toggleConnectionMode();
        });
        
        document.getElementById('delete-device-btn')?.addEventListener('click', () => {
            this.enableDeleteMode('device');
        });
        
        document.getElementById('delete-connection-btn')?.addEventListener('click', () => {
            this.enableDeleteMode('connection');
        });
        
        document.getElementById('clear-canvas-btn')?.addEventListener('click', () => {
            this.clearCanvas();
        });
        
        // Validation button
        document.getElementById('validate-btn')?.addEventListener('click', () => {
            this.validateCurrentTopology();
        });
    }
    
    populateScenarios() {
        const categoriesContainer = document.getElementById('scenario-categories');
        if (!categoriesContainer) return;
        
        const scenarios = GAMIFIED_TOPOLOGY_DATA.scenarios || [];
        
        // Group scenarios by topology type
        const scenariosByType = {};
        scenarios.forEach(scenario => {
            if (!scenariosByType[scenario.topology_type]) {
                scenariosByType[scenario.topology_type] = [];
            }
            scenariosByType[scenario.topology_type].push(scenario);
        });
        
        // Create category sections
        categoriesContainer.innerHTML = '';
        
        Object.entries(scenariosByType).forEach(([topologyType, typeScenarios]) => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'topology-category';
            
            const titleDiv = document.createElement('div');
            titleDiv.className = 'category-title';
            titleDiv.textContent = this.formatTopologyName(topologyType);
            categoryDiv.appendChild(titleDiv);
            
            const gridDiv = document.createElement('div');
            gridDiv.className = 'scenario-grid';
            
            // Sort by difficulty: easy, medium, hard
            const difficultyOrder = ['easy', 'medium', 'hard'];
            typeScenarios.sort((a, b) => {
                return difficultyOrder.indexOf(a.difficulty) - difficultyOrder.indexOf(b.difficulty);
            });
            
            typeScenarios.forEach(scenario => {
                const card = this.createScenarioCard(scenario);
                gridDiv.appendChild(card);
            });
            
            categoryDiv.appendChild(gridDiv);
            categoriesContainer.appendChild(categoryDiv);
        });
    }
    
    createScenarioCard(scenario) {
        const card = document.createElement('div');
        card.className = `scenario-card ${scenario.is_completed ? 'completed' : ''} ${!scenario.is_unlocked ? 'locked' : ''}`;
        card.dataset.scenarioId = scenario.id;
        
        // Difficulty badge
        const badge = document.createElement('div');
        badge.className = `difficulty-badge difficulty-${scenario.difficulty}`;
        badge.textContent = scenario.difficulty;
        card.appendChild(badge);
        
        // Scenario name
        const name = document.createElement('div');
        name.className = 'scenario-name';
        name.textContent = scenario.name;
        card.appendChild(name);
        
        // Description
        const description = document.createElement('div');
        description.className = 'scenario-description';
        description.textContent = scenario.description;
        card.appendChild(description);
        
        // Stats
        const stats = document.createElement('div');
        stats.className = 'scenario-stats';
        
        const timeLimit = document.createElement('span');
        timeLimit.innerHTML = `<i class="fas fa-clock"></i> ${Math.floor(scenario.time_limit / 60)}min`;
        
        const bestScore = document.createElement('span');
        bestScore.innerHTML = `<i class="fas fa-star"></i> ${scenario.best_score || 0}`;
        
        stats.appendChild(timeLimit);
        stats.appendChild(bestScore);
        card.appendChild(stats);
        
        // Click handler
        if (scenario.is_unlocked) {
            card.addEventListener('click', () => this.selectScenario(scenario));
        }
        
        return card;
    }
    
    formatTopologyName(topologyType) {
        return topologyType.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
    async selectScenario(scenario) {
        if (!scenario.is_unlocked) {
            this.showMessage('This scenario is locked. Complete the previous difficulty first!', 'warning');
            return;
        }
        
        try {
            // Start the scenario on the server
            const response = await fetch(`/topology/api/scenario/${scenario.id}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (!result.success) {
                this.showMessage(result.error || 'Failed to start scenario', 'error');
                return;
            }
            
            this.currentScenario = scenario;
            this.startTime = new Date();
            this.currentScore = 0;
            this.hintsUsed = 0;
            this.devices = [];
            this.connections = [];
            
            this.setupScenarioUI();
            this.startTimer();
            this.clearCanvas();
            this.showDevicePalette();
            this.hideWelcomeMessage();
            this.displayRequirements();
            
            // Play start sound
            this.playSound('clickSound');
            
            console.log('Started scenario:', scenario);
            
        } catch (error) {
            console.error('Error starting scenario:', error);
            this.showMessage('Failed to start scenario', 'error');
        }
    }
    
    setupScenarioUI() {
        // Update header
        const titleElement = document.getElementById('current-scenario-title');
        if (titleElement && this.currentScenario) {
            titleElement.textContent = `${this.currentScenario.name} (${this.currentScenario.difficulty.toUpperCase()})`;
        }
        
        // Show control elements
        document.getElementById('timer-display').style.display = 'block';
        document.getElementById('score-display').style.display = 'block';
        document.getElementById('hint-btn').style.display = 'block';
        document.getElementById('tutorial-btn').style.display = 'block';
        document.getElementById('validate-btn').style.display = 'block';
        
        this.updateScoreDisplay();
    }
    
    showDevicePalette() {
        document.getElementById('device-palette').style.display = 'block';
    }
    
    hideDevicePalette() {
        document.getElementById('device-palette').style.display = 'none';
    }
    
    displayRequirements() {
        if (!this.currentScenario) return;
        
        const panel = document.getElementById('requirements-panel');
        const list = document.getElementById('requirements-list');
        
        if (!panel || !list) return;
        
        panel.style.display = 'block';
        list.innerHTML = '';
        
        const requirements = this.currentScenario.requirements;
        Object.entries(requirements).forEach(([deviceType, count]) => {
            if (count > 0) {
                const item = document.createElement('div');
                item.className = 'requirement-item';
                item.innerHTML = `
                    <span><i class="fas fa-${this.getDeviceIcon(deviceType)}"></i> ${deviceType.toUpperCase()}</span>
                    <span>${count}</span>
                `;
                list.appendChild(item);
            }
        });
    }
    
    getDeviceIcon(deviceType) {
        const icons = {
            pc: 'desktop',
            router: 'network-wired',
            switch: 'project-diagram',
            server: 'server'
        };
        return icons[deviceType] || 'question';
    }
    
    startTimer() {
        if (this.timer) clearInterval(this.timer);
        
        this.timer = setInterval(() => {
            if (!this.startTime) return;
            
            const elapsed = Math.floor((new Date() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            const timerElement = document.getElementById('timer');
            if (timerElement) {
                timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
            
            // Check time limit
            if (this.currentScenario && elapsed > this.currentScenario.time_limit) {
                this.handleTimeOut();
            }
        }, 1000);
    }
    
    stopTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
    
    handleTimeOut() {
        this.stopTimer();
        this.showMessage('Time\'s up! Try again to improve your time.', 'warning');
        this.validateCurrentTopology(); // Auto-validate when time runs out
    }
    
    updateScoreDisplay() {
        const scoreElement = document.getElementById('current-score');
        if (scoreElement) {
            scoreElement.textContent = this.currentScore;
        }
    }
    
    updateProgressDisplay() {
        const progressData = GAMIFIED_TOPOLOGY_DATA.userProgress || {};
        
        document.getElementById('completed-count').textContent = 
            `${progressData.total_completed || 0}/${progressData.total_scenarios || 0}`;
        
        document.getElementById('total-score').textContent = progressData.total_score || 0;
        
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progressData.completion_percentage || 0}%`;
        }
    }
    
    handleCanvasDrop(e) {
        e.preventDefault();
        
        const deviceType = e.dataTransfer.getData('text/plain');
        if (!deviceType) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        this.addDevice(deviceType, x, y);
        this.playSound('clickSound');
    }
    
    addDevice(type, x, y) {
        const deviceId = `${type}_${this.devices.length + 1}`;
        const device = {
            id: deviceId,
            type: type,
            x: x,
            y: y,
            label: deviceId.toUpperCase(),
            selected: false
        };
        
        this.devices.push(device);
        this.redrawCanvas();
        console.log('Added device:', device);
    }
    
    handleCanvasClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const clickedDevice = this.findDeviceAt(x, y);
        
        if (this.isConnecting) {
            this.handleConnectionClick(clickedDevice);
        } else {
            this.selectDevice(clickedDevice);
        }
        
        this.redrawCanvas();
    }
    
    findDeviceAt(x, y) {
        return this.devices.find(device => {
            const dx = x - device.x;
            const dy = y - device.y;
            return Math.sqrt(dx * dx + dy * dy) < 30; // 30px radius
        });
    }
    
    selectDevice(device) {
        // Deselect all devices
        this.devices.forEach(d => d.selected = false);
        
        if (device) {
            device.selected = true;
            console.log('Selected device:', device);
        }
        
        this.selectedDevice = device;
    }
    
    toggleConnectionMode() {
        this.isConnecting = !this.isConnecting;
        this.selectedDevice = null;
        
        const btn = document.getElementById('connection-mode-btn');
        if (btn) {
            btn.classList.toggle('active', this.isConnecting);
            btn.innerHTML = this.isConnecting ? 
                '<i class="fas fa-link"></i> Connecting...' : 
                '<i class="fas fa-link"></i> Connect Mode';
        }
        
        this.redrawCanvas();
    }
    
    handleConnectionClick(device) {
        if (!device) return;
        
        if (!this.selectedDevice) {
            this.selectDevice(device);
        } else if (this.selectedDevice !== device) {
            // Create connection
            this.addConnection(this.selectedDevice, device);
            this.selectedDevice = null;
            this.devices.forEach(d => d.selected = false);
            this.isConnecting = false;
            
            // Reset connection mode button
            const btn = document.getElementById('connection-mode-btn');
            if (btn) {
                btn.classList.remove('active');
                btn.innerHTML = '<i class="fas fa-link"></i> Connect Mode';
            }
        }
    }
    
    addConnection(device1, device2) {
        // Check if connection already exists
        const exists = this.connections.some(conn => 
            (conn.device1.id === device1.id && conn.device2.id === device2.id) ||
            (conn.device1.id === device2.id && conn.device2.id === device1.id)
        );
        
        if (exists) {
            this.showMessage('Connection already exists!', 'warning');
            return;
        }
        
        const connection = {
            id: `conn_${this.connections.length + 1}`,
            device1: device1,
            device2: device2
        };
        
        this.connections.push(connection);
        this.playSound('clickSound');
        console.log('Added connection:', connection);
    }
    
    clearCanvas() {
        this.devices = [];
        this.connections = [];
        this.selectedDevice = null;
        this.isConnecting = false;
        
        // Reset UI
        const btn = document.getElementById('connection-mode-btn');
        if (btn) {
            btn.classList.remove('active');
            btn.innerHTML = '<i class="fas fa-link"></i> Connect Mode';
        }
        
        this.redrawCanvas();
    }
    
    redrawCanvas() {
        if (!this.ctx) return;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw connections first (so they appear behind devices)
        this.connections.forEach(connection => this.drawConnection(connection));
        
        // Draw devices
        this.devices.forEach(device => this.drawDevice(device));
    }
    
    drawConnection(connection) {
        this.ctx.strokeStyle = '#00C3B5';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.moveTo(connection.device1.x, connection.device1.y);
        this.ctx.lineTo(connection.device2.x, connection.device2.y);
        this.ctx.stroke();
    }
    
    drawDevice(device) {
        const img = this.deviceImages[device.type];
        if (img && img.complete) {
            const size = 50;
            this.ctx.drawImage(img, device.x - size/2, device.y - size/2, size, size);
        } else {
            // Fallback circle
            this.ctx.fillStyle = device.selected ? '#FFD700' : '#00C3B5';
            this.ctx.beginPath();
            this.ctx.arc(device.x, device.y, 25, 0, 2 * Math.PI);
            this.ctx.fill();
        }
        
        // Device label
        this.ctx.fillStyle = '#000';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(device.label, device.x, device.y + 40);
        
        // Selection highlight
        if (device.selected) {
            this.ctx.strokeStyle = '#FFD700';
            this.ctx.lineWidth = 3;
            this.ctx.beginPath();
            this.ctx.arc(device.x, device.y, 30, 0, 2 * Math.PI);
            this.ctx.stroke();
        }
    }
    
    async validateCurrentTopology() {
        if (!this.currentScenario) {
            this.showMessage('No scenario selected!', 'error');
            return;
        }
        
        const completionTime = this.startTime ? 
            Math.floor((new Date() - this.startTime) / 1000) : null;
        
        try {
            const response = await fetch(`/topology/api/scenario/${this.currentScenario.id}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    devices: this.devices,
                    connections: this.connections,
                    completion_time: completionTime,
                    start_time: this.startTime?.toISOString()
                })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                this.showMessage(result.error || 'Validation failed', 'error');
                return;
            }
            
            this.handleValidationResult(result.validation);
            
        } catch (error) {
            console.error('Validation error:', error);
            this.showMessage('Failed to validate topology', 'error');
        }
    }
    
    handleValidationResult(validation) {
        this.stopTimer();
        
        if (validation.valid) {
            this.currentScore = validation.score;
            this.updateScoreDisplay();
            
            this.playSound('successSound');
            this.showMessage(`Great job! Score: ${validation.score}`, 'success');
            
            // Show achievements if any
            if (validation.achievements && validation.achievements.length > 0) {
                validation.achievements.forEach(achievement => {
                    this.showAchievement(achievement);
                });
            }
            
            // Update progress display
            setTimeout(() => {
                this.updateProgressAfterCompletion();
            }, 2000);
            
        } else {
            this.showMessage(`Validation failed: ${validation.errors.join(', ')}`, 'error');
        }
    }
    
    async updateProgressAfterCompletion() {
        try {
            const response = await fetch('/topology/api/progress');
            const result = await response.json();
            
            if (result.success) {
                GAMIFIED_TOPOLOGY_DATA.userProgress = result.progress;
                this.updateProgressDisplay();
                this.populateScenarios(); // Refresh to show new unlocked scenarios
            }
        } catch (error) {
            console.error('Failed to update progress:', error);
        }
    }
    
    showAchievement(achievement) {
        const notification = document.getElementById('achievement-notification');
        const title = document.getElementById('achievement-title');
        const description = document.getElementById('achievement-description');
        
        if (notification && title && description) {
            title.textContent = `${achievement.icon} ${achievement.name}`;
            description.textContent = achievement.description;
            
            notification.classList.add('show');
            this.playSound('achievementSound');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 4000);
        }
    }
    
    showWelcomeMessage() {
        document.getElementById('welcome-message').style.display = 'flex';
    }
    
    hideWelcomeMessage() {
        document.getElementById('welcome-message').style.display = 'none';
    }
    
    showMessage(message, type = 'info') {
        // You could implement a toast notification system here
        console.log(`${type.toUpperCase()}: ${message}`);
        alert(message); // Simple fallback
    }
    
    playSound(soundId) {
        try {
            const audio = document.getElementById(soundId);
            if (audio) {
                audio.currentTime = 0;
                audio.play().catch(e => console.log('Audio play failed:', e));
            }
        } catch (error) {
            console.log('Sound error:', error);
        }
    }
    
    async getHint() {
        if (!this.currentScenario) return;
        
        try {
            const response = await fetch('/topology/api/hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scenario_id: this.currentScenario.id,
                    current_step: this.tutorialStep
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showMessage(result.hint, 'info');
                this.hintsUsed = result.hints_used;
            } else {
                this.showMessage(result.error || 'Failed to get hint', 'error');
            }
        } catch (error) {
            console.error('Hint error:', error);
            this.showMessage('Failed to get hint', 'error');
        }
    }
    
    async showTutorial() {
        if (!this.currentScenario) return;
        
        try {
            const response = await fetch(`/topology/api/scenarios/${this.currentScenario.id}/tutorial`);
            const result = await response.json();
            
            if (result.success) {
                this.tutorialSteps = result.tutorial.steps;
                this.tutorialStep = 0;
                this.displayTutorial();
            } else {
                this.showMessage(result.error || 'Failed to load tutorial', 'error');
            }
        } catch (error) {
            console.error('Tutorial error:', error);
            this.showMessage('Failed to load tutorial', 'error');
        }
    }
    
    displayTutorial() {
        const modal = document.getElementById('tutorial-modal');
        const title = document.getElementById('tutorial-title');
        const steps = document.getElementById('tutorial-steps');
        
        if (!modal || !title || !steps || !this.currentScenario) return;
        
        title.textContent = `${this.currentScenario.name} Tutorial`;
        
        steps.innerHTML = '';
        this.tutorialSteps.forEach((step, index) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = `tutorial-step ${index === this.tutorialStep ? 'active' : ''}`;
            stepDiv.innerHTML = `<strong>Step ${index + 1}:</strong> ${step}`;
            steps.appendChild(stepDiv);
        });
        
        modal.style.display = 'flex';
        this.updateTutorialNavigation();
    }
    
    updateTutorialNavigation() {
        const prevBtn = document.getElementById('tutorial-prev');
        const nextBtn = document.getElementById('tutorial-next');
        
        if (prevBtn) prevBtn.disabled = this.tutorialStep === 0;
        if (nextBtn) nextBtn.disabled = this.tutorialStep >= this.tutorialSteps.length - 1;
    }
    
    nextTutorialStep() {
        if (this.tutorialStep < this.tutorialSteps.length - 1) {
            this.tutorialStep++;
            this.displayTutorial();
        }
    }
    
    previousTutorialStep() {
        if (this.tutorialStep > 0) {
            this.tutorialStep--;
            this.displayTutorial();
        }
    }
    
    closeTutorial() {
        const modal = document.getElementById('tutorial-modal');
        if (modal) modal.style.display = 'none';
    }
}

// Global functions for button handlers
function initializeGamifiedTopology() {
    window.gamifiedTopologyApp = new GamifiedTopologyApp();
}

function getHint() {
    if (window.gamifiedTopologyApp) {
        window.gamifiedTopologyApp.getHint();
    }
}

function showTutorial() {
    if (window.gamifiedTopologyApp) {
        window.gamifiedTopologyApp.showTutorial();
    }
}

function validateTopology() {
    if (window.gamifiedTopologyApp) {
        window.gamifiedTopologyApp.validateCurrentTopology();
    }
}

function nextTutorialStep() {
    if (window.gamifiedTopologyApp) {
        window.gamifiedTopologyApp.nextTutorialStep();
    }
}

function previousTutorialStep() {
    if (window.gamifiedTopologyApp) {
        window.gamifiedTopologyApp.previousTutorialStep();
    }
}

function closeTutorial() {
    if (window.gamifiedTopologyApp) {
        window.gamifiedTopologyApp.closeTutorial();
    }
}

function showAchievements() {
    // Implement achievements modal
    alert('Achievements feature coming soon!');
}

function showLeaderboard() {
    // Implement leaderboard modal
    alert('Leaderboard feature coming soon!');
}

function resetProgress() {
    if (confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
        fetch('/topology/api/reset-progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ confirm: true })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                location.reload();
            } else {
                alert(result.error || 'Failed to reset progress');
            }
        })
        .catch(error => {
            console.error('Reset error:', error);
            alert('Failed to reset progress');
        });
    }
}

// Export the class for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GamifiedTopologyApp;
}
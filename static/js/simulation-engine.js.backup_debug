/**
 * Enhanced Simulation Engine - Following troubleshoot.html patterns
 * Provides comprehensive simulation functionality with performance tracking,
 * hint system, achievement unlocks, and collaborative features.
 */

class SimulationEngine {
    constructor() {
        this.state = {
            currentMode: 'select',
            selectedTool: null,
            score: 0,
            progress: 0,
            startTime: Date.now(),
            actionCount: 0,
            hintsUsed: 0,
            accuracy: 100,
            achievements: [],
            difficulty: 'medium',
            scenario: null,
            isRunning: false,
            isPaused: false
        };
        
        this.canvas = null;
        this.ctx = null;
        this.performanceInterval = null;
        this.elements = [];
        this.connections = [];
        this.selectedElement = null;
        
        this.init();
    }

    init() {
        console.log('🚀 Initializing Enhanced Simulation Engine...');
        
        // Initialize canvas
        this.setupCanvas();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize performance tracking
        this.startPerformanceTracking();
        
        // Show initial tutorial
        setTimeout(() => this.showInitialTutorial(), 1000);
        
        console.log('✅ Simulation Engine initialized successfully');
    }

    setupCanvas() {
        this.canvas = document.getElementById('Canvas');
        if (!this.canvas) {
            console.error('❌ Canvas element not found');
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.resizeCanvas();
        
        // Canvas event listeners
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
        this.canvas.addEventListener('mousedown', (e) => this.handleCanvasMouseDown(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleCanvasMouseUp(e));
        
        // Initial canvas render
        this.renderCanvas();
        
        console.log('✅ Canvas initialized');
    }

    resizeCanvas() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // Set canvas size to fill container
        this.canvas.width = rect.width - 40;
        this.canvas.height = rect.height - 40;
        
        this.renderCanvas();
    }

    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // Window resize
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Performance sidebar toggle
        const performanceToggle = document.querySelector('.performance-toggle');
        if (performanceToggle) {
            performanceToggle.addEventListener('click', () => this.togglePerformanceSidebar());
        }
        
        // Mobile performance toggle
        const mobileToggle = document.querySelector('.mobile-performance-toggle');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => this.togglePerformanceSidebar());
        }
        
        console.log('✅ Event listeners setup complete');
    }

    handleCanvasClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        this.incrementActionCount();
        this.updateProgress(2);
        
        switch (this.state.currentMode) {
            case 'select':
                this.handleSelectMode(x, y);
                break;
            case 'draw':
                this.handleDrawMode(x, y);
                break;
            case 'connect':
                this.handleConnectMode(x, y);
                break;
        }
        
        this.renderCanvas();
        this.updateScore(this.calculateActionScore());
    }

    handleSelectMode(x, y) {
        // Find element at position
        const element = this.findElementAt(x, y);
        
        if (element) {
            this.selectedElement = element;
            this.addHint(`Selected ${element.type} at position (${Math.round(x)}, ${Math.round(y)})`, 'auto');
            this.updateScore(5);
        } else {
            this.selectedElement = null;
            this.addHint(`Clicked empty area at (${Math.round(x)}, ${Math.round(y)})`, 'auto');
        }
    }

    handleDrawMode(x, y) {
        if (!this.state.selectedTool) {
            this.addHint('Select a tool first before drawing!', 'warning');
            return;
        }
        
        // Create new element
        const element = {
            id: `element_${Date.now()}`,
            type: this.state.selectedTool,
            x: x,
            y: y,
            width: 40,
            height: 40,
            color: this.getToolColor(this.state.selectedTool)
        };
        
        this.elements.push(element);
        this.addHint(`Drew ${this.state.selectedTool} at position (${Math.round(x)}, ${Math.round(y)})`, 'auto');
        this.updateScore(10);
    }

    handleConnectMode(x, y) {
        const element = this.findElementAt(x, y);
        
        if (element) {
            if (this.selectedElement && this.selectedElement !== element) {
                // Create connection
                const connection = {
                    id: `connection_${Date.now()}`,
                    from: this.selectedElement,
                    to: element,
                    type: 'basic'
                };
                
                this.connections.push(connection);
                this.addHint(`Connected ${this.selectedElement.type} to ${element.type}`, 'auto');
                this.updateScore(15);
                this.selectedElement = null;
            } else {
                this.selectedElement = element;
                this.addHint(`Selected ${element.type} for connection`, 'auto');
            }
        } else {
            this.selectedElement = null;
            this.addHint('Click on elements to create connections', 'info');
        }
    }

    handleCanvasMouseMove(e) {
        if (this.state.currentMode === 'select' && this.selectedElement) {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Update element position if dragging
            if (e.buttons === 1) { // Left mouse button
                this.selectedElement.x = x - this.selectedElement.width / 2;
                this.selectedElement.y = y - this.selectedElement.height / 2;
                this.renderCanvas();
            }
        }
    }

    handleCanvasMouseDown(e) {
        // Handle mouse down events for dragging
    }

    handleCanvasMouseUp(e) {
        // Handle mouse up events
    }

    handleKeyboard(e) {
        switch (e.key) {
            case 'Escape':
                this.closeAllModals();
                break;
            case '1':
                this.setMode('select');
                break;
            case '2':
                this.setMode('draw');
                break;
            case '3':
                this.setMode('connect');
                break;
            case 'p':
            case 'P':
                this.togglePerformanceSidebar();
                break;
            case 'h':
            case 'H':
                this.showHelp();
                break;
            case 's':
            case 'S':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.saveSimulation();
                }
                break;
        }
    }

    renderCanvas() {
        if (!this.ctx) return;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid background
        this.drawGrid();
        
        // Draw connections first (so they appear behind elements)
        this.drawConnections();
        
        // Draw elements
        this.drawElements();
        
        // Draw selection indicator
        if (this.selectedElement) {
            this.drawSelectionIndicator(this.selectedElement);
        }
    }

    drawGrid() {
        const gridSize = 20;
        this.ctx.strokeStyle = 'rgba(0, 217, 255, 0.1)';
        this.ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x <= this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    drawElements() {
        this.elements.forEach(element => {
            this.ctx.fillStyle = element.color;
            this.ctx.fillRect(element.x, element.y, element.width, element.height);
            
            // Draw element border
            this.ctx.strokeStyle = '#00D9FF';
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(element.x, element.y, element.width, element.height);
            
            // Draw element label
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.font = '12px Orbitron';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(
                element.type, 
                element.x + element.width / 2, 
                element.y + element.height / 2 + 4
            );
        });
    }

    drawConnections() {
        this.connections.forEach(connection => {
            const fromCenter = {
                x: connection.from.x + connection.from.width / 2,
                y: connection.from.y + connection.from.height / 2
            };
            
            const toCenter = {
                x: connection.to.x + connection.to.width / 2,
                y: connection.to.y + connection.to.height / 2
            };
            
            // Draw connection line
            this.ctx.strokeStyle = '#39FF14';
            this.ctx.lineWidth = 3;
            this.ctx.beginPath();
            this.ctx.moveTo(fromCenter.x, fromCenter.y);
            this.ctx.lineTo(toCenter.x, toCenter.y);
            this.ctx.stroke();
            
            // Draw arrow head
            this.drawArrow(fromCenter, toCenter);
        });
    }

    drawArrow(from, to) {
        const angle = Math.atan2(to.y - from.y, to.x - from.x);
        const arrowLength = 15;
        const arrowAngle = 0.5;
        
        this.ctx.strokeStyle = '#39FF14';
        this.ctx.lineWidth = 2;
        
        // Arrow head lines
        this.ctx.beginPath();
        this.ctx.moveTo(to.x, to.y);
        this.ctx.lineTo(
            to.x - arrowLength * Math.cos(angle - arrowAngle),
            to.y - arrowLength * Math.sin(angle - arrowAngle)
        );
        this.ctx.moveTo(to.x, to.y);
        this.ctx.lineTo(
            to.x - arrowLength * Math.cos(angle + arrowAngle),
            to.y - arrowLength * Math.sin(angle + arrowAngle)
        );
        this.ctx.stroke();
    }

    drawSelectionIndicator(element) {
        // Animated selection ring
        const time = Date.now() / 1000;
        const pulse = Math.sin(time * 3) * 0.5 + 0.5;
        
        this.ctx.strokeStyle = `rgba(57, 255, 20, ${0.5 + pulse * 0.5})`;
        this.ctx.lineWidth = 3;
        this.ctx.setLineDash([5, 5]);
        this.ctx.strokeRect(
            element.x - 5,
            element.y - 5,
            element.width + 10,
            element.height + 10
        );
        this.ctx.setLineDash([]);
    }

    findElementAt(x, y) {
        // Find element at given coordinates (reverse order for top-most)
        for (let i = this.elements.length - 1; i >= 0; i--) {
            const element = this.elements[i];
            if (x >= element.x && x <= element.x + element.width &&
                y >= element.y && y <= element.y + element.height) {
                return element;
            }
        }
        return null;
    }

    getToolColor(toolType) {
        const colors = {
            'tool1': '#3B82F6',
            'tool2': '#10B981',
            'tool3': '#F59E0B',
            'tool4': '#EF4444'
        };
        return colors[toolType] || '#6B7280';
    }

    calculateActionScore() {
        const baseScore = 5;
        const accuracyBonus = Math.floor(this.state.accuracy / 10);
        const speedBonus = this.state.actionCount < 50 ? 2 : 0;
        return baseScore + accuracyBonus + speedBonus;
    }

    // State management methods
    setMode(mode) {
        if (this.state.currentMode === mode) return;
        
        this.state.currentMode = mode;
        this.incrementActionCount();
        
        // Update UI
        this.updateModeButtons(mode);
        this.addHint(`Switched to ${mode} mode. ${this.getModeInstructions(mode)}`, 'auto');
        
        // Clear selection when changing modes
        this.selectedElement = null;
        this.renderCanvas();
    }

    setTool(toolId) {
        this.state.selectedTool = toolId;
        this.incrementActionCount();
        
        // Update UI
        this.updateToolSelection(toolId);
        this.addHint(`Selected ${toolId}. Use it with the current ${this.state.currentMode} mode.`, 'auto');
    }

    updateModeButtons(activeMode) {
        document.querySelectorAll('.left-section .action-btn').forEach(btn => {
            btn.classList.remove('mode-active', 'mode-inactive', 'mode-neutral');
            
            const btnText = btn.querySelector('.label').textContent.toLowerCase();
            if (btnText === activeMode) {
                btn.classList.add('mode-active');
            } else {
                btn.classList.add('mode-inactive');
            }
        });
    }

    updateToolSelection(selectedTool) {
        document.querySelectorAll('.device').forEach(device => {
            device.classList.remove('selected-device');
        });
        
        // Find and select the current tool
        const toolElements = document.querySelectorAll('.device');
        toolElements.forEach((device, index) => {
            const toolId = `tool${index + 1}`;
            if (toolId === selectedTool) {
                device.classList.add('selected-device');
            }
        });
    }

    getModeInstructions(mode) {
        const instructions = {
            select: 'Click on elements to select and drag them around.',
            draw: 'Click anywhere to place the selected tool.',
            connect: 'Click on two elements to create a connection between them.'
        };
        return instructions[mode] || '';
    }

    // Performance tracking
    startPerformanceTracking() {
        this.performanceInterval = setInterval(() => {
            this.updatePerformanceMetrics();
        }, 1000);
    }

    updatePerformanceMetrics() {
        const elapsedSeconds = Math.floor((Date.now() - this.state.startTime) / 1000);
        const minutes = Math.floor(elapsedSeconds / 60);
        const seconds = elapsedSeconds % 60;
        
        // Update DOM elements
        this.updateElement('elapsedTime', 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
        this.updateElement('currentScore', this.state.score);
        this.updateElement('actionCount', this.state.actionCount);
        this.updateElement('accuracyPercent', `${this.state.accuracy}%`);
        this.updateElement('hintsUsed', this.state.hintsUsed);
        
        // Update progress ring
        this.updateProgressRing(this.state.progress);
        
        // Update progress status
        this.updateProgressStatus(this.state.progress);
        
        // Check for achievements
        this.checkAchievements();
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    updateProgressRing(progress) {
        const progressRing = document.getElementById('progressRing');
        const progressText = document.getElementById('progressText');
        
        if (progressRing && progressText) {
            const circumference = 2 * Math.PI * 35;
            const offset = circumference - (progress / 100) * circumference;
            progressRing.style.strokeDashoffset = offset;
            progressText.textContent = `${Math.round(progress)}%`;
        }
    }

    updateProgressStatus(progress) {
        const statusElement = document.getElementById('progressStatus');
        if (!statusElement) return;
        
        let status = 'Getting Started';
        if (progress > 75) status = 'Almost Complete!';
        else if (progress > 50) status = 'Making Great Progress';
        else if (progress > 25) status = 'Getting the Hang of It';
        
        statusElement.textContent = status;
    }

    // Hints system
    addHint(text, type = 'info') {
        const hintsContainer = document.getElementById('hintsContainer');
        if (!hintsContainer) return;
        
        const hintItem = document.createElement('div');
        hintItem.className = 'hint-item';
        
        let iconClass = 'fa-info-circle';
        if (type === 'warning') iconClass = 'fa-exclamation-triangle';
        else if (type === 'success') iconClass = 'fa-check-circle';
        else if (type === 'auto') iconClass = 'fa-robot';
        
        hintItem.innerHTML = `
            <i class="fas ${iconClass} hint-icon"></i>
            <div class="hint-text">${text}</div>
        `;
        
        hintsContainer.appendChild(hintItem);
        
        // Keep only last 5 hints
        while (hintsContainer.children.length > 5) {
            hintsContainer.removeChild(hintsContainer.firstChild);
        }
        
        // Scroll to bottom
        hintsContainer.scrollTop = hintsContainer.scrollHeight;
        
        // Count hint usage
        if (type !== 'auto') {
            this.state.hintsUsed++;
        }
        
        // Auto-remove hints after 10 seconds
        setTimeout(() => {
            if (hintItem.parentNode) {
                hintItem.style.opacity = '0.5';
            }
        }, 10000);
    }

    // Achievement system
    checkAchievements() {
        const achievements = [
            {
                id: 'first_click',
                name: 'First Click',
                condition: () => this.state.actionCount >= 1,
                points: 25
            },
            {
                id: 'tool_user',
                name: 'Tool User',
                condition: () => this.state.selectedTool !== null,
                points: 50
            },
            {
                id: 'mode_switcher',
                name: 'Mode Switcher',
                condition: () => this.state.actionCount >= 10,
                points: 75
            },
            {
                id: 'creator',
                name: 'Creator',
                condition: () => this.elements.length >= 3,
                points: 100
            },
            {
                id: 'connector',
                name: 'Connector',
                condition: () => this.connections.length >= 2,
                points: 150
            },
            {
                id: 'perfectionist',
                name: 'Perfectionist',
                condition: () => this.state.accuracy >= 100 && this.state.actionCount >= 20,
                points: 200
            }
        ];
        
        achievements.forEach(achievement => {
            if (!this.state.achievements.includes(achievement.id) && achievement.condition()) {
                this.unlockAchievement(achievement);
            }
        });
    }

    unlockAchievement(achievement) {
        this.state.achievements.push(achievement.id);
        this.updateScore(achievement.points);
        
        // Show achievement notification
        this.showAchievementNotification(achievement);
        
        // Add to hints
        this.addHint(`🏆 Achievement Unlocked: ${achievement.name} (+${achievement.points} pts)`, 'success');
    }

    showAchievementNotification(achievement) {
        // Create achievement notification element
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-icon">🏆</div>
            <div class="achievement-details">
                <div class="achievement-name">${achievement.name}</div>
                <div class="achievement-desc">Achievement Unlocked!</div>
                <div class="achievement-points">+${achievement.points} points</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Hide notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Score and progress management
    updateScore(points) {
        this.state.score += points;
        
        // Create score change animation
        this.showScoreChange(points);
    }

    showScoreChange(points) {
        const scoreElement = document.getElementById('currentScore');
        if (!scoreElement) return;
        
        const changeElement = document.createElement('div');
        changeElement.className = `score-change ${points > 0 ? 'positive' : 'negative'}`;
        changeElement.textContent = `${points > 0 ? '+' : ''}${points}`;
        
        scoreElement.parentNode.style.position = 'relative';
        scoreElement.parentNode.appendChild(changeElement);
        
        // Remove after animation
        setTimeout(() => {
            if (changeElement.parentNode) {
                changeElement.parentNode.removeChild(changeElement);
            }
        }, 2000);
    }

    updateProgress(amount) {
        this.state.progress = Math.min(this.state.progress + amount, 100);
    }

    incrementActionCount() {
        this.state.actionCount++;
        
        // Update accuracy based on performance
        if (this.state.actionCount > 0) {
            const expectedActions = Math.floor(this.state.progress * 0.5);
            this.state.accuracy = Math.max(50, Math.min(100, 
                Math.round(100 - ((this.state.actionCount - expectedActions) * 2))
            ));
        }
    }

    // Modal management
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    }

    closeAllModals() {
        document.querySelectorAll('.simulation-modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    // Performance sidebar
    togglePerformanceSidebar() {
        const sidebar = document.getElementById('performanceSidebar');
        if (sidebar) {
            sidebar.classList.toggle('active');
        }
    }

    showInitialTutorial() {
        // Show scenario selection modal
        this.showModal('scenarioModal');
        this.addHint('Welcome to the interactive simulation! Select a scenario to begin your learning journey.');
    }

    // Scenario management
    selectScenario(difficulty) {
        this.state.difficulty = difficulty;
        this.state.scenario = difficulty;
        this.closeModal('scenarioModal');
        
        // Update hints based on difficulty
        this.setupDifficultyHints(difficulty);
        
        this.addHint(`Starting ${difficulty} scenario. ${this.getDifficultyDescription(difficulty)}`, 'success');
        this.updateProgress(5);
        
        // Auto-show performance sidebar for beginners
        if (difficulty === 'beginner' && window.innerWidth > 768) {
            setTimeout(() => {
                document.getElementById('performanceSidebar').classList.add('active');
            }, 1500);
        }
    }

    setupDifficultyHints(difficulty) {
        // Clear existing hints
        const hintsContainer = document.getElementById('hintsContainer');
        if (hintsContainer) {
            hintsContainer.innerHTML = '';
        }
        
        // Add difficulty-specific initial hints
        switch (difficulty) {
            case 'beginner':
                this.addHint('💡 Beginner Mode: You\'ll get step-by-step guidance and helpful hints!');
                this.addHint('🎯 Try selecting a tool from the center palette first.');
                break;
            case 'intermediate':
                this.addHint('🔧 Intermediate Mode: Some guidance provided with contextual hints.');
                this.addHint('🎯 Explore the different modes and tools available.');
                break;
            case 'advanced':
                this.addHint('🔥 Advanced Mode: Minimal guidance - challenge yourself!');
                this.addHint('🎯 Plan your approach and work independently.');
                break;
        }
    }

    getDifficultyDescription(difficulty) {
        const descriptions = {
            beginner: 'You\'ll receive detailed guidance and frequent helpful hints.',
            intermediate: 'Moderate complexity with contextual hints when needed.',
            advanced: 'Complex challenges with minimal guidance. Good luck!'
        };
        return descriptions[difficulty] || '';
    }

    // Utility functions
    saveSimulation() {
        const saveData = {
            state: this.state,
            elements: this.elements,
            connections: this.connections,
            timestamp: new Date().toISOString()
        };
        
        // In a real implementation, send to server
        localStorage.setItem('simulation_save', JSON.stringify(saveData));
        this.addHint('Simulation progress saved successfully! 💾', 'success');
        this.incrementActionCount();
    }

    loadSimulation() {
        const saveData = localStorage.getItem('simulation_save');
        if (saveData) {
            try {
                const data = JSON.parse(saveData);
                this.state = { ...this.state, ...data.state };
                this.elements = data.elements || [];
                this.connections = data.connections || [];
                
                this.renderCanvas();
                this.addHint('Simulation loaded successfully! 📁', 'success');
            } catch (e) {
                this.addHint('Error loading simulation data.', 'warning');
            }
        } else {
            this.addHint('No saved simulation found.', 'info');
        }
        this.incrementActionCount();
    }

    showSettings() {
        this.showModal('settingsModal');
        this.incrementActionCount();
    }

    showHelp() {
        this.showModal('scenarioModal');
        this.incrementActionCount();
    }

    // API integration methods
    async submitProgress(actionType, actionData = {}) {
        try {
            const response = await fetch('/simulation-template/api/progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: actionType,
                    step: this.getCurrentStep(),
                    score: this.state.score,
                    progress: this.state.progress,
                    data: actionData
                })
            });
            
            const result = await response.json();
            if (result.success) {
                console.log('✅ Progress updated:', result.message);
            }
        } catch (error) {
            console.error('❌ Error submitting progress:', error);
        }
    }

    async getHint(difficulty = null) {
        try {
            const response = await fetch('/simulation-template/api/hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    step: this.getCurrentStep(),
                    mode: this.state.currentMode,
                    difficulty: difficulty || this.state.difficulty
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.addHint(result.hint, 'info');
                this.state.hintsUsed++;
            }
        } catch (error) {
            console.error('❌ Error getting hint:', error);
            this.addHint('Unable to get hint at this time.', 'warning');
        }
    }

    getCurrentStep() {
        // Determine current step based on progress
        if (this.state.progress < 20) return 1;
        if (this.state.progress < 40) return 2;
        if (this.state.progress < 60) return 3;
        if (this.state.progress < 80) return 4;
        return 5;
    }

    // Cleanup
    destroy() {
        if (this.performanceInterval) {
            clearInterval(this.performanceInterval);
        }
        
        // Remove event listeners
        document.removeEventListener('keydown', this.handleKeyboard.bind(this));
        window.removeEventListener('resize', this.resizeCanvas.bind(this));
        
        console.log('🧹 Simulation Engine cleaned up');
    }
}

// Global simulation instance
let simulationEngine = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing simulation engine...');
    simulationEngine = new SimulationEngine();
    
    // Make it globally accessible for debugging
    window.simulationEngine = simulationEngine;
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimulationEngine;
}

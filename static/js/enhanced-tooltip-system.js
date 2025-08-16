// Enhanced Tutorial/Manual Tooltip System for RiddleNet
// Comprehensive tooltip and tutorial guidance system

class EnhancedTooltipSystem {
    constructor() {
        this.tooltips = new Map();
        this.tutorials = new Map();
        this.currentTutorial = null;
        this.tutorialStep = 0;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeEnhancedTooltips();
            this.setupTutorialSystem();
            this.addHelpButtons();
        });
    }

    initializeEnhancedTooltips() {
        // Enhanced tooltips for admin interfaces
        this.addAdvancedTooltips();
        this.setupDynamicTooltips();
        this.setupContextualHelp();
    }

    addAdvancedTooltips() {
        const tooltipConfigs = {
            // Class Management
            '.class-selector': {
                text: 'Select which class to manage. Only one class can be active at a time.',
                type: 'info',
                position: 'bottom'
            },
            '#classSelector': {
                text: 'Choose a class to view and edit its content, assignments, and student data.',
                type: 'info',
                position: 'bottom'
            },
            '.class-code': {
                text: 'Students use this 6-character code to join your class. Share it carefully!',
                type: 'warning',
                position: 'top'
            },
            
            // Module Management
            '.create-btn': {
                text: 'Create new content for your students. Choose from lessons, assignments, or simulations.',
                type: 'success',
                position: 'top'
            },
            '.sidebar-action-btn': {
                text: 'Quick actions for module management. Create, preview, or organize your content.',
                type: 'info',
                position: 'right'
            },
            '.module-card': {
                text: 'Click to edit module content. Drag to reorder. Use the menu for advanced options.',
                type: 'info',
                position: 'top'
            },
            
            // Simulation Builder
            '.component-item': {
                text: 'Drag network devices onto the canvas. Double-click to configure device settings.',
                type: 'info',
                position: 'right'
            },
            '#simulationCanvas': {
                text: 'Build your network topology here. Drop devices and create connections between them.',
                type: 'info',
                position: 'top'
            },
            '.btn-primary[onclick*="preview"]': {
                text: 'Test your simulation as students will see it. Always preview before publishing!',
                type: 'warning',
                position: 'top'
            },
            '.btn-success[onclick*="save"]': {
                text: 'Save your simulation. Only saved simulations are available to students.',
                type: 'success',
                position: 'top'
            },
            
            // Assignment Creation
            '#assignmentTitle': {
                text: 'Give your assignment a clear, descriptive title that tells students what they\'ll be doing.',
                type: 'info',
                position: 'top'
            },
            '#assignmentDueDate': {
                text: 'Set a realistic deadline. Students receive automatic reminders as the due date approaches.',
                type: 'warning',
                position: 'top'
            },
            '#assignmentPoints': {
                text: 'Maximum points students can earn. This affects their overall grade calculation.',
                type: 'info',
                position: 'top'
            },
            '#assignmentPriority': {
                text: 'High priority assignments show prominently on student dashboards and send more notifications.',
                type: 'warning',
                position: 'top'
            },
            '#assignmentCategory': {
                text: 'Category helps organize assignments by subject. Students can filter by category.',
                type: 'info',
                position: 'top'
            },
            '#assignmentPublished': {
                text: 'Only published assignments are visible to students. Keep unchecked to save as draft.',
                type: 'warning',
                position: 'top'
            },
            
            // User Management
            '.user-card': {
                text: 'View student progress, send messages, or manage account settings.',
                type: 'info',
                position: 'top'
            },
            '.btn-danger[onclick*="remove"]': {
                text: 'Permanently remove this student from the class. This action cannot be undone!',
                type: 'error',
                position: 'top'
            },
            
            // Analytics & Reports
            '.chart-container': {
                text: 'Interactive chart showing student performance data. Click elements for detailed breakdowns.',
                type: 'info',
                position: 'top'
            },
            '.export-btn': {
                text: 'Download data as CSV or PDF. Useful for gradebook integration or parent conferences.',
                type: 'info',
                position: 'top'
            },
            
            // Settings & Configuration
            '.form-control[type="date"]': {
                text: 'Set class start and end dates to control when students can access content.',
                type: 'info',
                position: 'top'
            },
            '.form-control[type="number"]': {
                text: 'Set limits for class size, attempts, or time restrictions.',
                type: 'info',
                position: 'top'
            },
            
            // Enhanced Dropdowns (newly implemented)
            '.enhanced-select': {
                text: 'Color-coded dropdown showing categories. Colors help quickly identify content types.',
                type: 'success',
                position: 'top'
            }
        };

        // Apply all tooltip configurations
        Object.entries(tooltipConfigs).forEach(([selector, config]) => {
            this.addTooltip(selector, config.text, config);
        });
    }

    setupDynamicTooltips() {
        // Dynamic tooltips that change based on context
        this.setupConditionalTooltips();
        this.setupProgressTooltips();
        this.setupStatusTooltips();
    }

    setupConditionalTooltips() {
        // Show different tooltips based on element state
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn[disabled]')) {
                this.showTemporaryTooltip(e.target, 'This action is currently disabled. Check requirements or permissions.', 'warning');
            }
        });

        // Update tooltips when form validation changes
        document.addEventListener('input', (e) => {
            if (e.target.matches('.form-control:invalid')) {
                this.updateTooltip(e.target, 'Please enter a valid value for this field.', 'error');
            } else if (e.target.matches('.form-control:valid')) {
                this.updateTooltip(e.target, 'Input is valid ✓', 'success');
            }
        });
    }

    setupProgressTooltips() {
        // Show progress information in tooltips
        const progressElements = document.querySelectorAll('[data-progress]');
        progressElements.forEach(element => {
            const progress = element.getAttribute('data-progress');
            const tooltip = `Progress: ${progress}% complete. ${100 - progress}% remaining.`;
            this.addTooltip(element, tooltip, { type: 'info', position: 'top' });
        });
    }

    setupStatusTooltips() {
        // Add status-specific tooltips
        const statusMappings = {
            'active': { text: 'Currently active and available to students', type: 'success' },
            'draft': { text: 'Saved as draft - not visible to students yet', type: 'warning' },
            'archived': { text: 'Archived content - read-only for students', type: 'info' },
            'expired': { text: 'Past due date - submissions may be restricted', type: 'error' }
        };

        Object.entries(statusMappings).forEach(([status, config]) => {
            this.addTooltip(`[data-status="${status}"]`, config.text, config);
        });
    }

    setupContextualHelp() {
        // Context-aware help system
        this.addContextualHelp('simulation-builder', this.getSimulationBuilderHelp());
        this.addContextualHelp('class-management', this.getClassManagementHelp());
        this.addContextualHelp('assignment-creation', this.getAssignmentCreationHelp());
        this.addContextualHelp('user-management', this.getUserManagementHelp());
    }

    getSimulationBuilderHelp() {
        return {
            title: 'Simulation Builder Guide',
            steps: [
                {
                    title: 'Getting Started',
                    content: 'Welcome to the Simulation Builder! Create interactive network labs for your students.',
                    target: '.simulation-canvas'
                },
                {
                    title: 'Adding Devices',
                    content: 'Drag devices from the component panel onto the canvas. Each device represents network equipment.',
                    target: '.component-panel'
                },
                {
                    title: 'Creating Connections',
                    content: 'Click two devices to create a connection. Connections represent network cables or wireless links.',
                    target: '.connection-tool'
                },
                {
                    title: 'Device Configuration',
                    content: 'Double-click any device to configure its settings, IP addresses, and network protocols.',
                    target: '.canvas-device'
                },
                {
                    title: 'Setting Objectives',
                    content: 'Define what students need to accomplish. Clear objectives help students understand goals.',
                    target: '.objectives-panel'
                },
                {
                    title: 'Testing & Preview',
                    content: 'Always preview your simulation before publishing. Test all interactions and scenarios.',
                    target: '.preview-btn'
                },
                {
                    title: 'Publishing',
                    content: 'Save and publish your simulation to make it available to students in their classes.',
                    target: '.save-btn'
                }
            ]
        };
    }

    getClassManagementHelp() {
        return {
            title: 'Class Management Guide',
            steps: [
                {
                    title: 'Class Overview',
                    content: 'Manage all aspects of your class: students, content, assignments, and progress tracking.',
                    target: '.class-header'
                },
                {
                    title: 'Student Enrollment',
                    content: 'Share your class code with students so they can join. Monitor enrollment in real-time.',
                    target: '.class-code'
                },
                {
                    title: 'Content Organization',
                    content: 'Organize your content into modules. Students progress through modules in sequence.',
                    target: '.module-list'
                },
                {
                    title: 'Assignment Management',
                    content: 'Create assignments, set due dates, and track student submissions and grades.',
                    target: '.assignment-panel'
                },
                {
                    title: 'Progress Monitoring',
                    content: 'Track individual student progress and identify students who need additional support.',
                    target: '.progress-dashboard'
                }
            ]
        };
    }

    getAssignmentCreationHelp() {
        return {
            title: 'Assignment Creation Guide',
            steps: [
                {
                    title: 'Assignment Basics',
                    content: 'Create engaging assignments that align with your learning objectives and curriculum standards.',
                    target: '#assignmentTitle'
                },
                {
                    title: 'Setting Deadlines',
                    content: 'Choose realistic deadlines that give students adequate time while maintaining course pace.',
                    target: '#assignmentDueDate'
                },
                {
                    title: 'Point Values',
                    content: 'Assign point values that reflect the assignment complexity and importance in your grading scheme.',
                    target: '#assignmentPoints'
                },
                {
                    title: 'Categories & Organization',
                    content: 'Use categories to organize assignments by topic, helping students navigate course content.',
                    target: '#assignmentCategory'
                },
                {
                    title: 'Priority Levels',
                    content: 'Set priority levels to highlight important assignments and control notification frequency.',
                    target: '#assignmentPriority'
                },
                {
                    title: 'Publishing Control',
                    content: 'Control when assignments become visible to students. Use draft mode for preparation.',
                    target: '#assignmentPublished'
                }
            ]
        };
    }

    getUserManagementHelp() {
        return {
            title: 'User Management Guide',
            steps: [
                {
                    title: 'Student Overview',
                    content: 'Monitor all your students in one place. View progress, grades, and participation levels.',
                    target: '.user-list'
                },
                {
                    title: 'Individual Progress',
                    content: 'Click any student to view detailed progress reports and identify learning gaps.',
                    target: '.user-card'
                },
                {
                    title: 'Communication Tools',
                    content: 'Send messages, announcements, or feedback directly to students or groups.',
                    target: '.message-btn'
                },
                {
                    title: 'Class Management',
                    content: 'Add or remove students, manage permissions, and handle enrollment changes.',
                    target: '.management-tools'
                }
            ]
        };
    }

    addTooltip(selector, text, options = {}) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.setAttribute('data-tooltip', text);
            if (options.position) element.setAttribute('data-tooltip-position', options.position);
            if (options.type) element.setAttribute('data-tooltip-type', options.type);
            
            // Use existing tooltip manager
            if (window.tooltipManager) {
                window.tooltipManager.createTooltip(element, options);
            }
        });
    }

    updateTooltip(element, newText, type = null) {
        element.setAttribute('data-tooltip', newText);
        if (type) element.setAttribute('data-tooltip-type', type);
        
        if (window.tooltipManager) {
            window.tooltipManager.updateTooltip(element, newText);
        }
    }

    showTemporaryTooltip(element, text, type = 'info', duration = 3000) {
        const originalText = element.getAttribute('data-tooltip');
        const originalType = element.getAttribute('data-tooltip-type');
        
        this.updateTooltip(element, text, type);
        
        setTimeout(() => {
            if (originalText) {
                this.updateTooltip(element, originalText, originalType);
            } else {
                this.removeTooltip(element);
            }
        }, duration);
    }

    removeTooltip(element) {
        if (window.tooltipManager) {
            window.tooltipManager.removeTooltip(element);
        }
    }

    setupTutorialSystem() {
        this.createTutorialModal();
        this.addTutorialTriggers();
    }

    createTutorialModal() {
        if (document.getElementById('enhancedTutorialModal')) return;

        const modalHTML = `
            <div id="enhancedTutorialModal" class="enhanced-tutorial-modal">
                <div class="tutorial-content">
                    <div class="tutorial-header">
                        <h2 id="tutorialTitle">Interactive Tutorial</h2>
                        <button class="tutorial-close" onclick="enhancedTooltipSystem.closeTutorial()">&times;</button>
                    </div>
                    <div class="tutorial-body" id="tutorialBody">
                        <!-- Tutorial content will be loaded here -->
                    </div>
                    <div class="tutorial-footer">
                        <div class="tutorial-progress">
                            <span class="step-counter">Step <span id="currentTutorialStep">1</span> of <span id="totalTutorialSteps">1</span></span>
                            <div class="tutorial-progress-bar">
                                <div class="tutorial-progress-fill" id="tutorialProgressFill"></div>
                            </div>
                        </div>
                        <div class="tutorial-buttons">
                            <button class="btn btn-secondary" id="tutorialPrevBtn" onclick="enhancedTooltipSystem.previousTutorialStep()">Previous</button>
                            <button class="btn btn-primary" id="tutorialNextBtn" onclick="enhancedTooltipSystem.nextTutorialStep()">Next</button>
                            <button class="btn btn-success" id="tutorialFinishBtn" onclick="enhancedTooltipSystem.closeTutorial()" style="display: none;">Finish</button>
                        </div>
                    </div>
                </div>
                <div class="tutorial-overlay" onclick="enhancedTooltipSystem.closeTutorial()"></div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.addTutorialStyles();
    }

    addTutorialStyles() {
        const styles = `
            <style id="enhanced-tutorial-styles">
                .enhanced-tutorial-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 10000;
                    display: none;
                    align-items: center;
                    justify-content: center;
                }
                
                .tutorial-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.7);
                    backdrop-filter: blur(5px);
                }
                
                .tutorial-content {
                    position: relative;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f4c75 100%);
                    border-radius: 12px;
                    max-width: 600px;
                    width: 90%;
                    max-height: 80vh;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3);
                    border: 1px solid #00ffff;
                }
                
                .tutorial-header {
                    padding: 1.5rem;
                    border-bottom: 1px solid #00ffff;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .tutorial-header h2 {
                    color: #00ffff;
                    margin: 0;
                    font-size: 1.5rem;
                }
                
                .tutorial-close {
                    background: none;
                    border: none;
                    color: #00ffff;
                    font-size: 1.5rem;
                    cursor: pointer;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: all 0.3s ease;
                }
                
                .tutorial-close:hover {
                    background: rgba(255, 0, 0, 0.2);
                    transform: scale(1.1);
                }
                
                .tutorial-body {
                    padding: 2rem;
                    color: #ffffff;
                    max-height: 400px;
                    overflow-y: auto;
                }
                
                .tutorial-footer {
                    padding: 1.5rem;
                    border-top: 1px solid #00ffff;
                    background: rgba(0, 0, 0, 0.2);
                }
                
                .tutorial-progress {
                    margin-bottom: 1rem;
                }
                
                .step-counter {
                    color: #00ffff;
                    font-size: 0.9rem;
                    margin-bottom: 0.5rem;
                    display: block;
                }
                
                .tutorial-progress-bar {
                    width: 100%;
                    height: 8px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 4px;
                    overflow: hidden;
                }
                
                .tutorial-progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #00ffff, #00cc99);
                    border-radius: 4px;
                    transition: width 0.3s ease;
                    width: 0%;
                }
                
                .tutorial-buttons {
                    display: flex;
                    gap: 1rem;
                    justify-content: center;
                }
                
                .tutorial-buttons .btn {
                    padding: 0.75rem 1.5rem;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.3s ease;
                }
                
                .tutorial-buttons .btn-secondary {
                    background: rgba(108, 117, 125, 0.8);
                    color: #ffffff;
                }
                
                .tutorial-buttons .btn-primary {
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: #ffffff;
                }
                
                .tutorial-buttons .btn-success {
                    background: linear-gradient(135deg, #28a745, #1e7e34);
                    color: #ffffff;
                }
                
                .tutorial-buttons .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(0, 255, 255, 0.3);
                }
                
                .tutorial-buttons .btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .tutorial-highlight {
                    position: relative;
                    z-index: 9999;
                    box-shadow: 0 0 0 4px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.5) !important;
                    border-radius: 8px;
                    animation: tutorialGlow 2s infinite;
                }
                
                @keyframes tutorialGlow {
                    0%, 100% { box-shadow: 0 0 0 4px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.5); }
                    50% { box-shadow: 0 0 0 8px rgba(0, 255, 255, 0.6), 0 0 30px rgba(0, 255, 255, 0.7); }
                }
                
                @media (max-width: 768px) {
                    .tutorial-content {
                        width: 95%;
                        max-height: 90vh;
                    }
                    
                    .tutorial-buttons {
                        flex-direction: column;
                    }
                }
            </style>
        `;

        if (!document.getElementById('enhanced-tutorial-styles')) {
            document.head.insertAdjacentHTML('beforeend', styles);
        }
    }

    addTutorialTriggers() {
        // Add help buttons to key pages
        this.addHelpButton('.simulation-builder', 'simulation-builder');
        this.addHelpButton('.class-content-manager', 'class-management');
        this.addHelpButton('.assignment-creation', 'assignment-creation');
        this.addHelpButton('.user-management', 'user-management');
    }

    addHelpButton(containerSelector, tutorialType) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const helpButton = document.createElement('button');
        helpButton.className = 'tutorial-help-btn';
        helpButton.innerHTML = '❓ Help';
        helpButton.onclick = () => this.startTutorial(tutorialType);

        helpButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #00ffff, #00cc99);
            color: #1a1a2e;
            border: none;
            border-radius: 50px;
            padding: 12px 20px;
            font-weight: bold;
            cursor: pointer;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0, 255, 255, 0.3);
            transition: all 0.3s ease;
        `;

        helpButton.addEventListener('mouseenter', () => {
            helpButton.style.transform = 'scale(1.1)';
            helpButton.style.boxShadow = '0 6px 20px rgba(0, 255, 255, 0.5)';
        });

        helpButton.addEventListener('mouseleave', () => {
            helpButton.style.transform = 'scale(1)';
            helpButton.style.boxShadow = '0 4px 15px rgba(0, 255, 255, 0.3)';
        });

        document.body.appendChild(helpButton);
    }

    addHelpButtons() {
        // Add floating help button to admin pages
        const adminPaths = [
            '/admin/class-content-selector',
            '/admin/simulation-builder', 
            '/admin/module',
            '/admin/user-management'
        ];

        if (adminPaths.some(path => window.location.pathname.includes(path))) {
            this.addFloatingHelpButton();
        }
    }

    addFloatingHelpButton() {
        const helpButton = document.createElement('div');
        helpButton.className = 'floating-help-btn';
        helpButton.innerHTML = `
            <div class="help-btn-icon">?</div>
            <div class="help-btn-text">Need Help?</div>
        `;

        helpButton.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #00ffff, #00cc99);
            color: #1a1a2e;
            border-radius: 50px;
            padding: 15px 25px;
            cursor: pointer;
            z-index: 1000;
            box-shadow: 0 6px 20px rgba(0, 255, 255, 0.4);
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
            animation: helpButtonPulse 3s infinite;
        `;

        const pulseKeyframes = `
            @keyframes helpButtonPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
        `;

        if (!document.getElementById('help-button-animation')) {
            const style = document.createElement('style');
            style.id = 'help-button-animation';
            style.textContent = pulseKeyframes;
            document.head.appendChild(style);
        }

        helpButton.addEventListener('click', () => {
            this.showHelpMenu();
        });

        document.body.appendChild(helpButton);
    }

    showHelpMenu() {
        const helpMenu = document.createElement('div');
        helpMenu.className = 'help-menu';
        helpMenu.innerHTML = `
            <div class="help-menu-content">
                <h3>How can we help you?</h3>
                <div class="help-options">
                    <button onclick="enhancedTooltipSystem.startContextualTutorial()" class="help-option">
                        🎯 Interactive Tutorial
                        <span>Step-by-step guidance for this page</span>
                    </button>
                    <button onclick="enhancedTooltipSystem.showQuickTips()" class="help-option">
                        💡 Quick Tips
                        <span>Essential tips for getting started</span>
                    </button>
                    <button onclick="enhancedTooltipSystem.showKeyboardShortcuts()" class="help-option">
                        ⌨️ Keyboard Shortcuts
                        <span>Speed up your workflow</span>
                    </button>
                    <button onclick="enhancedTooltipSystem.showVideoGuides()" class="help-option">
                        🎥 Video Guides
                        <span>Watch detailed explanations</span>
                    </button>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="help-close">Close</button>
            </div>
        `;

        helpMenu.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        const menuContentStyle = `
            .help-menu-content {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f4c75 100%);
                border-radius: 12px;
                padding: 2rem;
                max-width: 500px;
                width: 90%;
                border: 1px solid #00ffff;
                box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3);
            }
            
            .help-menu-content h3 {
                color: #00ffff;
                margin-bottom: 1.5rem;
                text-align: center;
            }
            
            .help-options {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin-bottom: 1.5rem;
            }
            
            .help-option {
                background: rgba(0, 255, 255, 0.1);
                border: 1px solid #00ffff;
                border-radius: 8px;
                padding: 1rem;
                color: #ffffff;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: left;
            }
            
            .help-option:hover {
                background: rgba(0, 255, 255, 0.2);
                transform: translateX(5px);
            }
            
            .help-option span {
                display: block;
                font-size: 0.9rem;
                color: #cccccc;
                margin-top: 0.5rem;
            }
            
            .help-close {
                background: #dc3545;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 0.75rem 1.5rem;
                cursor: pointer;
                width: 100%;
            }
        `;

        if (!document.getElementById('help-menu-styles')) {
            const style = document.createElement('style');
            style.id = 'help-menu-styles';
            style.textContent = menuContentStyle;
            document.head.appendChild(style);
        }

        document.body.appendChild(helpMenu);
    }

    startContextualTutorial() {
        // Determine which tutorial to show based on current page
        const path = window.location.pathname;
        
        if (path.includes('simulation-builder')) {
            this.startTutorial('simulation-builder');
        } else if (path.includes('class-content') || path.includes('module')) {
            this.startTutorial('class-management');
        } else if (path.includes('assignment')) {
            this.startTutorial('assignment-creation');
        } else if (path.includes('user') || path.includes('student')) {
            this.startTutorial('user-management');
        } else {
            this.startTutorial('general');
        }
        
        // Close help menu
        document.querySelector('.help-menu')?.remove();
    }

    showQuickTips() {
        const tips = [
            "💡 Use Ctrl+S to quickly save your work",
            "🎯 Preview simulations before publishing to catch issues early",
            "📊 Check the analytics dashboard regularly to monitor student progress",
            "🔄 Use drag-and-drop to reorder modules and assignments",
            "📱 The interface is mobile-friendly for on-the-go management",
            "🎨 Color-coded dropdowns help organize content by category",
            "⚡ Keyboard shortcuts speed up common tasks",
            "📈 Set up automatic progress tracking for better insights"
        ];

        const tipHTML = tips.map(tip => `<li>${tip}</li>`).join('');
        
        this.showInfoModal('Quick Tips', `<ul style="text-align: left; padding-left: 1.5rem;">${tipHTML}</ul>`);
        document.querySelector('.help-menu')?.remove();
    }

    showKeyboardShortcuts() {
        const shortcuts = [
            { key: 'Ctrl + S', action: 'Save current work' },
            { key: 'Ctrl + N', action: 'Create new item' },
            { key: 'Ctrl + E', action: 'Edit selected item' },
            { key: 'Ctrl + D', action: 'Duplicate item' },
            { key: 'Delete', action: 'Delete selected item' },
            { key: 'F2', action: 'Rename item' },
            { key: 'Ctrl + Z', action: 'Undo last action' },
            { key: 'Ctrl + Y', action: 'Redo action' },
            { key: 'F1', action: 'Show help' },
            { key: 'Escape', action: 'Cancel/Close modal' }
        ];

        const shortcutHTML = shortcuts.map(s => 
            `<div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                <kbd style="background: #333; padding: 0.25rem 0.5rem; border-radius: 4px;">${s.key}</kbd>
                <span>${s.action}</span>
            </div>`
        ).join('');

        this.showInfoModal('Keyboard Shortcuts', shortcutHTML);
        document.querySelector('.help-menu')?.remove();
    }

    showVideoGuides() {
        const guides = [
            { title: 'Getting Started with RiddleNet', url: '#', duration: '5:30' },
            { title: 'Creating Your First Simulation', url: '#', duration: '8:45' },
            { title: 'Class Management Best Practices', url: '#', duration: '6:20' },
            { title: 'Student Progress Tracking', url: '#', duration: '4:15' },
            { title: 'Advanced Assignment Features', url: '#', duration: '7:50' }
        ];

        const guideHTML = guides.map(g => 
            `<div style="display: flex; justify-content: space-between; align-items: center; margin: 0.75rem 0; padding: 0.5rem; background: rgba(0,255,255,0.1); border-radius: 6px;">
                <span>🎥 ${g.title}</span>
                <span style="color: #00ffff;">${g.duration}</span>
            </div>`
        ).join('');

        this.showInfoModal('Video Guides', `${guideHTML}<p style="color: #cccccc; font-size: 0.9rem; margin-top: 1rem;">Click any video to open in a new window</p>`);
        document.querySelector('.help-menu')?.remove();
    }

    showInfoModal(title, content) {
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10002; display: flex; align-items: center; justify-content: center;">
                <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f4c75 100%); border-radius: 12px; padding: 2rem; max-width: 600px; width: 90%; border: 1px solid #00ffff; box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3);">
                    <h3 style="color: #00ffff; margin-bottom: 1.5rem;">${title}</h3>
                    <div style="color: #ffffff; margin-bottom: 1.5rem;">${content}</div>
                    <button onclick="this.closest('[style*=\"position: fixed\"]').remove()" style="background: #dc3545; color: white; border: none; border-radius: 6px; padding: 0.75rem 1.5rem; cursor: pointer; width: 100%;">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Tutorial navigation methods
    startTutorial(type) {
        const tutorialData = this.getTutorialData(type);
        if (!tutorialData) return;

        this.currentTutorial = tutorialData;
        this.tutorialStep = 0;
        
        const modal = document.getElementById('enhancedTutorialModal');
        modal.style.display = 'flex';
        
        this.updateTutorialStep();
    }

    getTutorialData(type) {
        const tutorials = {
            'simulation-builder': this.getSimulationBuilderHelp(),
            'class-management': this.getClassManagementHelp(),
            'assignment-creation': this.getAssignmentCreationHelp(),
            'user-management': this.getUserManagementHelp(),
            'general': {
                title: 'RiddleNet Overview',
                steps: [
                    {
                        title: 'Welcome to RiddleNet',
                        content: 'RiddleNet is a comprehensive platform for teaching networking concepts through interactive simulations and labs.',
                        target: 'body'
                    },
                    {
                        title: 'Navigation',
                        content: 'Use the main navigation to access different areas: class management, simulation builder, user management, and analytics.',
                        target: '.admin-nav'
                    },
                    {
                        title: 'Help System',
                        content: 'Look for ? icons throughout the interface for contextual help and tooltips.',
                        target: '.help-icon'
                    }
                ]
            }
        };

        return tutorials[type];
    }

    updateTutorialStep() {
        if (!this.currentTutorial) return;

        const step = this.currentTutorial.steps[this.tutorialStep];
        const totalSteps = this.currentTutorial.steps.length;

        // Update content
        document.getElementById('tutorialTitle').textContent = this.currentTutorial.title;
        document.getElementById('tutorialBody').innerHTML = `
            <h3 style="color: #00ffff; margin-bottom: 1rem;">${step.title}</h3>
            <div>${step.content}</div>
        `;

        // Update progress
        document.getElementById('currentTutorialStep').textContent = this.tutorialStep + 1;
        document.getElementById('totalTutorialSteps').textContent = totalSteps;
        
        const progressPercent = ((this.tutorialStep + 1) / totalSteps) * 100;
        document.getElementById('tutorialProgressFill').style.width = `${progressPercent}%`;

        // Update buttons
        const prevBtn = document.getElementById('tutorialPrevBtn');
        const nextBtn = document.getElementById('tutorialNextBtn');
        const finishBtn = document.getElementById('tutorialFinishBtn');

        prevBtn.disabled = this.tutorialStep === 0;
        
        if (this.tutorialStep === totalSteps - 1) {
            nextBtn.style.display = 'none';
            finishBtn.style.display = 'inline-block';
        } else {
            nextBtn.style.display = 'inline-block';
            finishBtn.style.display = 'none';
        }

        // Highlight target element
        this.highlightElement(step.target);
    }

    nextTutorialStep() {
        if (this.currentTutorial && this.tutorialStep < this.currentTutorial.steps.length - 1) {
            this.tutorialStep++;
            this.updateTutorialStep();
        }
    }

    previousTutorialStep() {
        if (this.tutorialStep > 0) {
            this.tutorialStep--;
            this.updateTutorialStep();
        }
    }

    highlightElement(selector) {
        // Remove previous highlights
        document.querySelectorAll('.tutorial-highlight').forEach(el => {
            el.classList.remove('tutorial-highlight');
        });

        // Add new highlight
        const element = document.querySelector(selector);
        if (element) {
            element.classList.add('tutorial-highlight');
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    closeTutorial() {
        const modal = document.getElementById('enhancedTutorialModal');
        modal.style.display = 'none';
        
        // Remove highlights
        document.querySelectorAll('.tutorial-highlight').forEach(el => {
            el.classList.remove('tutorial-highlight');
        });
        
        this.currentTutorial = null;
        this.tutorialStep = 0;
    }

    addContextualHelp(context, helpData) {
        this.tutorials.set(context, helpData);
    }
}

// Initialize the enhanced tooltip system
const enhancedTooltipSystem = new EnhancedTooltipSystem();

// Make it globally available
window.enhancedTooltipSystem = enhancedTooltipSystem;

// Export for use in other scripts
window.EnhancedTooltipSystem = EnhancedTooltipSystem;

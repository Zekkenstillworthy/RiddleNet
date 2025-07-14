/**
 * Crimping Simulation Tutorial System
 * Comprehensive tutorial for network cable crimping
 */

// Crimping Tutorial Configuration
const crimpingTutorialSteps = [
    {
        title: "Welcome to Cable Crimping",
        content: `
            <div class="tutorial-welcome">
                <div class="tutorial-icon">🔧</div>
                <p>Welcome to the Network Cable Crimping Simulation! This interactive tutorial will teach you how to create professional Ethernet cables.</p>
                <div class="tutorial-objectives">
                    <h4>What you'll learn:</h4>
                    <ul>
                        <li>Cable wire color codes (T568A & T568B)</li>
                        <li>Proper wire arrangement techniques</li>
                        <li>Crimping tool usage</li>
                        <li>Quality testing procedures</li>
                    </ul>
                </div>
            </div>
        `,
        target: ".container",
        action: "highlight_container"
    },
    {
        title: "Understanding Wire Color Codes",
        content: `
            <div class="tutorial-step">
                <p>Network cables use specific color patterns called <strong>T568A</strong> and <strong>T568B</strong> standards.</p>
                <div class="color-guide">
                    <div class="standard">
                        <h5>T568B Standard (Most Common):</h5>
                        <div class="wire-pattern">
                            <span class="wire-color orange-white">1. Orange/White</span>
                            <span class="wire-color orange">2. Orange</span>
                            <span class="wire-color green-white">3. Green/White</span>
                            <span class="wire-color blue">4. Blue</span>
                            <span class="wire-color blue-white">5. Blue/White</span>
                            <span class="wire-color green">6. Green</span>
                            <span class="wire-color brown-white">7. Brown/White</span>
                            <span class="wire-color brown">8. Brown</span>
                        </div>
                    </div>
                </div>
                <p><strong>Tip:</strong> Consistency is key! Use the same standard on both ends of your cable.</p>
            </div>
        `,
        target: ".color-options",
        action: "highlight_colors"
    },
    {
        title: "Selecting Your Wire Pattern",
        content: `
            <div class="tutorial-step">
                <p>Choose a color pattern from the available options. Each pattern represents a different wiring standard:</p>
                <ul>
                    <li><strong>T568B:</strong> Most common in North America</li>
                    <li><strong>T568A:</strong> Common in government and residential installations</li>
                    <li><strong>Crossover:</strong> Used for direct device-to-device connections</li>
                </ul>
                <p>Click on a pattern to select it and see the wire arrangement.</p>
            </div>
        `,
        target: ".color-pattern",
        action: "pulse_patterns"
    },
    {
        title: "Wire Preparation Area",
        content: `
            <div class="tutorial-step">
                <p>This is your work area where you'll arrange the wires according to your chosen pattern.</p>
                <div class="preparation-tips">
                    <h5>Best Practices:</h5>
                    <ul>
                        <li>Strip about 1/2 inch of outer cable jacket</li>
                        <li>Untwist wire pairs minimally</li>
                        <li>Keep wires straight and parallel</li>
                        <li>Trim wires to equal length</li>
                    </ul>
                </div>
            </div>
        `,
        target: ".wire-slots",
        action: "highlight_slots"
    },
    {
        title: "Arranging the Wires",
        content: `
            <div class="tutorial-step">
                <p>Drag each wire from the available wires section into the correct slot based on your selected pattern.</p>
                <div class="arrangement-guide">
                    <h5>Arrangement Tips:</h5>
                    <ul>
                        <li>Follow the pattern order from left to right</li>
                        <li>Double-check each wire position</li>
                        <li>Look for the visual pattern match indicator</li>
                        <li>Take your time - accuracy is more important than speed</li>
                    </ul>
                </div>
                <p><em>Try dragging a wire now to see how it works!</em></p>
            </div>
        `,
        target: ".available-wires",
        action: "animate_drag"
    },
    {
        title: "Using the Crimping Tool",
        content: `
            <div class="tutorial-step">
                <p>Once all wires are properly arranged, use the crimping tool to secure the connector.</p>
                <div class="crimping-guide">
                    <h5>Crimping Process:</h5>
                    <ol>
                        <li>Insert the connector into the crimping tool</li>
                        <li>Ensure all wires are fully inserted</li>
                        <li>Apply firm, even pressure</li>
                        <li>Release and inspect the connection</li>
                    </ol>
                </div>
                <p><strong>Note:</strong> A proper crimp should be secure but not over-compressed.</p>
            </div>
        `,
        target: ".crimp-tool",
        action: "highlight_tool"
    },
    {
        title: "Quality Testing",
        content: `
            <div class="tutorial-step">
                <p>After crimping, test your cable to ensure all connections are working properly.</p>
                <div class="testing-info">
                    <h5>What the tester checks:</h5>
                    <ul>
                        <li>Continuity on all 8 wires</li>
                        <li>Correct wire mapping</li>
                        <li>No short circuits</li>
                        <li>Proper signal transmission</li>
                    </ul>
                </div>
                <p>A green light indicates a successful cable, while red indicates errors that need fixing.</p>
            </div>
        `,
        target: ".test-section",
        action: "highlight_tester"
    },
    {
        title: "Reading Your Results",
        content: `
            <div class="tutorial-step">
                <p>The simulation provides detailed feedback on your crimping performance:</p>
                <div class="results-guide">
                    <h5>Performance Metrics:</h5>
                    <ul>
                        <li><strong>Accuracy:</strong> Percentage of correct wire placements</li>
                        <li><strong>Speed:</strong> Time taken to complete the crimp</li>
                        <li><strong>Pattern Match:</strong> Conformance to standard</li>
                        <li><strong>Quality Score:</strong> Overall cable reliability</li>
                    </ul>
                </div>
                <p>Aim for 100% accuracy and try to improve your speed with practice!</p>
            </div>
        `,
        target: ".score-display",
        action: "highlight_scores"
    },
    {
        title: "Ready to Start Crimping!",
        content: `
            <div class="tutorial-complete">
                <div class="tutorial-icon">🎯</div>
                <p>Congratulations! You're now ready to start crimping network cables like a professional.</p>
                <div class="final-tips">
                    <h5>Remember:</h5>
                    <ul>
                        <li>Practice makes perfect</li>
                        <li>Accuracy over speed initially</li>
                        <li>Double-check your pattern before crimping</li>
                        <li>Learn from mistakes and keep improving</li>
                    </ul>
                </div>
                <p><strong>Good luck with your first crimp!</strong> 🚀</p>
            </div>
        `,
        target: ".container",
        action: "celebrate"
    }
];

// Tutorial system for other simulations
const simulationTutorials = {
    networking_components: [
        {
            title: "Network Components Overview",
            content: `
                <p>Learn to build network topologies using various network devices and understand their functions.</p>
                <ul>
                    <li>End devices: Computers, laptops, servers, printers</li>
                    <li>Network devices: Switches, routers, hubs, access points</li>
                    <li>Connection types and cable management</li>
                </ul>
            `,
            target: ".device-palette",
            action: "highlight"
        },
        {
            title: "Device Palette",
            content: `
                <p>Drag devices from this palette onto the canvas to build your network.</p>
                <p>Each device type serves a specific purpose in network communication.</p>
            `,
            target: ".device-palette",
            action: "pulse"
        },
        {
            title: "Building Your Network",
            content: `
                <p>Click and drag devices onto the canvas, then use connection mode to link them together.</p>
                <p>Try connecting computers to a switch, then the switch to a router!</p>
            `,
            target: ".canvas",
            action: "highlight"
        }
    ],
    
    networking_protocols: [
        {
            title: "Application Protocols",
            content: `
                <p>Explore how different application layer protocols work in network communication.</p>
                <ul>
                    <li>HTTP/HTTPS for web browsing</li>
                    <li>FTP for file transfers</li>
                    <li>SMTP for email</li>
                    <li>DNS for name resolution</li>
                </ul>
            `,
            target: ".protocol-selector",
            action: "highlight"
        },
        {
            title: "Protocol Selection",
            content: `
                <p>Choose a protocol to simulate. Each protocol has different characteristics and use cases.</p>
                <p>Watch how data flows between client and server for each protocol type.</p>
            `,
            target: ".protocol-option",
            action: "pulse"
        }
    ],
    
    osi_model: [
        {
            title: "OSI Model Layers",
            content: `
                <p>Understand how data travels through the 7 layers of the OSI model.</p>
                <p>Watch encapsulation as data moves down the sender stack and decapsulation as it moves up the receiver stack.</p>
            `,
            target: ".osi-stack",
            action: "highlight"
        },
        {
            title: "Data Encapsulation",
            content: `
                <p>See how each layer adds its own header/trailer to the data.</p>
                <p>This process ensures reliable, secure, and properly formatted data transmission.</p>
            `,
            target: ".sender-stack",
            action: "animate"
        }
    ],
    
    ethernet_frames: [
        {
            title: "Ethernet Communication",
            content: `
                <p>Learn about Ethernet frame structure and collision domains.</p>
                <p>Compare hub vs switch behavior in network communication.</p>
            `,
            target: ".topology-selector",
            action: "highlight"
        },
        {
            title: "Collision Detection",
            content: `
                <p>In hub-based networks, collisions can occur when multiple devices transmit simultaneously.</p>
                <p>Switches eliminate collision domains by providing dedicated bandwidth to each port.</p>
            `,
            target: ".hub-container",
            action: "pulse"
        }
    ]
};

// Enhanced tutorial functions
function initializeEnhancedTutorial(simulationType = 'crimping') {
    // Load the enhanced modal CSS and JS if not already loaded
    if (!document.querySelector('#enhanced-modal-css')) {
        const cssLink = document.createElement('link');
        cssLink.id = 'enhanced-modal-css';
        cssLink.rel = 'stylesheet';
        cssLink.href = '/static/css/enhanced-modal.css';
        document.head.appendChild(cssLink);
    }
    
    if (!document.querySelector('#enhanced-modal-js')) {
        const jsScript = document.createElement('script');
        jsScript.id = 'enhanced-modal-js';
        jsScript.src = '/static/js/enhanced-modal.js';
        document.head.appendChild(jsScript);
    }
    
    // Create tutorial modal if it doesn't exist
    createTutorialModal();
    
    // Set up tutorial based on simulation type
    const steps = simulationType === 'crimping' ? crimpingTutorialSteps : simulationTutorials[simulationType] || [];
    
    return steps;
}

function createTutorialModal() {
    if (document.getElementById('tutorialModal')) return;
    
    const modalHTML = `
        <div id="tutorialModal" class="modal tutorial-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Interactive Tutorial</h2>
                    <span class="close" onclick="closeTutorial()">&times;</span>
                </div>
                <div class="modal-body" id="tutorialStep">
                    <!-- Tutorial content will be loaded here -->
                </div>
                <div class="modal-footer">
                    <div class="tutorial-progress">
                        <span class="step-counter">Step <span id="currentStepNum">1</span> of <span id="totalSteps">1</span></span>
                        <div class="progress-bar">
                            <div class="progress-fill" id="tutorialProgress"></div>
                        </div>
                    </div>
                    <div class="tutorial-buttons">
                        <button class="btn btn-secondary" id="prevStep" onclick="previousTutorialStep()">Previous</button>
                        <button class="btn btn-primary" id="nextStep" onclick="nextTutorialStep()">Next</button>
                        <button class="btn btn-success" id="finishTutorial" onclick="closeTutorial()" style="display: none;">Finish</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Add tutorial-specific styles
    const tutorialStyles = `
        <style id="tutorial-styles">
            .tutorial-highlight {
                position: relative;
                z-index: 9999;
                box-shadow: 0 0 0 4px rgba(0, 217, 255, 0.8), 0 0 20px rgba(0, 217, 255, 0.5) !important;
                border-radius: 8px;
                animation: tutorialPulse 2s infinite;
            }
            
            @keyframes tutorialPulse {
                0%, 100% { box-shadow: 0 0 0 4px rgba(0, 217, 255, 0.8), 0 0 20px rgba(0, 217, 255, 0.5); }
                50% { box-shadow: 0 0 0 8px rgba(0, 217, 255, 0.6), 0 0 30px rgba(0, 217, 255, 0.7); }
            }
            
            .tutorial-welcome, .tutorial-step, .tutorial-complete {
                text-align: left;
            }
            
            .tutorial-icon {
                font-size: 3rem;
                text-align: center;
                margin-bottom: 1rem;
            }
            
            .tutorial-objectives, .preparation-tips, .arrangement-guide, 
            .crimping-guide, .testing-info, .results-guide, .final-tips {
                background: rgba(0, 217, 255, 0.1);
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                border-left: 4px solid #00D9FF;
            }
            
            .color-guide .standard {
                margin: 1rem 0;
            }
            
            .wire-pattern {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 0.5rem;
                margin: 0.5rem 0;
            }
            
            .wire-color {
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
                text-align: center;
                font-weight: bold;
            }
            
            .wire-color.orange-white { background: linear-gradient(135deg, #ff8c00, #fff); color: #000; }
            .wire-color.orange { background: #ff8c00; color: #fff; }
            .wire-color.green-white { background: linear-gradient(135deg, #32cd32, #fff); color: #000; }
            .wire-color.blue { background: #0066cc; color: #fff; }
            .wire-color.blue-white { background: linear-gradient(135deg, #0066cc, #fff); color: #000; }
            .wire-color.green { background: #32cd32; color: #fff; }
            .wire-color.brown-white { background: linear-gradient(135deg, #8b4513, #fff); color: #000; }
            .wire-color.brown { background: #8b4513; color: #fff; }
            
            .tutorial-progress {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                margin-bottom: 1rem;
            }
            
            .step-counter {
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.8);
                text-align: center;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #00D9FF, #39FF14);
                border-radius: 4px;
                transition: width 0.3s ease;
                width: 0%;
            }
            
            .tutorial-buttons {
                display: flex;
                gap: 1rem;
                justify-content: center;
            }
            
            @media (max-width: 768px) {
                .wire-pattern {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .tutorial-buttons {
                    flex-direction: column;
                }
            }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', tutorialStyles);
}

// Global tutorial state
let tutorialActive = false;
let currentTutorialStep = 0;
let tutorialSteps = [];

// Enhanced showTutorial function
function showTutorial(simulationType = 'crimping') {
    if (tutorialActive) {
        closeTutorial();
        return;
    }
    
    // Initialize tutorial for the specific simulation type
    tutorialSteps = initializeEnhancedTutorial(simulationType);
    
    if (tutorialSteps.length === 0) {
        console.warn(`No tutorial steps found for simulation type: ${simulationType}`);
        return;
    }
    
    tutorialActive = true;
    currentTutorialStep = 0;
    
    // Show modal
    const modal = document.getElementById('tutorialModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
        updateTutorialStep();
        
        // Pause any running timers/animations
        pauseSimulationForTutorial();
    }
}

function updateTutorialStep() {
    if (currentTutorialStep >= tutorialSteps.length) return;
    
    const step = tutorialSteps[currentTutorialStep];
    const tutorialStepElement = document.getElementById('tutorialStep');
    const currentStepNum = document.getElementById('currentStepNum');
    const totalSteps = document.getElementById('totalSteps');
    const progressFill = document.getElementById('tutorialProgress');
    const prevButton = document.getElementById('prevStep');
    const nextButton = document.getElementById('nextStep');
    const finishButton = document.getElementById('finishTutorial');
    
    // Clear previous highlights
    clearTutorialHighlights();
    
    // Update progress
    const progressPercentage = ((currentTutorialStep + 1) / tutorialSteps.length) * 100;
    if (progressFill) {
        progressFill.style.width = `${progressPercentage}%`;
    }
    
    if (currentStepNum) currentStepNum.textContent = currentTutorialStep + 1;
    if (totalSteps) totalSteps.textContent = tutorialSteps.length;
    
    // Update content
    if (tutorialStepElement) {
        tutorialStepElement.innerHTML = `
            <h3 style="color: #00D9FF; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
                <span style="background: linear-gradient(135deg, #00D9FF, #8B5CF6); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.9em;">
                    ${currentTutorialStep + 1}
                </span>
                ${step.title}
            </h3>
            <div>${step.content}</div>
        `;
    }
    
    // Update navigation buttons
    if (prevButton) {
        prevButton.disabled = currentTutorialStep === 0;
        prevButton.style.opacity = currentTutorialStep === 0 ? '0.5' : '1';
    }
    
    if (nextButton && finishButton) {
        if (currentTutorialStep === tutorialSteps.length - 1) {
            nextButton.style.display = 'none';
            finishButton.style.display = 'inline-block';
        } else {
            nextButton.style.display = 'inline-block';
            finishButton.style.display = 'none';
        }
    }
    
    // Apply highlighting and actions
    if (step.target) {
        highlightTutorialElement(step.target);
    }
    
    if (step.action) {
        executeTutorialAction(step.action, step.target);
    }
}

function nextTutorialStep() {
    if (currentTutorialStep < tutorialSteps.length - 1) {
        currentTutorialStep++;
        updateTutorialStep();
    }
}

function previousTutorialStep() {
    if (currentTutorialStep > 0) {
        currentTutorialStep--;
        updateTutorialStep();
    }
}

function closeTutorial() {
    tutorialActive = false;
    
    const modal = document.getElementById('tutorialModal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
    
    clearTutorialHighlights();
    resumeSimulationAfterTutorial();
}

function clearTutorialHighlights() {
    document.querySelectorAll('.tutorial-highlight').forEach(element => {
        element.classList.remove('tutorial-highlight');
    });
}

function highlightTutorialElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.classList.add('tutorial-highlight');
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function executeTutorialAction(action, target) {
    const element = document.querySelector(target);
    if (!element) return;
    
    switch (action) {
        case 'pulse':
        case 'pulse_patterns':
        case 'pulse_container':
            element.style.animation = 'tutorialPulse 1.5s ease-in-out 3';
            break;
            
        case 'highlight':
        case 'highlight_container':
        case 'highlight_colors':
        case 'highlight_slots':
        case 'highlight_tool':
        case 'highlight_tester':
        case 'highlight_scores':
            // Already handled by highlightTutorialElement
            break;
            
        case 'animate_drag':
            // Simulate drag animation for wire placement
            const wires = element.querySelectorAll('.wire');
            wires.forEach((wire, index) => {
                setTimeout(() => {
                    wire.style.transform = 'translateX(10px)';
                    setTimeout(() => {
                        wire.style.transform = 'translateX(0)';
                    }, 200);
                }, index * 100);
            });
            break;
            
        case 'celebrate':
            // Add celebration animation
            element.style.animation = 'celebrate 2s ease-in-out';
            break;
            
        default:
            console.log(`Tutorial action '${action}' not implemented`);
    }
}

function pauseSimulationForTutorial() {
    // Pause any running timers, animations, or game loops
    if (typeof gameStats !== 'undefined' && gameStats.timerInterval) {
        clearInterval(gameStats.timerInterval);
    }
}

function resumeSimulationAfterTutorial() {
    // Resume any paused elements
    if (typeof startTimer === 'function') {
        // This would be implemented in the specific simulation
    }
}

// Make functions globally available
window.showTutorial = showTutorial;
window.closeTutorial = closeTutorial;
window.nextTutorialStep = nextTutorialStep;
window.previousTutorialStep = previousTutorialStep;

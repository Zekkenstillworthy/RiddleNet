/* filepath: c:\Users\gilbe\Documents\Flask_Main_Official_2 - Copy\static\js\user\troubleshooting.js */
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const scenarioSelection = document.getElementById('scenario-selection');
    const activeScenario = document.getElementById('active-scenario');
    const resultScreen = document.getElementById('result-screen');
    const scenarioCards = document.querySelectorAll('.scenario-card');
    
    // Timer elements
    const timeDisplay = document.getElementById('time-display');
    let timer;
    let seconds = 0;
    
    // Canvas elements
    const topologyCanvas = document.getElementById('topology-canvas');
    const ctx = topologyCanvas.getContext('2d');
    
    // Current scenario data
    let currentScenario = null;
    let userSolution = {
        devices: [],
        connections: []
    };
    
    // Initialize the page
    initPage();
    
    function initPage() {
        // Set up event listeners for scenario cards
        scenarioCards.forEach(card => {
            card.querySelector('.start-scenario-btn').addEventListener('click', function() {
                const scenarioId = card.dataset.id;
                loadScenario(scenarioId);
            });
        });
        
        // Set up event listeners for action buttons
        document.getElementById('hint-btn').addEventListener('click', showHint);
        document.getElementById('check-solution-btn').addEventListener('click', checkSolution);
        document.getElementById('reset-topology-btn').addEventListener('click', resetTopology);
        document.getElementById('exit-scenario-btn').addEventListener('click', exitScenario);
        document.getElementById('try-again-btn').addEventListener('click', retryScenario);
        document.getElementById('back-to-scenarios-btn').addEventListener('click', backToScenarios);
        
        // Initialize canvas size
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
    }
    
    function resizeCanvas() {
        const container = document.getElementById('topology-canvas-container');
        topologyCanvas.width = container.offsetWidth;
        topologyCanvas.height = container.offsetHeight;
        
        // Redraw if we have a scenario loaded
        if (currentScenario) {
            renderTopology();
        }
    }
    
    function loadScenario(scenarioId) {
        // Fetch scenario data from the server
        fetch(`/api/troubleshooting/${scenarioId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load scenario');
                }
                return response.json();
            })
            .then(data => {
                currentScenario = data;
                startScenario();
            })
            .catch(error => {
                console.error('Error loading scenario:', error);
                alert('Failed to load the scenario. Please try again.');
            });
    }
    
    function startScenario() {
        // Hide scenario selection and show active scenario
        scenarioSelection.classList.add('hidden');
        activeScenario.classList.remove('hidden');
        resultScreen.classList.add('hidden');
        
        // Set scenario title and description
        document.getElementById('scenario-title').textContent = currentScenario.title;
        document.getElementById('scenario-description-text').innerHTML = marked.parse(currentScenario.scenario);
        
        // Initialize timer
        startTimer();
        
        // Initialize topology
        initTopology();
        
        // Hide hints panel initially
        document.getElementById('hints-container').innerHTML = '';
        document.querySelector('.hints-panel').classList.add('hidden');
    }
    
    function startTimer() {
        seconds = 0;
        updateTimerDisplay();
        
        // Clear any existing timer
        if (timer) {
            clearInterval(timer);
        }
        
        // Start a new timer
        timer = setInterval(() => {
            seconds++;
            updateTimerDisplay();
        }, 1000);
    }
    
    function updateTimerDisplay() {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        timeDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    function stopTimer() {
        clearInterval(timer);
        timer = null;
    }
    
    function initTopology() {
        // Initialize topology palette
        const devicePalette = document.getElementById('device-palette');
        const connectionPalette = document.getElementById('connection-palette');
        
        // Clear existing palettes
        devicePalette.innerHTML = '';
        connectionPalette.innerHTML = '';
        
        // Populate device palette based on allowed devices
        const allowedDevices = currentScenario.topology_config?.allowedDevices || ['router', 'switch', 'pc', 'server'];
        allowedDevices.forEach(deviceType => {
            const deviceItem = document.createElement('div');
            deviceItem.className = 'palette-item';
            deviceItem.dataset.type = deviceType;
            
            // Create an image element for the device icon
            const icon = document.createElement('img');
            icon.src = `/static/img/network/${deviceType}.png`;
            icon.alt = deviceType;
            
            deviceItem.appendChild(icon);
            devicePalette.appendChild(deviceItem);
            
            // Add event listener
            deviceItem.addEventListener('click', () => selectDeviceType(deviceType));
        });
        
        // Populate connection palette
        const connectionTypes = ['ethernet', 'fiber', 'serial'];
        connectionTypes.forEach(connType => {
            const connItem = document.createElement('div');
            connItem.className = 'palette-item';
            connItem.dataset.type = connType;
            
            // Create an image element for the connection icon
            const icon = document.createElement('img');
            icon.src = `/static/img/network/${connType}-cable.png`;
            icon.alt = connType;
            
            connItem.appendChild(icon);
            connectionPalette.appendChild(connItem);
            
            // Add event listener
            connItem.addEventListener('click', () => selectConnectionType(connType));
        });
        
        // Initialize user solution with the initial topology if provided
        if (currentScenario.initial_topology) {
            userSolution = JSON.parse(JSON.stringify(currentScenario.initial_topology));
        } else {
            userSolution = {
                devices: [],
                connections: []
            };
        }
        
        // Render initial topology
        renderTopology();
    }
    
    function renderTopology() {
        // Clear canvas
        ctx.clearRect(0, 0, topologyCanvas.width, topologyCanvas.height);
        
        // Draw background grid
        drawGrid();
        
        // Draw connections first (so they appear behind devices)
        userSolution.connections?.forEach(conn => {
            drawConnection(conn);
        });
        
        // Draw devices
        userSolution.devices?.forEach(device => {
            drawDevice(device);
        });
    }
    
    function drawGrid() {
        const gridSize = 20;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        
        // Draw vertical grid lines
        for (let x = 0; x < topologyCanvas.width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, topologyCanvas.height);
            ctx.stroke();
        }
        
        // Draw horizontal grid lines
        for (let y = 0; y < topologyCanvas.height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(topologyCanvas.width, y);
            ctx.stroke();
        }
    }
    
    function drawDevice(device) {
        // This is a simple placeholder implementation
        // In a real implementation, you would use images and more sophisticated rendering
        const size = 40;
        ctx.fillStyle = getDeviceColor(device.type);
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        
        // Draw device shape
        ctx.beginPath();
        ctx.fillRect(device.x - size/2, device.y - size/2, size, size);
        ctx.strokeRect(device.x - size/2, device.y - size/2, size, size);
        
        // Draw device label
        ctx.fillStyle = '#fff';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(device.label, device.x, device.y + size/2 + 15);
    }
    
    function getDeviceColor(type) {
        switch (type.toLowerCase()) {
            case 'router':
                return '#e74c3c';
            case 'switch':
                return '#3498db';
            case 'pc':
                return '#2ecc71';
            case 'server':
                return '#9b59b6';
            default:
                return '#f39c12';
        }
    }
    
    function drawConnection(connection) {
        // Find the source and target devices
        const source = userSolution.devices.find(d => d.id === connection.source);
        const target = userSolution.devices.find(d => d.id === connection.target);
        
        if (!source || !target) return;
        
        // Draw a line between the devices
        ctx.strokeStyle = getConnectionColor(connection.type);
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();
        
        // Draw a small circle at midpoint to indicate connection type
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        ctx.fillStyle = getConnectionColor(connection.type);
        ctx.beginPath();
        ctx.arc(midX, midY, 4, 0, Math.PI * 2);
        ctx.fill();
    }
    
    function getConnectionColor(type) {
        switch (type) {
            case 'ethernet':
                return '#3498db';
            case 'fiber':
                return '#00C3B5';
            case 'serial':
                return '#e67e22';
            default:
                return '#95a5a6';
        }
    }
    
    function selectDeviceType(deviceType) {
        console.log(`Selected device type: ${deviceType}`);
        // Implement device selection logic
        // This would be used when adding new devices to the topology
    }
    
    function selectConnectionType(connectionType) {
        console.log(`Selected connection type: ${connectionType}`);
        // Implement connection selection logic
        // This would be used when adding new connections between devices
    }
    
    function showHint() {
        const hintsPanel = document.querySelector('.hints-panel');
        const hintsContainer = document.getElementById('hints-container');
        
        // Toggle hints panel visibility
        if (hintsPanel.classList.contains('hidden')) {
            // Show the panel if it's hidden
            hintsPanel.classList.remove('hidden');
            
            // Check if hints are already loaded
            if (hintsContainer.children.length === 0 && currentScenario.hints && currentScenario.hints.length > 0) {
                // Create a list for hints
                const hintsList = document.createElement('ol');
                
                // Add each hint as a list item
                currentScenario.hints.forEach((hint, index) => {
                    const hintItem = document.createElement('li');
                    hintItem.textContent = hint;
                    hintsList.appendChild(hintItem);
                });
                
                hintsContainer.appendChild(hintsList);
            }
        } else {
            // Hide the panel if it's visible
            hintsPanel.classList.add('hidden');
        }
    }
    
    function checkSolution() {
        // Stop the timer
        stopTimer();
        
        // Prepare data for submission
        const submissionData = {
            scenario_id: currentScenario.id,
            time_taken: seconds,
            user_solution: userSolution
        };
        
        // Submit the solution to the server
        fetch('/api/troubleshooting/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(submissionData),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to submit solution');
            }
            return response.json();
        })
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            console.error('Error submitting solution:', error);
            alert('Failed to submit your solution. Please try again.');
            
            // Restart the timer in case of error
            startTimer();
        });
    }
    
    function displayResults(results) {
        // Hide active scenario and show result screen
        activeScenario.classList.add('hidden');
        resultScreen.classList.remove('hidden');
        
        // Update result title based on match percentage
        const resultTitle = document.getElementById('result-title');
        const matchPercentage = results.topology_match_percentage;
        
        if (matchPercentage >= 90) {
            resultTitle.textContent = 'Excellent Job!';
            resultTitle.style.color = '#2ecc71';
        } else if (matchPercentage >= 70) {
            resultTitle.textContent = 'Good Work!';
            resultTitle.style.color = '#00C3B5';
        } else if (matchPercentage >= 50) {
            resultTitle.textContent = 'Almost There!';
            resultTitle.style.color = '#f39c12';
        } else {
            resultTitle.textContent = 'Keep Trying!';
            resultTitle.style.color = '#e74c3c';
        }
        
        // Update score displays
        document.getElementById('final-score').textContent = results.score;
        document.getElementById('base-score-value').textContent = results.base_score;
        document.getElementById('time-bonus-value').textContent = results.time_bonus;
        document.getElementById('match-score-value').textContent = results.match_score;
        
        // Update feedback text
        document.getElementById('feedback-text').innerHTML = results.feedback || 'No specific feedback available.';
        
        // Display solution comparison
        // In a real implementation, you would render both solutions using similar methods to renderTopology
        const yourSolutionDisplay = document.getElementById('your-solution-display');
        const expectedSolutionDisplay = document.getElementById('expected-solution-display');
        
        yourSolutionDisplay.textContent = JSON.stringify(userSolution, null, 2);
        expectedSolutionDisplay.textContent = JSON.stringify(currentScenario.expected_topology, null, 2);
    }
    
    function resetTopology() {
        // Reset to the initial topology
        if (currentScenario.initial_topology) {
            userSolution = JSON.parse(JSON.stringify(currentScenario.initial_topology));
        } else {
            userSolution = {
                devices: [],
                connections: []
            };
        }
        
        // Redraw the topology
        renderTopology();
    }
    
    function exitScenario() {
        // Stop the timer
        stopTimer();
        
        // Confirm exit if the user has started working on the topology
        if (confirm('Are you sure you want to exit? Your progress will be lost.')) {
            backToScenarios();
        } else {
            // Restart the timer
            startTimer();
        }
    }
    
    function retryScenario() {
        // Restart the current scenario
        startScenario();
    }
    
    function backToScenarios() {
        // Reset state
        currentScenario = null;
        userSolution = {
            devices: [],
            connections: []
        };
        stopTimer();
        
        // Show scenario selection screen
        resultScreen.classList.add('hidden');
        activeScenario.classList.add('hidden');
        scenarioSelection.classList.remove('hidden');
    }
});

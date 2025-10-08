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
    
    // MVP Enhancement: Interaction state for hover and selection
    let hoveredDevice = null;
    let hoveredConnection = null;
    let selectedDevice = null;
    let selectedConnection = null;
    
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
        
        // MVP Enhancement: Add mouse interaction for hover effects
        topologyCanvas.addEventListener('mousemove', handleCanvasMouseMove);
        topologyCanvas.addEventListener('click', handleCanvasClick);
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
        
        // Draw background grid with improved visibility
        drawGrid();
        
        // Draw connections first (so they appear behind devices)
        // Enhanced with hover detection and better visual feedback
        userSolution.connections?.forEach(conn => {
            drawConnection(conn);
        });
        
        // Draw devices with improved styling
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
        // MVP Enhancement: Better device rendering with glow effects and clear visibility
        const size = 50;
        const isSelected = device.selected || false;
        const isHovered = device === hoveredDevice;
        
        // Draw selection or hover glow
        if (isSelected || isHovered) {
            const glowColor = isSelected ? 'rgba(57, 255, 20, 0.3)' : 'rgba(0, 217, 255, 0.3)';
            ctx.fillStyle = glowColor;
            ctx.beginPath();
            ctx.fillRect(device.x - size/2 - 4, device.y - size/2 - 4, size + 8, size + 8);
        }
        
        // Draw device shadow for depth
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.fillRect(device.x - size/2 + 2, device.y - size/2 + 2, size, size);
        
        // Draw device background
        ctx.fillStyle = getDeviceColor(device.type);
        ctx.globalAlpha = 0.9;
        ctx.fillRect(device.x - size/2, device.y - size/2, size, size);
        ctx.globalAlpha = 1.0;
        
        // Draw device border
        const borderColor = isSelected ? '#39FF14' : (isHovered ? '#00D9FF' : '#F8FAFC');
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = isSelected ? 3 : (isHovered ? 3 : 2);
        ctx.strokeRect(device.x - size/2, device.y - size/2, size, size);
        
        // Draw device icon/type indicator
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Type-based emoji icons for better recognition
        const iconChar = getDeviceIcon(device.type);
        ctx.fillText(iconChar, device.x, device.y - 5);
        
        // Draw device label with background for readability
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        
        const labelText = device.label || device.name || device.type;
        const textWidth = ctx.measureText(labelText).width;
        
        // Label background
        ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
        ctx.fillRect(
            device.x - textWidth/2 - 4,
            device.y + size/2 + 4,
            textWidth + 8,
            18
        );
        
        // Label text
        const labelColor = isSelected ? '#39FF14' : (isHovered ? '#00D9FF' : '#F8FAFC');
        ctx.fillStyle = labelColor;
        ctx.fillText(labelText, device.x, device.y + size/2 + 8);
        
        // Connection indicator - show number of connections
        if (device.connections && device.connections.length > 0) {
            const connCount = device.connections.length;
            ctx.fillStyle = '#00D9FF';
            ctx.beginPath();
            ctx.arc(device.x + size/2 - 8, device.y - size/2 + 8, 10, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#0F172A';
            ctx.font = 'bold 10px Arial';
            ctx.fillText(connCount.toString(), device.x + size/2 - 8, device.y - size/2 + 8);
        }
        
        // Show device type tooltip on hover
        if (isHovered) {
            const tooltipText = device.type.charAt(0).toUpperCase() + device.type.slice(1);
            const tooltipWidth = ctx.measureText(tooltipText).width;
            
            ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
            ctx.fillRect(
                device.x - tooltipWidth/2 - 6,
                device.y - size/2 - 25,
                tooltipWidth + 12,
                18
            );
            
            ctx.fillStyle = '#00D9FF';
            ctx.font = 'bold 11px Arial';
            ctx.fillText(tooltipText, device.x, device.y - size/2 - 16);
        }
    }
    
    function getDeviceIcon(type) {
        // Return emoji icons for better visual distinction
        const iconMap = {
            router: '🔀',
            switch: '🔌',
            hub: '⚡',
            pc: '🖥️',
            computer: '🖥️',
            laptop: '💻',
            server: '🖥️',
            printer: '🖨️',
            'access-point': '📶',
            firewall: '🛡️',
            cloud: '☁️',
            internet: '🌐'
        };
        
        return iconMap[type.toLowerCase()] || '📦';
    }
    
    function getDeviceColor(type) {
        // MVP Enhancement: More vibrant colors matching the theme
        switch (type.toLowerCase()) {
            case 'router':
                return '#EF4444'; // Bright red
            case 'switch':
                return '#3B82F6'; // Bright blue
            case 'hub':
                return '#8B5CF6'; // Purple
            case 'pc':
            case 'computer':
            case 'laptop':
                return '#10B981'; // Bright green
            case 'server':
                return '#8B5CF6'; // Purple
            case 'printer':
                return '#F59E0B'; // Orange
            case 'access-point':
                return '#00D9FF'; // Cyan
            case 'firewall':
                return '#DC2626'; // Dark red
            case 'cloud':
            case 'internet':
                return '#06B6D4'; // Teal
            default:
                return '#6B7280'; // Gray
        }
    }
    
    function drawConnection(connection) {
        // Find the source and target devices
        const source = userSolution.devices.find(d => d.id === connection.source);
        const target = userSolution.devices.find(d => d.id === connection.target);
        
        if (!source || !target) return;
        
        // MVP Enhancement: Enhanced visual distinction between wired and wireless
        const isWireless = connection.type === 'wireless';
        const isSelected = connection.selected || false;
        const isHovered = connection === hoveredConnection;
        const isActive = connection.status !== 'down';
        
        // Connection color based on type
        const baseColor = isWireless ? '#8B5CF6' : '#00D9FF'; // Purple for wireless, cyan for wired
        const glowColor = isSelected ? '#39FF14' : '#00D9FF';
        
        // Draw glow effect for better visibility (selected or hovered)
        if (isSelected || isHovered) {
            ctx.strokeStyle = glowColor;
            ctx.lineWidth = isHovered ? 10 : 8;
            ctx.globalAlpha = isHovered ? 0.4 : 0.3;
            ctx.beginPath();
            ctx.moveTo(source.x, source.y);
            ctx.lineTo(target.x, target.y);
            ctx.stroke();
            ctx.globalAlpha = 1.0;
        }
        
        // Set line style based on connection type (matching dynamic simulation)
        ctx.strokeStyle = isSelected ? glowColor : (isHovered ? '#39FF14' : baseColor);
        ctx.lineWidth = isWireless ? 2 : 3; // Thinner for wireless
        ctx.globalAlpha = isActive ? 1.0 : 0.5;
        
        // Dashed for wireless, solid for wired
        if (isWireless) {
            ctx.setLineDash([8, 4]); // Dashed line for wireless
        } else {
            ctx.setLineDash([]); // Solid line for wired
        }
        
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();
        
        // Reset line dash
        ctx.setLineDash([]);
        ctx.globalAlpha = 1.0;
        
        // Draw midpoint indicator - type-specific
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        
        // Outer glow for midpoint
        const midpointSize = isHovered ? 10 : 8;
        ctx.fillStyle = baseColor;
        ctx.globalAlpha = 0.3;
        ctx.beginPath();
        ctx.arc(midX, midY, midpointSize, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
        
        // Main midpoint indicator
        ctx.fillStyle = isSelected ? glowColor : (isHovered ? '#39FF14' : baseColor);
        ctx.beginPath();
        ctx.arc(midX, midY, isHovered ? 6 : 5, 0, Math.PI * 2);
        ctx.fill();
        
        // Inner highlight for depth
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.beginPath();
        ctx.arc(midX, midY, 2, 0, Math.PI * 2);
        ctx.fill();
        
        // Show connection info on hover with type
        if (isHovered) {
            const connType = isWireless ? 'Wireless' : 'Wired (Ethernet)';
            
            ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
            const textWidth = ctx.measureText(connType).width + 20;
            ctx.fillRect(midX - textWidth/2, midY - 25, textWidth, 20);
            
            ctx.fillStyle = baseColor;
            ctx.font = 'bold 11px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(connType, midX, midY - 15);
        }
        
        // Status indicator near midpoint
        if (!isActive) {
            ctx.fillStyle = '#EF4444';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('✕', midX, midY - 15);
        }
    }
    
    function getConnectionColor(type) {
        // MVP Enhancement: More vibrant, distinguishable colors
        switch (type) {
            case 'ethernet':
                return '#00D9FF'; // Bright cyber cyan
            case 'fiber':
                return '#39FF14'; // Neon green
            case 'serial':
                return '#F59E0B'; // Bright orange
            case 'wireless':
                return '#8B5CF6'; // Purple
            default:
                return '#3B82F6'; // Blue
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
        hoveredDevice = null;
        hoveredConnection = null;
        selectedDevice = null;
        selectedConnection = null;
        stopTimer();
        
        // Show scenario selection screen
        resultScreen.classList.add('hidden');
        activeScenario.classList.add('hidden');
        scenarioSelection.classList.remove('hidden');
    }
    
    // ===== MVP ENHANCEMENT: INTERACTION HELPERS =====
    
    function handleCanvasMouseMove(e) {
        const rect = topologyCanvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // Check for device hover
        const device = getDeviceAt(mouseX, mouseY);
        const connection = device ? null : getConnectionAt(mouseX, mouseY);
        
        let needsRedraw = false;
        
        if (device !== hoveredDevice) {
            hoveredDevice = device;
            needsRedraw = true;
            topologyCanvas.style.cursor = device ? 'pointer' : 'default';
        }
        
        if (connection !== hoveredConnection) {
            hoveredConnection = connection;
            needsRedraw = true;
            topologyCanvas.style.cursor = connection ? 'pointer' : (device ? 'pointer' : 'default');
        }
        
        if (needsRedraw) {
            renderTopology();
        }
    }
    
    function handleCanvasClick(e) {
        const rect = topologyCanvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // Check for device click first
        const device = getDeviceAt(mouseX, mouseY);
        if (device) {
            selectDevice(device);
            return;
        }
        
        // Check for connection click
        const connection = getConnectionAt(mouseX, mouseY);
        if (connection) {
            selectConnection(connection);
            return;
        }
        
        // Clear selection if clicking empty space
        clearSelection();
    }
    
    function getDeviceAt(x, y) {
        // Check devices in reverse order (top device first)
        for (let i = userSolution.devices.length - 1; i >= 0; i--) {
            const device = userSolution.devices[i];
            const size = 50;
            if (x >= device.x - size/2 &&
                x <= device.x + size/2 &&
                y >= device.y - size/2 &&
                y <= device.y + size/2) {
                return device;
            }
        }
        return null;
    }
    
    function getConnectionAt(x, y) {
        const tolerance = 8; // Increased tolerance for easier clicking
        
        for (const connection of userSolution.connections || []) {
            const source = userSolution.devices.find(d => d.id === connection.source);
            const target = userSolution.devices.find(d => d.id === connection.target);
            
            if (!source || !target) continue;
            
            const dist = distanceToLine(x, y, source.x, source.y, target.x, target.y);
            
            if (dist <= tolerance) {
                return connection;
            }
        }
        
        return null;
    }
    
    function distanceToLine(px, py, x1, y1, x2, y2) {
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
    
    function selectDevice(device) {
        clearSelection();
        device.selected = true;
        selectedDevice = device;
        renderTopology();
        
        console.log('📱 Selected device:', device.id || device.label);
    }
    
    function selectConnection(connection) {
        clearSelection();
        connection.selected = true;
        selectedConnection = connection;
        renderTopology();
        
        console.log('🔗 Selected connection:', connection.id);
    }
    
    function clearSelection() {
        if (selectedDevice) {
            selectedDevice.selected = false;
            selectedDevice = null;
        }
        if (selectedConnection) {
            selectedConnection.selected = false;
            selectedConnection = null;
        }
        userSolution.devices?.forEach(device => device.selected = false);
        userSolution.connections?.forEach(conn => conn.selected = false);
        renderTopology();
    }
});

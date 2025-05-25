document.addEventListener('DOMContentLoaded', function() {
    // Safely initialize dashboard elements
    initializeDashboard();
    initializeWebSocketFeatures();
    initializeCharts();
});

function initializeDashboard() {
    // Add null checks for all DOM interactions
    const filterElements = {
        dateRange: document.getElementById('date-range-filter'),
        category: document.getElementById('category-filter'),
        exportBtn: document.getElementById('export-data-btn')
    };
    
    // Only add event listeners if elements exist
    if (filterElements.dateRange) {
        filterElements.dateRange.addEventListener('change', updateCharts);
    }
    
    if (filterElements.category) {
        filterElements.category.addEventListener('change', updateCharts);
    }
    
    if (filterElements.exportBtn) {
        filterElements.exportBtn.addEventListener('click', exportData);
    }
}

function initializeWebSocketFeatures() {
    // WebSocket connection control panel
    const wsElements = {
        connectBtn: document.getElementById('connect-websocket'),
        broadcastForm: document.getElementById('broadcast-form'),
        statusIndicator: document.querySelector('.status-dot'),
        statusText: document.querySelector('.status-text')
    };
    
    if (wsElements.connectBtn) {
        wsElements.connectBtn.addEventListener('click', function() {
            if (typeof window.socketClient !== 'undefined') {
                if (window.socketClient.connected) {
                    window.socketClient.disconnect();
                    this.textContent = 'Connect';
                    this.classList.remove('btn-success');
                } else {
                    window.socketClient.connect();
                    this.textContent = 'Connecting...';
                }
            }
        });
    }
    
    if (wsElements.broadcastForm) {
        wsElements.broadcastForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendBroadcastMessage();
        });
    }
    
    // Initialize WebSocket event handlers if available
    if (typeof window.socketClient !== 'undefined') {
        window.socketClient.on('connected', function() {
            updateConnectionStatus(true);
            loadActiveUsers();
        });
        
        window.socketClient.on('disconnected', function() {
            updateConnectionStatus(false);
        });
        
        window.socketClient.on('user_connected', function(data) {
            addUserToActiveList(data);
            logActivity('info', `User ${data.username} connected`);
        });
        
        window.socketClient.on('user_disconnected', function(data) {
            removeUserFromActiveList(data);
            logActivity('warning', `User ${data.username} disconnected`);
        });
    }
}

function updateConnectionStatus(connected) {
    const statusIndicator = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    const connectBtn = document.getElementById('connect-websocket');
    
    if (statusIndicator) {
        statusIndicator.className = connected ? 'status-dot connected' : 'status-dot disconnected';
    }
    
    if (statusText) {
        statusText.textContent = connected ? 'Connected' : 'Disconnected';
    }
    
    if (connectBtn) {
        connectBtn.textContent = connected ? 'Disconnect' : 'Connect';
        if (connected) {
            connectBtn.classList.add('btn-success');
        } else {
            connectBtn.classList.remove('btn-success');
        }
    }
}

function sendBroadcastMessage() {
    const form = document.getElementById('broadcast-form');
    if (!form) return;
    
    const formData = new FormData(form);
    const message = {
        type: formData.get('message-type'),
        title: formData.get('message-title'),
        content: formData.get('message-content'),
        target: formData.get('message-target')
    };
    
    if (typeof window.socketClient !== 'undefined' && window.socketClient.connected) {
        window.socketClient.emit('admin_broadcast', message);
        logActivity('success', `Broadcast sent: ${message.title}`);
        form.reset();
    } else {
        alert('WebSocket not connected. Cannot send broadcast message.');
    }
}

function loadActiveUsers() {
    if (typeof window.socketClient !== 'undefined' && window.socketClient.connected) {
        window.socketClient.emit('get_active_users');
    }
}

function addUserToActiveList(userData) {
    const usersGrid = document.querySelector('.users-grid');
    if (!usersGrid) return;
    
    // Check if user already exists
    const existingUser = usersGrid.querySelector(`[data-user-id="${userData.user_id}"]`);
    if (existingUser) return;
    
    const userCard = document.createElement('div');
    userCard.className = 'user-card';
    userCard.setAttribute('data-user-id', userData.user_id);
    userCard.innerHTML = `
        <div class="user-info">
            <strong>${userData.username}</strong>
            <small>Connected: ${new Date().toLocaleTimeString()}</small>
        </div>
        <div class="activity">${userData.current_page || 'Dashboard'}</div>
    `;
    
    usersGrid.appendChild(userCard);
}

function removeUserFromActiveList(userData) {
    const usersGrid = document.querySelector('.users-grid');
    if (!usersGrid) return;
    
    const userCard = usersGrid.querySelector(`[data-user-id="${userData.user_id}"]`);
    if (userCard) {
        userCard.remove();
    }
}

function logActivity(type, message) {
    const activityList = document.querySelector('.activity-list');
    if (!activityList) return;
    
    const activityItem = document.createElement('div');
    activityItem.className = `activity-item ${type}`;
    
    const iconClass = {
        'success': 'bx-check-circle',
        'warning': 'bx-error-circle',
        'error': 'bx-x-circle',
        'info': 'bx-info-circle'
    }[type] || 'bx-info-circle';
    
    activityItem.innerHTML = `
        <div class="activity-icon">
            <i class="bx ${iconClass}"></i>
        </div>
        <div class="activity-message">${message}</div>
        <div class="activity-time">${new Date().toLocaleTimeString()}</div>
    `;
    
    // Insert at the beginning
    activityList.insertBefore(activityItem, activityList.firstChild);
    
    // Keep only the last 10 items
    while (activityList.children.length > 10) {
        activityList.removeChild(activityList.lastChild);
    }
}

function initializeCharts() {
    // Initialize charts with error handling
    try {
        if (typeof Chart !== 'undefined') {
            initializeScoreDistributionChart();
            initializeActivityChart();
            initializeCategoryChart();
        }
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

function initializeScoreDistributionChart() {
    const ctx = document.getElementById('scoreDistributionChart');
    if (!ctx) return;
    
    // Chart initialization code here
    console.log('Score distribution chart initialized');
}

function initializeActivityChart() {
    const ctx = document.getElementById('activityChart');
    if (!ctx) return;
    
    // Chart initialization code here
    console.log('Activity chart initialized');
}

function initializeCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    // Chart initialization code here
    console.log('Category chart initialized');
}

function updateCharts() {
    const dateRange = document.getElementById('date-range-filter')?.value || '7';
    const category = document.getElementById('category-filter')?.value || 'all';
    
    // Fetch updated chart data
    fetch(`/admin/api/chart-data?date_range=${dateRange}&category=${category}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update charts with new data
                updateScoreDistributionChart(data.score_dist);
                updateActivityChart(data.activity_dates, data.active_users);
                updateCategoryChart(data.category_avg);
            }
        })
        .catch(error => {
            console.error('Error updating charts:', error);
        });
}

function updateScoreDistributionChart(data) {
    // Update score distribution chart
    console.log('Updating score distribution chart:', data);
}

function updateActivityChart(dates, users) {
    // Update activity chart
    console.log('Updating activity chart:', dates, users);
}

function updateCategoryChart(data) {
    // Update category chart
    console.log('Updating category chart:', data);
}

function exportData() {
    const exportType = prompt('Export type (scores, users, questions):') || 'scores';
    const format = 'json';
    
    window.open(`/admin/export-data?type=${exportType}&format=${format}`, '_blank');
}

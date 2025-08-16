// Enhanced Deadline Management System
class DeadlineManager {
    constructor() {
        this.deadlines = new Map();
        this.notifications = [];
        this.checkInterval = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.loadDeadlines();
            this.startDeadlineMonitoring();
            this.enhanceDeadlineInputs();
        });
    }

    // Load existing deadlines from the system
    loadDeadlines() {
        // This would typically fetch from the backend
        fetch('/admin/api/deadlines')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                data.deadlines?.forEach(deadline => {
                    this.addDeadline(deadline);
                });
                this.updateDeadlineDisplay();
            })
            .catch(error => {
                console.warn('Deadlines API not available, using local mode:', error.message);
                // Initialize with empty deadlines for now
                this.updateDeadlineDisplay();
            });
    }

    // Add a new deadline to the system
    addDeadline(deadlineData) {
        const deadline = {
            id: deadlineData.id || Date.now(),
            title: deadlineData.title,
            description: deadlineData.description,
            dueDate: new Date(deadlineData.dueDate),
            type: deadlineData.type || 'assignment', // assignment, quiz, project, etc.
            classId: deadlineData.classId,
            priority: deadlineData.priority || 'medium',
            notificationSettings: deadlineData.notificationSettings || {
                enabled: true,
                beforeDays: [7, 3, 1],
                beforeHours: [24, 12, 2, 1]
            },
            status: deadlineData.status || 'active',
            created: new Date(deadlineData.created || Date.now()),
            students: deadlineData.students || []
        };

        this.deadlines.set(deadline.id, deadline);
        return deadline;
    }

    // Update deadline
    updateDeadline(id, updates) {
        const deadline = this.deadlines.get(id);
        if (deadline) {
            Object.assign(deadline, updates);
            this.saveDeadline(deadline);
            this.updateDeadlineDisplay();
        }
    }

    // Delete deadline
    deleteDeadline(id) {
        this.deadlines.delete(id);
        this.updateDeadlineDisplay();
    }

    // Start monitoring deadlines for notifications
    startDeadlineMonitoring() {
        // Check every minute
        this.checkInterval = setInterval(() => {
            this.checkUpcomingDeadlines();
        }, 60000);

        // Initial check
        this.checkUpcomingDeadlines();
    }

    // Check for upcoming deadlines and send notifications
    checkUpcomingDeadlines() {
        const now = new Date();
        
        this.deadlines.forEach(deadline => {
            if (deadline.status !== 'active') return;
            
            const timeDiff = deadline.dueDate.getTime() - now.getTime();
            const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
            const hoursDiff = Math.ceil(timeDiff / (1000 * 60 * 60));

            // Check if we should send notifications
            if (deadline.notificationSettings.enabled) {
                // Days-based notifications
                if (deadline.notificationSettings.beforeDays.includes(daysDiff) && 
                    !this.hasNotificationBeenSent(deadline.id, `${daysDiff}days`)) {
                    this.sendDeadlineNotification(deadline, `${daysDiff} day${daysDiff === 1 ? '' : 's'}`);
                    this.markNotificationSent(deadline.id, `${daysDiff}days`);
                }
                
                // Hours-based notifications (for last 24 hours)
                if (daysDiff <= 1 && deadline.notificationSettings.beforeHours.includes(hoursDiff) &&
                    !this.hasNotificationBeenSent(deadline.id, `${hoursDiff}hours`)) {
                    this.sendDeadlineNotification(deadline, `${hoursDiff} hour${hoursDiff === 1 ? '' : 's'}`);
                    this.markNotificationSent(deadline.id, `${hoursDiff}hours`);
                }

                // Overdue notification
                if (timeDiff < 0 && deadline.status === 'active') {
                    this.markDeadlineOverdue(deadline);
                }
            }
        });
    }

    // Send notification about upcoming deadline
    sendDeadlineNotification(deadline, timeRemaining) {
        const notification = {
            title: `Deadline Reminder: ${deadline.title}`,
            message: `Due in ${timeRemaining}`,
            type: this.getNotificationType(timeRemaining),
            deadline: deadline
        };

        // Show browser notification
        this.showBrowserNotification(notification);
        
        // Show in-app notification
        this.showInAppNotification(notification);
        
        // Log notification
        console.log(`Deadline notification sent for ${deadline.title} - Due in ${timeRemaining}`);
    }

    // Enhance deadline input fields with validation and helpers
    enhanceDeadlineInputs() {
        const deadlineInputs = document.querySelectorAll('input[type="datetime-local"]');
        
        deadlineInputs.forEach(input => {
            this.enhanceDeadlineInput(input);
        });
    }

    enhanceDeadlineInput(input) {
        // Add wrapper for enhanced functionality
        if (!input.parentElement.classList.contains('deadline-input-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'deadline-input-wrapper';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            // Add helper text
            const helper = document.createElement('div');
            helper.className = 'deadline-helper';
            wrapper.appendChild(helper);

            // Add quick select buttons
            const quickSelect = document.createElement('div');
            quickSelect.className = 'deadline-quick-select';
            quickSelect.innerHTML = `
                <span class="quick-label">Quick select:</span>
                <button type="button" class="btn-quick" data-hours="24">Tomorrow</button>
                <button type="button" class="btn-quick" data-days="3">3 days</button>
                <button type="button" class="btn-quick" data-days="7">1 week</button>
                <button type="button" class="btn-quick" data-days="14">2 weeks</button>
            `;
            wrapper.appendChild(quickSelect);

            // Bind quick select events
            quickSelect.addEventListener('click', (e) => {
                if (e.target.classList.contains('btn-quick')) {
                    const hours = e.target.getAttribute('data-hours');
                    const days = e.target.getAttribute('data-days');
                    
                    const date = new Date();
                    if (hours) {
                        date.setHours(date.getHours() + parseInt(hours));
                    }
                    if (days) {
                        date.setDate(date.getDate() + parseInt(days));
                    }
                    
                    // Format for datetime-local input
                    const formatted = date.toISOString().slice(0, 16);
                    input.value = formatted;
                    
                    // Trigger change event
                    input.dispatchEvent(new Event('change'));
                }
            });
        }

        // Add validation and helper text
        input.addEventListener('change', () => {
            this.validateDeadlineInput(input);
        });

        // Set minimum date to now
        const now = new Date();
        const minDate = now.toISOString().slice(0, 16);
        input.setAttribute('min', minDate);
    }

    validateDeadlineInput(input) {
        const value = input.value;
        const helper = input.parentElement.querySelector('.deadline-helper');
        
        if (!value) {
            helper.textContent = '';
            input.classList.remove('valid', 'invalid', 'warning');
            return;
        }

        const selectedDate = new Date(value);
        const now = new Date();
        const timeDiff = selectedDate.getTime() - now.getTime();
        const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));

        if (timeDiff < 0) {
            // Past date
            helper.textContent = 'Deadline is in the past';
            helper.className = 'deadline-helper error';
            input.classList.add('invalid');
            input.classList.remove('valid', 'warning');
        } else if (daysDiff < 1) {
            // Less than 24 hours
            const hoursLeft = Math.ceil(timeDiff / (1000 * 60 * 60));
            helper.textContent = `Due in ${hoursLeft} hour${hoursLeft === 1 ? '' : 's'} - Very soon!`;
            helper.className = 'deadline-helper warning';
            input.classList.add('warning');
            input.classList.remove('valid', 'invalid');
        } else {
            // Valid future date
            helper.textContent = `Due in ${daysDiff} day${daysDiff === 1 ? '' : 's'}`;
            helper.className = 'deadline-helper success';
            input.classList.add('valid');
            input.classList.remove('invalid', 'warning');
        }
    }

    // Get notification type based on time remaining
    getNotificationType(timeRemaining) {
        if (timeRemaining.includes('hour') && parseInt(timeRemaining) <= 2) {
            return 'urgent';
        } else if (timeRemaining.includes('day') && parseInt(timeRemaining) <= 1) {
            return 'warning';
        } else {
            return 'info';
        }
    }

    // Show browser notification
    showBrowserNotification(notification) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/static/img/Logo.png',
                badge: '/static/img/Logo.png'
            });
        }
    }

    // Show in-app notification
    showInAppNotification(notification) {
        // Create notification element
        const notificationEl = document.createElement('div');
        notificationEl.className = `deadline-notification notification-${notification.type}`;
        notificationEl.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-clock"></i>
                <div class="notification-text">
                    <strong>${notification.title}</strong>
                    <p>${notification.message}</p>
                </div>
                <button class="notification-close">&times;</button>
            </div>
        `;

        // Add to notifications container
        let container = document.querySelector('.deadline-notifications');
        if (!container) {
            container = document.createElement('div');
            container.className = 'deadline-notifications';
            document.body.appendChild(container);
        }
        
        container.appendChild(notificationEl);

        // Auto remove after 10 seconds
        setTimeout(() => {
            if (notificationEl.parentElement) {
                notificationEl.remove();
            }
        }, 10000);

        // Manual close
        notificationEl.querySelector('.notification-close').addEventListener('click', () => {
            notificationEl.remove();
        });
    }

    // Update deadline display in UI
    updateDeadlineDisplay() {
        const deadlinesList = document.querySelector('.deadlines-list');
        if (!deadlinesList) return;

        // Sort deadlines by due date
        const sortedDeadlines = Array.from(this.deadlines.values())
            .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime());

        deadlinesList.innerHTML = sortedDeadlines.map(deadline => 
            this.renderDeadlineItem(deadline)
        ).join('');
    }

    // Render individual deadline item
    renderDeadlineItem(deadline) {
        const now = new Date();
        const timeDiff = deadline.dueDate.getTime() - now.getTime();
        const isOverdue = timeDiff < 0;
        const daysDiff = Math.ceil(Math.abs(timeDiff) / (1000 * 60 * 60 * 24));
        
        const statusClass = isOverdue ? 'overdue' : 
                          (daysDiff <= 1 ? 'urgent' : 
                          (daysDiff <= 3 ? 'warning' : 'normal'));

        return `
            <div class="deadline-item ${statusClass}" data-deadline-id="${deadline.id}">
                <div class="deadline-content">
                    <div class="deadline-title">${deadline.title}</div>
                    <div class="deadline-description">${deadline.description || ''}</div>
                    <div class="deadline-meta">
                        <span class="deadline-type">${deadline.type}</span>
                        <span class="deadline-due">${deadline.dueDate.toLocaleString()}</span>
                        <span class="deadline-status ${statusClass}">
                            ${isOverdue ? 'Overdue' : `${daysDiff} day${daysDiff === 1 ? '' : 's'} left`}
                        </span>
                    </div>
                </div>
                <div class="deadline-actions">
                    <button class="btn-edit" onclick="deadlineManager.editDeadline('${deadline.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-delete" onclick="deadlineManager.deleteDeadline('${deadline.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // Utility methods
    hasNotificationBeenSent(deadlineId, type) {
        return this.notifications.some(n => n.deadlineId === deadlineId && n.type === type);
    }

    markNotificationSent(deadlineId, type) {
        this.notifications.push({
            deadlineId,
            type,
            sentAt: new Date()
        });
    }

    markDeadlineOverdue(deadline) {
        deadline.status = 'overdue';
        this.updateDeadlineDisplay();
    }

    saveDeadline(deadline) {
        // Save to backend
        fetch('/admin/api/deadlines', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(deadline)
        }).catch(error => console.error('Failed to save deadline:', error));
    }
}

// Initialize deadline manager
const deadlineManager = new DeadlineManager();
window.deadlineManager = deadlineManager;

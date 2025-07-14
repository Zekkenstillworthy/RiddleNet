/**
 * Notification Center JavaScript
 * Handles all frontend functionality for the admin notification center
 */

class NotificationCenter {
    constructor() {
        this.socket = null;
        this.init();
    }

    init() {
        this.initializeWebSocket();
        this.bindEventListeners();
        this.loadInitialData();
    }

    initializeWebSocket() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            this.setupSocketListeners();
        }
    }

    setupSocketListeners() {
        if (!this.socket) return;

        this.socket.on('notification_sent', (data) => {
            this.showMessage('Notification sent successfully!', 'success');
            this.refreshStats();
            this.refreshHistory();
        });

        this.socket.on('notification_error', (data) => {
            this.showMessage('Error sending notification: ' + data.error, 'error');
        });
    }

    bindEventListeners() {
        // Send notification form
        const sendForm = document.getElementById('sendNotificationForm');
        if (sendForm) {
            sendForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendNotification();
            });
        }

        // Template selection
        const templateSelect = document.getElementById('templateSelect');
        if (templateSelect) {
            templateSelect.addEventListener('change', (e) => {
                this.loadTemplate(e.target.value);
            });
        }

        // Refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="refresh-stats"]')) {
                this.refreshStats();
            }
            if (e.target.matches('[data-action="refresh-history"]')) {
                this.refreshHistory();
            }
        });
    }

    async loadInitialData() {
        await Promise.all([
            this.refreshStats(),
            this.refreshHistory(),
            this.loadUsers(),
            this.loadTemplates()
        ]);
    }

    async sendNotification() {
        const form = document.getElementById('sendNotificationForm');
        const formData = new FormData(form);
        
        const data = {
            title: formData.get('title'),
            message: formData.get('message'),
            notification_type: formData.get('notification_type'),
            priority: formData.get('priority'),
            recipient_type: formData.get('recipient_type'),
            specific_user: formData.get('specific_user'),
            channel: formData.get('channel')
        };

        try {
            const response = await fetch('/admin/api/notifications/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                this.showMessage('Notification sent successfully!', 'success');
                form.reset();
                this.refreshStats();
                this.refreshHistory();
            } else {
                throw new Error(result.error || 'Failed to send notification');
            }
        } catch (error) {
            this.showMessage('Error: ' + error.message, 'error');
        }
    }

    async refreshStats() {
        try {
            const response = await fetch('/admin/api/notifications/stats');
            const stats = await response.json();

            // Update stat displays
            this.updateStatElement('totalSent', stats.total_sent || 0);
            this.updateStatElement('emailsSent', stats.emails_sent || 0);
            this.updateStatElement('websocketsSent', stats.websockets_sent || 0);
            this.updateStatElement('successRate', (stats.success_rate || 0).toFixed(1) + '%');

        } catch (error) {
            console.error('Error refreshing stats:', error);
        }
    }

    async refreshHistory() {
        try {
            const response = await fetch('/admin/api/notifications/history');
            const history = await response.json();

            this.updateHistoryTable(history);

        } catch (error) {
            console.error('Error refreshing history:', error);
        }
    }

    async loadUsers() {
        try {
            const response = await fetch('/admin/api/users');
            const users = await response.json();

            const userSelect = document.getElementById('specificUser');
            if (userSelect) {
                userSelect.innerHTML = '<option value="">Select User...</option>';
                users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = `${user.username} (${user.email})`;
                    userSelect.appendChild(option);
                });
            }

        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    async loadTemplates() {
        try {
            const response = await fetch('/admin/api/notifications/templates');
            const templates = await response.json();

            const templateSelect = document.getElementById('templateSelect');
            if (templateSelect) {
                templateSelect.innerHTML = '<option value="">Select Template...</option>';
                Object.keys(templates).forEach(key => {
                    const option = document.createElement('option');
                    option.value = key;
                    option.textContent = templates[key].title;
                    templateSelect.appendChild(option);
                });
            }

        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }

    loadTemplate(templateKey) {
        if (!templateKey) return;

        fetch('/admin/api/notifications/templates')
            .then(response => response.json())
            .then(templates => {
                const template = templates[templateKey];
                if (template) {
                    document.getElementById('notificationTitle').value = template.title;
                    document.getElementById('notificationMessage').value = template.message;
                    document.getElementById('notificationPriority').value = template.priority;
                    document.getElementById('notificationType').value = template.type;
                }
            })
            .catch(error => {
                console.error('Error loading template:', error);
            });
    }

    updateStatElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    updateHistoryTable(history) {
        const tableBody = document.querySelector('#historyTable tbody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        history.forEach(notification => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(notification.timestamp).toLocaleString()}</td>
                <td><span class="notification-type ${notification.type}">${notification.type}</span></td>
                <td>${this.escapeHtml(notification.title)}</td>
                <td><span class="priority ${notification.priority}">${notification.priority}</span></td>
                <td>${notification.recipient_type}</td>
                <td><span class="status ${notification.status}">${notification.status}</span></td>
                <td>${notification.email_sent}/${notification.websocket_sent}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    showMessage(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span>${this.escapeHtml(message)}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;

        // Add to page
        const container = document.getElementById('notification-container') || document.body;
        container.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.notificationCenter = new NotificationCenter();
});

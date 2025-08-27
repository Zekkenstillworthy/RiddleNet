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

// === ADVANCED DEADLINE POLICY MANAGEMENT ===

class AdvancedDeadlineManager extends DeadlineManager {
    constructor() {
        super();
        this.penaltyTiers = [];
        this.currentPenaltyType = 'simple';
        this.initAdvancedFeatures();
    }

    initAdvancedFeatures() {
        this.bindAdvancedEventListeners();
        this.updatePolicyPreview();
        this.initializePenaltyCalculator();
    }

    bindAdvancedEventListeners() {
        // Policy type change handler
        $(document).on('change', '#penalty_policy_type', (e) => {
            this.currentPenaltyType = e.target.value;
            this.togglePolicySettings();
            this.updatePolicyPreview();
        });

        // Add penalty tier button
        $(document).on('click', '#addPenaltyTier', () => {
            this.addPenaltyTier();
        });

        // Remove penalty tier
        $(document).on('click', '.penalty-tier-remove', (e) => {
            this.removePenaltyTier(e.target.closest('.penalty-tier'));
        });

        // Penalty tier input changes
        $(document).on('input', '.penalty-tier input', () => {
            this.updatePolicyPreview();
        });

        // Exponential penalty settings
        $(document).on('input', '#exponential_base, #exponential_max_penalty', () => {
            this.updatePolicyPreview();
        });

        // Fixed penalty settings
        $(document).on('input', '#fixed_penalty_amount', () => {
            this.updatePolicyPreview();
        });

        // Simple penalty settings
        $(document).on('input', '#simple_penalty_per_day', () => {
            this.updatePolicyPreview();
        });

        // Penalty calculator inputs
        $(document).on('input', '#calculator_days_late, #calculator_original_grade', () => {
            this.calculatePenaltyPreview();
        });

        // Extension form validation
        $(document).on('input', '#extension_hours', (e) => {
            this.validateExtensionHours(e.target);
        });

        // Availability window preview
        $(document).on('change', '#availability_from, #availability_to, #deadline_date', () => {
            this.updateAvailabilityPreview();
        });
    }

    togglePolicySettings() {
        // Hide all policy-specific settings
        $('.policy-type-settings').hide();
        
        // Show the relevant settings based on selected type
        switch(this.currentPenaltyType) {
            case 'tiered':
                $('#tieredPenaltySettings').show();
                break;
            case 'exponential':
                $('#exponentialPenaltySettings').show();
                break;
            case 'fixed':
                $('#fixedPenaltySettings').show();
                break;
            case 'simple':
                $('#simplePenaltySettings').show();
                break;
            default:
                $('#customPenaltySettings').show();
        }
    }

    addPenaltyTier() {
        const tierCount = $('.penalty-tier').length + 1;
        const tierHtml = `
            <div class="penalty-tier">
                <div class="penalty-tier-header">
                    <span class="tier-number">${tierCount}</span>
                    <button type="button" class="penalty-tier-remove">
                        <i class="fas fa-times"></i> Remove
                    </button>
                </div>
                <div class="row">
                    <div class="col-md-4">
                        <label class="form-label">Days Late (Start)</label>
                        <input type="number" class="form-control tier-days-start" 
                               min="1" step="1" value="${tierCount}" required>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Days Late (End)</label>
                        <input type="number" class="form-control tier-days-end" 
                               min="1" step="1" value="${tierCount + 2}" required>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Penalty (%)</label>
                        <input type="number" class="form-control tier-penalty" 
                               min="0" max="100" step="0.1" value="${tierCount * 10}" required>
                    </div>
                </div>
            </div>
        `;
        
        $('#penaltyTiersList').append(tierHtml);
        this.updatePolicyPreview();
        
        // Scroll to new tier
        $('.penalty-tier:last')[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    removePenaltyTier(tierElement) {
        $(tierElement).fadeOut(300, function() {
            $(this).remove();
            // Renumber remaining tiers
            $('.penalty-tier').each(function(index) {
                $(this).find('.tier-number').text(index + 1);
            });
        });
        
        setTimeout(() => {
            this.updatePolicyPreview();
        }, 350);
    }

    updatePolicyPreview() {
        const previewData = this.generatePreviewData();
        this.renderPolicyPreview(previewData);
    }

    generatePreviewData() {
        const data = [];
        
        switch(this.currentPenaltyType) {
            case 'tiered':
                $('.penalty-tier').each(function() {
                    const startDay = parseInt($(this).find('.tier-days-start').val()) || 0;
                    const endDay = parseInt($(this).find('.tier-days-end').val()) || 0;
                    const penalty = parseFloat($(this).find('.tier-penalty').val()) || 0;
                    
                    if (startDay > 0 && endDay >= startDay && penalty >= 0) {
                        for (let day = startDay; day <= Math.min(endDay, startDay + 10); day++) {
                            data.push({
                                day: day,
                                penalty: penalty,
                                finalGrade: Math.max(0, 100 - penalty)
                            });
                        }
                    }
                });
                break;
                
            case 'exponential':
                const base = parseFloat($('#exponential_base').val()) || 1.1;
                const maxPenalty = parseFloat($('#exponential_max_penalty').val()) || 100;
                
                for (let day = 1; day <= 15; day++) {
                    const penalty = Math.min(Math.pow(base, day) - 1, maxPenalty);
                    data.push({
                        day: day,
                        penalty: penalty.toFixed(1),
                        finalGrade: Math.max(0, 100 - penalty).toFixed(1)
                    });
                }
                break;
                
            case 'fixed':
                const fixedPenalty = parseFloat($('#fixed_penalty_amount').val()) || 0;
                for (let day = 1; day <= 10; day++) {
                    data.push({
                        day: day,
                        penalty: fixedPenalty,
                        finalGrade: Math.max(0, 100 - fixedPenalty)
                    });
                }
                break;
                
            case 'simple':
                const dailyPenalty = parseFloat($('#simple_penalty_per_day').val()) || 5;
                for (let day = 1; day <= 15; day++) {
                    const penalty = Math.min(day * dailyPenalty, 100);
                    data.push({
                        day: day,
                        penalty: penalty.toFixed(1),
                        finalGrade: Math.max(0, 100 - penalty).toFixed(1)
                    });
                }
                break;
        }
        
        return data.slice(0, 15); // Limit to 15 rows for preview
    }

    renderPolicyPreview(data) {
        const tableBody = $('#policyPreviewTable tbody');
        tableBody.empty();
        
        if (data.length === 0) {
            tableBody.append(`
                <tr>
                    <td colspan="3" class="text-center text-muted">
                        Configure penalty settings to see preview
                    </td>
                </tr>
            `);
            return;
        }
        
        data.forEach(row => {
            const penaltyClass = row.penalty >= 50 ? 'text-danger' : 
                                row.penalty >= 25 ? 'text-warning' : 'text-info';
            
            tableBody.append(`
                <tr>
                    <td>${row.day}</td>
                    <td class="${penaltyClass}">${row.penalty}%</td>
                    <td>${row.finalGrade}%</td>
                </tr>
            `);
        });
    }

    initializePenaltyCalculator() {
        // Set default values
        $('#calculator_original_grade').val('100');
        $('#calculator_days_late').val('1');
        this.calculatePenaltyPreview();
    }

    calculatePenaltyPreview() {
        const daysLate = parseInt($('#calculator_days_late').val()) || 0;
        const originalGrade = parseFloat($('#calculator_original_grade').val()) || 100;
        
        if (daysLate <= 0 || originalGrade <= 0) {
            $('#calculatorResult .penalty-amount').text('0%');
            $('#calculatorResult .final-grade').text(`${originalGrade}%`);
            return;
        }
        
        let penalty = 0;
        
        switch(this.currentPenaltyType) {
            case 'tiered':
                penalty = this.calculateTieredPenalty(daysLate);
                break;
            case 'exponential':
                const base = parseFloat($('#exponential_base').val()) || 1.1;
                const maxPenalty = parseFloat($('#exponential_max_penalty').val()) || 100;
                penalty = Math.min(Math.pow(base, daysLate) - 1, maxPenalty);
                break;
            case 'fixed':
                penalty = parseFloat($('#fixed_penalty_amount').val()) || 0;
                break;
            case 'simple':
                const dailyPenalty = parseFloat($('#simple_penalty_per_day').val()) || 5;
                penalty = Math.min(daysLate * dailyPenalty, 100);
                break;
        }
        
        const finalGrade = Math.max(0, originalGrade - (originalGrade * penalty / 100));
        
        $('#calculatorResult .penalty-amount').text(`${penalty.toFixed(1)}%`);
        $('#calculatorResult .final-grade').text(`Final Grade: ${finalGrade.toFixed(1)}%`);
    }

    calculateTieredPenalty(daysLate) {
        let penalty = 0;
        
        $('.penalty-tier').each(function() {
            const startDay = parseInt($(this).find('.tier-days-start').val()) || 0;
            const endDay = parseInt($(this).find('.tier-days-end').val()) || 0;
            const tierPenalty = parseFloat($(this).find('.tier-penalty').val()) || 0;
            
            if (daysLate >= startDay && daysLate <= endDay) {
                penalty = tierPenalty;
                return false; // Break the loop
            }
        });
        
        return penalty;
    }

    validateExtensionHours(input) {
        const hours = parseInt(input.value);
        const helpText = $(input).siblings('.form-text');
        
        if (hours < 1) {
            input.classList.add('is-invalid');
            helpText.text('Extension must be at least 1 hour').addClass('text-danger');
        } else if (hours > 168) { // 1 week
            input.classList.add('is-invalid');
            helpText.text('Extensions cannot exceed 168 hours (1 week)').addClass('text-danger');
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            
            const days = Math.floor(hours / 24);
            const remainingHours = hours % 24;
            let timeText = '';
            
            if (days > 0) {
                timeText += `${days} day${days > 1 ? 's' : ''}`;
                if (remainingHours > 0) {
                    timeText += ` and ${remainingHours} hour${remainingHours > 1 ? 's' : ''}`;
                }
            } else {
                timeText = `${hours} hour${hours > 1 ? 's' : ''}`;
            }
            
            helpText.text(`Extension: ${timeText}`).removeClass('text-danger').addClass('text-success');
        }
    }

    updateAvailabilityPreview() {
        const availableFrom = $('#availability_from').val();
        const availableTo = $('#availability_to').val();
        const deadlineDate = $('#deadline_date').val();
        
        if (!availableFrom || !availableTo || !deadlineDate) {
            $('.availability-window-preview').hide();
            return;
        }
        
        const fromDate = new Date(availableFrom);
        const toDate = new Date(availableTo);
        const deadline = new Date(deadlineDate);
        
        // Calculate durations
        const totalDuration = toDate - fromDate;
        const workingDuration = deadline - fromDate;
        const workingPercentage = Math.max(0, Math.min(100, (workingDuration / totalDuration) * 100));
        
        // Update timeline visualization
        $('.timeline-line').css('background', 
            `linear-gradient(to right, var(--cyber-glow) 0%, var(--cyber-glow) ${workingPercentage}%, var(--danger-color) ${workingPercentage}%, var(--danger-color) 100%)`
        );
        
        // Update labels
        $('.timeline-label:first').text(this.formatDate(fromDate));
        $('.timeline-label:nth-child(3)').text(this.formatDate(deadline));
        $('.timeline-label:last').text(this.formatDate(toDate));
        
        $('.availability-window-preview').show();
    }

    formatDate(date) {
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Public methods for external use
    savePolicyConfiguration() {
        const config = {
            type: this.currentPenaltyType,
            settings: this.getPolicySettings(),
            preview: this.generatePreviewData()
        };
        
        return config;
    }

    getPolicySettings() {
        const settings = {};
        
        switch(this.currentPenaltyType) {
            case 'tiered':
                settings.tiers = [];
                $('.penalty-tier').each(function() {
                    settings.tiers.push({
                        start_day: parseInt($(this).find('.tier-days-start').val()),
                        end_day: parseInt($(this).find('.tier-days-end').val()),
                        penalty: parseFloat($(this).find('.tier-penalty').val())
                    });
                });
                break;
            case 'exponential':
                settings.base = parseFloat($('#exponential_base').val());
                settings.max_penalty = parseFloat($('#exponential_max_penalty').val());
                break;
            case 'fixed':
                settings.penalty_amount = parseFloat($('#fixed_penalty_amount').val());
                break;
            case 'simple':
                settings.penalty_per_day = parseFloat($('#simple_penalty_per_day').val());
                break;
        }
        
        return settings;
    }

    loadPolicyConfiguration(config) {
        this.currentPenaltyType = config.type;
        $('#penalty_policy_type').val(config.type);
        this.togglePolicySettings();
        
        // Load specific settings
        switch(config.type) {
            case 'tiered':
                this.loadTieredSettings(config.settings);
                break;
            case 'exponential':
                $('#exponential_base').val(config.settings.base);
                $('#exponential_max_penalty').val(config.settings.max_penalty);
                break;
            case 'fixed':
                $('#fixed_penalty_amount').val(config.settings.penalty_amount);
                break;
            case 'simple':
                $('#simple_penalty_per_day').val(config.settings.penalty_per_day);
                break;
        }
        
        this.updatePolicyPreview();
    }

    loadTieredSettings(settings) {
        $('#penaltyTiersList').empty();
        
        if (settings.tiers && settings.tiers.length > 0) {
            settings.tiers.forEach((tier, index) => {
                const tierHtml = `
                    <div class="penalty-tier">
                        <div class="penalty-tier-header">
                            <span class="tier-number">${index + 1}</span>
                            <button type="button" class="penalty-tier-remove">
                                <i class="fas fa-times"></i> Remove
                            </button>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <label class="form-label">Days Late (Start)</label>
                                <input type="number" class="form-control tier-days-start" 
                                       min="1" step="1" value="${tier.start_day}" required>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">Days Late (End)</label>
                                <input type="number" class="form-control tier-days-end" 
                                       min="1" step="1" value="${tier.end_day}" required>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">Penalty (%)</label>
                                <input type="number" class="form-control tier-penalty" 
                                       min="0" max="100" step="0.1" value="${tier.penalty}" required>
                            </div>
                        </div>
                    </div>
                `;
                $('#penaltyTiersList').append(tierHtml);
            });
        } else {
            // Add default tier if none exist
            this.addPenaltyTier();
        }
    }
}

// Enhanced notification system for deadline alerts
class DeadlineNotifications {
    constructor() {
        this.notifications = [];
        this.init();
    }

    init() {
        this.createNotificationContainer();
        this.bindEventListeners();
    }

    createNotificationContainer() {
        if (!$('#deadlineNotifications').length) {
            $('body').append('<div id="deadlineNotifications" class="deadline-notifications"></div>');
        }
    }

    bindEventListeners() {
        $(document).on('click', '.notification-close', (e) => {
            this.removeNotification($(e.target).closest('.deadline-notification'));
        });
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notificationId = 'notification_' + Date.now();
        const iconClass = this.getIconClass(type);
        
        const notificationHtml = `
            <div id="${notificationId}" class="deadline-notification notification-${type}">
                <div class="notification-content">
                    <i class="${iconClass}"></i>
                    <div class="notification-text">
                        <strong>${this.getTypeTitle(type)}</strong>
                        <p>${message}</p>
                    </div>
                    <button class="notification-close" type="button">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        
        $('#deadlineNotifications').append(notificationHtml);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification($(`#${notificationId}`));
            }, duration);
        }
        
        return notificationId;
    }

    removeNotification(element) {
        element.fadeOut(300, function() {
            $(this).remove();
        });
    }

    getIconClass(type) {
        const icons = {
            info: 'fas fa-info-circle',
            warning: 'fas fa-exclamation-triangle',
            urgent: 'fas fa-exclamation-circle',
            success: 'fas fa-check-circle'
        };
        return icons[type] || icons.info;
    }

    getTypeTitle(type) {
        const titles = {
            info: 'Information',
            warning: 'Warning',
            urgent: 'Urgent',
            success: 'Success'
        };
        return titles[type] || 'Notification';
    }
}

// Initialize advanced features when document is ready
$(document).ready(function() {
    // Replace basic deadline manager with advanced version
    window.deadlineManager = new AdvancedDeadlineManager();
    window.deadlineNotifications = new DeadlineNotifications();
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Show notification when policy is saved
    $(document).on('click', '#savePolicyConfiguration', function() {
        const config = window.deadlineManager.savePolicyConfiguration();
        console.log('Saving policy configuration:', config);
        
        window.deadlineNotifications.showNotification(
            'Deadline policy configuration saved successfully!', 
            'success'
        );
    });
    
    // Initialize policy settings toggle
    if ($('#penalty_policy_type').length) {
        window.deadlineManager.togglePolicySettings();
    }
});

// Export for external use
window.AdvancedDeadlineManager = AdvancedDeadlineManager;
window.DeadlineNotifications = DeadlineNotifications;

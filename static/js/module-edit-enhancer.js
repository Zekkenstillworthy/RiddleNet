/**
 * Module Edit Enhanced JavaScript
 * Provides interactive functionality for the module edit interface
 */

class ModuleEditEnhancer {
    constructor() {
        this.autoSaveEnabled = true;
        this.autoSaveDelay = 2000;
        this.autoSaveTimeout = null;
        this.originalData = {};
        this.isDirty = false;
        
        this.init();
    }
    
    init() {
        this.setupAutoSave();
        this.setupFormValidation();
        this.setupKeyboardShortcuts();
        this.setupProgressIndicator();
        this.setupTooltips();
        this.setupAnimations();
        this.captureOriginalData();
    }
    
    // ===== AUTO-SAVE FUNCTIONALITY =====
    setupAutoSave() {
        const inputs = document.querySelectorAll('.module-form-control');
        const autoSaveIndicator = this.createAutoSaveIndicator();
        
        inputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.markAsDirty();
                this.scheduleAutoSave();
                this.addInputAnimation(e.target);
            });
            
            input.addEventListener('blur', (e) => {
                this.validateField(e.target);
            });
        });
    }
    
    createAutoSaveIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'module-autosave-indicator';
        indicator.innerHTML = '<i class="fas fa-check"></i> Auto-saved';
        document.body.appendChild(indicator);
        return indicator;
    }
    
    scheduleAutoSave() {
        if (!this.autoSaveEnabled) return;
        
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.performAutoSave();
        }, this.autoSaveDelay);
    }
    
    async performAutoSave() {
        if (!this.isDirty) return;
        
        const formData = this.collectFormData();
        const indicator = document.querySelector('.module-autosave-indicator');
        
        try {
            // Show saving indicator
            indicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            indicator.classList.add('show');
            
            // Simulate API call (replace with actual endpoint)
            await this.saveModuleDraft(formData);
            
            // Show success
            indicator.innerHTML = '<i class="fas fa-check"></i> Auto-saved';
            setTimeout(() => {
                indicator.classList.remove('show');
            }, 2000);
            
            this.isDirty = false;
            
        } catch (error) {
            console.error('Auto-save failed:', error);
            indicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Save failed';
            indicator.style.background = 'var(--module-danger)';
            setTimeout(() => {
                indicator.classList.remove('show');
                indicator.style.background = 'var(--module-success)';
            }, 3000);
        }
    }
    
    async saveModuleDraft(formData) {
        // Replace with actual API endpoint
        return new Promise((resolve) => {
            setTimeout(resolve, 500); // Simulate network delay
        });
    }
    
    // ===== FORM VALIDATION =====
    setupFormValidation() {
        const form = document.querySelector('form');
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                this.showValidationErrors();
            }
        });
    }
    
    validateForm() {
        const requiredFields = document.querySelectorAll('.module-form-control[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Specific field validations
        switch (field.name) {
            case 'title':
                if (value && value.length < 3) {
                    isValid = false;
                    errorMessage = 'Title must be at least 3 characters long';
                } else if (value && value.length > 100) {
                    isValid = false;
                    errorMessage = 'Title must not exceed 100 characters';
                }
                break;
                
            case 'estimated_duration':
                const duration = parseInt(value);
                if (value && (isNaN(duration) || duration < 1 || duration > 1000)) {
                    isValid = false;
                    errorMessage = 'Duration must be between 1 and 1000 minutes';
                }
                break;
                
            case 'order_index':
                const order = parseInt(value);
                if (value && (isNaN(order) || order < 0)) {
                    isValid = false;
                    errorMessage = 'Order index must be a non-negative number';
                }
                break;
        }
        
        this.displayFieldValidation(field, isValid, errorMessage);
        return isValid;
    }
    
    displayFieldValidation(field, isValid, errorMessage) {
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Update field styling
        field.classList.remove('field-valid', 'field-invalid');
        
        if (!isValid && errorMessage) {
            field.classList.add('field-invalid');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error';
            errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${errorMessage}`;
            field.parentNode.appendChild(errorDiv);
        } else if (isValid && field.value.trim()) {
            field.classList.add('field-valid');
        }
    }
    
    showValidationErrors() {
        const firstError = document.querySelector('.field-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
        
        this.showNotification('Please fix the validation errors before saving', 'error');
    }
    
    // ===== KEYBOARD SHORTCUTS =====
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+S / Cmd+S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveForm();
            }
            
            // Ctrl+Z / Cmd+Z to undo (if supported)
            if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
                this.undoLastChange();
            }
            
            // Escape to reset form
            if (e.key === 'Escape') {
                this.resetForm();
            }
        });
    }
    
    saveForm() {
        const submitButton = document.querySelector('.module-btn-primary');
        if (submitButton) {
            submitButton.click();
        }
    }
    
    undoLastChange() {
        // Implement undo functionality if needed
        console.log('Undo functionality - to be implemented');
    }
    
    resetForm() {
        if (this.isDirty) {
            if (confirm('Are you sure you want to reset all changes?')) {
                this.restoreOriginalData();
            }
        }
    }
    
    // ===== PROGRESS INDICATOR =====
    setupProgressIndicator() {
        const progressBar = this.createProgressBar();
        this.updateProgress();
        
        // Update progress when fields are filled
        const inputs = document.querySelectorAll('.module-form-control');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                setTimeout(() => this.updateProgress(), 100);
            });
        });
    }
    
    createProgressBar() {
        const container = document.createElement('div');
        container.className = 'module-progress-container';
        container.innerHTML = `
            <div class="module-progress-bar">
                <div class="module-progress-fill"></div>
            </div>
            <span class="module-progress-text">0% Complete</span>
        `;
        
        const header = document.querySelector('.module-edit-header');
        if (header) {
            header.appendChild(container);
        }
        
        return container;
    }
    
    updateProgress() {
        const requiredFields = document.querySelectorAll('.module-form-control[required]');
        const optionalFields = document.querySelectorAll('.module-form-control:not([required])');
        
        let filledRequired = 0;
        let filledOptional = 0;
        
        requiredFields.forEach(field => {
            if (field.value.trim()) filledRequired++;
        });
        
        optionalFields.forEach(field => {
            if (field.value.trim()) filledOptional++;
        });
        
        // Calculate progress (required fields worth 70%, optional 30%)
        const requiredProgress = (filledRequired / requiredFields.length) * 70;
        const optionalProgress = (filledOptional / optionalFields.length) * 30;
        const totalProgress = Math.round(requiredProgress + optionalProgress);
        
        const progressFill = document.querySelector('.module-progress-fill');
        const progressText = document.querySelector('.module-progress-text');
        
        if (progressFill && progressText) {
            progressFill.style.width = `${totalProgress}%`;
            progressText.textContent = `${totalProgress}% Complete`;
            
            // Change color based on progress
            if (totalProgress < 50) {
                progressFill.style.background = 'var(--module-danger)';
            } else if (totalProgress < 80) {
                progressFill.style.background = 'var(--module-warning)';
            } else {
                progressFill.style.background = 'var(--module-success)';
            }
        }
    }
    
    // ===== TOOLTIPS =====
    setupTooltips() {
        const elements = document.querySelectorAll('[data-tooltip]');
        elements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip);
            element.addEventListener('mouseleave', this.hideTooltip);
        });
    }
    
    showTooltip(e) {
        const text = e.target.getAttribute('data-tooltip');
        if (!text) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'module-tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);
        
        const rect = e.target.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - 35}px`;
        tooltip.style.transform = 'translateX(-50%)';
        
        setTimeout(() => tooltip.classList.add('show'), 10);
    }
    
    hideTooltip() {
        const tooltip = document.querySelector('.module-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
    
    // ===== ANIMATIONS =====
    setupAnimations() {
        this.observeElements();
        this.setupInputAnimations();
    }
    
    observeElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        });
        
        const sections = document.querySelectorAll('.module-form-section');
        sections.forEach(section => {
            observer.observe(section);
        });
    }
    
    setupInputAnimations() {
        const inputs = document.querySelectorAll('.module-form-control');
        inputs.forEach(input => {
            input.addEventListener('focus', (e) => {
                e.target.classList.add('input-focused');
            });
            
            input.addEventListener('blur', (e) => {
                e.target.classList.remove('input-focused');
            });
        });
    }
    
    addInputAnimation(element) {
        element.classList.add('input-changed');
        setTimeout(() => {
            element.classList.remove('input-changed');
        }, 300);
    }
    
    // ===== DATA MANAGEMENT =====
    captureOriginalData() {
        const inputs = document.querySelectorAll('.module-form-control');
        inputs.forEach(input => {
            this.originalData[input.name] = input.value;
        });
    }
    
    restoreOriginalData() {
        const inputs = document.querySelectorAll('.module-form-control');
        inputs.forEach(input => {
            if (this.originalData[input.name] !== undefined) {
                input.value = this.originalData[input.name];
            }
        });
        this.isDirty = false;
    }
    
    collectFormData() {
        const formData = {};
        const inputs = document.querySelectorAll('.module-form-control');
        inputs.forEach(input => {
            formData[input.name] = input.value;
        });
        return formData;
    }
    
    markAsDirty() {
        this.isDirty = true;
    }
    
    // ===== UTILITY METHODS =====
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `module-notification module-notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="close-notification" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Additional CSS for JavaScript enhancements
const additionalStyles = `
<style>
/* ===== FIELD VALIDATION STYLES ===== */
.field-valid {
    border-color: var(--module-success) !important;
    box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.1) !important;
}

.field-invalid {
    border-color: var(--module-danger) !important;
    box-shadow: 0 0 0 3px rgba(255, 71, 87, 0.1) !important;
}

.field-error {
    color: var(--module-danger);
    font-size: 0.85rem;
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    gap: 6px;
    animation: slideDown 0.3s ease;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* ===== PROGRESS BAR STYLES ===== */
.module-progress-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 1rem;
    padding: 1rem;
    background: rgba(15, 23, 42, 0.4);
    border-radius: 12px;
    border: 1px solid var(--module-border);
}

.module-progress-bar {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.module-progress-fill {
    height: 100%;
    background: var(--module-primary);
    border-radius: 4px;
    transition: all 0.3s ease;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.module-progress-text {
    color: var(--module-text-primary);
    font-size: 0.85rem;
    font-weight: 600;
    min-width: 100px;
}

/* ===== TOOLTIP STYLES ===== */
.module-tooltip {
    position: absolute;
    background: var(--module-surface);
    color: var(--module-text-primary);
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.85rem;
    border: 1px solid var(--module-border);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
}

.module-tooltip.show {
    opacity: 1;
}

.module-tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: var(--module-surface);
}

/* ===== NOTIFICATION STYLES ===== */
.module-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--module-surface);
    border: 1px solid var(--module-border);
    border-radius: 12px;
    padding: 16px;
    color: var(--module-text-primary);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(15px);
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 12px;
    max-width: 400px;
    opacity: 0;
    transform: translateX(100px);
    transition: all 0.3s ease;
}

.module-notification.show {
    opacity: 1;
    transform: translateX(0);
}

.module-notification-success {
    border-color: var(--module-success);
}

.module-notification-warning {
    border-color: var(--module-warning);
}

.module-notification-error {
    border-color: var(--module-danger);
}

.close-notification {
    background: none;
    border: none;
    color: var(--module-text-muted);
    cursor: pointer;
    padding: 4px;
    margin-left: auto;
    transition: color 0.3s ease;
}

.close-notification:hover {
    color: var(--module-text-primary);
}

/* ===== ANIMATION CLASSES ===== */
.animate-in {
    animation: fadeInUp 0.5s ease forwards;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.input-focused {
    transform: scale(1.02);
}

.input-changed {
    animation: inputPulse 0.3s ease;
}

@keyframes inputPulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}
</style>
`;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Add additional styles
    document.head.insertAdjacentHTML('beforeend', additionalStyles);
    
    // Initialize the module edit enhancer
    window.moduleEditEnhancer = new ModuleEditEnhancer();
    
    console.log('Module Edit Enhancer initialized successfully!');
});

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModuleEditEnhancer;
}

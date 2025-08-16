// Enhanced Tooltip System JavaScript
class TooltipManager {
    constructor() {
        this.tooltips = new Map();
        this.init();
    }

    init() {
        // Auto-initialize tooltips on page load
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeTooltips();
        });
    }

    initializeTooltips() {
        // Find all elements with data-tooltip attribute
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            this.createTooltip(element);
        });
    }

    createTooltip(element, options = {}) {
        const text = element.getAttribute('data-tooltip') || options.text || '';
        const position = element.getAttribute('data-tooltip-position') || options.position || 'top';
        const type = element.getAttribute('data-tooltip-type') || options.type || 'info';
        
        if (!text) return;

        // Create tooltip container if it doesn't exist
        if (!element.classList.contains('tooltip-container')) {
            element.classList.add('tooltip-container');
        }

        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = `tooltip tooltip-${position} tooltip-${type}`;
        tooltip.textContent = text;
        tooltip.setAttribute('role', 'tooltip');

        // Remove existing tooltip if present
        const existingTooltip = element.querySelector('.tooltip');
        if (existingTooltip) {
            existingTooltip.remove();
        }

        element.appendChild(tooltip);
        this.tooltips.set(element, tooltip);

        return tooltip;
    }

    // Method to add tooltip to any element programmatically
    addTooltip(selector, text, options = {}) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.setAttribute('data-tooltip', text);
            if (options.position) {
                element.setAttribute('data-tooltip-position', options.position);
            }
            if (options.type) {
                element.setAttribute('data-tooltip-type', options.type);
            }
            this.createTooltip(element, options);
        });
    }

    // Method to update tooltip text
    updateTooltip(element, newText) {
        const tooltip = this.tooltips.get(element);
        if (tooltip) {
            tooltip.textContent = newText;
            element.setAttribute('data-tooltip', newText);
        }
    }

    // Method to remove tooltip
    removeTooltip(element) {
        const tooltip = this.tooltips.get(element);
        if (tooltip) {
            tooltip.remove();
            this.tooltips.delete(element);
            element.removeAttribute('data-tooltip');
            element.removeAttribute('data-tooltip-position');
            element.removeAttribute('data-tooltip-type');
            element.classList.remove('tooltip-container');
        }
    }

    // Utility method to add help icon with tooltip
    addHelpIcon(labelSelector, tooltipText, options = {}) {
        const labels = document.querySelectorAll(labelSelector);
        labels.forEach(label => {
            // Create help icon
            const helpIcon = document.createElement('span');
            helpIcon.className = 'help-icon';
            helpIcon.innerHTML = '?';
            helpIcon.setAttribute('data-tooltip', tooltipText);
            helpIcon.setAttribute('data-tooltip-position', options.position || 'top');
            helpIcon.setAttribute('data-tooltip-type', options.type || 'info');

            // Add to label
            if (!label.classList.contains('form-label-with-tooltip')) {
                label.classList.add('form-label-with-tooltip');
            }
            label.appendChild(helpIcon);

            // Create tooltip for help icon
            this.createTooltip(helpIcon, options);
        });
    }
}

// Initialize global tooltip manager
const tooltipManager = new TooltipManager();

// Export for use in other scripts
window.tooltipManager = tooltipManager;

// Common tooltip configurations for RiddleNet
const RiddleNetTooltips = {
    // Admin interface tooltips
    admin: {
        classCode: "Unique 6-character code students use to join this class",
        classSection: "Optional section identifier (e.g., 'Period 1', 'Morning')",
        moduleOrder: "Determines the sequence students will see modules",
        simulationCategory: "Groups simulations by subject area for easy organization",
        difficultyLevel: "Helps students understand complexity before starting",
        estimatedDuration: "Expected time for completion (helps with planning)",
        learningObjectives: "What students should learn from this activity",
        prerequisites: "Required knowledge before attempting this activity",
        isPublished: "Only published content is visible to students",
        sequentialCompletion: "Students must complete modules in order",
        assignmentDeadline: "When this assignment is due",
        gradingRubric: "How this activity will be scored"
    },
    
    // Student interface tooltips  
    student: {
        progressBar: "Shows your completion percentage for this module",
        lessonStatus: "Green = complete, Yellow = in progress, Gray = not started",
        simulationAttempts: "Number of times you can retry this simulation",
        currentScore: "Your current grade for this activity",
        timeRemaining: "How much time you have left to complete this",
        prerequisiteCheck: "Complete these requirements before proceeding"
    },
    
    // Simulation builder tooltips
    builder: {
        dragComponent: "Drag network devices onto the canvas to build topology",
        connectionTool: "Click two devices to create a connection between them",
        configureDevice: "Double-click any device to configure its settings",
        saveSimulation: "Save your work - students can only access saved simulations",
        previewMode: "Test your simulation as a student would experience it",
        validationRules: "Define what students must accomplish to complete this lab"
    }
};

// Auto-apply common tooltips based on class names and IDs
document.addEventListener('DOMContentLoaded', function() {
    // Apply admin tooltips
    tooltipManager.addTooltip('.class-code-input', RiddleNetTooltips.admin.classCode);
    tooltipManager.addTooltip('.section-input', RiddleNetTooltips.admin.classSection);
    tooltipManager.addTooltip('.module-order-input', RiddleNetTooltips.admin.moduleOrder);
    tooltipManager.addTooltip('.simulation-category-select', RiddleNetTooltips.admin.simulationCategory);
    tooltipManager.addTooltip('.difficulty-select', RiddleNetTooltips.admin.difficultyLevel);
    tooltipManager.addTooltip('.duration-input', RiddleNetTooltips.admin.estimatedDuration);
    tooltipManager.addTooltip('.learning-objectives-textarea', RiddleNetTooltips.admin.learningObjectives);
    tooltipManager.addTooltip('.prerequisites-textarea', RiddleNetTooltips.admin.prerequisites);
    tooltipManager.addTooltip('.is-published-checkbox', RiddleNetTooltips.admin.isPublished);
    tooltipManager.addTooltip('.sequential-completion-checkbox', RiddleNetTooltips.admin.sequentialCompletion);

    // Apply student tooltips
    tooltipManager.addTooltip('.progress-bar', RiddleNetTooltips.student.progressBar);
    tooltipManager.addTooltip('.lesson-status-indicator', RiddleNetTooltips.student.lessonStatus);
    tooltipManager.addTooltip('.simulation-attempts-counter', RiddleNetTooltips.student.simulationAttempts);
    tooltipManager.addTooltip('.current-score-display', RiddleNetTooltips.student.currentScore);

    // Apply simulation builder tooltips
    tooltipManager.addTooltip('.component-item[draggable="true"]', RiddleNetTooltips.builder.dragComponent);
    tooltipManager.addTooltip('.connection-tool', RiddleNetTooltips.builder.connectionTool);
    tooltipManager.addTooltip('.device-config-btn', RiddleNetTooltips.builder.configureDevice);
    tooltipManager.addTooltip('.save-simulation-btn', RiddleNetTooltips.builder.saveSimulation);
    tooltipManager.addTooltip('.preview-simulation-btn', RiddleNetTooltips.builder.previewMode);
});

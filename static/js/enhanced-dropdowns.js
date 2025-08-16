// CSS Styles for Enhanced Dropdowns
const enhancedDropdownStyles = `
<style>
/* Enhanced Dropdown Styles */
.select-with-indicator {
    position: relative;
    display: inline-block;
    width: 100%;
}

.enhanced-select {
    transition: all 0.3s ease;
    border-width: 2px;
}

/* Category-based coloring */
.enhanced-select[data-selected-category="general"],
.select-with-indicator[data-category="general"] .enhanced-select {
    border-color: #8b5cf6 !important;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
}

.enhanced-select[data-selected-category="networking1"],
.select-with-indicator[data-category="networking1"] .enhanced-select {
    border-color: #3b82f6 !important;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
}

.enhanced-select[data-selected-category="networking2"],
.select-with-indicator[data-category="networking2"] .enhanced-select {
    border-color: #10b981 !important;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
}

.enhanced-select[data-selected-category="security"],
.select-with-indicator[data-category="security"] .enhanced-select {
    border-color: #ef4444 !important;
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
}

.enhanced-select[data-selected-category="troubleshooting"],
.select-with-indicator[data-category="troubleshooting"] .enhanced-select {
    border-color: #f59e0b !important;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
}

/* Difficulty-based coloring */
.enhanced-select[data-selected-difficulty="beginner"] {
    border-color: #10b981 !important;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
}

.enhanced-select[data-selected-difficulty="intermediate"] {
    border-color: #f59e0b !important;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
}

.enhanced-select[data-selected-difficulty="advanced"] {
    border-color: #ef4444 !important;
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
}

/* Status-based coloring */
.enhanced-select[data-selected-status="active"] {
    border-color: #10b981 !important;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
}

.enhanced-select[data-selected-status="draft"] {
    border-color: #f59e0b !important;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
}

.enhanced-select[data-selected-status="archived"] {
    border-color: #6b7280 !important;
    background: linear-gradient(135deg, rgba(107, 114, 128, 0.1), rgba(107, 114, 128, 0.05));
}

/* Priority-based coloring */
.enhanced-select[data-selected-priority="high"] {
    border-color: #ef4444 !important;
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
}

.enhanced-select[data-selected-priority="medium"] {
    border-color: #f59e0b !important;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
}

.enhanced-select[data-selected-priority="low"] {
    border-color: #10b981 !important;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
}

/* Category indicator */
.select-with-indicator::before {
    content: '';
    position: absolute;
    left: -8px;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 60%;
    border-radius: 2px;
    background: transparent;
    transition: all 0.3s ease;
    z-index: 1;
}

.select-with-indicator[data-category="general"]::before {
    background: #8b5cf6;
}

.select-with-indicator[data-category="networking1"]::before {
    background: #3b82f6;
}

.select-with-indicator[data-category="networking2"]::before {
    background: #10b981;
}

.select-with-indicator[data-category="security"]::before {
    background: #ef4444;
}

.select-with-indicator[data-category="troubleshooting"]::before {
    background: #f59e0b;
}

/* Option styling within dropdowns */
.enhanced-select option[data-category="general"] {
    background-color: rgba(139, 92, 246, 0.1);
    color: #8b5cf6;
}

.enhanced-select option[data-category="networking1"] {
    background-color: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.enhanced-select option[data-category="networking2"] {
    background-color: rgba(16, 185, 129, 0.1);
    color: #10b981;
}

.enhanced-select option[data-category="security"] {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

.enhanced-select option[data-category="troubleshooting"] {
    background-color: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
}

/* Focus states */
.enhanced-select:focus {
    box-shadow: 0 0 0 3px rgba(var(--cyber-glow-rgb, 0, 217, 255), 0.3);
}

/* Hover effects */
.enhanced-select:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
`;

// Inject styles into the document
function injectEnhancedDropdownStyles() {
    if (!document.getElementById('enhanced-dropdown-styles')) {
        const styleElement = document.createElement('div');
        styleElement.id = 'enhanced-dropdown-styles';
        styleElement.innerHTML = enhancedDropdownStyles;
        document.head.appendChild(styleElement);
    }
}

// Enhanced Dropdown Management
class DropdownEnhancer {
    constructor() {
        this.init();
    }

    init() {
        // Inject styles immediately
        injectEnhancedDropdownStyles();
        
        document.addEventListener('DOMContentLoaded', () => {
            this.enhanceDropdowns();
            this.bindEvents();
        });
    }

    enhanceDropdowns() {
        // Find all dropdowns that need enhancement
        const dropdowns = document.querySelectorAll('select.form-select, select[data-enhance="true"]');
        
        dropdowns.forEach(dropdown => {
            this.enhanceDropdown(dropdown);
        });
    }

    enhanceDropdown(dropdown) {
        // Add enhanced class
        dropdown.classList.add('enhanced-select');
        
        // Add category indicator wrapper
        if (!dropdown.parentElement.classList.contains('select-with-indicator')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'select-with-indicator';
            dropdown.parentNode.insertBefore(wrapper, dropdown);
            wrapper.appendChild(dropdown);
        }

        // Set initial category color
        this.updateDropdownAppearance(dropdown);
    }

    bindEvents() {
        document.addEventListener('change', (event) => {
            if (event.target.matches('select.enhanced-select, select[data-enhance="true"]')) {
                this.updateDropdownAppearance(event.target);
                this.triggerCategoryChange(event.target);
            }
        });
    }

    updateDropdownAppearance(dropdown) {
        const selectedOption = dropdown.options[dropdown.selectedIndex];
        if (!selectedOption) return;

        // Get category, difficulty, status, etc. from selected option
        const category = selectedOption.getAttribute('data-category');
        const difficulty = selectedOption.getAttribute('data-difficulty');
        const status = selectedOption.getAttribute('data-status');
        const type = selectedOption.getAttribute('data-type');
        const priority = selectedOption.getAttribute('data-priority');

        // Update dropdown border color based on selection
        if (category) {
            dropdown.setAttribute('data-selected-category', category);
            dropdown.parentElement.setAttribute('data-category', category);
        }
        if (difficulty) {
            dropdown.setAttribute('data-selected-difficulty', difficulty);
        }
        if (status) {
            dropdown.setAttribute('data-selected-status', status);
        }
        if (type) {
            dropdown.setAttribute('data-selected-type', type);
        }
        if (priority) {
            dropdown.setAttribute('data-selected-priority', priority);
        }
    }

    triggerCategoryChange(dropdown) {
        // Dispatch custom event for other components to listen to
        const event = new CustomEvent('dropdown:categoryChanged', {
            detail: {
                dropdown: dropdown,
                category: dropdown.getAttribute('data-selected-category'),
                difficulty: dropdown.getAttribute('data-selected-difficulty'),
                status: dropdown.getAttribute('data-selected-status'),
                type: dropdown.getAttribute('data-selected-type'),
                priority: dropdown.getAttribute('data-selected-priority')
            }
        });
        dropdown.dispatchEvent(event);
    }

    // Method to programmatically add color-coded options
    addColorCodedOption(dropdown, value, text, attributes = {}) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        
        // Add data attributes for coloring
        Object.entries(attributes).forEach(([key, val]) => {
            option.setAttribute(`data-${key}`, val);
        });
        
        dropdown.appendChild(option);
        return option;
    }

    // Method to populate dropdown with RiddleNet-specific options
    populateDropdown(dropdown, type) {
        const options = this.getOptionsByType(type);
        
        // Clear existing options except first (usually "Select..." option)
        while (dropdown.children.length > 1) {
            dropdown.removeChild(dropdown.lastChild);
        }
        
        options.forEach(option => {
            this.addColorCodedOption(dropdown, option.value, option.text, option.attributes);
        });
    }

    getOptionsByType(type) {
        const optionSets = {
            category: [
                { value: 'general', text: 'General', attributes: { category: 'general' }},
                { value: 'networking1', text: 'Networking 1', attributes: { category: 'networking1' }},
                { value: 'networking2', text: 'Networking 2', attributes: { category: 'networking2' }},
                { value: 'security', text: 'Security', attributes: { category: 'security' }},
                { value: 'troubleshooting', text: 'Troubleshooting', attributes: { category: 'troubleshooting' }}
            ],
            difficulty: [
                { value: 'beginner', text: 'Beginner', attributes: { difficulty: 'beginner' }},
                { value: 'intermediate', text: 'Intermediate', attributes: { difficulty: 'intermediate' }},
                { value: 'advanced', text: 'Advanced', attributes: { difficulty: 'advanced' }}
            ],
            status: [
                { value: 'active', text: 'Active', attributes: { status: 'active' }},
                { value: 'draft', text: 'Draft', attributes: { status: 'draft' }},
                { value: 'archived', text: 'Archived', attributes: { status: 'archived' }}
            ],
            contentType: [
                { value: 'lesson', text: 'Lesson', attributes: { type: 'lesson' }},
                { value: 'simulation', text: 'Simulation', attributes: { type: 'simulation' }},
                { value: 'assessment', text: 'Assessment', attributes: { type: 'assessment' }},
                { value: 'lab', text: 'Lab', attributes: { type: 'lab' }}
            ],
            priority: [
                { value: 'high', text: 'High Priority', attributes: { priority: 'high' }},
                { value: 'medium', text: 'Medium Priority', attributes: { priority: 'medium' }},
                { value: 'low', text: 'Low Priority', attributes: { priority: 'low' }}
            ]
        };
        
        return optionSets[type] || [];
    }
}

// Initialize dropdown enhancer
const dropdownEnhancer = new DropdownEnhancer();

// Export for global use
window.dropdownEnhancer = dropdownEnhancer;

// Utility functions for easy integration
window.RiddleNetDropdowns = {
    // Quick method to enhance a specific dropdown
    enhance: (selector) => {
        const dropdown = document.querySelector(selector);
        if (dropdown) {
            dropdownEnhancer.enhanceDropdown(dropdown);
        }
    },
    
    // Quick method to populate dropdown with standard options
    populate: (selector, type) => {
        const dropdown = document.querySelector(selector);
        if (dropdown) {
            dropdownEnhancer.populateDropdown(dropdown, type);
        }
    },
    
    // Listen for category changes
    onCategoryChange: (callback) => {
        document.addEventListener('dropdown:categoryChanged', callback);
    },
    
    // Initialize styles
    initStyles: injectEnhancedDropdownStyles
};

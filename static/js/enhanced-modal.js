/**
 * Enhanced Modal System for RiddleNet
 * Modern, accessible, and feature-rich modal functionality
 */

class EnhancedModal {
    constructor(modalId, options = {}) {
        this.modalId = modalId;
        this.modal = document.getElementById(modalId);
        this.options = {
            closeOnBackdrop: true,
            closeOnEscape: true,
            showAnimation: true,
            blurBackground: true,
            disableScroll: true,
            autoFocus: true,
            ...options
        };
        
        this.isOpen = false;
        this.previousFocus = null;
        
        this.init();
    }
    
    init() {
        if (!this.modal) {
            console.warn(`Modal with ID '${this.modalId}' not found`);
            return;
        }
        
        this.setupEventListeners();
        this.setupAccessibility();
    }
    
    setupEventListeners() {
        // Close button listeners
        const closeButtons = this.modal.querySelectorAll('.close, .close-modal, [data-modal-close]');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', () => this.close());
        });
        
        // Backdrop click listener
        if (this.options.closeOnBackdrop) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.close();
                }
            });
        }
        
        // Escape key listener
        if (this.options.closeOnEscape) {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });
        }
        
        // Prevent modal content from closing when clicked
        const modalContent = this.modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
    }
    
    setupAccessibility() {
        // Add ARIA attributes
        this.modal.setAttribute('role', 'dialog');
        this.modal.setAttribute('aria-modal', 'true');
        
        // Add aria-labelledby if header exists
        const header = this.modal.querySelector('.modal-header h2, .modal-header h3');
        if (header && !header.id) {
            header.id = `${this.modalId}-title`;
            this.modal.setAttribute('aria-labelledby', header.id);
        }
        
        // Add aria-describedby if body exists
        const body = this.modal.querySelector('.modal-body');
        if (body && !body.id) {
            body.id = `${this.modalId}-description`;
            this.modal.setAttribute('aria-describedby', body.id);
        }
    }
    
    open() {
        if (this.isOpen) return;
        
        // Store current focus
        this.previousFocus = document.activeElement;
        
        // Disable background scroll
        if (this.options.disableScroll) {
            document.body.classList.add('modal-no-scroll');
        }
        
        // Blur background
        if (this.options.blurBackground) {
            const mainContent = document.querySelector('main, .main-content, .page-container');
            if (mainContent) {
                mainContent.classList.add('modal-blur-background');
            }
        }
        
        // Show modal
        this.modal.style.display = 'flex';
        this.modal.classList.add('active');
        
        // Focus management
        if (this.options.autoFocus) {
            setTimeout(() => {
                const focusTarget = this.modal.querySelector('[autofocus], .modal-header, .modal-body');
                if (focusTarget) {
                    focusTarget.focus();
                }
            }, 100);
        }
        
        // Trap focus within modal
        this.trapFocus();
        
        this.isOpen = true;
        this.onOpen();
    }
    
    close() {
        if (!this.isOpen) return;
        
        // Remove active class for animation
        this.modal.classList.remove('active');
        
        // Wait for animation to complete
        setTimeout(() => {
            this.modal.style.display = 'none';
            
            // Re-enable background scroll
            document.body.classList.remove('modal-no-scroll');
            
            // Remove background blur
            const mainContent = document.querySelector('main, .main-content, .page-container');
            if (mainContent) {
                mainContent.classList.remove('modal-blur-background');
            }
            
            // Restore focus
            if (this.previousFocus) {
                this.previousFocus.focus();
            }
            
            this.isOpen = false;
            this.onClose();
        }, 300);
    }
    
    trapFocus() {
        const focusableElements = this.modal.querySelectorAll(
            'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        this.modal.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }
    
    // Event hooks
    onOpen() {
        // Override in subclasses or set via options
        if (this.options.onOpen) {
            this.options.onOpen();
        }
    }
    
    onClose() {
        // Override in subclasses or set via options
        if (this.options.onClose) {
            this.options.onClose();
        }
    }
    
    // Utility methods
    setContent(content) {
        const body = this.modal.querySelector('.modal-body');
        if (body) {
            body.innerHTML = content;
        }
    }
    
    setTitle(title) {
        const titleElement = this.modal.querySelector('.modal-header h2, .modal-header h3');
        if (titleElement) {
            titleElement.textContent = title;
        }
    }
    
    addLoading() {
        const body = this.modal.querySelector('.modal-body');
        if (body) {
            body.classList.add('modal-loading');
            body.innerHTML = '';
        }
    }
    
    removeLoading() {
        const body = this.modal.querySelector('.modal-body');
        if (body) {
            body.classList.remove('modal-loading');
        }
    }
    
    setType(type) {
        // Remove existing type classes
        this.modal.classList.remove('modal-success', 'modal-error', 'tutorial-modal', 'form-modal', 'large-modal');
        
        // Add new type class
        if (type) {
            this.modal.classList.add(`modal-${type}`);
        }
    }
}

// Global modal management
class ModalManager {
    constructor() {
        this.modals = new Map();
        this.init();
    }
    
    init() {
        // Auto-initialize modals with data-modal attribute
        document.addEventListener('DOMContentLoaded', () => {
            this.autoInitialize();
            this.setupGlobalListeners();
        });
    }
    
    autoInitialize() {
        const modalElements = document.querySelectorAll('[data-modal]');
        modalElements.forEach(element => {
            const modalId = element.getAttribute('data-modal');
            const options = this.parseOptions(element);
            this.register(modalId, options);
        });
    }
    
    parseOptions(element) {
        const options = {};
        
        // Parse data attributes
        if (element.hasAttribute('data-modal-backdrop')) {
            options.closeOnBackdrop = element.getAttribute('data-modal-backdrop') !== 'false';
        }
        if (element.hasAttribute('data-modal-keyboard')) {
            options.closeOnEscape = element.getAttribute('data-modal-keyboard') !== 'false';
        }
        if (element.hasAttribute('data-modal-blur')) {
            options.blurBackground = element.getAttribute('data-modal-blur') !== 'false';
        }
        
        return options;
    }
    
    setupGlobalListeners() {
        // Handle data-modal-target clicks
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-modal-target]');
            if (trigger) {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal-target');
                this.open(modalId);
            }
        });
    }
    
    register(modalId, options = {}) {
        if (!this.modals.has(modalId)) {
            const modal = new EnhancedModal(modalId, options);
            this.modals.set(modalId, modal);
        }
        return this.modals.get(modalId);
    }
    
    open(modalId, options = {}) {
        let modal = this.modals.get(modalId);
        if (!modal) {
            modal = this.register(modalId, options);
        }
        modal.open();
        return modal;
    }
    
    close(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.close();
        }
    }
    
    closeAll() {
        this.modals.forEach(modal => {
            if (modal.isOpen) {
                modal.close();
            }
        });
    }
    
    get(modalId) {
        return this.modals.get(modalId);
    }
}

// Tutorial Modal specialized class
class TutorialModal extends EnhancedModal {
    constructor(modalId, steps = [], options = {}) {
        super(modalId, {
            closeOnBackdrop: false,
            closeOnEscape: true,
            ...options
        });
        
        this.steps = steps;
        this.currentStep = 0;
        this.setupTutorial();
    }
    
    setupTutorial() {
        this.modal.classList.add('tutorial-modal');
        this.createTutorialNavigation();
    }
    
    createTutorialNavigation() {
        const footer = this.modal.querySelector('.modal-footer');
        if (footer) {
            footer.innerHTML = `
                <div class="tutorial-progress">
                    <span class="step-counter">Step <span class="current-step">1</span> of <span class="total-steps">${this.steps.length}</span></span>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
                <div class="tutorial-buttons">
                    <button class="btn btn-secondary" id="tutorial-prev" disabled>Previous</button>
                    <button class="btn btn-primary" id="tutorial-next">Next</button>
                    <button class="btn btn-success" id="tutorial-finish" style="display: none;">Finish</button>
                </div>
            `;
            
            this.setupTutorialButtons();
        }
    }
    
    setupTutorialButtons() {
        const prevBtn = this.modal.querySelector('#tutorial-prev');
        const nextBtn = this.modal.querySelector('#tutorial-next');
        const finishBtn = this.modal.querySelector('#tutorial-finish');
        
        prevBtn?.addEventListener('click', () => this.previousStep());
        nextBtn?.addEventListener('click', () => this.nextStep());
        finishBtn?.addEventListener('click', () => this.close());
    }
    
    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) return;
        
        this.currentStep = stepIndex;
        const step = this.steps[stepIndex];
        
        // Update content
        this.setTitle(step.title);
        this.setContent(step.content);
        
        // Update navigation
        this.updateTutorialNavigation();
        
        // Highlight target element if specified
        if (step.target) {
            this.highlightElement(step.target);
        }
    }
    
    updateTutorialNavigation() {
        const currentStepSpan = this.modal.querySelector('.current-step');
        const progressFill = this.modal.querySelector('.progress-fill');
        const prevBtn = this.modal.querySelector('#tutorial-prev');
        const nextBtn = this.modal.querySelector('#tutorial-next');
        const finishBtn = this.modal.querySelector('#tutorial-finish');
        
        if (currentStepSpan) {
            currentStepSpan.textContent = this.currentStep + 1;
        }
        
        if (progressFill) {
            const progress = ((this.currentStep + 1) / this.steps.length) * 100;
            progressFill.style.width = `${progress}%`;
        }
        
        if (prevBtn) {
            prevBtn.disabled = this.currentStep === 0;
        }
        
        if (nextBtn && finishBtn) {
            if (this.currentStep === this.steps.length - 1) {
                nextBtn.style.display = 'none';
                finishBtn.style.display = 'inline-block';
            } else {
                nextBtn.style.display = 'inline-block';
                finishBtn.style.display = 'none';
            }
        }
    }
    
    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.showStep(this.currentStep + 1);
        }
    }
    
    previousStep() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }
    
    highlightElement(selector) {
        // Remove previous highlights
        document.querySelectorAll('.tutorial-highlight').forEach(el => {
            el.classList.remove('tutorial-highlight');
        });
        
        // Add new highlight
        const target = document.querySelector(selector);
        if (target) {
            target.classList.add('tutorial-highlight');
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    start() {
        this.open();
        this.showStep(0);
    }
}

// Initialize global modal manager
const modalManager = new ModalManager();

// Export for global use
window.EnhancedModal = EnhancedModal;
window.TutorialModal = TutorialModal;
window.modalManager = modalManager;

// Global utility functions
window.openModal = (modalId, options) => modalManager.open(modalId, options);
window.closeModal = (modalId) => modalManager.close(modalId);
window.showTutorial = (steps, modalId = 'tutorialModal') => {
    const tutorial = new TutorialModal(modalId, steps);
    tutorial.start();
    return tutorial;
};

/**
 * Password Strength Validator
 * Provides real-time password validation with visual feedback
 */

class PasswordValidator {
    constructor() {
        this.minLength = 8;
        this.specialChars = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/;
    }

    /**
     * Validate password against all requirements
     * @param {string} password - The password to validate
     * @returns {Object} Validation result with requirements status
     */
    validate(password) {
        const requirements = {
            length: password.length >= this.minLength,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            number: /\d/.test(password),
            special: this.specialChars.test(password)
        };

        const errors = [];
        if (!requirements.length) {
            errors.push(`Password must be at least ${this.minLength} characters long`);
        }
        if (!requirements.lowercase) {
            errors.push('Password must contain at least one lowercase letter (a-z)');
        }
        if (!requirements.uppercase) {
            errors.push('Password must contain at least one uppercase letter (A-Z)');
        }
        if (!requirements.number) {
            errors.push('Password must contain at least one number (0-9)');
        }
        if (!requirements.special) {
            errors.push('Password must contain at least one special character (!@#$%^&*)');
        }

        const isValid = Object.values(requirements).every(req => req === true);

        return {
            isValid,
            requirements,
            errors,
            strength: this.calculateStrength(requirements),
            score: this.calculateScore(requirements)
        };
    }

    /**
     * Calculate password strength level
     * @param {Object} requirements - Requirements object
     * @returns {string} Strength level: 'weak', 'medium', or 'strong'
     */
    calculateStrength(requirements) {
        const metCount = Object.values(requirements).filter(req => req).length;
        
        if (metCount === 5) return 'strong';
        if (metCount >= 3) return 'medium';
        return 'weak';
    }

    /**
     * Calculate password score (0-100)
     * @param {Object} requirements - Requirements object
     * @returns {number} Score from 0 to 100
     */
    calculateScore(requirements) {
        const metCount = Object.values(requirements).filter(req => req).length;
        return (metCount / 5) * 100;
    }

    /**
     * Get list of password requirements
     * @returns {Array} Array of requirement strings
     */
    getRequirements() {
        return [
            `At least ${this.minLength} characters long`,
            'At least one lowercase letter (a-z)',
            'At least one uppercase letter (A-Z)',
            'At least one number (0-9)',
            'At least one special character (!@#$%^&*)'
        ];
    }
}

/**
 * Password Strength UI Component
 * Manages the visual display of password validation feedback
 */
class PasswordStrengthUI {
    constructor(passwordInput, options = {}) {
        this.passwordInput = passwordInput;
        this.validator = new PasswordValidator();
        
        // Configuration options
        this.options = {
            showStrengthMeter: options.showStrengthMeter !== false,
            showRequirementsList: options.showRequirementsList !== false,
            showErrors: options.showErrors !== false,
            containerClass: options.containerClass || 'password-strength-container',
            updateOnInput: options.updateOnInput !== false,
            preventSubmitOnInvalid: options.preventSubmitOnInvalid !== false
        };

        this.init();
    }

    /**
     * Initialize the password strength UI
     */
    init() {
        if (!this.passwordInput) {
            console.error('Password input element not found');
            return;
        }

        this.createUI();
        this.attachEventListeners();
    }

    /**
     * Create the UI elements for password validation
     */
    createUI() {
        // Create main container
        this.container = document.createElement('div');
        this.container.className = this.options.containerClass;

        // Create strength meter
        if (this.options.showStrengthMeter) {
            this.strengthMeter = this.createStrengthMeter();
            this.container.appendChild(this.strengthMeter);
        }

        // Create requirements list
        if (this.options.showRequirementsList) {
            this.requirementsList = this.createRequirementsList();
            this.container.appendChild(this.requirementsList);
        }

        // Create error message container
        if (this.options.showErrors) {
            this.errorContainer = document.createElement('div');
            this.errorContainer.className = 'password-error-message';
            this.errorContainer.style.display = 'none';
            this.container.appendChild(this.errorContainer);
        }

        // Insert container after the password input
        this.passwordInput.parentNode.insertBefore(
            this.container,
            this.passwordInput.nextSibling
        );
    }

    /**
     * Create strength meter element
     */
    createStrengthMeter() {
        const meterWrapper = document.createElement('div');
        meterWrapper.className = 'password-strength-meter';
        meterWrapper.innerHTML = `
            <div class="strength-meter-bar">
                <div class="strength-meter-fill"></div>
            </div>
            <div class="strength-meter-text">Password Strength: <span class="strength-level">-</span></div>
        `;
        return meterWrapper;
    }

    /**
     * Create requirements checklist
     */
    createRequirementsList() {
        const list = document.createElement('ul');
        list.className = 'password-requirements-list';
        
        const requirements = this.validator.getRequirements();
        requirements.forEach((req, index) => {
            const li = document.createElement('li');
            li.className = 'requirement-item';
            li.setAttribute('data-requirement', this.getRequirementKey(index));
            li.innerHTML = `
                <i class="requirement-icon fas fa-circle"></i>
                <span class="requirement-text">${req}</span>
            `;
            list.appendChild(li);
        });

        return list;
    }

    /**
     * Get requirement key by index
     */
    getRequirementKey(index) {
        const keys = ['length', 'lowercase', 'uppercase', 'number', 'special'];
        return keys[index];
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        if (this.options.updateOnInput) {
            this.passwordInput.addEventListener('input', () => {
                this.updateUI();
            });
        }

        // Prevent form submission if password is invalid
        if (this.options.preventSubmitOnInvalid) {
            const form = this.passwordInput.closest('form');
            if (form) {
                form.addEventListener('submit', (e) => {
                    const result = this.validator.validate(this.passwordInput.value);
                    if (!result.isValid) {
                        e.preventDefault();
                        this.showErrors(result.errors);
                    }
                });
            }
        }
    }

    /**
     * Update UI based on password input
     */
    updateUI() {
        const password = this.passwordInput.value;
        const result = this.validator.validate(password);

        // Update strength meter
        if (this.options.showStrengthMeter) {
            this.updateStrengthMeter(result.strength, result.score);
        }

        // Update requirements list
        if (this.options.showRequirementsList) {
            this.updateRequirementsList(result.requirements);
        }

        // Hide errors when typing (show on submit attempt)
        if (this.options.showErrors && this.errorContainer) {
            this.errorContainer.style.display = 'none';
        }

        return result;
    }

    /**
     * Update strength meter display
     */
    updateStrengthMeter(strength, score) {
        const fill = this.strengthMeter.querySelector('.strength-meter-fill');
        const levelText = this.strengthMeter.querySelector('.strength-level');

        // Update fill width
        fill.style.width = `${score}%`;

        // Update colors and text based on strength
        fill.className = 'strength-meter-fill';
        if (strength === 'strong') {
            fill.classList.add('strength-strong');
            levelText.textContent = 'Strong';
            levelText.className = 'strength-level strength-strong';
        } else if (strength === 'medium') {
            fill.classList.add('strength-medium');
            levelText.textContent = 'Medium';
            levelText.className = 'strength-level strength-medium';
        } else {
            fill.classList.add('strength-weak');
            levelText.textContent = 'Weak';
            levelText.className = 'strength-level strength-weak';
        }
    }

    /**
     * Update requirements list display
     */
    updateRequirementsList(requirements) {
        Object.entries(requirements).forEach(([key, met]) => {
            const item = this.requirementsList.querySelector(`[data-requirement="${key}"]`);
            if (item) {
                const icon = item.querySelector('.requirement-icon');
                if (met) {
                    item.classList.add('requirement-met');
                    item.classList.remove('requirement-unmet');
                    icon.className = 'requirement-icon fas fa-check-circle';
                } else {
                    item.classList.add('requirement-unmet');
                    item.classList.remove('requirement-met');
                    icon.className = 'requirement-icon fas fa-circle';
                }
            }
        });
    }

    /**
     * Show error messages
     */
    showErrors(errors) {
        if (!this.options.showErrors || !this.errorContainer) return;

        if (errors.length > 0) {
            this.errorContainer.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                <span>${errors[0]}</span>
            `;
            this.errorContainer.style.display = 'block';
        } else {
            this.errorContainer.style.display = 'none';
        }
    }

    /**
     * Validate password and return result
     */
    validate() {
        return this.validator.validate(this.passwordInput.value);
    }

    /**
     * Destroy the UI component
     */
    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PasswordValidator, PasswordStrengthUI };
}

/**
 * Dynamic User Creation Form Handler
 * Handles the multi-step user creation process with validation and AJAX submission
 */

// Global variables
let currentStep = 1;
let selectedUserType = null;
let totpSecret = null;

// User type selection
function selectUserType(type) {
    selectedUserType = type;
    
    // Update sidebar cards
    document.querySelectorAll('.user-type-card').forEach(card => {
        card.classList.remove('active');
    });
    document.querySelector(`[data-type="${type}"]`).classList.add('active');
    
    // Update form
    document.getElementById('userType').value = type;
    
    // Show/hide class assignments based on user type
    const classAssignments = document.getElementById('classAssignments');
    if (type === 'instructor') {
        classAssignments.style.display = '';
        loadAvailableClasses();
    } else {
        classAssignments.style.display = 'none';
    }
    
    // Auto-advance to next step if all basic info is filled
    if (validateBasicInfo()) {
        setTimeout(() => nextStep(2), 500);
    }
}

// Step navigation with animation
function nextStep(step) {
    if (validateCurrentStep()) {
        // Add completion animation
        const currentStepElement = document.getElementById(`step${currentStep}`);
        currentStepElement.style.transform = 'scale(1.1)';
        
        setTimeout(() => {
            // Hide current step
            document.getElementById(`formStep${currentStep}`).classList.remove('active');
            currentStepElement.classList.remove('active');
            currentStepElement.classList.add('completed');
            currentStepElement.style.transform = 'scale(1)';
            
            // Show next step
            currentStep = step;
            document.getElementById(`formStep${currentStep}`).classList.add('active');
            document.getElementById(`step${currentStep}`).classList.add('active');
            
            // Special handling for step 2 (generate TOTP if enabled)
            if (step === 2) {
                setupTwoFactorAuth();
            }
            
            // Scroll to top of form
            document.querySelector('.main-form-area').scrollTop = 0;
        }, 200);
    }
}

function previousStep(step) {
    // Hide current step
    document.getElementById(`formStep${currentStep}`).classList.remove('active');
    document.getElementById(`step${currentStep}`).classList.remove('active');
    
    // Show previous step
    currentStep = step;
    document.getElementById(`formStep${currentStep}`).classList.add('active');
    document.getElementById(`step${currentStep}`).classList.add('active');
    document.getElementById(`step${currentStep}`).classList.remove('completed');
    
    // Scroll to top of form
    document.querySelector('.main-form-area').scrollTop = 0;
}

// Enhanced form validation
function validateCurrentStep() {
    const step = currentStep;
    let isValid = true;
    
    // Clear previous errors
    clearErrors();
    
    if (step === 1) {
        isValid = validateBasicInfo();
    } else if (step === 2) {
        isValid = validateSecuritySettings();
    } else if (step === 3) {
        isValid = validateAccountSettings();
    }
    
    return isValid;
}

function validateBasicInfo() {
    let isValid = true;
    
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const userType = document.getElementById('userType').value;
    
    if (!userType) {
        showFieldError('userType', 'Please select a user type');
        isValid = false;
    }
    
    if (!username) {
        showFieldError('username', 'Username is required');
        isValid = false;
    } else if (!isValidUsername(username)) {
        showFieldError('username', 'Username can only contain letters, numbers, dots, hyphens, and underscores');
        isValid = false;
    } else {
        // Check username availability (async)
        checkUsernameAvailability(username);
    }
    
    if (!email) {
        showFieldError('email', 'Email address is required');
        isValid = false;
    } else if (!isValidEmail(email)) {
        showFieldError('email', 'Please enter a valid email address');
        isValid = false;
    } else {
        // Check email availability (async)
        checkEmailAvailability(email);
    }
    
    if (!firstName) {
        showFieldError('firstName', 'First name is required');
        isValid = false;
    }
    
    if (!lastName) {
        showFieldError('lastName', 'Last name is required');
        isValid = false;
    }
    
    return isValid;
}

function validateSecuritySettings() {
    let isValid = true;
    
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (!password) {
        showFieldError('password', 'Password is required');
        isValid = false;
    } else if (!isStrongPassword(password)) {
        showFieldError('password', 'Password does not meet security requirements');
        isValid = false;
    }
    
    if (!confirmPassword) {
        showFieldError('confirmPassword', 'Please confirm your password');
        isValid = false;
    } else if (password !== confirmPassword) {
        showFieldError('confirmPassword', 'Passwords do not match');
        isValid = false;
    }
    
    return isValid;
}

function validateAccountSettings() {
    let isValid = true;
    
    const status = document.getElementById('status').value;
    if (!status) {
        showFieldError('status', 'Please select an account status');
        isValid = false;
    }
    
    // Additional validation for instructor class assignments
    if (selectedUserType === 'instructor') {
        const assignedClasses = document.getElementById('assignedClasses');
        if (assignedClasses.selectedOptions.length === 0) {
            showNotification('No classes assigned to instructor', 'warning');
        }
    }
    
    return isValid;
}

// Validation helpers
function isValidUsername(username) {
    return /^[a-zA-Z0-9_.-]+$/.test(username) && username.length >= 3;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isStrongPassword(password) {
    return password.length >= 8 && 
           /[A-Z]/.test(password) && 
           /[a-z]/.test(password) && 
           /[0-9]/.test(password);
}

// Async validation functions
async function checkUsernameAvailability(username) {
    try {
        const response = await fetch('/admin/users/check-username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username })
        });
        
        const data = await response.json();
        
        if (!data.available) {
            showFieldError('username', 'Username already exists');
            return false;
        } else {
            showFieldSuccess('username', 'Username is available');
            return true;
        }
    } catch (error) {
        console.error('Error checking username:', error);
        return true; // Allow to proceed if check fails
    }
}

async function checkEmailAvailability(email) {
    try {
        const response = await fetch('/admin/users/check-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (!data.available) {
            showFieldError('email', 'Email address already exists');
            return false;
        } else {
            showFieldSuccess('email', 'Email is available');
            return true;
        }
    } catch (error) {
        console.error('Error checking email:', error);
        return true; // Allow to proceed if check fails
    }
}

// Error and success display functions
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const formGroup = field.closest('.form-group');
    
    // Remove any existing success state
    formGroup.classList.remove('success');
    formGroup.classList.add('error');
    
    // Create or update error message
    let errorDiv = formGroup.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i><span></span>';
        formGroup.appendChild(errorDiv);
    }
    
    errorDiv.querySelector('span').textContent = message;
    errorDiv.style.display = 'flex';
    
    // Add shake animation
    field.style.animation = 'shake 0.5s ease-in-out';
    setTimeout(() => {
        field.style.animation = '';
    }, 500);
}

function showFieldSuccess(fieldId, message) {
    const field = document.getElementById(fieldId);
    const formGroup = field.closest('.form-group');
    
    // Remove any existing error state
    formGroup.classList.remove('error');
    formGroup.classList.add('success');
    
    // Create or update success message
    let successDiv = formGroup.querySelector('.success-message');
    if (!successDiv) {
        successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = '<i class="fas fa-check-circle"></i><span></span>';
        formGroup.appendChild(successDiv);
    }
    
    successDiv.querySelector('span').textContent = message;
    successDiv.style.display = 'flex';
    
    // Hide any existing error message
    const errorDiv = formGroup.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function clearErrors() {
    document.querySelectorAll('.form-group').forEach(group => {
        group.classList.remove('error', 'success');
    });
    
    document.querySelectorAll('.error-message').forEach(error => {
        error.style.display = 'none';
    });
    
    document.querySelectorAll('.success-message').forEach(success => {
        success.style.display = 'none';
    });
}

// Password strength indicator with real-time updates
function updatePasswordStrength() {
    const password = document.getElementById('password').value;
    const strengthFill = document.getElementById('passwordStrengthFill');
    
    // Reset all requirements
    document.querySelectorAll('.requirement').forEach(req => {
        req.classList.remove('met');
        req.querySelector('i').className = 'fas fa-times';
    });
    
    let score = 0;
    const requirements = [
        { id: 'req-length', test: () => password.length >= 8 },
        { id: 'req-upper', test: () => /[A-Z]/.test(password) },
        { id: 'req-lower', test: () => /[a-z]/.test(password) },
        { id: 'req-number', test: () => /[0-9]/.test(password) }
    ];
    
    requirements.forEach(req => {
        if (req.test()) {
            const element = document.getElementById(req.id);
            element.classList.add('met');
            element.querySelector('i').className = 'fas fa-check';
            score++;
        }
    });
    
    // Update strength bar with animation
    strengthFill.className = 'strength-fill';
    strengthFill.style.width = '0%';
    
    setTimeout(() => {
        if (score === 1) {
            strengthFill.classList.add('strength-weak');
        } else if (score === 2 || score === 3) {
            strengthFill.classList.add('strength-medium');
        } else if (score === 4) {
            strengthFill.classList.add('strength-strong');
        }
    }, 100);
}

// Two-factor authentication setup
function setupTwoFactorAuth() {
    const enableTwoFactor = document.getElementById('enableTwoFactor');
    const totpSetup = document.getElementById('totpSetup');
    
    enableTwoFactor.addEventListener('change', function() {
        if (this.checked) {
            totpSetup.style.display = 'block';
            generateTOTPSecret();
        } else {
            totpSetup.style.display = 'none';
            totpSecret = null;
        }
    });
}

async function generateTOTPSecret() {
    try {
        const response = await fetch('/admin/users/generate-totp-secret', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            totpSecret = data.secret;
            displayQRCode(data.qr_code_url, data.secret);
        } else {
            showNotification('Failed to generate 2FA secret', 'error');
        }
    } catch (error) {
        console.error('Error generating TOTP secret:', error);
        // Fallback to client-side generation
        generateQRCodeFallback();
    }
}

function displayQRCode(qrCodeUrl, secret) {
    const qrContainer = document.getElementById('qrCodeContainer');
    qrContainer.innerHTML = `
        <img src="${qrCodeUrl}" alt="QR Code for 2FA Setup" style="width: 200px; height: 200px;">
        <p style="margin-top: 1rem; font-family: monospace; color: #333; font-size: 0.9rem; word-break: break-all;">
            Secret: ${secret}
        </p>
    `;
}

function generateQRCodeFallback() {
    // Fallback when server-side generation fails
    const qrContainer = document.getElementById('qrCodeContainer');
    const secret = 'JBSWY3DPEHPK3PXP'; // This should be dynamically generated
    totpSecret = secret;
    
    qrContainer.innerHTML = `
        <div style="width: 200px; height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; margin: 0 auto; border-radius: 8px;">
            <i class="fas fa-qrcode" style="font-size: 4rem; color: #333;"></i>
        </div>
        <p style="margin-top: 1rem; font-family: monospace; color: #333; font-size: 0.9rem;">
            Secret: ${secret}
        </p>
        <p style="margin-top: 0.5rem; font-size: 0.8rem; color: #666;">
            QR code generation failed. Please enter the secret manually in your authenticator app.
        </p>
    `;
}

// Load available classes for instructor assignment
async function loadAvailableClasses() {
    try {
        const response = await fetch('/admin/users/available-classes');
        const data = await response.json();
        
        const classSelect = document.getElementById('assignedClasses');
        classSelect.innerHTML = '';
        
        if (data.classes && data.classes.length > 0) {
            data.classes.forEach(cls => {
                const option = document.createElement('option');
                option.value = cls.id;
                option.textContent = cls.name;
                classSelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No classes available';
            option.disabled = true;
            classSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading classes:', error);
        // Fallback to sample data
        loadSampleClasses();
    }
}

function loadSampleClasses() {
    const classSelect = document.getElementById('assignedClasses');
    const sampleClasses = [
        { id: 1, name: 'Networking Fundamentals' },
        { id: 2, name: 'Advanced Routing' },
        { id: 3, name: 'Network Security' },
        { id: 4, name: 'Wireless Technologies' }
    ];
    
    classSelect.innerHTML = '';
    sampleClasses.forEach(cls => {
        const option = document.createElement('option');
        option.value = cls.id;
        option.textContent = cls.name;
        classSelect.appendChild(option);
    });
}

// Form submission with enhanced error handling
async function submitUserCreationForm(formData) {
    try {
        showLoading();
        
        // Add TOTP secret if 2FA is enabled
        if (totpSecret) {
            formData.append('totp_secret', totpSecret);
        }
        
        const response = await fetch('/admin/users/create-new-user', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showSuccess();
            setTimeout(() => {
                window.location.href = data.redirect || '/admin/users/';
            }, 2000);
        } else {
            hideLoading();
            showNotification(data.message || 'Failed to create user', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Error creating user:', error);
        showNotification('An unexpected error occurred. Please try again.', 'error');
    }
}

// UI feedback functions
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('createUserBtn').disabled = true;
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
    document.getElementById('createUserBtn').disabled = false;
}

function showSuccess() {
    document.getElementById('loadingOverlay').style.display = 'none';
    document.getElementById('successOverlay').style.display = 'flex';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--card-bg);
        color: var(--text-primary);
        padding: 16px 20px;
        border-radius: 12px;
        border-left: 4px solid var(--${type === 'success' ? 'success' : type === 'error' ? 'error' : 'cyber'}-color);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Form cancellation
function cancelCreation() {
    if (confirm('Are you sure you want to cancel user creation? All entered data will be lost.')) {
        window.location.href = '/admin/users/';
    }
}

// Event listeners and initialization
document.addEventListener('DOMContentLoaded', function() {
    // Password strength checker with debouncing
    let passwordTimeout;
    document.getElementById('password').addEventListener('input', function() {
        clearTimeout(passwordTimeout);
        passwordTimeout = setTimeout(updatePasswordStrength, 200);
    });
    
    // Real-time username validation
    let usernameTimeout;
    document.getElementById('username').addEventListener('input', function() {
        clearTimeout(usernameTimeout);
        const username = this.value.trim();
        
        if (username.length >= 3) {
            usernameTimeout = setTimeout(() => checkUsernameAvailability(username), 500);
        }
        
        // Clear previous errors
        this.closest('.form-group').classList.remove('error');
        const errorMsg = this.closest('.form-group').querySelector('.error-message');
        if (errorMsg) errorMsg.style.display = 'none';
    });
    
    // Real-time email validation
    let emailTimeout;
    document.getElementById('email').addEventListener('input', function() {
        clearTimeout(emailTimeout);
        const email = this.value.trim();
        
        if (isValidEmail(email)) {
            emailTimeout = setTimeout(() => checkEmailAvailability(email), 500);
        }
        
        // Clear previous errors
        this.closest('.form-group').classList.remove('error');
        const errorMsg = this.closest('.form-group').querySelector('.error-message');
        if (errorMsg) errorMsg.style.display = 'none';
    });
    
    // Password confirmation validation
    document.getElementById('confirmPassword').addEventListener('input', function() {
        const password = document.getElementById('password').value;
        const confirmPassword = this.value;
        
        const formGroup = this.closest('.form-group');
        formGroup.classList.remove('error', 'success');
        
        if (confirmPassword && password === confirmPassword) {
            showFieldSuccess('confirmPassword', 'Passwords match');
        } else if (confirmPassword && password !== confirmPassword) {
            showFieldError('confirmPassword', 'Passwords do not match');
        }
    });
    
    // User type change handler
    document.getElementById('userType').addEventListener('change', function() {
        if (this.value) {
            selectUserType(this.value);
        }
    });
    
    // Form submission handler
    document.getElementById('userCreationForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateCurrentStep()) {
            const formData = new FormData(this);
            submitUserCreationForm(formData);
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // ESC to cancel
        if (e.key === 'Escape') {
            cancelCreation();
        }
        
        // Enter to proceed to next step (except in textareas)
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            if (currentStep < 3) {
                nextStep(currentStep + 1);
            }
        }
    });
    
    // Auto-save form data to localStorage
    const formInputs = document.querySelectorAll('#userCreationForm input, #userCreationForm select, #userCreationForm textarea');
    formInputs.forEach(input => {
        // Load saved data
        const savedValue = localStorage.getItem(`userForm_${input.name}`);
        if (savedValue && input.type !== 'password') {
            input.value = savedValue;
        }
        
        // Save data on change
        input.addEventListener('change', function() {
            if (this.type !== 'password') {
                localStorage.setItem(`userForm_${this.name}`, this.value);
            }
        });
    });
    
    // Clear localStorage on successful submission
    window.addEventListener('beforeunload', function() {
        if (document.getElementById('successOverlay').style.display === 'flex') {
            formInputs.forEach(input => {
                localStorage.removeItem(`userForm_${input.name}`);
            });
        }
    });
});

// Add CSS for shake animation
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(shakeStyle);

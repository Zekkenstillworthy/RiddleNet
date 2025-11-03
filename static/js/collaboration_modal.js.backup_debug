/**
 * Collaboration Modal Management
 * MVP functionality for managing collaboration settings
 */

// Global collaboration modal state
let collaborationModalState = {
    isOpen: false,
    currentSettings: {},
    hasUnsavedChanges: false
};

/**
 * Open the collaboration modal
 */
function openCollaborationModal() {
    const modal = document.getElementById('collaboration-modal');
    if (!modal) {
        console.error('Collaboration modal element not found');
        return;
    }

    // Show modal
    modal.classList.add('active');
    modal.style.display = 'flex';
    
    // Prevent body scroll
    document.body.classList.add('modal-no-scroll');
    
    // Load current settings
    loadCollaborationSettings();
    
    // Update state
    collaborationModalState.isOpen = true;
    collaborationModalState.hasUnsavedChanges = false;
    
    // Set up form change detection
    setupFormChangeDetection();
    
    console.log('✅ Collaboration modal opened');
}

/**
 * Close the collaboration modal
 */
function closeCollaborationModal() {
    const modal = document.getElementById('collaboration-modal');
    if (!modal) {
        console.error('Collaboration modal element not found');
        return;
    }

    // Check for unsaved changes
    if (collaborationModalState.hasUnsavedChanges) {
        const confirmClose = confirm('You have unsaved changes. Are you sure you want to close?');
        if (!confirmClose) {
            return;
        }
    }

    // Hide modal
    modal.classList.remove('active');
    modal.style.display = 'none';
    
    // Restore body scroll
    document.body.classList.remove('modal-no-scroll');
    
    // Reset state
    collaborationModalState.isOpen = false;
    collaborationModalState.hasUnsavedChanges = false;
    
    console.log('✅ Collaboration modal closed');
}

/**
 * Load current collaboration settings into the form
 */
function loadCollaborationSettings() {
    try {
        // Get simulation ID from current page (you might need to adjust this)
        const simulationId = getSimulationId();
        
        // Load settings from server or local storage
        // For MVP, we'll use default settings
        const defaultSettings = {
            enable_collaboration: false,
            max_team_size: 4,
            team_formation: 'student_choice',
            enable_chat: true,
            enable_screen_share: false,
            enable_annotations: true,
            instructor_monitoring: true,
            activity_logging: true,
            session_timeout: 60,
            max_sessions: 5
        };

        // Populate form with settings
        populateFormWithSettings(defaultSettings);
        
        // Store current settings
        collaborationModalState.currentSettings = { ...defaultSettings };
        
        console.log('✅ Collaboration settings loaded');
        
    } catch (error) {
        console.error('❌ Error loading collaboration settings:', error);
        showNotification('Error loading settings', 'error');
    }
}

/**
 * Populate form fields with settings data
 */
function populateFormWithSettings(settings) {
    // Enable collaboration toggle
    const enableCollab = document.getElementById('enable-collaboration');
    if (enableCollab) {
        enableCollab.checked = settings.enable_collaboration;
        toggleCollaborationSections(settings.enable_collaboration);
    }

    // Team settings
    setValue('max-team-size', settings.max_team_size);
    setValue('team-formation', settings.team_formation);

    // Communication settings
    setChecked('enable-chat', settings.enable_chat);
    setChecked('enable-screen-share', settings.enable_screen_share);
    setChecked('enable-annotations', settings.enable_annotations);

    // Monitoring settings
    setChecked('instructor-monitoring', settings.instructor_monitoring);
    setChecked('activity-logging', settings.activity_logging);

    // Session settings
    setValue('session-timeout', settings.session_timeout);
    setValue('max-sessions', settings.max_sessions);
}

/**
 * Helper function to set form field values
 */
function setValue(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.value = value;
    }
}

/**
 * Helper function to set checkbox values
 */
function setChecked(id, checked) {
    const element = document.getElementById(id);
    if (element) {
        element.checked = checked;
    }
}

/**
 * Toggle visibility of collaboration sections based on enable state
 */
function toggleCollaborationSections(enabled) {
    const sections = [
        'team-settings',
        'communication-settings',
        'monitoring-settings',
        'session-settings'
    ];

    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.style.display = enabled ? 'block' : 'none';
        }
    });
}

/**
 * Save collaboration settings
 */
function saveCollaborationSettings() {
    try {
        const formData = gatherFormData();
        
        // Validate form data
        if (!validateCollaborationSettings(formData)) {
            return;
        }

        // Show loading state
        const saveButton = document.querySelector('#collaboration-modal .btn-primary');
        const originalText = saveButton.innerHTML;
        saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        saveButton.disabled = true;

        // Simulate API call (replace with actual API call)
        setTimeout(() => {
            try {
                // Here you would make the actual API call
                console.log('💾 Saving collaboration settings:', formData);
                
                // Update stored settings
                collaborationModalState.currentSettings = { ...formData };
                collaborationModalState.hasUnsavedChanges = false;
                
                // Show success message
                showNotification('Collaboration settings saved successfully', 'success');
                
                // Close modal
                closeCollaborationModal();
                
            } catch (error) {
                console.error('❌ Error saving settings:', error);
                showNotification('Error saving settings', 'error');
            } finally {
                // Restore button state
                saveButton.innerHTML = originalText;
                saveButton.disabled = false;
            }
        }, 1000);

    } catch (error) {
        console.error('❌ Error in saveCollaborationSettings:', error);
        showNotification('Error saving settings', 'error');
    }
}

/**
 * Gather form data into an object
 */
function gatherFormData() {
    const form = document.getElementById('collaboration-settings-form');
    const formData = new FormData(form);
    const settings = {};

    // Process form data
    for (let [key, value] of formData.entries()) {
        settings[key] = value;
    }

    // Handle checkboxes (they won't be in FormData if unchecked)
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        settings[checkbox.name] = checkbox.checked;
    });

    return settings;
}

/**
 * Validate collaboration settings
 */
function validateCollaborationSettings(settings) {
    // Check team size
    if (settings.enable_collaboration) {
        const maxTeamSize = parseInt(settings.max_team_size);
        if (isNaN(maxTeamSize) || maxTeamSize < 2 || maxTeamSize > 8) {
            showNotification('Team size must be between 2 and 8', 'error');
            return false;
        }

        const sessionTimeout = parseInt(settings.session_timeout);
        if (isNaN(sessionTimeout) || sessionTimeout < 15 || sessionTimeout > 480) {
            showNotification('Session timeout must be between 15 and 480 minutes', 'error');
            return false;
        }

        const maxSessions = parseInt(settings.max_sessions);
        if (isNaN(maxSessions) || maxSessions < 1 || maxSessions > 20) {
            showNotification('Max sessions must be between 1 and 20', 'error');
            return false;
        }
    }

    return true;
}

/**
 * Set up form change detection
 */
function setupFormChangeDetection() {
    const form = document.getElementById('collaboration-settings-form');
    if (!form) return;

    const formElements = form.querySelectorAll('input, select');
    
    formElements.forEach(element => {
        element.addEventListener('change', () => {
            collaborationModalState.hasUnsavedChanges = true;
        });

        element.addEventListener('input', () => {
            collaborationModalState.hasUnsavedChanges = true;
        });
    });

    // Special handling for collaboration enable toggle
    const enableCollab = document.getElementById('enable-collaboration');
    if (enableCollab) {
        enableCollab.addEventListener('change', function() {
            toggleCollaborationSections(this.checked);
            collaborationModalState.hasUnsavedChanges = true;
        });
    }
}

/**
 * Get simulation ID from current page
 */
function getSimulationId() {
    // Try to get from URL params or page data
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('simulation_id') || 'default';
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: 'white',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: '10001',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        minWidth: '300px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
        transform: 'translateX(400px)',
        transition: 'transform 0.3s ease'
    });

    // Set background color based on type
    const colors = {
        success: '#10B981',
        error: '#EF4444',
        info: '#3B82F6'
    };
    notification.style.background = colors[type] || colors.info;

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Remove after delay
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

/**
 * Handle clicks outside modal to close it
 */
document.addEventListener('click', function(event) {
    const modal = document.getElementById('collaboration-modal');
    if (modal && modal.classList.contains('active')) {
        if (event.target === modal) {
            closeCollaborationModal();
        }
    }
});

/**
 * Handle escape key to close modal
 */
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && collaborationModalState.isOpen) {
        closeCollaborationModal();
    }
});

/**
 * Initialize collaboration modal when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Collaboration modal initialized');
});
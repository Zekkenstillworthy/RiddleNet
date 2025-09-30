// questions.js - JavaScript for questions management

// Authentication utility
function checkAuthentication() {
    // Check if we're on the admin pages and authenticated
    const isAdminPage = window.location.pathname.startsWith('/admin/');
    const loginForm = document.querySelector('form[action="/admin/login"]');
    
    // If we're on admin pages and see a login form, we're not authenticated
    if (isAdminPage && loginForm) {
        return false;
    }
    
    return true;
}

function handleAuthError(error) {
    if (error.message === 'Authentication required') {
        showNotification('Please log in to access this feature.', 'error');
        setTimeout(() => {
            window.location.href = '/admin/login';
        }, 2000);
        return true;
    }
    return false;
}

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication before initializing
    if (!checkAuthentication()) {
        console.warn('User not authenticated, redirecting to login');
        window.location.href = '/admin/login';
        return;
    }
    
    initializeQuestionForm();
    loadUngroupedQuestions();
    setupEventListeners();
});

// Modal Management
function openModal(modalId) {
    console.log(`Opening modal: ${modalId}`);
    const modal = document.getElementById(modalId);
    if (modal) {
        // Reset any existing styles that might interfere
        modal.removeAttribute('style');
        
        // Force proper modal display with critical CSS properties
        modal.style.cssText = `
            display: flex !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 10000 !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 20px !important;
            box-sizing: border-box !important;
            background-color: rgba(0, 0, 0, 0.85) !important;
            backdrop-filter: blur(15px) !important;
            margin: 0 !important;
            flex-direction: column !important;
            opacity: 1 !important;
        `;
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Force reflow to ensure display:flex is applied
        modal.offsetHeight;
        
        // Add show class for animation (with slight delay for smoother transition)
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        
        // Ensure modal content positioning
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.scrollTop = 0;
            // Force modal content CSS properties to prevent positioning issues
            modalContent.style.cssText += `
                position: relative !important;
                margin: 0 auto !important;
                top: auto !important;
                left: auto !important;
                right: auto !important;
                bottom: auto !important;
                align-self: center !important;
                z-index: 10001 !important;
            `;
        }
        
        // Accessibility: Set focus trap and ARIA attributes
        modal.setAttribute('aria-hidden', 'false');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        
        // Focus on first input if available
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
        
        // Add keyboard navigation
        modal.addEventListener('keydown', handleModalKeydown);
        
        console.log(`✅ Modal ${modalId} opened with flexbox centering`);
    } else {
        console.error(`❌ Modal ${modalId} not found`);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        // Remove show class for animation
        modal.classList.remove('show');
        
        // Accessibility: Update ARIA attributes
        modal.setAttribute('aria-hidden', 'true');
        modal.removeAttribute('role');
        modal.removeAttribute('aria-modal');
        
        // Hide modal after transition
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }, 300);
        
        // Reset forms when closing modals
        const forms = modal.querySelectorAll('form');
        forms.forEach(form => form.reset());
        
        // Remove keyboard event listener
        modal.removeEventListener('keydown', handleModalKeydown);
    }
}

// Handle keyboard navigation in modals
function handleModalKeydown(event) {
    if (event.key === 'Escape') {
        const modal = event.currentTarget;
        closeModal(modal.id);
    }
    
    // Tab trapping
    if (event.key === 'Tab') {
        const modal = event.currentTarget;
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        if (event.shiftKey) {
            if (document.activeElement === firstFocusable) {
                lastFocusable.focus();
                event.preventDefault();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                firstFocusable.focus();
                event.preventDefault();
            }
        }
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
});

// Close modal when pressing Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        // Find any open modal
        const openModals = document.querySelectorAll('.modal[style*="flex"]');
        openModals.forEach(modal => {
            closeModal(modal.id);
        });
    }
});

// Question Form Management
function initializeQuestionForm() {
    const questionTypeSelect = document.getElementById('question-type');
    const editQuestionTypeSelect = document.getElementById('edit-question-type');
    const optionsContainer = document.getElementById('options-container');
    const matchingContainer = document.getElementById('matching-container');
    const editOptionsContainer = document.getElementById('edit-options-container');
    const editMatchingContainer = document.getElementById('edit-matching-container');
    
    function handleTypeChange(selectElement, optionsContainer, matchingContainer) {
        if (!selectElement) return;
        
        const selectedType = selectElement.value;
        
        // Hide all type-specific containers
        if (optionsContainer) optionsContainer.style.display = 'none';
        if (matchingContainer) matchingContainer.style.display = 'none';
        
        // Show relevant container based on type
        switch (selectedType) {
            case 'multiple_choice':
                if (optionsContainer) optionsContainer.style.display = 'block';
                break;
            case 'matching':
                if (matchingContainer) matchingContainer.style.display = 'block';
                break;
            default:
                // For other types (fill_blank, short_answer, essay), hide both containers
                break;
        }
    }
    
    if (questionTypeSelect) {
        questionTypeSelect.addEventListener('change', function() {
            handleTypeChange(this, optionsContainer, matchingContainer);
        });
        // Initialize on page load
        handleTypeChange(questionTypeSelect, optionsContainer, matchingContainer);
    }
    
    if (editQuestionTypeSelect) {
        editQuestionTypeSelect.addEventListener('change', function() {
            handleTypeChange(this, editOptionsContainer, editMatchingContainer);
        });
    }
    
    // Add option button functionality
    const addOptionBtn = document.getElementById('add-option');
    if (addOptionBtn) {
        addOptionBtn.addEventListener('click', function() {
            const optionInputs = document.querySelector('.option-inputs');
            if (optionInputs) {
                const newInput = document.createElement('input');
                newInput.type = 'text';
                newInput.name = 'options[]';
                newInput.placeholder = `Option ${optionInputs.children.length + 1}`;
                optionInputs.appendChild(newInput);
            }
        });
    }
    
    // Edit form add option button
    const editAddOptionBtn = document.getElementById('edit-add-option');
    if (editAddOptionBtn) {
        editAddOptionBtn.addEventListener('click', function() {
            const optionInputs = document.getElementById('edit-option-inputs');
            if (optionInputs) {
                const newInput = document.createElement('input');
                newInput.type = 'text';
                newInput.name = 'options[]';
                newInput.placeholder = `Option ${optionInputs.children.length + 1}`;
                optionInputs.appendChild(newInput);
            }
        });
    }
    
    // Add matching pair functionality
    const addPairBtn = document.getElementById('add-pair');
    if (addPairBtn) {
        addPairBtn.addEventListener('click', function() {
            const matchingPairs = document.querySelector('.matching-pairs');
            if (matchingPairs) {
                addMatchingPair(matchingPairs);
            }
        });
    }
    
    // Edit form add pair button
    const editAddPairBtn = document.getElementById('edit-add-pair');
    if (editAddPairBtn) {
        editAddPairBtn.addEventListener('click', function() {
            const matchingPairs = document.getElementById('edit-matching-pairs');
            if (matchingPairs) {
                addMatchingPair(matchingPairs);
            }
        });
    }
    
    // Add remove functionality to existing pairs
    document.querySelectorAll('.btn-remove-pair').forEach(btn => {
        btn.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
}

function addMatchingPair(container) {
    const pairDiv = document.createElement('div');
    pairDiv.className = 'matching-pair';
    pairDiv.innerHTML = `
        <input type="text" name="matching_items[]" placeholder="Item">
        <input type="text" name="matching_matches[]" placeholder="Match">
        <button type="button" class="btn-remove-pair">×</button>
    `;
    container.appendChild(pairDiv);
    
    // Add remove functionality to new pair
    const removeBtn = pairDiv.querySelector('.btn-remove-pair');
    removeBtn.addEventListener('click', function() {
        pairDiv.remove();
    });
}

// Question Group Management
function viewQuestionGroup(groupId, groupName, groupDescription) {
    fetch(`/admin/groups/api/${groupId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
    .then(data => {
            if (data.success) {
                displayGroupQuestions(data.questions, groupName, groupDescription, groupId);
            } else {
                console.error('Error loading group questions:', data.message);
                showNotification('Error loading group questions: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error loading group questions:', error);
            showNotification('Error loading group questions. Please try again.', 'error');
        });
}

function displayGroupQuestions(questions, groupName, groupDescription, groupId) {
    // Create and show group questions modal
    let existingModal = document.getElementById('groupQuestionsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.id = 'groupQuestionsModal';
    modal.className = 'modal';
    modal.style.display = 'flex';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 1000px;">
            <div class="modal-header">
                <h3>Questions in Group: ${groupName}</h3>
                <span class="close-modal" onclick="closeModal('groupQuestionsModal')">&times;</span>
            </div>
            <div class="modal-body">
                <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 20px;">${groupDescription || 'No description available'}</p>
                <div class="questions-list">
                    ${questions.length > 0 ? questions.map(q => `
                        <div class="question-item" style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(0, 217, 255, 0.15); border-radius: 8px; padding: 16px; margin-bottom: 12px; transition: all 0.3s ease;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <h4 style="color: #00D9FF; margin: 0 0 8px 0; font-weight: 600;">Question ${q.numb}</h4>
                                    <p style="color: rgba(255, 255, 255, 0.9); margin: 0 0 8px 0; line-height: 1.4;">${q.question}</p>
                                    <div style="display: flex; gap: 12px; font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">
                                        <span style="background: rgba(139, 92, 246, 0.2); padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3);">Type: ${q.question_type}</span>
                                        <span style="background: rgba(0, 217, 255, 0.2); padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(0, 217, 255, 0.3);">Category: ${q.category}</span>
                                    </div>
                                </div>
                                <div style="display: flex; gap: 8px;">
                                    <button class="btn btn-small" style="background: linear-gradient(135deg, #00D9FF, #8B5CF6); border: none; color: white; padding: 8px 16px; border-radius: 8px; font-weight: 600; transition: all 0.3s ease;" onclick="editQuestion(${q.id})">
                                        <i class="fas fa-edit"></i> Edit
                                    </button>
                                    <button class="btn btn-small" style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); border: none; color: white; padding: 8px 16px; border-radius: 8px; font-weight: 600; transition: all 0.3s ease;" onclick="removeFromGroup(${q.id}, ${groupId})">
                                        <i class="fas fa-trash"></i> Remove
                                    </button>
                                </div>
                            </div>
                        </div>
                    `).join('') : '<p style="color: rgba(255, 255, 255, 0.6); text-align: center; padding: 40px; font-style: italic;">No questions in this group.</p>'}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('groupQuestionsModal')" style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(0, 217, 255, 0.15); color: rgba(255, 255, 255, 0.9); padding: 12px 20px; border-radius: 8px; font-weight: 600;">Close</button>
                <button class="btn" onclick="addQuestionsToGroup(${groupId})" style="background: linear-gradient(135deg, #39FF14, #00D9FF); border: none; color: white; padding: 12px 20px; border-radius: 8px; font-weight: 600;">
                    <i class="fas fa-plus"></i> Add Questions
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
}

function editQuestionGroup(groupId, groupName, groupDescription) {
    console.log('editQuestionGroup called with:', { groupId, groupName, groupDescription });
    
    // Populate edit form with the correct field IDs
    const groupIdField = document.getElementById('edit-group-id');
    const groupNameField = document.getElementById('edit-group-name');
    const groupDescField = document.getElementById('edit-group-description');
    
    if (groupIdField) groupIdField.value = groupId;
    if (groupNameField) groupNameField.value = groupName;
    if (groupDescField) groupDescField.value = groupDescription || '';
    
    // Update the form action to include the group ID
    const form = document.getElementById('editGroupForm');
    if (form) {
        form.action = `/admin/groups/edit/${groupId}`;
        console.log('Form action updated to:', form.action);
    }
    
    // Force open the modal with enhanced positioning
    const modal = document.getElementById('editGroupModal');
    if (modal) {
        console.log('Opening editGroupModal...');
        
        // Reset any existing styles
        modal.removeAttribute('style');
        
        // Apply critical positioning styles
        modal.style.cssText = `
            display: flex !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 10000 !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 20px !important;
            box-sizing: border-box !important;
            background-color: rgba(0, 0, 0, 0.85) !important;
            backdrop-filter: blur(15px) !important;
            margin: 0 !important;
            flex-direction: column !important;
            opacity: 1 !important;
        `;
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Force reflow
        modal.offsetHeight;
        
        // Add show class
        modal.classList.add('show');
        
        // Ensure modal content is properly positioned
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.cssText += `
                position: relative !important;
                margin: 0 auto !important;
                top: auto !important;
                left: auto !important;
                right: auto !important;
                bottom: auto !important;
                align-self: center !important;
                z-index: 10001 !important;
            `;
        }
        
        // Set accessibility attributes
        modal.setAttribute('aria-hidden', 'false');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        
        // Focus on first input
        const firstInput = modal.querySelector('input, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
        
        // Load ungrouped questions for the edit modal
        loadUngroupedQuestionsForEdit(groupId);
        
        console.log('✅ editGroupModal opened successfully');
    } else {
        console.error('❌ editGroupModal not found');
    }
}

// Function to load ungrouped questions specifically for the edit group modal
function loadUngroupedQuestionsForEdit(currentGroupId) {
    console.log('Loading ungrouped questions for edit modal, excluding group:', currentGroupId);
    
    const container = document.getElementById('edit-available-questions');
    if (!container) {
        console.error('Edit available questions container not found');
        return;
    }
    
    // Show loading state
    container.innerHTML = '<div class="edit-group-loading"><i class="fas fa-spinner fa-spin"></i> Loading available questions...</div>';
    
    // Fetch ungrouped questions
    fetch('/admin/questions/ungrouped?format=json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Ungrouped questions API response:', data);
            
            if (data.success && data.questions) {
                displayUngroupedQuestionsInEditModal(data.questions, currentGroupId);
            } else {
                container.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 20px; font-style: italic;">No ungrouped questions available</div>';
            }
        })
        .catch(error => {
            console.error('Error loading ungrouped questions for edit:', error);
            container.innerHTML = `
                <div class="edit-group-empty" style="color: rgba(255, 107, 107, 0.8); border-color: rgba(255, 107, 107, 0.3);">
                    <i class="fas fa-exclamation-triangle"></i><br>
                    Error loading questions. Please try again.
                    <br><button type="button" onclick="loadUngroupedQuestionsForEdit('${currentGroupId}')" class="btn btn-small" style="margin-top: 12px; background: var(--gradient-primary);">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
        });
}

// Function to display ungrouped questions in the edit modal
function displayUngroupedQuestionsInEditModal(questions, currentGroupId) {
    const container = document.getElementById('edit-available-questions');
    if (!container) return;
    
    if (!questions || questions.length === 0) {
        container.innerHTML = '<div class="edit-group-empty"><i class="fas fa-inbox"></i><br>No ungrouped questions available</div>';
        updateEditSelectionStats();
        return;
    }
    
    container.innerHTML = questions.map((q, index) => `
        <div class="edit-group-question-item" data-question-id="${q.id}" onclick="toggleQuestionSelection(this, '${q.id}')">
            <div class="edit-group-toggle-container">
                <input type="checkbox" class="edit-group-question-checkbox" name="edit_selected_questions" value="${q.id}">
                <span class="edit-group-toggle-slider"></span>
            </div>
            <div class="edit-group-question-content">
                <h5 class="edit-group-question-title">
                    <span class="edit-group-number-badge">Q${q.numb}</span>
                    <span class="edit-group-question-text">${q.question}</span>
                </h5>
                <div class="edit-group-question-meta">
                    <span class="edit-group-type-badge">
                        <i class="fas fa-code"></i> ${q.type || q.question_type || 'Multiple Choice'}
                    </span>
                    <span class="edit-group-category-badge">
                        <i class="fas fa-tag"></i> ${q.category}
                    </span>
                    ${q.answer ? `<span class="edit-group-answer-badge"><i class="fas fa-check-circle"></i> Has Answer</span>` : ''}
                </div>
            </div>
        </div>
    `).join('');
    
    // Update stats after displaying questions
    updateEditSelectionStats();
    
    console.log(`✅ Displayed ${questions.length} ungrouped questions in edit modal with custom styling`);
}

// Function to toggle question selection styling
function toggleQuestionSelection(element, questionId) {
    const checkbox = element.querySelector('.edit-group-question-checkbox');
    if (checkbox && !checkbox.disabled) {
        checkbox.checked = !checkbox.checked;
        toggleItemSelection(checkbox);
        updateEditSelectionStats();
    }
}

// Function to toggle visual selection state
function toggleItemSelection(checkbox) {
    const questionItem = checkbox.closest('.edit-group-question-item');
    if (questionItem) {
        if (checkbox.checked) {
            questionItem.classList.add('selected');
        } else {
            questionItem.classList.remove('selected');
        }
    }
}

// Function to update selection statistics in edit modal
function updateEditSelectionStats() {
    const checkboxes = document.querySelectorAll('input[name="edit_selected_questions"]');
    const checkedBoxes = document.querySelectorAll('input[name="edit_selected_questions"]:checked');
    const statsElement = document.getElementById('edit-selection-stats');
    const addButton = document.getElementById('add-selected-questions-btn');
    
    if (statsElement) {
        const selectedCount = checkedBoxes.length;
        const totalCount = checkboxes.length;
        statsElement.innerHTML = `<span class="edit-group-counter">${selectedCount} of ${totalCount} questions selected</span>`;
    }
    
    if (addButton) {
        addButton.disabled = checkedBoxes.length === 0;
        if (checkedBoxes.length > 0) {
            addButton.style.opacity = '1';
            addButton.style.cursor = 'pointer';
        } else {
            addButton.style.opacity = '0.5';
            addButton.style.cursor = 'not-allowed';
        }
    }
}

// Test function to verify modal positioning
function testModalPositioning() {
    console.log('🧪 Testing modal positioning...');
    
    // Test editGroupModal
    const testModal = document.getElementById('editGroupModal');
    if (testModal) {
        console.log('✅ editGroupModal found');
        
        // Test opening
        editQuestionGroup('test-id', 'Test Group', 'Test description');
        
        // Check positioning
        setTimeout(() => {
            const computedStyle = window.getComputedStyle(testModal);
            console.log('Modal computed styles:', {
                display: computedStyle.display,
                position: computedStyle.position,
                top: computedStyle.top,
                left: computedStyle.left,
                justifyContent: computedStyle.justifyContent,
                alignItems: computedStyle.alignItems,
                zIndex: computedStyle.zIndex
            });
            
            // Close modal
            closeModal('editGroupModal');
        }, 1000);
    } else {
        console.error('❌ editGroupModal not found');
    }
}

// Add to window for easy browser console testing
window.testModalPositioning = testModalPositioning;
window.editQuestionGroup = editQuestionGroup;

function deleteQuestionGroup(groupId, groupName) {
    console.log('Requesting deletion of question group:', groupName, 'ID:', groupId);
    
    fetch(`/admin/groups/api/delete/${groupId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Question group deleted successfully:', groupName);
            showNotification('Question group deleted successfully', 'success');
            // Emit WebSocket event to refresh data
            if (window.socketClient) {
                window.socketClient.emit('question_group_deleted', { groupId, groupName });
            }
        } else {
            console.error('Error deleting group:', data.message);
            showNotification('Error deleting group: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting group:', error);
        showNotification('Error deleting group. Please try again.', 'error');
    });
}

// Ungrouped Questions Management
function loadUngroupedQuestions() {
    const container = document.getElementById('main-ungrouped-container');
    
    if (!container) {
        console.error('Container element main-ungrouped-container not found!');
        return;
    }
    
    console.log('Container found, loading ungrouped questions...');
    
    function fetchUngrouped() {
        const url = '/admin/questions/api/ungrouped';
        
        console.log('Loading ungrouped questions from:', url);
        container.innerHTML = '<div class="loading-spinner" style="text-align: center; color: rgba(255, 255, 255, 0.6); padding: 40px;"><i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 12px;"></i><br>Loading ungrouped questions...</div>';
        
        // Add a timeout to catch hanging requests
        const timeoutId = setTimeout(() => {
            console.error('Request timeout - taking too long to load');
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: rgba(255, 255, 255, 0.6);">
                    <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); padding: 20px; border-radius: 50%; display: inline-block; margin-bottom: 20px; box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);">
                        <i class="fas fa-clock" style="font-size: 2rem; color: white;"></i>
                    </div>
                    <p style="font-size: 1.1rem; font-weight: 500; color: #ff6b6b;">Request timeout. Please check server connection.</p>
                    <button onclick="loadUngroupedQuestions()" style="background: var(--gradient-primary); border: none; color: white; padding: 10px 20px; border-radius: 8px; margin-top: 16px; cursor: pointer;">
                        Try Again
                    </button>
                </div>
            `;
        }, 10000); // 10 second timeout
        
        fetch(url)
            .then(response => {
                clearTimeout(timeoutId); // Clear timeout if request completes
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                console.log('Response URL:', response.url);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                // Check if we got redirected to login page
                if (response.url.includes('/admin/login')) {
                    throw new Error('Authentication required');
                }
                
                return response.json();
            })
            .then(data => {
                clearTimeout(timeoutId); // Clear timeout if request completes
                console.log('=== API Response ===');
                console.log('Received data:', data);
                console.log('Data type:', typeof data);
                console.log('Data keys:', Object.keys(data || {}));
                
                if (data && data.success) {
                    console.log('Number of questions:', data.questions ? data.questions.length : 0);
                    if (data.questions && Array.isArray(data.questions)) {
                        console.log('About to call displayUngroupedQuestions...');
                        displayUngroupedQuestions(data.questions);
                    } else {
                        console.error('Questions data is not an array:', data.questions);
                        container.innerHTML = `
                            <div style="text-align: center; padding: 60px 20px; color: rgba(255, 255, 255, 0.6);">
                                <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); padding: 20px; border-radius: 50%; display: inline-block; margin-bottom: 20px; box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);">
                                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: white;"></i>
                                </div>
                                <p style="font-size: 1.1rem; font-weight: 500; color: #ff6b6b;">Invalid data format received</p>
                                <button onclick="loadUngroupedQuestions()" style="background: var(--gradient-primary); border: none; color: white; padding: 10px 20px; border-radius: 8px; margin-top: 16px; cursor: pointer;">
                                    Try Again
                                </button>
                            </div>
                        `;
                    }
                } else {
                    console.error('API returned success: false or no success field', data);
                    container.innerHTML = `
                        <div style="text-align: center; padding: 60px 20px; color: rgba(255, 255, 255, 0.6);">
                            <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); padding: 20px; border-radius: 50%; display: inline-block; margin-bottom: 20px; box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);">
                                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: white;"></i>
                            </div>
                            <p style="font-size: 1.1rem; font-weight: 500; color: #ff6b6b;">Error loading questions</p>
                            <button onclick="loadUngroupedQuestions()" style="background: var(--gradient-primary); border: none; color: white; padding: 10px 20px; border-radius: 8px; margin-top: 16px; cursor: pointer;">
                                Try Again
                            </button>
                        </div>
                    `;
                }
            })
            .catch(error => {
                clearTimeout(timeoutId); // Clear timeout if request fails
                console.error('Error loading ungrouped questions:', error);
                if (handleAuthError(error)) {
                    // User is not authenticated, handled in handleAuthError
                } else {
                    container.innerHTML = `
                        <div style="text-align: center; padding: 60px 20px; color: rgba(255, 255, 255, 0.6);">
                            <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); padding: 20px; border-radius: 50%; display: inline-block; margin-bottom: 20px; box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);">
                                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: white;"></i>
                            </div>
                            <p style="font-size: 1.1rem; font-weight: 500; color: #ff6b6b;">Error loading questions: ${error.message}</p>
                            <button onclick="loadUngroupedQuestions()" style="background: var(--gradient-primary); border: none; color: white; padding: 10px 20px; border-radius: 8px; margin-top: 16px; cursor: pointer;">
                                Try Again
                            </button>
                        </div>
                    `;
                }
            });
    }
    
    fetchUngrouped(); // Load all questions
}

// Debug function to help identify styling issues
function debugUngroupedQuestions() {
    console.log('=== Debug Ungrouped Questions ===');
    
    const container = document.getElementById('main-ungrouped-container');
    if (!container) {
        console.error('Container not found!');
        return;
    }
    
    console.log('Container found:', container);
    console.log('Container computed style:', window.getComputedStyle(container));
    console.log('Container bounding rect:', container.getBoundingClientRect());
    console.log('Container children:', container.children.length);
    
    // Check if any loading spinners exist
    const spinners = document.querySelectorAll('.loading-spinner');
    console.log('Loading spinners found:', spinners.length);
    spinners.forEach((spinner, i) => {
        console.log(`Spinner ${i}:`, spinner, 'Parent:', spinner.parentElement);
    });
    
    // Check for conflicting CSS
    const allContainers = document.querySelectorAll('[id*="ungrouped"], [class*="ungrouped"]');
    console.log('All ungrouped-related elements:', allContainers);
    
    // Force show questions with brute force
    container.innerHTML = `
        <div style="background: red; color: white; padding: 20px; border: 2px solid yellow;">
            <h3>TEST: If you can see this, the container is working!</h3>
            <p>Container ID: ${container.id}</p>
            <p>Container classes: ${container.className}</p>
        </div>
    `;
}

// Make debug function available globally
window.debugUngroupedQuestions = debugUngroupedQuestions;

function displayUngroupedQuestions(questions) {
    console.log('=== displayUngroupedQuestions called ===');
    console.log('Questions received:', questions);
    console.log('Questions type:', typeof questions);
    console.log('Questions is array:', Array.isArray(questions));
    console.log('Questions length:', questions ? questions.length : 'undefined');
    
    const container = document.getElementById('main-ungrouped-container');
    
    if (!container) {
        console.error('Container element not found!');
        return;
    }
    
    console.log('Container found:', container);
    
    if (!questions || questions.length === 0) {
        console.log('No questions to display');
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; color: rgba(255, 255, 255, 0.6);">
                <div style="background: linear-gradient(135deg, #00D9FF, #8B5CF6); padding: 20px; border-radius: 50%; display: inline-block; margin-bottom: 20px; box-shadow: 0 8px 25px rgba(0, 217, 255, 0.3);">
                    <i class="fas fa-question-circle" style="font-size: 2rem; color: white;"></i>
                </div>
                <p style="font-size: 1.1rem; font-weight: 500;">No ungrouped questions found.</p>
            </div>
        `;
        return;
    }
    
    console.log('Rendering', questions.length, 'questions');
    
    // Force container visibility with stronger CSS
    container.style.cssText = `
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
        min-height: 200px !important;
        background: var(--dark-bg) !important;
        border-radius: 16px !important;
        padding: 32px !important;
        border: 1px solid var(--glass-border) !important;
        position: relative !important;
        z-index: 1 !important;
        overflow: visible !important;
    `;
    container.classList.add('questions-loaded');
    
    try {
        const questionsHtml = questions.map((q, index) => {
            console.log(`Processing question ${index}:`, q);
            
            const questionText = q.question || q.content || 'No content';
            const questionId = q.id || index;
            const questionType = q.type || 'Unknown';
            const questionCategory = q.category || 'None';
            const questionNumb = q.numb || q.id || index;
            
            return `
                <div class="question-item" style="background: rgba(139, 92, 246, 0.08) !important; border: 1px solid rgba(0, 217, 255, 0.15) !important; border-radius: 12px; padding: 18px; margin-bottom: 16px; display: flex !important; align-items: start; gap: 14px; transition: all 0.3s ease; position: relative; overflow: hidden; visibility: visible !important; opacity: 1 !important;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(135deg, #00D9FF, #8B5CF6); opacity: 0.6;"></div>
                    <input type="checkbox" class="question-checkbox" value="${questionId}" style="margin-top: 6px; transform: scale(1.2); accent-color: #00D9FF;">
                    <div style="flex: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                            <h4 style="color: #00D9FF; margin: 0; font-weight: 600; text-shadow: 0 0 10px rgba(0, 217, 255, 0.3);">Question ${questionNumb}</h4>
                            <div style="display: flex; gap: 8px;">
                                <button class="btn btn-small" onclick="editQuestion(${questionId})" style="background: linear-gradient(135deg, #00D9FF, #8B5CF6); border: none; color: white; padding: 8px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0, 217, 255, 0.3);">
                                    <i class="fas fa-edit"></i> Edit
                                </button>
                                <button class="btn btn-small" onclick="deleteQuestion(${questionId})" style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); border: none; color: white; padding: 8px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);">
                                    <i class="fas fa-trash"></i> Delete
                                </button>
                            </div>
                        </div>
                        <p style="color: rgba(255, 255, 255, 0.9) !important; margin: 0 0 12px 0; line-height: 1.5; font-size: 0.95rem;">${questionText}</p>
                        <div style="display: flex; gap: 12px; font-size: 0.85rem;">
                            <span style="background: rgba(139, 92, 246, 0.2); color: rgba(255, 255, 255, 0.8) !important; padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3);">Type: ${questionType}</span>
                            <span style="background: rgba(0, 217, 255, 0.2); color: rgba(255, 255, 255, 0.8) !important; padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(0, 217, 255, 0.3);">Category: ${questionCategory}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        console.log('Generated HTML length:', questionsHtml.length);
        
        // Clear any loading classes first
        container.className = 'main-ungrouped-questions-container modern-card questions-loaded';
        
        // Add the CSS class that triggers visibility rules
        container.classList.add('questions-loaded');
        
        // Set the HTML content
        container.innerHTML = questionsHtml;
        
        // Force visibility and styling with high specificity
        container.style.cssText = `
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: auto !important;
            min-height: 200px !important;
            background: rgba(26, 35, 126, 0.3) !important;
            border-radius: 16px !important;
            padding: 32px !important;
            border: 1px solid rgba(0, 217, 255, 0.3) !important;
            position: relative !important;
            z-index: 1 !important;
            overflow: visible !important;
        `;
        
        // Also force each question item to be visible with hard-coded colors
        setTimeout(() => {
            const questionItems = container.querySelectorAll('.question-item');
            questionItems.forEach((item, index) => {
                item.style.cssText += `
                    display: flex !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    background: rgba(139, 92, 246, 0.08) !important;
                    border: 1px solid rgba(0, 217, 255, 0.15) !important;
                    margin-bottom: 16px !important;
                    padding: 18px !important;
                    position: relative !important;
                    z-index: 10 !important;
                `;
                
                // Force text visibility
                const textElements = item.querySelectorAll('p, h4, span');
                textElements.forEach(el => {
                    el.style.cssText += `
                        color: rgba(255, 255, 255, 0.9) !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                    `;
                });
            });
            
            console.log('Applied visibility fixes to', questionItems.length, 'question items');
        }, 100);
        
        // Remove any loading spinners that might still exist
        const loadingSpinners = container.querySelectorAll('.loading-spinner');
        loadingSpinners.forEach(spinner => {
            spinner.remove();
            console.log('Removed loading spinner');
        });
        
        // Force a reflow to ensure the changes take effect
        container.offsetHeight;
        
        console.log('Questions rendered successfully');
        console.log('Container after rendering:', container);
        console.log('Container children count:', container.children.length);
        console.log('Container className:', container.className);
        console.log('Container style:', container.style.cssText);
        
        // Check if the first question element is visible
        const firstQuestion = container.querySelector('.question-item');
        if (firstQuestion) {
            console.log('First question element found:', firstQuestion);
            console.log('First question visible:', firstQuestion.offsetHeight > 0);
        } else {
            console.error('No question elements found in container!');
        }
        
        // Update checkbox listeners with error handling
        try {
            updateCheckboxListeners();
        } catch (error) {
            console.error('Error updating checkbox listeners:', error);
        }
        
    } catch (error) {
        console.error('Error rendering questions:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; color: rgba(255, 255, 255, 0.6);">
                <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); padding: 20px; border-radius: 50%; display: inline-block; margin-bottom: 20px; box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: white;"></i>
                </div>
                <p style="font-size: 1.1rem; font-weight: 500; color: #ff6b6b;">Error rendering questions</p>
            </div>
        `;
    }
}

function updateCheckboxListeners() {
    const checkboxes = document.querySelectorAll('.question-checkbox');
    const groupSelectedBtn = document.getElementById('groupSelectedBtn');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('.question-checkbox:checked').length;
            
            if (checkedCount > 0) {
                groupSelectedBtn.style.display = 'inline-block';
            } else {
                groupSelectedBtn.style.display = 'none';
            }
        });
    });
    
    // Add click handler for group selected button
    if (groupSelectedBtn) {
        groupSelectedBtn.onclick = function() {
            openModal('ungroupedQuestionsModal');
            loadUngroupedQuestionsInModal();
        };
    }
}

function loadUngroupedQuestionsInModal() {
    const container = document.querySelector('#ungroupedQuestionsModal .ungrouped-questions-container');
    
    if (!container) return;
    
    container.innerHTML = '<div class="loading-spinner" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading questions...</div>';
    
    fetch('/admin/questions/ungrouped?format=json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                displayUngroupedInModal(data.questions);
            } else {
                container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">Error loading questions</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">Error loading questions. Please try again.</p>';
        });
}

function displayUngroupedInModal(questions) {
    const container = document.querySelector('#ungroupedQuestionsModal .ungrouped-questions-container');
    
    container.innerHTML = questions.map(q => `
        <div class="question-item" style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(0, 217, 255, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 12px; display: flex; align-items: start; gap: 12px; transition: all 0.3s ease; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(135deg, #00D9FF, #8B5CF6); opacity: 0.6;"></div>
            <input type="checkbox" name="selected_questions" value="${q.id}" style="margin-top: 6px; transform: scale(1.2); accent-color: #00D9FF;">
            <div style="flex: 1;">
                <h5 style="color: #00D9FF; margin: 0 0 8px 0; font-weight: 600; text-shadow: 0 0 10px rgba(0, 217, 255, 0.3);">Q${q.numb}: ${q.question.substring(0, 100)}${q.question.length > 100 ? '...' : ''}</h5>
                <div style="font-size: 0.85rem; display: flex; gap: 12px;">
                    <span style="background: rgba(139, 92, 246, 0.2); color: rgba(255, 255, 255, 0.8); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3);">Type: ${q.question_type}</span>
                    <span style="background: rgba(0, 217, 255, 0.2); color: rgba(255, 255, 255, 0.8); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(0, 217, 255, 0.3);">Category: ${q.category}</span>
                </div>
            </div>
        </div>
    `).join('');
    
    // Update selection counter
    updateSelectionCounter();
}

function updateSelectionCounter() {
    const checkboxes = document.querySelectorAll('#ungroupedQuestionsModal input[name="selected_questions"]');
    const selectedCount = document.getElementById('selected-count');
    const groupBtn = document.getElementById('group-selected-btn');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const count = document.querySelectorAll('#ungroupedQuestionsModal input[name="selected_questions"]:checked').length;
            selectedCount.textContent = count;
            groupBtn.disabled = count === 0;
        });
    });
}

// Function to add selected questions to the group being edited
function addSelectedQuestionsToGroup() {
    const checkedBoxes = document.querySelectorAll('input[name="edit_selected_questions"]:checked');
    const groupIdField = document.getElementById('edit-group-id');
    
    if (!groupIdField || !groupIdField.value) {
        console.error('Group ID not found');
        showNotification('Error: Group ID not found', 'error');
        return;
    }
    
    if (checkedBoxes.length === 0) {
        showNotification('Please select at least one question to add', 'warning');
        return;
    }
    
    const groupId = groupIdField.value;
    const questionIds = Array.from(checkedBoxes).map(cb => cb.value);
    
    console.log('Adding questions to group:', { groupId, questionIds });
    
    // Show loading state
    const addButton = document.getElementById('add-selected-questions-btn');
    const originalText = addButton.innerHTML;
    addButton.disabled = true;
    addButton.classList.add('edit-group-btn-loading');
    addButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding Questions...';
    
    // Prepare form data
    const formData = new FormData();
    formData.append('group_id', groupId);
    questionIds.forEach(id => {
        formData.append('question_ids[]', id);
    });
    
    fetch('/admin/groups/add-questions', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Add questions response:', data);
        
        if (data.success) {
            showNotification(`Successfully added ${questionIds.length} question(s) to the group`, 'success');
            
            // Refresh the ungrouped questions list to remove the added questions
            loadUngroupedQuestionsForEdit(groupId);
            
            // Update the main page ungrouped questions if visible
            if (document.getElementById('main-ungrouped-container')) {
                loadUngroupedQuestions();
            }
        } else {
            throw new Error(data.message || 'Failed to add questions to group');
        }
    })
    .catch(error => {
        console.error('Error adding questions to group:', error);
        showNotification(`Error: ${error.message}`, 'error');
    })
    .finally(() => {
        // Restore button state
        addButton.disabled = false;
        addButton.classList.remove('edit-group-btn-loading');
        addButton.innerHTML = originalText;
    });
}

// Question Management
function editQuestion(questionId) {
    fetch(`/admin/questions/get/${questionId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // Check if we got redirected to login page
            if (response.url.includes('/admin/login')) {
                throw new Error('Authentication required');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                populateEditForm(data.question);
                openModal('editQuestionModal');
            } else {
                console.error('Error loading question:', data.message);
                showNotification('Error loading question: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error loading question:', error);
            if (handleAuthError(error)) {
                // User is not authenticated, handled in handleAuthError
            } else {
                showNotification('Error loading question. Please try again.', 'error');
            }
        });
}

function populateEditForm(question) {
    document.getElementById('edit-question-id').value = question.id;
    document.getElementById('edit-question').value = question.question;
    document.getElementById('edit-question-type').value = question.question_type;
    document.getElementById('edit-category').value = question.category;
    document.getElementById('edit-answer').value = question.answer;
    document.getElementById('edit-explanation').value = question.explanation || '';
    document.getElementById('edit-number').value = question.numb;
}

function deleteQuestion(questionId) {
    console.log('Requesting deletion of question:', questionId);
    
    fetch(`/admin/questions/delete/${questionId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // Check if we got redirected to login page
        if (response.url.includes('/admin/login')) {
            throw new Error('Authentication required');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Question deleted successfully:', questionId);
            showNotification('Question deleted successfully', 'success');
            // Emit WebSocket event to refresh data
            if (window.socketClient) {
                window.socketClient.emit('question_deleted', { questionId });
            }
        } else {
            console.error('Error deleting question:', data.message);
            showNotification('Error deleting question: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting question:', error);
        if (handleAuthError(error)) {
            // User is not authenticated, handled in handleAuthError
        } else {
            showNotification('Error deleting question. Please try again.', 'error');
        }
    });
}

// Enhanced loading and feedback utilities
function showModalLoading(modalId, message = 'Loading...') {
    const modal = document.getElementById(modalId);
    if (modal) {
        const modalContent = modal.querySelector('.modal-content');
        let loadingOverlay = modal.querySelector('.modal-loading');
        
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'modal-loading';
            loadingOverlay.innerHTML = `
                <div>
                    <div class="loading-spinner"></div>
                    <div class="loading-text">${message}</div>
                </div>
            `;
            modalContent.appendChild(loadingOverlay);
        } else {
            loadingOverlay.querySelector('.loading-text').textContent = message;
            loadingOverlay.classList.remove('hidden');
        }
    }
}

function hideModalLoading(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const loadingOverlay = modal.querySelector('.modal-loading');
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
        }
    }
}

function setButtonLoading(buttonElement, isLoading = true) {
    if (isLoading) {
        buttonElement.classList.add('loading');
        buttonElement.disabled = true;
        buttonElement.setAttribute('aria-busy', 'true');
    } else {
        buttonElement.classList.remove('loading');
        buttonElement.disabled = false;
        buttonElement.setAttribute('aria-busy', 'false');
    }
}

// Enhanced form submission with loading states
function submitFormWithLoading(formId, buttonId, loadingMessage = 'Processing...') {
    const form = document.getElementById(formId);
    const button = document.getElementById(buttonId);
    
    if (!form || !button) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Set loading state
        setButtonLoading(button, true);
        const originalText = button.textContent;
        button.textContent = loadingMessage;
        
        // Get form data
        const formData = new FormData(form);
        
        // Submit via fetch
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message || 'Operation completed successfully!', 'success');
                // Close modal and refresh if needed
                const modalId = form.closest('.modal').id;
                closeModal(modalId);
                if (typeof loadQuestions === 'function') {
                    loadQuestions();
                }
            } else {
                showNotification(data.message || 'Operation failed. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        })
        .finally(() => {
            // Reset button state
            setButtonLoading(button, false);
            button.textContent = originalText;
        });
    });
}

// Form Submissions
function setupEventListeners() {
    // Add Question Form
    const addQuestionForm = document.getElementById('addQuestionForm');
    if (addQuestionForm) {
        addQuestionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitQuestionForm(this, 'add');
        });
    }
    
    // Edit Question Form
    const editQuestionForm = document.getElementById('editQuestionForm');
    if (editQuestionForm) {
        editQuestionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitQuestionForm(this, 'edit');
        });
    }
    
    // Group Ungrouped Form
    const groupUngroupedForm = document.getElementById('groupUngroupedForm');
    if (groupUngroupedForm) {
        groupUngroupedForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitGroupingForm(this);
        });
    }
    
    // Group action radio buttons
    const addToExisting = document.getElementById('add-to-existing');
    const createNewGroup = document.getElementById('create-new-group');
    const existingGroupType = document.getElementById('existing-group-section');
    const newGroupSection = document.getElementById('new-group-section');
    
    if (addToExisting && createNewGroup) {
        addToExisting.addEventListener('change', function() {
            if (this.checked) {
                existingGroupType.style.display = 'block';
                newGroupSection.style.display = 'none';
            }
        });
        
        createNewGroup.addEventListener('change', function() {
            if (this.checked) {
                existingGroupType.style.display = 'none';
                newGroupSection.style.display = 'block';
            }
        });
    }
    
    // Edit Group Modal Event Listeners
    const refreshUngroupedBtn = document.getElementById('refresh-ungrouped-btn');
    if (refreshUngroupedBtn) {
        refreshUngroupedBtn.addEventListener('click', function() {
            console.log('Refresh ungrouped questions clicked');
            const groupIdField = document.getElementById('edit-group-id');
            const currentGroupId = groupIdField ? groupIdField.value : null;
            loadUngroupedQuestionsForEdit(currentGroupId);
        });
    }
    
    const addSelectedQuestionsBtn = document.getElementById('add-selected-questions-btn');
    if (addSelectedQuestionsBtn) {
        addSelectedQuestionsBtn.addEventListener('click', function() {
            addSelectedQuestionsToGroup();
        });
    }
}

function submitQuestionForm(form, action) {
    const formData = new FormData(form);
    const url = action === 'add' ? '/admin/questions/add' : `/admin/questions/edit/${formData.get('question_id')}`;
    const method = 'POST';  // Always use POST for form submissions
    
    // Process options for multiple choice questions
    if (formData.get('question_type') === 'multiple_choice') {
        const optionInputs = form.querySelectorAll('input[name="options[]"]');
        optionInputs.forEach((input, index) => {
            if (input.value.trim()) {
                formData.append(`option${index + 1}`, input.value.trim());
            }
        });
    }
    
    fetch(url, {
        method: method,
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log(`Question ${action}ed successfully:`, data);
            showNotification(`Question ${action}ed successfully`, 'success');
            closeModal(action === 'add' ? 'addQuestionModal' : 'editQuestionModal');
            
            // Emit WebSocket event to refresh data
            if (window.socketClient) {
                window.socketClient.emit(`question_${action}ed`, { 
                    questionId: data.question_id || formData.get('question_id'),
                    action: action
                });
            }
        } else {
            console.error('Error saving question:', data.message);
            showNotification('Error saving question: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error saving question:', error);
        showNotification('Error saving question. Please try again.', 'error');
    });
}

function submitGroupingForm(form) {
    const formData = new FormData(form);
    const selectedQuestions = Array.from(document.querySelectorAll('#ungroupedQuestionsModal input[name="selected_questions"]:checked')).map(cb => cb.value);
    
    if (selectedQuestions.length === 0) {
        console.warn('No questions selected for grouping');
        showNotification('Please select at least one question to group.', 'warning');
        return;
    }
    
    // Add selected questions to form data
    selectedQuestions.forEach(id => formData.append('question_ids', id));
    
    fetch('/admin/questions/group_questions', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Questions grouped successfully:', data);
            showNotification('Questions grouped successfully', 'success');
            closeModal('ungroupedQuestionsModal');
            
            // Emit WebSocket event to refresh data
            if (window.socketClient) {
                window.socketClient.emit('questions_grouped', { 
                    questionIds: selectedQuestions,
                    groupId: data.group_id,
                    groupName: formData.get('group_name') || formData.get('existing_group')
                });
            }
        } else {
            console.error('Error grouping questions:', data.message);
            showNotification('Error grouping questions: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error grouping questions:', error);
        showNotification('Error grouping questions. Please try again.', 'error');
    });
}

// Notification System
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Locate or create notification container using class (no global ID)
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 24px;
            right: 24px;
            z-index: 15000;
            pointer-events: none;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        background: rgba(139, 92, 246, 0.08);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 217, 255, 0.15);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        color: ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#39FF14' : type === 'warning' ? '#ffd43b' : '#00D9FF'};
        border-left: 4px solid ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#39FF14' : type === 'warning' ? '#ffd43b' : '#00D9FF'};
        box-shadow: 0 8px 32px rgba(26, 35, 126, 0.4);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        pointer-events: auto;
        cursor: pointer;
        max-width: 350px;
        word-wrap: break-word;
        font-weight: 500;
        font-size: 0.95rem;
        position: relative;
        overflow: hidden;
    `;
    
    // Add cyber-themed glow effect
    const glowEffect = document.createElement('div');
    glowEffect.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(135deg, #00D9FF, #8B5CF6);
        opacity: 0.8;
    `;
    notification.appendChild(glowEffect);
    
    notification.textContent = message;
    notification.title = 'Click to dismiss';
    
    // Add click to dismiss
    notification.addEventListener('click', () => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    });
    
    container.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// WebSocket Event Listeners for Real-time Updates
function setupWebSocketListeners() {
    if (!window.socketClient) {
        console.log('WebSocket client not available, skipping real-time setup');
        return;
    }
    
    // Listen for question-related events
    window.socketClient.on('question_added', (data) => {
        console.log('Question added via WebSocket:', data);
        showNotification('Question added successfully', 'success');
        loadUngroupedQuestions();
        if (typeof loadQuestionGroups === 'function') {
            loadQuestionGroups();
        }
    });
    
    window.socketClient.on('question_updated', (data) => {
        console.log('Question updated via WebSocket:', data);
        showNotification('Question updated successfully', 'success');
        loadUngroupedQuestions();
        if (typeof loadQuestionGroups === 'function') {
            loadQuestionGroups();
        }
    });
    
    window.socketClient.on('question_deleted', (data) => {
        console.log('Question deleted via WebSocket:', data);
        showNotification('Question deleted successfully', 'success');
        loadUngroupedQuestions();
        if (typeof loadQuestionGroups === 'function') {
            loadQuestionGroups();
        }
    });
    
    window.socketClient.on('question_group_created', (data) => {
        console.log('Question group created via WebSocket:', data);
        showNotification('Question group created successfully', 'success');
        loadUngroupedQuestions();
        if (typeof loadQuestionGroups === 'function') {
            loadQuestionGroups();
        }
    });
    
    window.socketClient.on('question_group_deleted', (data) => {
        console.log('Question group deleted via WebSocket:', data);
        showNotification('Question group deleted successfully', 'success');
        loadUngroupedQuestions();
        if (typeof loadQuestionGroups === 'function') {
            loadQuestionGroups();
        }
    });
    
    window.socketClient.on('questions_grouped', (data) => {
        console.log('Questions grouped via WebSocket:', data);
        showNotification('Questions grouped successfully', 'success');
        loadUngroupedQuestions();
        if (typeof loadQuestionGroups === 'function') {
            loadQuestionGroups();
        }
    });
    
    window.socketClient.on('question_removed_from_group', (data) => {
        console.log('Question removed from group via WebSocket:', data);
        showNotification('Question removed from group successfully', 'success');
        loadUngroupedQuestions();
        if (typeof loadQuestionGroups === 'function') {
            loadQuestionGroups();
        }
        // Close the group modal if it's open
        const groupModal = document.getElementById('groupQuestionsModal');
        if (groupModal && groupModal.style.display === 'flex') {
            closeModal('groupQuestionsModal');
        }
    });
    
    console.log('WebSocket listeners for questions management setup complete');
}

// Initialize WebSocket listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Setup WebSocket listeners after a short delay to ensure socketClient is available
    setTimeout(setupWebSocketListeners, 1000);
});

// Also setup listeners if socketClient becomes available later
if (window.socketClient) {
    setupWebSocketListeners();
} else {
    // Check periodically for socketClient availability
    const checkSocketClient = setInterval(() => {
        if (window.socketClient) {
            setupWebSocketListeners();
            clearInterval(checkSocketClient);
        }
    }, 1000);
    
    // Stop checking after 30 seconds
    setTimeout(() => clearInterval(checkSocketClient), 30000);
}

// Utility functions
function playClickSound() {
    const clickSound = document.getElementById('clickSound');
    if (clickSound) {
        clickSound.currentTime = 0;
        clickSound.play().catch(e => console.log('Could not play sound:', e));
    }
}

// Add click sound to buttons
document.addEventListener('click', function(e) {
    if (e.target.matches('button, .btn, .btn-primary, .btn-secondary')) {
        playClickSound();
    }
});

// Enhanced functions - replacing placeholders with actual functionality
function addQuestionsToGroup(groupId) {
    console.log('Add questions to group functionality called for group:', groupId);
    // First, load ungrouped questions
    loadUngroupedQuestionsInModal();
    // Then open the modal
    openModal('ungroupedQuestionsModal');
    // Store the group ID for later use
    window.currentGroupId = groupId;
}

function loadUngroupedQuestionsInModal() {
    const container = document.querySelector('#ungroupedQuestionsModal .ungrouped-questions-container');
    
    if (!container) return;
 
    container.innerHTML = '<div class="loading-spinner" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading questions...</div>';
    
    fetch('/admin/questions/ungrouped?format=json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                displayUngroupedInModal(data.questions);
            } else {
                container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">Error loading questions</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">Error loading questions. Please try again.</p>';
        });
}


// Icon loading error handler
document.addEventListener('DOMContentLoaded', function() {
    // Check if Font Awesome loaded
    const fontAwesome = document.querySelector('link[href*="font-awesome"]');
    if (fontAwesome) {
        fontAwesome.onerror = function() {
            console.warn('Font Awesome failed to load, using fallback');
            // Add fallback CSS
            const fallbackCSS = document.createElement('style');
            fallbackCSS.textContent = `
                .fas::before, .far::before, .fab::before { 
                    content: "⚙️"; 
                    font-family: initial; 
                }
                .fas.fa-network-wired::before { content: "🔗"; }
                .fas.fa-database::before { content: "🗄️"; }
                .fas.fa-layer-group::before { content: "📚"; }
                .fas.fa-question-circle::before { content: "❓"; }
                .fas.fa-mouse-pointer::before { content: "👆"; }
                .fas.fa-share-alt::before { content: "🔗"; }
                .fas.fa-list::before { content: "📋"; }
                .fas.fa-edit::before { content: "✏️"; }
                .fas.fa-trash::before { content: "🗑️"; }
                .fas.fa-spinner::before { content: "⚡"; }
            `;
            document.head.appendChild(fallbackCSS);
        };
    }
    
    // Check if Boxicons loaded
    const boxicons = document.querySelector('link[href*="boxicons"]');
    if (boxicons) {
        boxicons.onerror = function() {
            console.warn('Boxicons failed to load, using fallback');
            // Add fallback CSS
            const fallbackCSS = document.createElement('style');
            fallbackCSS.textContent = `
                .bx::before { 
                    content: "📋"; 
                    font-family: initial; 
                }
                .bxs-folder-plus::before { content: "📁"; }
                .bx-plus::before { content: "➕"; }
                .bxs-info-circle::before { content: "ℹ️"; }
                .bxs-folder::before { content: "📂"; }
                .bx-help-circle::before { content: "❓"; }
            `;
            document.head.appendChild(fallbackCSS);
        };
    }
    
    // Verify icons are loaded after a short delay
    setTimeout(function() {
        const icons = document.querySelectorAll('i[class*="fas"], i[class*="bx"]');
        icons.forEach(function(icon) {
            const computedStyle = window.getComputedStyle(icon, '::before');
            if (!computedStyle.content || computedStyle.content === 'none') {
                icon.classList.add('icon-loading');
                console.warn('Icon not loaded properly:', icon.className);
            }
        });
    }, 500);
});
// questions.js - JavaScript for questions management

document.addEventListener('DOMContentLoaded', function() {
    initializeQuestionForm();
    loadUngroupedQuestions();
    setupEventListeners();
});

// Modal Management
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Reset forms when closing modals
        const forms = modal.querySelectorAll('form');
        forms.forEach(form => form.reset());
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
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
                <p style="color: var(--text-muted); margin-bottom: 20px;">${groupDescription || 'No description available'}</p>
                <div class="questions-list">
                    ${questions.length > 0 ? questions.map(q => `
                        <div class="question-item" style="background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <h4 style="color: var(--text-primary); margin: 0 0 8px 0;">Question ${q.numb}</h4>
                                    <p style="color: var(--text-secondary); margin: 0 0 8px 0;">${q.question}</p>
                                    <div style="display: flex; gap: 12px; font-size: 0.85rem; color: var(--text-muted);">
                                        <span>Type: ${q.question_type}</span>
                                        <span>Category: ${q.category}</span>
                                    </div>
                                </div>
                                <div style="display: flex; gap: 8px;">
                                    <button class="btn btn-small" onclick="editQuestion(${q.id})">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="removeFromGroup(${q.id}, ${groupId})">Remove</button>
                                </div>
                            </div>
                        </div>
                    `).join('') : '<p style="color: var(--text-muted); text-align: center; padding: 40px;">No questions in this group.</p>'}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('groupQuestionsModal')">Close</button>
                <button class="btn" onclick="addQuestionsToGroup(${groupId})">Add Questions</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
}

function editQuestionGroup(groupId, groupName, groupDescription) {
    // Populate edit form and open modal
    document.getElementById('edit-group-id').value = groupId;
    document.getElementById('edit-group-name').value = groupName;
    document.getElementById('edit-group-description').value = groupDescription;
    openModal('editGroupModal');
}

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
    const categoryFilter = document.getElementById('main-ungrouped-category-filter');
    
    if (!container || !categoryFilter) return;
    
    function fetchUngrouped() {
        const category = categoryFilter.value;
        const url = category === 'all' ? '/admin/questions/ungrouped?format=json' : `/admin/questions/ungrouped?category=${category}&format=json`;
        
        console.log('Loading ungrouped questions from:', url);
        container.innerHTML = '<div class="loading-spinner" style="text-align: center; color: rgba(255, 255, 255, 0.6); padding: 40px;">Loading ungrouped questions...</div>';
        
        fetch(url)
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);
                if (data.success) {
                    console.log('Number of questions:', data.questions.length);
                    displayUngroupedQuestions(data.questions);
                } else {
                    console.error('API returned success: false', data);
                    container.innerHTML = '<p style="color: rgba(255, 255, 255, 0.6); text-align: center; padding: 40px;">Error loading questions</p>';
                }
            })
            .catch(error => {
                console.error('Error loading ungrouped questions:', error);
                container.innerHTML = '<p style="color: rgba(255, 255, 255, 0.6); text-align: center; padding: 40px;">Error loading questions. Please try again.</p>';
            });
    }
    
    categoryFilter.addEventListener('change', fetchUngrouped);
    fetchUngrouped(); // Initial load
}

function displayUngroupedQuestions(questions) {
    console.log('Displaying questions in UI:', questions);
    const container = document.getElementById('main-ungrouped-container');
    
    if (questions.length === 0) {
        container.innerHTML = '<p style="color: rgba(255, 255, 255, 0.6); text-align: center; padding: 40px;">No ungrouped questions found for this category.</p>';
        return;
    }
    
    console.log('Rendering', questions.length, 'questions');
    
    container.innerHTML = questions.map(q => {
        console.log('Rendering question:', q.id, q.question || q.content);
        return `
            <div class="question-item" style="background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 8px; padding: 16px; margin-bottom: 12px; display: flex; align-items: start; gap: 12px;">
                <input type="checkbox" class="question-checkbox" value="${q.id}" style="margin-top: 4px;">
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <h4 style="color: var(--cyber-glow); margin: 0;">Question ${q.numb || q.id}</h4>
                        <div style="display: flex; gap: 8px;">
                            <button class="btn btn-small" onclick="editQuestion(${q.id})" style="background: var(--gradient-primary); font-size: 0.8rem;">Edit</button>
                            <button class="btn btn-small" onclick="deleteQuestion(${q.id})" style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); font-size: 0.8rem;">Delete</button>
                        </div>
                    </div>
                    <p style="color: rgba(255, 255, 255, 0.9); margin: 0 0 8px 0;">${q.question || q.content || 'No content'}</p>
                    <div style="display: flex; gap: 12px; font-size: 0.85rem; color: rgba(255, 255, 255, 0.7);">
                        <span>Type: ${q.type || 'Unknown'}</span>
                        <span>Category: ${q.category || 'None'}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    console.log('Questions rendered successfully');
    
    // Update checkbox listeners
    updateCheckboxListeners();
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
    const categoryFilter = document.getElementById('ungrouped-category-filter');
    
    if (!container) return;
    
    fetch('/admin/questions/ungrouped')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayUngroupedInModal(data.questions);
            } else {
                container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">Error loading questions</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">Error loading questions</p>';
        });
}

function displayUngroupedInModal(questions) {
    const container = document.querySelector('#ungroupedQuestionsModal .ungrouped-questions-container');
    
    container.innerHTML = questions.map(q => `
        <div class="question-item" style="background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; align-items: start; gap: 8px;">
            <input type="checkbox" name="selected_questions" value="${q.id}" style="margin-top: 4px;">
            <div style="flex: 1;">
                <h5 style="color: var(--text-primary); margin: 0 0 4px 0;">Q${q.numb}: ${q.question.substring(0, 100)}${q.question.length > 100 ? '...' : ''}</h5>
                <div style="font-size: 0.8rem; color: var(--text-muted);">
                    <span>Type: ${q.question_type}</span> | <span>Category: ${q.category}</span>
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

// Question Management
function editQuestion(questionId) {
    fetch(`/admin/questions/${questionId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
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
            showNotification('Error loading question. Please try again.', 'error');
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
    
    fetch(`/admin/questions/${questionId}`, {
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
        showNotification('Error deleting question. Please try again.', 'error');
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
}

function submitQuestionForm(form, action) {
    const formData = new FormData(form);
    const url = action === 'add' ? '/admin/questions/add' : `/admin/questions/${formData.get('question_id')}/edit`;
    const method = action === 'add' ? 'POST' : 'PUT';
    
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
    
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        background: var(--glass-bg, rgba(255, 255, 255, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        color: ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : type === 'warning' ? '#ffd43b' : '#74c0fc'};
        border-left: 4px solid ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : type === 'warning' ? '#ffd43b' : '#74c0fc'};
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        pointer-events: auto;
        cursor: pointer;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
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

// Missing functions
function editQuestionGroup(groupId, groupName, groupDescription) {
    console.log('Edit group functionality called for:', groupName);
    showNotification('Edit group functionality is not yet implemented. Please delete and recreate the group if changes are needed.', 'info');
}

function addQuestionsToGroup(groupId) {
    console.log('Add questions to group functionality called for group:', groupId);
    showNotification('Add questions to group functionality is not yet implemented. Please use the main interface to manage group questions.', 'info');
}

function loadUngroupedQuestionsInModal() {
    const container = document.querySelector('#ungroupedQuestionsModal .ungrouped-questions-container');
    const categoryFilter = document.getElementById('ungrouped-category-filter');
    
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
// essay.js - JavaScript for essay response management

document.addEventListener('DOMContentLoaded', function() {
    console.log('Essay administration JavaScript loaded');
    initializeEssayHandlers();
    setupModalHandlers();
});

// Initialize essay button handlers
function initializeEssayHandlers() {
    // View essay buttons
    document.querySelectorAll('.view-essay-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const essayData = {
                id: this.dataset.id,
                username: this.dataset.username,
                question: this.dataset.question,
                answer: this.dataset.answer,
                category: this.dataset.category,
                date: this.dataset.date,
                status: this.dataset.status,
                score: this.dataset.score
            };
            showEssayModal(essayData);
        });
    });

    // Edit essay buttons
    document.querySelectorAll('.edit-essay-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const essayId = this.dataset.id;
            showEditEssayModal(essayId);
        });
    });

    // Delete essay buttons (forms)
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const essayId = this.querySelector('.delete-essay-btn').dataset.id;
            if (confirm('Are you sure you want to delete this essay response? This action cannot be undone.')) {
                this.submit();
            }
        });
    });
}

// Setup modal handlers
function setupModalHandlers() {
    // Essay view modal handlers
    const essayModal = document.getElementById('essayModal');
    const editEssayModal = document.getElementById('editEssayModal');
    
    // Close buttons
    document.querySelectorAll('.close, #close-modal-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            closeModal(essayModal);
        });
    });

    document.querySelectorAll('#edit-close, #edit-cancel-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            closeModal(editEssayModal);
        });
    });

    // Grade save button
    const saveGradeBtn = document.getElementById('save-grade-btn');
    if (saveGradeBtn) {
        saveGradeBtn.addEventListener('click', function() {
            saveEssayGrade();
        });
    }

    // Edit form submission
    const editForm = document.getElementById('edit-essay-form');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveEssayEdit();
        });
    }

    // Close modals when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === essayModal) {
            closeModal(essayModal);
        }
        if (e.target === editEssayModal) {
            closeModal(editEssayModal);
        }
    });
}

// Show essay view modal
function showEssayModal(essayData) {
    console.log('Showing essay modal for:', essayData);
    
    // Populate modal fields
    document.getElementById('essay-id').textContent = essayData.id;
    document.getElementById('essay-username').textContent = essayData.username;
    document.getElementById('essay-category').textContent = essayData.category;
    document.getElementById('essay-date').textContent = essayData.date;
    document.getElementById('essay-status').textContent = essayData.status;
    document.getElementById('essay-score').textContent = essayData.score || 'Not graded';
    document.getElementById('essay-question').textContent = essayData.question;
    document.getElementById('essay-answer').textContent = essayData.answer;
    
    // Set up grading section
    const gradeInput = document.getElementById('grade-input');
    if (gradeInput && essayData.score) {
        gradeInput.value = essayData.score;
    }
    
    // Store essay ID for grading
    document.getElementById('save-grade-btn').dataset.essayId = essayData.id;
    
    // Show modal
    showModal(document.getElementById('essayModal'));
}

// Show edit essay modal
function showEditEssayModal(essayId) {
    console.log('Showing edit modal for essay:', essayId);
    
    // Fetch essay data
    fetch(`/admin/api/essays/${essayId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                populateEditModal(data.essay);
                showModal(document.getElementById('editEssayModal'));
            } else {
                console.error('Error loading essay:', data.message);
                showNotification('Error loading essay: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error loading essay:', error);
            showNotification('Error loading essay. Please try again.', 'error');
        });
}

// Populate edit modal with essay data
function populateEditModal(essay) {
    document.getElementById('edit-essay-id').value = essay.id;
    document.getElementById('edit-question').value = essay.question_text;
    document.getElementById('edit-answer').value = essay.response_text;
    document.getElementById('edit-category').value = essay.category;
}

// Save essay grade
function saveEssayGrade() {
    const essayId = document.getElementById('save-grade-btn').dataset.essayId;
    const gradeInput = document.getElementById('grade-input');
    const grade = parseInt(gradeInput.value);
    
    if (!grade || grade < 0 || grade > 100) {
        showNotification('Please enter a valid grade between 0 and 100', 'error');
        return;
    }
    
    console.log('Saving grade for essay:', essayId, 'Grade:', grade);
    
    // Disable button while saving
    const saveBtn = document.getElementById('save-grade-btn');
    const originalText = saveBtn.textContent;
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
    
    fetch(`/admin/api/essays/${essayId}/grade`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ grade: grade })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('Grade saved successfully!', 'success');
            
            // Update the displayed score
            document.getElementById('essay-score').textContent = grade;
            document.getElementById('essay-status').textContent = 'Reviewed';
            
            // Refresh the page to show updated data
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            console.error('Error saving grade:', data.message);
            showNotification('Error saving grade: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error saving grade:', error);
        showNotification('Error saving grade. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable button
        saveBtn.disabled = false;
        saveBtn.textContent = originalText;
    });
}

// Save essay edit
function saveEssayEdit() {
    const formData = new FormData();
    formData.append('essay_id', document.getElementById('edit-essay-id').value);
    formData.append('question_text', document.getElementById('edit-question').value);
    formData.append('response_text', document.getElementById('edit-answer').value);
    formData.append('category', document.getElementById('edit-category').value);
    
    console.log('Saving essay edit...');
    
    fetch('/admin/essays/edit', {
        method: 'POST',
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
            showNotification('Essay updated successfully!', 'success');
            closeModal(document.getElementById('editEssayModal'));
            
            // Refresh the page to show updated data
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            console.error('Error updating essay:', data.message);
            showNotification('Error updating essay: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error updating essay:', error);
        showNotification('Error updating essay. Please try again.', 'error');
    });
}

// Modal utilities
function showModal(modal) {
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Add fade-in animation
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.opacity = '1';
        }, 10);
    }
}

function closeModal(modal) {
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }, 200);
    }
}

// Notification system
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
            </span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
    
    // Also use browser alert as fallback
    if (type === 'error') {
        alert(message);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'flex') {
                closeModal(modal);
            }
        });
    }
});

// Add CSS for notifications if not present
const notificationCSS = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 400px;
        margin-bottom: 10px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .notification-success {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
    }
    
    .notification-error {
        background: linear-gradient(45deg, #f44336, #d32f2f);
        color: white;
    }
    
    .notification-info {
        background: linear-gradient(45deg, #2196F3, #1976D2);
        color: white;
    }
    
    .notification-content {
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .notification-icon {
        font-size: 16px;
    }
    
    .notification-message {
        flex: 1;
        font-weight: 500;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .notification-close:hover {
        opacity: 0.7;
    }
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = notificationCSS;
document.head.appendChild(style);

console.log('Essay administration system ready');

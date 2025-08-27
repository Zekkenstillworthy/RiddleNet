/**
 * Enhanced Tutorial Editor for Simulation Editor
 * Integrates with tutorial_controller.py backend
 */

class TutorialEditorManager {
    constructor() {
        this.currentTutorial = null;
        this.currentSteps = [];
        this.selectedStep = null;
        this.isDragging = false;
        this.draggedStep = null;
        this.mediaUploadUrl = '/admin/tutorials/steps';
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Tutorial toolbar buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#add-tutorial-step')) {
                this.addTutorialStep();
            } else if (e.target.matches('#preview-tutorial')) {
                this.previewTutorial();
            } else if (e.target.matches('#save-tutorial')) {
                this.saveTutorial();
            } else if (e.target.matches('#reorder-steps')) {
                this.toggleReorderMode();
            } else if (e.target.closest('.tutorial-step-item')) {
                this.selectStep(e.target.closest('.tutorial-step-item'));
            } else if (e.target.matches('.delete-step')) {
                this.deleteStep(e.target.dataset.stepId);
            } else if (e.target.matches('.move-step-up')) {
                this.moveStep(e.target.dataset.stepId, 'up');
            } else if (e.target.matches('.move-step-down')) {
                this.moveStep(e.target.dataset.stepId, 'down');
            }
        });

        // Tutorial content editor
        document.addEventListener('change', (e) => {
            if (e.target.matches('#tutorial-step-type')) {
                this.updateStepType(e.target.value);
            } else if (e.target.matches('#tutorial-media-file')) {
                this.handleMediaUpload(e.target);
            }
        });

        // Auto-save tutorial content
        document.addEventListener('input', (e) => {
            if (e.target.matches('#tutorial-step-content') || 
                e.target.matches('#tutorial-step-caption')) {
                this.debounceAutoSave();
            }
        });
    }

    async loadTutorial(simulationId) {
        try {
            const response = await fetch(`/admin/tutorials/${simulationId}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentTutorial = data.tutorial;
                this.currentSteps = data.tutorial.steps || [];
                this.renderSteps();
                this.showSuccessMessage('Tutorial loaded successfully');
            } else {
                this.showErrorMessage('Failed to load tutorial');
            }
        } catch (error) {
            console.error('Error loading tutorial:', error);
            this.showErrorMessage('Error loading tutorial');
        }
    }

    renderSteps() {
        const stepsList = document.getElementById('tutorial-steps-list');
        if (!stepsList) return;

        if (this.currentSteps.length === 0) {
            stepsList.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-plus-circle fa-3x mb-2"></i>
                    <p>No tutorial steps yet. Click "Add Step" to get started.</p>
                </div>
            `;
            return;
        }

        stepsList.innerHTML = this.currentSteps
            .sort((a, b) => a.order_index - b.order_index)
            .map(step => this.createStepHTML(step))
            .join('');
    }

    createStepHTML(step) {
        const stepTypeIcon = this.getStepTypeIcon(step.step_type);
        const isSelected = this.selectedStep && this.selectedStep.id === step.id;
        
        return `
            <div class="tutorial-step-item ${isSelected ? 'selected' : ''}" 
                 data-step-id="${step.id}" 
                 draggable="true">
                <div class="step-header">
                    <div class="step-info">
                        <i class="fas ${stepTypeIcon} me-2"></i>
                        <span class="step-number">${step.order_index}</span>
                        <span class="step-title">${step.step_type}</span>
                    </div>
                    <div class="step-actions">
                        <button class="btn btn-sm btn-outline-primary move-step-up" 
                                data-step-id="${step.id}" title="Move Up">
                            <i class="fas fa-arrow-up"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-primary move-step-down" 
                                data-step-id="${step.id}" title="Move Down">
                            <i class="fas fa-arrow-down"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-step" 
                                data-step-id="${step.id}" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="step-preview">
                    ${this.createStepPreview(step)}
                </div>
            </div>
        `;
    }

    createStepPreview(step) {
        switch (step.step_type) {
            case 'text':
                return `<p class="text-muted small">${(step.content || '').substring(0, 100)}...</p>`;
            case 'image':
                return step.media_url ? 
                    `<img src="${step.media_url}" class="step-preview-image" alt="Step image">
                     <p class="text-muted small">${step.caption || ''}</p>` :
                    `<p class="text-muted small">No image uploaded</p>`;
            case 'video':
                return step.media_url ? 
                    `<video class="step-preview-video" src="${step.media_url}" controls></video>
                     <p class="text-muted small">${step.caption || ''}</p>` :
                    `<p class="text-muted small">No video uploaded</p>`;
            case 'code':
                return `<pre class="step-preview-code"><code>${(step.content || '').substring(0, 50)}...</code></pre>`;
            case 'tip':
                return `<div class="alert alert-info small">💡 ${(step.content || '').substring(0, 80)}...</div>`;
            default:
                return `<p class="text-muted small">${(step.content || '').substring(0, 100)}...</p>`;
        }
    }

    getStepTypeIcon(stepType) {
        const icons = {
            'text': 'fa-align-left',
            'image': 'fa-image',
            'video': 'fa-video',
            'code': 'fa-code',
            'tip': 'fa-lightbulb'
        };
        return icons[stepType] || 'fa-circle';
    }

    selectStep(stepElement) {
        // Remove previous selection
        document.querySelectorAll('.tutorial-step-item').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Select new step
        stepElement.classList.add('selected');
        const stepId = parseInt(stepElement.dataset.stepId);
        this.selectedStep = this.currentSteps.find(s => s.id === stepId);
        
        this.populateStepEditor();
    }

    populateStepEditor() {
        if (!this.selectedStep) {
            this.clearStepEditor();
            return;
        }

        const editor = document.getElementById('tutorial-content-editor');
        if (!editor) return;

        editor.style.display = 'block';

        // Populate form fields
        document.getElementById('tutorial-step-type').value = this.selectedStep.step_type;
        document.getElementById('tutorial-step-content').value = this.selectedStep.content || '';
        document.getElementById('tutorial-step-caption').value = this.selectedStep.caption || '';

        // Show/hide relevant fields based on step type
        this.updateStepType(this.selectedStep.step_type);

        // Show media preview if available
        if (this.selectedStep.media_url) {
            this.showMediaPreview(this.selectedStep.media_url, this.selectedStep.step_type);
        }
    }

    clearStepEditor() {
        const editor = document.getElementById('tutorial-content-editor');
        if (!editor) return;

        editor.style.display = 'none';
        document.getElementById('tutorial-step-content').value = '';
        document.getElementById('tutorial-step-caption').value = '';
        this.clearMediaPreview();
    }

    updateStepType(stepType) {
        const contentField = document.getElementById('tutorial-step-content');
        const mediaField = document.getElementById('tutorial-media-file');
        const captionField = document.getElementById('tutorial-step-caption');
        const mediaUploadSection = document.querySelector('.media-upload-section');
        const contentSection = document.querySelector('.content-section');

        // Update field labels and visibility based on step type
        switch (stepType) {
            case 'image':
            case 'video':
                mediaUploadSection.style.display = 'block';
                contentSection.style.display = 'none';
                captionField.parentElement.style.display = 'block';
                break;
            case 'text':
                mediaUploadSection.style.display = 'none';
                contentSection.style.display = 'block';
                captionField.parentElement.style.display = 'none';
                contentField.placeholder = 'Enter tutorial text content...';
                break;
            case 'code':
                mediaUploadSection.style.display = 'none';
                contentSection.style.display = 'block';
                captionField.parentElement.style.display = 'none';
                contentField.placeholder = 'Enter code snippet...';
                break;
            case 'tip':
                mediaUploadSection.style.display = 'none';
                contentSection.style.display = 'block';
                captionField.parentElement.style.display = 'none';
                contentField.placeholder = 'Enter tip or hint text...';
                break;
        }
    }

    async addTutorialStep() {
        if (!this.currentTutorial) {
            this.showErrorMessage('No tutorial loaded');
            return;
        }

        const stepData = {
            step_type: 'text',
            content: 'New tutorial step',
            order_index: this.currentSteps.length + 1
        };

        try {
            const response = await fetch(`/admin/tutorials/${this.currentTutorial.simulation_id}/steps`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(stepData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentSteps.push(data.step);
                this.renderSteps();
                this.showSuccessMessage('Tutorial step added');
                
                // Auto-select the new step
                setTimeout(() => {
                    const newStepElement = document.querySelector(`[data-step-id="${data.step.id}"]`);
                    if (newStepElement) {
                        this.selectStep(newStepElement);
                    }
                }, 100);
            } else {
                this.showErrorMessage('Failed to add tutorial step');
            }
        } catch (error) {
            console.error('Error adding tutorial step:', error);
            this.showErrorMessage('Error adding tutorial step');
        }
    }

    async deleteStep(stepId) {
        if (!confirm('Are you sure you want to delete this tutorial step?')) {
            return;
        }

        try {
            const response = await fetch(`/admin/tutorials/steps/${stepId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentSteps = this.currentSteps.filter(s => s.id !== parseInt(stepId));
                this.renderSteps();
                this.clearStepEditor();
                this.showSuccessMessage('Tutorial step deleted');
            } else {
                this.showErrorMessage('Failed to delete tutorial step');
            }
        } catch (error) {
            console.error('Error deleting tutorial step:', error);
            this.showErrorMessage('Error deleting tutorial step');
        }
    }

    async moveStep(stepId, direction) {
        const step = this.currentSteps.find(s => s.id === parseInt(stepId));
        if (!step) return;

        const currentIndex = step.order_index;
        const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;

        // Find step to swap with
        const swapStep = this.currentSteps.find(s => s.order_index === newIndex);
        if (!swapStep) return;

        // Update order indices
        step.order_index = newIndex;
        swapStep.order_index = currentIndex;

        await this.updateStep(step.id, { order_index: newIndex });
        await this.updateStep(swapStep.id, { order_index: currentIndex });

        this.renderSteps();
    }

    async handleMediaUpload(fileInput) {
        if (!this.selectedStep) {
            this.showErrorMessage('Please select a tutorial step first');
            return;
        }

        const file = fileInput.files[0];
        if (!file) return;

        // Validate file type
        const stepType = this.selectedStep.step_type;
        if (!this.validateFileType(file, stepType)) {
            this.showErrorMessage(`Invalid file type for ${stepType} step`);
            return;
        }

        // Show upload progress
        this.showUploadProgress();

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`/admin/tutorials/steps/${this.selectedStep.id}/media`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.selectedStep.media_url = data.step.media_url;
                this.showMediaPreview(data.step.media_url, stepType);
                this.renderSteps(); // Refresh steps to show updated preview
                this.showSuccessMessage('Media uploaded successfully');
            } else {
                this.showErrorMessage(data.error || 'Failed to upload media');
            }
        } catch (error) {
            console.error('Error uploading media:', error);
            this.showErrorMessage('Error uploading media');
        } finally {
            this.hideUploadProgress();
        }
    }

    validateFileType(file, stepType) {
        const validTypes = {
            'image': ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'],
            'video': ['video/mp4', 'video/webm', 'video/ogg', 'video/mov']
        };

        return validTypes[stepType] && validTypes[stepType].includes(file.type);
    }

    showMediaPreview(mediaUrl, stepType) {
        const previewContainer = document.getElementById('media-preview');
        if (!previewContainer) return;

        let previewHTML = '';
        
        if (stepType === 'image') {
            previewHTML = `
                <div class="media-preview-item">
                    <img src="${mediaUrl}" class="img-fluid rounded" alt="Tutorial image">
                    <button class="btn btn-sm btn-danger remove-media" onclick="tutorialEditor.removeMedia()">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            `;
        } else if (stepType === 'video') {
            previewHTML = `
                <div class="media-preview-item">
                    <video src="${mediaUrl}" class="w-100 rounded" controls></video>
                    <button class="btn btn-sm btn-danger remove-media" onclick="tutorialEditor.removeMedia()">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            `;
        }

        previewContainer.innerHTML = previewHTML;
        previewContainer.style.display = 'block';
    }

    clearMediaPreview() {
        const previewContainer = document.getElementById('media-preview');
        if (previewContainer) {
            previewContainer.innerHTML = '';
            previewContainer.style.display = 'none';
        }
    }

    async removeMedia() {
        if (!this.selectedStep) return;

        if (confirm('Remove media from this tutorial step?')) {
            this.selectedStep.media_url = null;
            await this.updateStep(this.selectedStep.id, { media_url: null });
            this.clearMediaPreview();
            this.renderSteps();
            this.showSuccessMessage('Media removed');
        }
    }

    showUploadProgress() {
        const progressContainer = document.getElementById('upload-progress');
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }
    }

    hideUploadProgress() {
        const progressContainer = document.getElementById('upload-progress');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }

    async updateStep(stepId, updateData) {
        try {
            const response = await fetch(`/admin/tutorials/steps/${stepId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateData)
            });

            const data = await response.json();
            
            if (data.success) {
                // Update local step data
                const step = this.currentSteps.find(s => s.id === stepId);
                if (step) {
                    Object.assign(step, updateData);
                }
                return true;
            } else {
                this.showErrorMessage('Failed to update step');
                return false;
            }
        } catch (error) {
            console.error('Error updating step:', error);
            this.showErrorMessage('Error updating step');
            return false;
        }
    }

    async saveTutorial() {
        if (!this.selectedStep) {
            this.showSuccessMessage('No changes to save');
            return;
        }

        const content = document.getElementById('tutorial-step-content').value;
        const caption = document.getElementById('tutorial-step-caption').value;
        const stepType = document.getElementById('tutorial-step-type').value;

        const updateData = {
            content: content,
            caption: caption,
            step_type: stepType
        };

        if (await this.updateStep(this.selectedStep.id, updateData)) {
            this.renderSteps();
            this.showSuccessMessage('Tutorial step saved');
        }
    }

    async reorderSteps() {
        if (!this.currentTutorial) return;

        const stepOrder = this.currentSteps
            .sort((a, b) => a.order_index - b.order_index)
            .map(step => step.id);

        try {
            const response = await fetch(`/admin/tutorials/${this.currentTutorial.simulation_id}/reorder`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ order: stepOrder })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentSteps = data.steps;
                this.renderSteps();
                this.showSuccessMessage('Tutorial steps reordered');
            } else {
                this.showErrorMessage('Failed to reorder steps');
            }
        } catch (error) {
            console.error('Error reordering steps:', error);
            this.showErrorMessage('Error reordering steps');
        }
    }

    toggleReorderMode() {
        const stepsList = document.getElementById('tutorial-steps-list');
        if (!stepsList) return;

        stepsList.classList.toggle('reorder-mode');
        
        if (stepsList.classList.contains('reorder-mode')) {
            this.enableDragAndDrop();
            this.showSuccessMessage('Drag and drop to reorder steps');
        } else {
            this.disableDragAndDrop();
        }
    }

    enableDragAndDrop() {
        const stepItems = document.querySelectorAll('.tutorial-step-item');
        
        stepItems.forEach(item => {
            item.addEventListener('dragstart', this.handleDragStart.bind(this));
            item.addEventListener('dragover', this.handleDragOver.bind(this));
            item.addEventListener('drop', this.handleDrop.bind(this));
            item.addEventListener('dragend', this.handleDragEnd.bind(this));
        });
    }

    disableDragAndDrop() {
        const stepItems = document.querySelectorAll('.tutorial-step-item');
        
        stepItems.forEach(item => {
            item.removeEventListener('dragstart', this.handleDragStart);
            item.removeEventListener('dragover', this.handleDragOver);
            item.removeEventListener('drop', this.handleDrop);
            item.removeEventListener('dragend', this.handleDragEnd);
        });
    }

    handleDragStart(e) {
        this.isDragging = true;
        this.draggedStep = e.target.closest('.tutorial-step-item');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.draggedStep.outerHTML);
        this.draggedStep.classList.add('dragging');
    }

    handleDragOver(e) {
        if (this.isDragging) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }
    }

    handleDrop(e) {
        if (this.isDragging) {
            e.preventDefault();
            
            const dropTarget = e.target.closest('.tutorial-step-item');
            if (dropTarget && dropTarget !== this.draggedStep) {
                const stepsList = document.getElementById('tutorial-steps-list');
                const draggedIndex = Array.from(stepsList.children).indexOf(this.draggedStep);
                const targetIndex = Array.from(stepsList.children).indexOf(dropTarget);
                
                if (draggedIndex < targetIndex) {
                    dropTarget.parentNode.insertBefore(this.draggedStep, dropTarget.nextSibling);
                } else {
                    dropTarget.parentNode.insertBefore(this.draggedStep, dropTarget);
                }
                
                this.updateStepOrder();
            }
        }
    }

    handleDragEnd(e) {
        this.isDragging = false;
        if (this.draggedStep) {
            this.draggedStep.classList.remove('dragging');
            this.draggedStep = null;
        }
    }

    updateStepOrder() {
        const stepItems = document.querySelectorAll('.tutorial-step-item');
        const newOrder = [];
        
        stepItems.forEach((item, index) => {
            const stepId = parseInt(item.dataset.stepId);
            const step = this.currentSteps.find(s => s.id === stepId);
            if (step) {
                step.order_index = index + 1;
                newOrder.push(stepId);
            }
        });
        
        // Save the new order
        this.reorderSteps();
    }

    previewTutorial() {
        if (!this.currentTutorial || this.currentSteps.length === 0) {
            this.showErrorMessage('No tutorial steps to preview');
            return;
        }

        // Create preview modal
        this.showTutorialPreview();
    }

    showTutorialPreview() {
        const modal = document.createElement('div');
        modal.className = 'modal fade tutorial-preview-modal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Tutorial Preview</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="tutorial-preview-content">
                            ${this.renderTutorialPreview()}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Remove modal from DOM when closed
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    renderTutorialPreview() {
        const sortedSteps = this.currentSteps.sort((a, b) => a.order_index - b.order_index);
        
        return sortedSteps.map((step, index) => {
            return `
                <div class="tutorial-step-preview mb-4">
                    <div class="step-header">
                        <h6><span class="badge bg-primary me-2">${index + 1}</span>${step.step_type.toUpperCase()}</h6>
                    </div>
                    <div class="step-content">
                        ${this.renderStepPreviewContent(step)}
                    </div>
                </div>
            `;
        }).join('');
    }

    renderStepPreviewContent(step) {
        switch (step.step_type) {
            case 'text':
                return `<p>${step.content || ''}</p>`;
            case 'image':
                return step.media_url ? 
                    `<img src="${step.media_url}" class="img-fluid mb-2" alt="Tutorial image">
                     ${step.caption ? `<p class="text-muted small">${step.caption}</p>` : ''}` :
                    `<p class="text-muted">No image uploaded</p>`;
            case 'video':
                return step.media_url ? 
                    `<video src="${step.media_url}" class="w-100 mb-2" controls></video>
                     ${step.caption ? `<p class="text-muted small">${step.caption}</p>` : ''}` :
                    `<p class="text-muted">No video uploaded</p>`;
            case 'code':
                return `<pre><code>${step.content || ''}</code></pre>`;
            case 'tip':
                return `<div class="alert alert-info"><i class="fas fa-lightbulb me-2"></i>${step.content || ''}</div>`;
            default:
                return `<p>${step.content || ''}</p>`;
        }
    }

    // Auto-save functionality
    debounceAutoSave() {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.autoSave();
        }, 2000); // Auto-save after 2 seconds of inactivity
    }

    async autoSave() {
        if (this.selectedStep) {
            const content = document.getElementById('tutorial-step-content').value;
            const caption = document.getElementById('tutorial-step-caption').value;
            
            if (content !== this.selectedStep.content || caption !== this.selectedStep.caption) {
                await this.updateStep(this.selectedStep.id, {
                    content: content,
                    caption: caption
                });
                this.showSuccessMessage('Auto-saved', 1000);
            }
        }
    }

    showSuccessMessage(message, duration = 3000) {
        this.showMessage(message, 'success', duration);
    }

    showErrorMessage(message, duration = 5000) {
        this.showMessage(message, 'error', duration);
    }

    showMessage(message, type = 'info', duration = 3000) {
        // Use the global toast function if available, otherwise console log
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else if (window.editor && typeof window.editor.showToast === 'function') {
            window.editor.showToast(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }

        // Also show in tutorial editor status if element exists
        const statusElement = document.getElementById('tutorial-editor-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `tutorial-status ${type}`;
            setTimeout(() => {
                statusElement.textContent = '';
                statusElement.className = 'tutorial-status';
            }, duration);
        }
    }
}

// Initialize the tutorial editor when the page loads
let tutorialEditor;
document.addEventListener('DOMContentLoaded', () => {
    tutorialEditor = new TutorialEditorManager();
    
    // Auto-load tutorial if simulation ID is available
    if (window.editor && window.editor.simulationData && window.editor.simulationData.id) {
        tutorialEditor.loadTutorial(window.editor.simulationData.id);
    }
});

// Export for global access
window.tutorialEditor = tutorialEditor;

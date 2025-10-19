/**
 * Advanced Lesson Editor
 * Provides rich multimedia lesson editing with drag-and-drop content blocks
 */

class LessonEditor {
    constructor(options) {
        this.lessonId = options.lessonId;
        this.apiUrl = options.apiUrl;
        this.uploadUrl = options.uploadUrl;
        this.previewUrl = options.previewUrl;
        
        this.contentBlocks = [];
        this.mediaFiles = [];
        this.isDirty = false;
        this.autoSaveTimeout = null;
        
        // DOM elements
        this.canvas = null;
        this.previewFrame = null;
        this.autoSaveIndicator = null;
        
        // Rich text editors
        this.activeEditors = new Map();
        
        // Drag and drop
        this.sortable = null;
    }
    
    initialize() {
        this.setupDOMElements();
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupMediaUpload();
        this.initializeTinyMCE();
        // Try to bootstrap media library from server-rendered JSON if available
        try {
            if (window.__INITIAL_MEDIA_FILES__ && Array.isArray(window.__INITIAL_MEDIA_FILES__)) {
                this.mediaFiles = window.__INITIAL_MEDIA_FILES__;
                this.updateMediaLibrary();
            }
        } catch (_) {}
        
        console.log('Lesson Editor initialized for lesson:', this.lessonId);
    }
    
    setupDOMElements() {
        this.canvas = document.getElementById('content-canvas');
        this.previewFrame = document.getElementById('preview-frame');
        this.autoSaveIndicator = document.getElementById('auto-save-indicator');
        
        if (!this.canvas) {
            console.error('Content canvas not found');
            return;
        }
    }
    
    setupEventListeners() {
        // Auto-save on content changes
        document.addEventListener('input', this.handleContentChange.bind(this));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Window unload warning
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        
        // Media library clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.media-item')) {
                this.handleMediaItemClick(e.target.closest('.media-item'));
            }
        });
    }
    
    setupDragAndDrop() {
        // Setup sortable for content blocks
        this.sortable = new Sortable(this.canvas, {
            handle: '.block-header',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onEnd: this.handleBlockReorder.bind(this)
        });
        
        // Setup drag from palette
        const palette = document.querySelector('.blocks-palette');
        if (palette) {
            palette.addEventListener('dragstart', this.handlePaletteDragStart.bind(this));
        }
        
        // Setup canvas drop zone
        this.canvas.addEventListener('dragover', this.handleCanvasDragOver.bind(this));
        this.canvas.addEventListener('drop', this.handleCanvasDrop.bind(this));
    }
    
    setupMediaUpload() {
        const uploadInput = document.getElementById('media-upload');
        const uploadArea = document.querySelector('.media-upload');
        
        if (uploadInput && uploadArea) {
            uploadInput.addEventListener('change', this.handleFileUpload.bind(this));
            
            // Drag and drop for media upload
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = Array.from(e.dataTransfer.files);
                this.uploadFiles(files);
            });
        }
    }
    
    initializeTinyMCE() {
        // Initialize TinyMCE for rich text editing
        tinymce.init({
            selector: '.rich-text-editor',
            plugins: 'advlist autolink lists link image charmap print preview hr anchor pagebreak',
            toolbar_items_size: 'small',
            toolbar: 'formatselect | bold italic underline | alignleft aligncenter alignright | bullist numlist | link image | removeformat',
            menubar: false,
            statusbar: false,
            height: 200,
            theme: 'silver',
            skin: 'oxide-dark',
            content_css: 'dark',
            setup: (editor) => {
                editor.on('change input', () => {
                    this.handleContentChange();
                });
            }
        });
    }
    
    // Content Block Management
    async loadContentBlocks() {
        try {
            this.showAutoSaveStatus('loading', 'Loading content...');
            
            const response = await fetch(`${this.apiUrl}/${this.lessonId}/content-blocks`);
            const data = await response.json();
            
            if (data.success) {
                this.contentBlocks = data.blocks;
                this.renderContentBlocks();
                this.showAutoSaveStatus('saved', 'Content loaded');
            } else {
                throw new Error(data.error || 'Failed to load content blocks');
            }
        } catch (error) {
            console.error('Error loading content blocks:', error);
            this.showAutoSaveStatus('error', 'Failed to load content');
        }
    }
    
    renderContentBlocks() {
        const emptyCanvas = document.getElementById('empty-canvas');
        if (emptyCanvas) {
            emptyCanvas.style.display = this.contentBlocks.length > 0 ? 'none' : 'block';
        }
        
        // Clear existing blocks
        const existingBlocks = this.canvas.querySelectorAll('.content-block');
        existingBlocks.forEach(block => block.remove());
        
        // Render each block
        this.contentBlocks.forEach(block => {
            const blockElement = this.createBlockElement(block);
            this.canvas.appendChild(blockElement);
        });
        
        this.updatePreview();
    }
    
    createBlockElement(block) {
        const template = document.getElementById(`${block.type}-block-template`);
        if (!template) {
            console.error(`Template not found for block type: ${block.type}`);
            return this.createFallbackBlock(block);
        }
        
        const blockElement = document.createElement('div');
        blockElement.innerHTML = template.innerHTML;
        const blockDiv = blockElement.firstElementChild;
        
        // Set block ID and data
        blockDiv.dataset.blockId = block.id || `block_${Date.now()}`;
        blockDiv.dataset.blockOrder = block.order || 0;
        
        // Populate block content based on type
        this.populateBlockContent(blockDiv, block);
        
        return blockDiv;
    }
    
    populateBlockContent(blockElement, block) {
        const blockType = block.type;
        const content = block.content || {};
        
        switch (blockType) {
            case 'text':
                const textEditor = blockElement.querySelector('.rich-text-editor');
                if (textEditor && content.html) {
                    textEditor.innerHTML = content.html;
                }
                break;
                
            case 'image':
                if (content.src) {
                    const placeholder = blockElement.querySelector('.image-placeholder');
                    if (placeholder) {
                        placeholder.innerHTML = `<img src="${content.src}" alt="${content.alt || ''}" style="max-width: 100%; height: auto;">`;
                    }
                }
                break;
                
            case 'video':
                if (content.src) {
                    const placeholder = blockElement.querySelector('.video-placeholder');
                    if (placeholder) {
                        placeholder.innerHTML = `<video controls style="width: 100%; height: auto;"><source src="${content.src}" type="${content.type || 'video/mp4'}"></video>`;
                    }
                }
                break;
                
            case 'file':
                if (content.filename) {
                    blockElement.querySelector('.block-content').innerHTML = `
                        <div class="block-file">
                            <div class="file-icon">
                                <i class="fas fa-file"></i>
                            </div>
                            <div class="file-info">
                                <div class="file-name">${content.filename}</div>
                                <div class="file-size">${this.formatFileSize(content.size || 0)}</div>
                            </div>
                        </div>
                    `;
                }
                break;
        }
    }
    
    createFallbackBlock(block) {
        const blockDiv = document.createElement('div');
        blockDiv.className = 'content-block';
        blockDiv.dataset.blockType = block.type;
        blockDiv.dataset.blockId = block.id || `block_${Date.now()}`;
        
        blockDiv.innerHTML = `
            <div class="block-header">
                <span class="block-type">${block.type} Block</span>
                <div class="block-actions">
                    <button class="block-btn" onclick="editBlock(this)" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="block-btn" onclick="deleteBlock(this)" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="block-content">
                <p>Unsupported block type: ${block.type}</p>
            </div>
        `;
        
        return blockDiv;
    }
    
    // Drag and Drop Handlers
    handlePaletteDragStart(e) {
        if (e.target.classList.contains('block-item')) {
            e.dataTransfer.setData('text/plain', e.target.dataset.blockType);
            e.dataTransfer.effectAllowed = 'copy';
        }
    }
    
    handleCanvasDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    }
    
    handleCanvasDrop(e) {
        e.preventDefault();
        
        const blockType = e.dataTransfer.getData('text/plain');
        if (blockType) {
            this.addContentBlock(blockType);
        }
    }
    
    handleBlockReorder(e) {
        // Update block order based on new positions
        const blocks = Array.from(this.canvas.querySelectorAll('.content-block'));
        blocks.forEach((block, index) => {
            block.dataset.blockOrder = index;
        });
        
        this.markDirty();
        this.scheduleAutoSave();
    }
    
    // Content Block Actions
    addContentBlock(type, position = -1) {
        const block = {
            id: `block_${Date.now()}`,
            type: type,
            content: this.getDefaultContentForType(type),
            order: position >= 0 ? position : this.contentBlocks.length
        };
        
        if (position >= 0) {
            this.contentBlocks.splice(position, 0, block);
        } else {
            this.contentBlocks.push(block);
        }
        
        const blockElement = this.createBlockElement(block);
        
        if (position >= 0) {
            const existingBlocks = this.canvas.querySelectorAll('.content-block');
            if (existingBlocks[position]) {
                this.canvas.insertBefore(blockElement, existingBlocks[position]);
            } else {
                this.canvas.appendChild(blockElement);
            }
        } else {
            this.canvas.appendChild(blockElement);
        }
        
        // Hide empty canvas message
        const emptyCanvas = document.getElementById('empty-canvas');
        if (emptyCanvas) {
            emptyCanvas.style.display = 'none';
        }
        
        this.markDirty();
        this.scheduleAutoSave();
        
        // Initialize rich text editor if it's a text block
        if (type === 'text') {
            setTimeout(() => {
                tinymce.init({
                    selector: `[data-block-id="${block.id}"] .rich-text-editor`,
                    plugins: 'advlist autolink lists link image charmap print preview hr anchor pagebreak',
                    toolbar: 'formatselect | bold italic underline | alignleft aligncenter alignright | bullist numlist | link image | removeformat',
                    menubar: false,
                    statusbar: false,
                    height: 200,
                    theme: 'silver',
                    skin: 'oxide-dark',
                    content_css: 'dark',
                    setup: (editor) => {
                        editor.on('change input', () => {
                            this.handleContentChange();
                        });
                    }
                });
            }, 100);
        }
    }
    
    getDefaultContentForType(type) {
        const defaults = {
            text: { html: '<p>Enter your text content here...</p>' },
            image: { src: '', alt: '', caption: '' },
            video: { src: '', title: '', description: '' },
            audio: { src: '', title: '', description: '' },
            file: { filename: '', url: '', description: '' },
            quiz: { question: '', type: 'multiple_choice', options: [] },
            simulation: { simulation_id: '', instructions: '' },
            separator: { style: 'line' }
        };
        
        return defaults[type] || {};
    }
    
    // File Upload
    handleFileUpload(e) {
        const files = Array.from(e.target.files);
        this.uploadFiles(files);
        e.target.value = ''; // Reset input
    }
    
    async uploadFiles(files) {
        for (const file of files) {
            await this.uploadFile(file);
        }
    }
    
    async uploadFile(file) {
        try {
            this.showAutoSaveStatus('saving', 'Uploading file...');
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(this.uploadUrl, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.mediaFiles.push(data.file);
                this.updateMediaLibrary();
                this.showAutoSaveStatus('saved', 'File uploaded');
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showAutoSaveStatus('error', 'Upload failed');
        }
    }
    
    updateMediaLibrary() {
        const mediaLibrary = document.getElementById('media-library');
        if (!mediaLibrary) return;
        
        mediaLibrary.innerHTML = '';
        
        this.mediaFiles.forEach(media => {
            const mediaItem = document.createElement('div');
            mediaItem.className = 'media-item';
            mediaItem.dataset.mediaId = media.id;
            mediaItem.dataset.mediaType = media.type;
            
            if (media.type === 'images') {
                mediaItem.innerHTML = `
                    <img src="${media.thumbnail_url || media.url}" alt="${media.filename}">
                    <div class="media-item-type">${media.type.substr(0, 3)}</div>
                `;
            } else {
                const iconClass = media.type === 'videos' ? 'video' : 
                                 media.type === 'audio' ? 'music' : 'file';
                mediaItem.innerHTML = `
                    <div class="media-placeholder">
                        <i class="fas fa-${iconClass}"></i>
                    </div>
                    <div class="media-item-type">${media.type.substr(0, 3)}</div>
                `;
            }
            
            mediaLibrary.appendChild(mediaItem);
        });
    }
    
    handleMediaItemClick(mediaItem) {
        const mediaId = mediaItem.dataset.mediaId;
        const mediaType = mediaItem.dataset.mediaType;
        const media = this.mediaFiles.find(m => m.id == mediaId);
        
        if (!media) return;
        
        // Find the currently active block or create a new one
        const activeBlock = document.querySelector('.content-block.active');
        if (activeBlock) {
            this.insertMediaIntoBlock(activeBlock, media);
        } else {
            // Create a new block based on media type
            const blockType = mediaType === 'images' ? 'image' : 
                             mediaType === 'videos' ? 'video' :
                             mediaType === 'audio' ? 'audio' : 'file';
            
            this.addContentBlock(blockType);
            
            // Wait a bit for the block to be created, then insert media
            setTimeout(() => {
                const newBlock = this.canvas.lastElementChild;
                if (newBlock) {
                    this.insertMediaIntoBlock(newBlock, media);
                }
            }, 100);
        }
    }
    
    insertMediaIntoBlock(blockElement, media) {
        const blockType = blockElement.dataset.blockType;
        const blockContent = blockElement.querySelector('.block-content');
        
        switch (blockType) {
            case 'image':
                const imagePlaceholder = blockContent.querySelector('.image-placeholder');
                if (imagePlaceholder) {
                    imagePlaceholder.innerHTML = `
                        <img src="${media.url}" alt="${media.filename}" style="max-width: 100%; height: auto;">
                        <div style="margin-top: 8px; font-size: 12px; color: var(--editor-text-secondary);">${media.filename}</div>
                    `;
                }
                break;
                
            case 'video':
                const videoPlaceholder = blockContent.querySelector('.video-placeholder');
                if (videoPlaceholder) {
                    videoPlaceholder.innerHTML = `
                        <video controls style="width: 100%; height: auto;">
                            <source src="${media.url}" type="${media.mime_type}">
                        </video>
                        <div style="margin-top: 8px; font-size: 12px; color: var(--editor-text-secondary);">${media.filename}</div>
                    `;
                }
                break;
                
            case 'file':
                blockContent.innerHTML = `
                    <div class="block-file">
                        <div class="file-icon">
                            <i class="fas fa-file"></i>
                        </div>
                        <div class="file-info">
                            <div class="file-name">${media.filename}</div>
                            <div class="file-size">${this.formatFileSize(media.size)}</div>
                        </div>
                        <a href="${media.url}" class="btn btn-primary btn-sm" download>
                            <i class="fas fa-download"></i> Download
                        </a>
                    </div>
                `;
                break;
        }
        
        this.markDirty();
        this.scheduleAutoSave();
    }
    
    // Auto-save functionality
    handleContentChange() {
        this.markDirty();
    this.scheduleAutoSave();
    this.updatePreviewDebounced();
    }
    
    markDirty() {
        this.isDirty = true;
    }
    
    scheduleAutoSave() {
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }
        
        this.showAutoSaveStatus('saving', 'Saving...');
        
        this.autoSaveTimeout = setTimeout(() => {
            this.saveLesson();
        }, 2000); // Auto-save after 2 seconds of inactivity
    }
    
    async saveLesson() {
        if (!this.isDirty) return;
        
        try {
            this.showAutoSaveStatus('saving', 'Saving...');
            
            // Collect current content blocks data
            const blocks = this.collectContentBlocksData();
            
            const response = await fetch(`${this.apiUrl}/${this.lessonId}/content-blocks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ blocks: blocks })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isDirty = false;
                this.showAutoSaveStatus('saved', 'All changes saved');
                this.updatePreview();
            } else {
                throw new Error(data.error || 'Save failed');
            }
        } catch (error) {
            console.error('Save error:', error);
            this.showAutoSaveStatus('error', 'Save failed');
        }
    }
    
    collectContentBlocksData() {
        const blocks = [];
        const blockElements = this.canvas.querySelectorAll('.content-block');
        
        blockElements.forEach((blockElement, index) => {
            const blockType = blockElement.dataset.blockType;
            const blockId = blockElement.dataset.blockId;
            
            const block = {
                id: blockId,
                type: blockType,
                order: index,
                content: this.extractBlockContent(blockElement, blockType)
            };
            
            blocks.push(block);
        });
        
        return blocks;
    }
    
    extractBlockContent(blockElement, blockType) {
        const blockContent = blockElement.querySelector('.block-content');
        
        switch (blockType) {
            case 'text':
                const editor = blockContent.querySelector('.rich-text-editor');
                return { html: editor ? editor.innerHTML : '' };
                
            case 'image':
                const img = blockContent.querySelector('img');
                return img ? {
                    src: img.src,
                    alt: img.alt,
                    caption: img.title || ''
                } : {};
                
            case 'video':
                const video = blockContent.querySelector('video source');
                return video ? {
                    src: video.src,
                    type: video.type,
                    title: '',
                    description: ''
                } : {};
                
            case 'file':
                const fileLink = blockContent.querySelector('a[download]');
                const fileName = blockContent.querySelector('.file-name');
                return fileLink && fileName ? {
                    url: fileLink.href,
                    filename: fileName.textContent,
                    description: ''
                } : {};
                
            default:
                return {};
        }
    }
    
    // Preview functionality
    updatePreview() {
        if (!this.previewFrame) return;
        const blocks = this.collectContentBlocksData();
        try {
            // Send blocks to preview iframe for instant update
            this.previewFrame.contentWindow.postMessage({
                type: 'lesson_preview_update',
                lessonId: this.lessonId,
                blocks
            }, '*');
        } catch (e) {
            // Fallback: reload preview
            this.previewFrame.src = `${this.previewUrl}?t=${Date.now()}`;
        }
    }

    updatePreviewDebounced() {
        if (this._previewTimer) clearTimeout(this._previewTimer);
        this._previewTimer = setTimeout(() => this.updatePreview(), 300);
    }
    
    // Template functionality
    async applyTemplate(templateId) {
        try {
            const response = await fetch(`${this.apiUrl}/templates/${templateId}/apply`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ lesson_id: this.lessonId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                await this.loadContentBlocks();
                this.showAutoSaveStatus('saved', 'Template applied');
            } else {
                throw new Error(data.error || 'Failed to apply template');
            }
        } catch (error) {
            console.error('Template apply error:', error);
            this.showAutoSaveStatus('error', 'Failed to apply template');
        }
    }
    
    // UI Helper functions
    showAutoSaveStatus(status, message) {
        if (!this.autoSaveIndicator) return;
        
        const icon = this.autoSaveIndicator.querySelector('i');
        const text = this.autoSaveIndicator.querySelector('span');
        
        // Reset classes
        this.autoSaveIndicator.classList.remove('saving', 'saved', 'error', 'loading');
        this.autoSaveIndicator.classList.add(status);
        
        // Update icon
        if (icon) {
            icon.className = status === 'saving' || status === 'loading' ? 'fas fa-spinner fa-spin' :
                            status === 'saved' ? 'fas fa-check-circle' :
                            status === 'error' ? 'fas fa-exclamation-triangle' :
                            'fas fa-circle';
        }
        
        // Update text
        if (text) {
            text.textContent = message;
        }
        
        // Auto-hide success messages
        if (status === 'saved') {
            setTimeout(() => {
                if (text) text.textContent = 'All changes saved';
            }, 3000);
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Keyboard shortcuts
    handleKeyboardShortcuts(e) {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 's':
                    e.preventDefault();
                    this.saveLesson();
                    break;
                case 'z':
                    if (!e.shiftKey) {
                        e.preventDefault();
                        // Implement undo
                    }
                    break;
            }
        }
    }
    
    handleBeforeUnload(e) {
        if (this.isDirty) {
            e.preventDefault();
            e.returnValue = '';
            return 'You have unsaved changes. Are you sure you want to leave?';
        }
    }
}

// Global functions for template event handlers
window.editBlock = function(button) {
    const block = button.closest('.content-block');
    
    // Remove active class from all blocks
    document.querySelectorAll('.content-block').forEach(b => b.classList.remove('active'));
    
    // Add active class to current block
    block.classList.add('active');
    
    // Focus on the content area
    const contentArea = block.querySelector('.rich-text-editor, .image-placeholder, .video-placeholder');
    if (contentArea) {
        contentArea.focus();
    }
};

window.deleteBlock = function(button) {
    if (confirm('Are you sure you want to delete this content block?')) {
        const block = button.closest('.content-block');
        block.remove();
        
        // Check if canvas is empty
        const remainingBlocks = document.querySelectorAll('.content-block');
        const emptyCanvas = document.getElementById('empty-canvas');
        if (remainingBlocks.length === 0 && emptyCanvas) {
            emptyCanvas.style.display = 'block';
        }
        
        // Trigger save
        if (window.lessonEditor) {
            window.lessonEditor.markDirty();
            window.lessonEditor.scheduleAutoSave();
        }
    }
};

window.saveLesson = function() {
    if (window.lessonEditor) {
        window.lessonEditor.saveLesson();
    }
};

window.previewLesson = function() {
    if (window.lessonEditor) {
        window.open(window.lessonEditor.previewUrl, '_blank');
    }
};

window.togglePreview = function() {
    const preview = document.getElementById('content-preview');
    if (preview) {
        preview.style.display = preview.style.display === 'none' ? 'block' : 'none';
    }
};

window.applyTemplate = function(templateId) {
    if (window.lessonEditor) {
        if (confirm('Applying a template will replace all current content. Continue?')) {
            window.lessonEditor.applyTemplate(templateId);
        }
    }
};

// Make lesson editor globally accessible
window.LessonEditor = LessonEditor;

// Device simulation helper
window.setPreviewDevice = function(device) {
    const frame = document.getElementById('preview-frame');
    if (!frame) return;
    let width = '800px';
    switch (device) {
        case 'tablet':
            width = '768px';
            break;
        case 'mobile':
            width = '414px';
            break;
        case 'desktop':
        default:
            width = '800px';
    }
    try {
        frame.contentWindow.postMessage({ type: 'lesson_preview_device', width }, '*');
    } catch (e) {
        // no-op
    }
};

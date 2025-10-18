/**
 * Multi-Tool Chat App - Frontend JavaScript
 * Enhanced with modern features, error handling, and user experience improvements
 */

class MultiToolApp {
    constructor() {
        this.form = document.getElementById('upload-form');
        this.textInput = document.getElementById('text-input');
        this.fileInput = document.getElementById('file-input');
        this.fileNameSpan = document.getElementById('file-name');
        this.responseOutput = document.getElementById('response-output');
        this.processBtn = document.getElementById('process-btn');
        this.btnText = document.querySelector('.btn-text');
        this.btnLoading = document.querySelector('.btn-loading');
        this.copyBtn = document.getElementById('copy-btn');
        this.metadataSection = document.getElementById('metadata-section');
        this.metadataContent = document.getElementById('metadata-content');
        this.statusDot = document.getElementById('status-dot');
        this.statusText = document.getElementById('status-text');
        this.analyzeOption = document.getElementById('analyze-option');
        this.notification = document.getElementById('notification');
        
        this.isProcessing = false;
        this.currentResponse = '';
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.updateStatus('ready', 'Ready');
        this.checkServerHealth();
    }
    
    bindEvents() {
        // File input change handler
        this.fileInput.addEventListener('change', () => this.handleFileChange());
        
        // Form submission handler
        this.form.addEventListener('submit', (event) => this.handleSubmit(event));
        
        // Copy button handler
        this.copyBtn.addEventListener('click', () => this.copyToClipboard());
        
        // Drag and drop handlers
        this.setupDragAndDrop();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => this.handleKeyboard(event));
    }
    
    handleFileChange() {
        const file = this.fileInput.files[0];
        if (file) {
            this.fileNameSpan.textContent = file.name;
            this.fileNameSpan.style.fontStyle = 'normal';
            this.fileNameSpan.style.color = 'var(--text-primary)';
            
            // Validate file
            this.validateFile(file);
        } else {
            this.fileNameSpan.textContent = 'No file chosen';
            this.fileNameSpan.style.fontStyle = 'italic';
            this.fileNameSpan.style.color = 'var(--text-secondary)';
        }
    }
    
    validateFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
        
        if (file.size > maxSize) {
            this.showNotification('File too large. Maximum size is 10MB.', 'error');
            this.fileInput.value = '';
            this.handleFileChange();
            return false;
        }
        
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('Unsupported file type. Please use PDF, PNG, JPG, JPEG, GIF, or WebP.', 'error');
            this.fileInput.value = '';
            this.handleFileChange();
            return false;
        }
        
        return true;
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        if (this.isProcessing) return;
        
        const text = this.textInput.value.trim();
        const file = this.fileInput.files[0];
        
        if (!text && !file) {
            this.showNotification('Please provide text input or upload a file.', 'warning');
            return;
        }
        
        if (file && !this.validateFile(file)) {
            return;
        }
        
        await this.processInput(text, file);
    }
    
    async processInput(text, file) {
        this.setProcessingState(true);
        this.clearResponse();
        
        const formData = new FormData();
        
        if (text) {
            formData.append('text', text);
        }
        
        if (file) {
            formData.append('file', file);
            formData.append('analyze', this.analyzeOption.checked);
        }
        
        try {
            this.updateStatus('processing', 'Processing...');
            
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData,
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || result.detail || `HTTP error! Status: ${response.status}`);
            }
            
            this.displayResponse(result);
            this.showNotification('Processing completed successfully!', 'success');
            this.updateStatus('ready', 'Ready');
            
        } catch (error) {
            console.error('Processing error:', error);
            this.displayError(error.message);
            this.showNotification(`Error: ${error.message}`, 'error');
            this.updateStatus('error', 'Error');
        } finally {
            this.setProcessingState(false);
        }
    }
    
    displayResponse(result) {
        this.currentResponse = result.response || 'No response received';
        
        // Clear placeholder
        this.responseOutput.innerHTML = '';
        this.responseOutput.style.fontFamily = "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace";
        
        // Display main response
        const responseText = document.createElement('div');
        responseText.textContent = this.currentResponse;
        responseText.style.whiteSpace = 'pre-wrap';
        responseText.style.wordWrap = 'break-word';
        this.responseOutput.appendChild(responseText);
        
        // Show copy button
        this.copyBtn.style.display = 'block';
        
        // Display metadata if available
        if (result.metadata && Object.keys(result.metadata).length > 0) {
            this.displayMetadata(result.metadata);
        }
        
        // Scroll to response
        this.responseOutput.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    displayMetadata(metadata) {
        this.metadataContent.innerHTML = '';
        
        const metadataItems = [
            { label: 'Status', value: metadata.status || 'Success' },
            { label: 'File Size', value: metadata.file_size ? this.formatFileSize(metadata.file_size) : null },
            { label: 'Page Count', value: metadata.page_count },
            { label: 'Text Length', value: metadata.text_length },
            { label: 'Content Type', value: metadata.content_type },
            { label: 'Filename', value: metadata.filename }
        ];
        
        metadataItems.forEach(item => {
            if (item.value !== null && item.value !== undefined) {
                const metadataItem = document.createElement('div');
                metadataItem.className = 'metadata-item';
                metadataItem.innerHTML = `
                    <span class="metadata-label">${item.label}:</span>
                    <span class="metadata-value">${item.value}</span>
                `;
                this.metadataContent.appendChild(metadataItem);
            }
        });
        
        if (this.metadataContent.children.length > 0) {
            this.metadataSection.style.display = 'block';
        }
    }
    
    displayError(errorMessage) {
        this.responseOutput.innerHTML = '';
        this.responseOutput.style.fontFamily = 'inherit';
        
        const errorDiv = document.createElement('div');
        errorDiv.style.color = 'var(--error-color)';
        errorDiv.style.textAlign = 'center';
        errorDiv.style.padding = '2rem';
        errorDiv.innerHTML = `
            <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
            <h3 style="margin-bottom: 1rem;">Processing Failed</h3>
            <p style="margin-bottom: 1rem;">${errorMessage}</p>
            <small style="color: var(--text-muted);">Please try again or contact support if the issue persists.</small>
        `;
        
        this.responseOutput.appendChild(errorDiv);
        this.copyBtn.style.display = 'none';
        this.metadataSection.style.display = 'none';
    }
    
    clearResponse() {
        this.responseOutput.innerHTML = `
            <div class="placeholder">
                <div class="placeholder-icon">⏳</div>
                <p>Processing your request...</p>
                <small>This may take a few moments depending on the complexity.</small>
            </div>
        `;
        this.copyBtn.style.display = 'none';
        this.metadataSection.style.display = 'none';
        this.currentResponse = '';
    }
    
    async copyToClipboard() {
        if (!this.currentResponse) return;
        
        try {
            await navigator.clipboard.writeText(this.currentResponse);
            this.showNotification('Response copied to clipboard!', 'success');
            
            // Temporarily change button text
            const originalText = this.copyBtn.textContent;
            this.copyBtn.textContent = '✅ Copied!';
            setTimeout(() => {
                this.copyBtn.textContent = originalText;
            }, 2000);
            
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            this.showNotification('Failed to copy to clipboard', 'error');
        }
    }
    
    setProcessingState(processing) {
        this.isProcessing = processing;
        this.processBtn.disabled = processing;
        
        if (processing) {
            this.btnText.style.display = 'none';
            this.btnLoading.style.display = 'inline';
        } else {
            this.btnText.style.display = 'inline';
            this.btnLoading.style.display = 'none';
        }
    }
    
    updateStatus(type, message) {
        this.statusText.textContent = message;
        
        // Remove existing status classes
        this.statusDot.className = 'status-dot';
        
        // Add appropriate status class
        switch (type) {
            case 'ready':
                this.statusDot.style.background = 'var(--success-color)';
                break;
            case 'processing':
                this.statusDot.style.background = 'var(--warning-color)';
                this.statusDot.classList.add('loading');
                break;
            case 'error':
                this.statusDot.style.background = 'var(--error-color)';
                break;
        }
    }
    
    showNotification(message, type = 'success') {
        this.notification.textContent = message;
        this.notification.className = `notification ${type}`;
        this.notification.style.display = 'block';
        
        // Trigger animation
        setTimeout(() => {
            this.notification.classList.add('show');
        }, 100);
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            this.hideNotification();
        }, 5000);
    }
    
    hideNotification() {
        this.notification.classList.remove('show');
        setTimeout(() => {
            this.notification.style.display = 'none';
        }, 300);
    }
    
    setupDragAndDrop() {
        const dropZone = this.form;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.style.background = 'rgba(37, 99, 235, 0.05)';
                dropZone.style.borderColor = 'var(--primary-color)';
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.style.background = '';
                dropZone.style.borderColor = '';
            }, false);
        });
        
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.fileInput.files = files;
                this.handleFileChange();
            }
        }, false);
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    handleKeyboard(event) {
        // Ctrl/Cmd + Enter to submit
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            if (!this.isProcessing) {
                this.form.dispatchEvent(new Event('submit'));
            }
        }
        
        // Escape to clear
        if (event.key === 'Escape') {
            if (this.isProcessing) {
                // Could implement cancellation here
            } else {
                this.textInput.value = '';
                this.fileInput.value = '';
                this.handleFileChange();
            }
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async checkServerHealth() {
        try {
            const response = await fetch('/health');
            const health = await response.json();
            
            if (response.ok && health.status === 'healthy') {
                this.updateStatus('ready', 'Ready');
            } else {
                this.updateStatus('error', 'Server Issue');
            }
        } catch (error) {
            console.warn('Health check failed:', error);
            this.updateStatus('error', 'Connection Issue');
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MultiToolApp();
});

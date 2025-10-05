/**
 * Audio Loader Utility
 * Handles safe loading of audio files with proper error handling
 * Prevents connection aborts and provides fallback behavior
 */

class AudioLoader {
    constructor() {
        this.audioElements = new Map();
        this.loadingPromises = new Map();
        this.maxRetries = 2;
        this.retryDelay = 1000; // 1 second
    }

    /**
     * Initialize audio elements with proper error handling
     * Call this on DOMContentLoaded
     */
    initializeAll() {
        console.log('🔊 Initializing audio elements...');
        
        const audioElements = document.querySelectorAll('audio');
        let initialized = 0;
        let failed = 0;
        
        audioElements.forEach(audio => {
            try {
                this.setupAudioElement(audio);
                initialized++;
            } catch (error) {
                console.warn(`⚠️ Failed to setup audio element ${audio.id || 'unnamed'}:`, error);
                failed++;
            }
        });
        
        console.log(`✅ Audio initialization complete: ${initialized} successful, ${failed} failed`);
    }

    /**
     * Setup a single audio element with error handlers and preload optimization
     */
    setupAudioElement(audio) {
        const audioId = audio.id || `audio_${Date.now()}`;
        
        // Store reference
        this.audioElements.set(audioId, audio);
        
        // Set preload strategy based on audio type
        // Background music: preload metadata only
        // Sound effects: preload auto
        if (audioId.includes('bg') || audioId.includes('background')) {
            audio.preload = 'metadata';
        } else {
            audio.preload = 'auto';
        }
        
        // Add error handler to prevent connection aborts from crashing
        audio.addEventListener('error', (e) => {
            console.warn(`⚠️ Audio load error for ${audioId}:`, e);
            this.handleAudioError(audio, audioId);
        });
        
        // Add load success handler
        audio.addEventListener('loadeddata', () => {
            console.debug(`✅ Audio loaded successfully: ${audioId}`);
        });
        
        // Prevent connection abort errors when page unloads
        window.addEventListener('beforeunload', () => {
            try {
                audio.pause();
                audio.src = ''; // Clear source to cancel any pending requests
            } catch (e) {
                // Silently fail - we're unloading anyway
            }
        });
    }

    /**
     * Handle audio loading errors with retry logic
     */
    async handleAudioError(audio, audioId) {
        const retryCount = audio.dataset.retryCount ? parseInt(audio.dataset.retryCount) : 0;
        
        if (retryCount < this.maxRetries) {
            console.log(`🔄 Retrying audio load for ${audioId} (attempt ${retryCount + 1}/${this.maxRetries})`);
            audio.dataset.retryCount = retryCount + 1;
            
            // Wait before retrying
            await new Promise(resolve => setTimeout(resolve, this.retryDelay));
            
            try {
                audio.load();
            } catch (e) {
                console.error(`❌ Failed to retry loading ${audioId}:`, e);
            }
        } else {
            console.error(`❌ Max retries reached for ${audioId}, audio will not be available`);
            // Mark as failed
            audio.dataset.loadFailed = 'true';
        }
    }

    /**
     * Safely play an audio element by ID
     */
    async play(audioId) {
        const audio = this.audioElements.get(audioId);
        
        if (!audio) {
            console.warn(`⚠️ Audio element not found: ${audioId}`);
            return false;
        }
        
        if (audio.dataset.loadFailed === 'true') {
            console.warn(`⚠️ Cannot play ${audioId}: Audio failed to load`);
            return false;
        }
        
        try {
            // Ensure audio is loaded before playing
            if (audio.readyState < 2) {
                console.debug(`⏳ Waiting for ${audioId} to load...`);
                await new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => {
                        reject(new Error('Audio load timeout'));
                    }, 5000);
                    
                    audio.addEventListener('loadeddata', () => {
                        clearTimeout(timeout);
                        resolve();
                    }, { once: true });
                    
                    audio.load();
                });
            }
            
            await audio.play();
            console.debug(`▶️ Playing ${audioId}`);
            return true;
        } catch (error) {
            // Handle autoplay restrictions gracefully
            if (error.name === 'NotAllowedError') {
                console.warn(`⚠️ Autoplay blocked for ${audioId}. User interaction required.`);
            } else {
                console.error(`❌ Error playing ${audioId}:`, error);
            }
            return false;
        }
    }

    /**
     * Safely pause an audio element
     */
    pause(audioId) {
        const audio = this.audioElements.get(audioId);
        
        if (!audio) {
            console.warn(`⚠️ Audio element not found: ${audioId}`);
            return false;
        }
        
        try {
            audio.pause();
            console.debug(`⏸️ Paused ${audioId}`);
            return true;
        } catch (error) {
            console.error(`❌ Error pausing ${audioId}:`, error);
            return false;
        }
    }

    /**
     * Stop an audio element (pause and reset to start)
     */
    stop(audioId) {
        const audio = this.audioElements.get(audioId);
        
        if (!audio) {
            console.warn(`⚠️ Audio element not found: ${audioId}`);
            return false;
        }
        
        try {
            audio.pause();
            audio.currentTime = 0;
            console.debug(`⏹️ Stopped ${audioId}`);
            return true;
        } catch (error) {
            console.error(`❌ Error stopping ${audioId}:`, error);
            return false;
        }
    }

    /**
     * Set volume for an audio element (0.0 to 1.0)
     */
    setVolume(audioId, volume) {
        const audio = this.audioElements.get(audioId);
        
        if (!audio) {
            console.warn(`⚠️ Audio element not found: ${audioId}`);
            return false;
        }
        
        try {
            audio.volume = Math.max(0, Math.min(1, volume));
            console.debug(`🔊 Set volume for ${audioId}: ${audio.volume}`);
            return true;
        } catch (error) {
            console.error(`❌ Error setting volume for ${audioId}:`, error);
            return false;
        }
    }

    /**
     * Clean up all audio elements (call on page unload)
     */
    cleanup() {
        console.log('🧹 Cleaning up audio elements...');
        
        this.audioElements.forEach((audio, audioId) => {
            try {
                audio.pause();
                audio.src = '';
                audio.load(); // This cancels any pending loads
            } catch (e) {
                // Silently fail during cleanup
            }
        });
        
        this.audioElements.clear();
        this.loadingPromises.clear();
    }
}

// Create global instance
window.audioLoader = new AudioLoader();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.audioLoader.initializeAll();
    });
} else {
    // DOM already loaded
    window.audioLoader.initializeAll();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    window.audioLoader.cleanup();
});

console.log('✅ Audio loader initialized');

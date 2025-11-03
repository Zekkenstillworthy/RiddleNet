/**
 * Challenge Progress Manager - MVP
 * Universal save/load/continue functionality for all challenges
 * 
 * Usage:
 *   const progressManager = new ChallengeProgressManager('crimping');
 *   await progressManager.checkForProgress();
 *   progressManager.startAutoSave(getStateCallback);
 */

class ChallengeProgressManager {
    constructor(challengeType) {
        this.challengeType = challengeType;
        this.autoSaveInterval = null;
        this.autoSaveDelay = 10000; // Auto-save every 10 seconds
        this.isSaving = false;
        
        console.log(`🎮 Challenge Progress Manager initialized for: ${challengeType}`);
    }

    /**
     * Check for existing progress on page load
     * @returns {Object|null} Saved state data or null
     */
    async checkForProgress() {
        try {
            const response = await fetch(`/api/challenge/load-progress/${this.challengeType}`);
            const data = await response.json();

            if (!data.success) {
                console.error('❌ Failed to check progress:', data.error);
                return null;
            }

            if (data.has_progress && !data.is_completed) {
                console.log(`📦 Found saved progress for ${this.challengeType}`);
                this.showContinueModal(data.state_data, data.last_updated);
                return data.state_data;
            } else if (data.is_completed) {
                console.log(`✅ Challenge ${this.challengeType} was already completed`);
                // Clear completed progress to start fresh
                await this.clearProgress();
            }
            
            return null;
        } catch (error) {
            console.error('❌ Error checking progress:', error);
            return null;
        }
    }

    /**
     * Show continue game modal
     * @param {Object} stateData - Saved game state
     * @param {string} lastUpdated - ISO timestamp
     */
    showContinueModal(stateData, lastUpdated) {
        const modal = document.getElementById('continueGameModal');
        const dateSpan = document.getElementById('lastPlayedDate');

        if (modal && dateSpan) {
            const date = new Date(lastUpdated);
            const formattedDate = date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
            
            dateSpan.textContent = formattedDate;
            modal.style.display = 'flex';

            // Store state data for later use
            window._savedGameState = stateData;
            
            console.log('🎯 Continue modal displayed');
        } else {
            console.warn('⚠️ Continue modal elements not found in DOM');
        }
    }

    /**
     * Save current game state to database
     * @param {Object} stateData - Game state to save
     * @param {boolean} isCompleted - Whether challenge is completed
     * @returns {boolean} Success status
     */
    async saveProgress(stateData, isCompleted = false) {
        // Prevent concurrent saves
        if (this.isSaving) {
            console.log('⏳ Save already in progress, skipping...');
            return false;
        }

        // Validate state data
        if (!stateData || typeof stateData !== 'object') {
            console.warn('⚠️ Invalid state data, skipping save');
            return false;
        }

        this.isSaving = true;

        try {
            const response = await fetch('/api/challenge/save-progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    challenge_type: this.challengeType,
                    state_data: stateData,
                    is_completed: isCompleted
                })
            });

            const data = await response.json();
            
            if (data.success) {
                const status = isCompleted ? '🎉 Completed' : '💾 Saved';
                console.log(`${status} progress for ${this.challengeType}`);
                return true;
            } else {
                console.error('❌ Save failed:', data.error);
                return false;
            }
        } catch (error) {
            console.error('❌ Error saving progress:', error);
            return false;
        } finally {
            this.isSaving = false;
        }
    }

    /**
     * Clear saved progress from database
     * @returns {boolean} Success status
     */
    async clearProgress() {
        try {
            const response = await fetch(`/api/challenge/clear-progress/${this.challengeType}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                console.log(`🗑️ Progress cleared for ${this.challengeType}`);
                return true;
            }
            return false;
        } catch (error) {
            console.error('❌ Error clearing progress:', error);
            return false;
        }
    }

    /**
     * Start auto-save timer
     * @param {Function} getStateCallback - Function that returns current game state
     */
    startAutoSave(getStateCallback) {
        if (typeof getStateCallback !== 'function') {
            console.error('❌ Auto-save requires a valid callback function');
            return;
        }

        this.stopAutoSave(); // Clear any existing interval

        this.autoSaveInterval = setInterval(async () => {
            try {
                const state = getStateCallback();
                if (state) {
                    await this.saveProgress(state);
                }
            } catch (error) {
                console.error('❌ Auto-save error:', error);
            }
        }, this.autoSaveDelay);

        console.log(`🔄 Auto-save enabled for ${this.challengeType} (every ${this.autoSaveDelay / 1000}s)`);
    }

    /**
     * Stop auto-save timer
     */
    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
            console.log(`⏹️ Auto-save stopped for ${this.challengeType}`);
        }
    }

    /**
     * Setup save on page unload using sendBeacon
     * @param {Function} getStateCallback - Function that returns current game state
     */
    setupBeforeUnloadSave(getStateCallback) {
        if (typeof getStateCallback !== 'function') {
            console.error('❌ Before-unload save requires a valid callback function');
            return;
        }

        window.addEventListener('beforeunload', (e) => {
            try {
                const state = getStateCallback();
                if (state && typeof state === 'object') {
                    // Use sendBeacon for reliable save on page unload
                    const blob = new Blob([JSON.stringify({
                        challenge_type: this.challengeType,
                        state_data: state
                    })], { type: 'application/json' });
                    
                    navigator.sendBeacon('/api/challenge/save-progress', blob);
                    console.log(`📤 Exit save triggered for ${this.challengeType}`);
                }
            } catch (error) {
                console.error('❌ Error in before-unload save:', error);
            }
        });

        console.log(`🚪 Exit save handler registered for ${this.challengeType}`);
    }

    /**
     * Save progress immediately (e.g., on level complete)
     * @param {Object} stateData - Game state to save
     * @returns {boolean} Success status
     */
    async saveImmediately(stateData) {
        console.log(`⚡ Immediate save triggered for ${this.challengeType}`);
        return await this.saveProgress(stateData, false);
    }

    /**
     * Mark challenge as completed and save final state
     * @param {Object} stateData - Final game state
     * @returns {boolean} Success status
     */
    async markCompleted(stateData) {
        console.log(`🏆 Marking ${this.challengeType} as completed`);
        this.stopAutoSave(); // Stop auto-save when completed
        return await this.saveProgress(stateData, true);
    }
}

// ============================================================================
// GLOBAL MODAL FUNCTIONS
// These are called by the continue modal buttons
// ============================================================================

function continueSavedGame() {
    const modal = document.getElementById('continueGameModal');
    if (modal) {
        modal.style.display = 'none';
    }

    console.log('▶️ User chose to continue saved game');

    // Trigger custom event with saved state
    const event = new CustomEvent('loadSavedGame', {
        detail: { state: window._savedGameState }
    });
    document.dispatchEvent(event);
}

function startNewGame() {
    const modal = document.getElementById('continueGameModal');
    if (modal) {
        modal.style.display = 'none';
    }

    console.log('🆕 User chose to start fresh');

    // Clear saved state
    if (window.challengeProgress) {
        window.challengeProgress.clearProgress();
    }

    // Trigger custom event for new game
    const event = new CustomEvent('startNewGame');
    document.dispatchEvent(event);
}

function closeContinueModal() {
    const modal = document.getElementById('continueGameModal');
    if (modal) {
        modal.style.display = 'none';
    }
    
    console.log('❌ Continue modal closed - defaulting to new game');
    
    // Default to starting new game if modal is closed
    startNewGame();
}

// Export for use in other scripts
window.ChallengeProgressManager = ChallengeProgressManager;

console.log('✅ Challenge Progress Manager module loaded');

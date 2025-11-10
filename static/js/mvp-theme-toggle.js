/**
 * ============================================
 * MVP THEME TOGGLE SYSTEM
 * Purpose: Light/Dark mode switching with persistence
 * ============================================
 */

class MVPThemeToggle {
    constructor() {
        this.currentTheme = localStorage.getItem('mvp-theme') || 'dark';
        this.toggleButton = null;
        this.toggleIcon = null;
        this.init();
    }

    init() {
        // Apply saved theme immediately (before creating button to prevent flicker)
        this.applyTheme(this.currentTheme);
        
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Create toggle button
        this.createToggleButton();
        
        // Listen for external theme changes (from other tabs/windows)
        window.addEventListener('storage', (e) => {
            if (e.key === 'mvp-theme' && e.newValue && e.newValue !== this.currentTheme) {
                this.applyTheme(e.newValue);
            }
        });

        // Listen for keyboard shortcut (Ctrl+Shift+T)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Mark as initialized
        document.documentElement.setAttribute('data-theme-initialized', 'true');
    }

    createToggleButton() {
        // Check if button already exists
        if (document.querySelector('.mvp-theme-toggle')) {
            return;
        }

        const toggle = document.createElement('button');
        toggle.className = 'mvp-theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle theme');
        toggle.setAttribute('title', `Switch to ${this.currentTheme === 'dark' ? 'light' : 'dark'} mode`);
        toggle.setAttribute('type', 'button');
        
        // Use Boxicons (already loaded in base.html)
        const icon = document.createElement('i');
        icon.className = this.currentTheme === 'dark' ? 'bx bx-sun' : 'bx bx-moon';
        toggle.appendChild(icon);
        
        // Add click handler
        toggle.addEventListener('click', () => this.toggleTheme());
        
        // Add hover sound effect (if available)
        toggle.addEventListener('mouseenter', () => {
            if (typeof playHoverSound === 'function') {
                playHoverSound();
            }
        });
        
        // Add to document
        document.body.appendChild(toggle);
        
        this.toggleButton = toggle;
        this.toggleIcon = icon;
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        
        // Play click sound if available
        if (typeof playClickSound === 'function') {
            playClickSound();
        }
        
        // Apply new theme
        this.applyTheme(newTheme);
    }

    updateToggleIcon() {
        if (this.toggleIcon) {
            this.toggleIcon.className = this.currentTheme === 'dark' ? 'bx bx-sun' : 'bx bx-moon';
        }
    }

    applyTheme(theme) {
        const normalizedTheme = theme === 'light' ? 'light' : 'dark';
        const previousTheme = this.currentTheme;

        // Apply to html element with highest priority
        document.documentElement.setAttribute('data-theme', normalizedTheme);
        document.body.setAttribute('data-theme', normalizedTheme);
        document.documentElement.classList.toggle('theme-light', normalizedTheme === 'light');
        document.documentElement.classList.toggle('theme-dark', normalizedTheme === 'dark');

        // Force theme application to all elements with inline styles
        if (normalizedTheme === 'light') {
            document.documentElement.style.setProperty('--primary-color', '#F8FAFC', 'important');
            document.documentElement.style.setProperty('--secondary-color', '#F1F5F9', 'important');
            document.documentElement.style.setProperty('--background', '#F8FAFC', 'important');
            document.documentElement.style.setProperty('--surface', '#FFFFFF', 'important');
            document.documentElement.style.setProperty('--text-primary', '#0F172A', 'important');
            document.documentElement.style.setProperty('--text-secondary', '#475569', 'important');
            document.documentElement.style.setProperty('--cyber-glow', '#3B82F6', 'important');
            document.documentElement.style.setProperty('--neon-green', '#059669', 'important');
            document.documentElement.style.setProperty('--network-purple', '#8B5CF6', 'important');
        } else {
            // Reset to dark theme defaults
            document.documentElement.style.setProperty('--primary-color', '#0B1426', 'important');
            document.documentElement.style.setProperty('--secondary-color', '#1A2B47', 'important');
            document.documentElement.style.setProperty('--background', '#0B1426', 'important');
            document.documentElement.style.setProperty('--surface', '#1A2B47', 'important');
            document.documentElement.style.setProperty('--text-primary', '#FFFFFF', 'important');
            document.documentElement.style.setProperty('--text-secondary', '#B3E5FC', 'important');
            document.documentElement.style.setProperty('--cyber-glow', '#00D4FF', 'important');
            document.documentElement.style.setProperty('--neon-green', '#39FF14', 'important');
            document.documentElement.style.setProperty('--network-purple', '#8B5CF6', 'important');
        }

        this.currentTheme = normalizedTheme;

        if (this.toggleButton) {
            this.toggleButton.setAttribute('title', `Switch to ${normalizedTheme === 'dark' ? 'light' : 'dark'} mode`);
        }

        this.updateToggleIcon();
        localStorage.setItem('mvp-theme', normalizedTheme);

        if (previousTheme && previousTheme !== normalizedTheme) {
            window.dispatchEvent(new CustomEvent('mvp-theme-changed', {
                detail: {
                    theme: normalizedTheme,
                    previousTheme
                }
            }));
        }

        // Update meta theme-color for mobile browsers
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = normalizedTheme === 'light' ? '#F8FAFC' : '#0B1426';

        // Force reflow to ensure CSS changes are applied immediately
        document.documentElement.offsetHeight;
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (theme === 'light' || theme === 'dark') {
            this.applyTheme(theme);
        } else {
            console.error('❌ Invalid theme:', theme);
        }
    }
}

// Initialize theme toggle system
if (!window.mvpThemeToggle) {
    window.mvpThemeToggle = new MVPThemeToggle();
}

// Export for module systems (optional)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MVPThemeToggle;
}

/**
 * ============================================
 * USAGE EXAMPLES
 * ============================================
 * 
 * // Listen for theme changes
 * window.addEventListener('mvp-theme-changed', (e) => {
 *     console.log('Theme changed to:', e.detail.theme);
 *     // Update your canvas, charts, etc.
 * });
 * 
 * // Get current theme
 * const currentTheme = window.mvpThemeToggle.getCurrentTheme();
 * 
 * // Programmatically set theme
 * window.mvpThemeToggle.setTheme('light');
 * 
 * // Keyboard shortcut: Ctrl+Shift+T
 * 
 * ============================================
 */

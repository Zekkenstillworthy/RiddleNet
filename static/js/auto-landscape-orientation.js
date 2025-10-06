/**
 * ============================================
 * AUTO LANDSCAPE ORIENTATION - MVP MODULE (JS)
 * ============================================
 * 
 * Purpose: Detect device type and handle orientation changes
 * Target: Mobile phones and tablets
 * 
 * Features:
 * - Device type detection (mobile/tablet/desktop)
 * - Orientation change monitoring
 * - Portrait mode overlay management
 * - Screen lock API attempts (when supported)
 * - iOS and Android compatibility
 * 
 * Usage: Include this script in challenge page templates
 */

(function() {
    'use strict';

    // ============================================
    // DEVICE DETECTION
    // ============================================

    /**
     * Detect if the device is mobile or tablet
     */
    function detectDeviceType() {
        const ua = navigator.userAgent || navigator.vendor || window.opera;
        
        // Detect mobile devices
        const isMobile = /android|webos|iphone|ipod|blackberry|iemobile|opera mini/i.test(ua.toLowerCase());
        
        // Detect tablets (including iPad, Android tablets)
        const isTablet = /(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua.toLowerCase());
        
        // Additional iPad detection (iOS 13+ reports as desktop)
        const isIPad = /macintosh/i.test(ua) && navigator.maxTouchPoints && navigator.maxTouchPoints > 1;
        
        // Screen size check as fallback
        const screenWidth = window.screen.width;
        const screenHeight = window.screen.height;
        const smallScreen = Math.min(screenWidth, screenHeight) <= 768;
        
        return {
            isMobile: isMobile && !isTablet,
            isTablet: isTablet || isIPad,
            isDesktop: !isMobile && !isTablet && !isIPad,
            smallScreen: smallScreen
        };
    }

    /**
     * Get current device orientation
     */
    function getOrientation() {
        // Use screen.orientation API if available
        if (window.screen && window.screen.orientation) {
            return window.screen.orientation.type.includes('landscape') ? 'landscape' : 'portrait';
        }
        
        // Fallback to window dimensions
        return window.innerWidth > window.innerHeight ? 'landscape' : 'portrait';
    }

    /**
     * Check if device is in portrait mode
     */
    function isPortrait() {
        return getOrientation() === 'portrait';
    }

    // ============================================
    // OVERLAY MANAGEMENT
    // ============================================

    /**
     * Create and inject portrait mode overlay into DOM
     */
    function createPortraitOverlay() {
        // Check if overlay already exists
        if (document.getElementById('portrait-mode-overlay')) {
            return document.getElementById('portrait-mode-overlay');
        }

        // Create overlay element
        const overlay = document.createElement('div');
        overlay.id = 'portrait-mode-overlay';
        overlay.className = 'portrait-mode-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-live', 'polite');
        overlay.setAttribute('aria-label', 'Please rotate your device');

        // Create content
        overlay.innerHTML = `
            <div class="device-icon">
                <i class="fas fa-mobile-screen rotate-icon"></i>
            </div>
            <div class="portrait-message">
                <h2>Rotate Your Device</h2>
                <p><strong>For the best experience, please rotate your device to landscape mode.</strong></p>
                <p style="font-size: 14px; color: #94A3B8; margin-top: 16px;">
                    <i class="fas fa-info-circle"></i> This challenge is optimized for landscape viewing
                </p>
            </div>
        `;

        // Inject into body
        document.body.appendChild(overlay);
        
        return overlay;
    }

    /**
     * Show portrait mode overlay
     */
    function showPortraitOverlay() {
        const overlay = document.getElementById('portrait-mode-overlay');
        if (overlay) {
            overlay.classList.add('active');
            // Prevent scrolling when overlay is shown
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * Hide portrait mode overlay
     */
    function hidePortraitOverlay() {
        const overlay = document.getElementById('portrait-mode-overlay');
        if (overlay) {
            overlay.classList.remove('active');
            // Restore scrolling
            document.body.style.overflow = '';
        }
    }

    // ============================================
    // ORIENTATION HANDLING
    // ============================================

    /**
     * Handle orientation changes
     */
    function handleOrientationChange() {
        const device = detectDeviceType();
        
        // Only apply to mobile and tablet devices
        if (!device.isMobile && !device.isTablet) {
            hidePortraitOverlay();
            return;
        }

        // Check orientation
        if (isPortrait()) {
            showPortraitOverlay();
            console.log('[Auto-Landscape] Portrait mode detected - showing overlay');
        } else {
            hidePortraitOverlay();
            console.log('[Auto-Landscape] Landscape mode detected - hiding overlay');
        }
    }

    /**
     * Attempt to lock screen orientation to landscape (when supported)
     * Note: This only works in fullscreen mode or PWA mode on most browsers
     */
    async function attemptLandscapeLock() {
        // Check if Screen Orientation API is supported
        if (!window.screen || !window.screen.orientation || !window.screen.orientation.lock) {
            console.log('[Auto-Landscape] Screen Orientation Lock API not supported');
            return false;
        }

        try {
            await window.screen.orientation.lock('landscape');
            console.log('[Auto-Landscape] Screen locked to landscape');
            return true;
        } catch (error) {
            // Lock typically fails if not in fullscreen mode
            console.log('[Auto-Landscape] Could not lock orientation:', error.message);
            return false;
        }
    }

    /**
     * Request fullscreen (optional enhancement)
     */
    function requestFullscreen() {
        const elem = document.documentElement;
        
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) { // Safari
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { // IE11
            elem.msRequestFullscreen();
        }
    }

    // ============================================
    // INITIALIZATION
    // ============================================

    /**
     * Initialize auto-landscape system
     */
    function initialize() {
        console.log('[Auto-Landscape] Initializing...');
        
        // Detect device type
        const device = detectDeviceType();
        console.log('[Auto-Landscape] Device detection:', device);
        
        // Add device class to body for CSS targeting
        if (device.isMobile) {
            document.body.classList.add('mobile-device');
        } else if (device.isTablet) {
            document.body.classList.add('tablet-device');
        } else {
            document.body.classList.add('desktop-device');
        }

        // Only proceed for mobile/tablet
        if (!device.isMobile && !device.isTablet) {
            console.log('[Auto-Landscape] Desktop detected - orientation control disabled');
            return;
        }

        // Create overlay
        createPortraitOverlay();

        // Initial orientation check
        handleOrientationChange();

        // Listen for orientation changes - multiple event types for compatibility
        window.addEventListener('orientationchange', function() {
            // Small delay to ensure dimensions are updated
            setTimeout(handleOrientationChange, 100);
        });

        window.addEventListener('resize', function() {
            // Debounce resize events
            clearTimeout(window.orientationTimeout);
            window.orientationTimeout = setTimeout(handleOrientationChange, 200);
        });

        // Screen orientation API listener (modern browsers)
        if (window.screen && window.screen.orientation) {
            window.screen.orientation.addEventListener('change', function() {
                setTimeout(handleOrientationChange, 100);
            });
        }

        // Attempt landscape lock (will likely fail unless in fullscreen)
        attemptLandscapeLock();

        console.log('[Auto-Landscape] Initialization complete');
    }

    // ============================================
    // STARTUP
    // ============================================

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // DOM already loaded
        initialize();
    }

    // Re-check orientation when page becomes visible (for iOS PWA)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            handleOrientationChange();
        }
    });

    // Handle page focus
    window.addEventListener('focus', function() {
        handleOrientationChange();
    });

    // ============================================
    // GLOBAL API (for debugging)
    // ============================================

    window.AutoLandscape = {
        getDeviceInfo: detectDeviceType,
        getOrientation: getOrientation,
        isPortrait: isPortrait,
        showOverlay: showPortraitOverlay,
        hideOverlay: hidePortraitOverlay,
        lockLandscape: attemptLandscapeLock,
        requestFullscreen: requestFullscreen,
        refresh: handleOrientationChange
    };

    console.log('[Auto-Landscape] Global API available: window.AutoLandscape');

})();

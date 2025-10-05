/**
 * Auto-Fullscreen System for Challenge Pages
 * MVP Architecture: Automatically enters fullscreen on mobile/tablet in landscape
 * 
 * Features:
 * - Automatic fullscreen on landscape orientation detection
 * - Cross-browser compatibility (Chrome, Safari, Firefox, Edge)
 * - Graceful fallbacks for browsers without fullscreen API
 * - Exit fullscreen on orientation change to portrait
 * - Retry mechanism for user gesture requirements
 * 
 * @version 1.0.0
 * @author RiddleNet Team
 */

(function(window) {
  'use strict';

  // ============================================
  // Configuration
  // ============================================
  const CONFIG = {
    // Mobile breakpoint (pixels)
    mobileBreakpoint: 1024,
    
    // Delay before attempting fullscreen (ms)
    activationDelay: 300,
    
    // Retry delay if fullscreen fails (ms)
    retryDelay: 1000,
    
    // Maximum retry attempts
    maxRetries: 3,
    
    // Enable debug logging
    debug: false
  };

  // ============================================
  // State Management
  // ============================================
  let state = {
    isActive: false,
    retryCount: 0,
    fullscreenElement: null,
    userInteracted: false,
    initialized: false
  };

  // ============================================
  // Utility Functions
  // ============================================
  
  /**
   * Log debug messages if debug mode is enabled
   */
  function log(...args) {
    if (CONFIG.debug) {
      console.log('[AutoFullscreen]', ...args);
    }
  }

  /**
   * Detect if device is mobile/tablet
   */
  function isMobileDevice() {
    const userAgent = navigator.userAgent || navigator.vendor || window.opera;
    const isMobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini|mobile|tablet/i.test(userAgent);
    const isSmallScreen = window.innerWidth <= CONFIG.mobileBreakpoint;
    return isMobileUA || isSmallScreen;
  }

  /**
   * Check if currently in landscape orientation
   */
  function isLandscapeOrientation() {
    // Primary: Screen Orientation API
    if (screen.orientation) {
      return screen.orientation.type.includes('landscape');
    }
    
    // Fallback: Compare dimensions
    return window.innerWidth > window.innerHeight;
  }

  /**
   * Get fullscreen API methods (cross-browser)
   */
  function getFullscreenAPI() {
    const doc = document;
    const docEl = document.documentElement;
    
    // Standard API
    if (docEl.requestFullscreen) {
      return {
        request: 'requestFullscreen',
        exit: 'exitFullscreen',
        element: 'fullscreenElement',
        enabled: 'fullscreenEnabled',
        change: 'fullscreenchange',
        error: 'fullscreenerror'
      };
    }
    
    // Webkit (Safari)
    if (docEl.webkitRequestFullscreen) {
      return {
        request: 'webkitRequestFullscreen',
        exit: 'webkitExitFullscreen',
        element: 'webkitFullscreenElement',
        enabled: 'webkitFullscreenEnabled',
        change: 'webkitfullscreenchange',
        error: 'webkitfullscreenerror'
      };
    }
    
    // Mozilla
    if (docEl.mozRequestFullScreen) {
      return {
        request: 'mozRequestFullScreen',
        exit: 'mozCancelFullScreen',
        element: 'mozFullScreenElement',
        enabled: 'mozFullScreenEnabled',
        change: 'mozfullscreenchange',
        error: 'mozfullscreenerror'
      };
    }
    
    // Microsoft
    if (docEl.msRequestFullscreen) {
      return {
        request: 'msRequestFullscreen',
        exit: 'msExitFullscreen',
        element: 'msFullscreenElement',
        enabled: 'msFullscreenEnabled',
        change: 'MSFullscreenChange',
        error: 'MSFullscreenError'
      };
    }
    
    return null;
  }

  /**
   * Check if fullscreen is currently active
   */
  function isFullscreenActive() {
    const api = getFullscreenAPI();
    if (!api) return false;
    
    return !!(document[api.element]);
  }

  /**
   * Check if fullscreen API is available
   */
  function isFullscreenAvailable() {
    const api = getFullscreenAPI();
    if (!api) return false;
    
    return document[api.enabled] !== false;
  }

  // ============================================
  // Core Fullscreen Functions
  // ============================================
  
  /**
   * Enter fullscreen mode
   */
  async function enterFullscreen(element) {
    const api = getFullscreenAPI();
    
    if (!api) {
      log('Fullscreen API not available');
      return false;
    }
    
    if (!isFullscreenAvailable()) {
      log('Fullscreen is not enabled');
      return false;
    }
    
    if (isFullscreenActive()) {
      log('Already in fullscreen');
      return true;
    }
    
    try {
      const targetElement = element || document.documentElement;
      log('Attempting to enter fullscreen...', targetElement);
      
      await targetElement[api.request]();
      state.isActive = true;
      state.retryCount = 0;
      log('✓ Fullscreen activated successfully');
      return true;
      
    } catch (error) {
      log('✗ Fullscreen request failed:', error.message);
      
      // Retry if user gesture is required
      if (error.message.includes('user gesture') || error.message.includes('user interaction')) {
        if (state.retryCount < CONFIG.maxRetries) {
          state.retryCount++;
          log(`Retry attempt ${state.retryCount}/${CONFIG.maxRetries} scheduled...`);
          
          setTimeout(() => {
            if (!state.userInteracted) {
              log('Waiting for user interaction...');
              setupUserInteractionListener();
            }
          }, CONFIG.retryDelay);
        }
      }
      
      return false;
    }
  }

  /**
   * Exit fullscreen mode
   */
  async function exitFullscreen() {
    const api = getFullscreenAPI();
    
    if (!api || !isFullscreenActive()) {
      log('Not in fullscreen, nothing to exit');
      return true;
    }
    
    try {
      log('Exiting fullscreen...');
      await document[api.exit]();
      state.isActive = false;
      log('✓ Fullscreen exited successfully');
      return true;
      
    } catch (error) {
      log('✗ Failed to exit fullscreen:', error.message);
      return false;
    }
  }

  // ============================================
  // Interaction Handling
  // ============================================
  
  /**
   * Setup listener for first user interaction
   */
  function setupUserInteractionListener() {
    const events = ['click', 'touchstart', 'keydown'];
    
    function onUserInteraction() {
      if (state.userInteracted) return;
      
      state.userInteracted = true;
      log('User interaction detected');
      
      // Remove listeners
      events.forEach(event => {
        document.removeEventListener(event, onUserInteraction);
      });
      
      // Retry fullscreen if needed
      if (isMobileDevice() && isLandscapeOrientation() && !isFullscreenActive()) {
        setTimeout(() => {
          enterFullscreen(state.fullscreenElement);
        }, 100);
      }
    }
    
    // Add listeners
    events.forEach(event => {
      document.addEventListener(event, onUserInteraction, { once: true, passive: true });
    });
  }

  // ============================================
  // Orientation Handling
  // ============================================
  
  /**
   * Handle orientation change
   */
  function handleOrientationChange() {
    log('Orientation changed', {
      isLandscape: isLandscapeOrientation(),
      isMobile: isMobileDevice(),
      isFullscreen: isFullscreenActive()
    });
    
    if (!isMobileDevice()) {
      log('Not a mobile device, skipping fullscreen');
      return;
    }
    
    if (isLandscapeOrientation()) {
      // Enter fullscreen in landscape
      if (!isFullscreenActive()) {
        setTimeout(() => {
          enterFullscreen(state.fullscreenElement);
        }, CONFIG.activationDelay);
      }
    } else {
      // Exit fullscreen in portrait (optional - keep commented to maintain fullscreen)
      // if (isFullscreenActive()) {
      //   exitFullscreen();
      // }
    }
  }

  /**
   * Setup orientation change listeners
   */
  function setupOrientationListeners() {
    // Screen Orientation API
    if (screen.orientation) {
      screen.orientation.addEventListener('change', handleOrientationChange);
    }
    
    // Legacy orientationchange event
    window.addEventListener('orientationchange', () => {
      setTimeout(handleOrientationChange, 100);
    });
    
    // Resize fallback
    window.addEventListener('resize', () => {
      setTimeout(handleOrientationChange, 100);
    });
    
    log('Orientation listeners setup complete');
  }

  // ============================================
  // Fullscreen Event Handlers
  // ============================================
  
  /**
   * Setup fullscreen change listeners
   */
  function setupFullscreenListeners() {
    const api = getFullscreenAPI();
    if (!api) return;
    
    // Fullscreen change event
    document.addEventListener(api.change, () => {
      const isActive = isFullscreenActive();
      log('Fullscreen state changed:', isActive ? 'ACTIVE' : 'INACTIVE');
      state.isActive = isActive;
      
      // Trigger custom event
      window.dispatchEvent(new CustomEvent('autofullscreenchange', {
        detail: { isActive }
      }));
    });
    
    // Fullscreen error event
    document.addEventListener(api.error, (event) => {
      log('Fullscreen error:', event);
      
      // Trigger custom event
      window.dispatchEvent(new CustomEvent('autofullscreenerror', {
        detail: { error: event }
      }));
    });
    
    log('Fullscreen event listeners setup complete');
  }

  // ============================================
  // Initialization
  // ============================================
  
  /**
   * Initialize the auto-fullscreen system
   * 
   * @param {Object} options - Configuration options
   * @param {HTMLElement} options.element - Element to fullscreen (default: documentElement)
   * @param {number} options.delay - Activation delay in ms
   * @param {boolean} options.debug - Enable debug logging
   */
  function initAutoFullscreen(options = {}) {
    if (state.initialized) {
      log('Already initialized');
      return;
    }
    
    // Merge options with config
    if (options.debug !== undefined) CONFIG.debug = options.debug;
    if (options.delay !== undefined) CONFIG.activationDelay = options.delay;
    
    // Store target element
    state.fullscreenElement = options.element || document.documentElement;
    
    log('Initializing Auto-Fullscreen System...', {
      element: state.fullscreenElement.tagName,
      isMobile: isMobileDevice(),
      isLandscape: isLandscapeOrientation(),
      fullscreenAvailable: isFullscreenAvailable()
    });
    
    // Check if fullscreen is supported
    if (!isFullscreenAvailable()) {
      log('⚠ Fullscreen API not available on this device/browser');
      state.initialized = true;
      return;
    }
    
    // Setup event listeners
    setupOrientationListeners();
    setupFullscreenListeners();
    
    // Initial orientation check
    setTimeout(() => {
      if (isMobileDevice() && isLandscapeOrientation()) {
        log('Initial landscape detected, attempting fullscreen...');
        enterFullscreen(state.fullscreenElement);
      }
    }, CONFIG.activationDelay);
    
    // Setup user interaction fallback
    setupUserInteractionListener();
    
    state.initialized = true;
    log('✓ Auto-Fullscreen System initialized successfully');
  }

  /**
   * Destroy the auto-fullscreen system
   */
  function destroyAutoFullscreen() {
    log('Destroying Auto-Fullscreen System...');
    
    // Exit fullscreen if active
    if (isFullscreenActive()) {
      exitFullscreen();
    }
    
    // Reset state
    state = {
      isActive: false,
      retryCount: 0,
      fullscreenElement: null,
      userInteracted: false,
      initialized: false
    };
    
    log('✓ Auto-Fullscreen System destroyed');
  }

  // ============================================
  // Public API
  // ============================================
  
  window.AutoFullscreen = {
    init: initAutoFullscreen,
    destroy: destroyAutoFullscreen,
    enter: enterFullscreen,
    exit: exitFullscreen,
    isActive: isFullscreenActive,
    isAvailable: isFullscreenAvailable,
    isMobile: isMobileDevice,
    isLandscape: isLandscapeOrientation,
    
    // State getter
    getState: () => ({ ...state }),
    
    // Config setter
    setConfig: (newConfig) => {
      Object.assign(CONFIG, newConfig);
      log('Config updated:', CONFIG);
    }
  };
  
  // Expose shorthand
  window.initAutoFullscreen = initAutoFullscreen;
  
  log('Auto-Fullscreen module loaded');

})(window);

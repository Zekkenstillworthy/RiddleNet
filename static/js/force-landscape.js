// MVP Auto-Landscape Experience Helper
// Automatically prompts mobile/tablet users to rotate to landscape for optimal experience
// Minimal, functional approach without forced fullscreen
(function () {
  let landscapePromptShown = false;
  let orientationCheckInterval = null;

  function isMobile() {
    return /Mobi|Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
  }

  function isTablet() {
    const ua = navigator.userAgent.toLowerCase();
    return (/(tablet|ipad|playbook|silk)|(android(?!.*mobile))/i.test(ua));
  }

  function isMobileOrTablet() {
    return isMobile() || isTablet();
  }

  function isMobileOrTablet() {
    return isMobile() || isTablet();
  }

  function ensureOverlay() {
    let overlay = document.getElementById('force-landscape-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'force-landscape-overlay';
      overlay.innerHTML = (
        '<div class="flo-backdrop">' +
        '  <div class="flo-card">' +
        '    <div class="flo-icon">📱↔️</div>' +
        '    <h3 class="flo-title">Rotate to Landscape</h3>' +
        '    <p class="flo-text">For the best experience, please rotate your device to landscape mode.</p>' +
        '  </div>' +
        '</div>'
      );
      document.body.appendChild(overlay);
    }
    return overlay;
  }

  function isLandscape() {
    // Use matchMedia when available
    if (window.matchMedia) {
      return window.matchMedia('(orientation: landscape)').matches;
    }
    // Fallback heuristic
    return window.innerWidth > window.innerHeight;
  }

  function onOrientationSatisfied() {
    const overlay = document.getElementById('force-landscape-overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
    landscapePromptShown = false;
    console.log('✅ Landscape orientation detected');
  }

  function onOrientationUnsatisfied() {
    if (!landscapePromptShown) {
      const overlay = ensureOverlay();
      overlay.style.display = 'block';
      landscapePromptShown = true;
      console.log('ℹ️ Portrait detected - showing landscape prompt');
    }
  }

  function checkAndAct() {
    if (!isMobileOrTablet()) return; // Desktop: do nothing
    
    if (isLandscape()) {
      onOrientationSatisfied();
    } else {
      onOrientationUnsatisfied();
    }
  }

  window.initForceLandscape = function initForceLandscape(options) {
    const opts = Object.assign({ 
      pageKey: ''
    }, options || {});
    
    // Initial check after DOM loads
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        setTimeout(() => checkAndAct(), 100);
      });
    } else {
      setTimeout(() => checkAndAct(), 100);
    }
    
    // Respond to orientation changes
    window.addEventListener('orientationchange', () => {
      setTimeout(() => checkAndAct(), 200);
    });
    
    window.addEventListener('resize', () => {
      setTimeout(() => checkAndAct(), 100);
    });
    
    if (screen.orientation && screen.orientation.addEventListener) {
      screen.orientation.addEventListener('change', () => {
        setTimeout(() => checkAndAct(), 200);
      });
    }
    
    // Periodic check for orientation (fallback)
    if (orientationCheckInterval) {
      clearInterval(orientationCheckInterval);
    }
    orientationCheckInterval = setInterval(() => checkAndAct(), 2000);
    
    console.log(`📱 MVP Landscape orientation helper initialized for: ${opts.pageKey}`);
  };
})();

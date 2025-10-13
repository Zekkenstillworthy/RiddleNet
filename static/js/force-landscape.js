// MVP Auto-Landscape & Fullscreen Experience Helper
// Automatically prompts mobile/tablet users to rotate to landscape and enter fullscreen
// Provides fullscreen mode with exit button for optimal immersive experience
(function () {
  let landscapePromptShown = false;
  let orientationCheckInterval = null;
  let fullscreenAttempted = false;
  let fullscreenExitBtn = null;
  let fullscreenDeniedMsg = null;

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

  function ensureOverlay() {
    let overlay = document.getElementById('force-landscape-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'force-landscape-overlay';
      overlay.className = 'portrait-mode-overlay';
      overlay.innerHTML = (
        '<div class="flo-backdrop">' +
        '  <div class="flo-card">' +
        '    <div class="rotate-icon">📱↔️</div>' +
        '    <div class="portrait-message">' +
        '      <h2>MVP: Rotate to Landscape</h2>' +
        '      <p>For the optimal MVP experience, please rotate your device to landscape mode.</p>' +
        '      <p style="color: #00D9FF; font-weight: 600; margin-top: 1rem;"><i class="fas fa-expand-arrows-alt"></i> We\'ll automatically enter fullscreen for an immersive learning experience.</p>' +
        '      <p style="color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-top: 0.5rem;">This challenge is optimized for landscape viewing</p>' +
        '    </div>' +
        '  </div>' +
        '</div>'
      );
      document.body.appendChild(overlay);
    }
    return overlay;
  }

  function createFullscreenExitButton() {
    if (!fullscreenExitBtn) {
      fullscreenExitBtn = document.createElement('button');
      fullscreenExitBtn.className = 'fullscreen-exit-btn';
      fullscreenExitBtn.innerHTML = '<i class="fas fa-times"></i> Exit Fullscreen';
      fullscreenExitBtn.addEventListener('click', exitFullscreen);
      document.body.appendChild(fullscreenExitBtn);
    }
    return fullscreenExitBtn;
  }

  function createFullscreenDeniedMessage() {
    if (!fullscreenDeniedMsg) {
      fullscreenDeniedMsg = document.createElement('div');
      fullscreenDeniedMsg.className = 'fullscreen-denied-msg';
      fullscreenDeniedMsg.innerHTML = '<i class="fas fa-info-circle"></i> Fullscreen mode requires user interaction. Click anywhere to continue.';
      document.body.appendChild(fullscreenDeniedMsg);
    }
    return fullscreenDeniedMsg;
  }

  function showFullscreenExitButton() {
    const btn = createFullscreenExitButton();
    btn.classList.add('visible');
  }

  function hideFullscreenExitButton() {
    if (fullscreenExitBtn) {
      fullscreenExitBtn.classList.remove('visible');
    }
  }

  function showFullscreenDeniedMessage() {
    const msg = createFullscreenDeniedMessage();
    msg.classList.add('visible');
    setTimeout(() => {
      msg.classList.remove('visible');
    }, 5000);
  }

  function isLandscape() {
    // Use matchMedia when available
    if (window.matchMedia) {
      return window.matchMedia('(orientation: landscape)').matches;
    }
    // Fallback heuristic
    return window.innerWidth > window.innerHeight;
  }

  function isFullscreen() {
    return !!(
      document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.mozFullScreenElement ||
      document.msFullscreenElement
    );
  }

  function enterFullscreen() {
    const elem = document.documentElement;
    
    const requestFullscreen = 
      elem.requestFullscreen ||
      elem.webkitRequestFullscreen ||
      elem.webkitEnterFullscreen ||
      elem.mozRequestFullScreen ||
      elem.msRequestFullscreen;

    if (requestFullscreen) {
      requestFullscreen.call(elem)
        .then(() => {
          console.log('✅ Fullscreen mode activated');
          document.body.classList.add('in-fullscreen');
          showFullscreenExitButton();
          fullscreenAttempted = true;
        })
        .catch((err) => {
          console.warn('⚠️ Fullscreen request failed:', err);
          showFullscreenDeniedMessage();
          fullscreenAttempted = true;
        });
    } else {
      console.warn('⚠️ Fullscreen API not supported');
      showFullscreenDeniedMessage();
      fullscreenAttempted = true;
    }
  }

  function exitFullscreen() {
    const exitMethod = 
      document.exitFullscreen ||
      document.webkitExitFullscreen ||
      document.mozCancelFullScreen ||
      document.msExitFullscreen;

    if (exitMethod) {
      exitMethod.call(document)
        .then(() => {
          console.log('✅ Exited fullscreen mode');
          document.body.classList.remove('in-fullscreen');
          hideFullscreenExitButton();
          fullscreenAttempted = false;
        })
        .catch((err) => {
          console.warn('⚠️ Exit fullscreen failed:', err);
        });
    }
  }

  function onOrientationSatisfied() {
    const overlay = document.getElementById('force-landscape-overlay');
    if (overlay) {
      overlay.classList.remove('active');
      overlay.style.display = 'none';
    }
    landscapePromptShown = false;
    
    // Attempt fullscreen if on mobile/tablet and not already attempted
    if (isMobileOrTablet() && !fullscreenAttempted && isLandscape()) {
      // Small delay to allow orientation to settle
      setTimeout(() => {
        if (!isFullscreen()) {
          enterFullscreen();
        }
      }, 500);
    }
    
    console.log('✅ Landscape orientation detected');
  }

  function onOrientationUnsatisfied() {
    if (!landscapePromptShown) {
      const overlay = ensureOverlay();
      overlay.classList.add('active');
      overlay.style.display = 'flex';
      landscapePromptShown = true;
      
      // Exit fullscreen if in portrait mode
      if (isFullscreen()) {
        exitFullscreen();
      }
      
      console.log('ℹ️ Portrait detected - showing landscape prompt');
    }
  }

  function checkAndAct() {
    if (!isMobileOrTablet()) {
      // Desktop: hide overlay if shown
      const overlay = document.getElementById('force-landscape-overlay');
      if (overlay) {
        overlay.style.display = 'none';
      }
      return;
    }
    
    if (isLandscape()) {
      onOrientationSatisfied();
    } else {
      onOrientationUnsatisfied();
    }
  }

  function handleFullscreenChange() {
    if (!isFullscreen()) {
      document.body.classList.remove('in-fullscreen');
      hideFullscreenExitButton();
      console.log('ℹ️ Fullscreen exited');
    } else {
      document.body.classList.add('in-fullscreen');
      showFullscreenExitButton();
      console.log('✅ Fullscreen active');
    }
  }

  window.initForceLandscape = function initForceLandscape(options) {
    const opts = Object.assign({ 
      pageKey: '',
      autoFullscreen: true
    }, options || {});
    
    // Listen for fullscreen changes
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);
    
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
    
    // User interaction trigger for fullscreen (iOS requirement)
    document.addEventListener('click', function fullscreenClickHandler() {
      if (isMobileOrTablet() && isLandscape() && !fullscreenAttempted) {
        enterFullscreen();
        document.removeEventListener('click', fullscreenClickHandler);
      }
    }, { once: true });
    
    console.log(`📱 MVP Landscape orientation & fullscreen helper initialized for: ${opts.pageKey}`);
  };

  // Expose exit fullscreen for external use
  window.exitChallengeFullscreen = exitFullscreen;
})();
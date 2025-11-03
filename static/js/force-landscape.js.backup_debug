// MVP Orientation Helper with Portrait/Landscape Choice
// Asks learners to pick their preferred orientation and provides fullscreen support when landscape is chosen
// Keeps existing fullscreen escape mechanisms while allowing portrait-friendly layouts
(function () {
  let landscapePromptShown = false;
  let orientationCheckInterval = null;
  let fullscreenAttempted = false;
  let fullscreenExitBtn = null;
  let fullscreenDeniedMsg = null;
  let overlayElement = null;
  let orientationToggleBtn = null;
  let orientationPreference = null;
  let orientationStorageKey = null;
  let fullscreenClickHandler = null;
  let listenersBound = false;
  let initOptions = {
    pageKey: '',
    autoFullscreen: true,
    rememberChoice: true,
    showToggle: true
  };

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
    if (overlayElement) {
      return overlayElement;
    }

    overlayElement = document.createElement('div');
    overlayElement.id = 'force-landscape-overlay';
    overlayElement.className = 'portrait-mode-overlay';
    overlayElement.dataset.state = 'hidden';
    overlayElement.innerHTML = [
      '<div class="flo-backdrop">',
      '  <div class="flo-card">',
      '    <div class="orientation-choice">',
      '      <div class="flo-icon">📱</div>',
      '      <h2 class="flo-title">Choose Your View</h2>',
      '      <p class="flo-text">Landscape unlocks the full workspace. Portrait keeps controls stacked when space is limited.</p>',
      '      <div class="orientation-actions">',
      '        <button class="flo-btn flo-btn-landscape" data-choice="landscape">Landscape Mode</button>',
      '        <button class="flo-btn flo-btn-portrait" data-choice="portrait">Portrait Mode</button>',
      '      </div>',
      '    </div>',
      '    <div class="rotate-prompt">',
      '      <div class="flo-icon">📱↔️</div>',
      '      <h2 class="flo-title">Rotate to Landscape</h2>',
      '      <p class="flo-text">You selected landscape for the optimal layout. Rotate your device or switch to portrait if you prefer.</p>',
      '      <button class="flo-link" data-action="change-preference">Switch to portrait instead</button>',
      '    </div>',
      '  </div>',
      '</div>'
    ].join('');
    document.body.appendChild(overlayElement);

    overlayElement.querySelectorAll('[data-choice]').forEach((btn) => {
      btn.addEventListener('click', (event) => {
        const choice = event.currentTarget.getAttribute('data-choice');
        selectOrientation(choice);
      });
    });

    overlayElement.querySelectorAll('[data-action="change-preference"]').forEach((btn) => {
      btn.addEventListener('click', (event) => {
        event.preventDefault();
        showOrientationChoice(true);
      });
    });

    return overlayElement;
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
      fullscreenDeniedMsg.innerHTML = '<i class="fas fa-info-circle"></i> Fullscreen mode requires user interaction. Tap anywhere to continue.';
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
    if (initOptions.autoFullscreen === false) {
      return;
    }

    const elem = document.documentElement;
    const requestFullscreen =
      elem.requestFullscreen ||
      elem.webkitRequestFullscreen ||
      elem.webkitEnterFullscreen ||
      elem.mozRequestFullScreen ||
      elem.msRequestFullscreen;

    if (!requestFullscreen) {
      console.warn('⚠️ Fullscreen API not supported');
      showFullscreenDeniedMessage();
      fullscreenAttempted = true;
      return;
    }

    try {
      const result = requestFullscreen.call(elem);
      if (result && typeof result.then === 'function') {
        result.then(() => {
          document.body.classList.add('in-fullscreen');
          showFullscreenExitButton();
          fullscreenAttempted = true;
          console.log('✅ Fullscreen mode activated');
        }).catch((err) => {
          console.warn('⚠️ Fullscreen request failed:', err);
          showFullscreenDeniedMessage();
          fullscreenAttempted = true;
        });
      } else {
        document.body.classList.add('in-fullscreen');
        showFullscreenExitButton();
        fullscreenAttempted = true;
        console.log('✅ Fullscreen mode activated');
      }
    } catch (err) {
      console.warn('⚠️ Fullscreen request failed:', err);
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

    if (!exitMethod) {
      document.body.classList.remove('in-fullscreen');
      hideFullscreenExitButton();
      fullscreenAttempted = false;
      return;
    }

    try {
      const result = exitMethod.call(document);
      if (result && typeof result.then === 'function') {
        result.then(() => {
          document.body.classList.remove('in-fullscreen');
          hideFullscreenExitButton();
          fullscreenAttempted = false;
          console.log('✅ Exited fullscreen mode');
        }).catch((err) => {
          console.warn('⚠️ Exit fullscreen failed:', err);
        });
      } else {
        document.body.classList.remove('in-fullscreen');
        hideFullscreenExitButton();
        fullscreenAttempted = false;
        console.log('✅ Exited fullscreen mode');
      }
    } catch (err) {
      console.warn('⚠️ Exit fullscreen failed:', err);
    }
  }

  function onOrientationSatisfied() {
    if (orientationPreference !== 'landscape') {
      hideOverlay();
      return;
    }

    hideOverlay();
    landscapePromptShown = false;

    if (isMobileOrTablet() && initOptions.autoFullscreen !== false && !fullscreenAttempted && isLandscape()) {
      setTimeout(() => {
        if (orientationPreference === 'landscape' && !isFullscreen()) {
          enterFullscreen();
        }
      }, 500);
    }
  }

  function onOrientationUnsatisfied() {
    if (orientationPreference !== 'landscape') {
      hideOverlay();
      return;
    }

    setOverlayState('rotate');
    landscapePromptShown = true;

    if (isFullscreen()) {
      exitFullscreen();
    }
  }

  function checkAndAct() {
    if (orientationPreference !== 'landscape') {
      return;
    }

    if (!isMobileOrTablet()) {
      hideOverlay();
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

  function setOverlayState(state) {
    const overlay = ensureOverlay();
    overlay.dataset.state = state;
    if (state === 'hidden') {
      overlay.classList.remove('active');
      overlay.style.display = 'none';
    } else {
      overlay.classList.add('active');
      overlay.style.display = 'flex';
    }
  }

  function hideOverlay() {
    if (!overlayElement) {
      return;
    }
    overlayElement.dataset.state = 'hidden';
    overlayElement.classList.remove('active');
    overlayElement.style.display = 'none';
  }

  function showOrientationChoice(force) {
    if (!force && !isMobileOrTablet()) {
      return;
    }
    stopMonitoring();
    if (fullscreenClickHandler) {
      document.removeEventListener('click', fullscreenClickHandler);
      fullscreenClickHandler = null;
    }
    orientationPreference = null;
    landscapePromptShown = false;
    setOverlayState('choose');
    updateOrientationToggle(null);
    if (isFullscreen()) {
      exitFullscreen();
    }
  }

  function startMonitoring() {
    if (orientationCheckInterval) {
      clearInterval(orientationCheckInterval);
    }
    orientationCheckInterval = setInterval(() => checkAndAct(), 2000);
  }

  function stopMonitoring() {
    if (orientationCheckInterval) {
      clearInterval(orientationCheckInterval);
      orientationCheckInterval = null;
    }
  }

  function persistPreference(choice) {
    if (!orientationStorageKey) {
      return;
    }
    try {
      localStorage.setItem(orientationStorageKey, choice);
    } catch (err) {
      console.warn('⚠️ Unable to store orientation preference', err);
    }
  }

  function readStoredPreference() {
    if (!orientationStorageKey) {
      return null;
    }
    try {
      return localStorage.getItem(orientationStorageKey);
    } catch (err) {
      console.warn('⚠️ Unable to read stored orientation preference', err);
      return null;
    }
  }

  function createOrientationToggle() {
    if (orientationToggleBtn) {
      return orientationToggleBtn;
    }
    orientationToggleBtn = document.createElement('button');
    orientationToggleBtn.type = 'button';
    orientationToggleBtn.className = 'orientation-toggle-btn';
    orientationToggleBtn.textContent = 'Choose orientation';
    orientationToggleBtn.addEventListener('click', () => showOrientationChoice(true));
    document.body.appendChild(orientationToggleBtn);
    return orientationToggleBtn;
  }

  function updateOrientationToggle(choice) {
    if (initOptions.showToggle === false) {
      return;
    }

    const btn = createOrientationToggle();
    if (!isMobileOrTablet()) {
      btn.style.display = 'none';
      return;
    }

    btn.style.display = 'flex';

    if (!choice) {
      btn.dataset.selected = 'none';
      btn.textContent = 'Choose orientation';
    } else if (choice === 'landscape') {
      btn.dataset.selected = 'landscape';
      btn.textContent = 'Landscape view';
    } else {
      btn.dataset.selected = 'portrait';
      btn.textContent = 'Portrait view';
    }
  }

  function setupFullscreenClickHandler() {
    if (fullscreenClickHandler) {
      document.removeEventListener('click', fullscreenClickHandler);
      fullscreenClickHandler = null;
    }

    if (initOptions.autoFullscreen === false) {
      return;
    }

    fullscreenClickHandler = function () {
      if (orientationPreference === 'landscape' && isMobileOrTablet() && isLandscape() && !fullscreenAttempted) {
        enterFullscreen();
      }
    };

    document.addEventListener('click', fullscreenClickHandler, { once: true });
  }

  function selectOrientation(choice) {
    const normalized = choice === 'portrait' ? 'portrait' : 'landscape';
    persistPreference(normalized);
    applyOrientationPreference(normalized);
  }

  function applyOrientationPreference(choice) {
    if (!choice) {
      updateOrientationToggle(null);
      return;
    }

    const normalized = choice === 'portrait' ? 'portrait' : 'landscape';
    orientationPreference = normalized;
    landscapePromptShown = false;

    if (normalized === 'landscape') {
      updateOrientationToggle('landscape');
      if (isMobileOrTablet()) {
        startMonitoring();
        setupFullscreenClickHandler();
      } else {
        stopMonitoring();
        if (fullscreenClickHandler) {
          document.removeEventListener('click', fullscreenClickHandler);
          fullscreenClickHandler = null;
        }
      }
      checkAndAct();
      console.log('📱 Landscape preference active');
    } else {
      updateOrientationToggle('portrait');
      stopMonitoring();
      hideOverlay();
      if (isFullscreen()) {
        exitFullscreen();
      }
      fullscreenAttempted = false;

      if (fullscreenClickHandler) {
        document.removeEventListener('click', fullscreenClickHandler);
        fullscreenClickHandler = null;
      }
      console.log('📱 Portrait preference active');
    }
  }

  function bindListenersOnce() {
    if (listenersBound) {
      return;
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);

    window.addEventListener('orientationchange', () => {
      setTimeout(() => checkAndAct(), 200);
    });

    window.addEventListener('resize', () => {
      setTimeout(() => checkAndAct(), 100);
    });

    if (typeof screen !== 'undefined' && screen.orientation && screen.orientation.addEventListener) {
      screen.orientation.addEventListener('change', () => {
        setTimeout(() => checkAndAct(), 200);
      });
    }

    listenersBound = true;
  }

  window.initForceLandscape = function initForceLandscape(options) {
    initOptions = Object.assign({
      pageKey: '',
      autoFullscreen: true,
      rememberChoice: true,
      showToggle: true
    }, options || {});

    orientationStorageKey = initOptions.rememberChoice === false
      ? null
      : `forceLandscapePreference_${initOptions.pageKey || 'global'}`;

    const storedPreference = readStoredPreference();
    if (storedPreference) {
      orientationPreference = storedPreference;
    } else if (!isMobileOrTablet()) {
      orientationPreference = 'landscape';
    } else {
      orientationPreference = null;
    }

    bindListenersOnce();

    const finalizeInit = () => {
      if (initOptions.showToggle !== false) {
        createOrientationToggle();
      }

      updateOrientationToggle(orientationPreference);

      if (!isMobileOrTablet()) {
        applyOrientationPreference('landscape');
        hideOverlay();
        return;
      }

      if (orientationPreference) {
        applyOrientationPreference(orientationPreference);
      } else {
        showOrientationChoice(false);
      }
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        setTimeout(finalizeInit, 100);
      });
    } else {
      setTimeout(finalizeInit, 0);
    }

    console.log(`📱 Orientation helper initialized for: ${initOptions.pageKey || 'global'}`);
  };

  // Expose exit fullscreen for external use
  window.exitChallengeFullscreen = exitFullscreen;
})();
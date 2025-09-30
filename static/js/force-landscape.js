// Reusable landscape experience helper
// Attempts to lock to landscape on mobile; falls back to rotate overlay and optional pseudo-rotation
(function () {
  function isMobile() {
    return /Mobi|Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
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
        '    <h3 class="flo-title">Best viewed in landscape</h3>' +
        '    <p class="flo-text">Rotate your device for the optimal experience. On supported devices, we can also switch automatically.</p>' +
        '    <div class="flo-actions">' +
        '      <button id="flo-try-landscape" class="flo-btn">Switch to landscape</button>' +
        '    </div>' +
        '  </div>' +
        '</div>'
      );
      document.body.appendChild(overlay);
    }
    return overlay;
  }

  async function tryLockLandscape() {
    try {
      // Some browsers require fullscreen to lock orientation
      const el = document.documentElement;
      if (el.requestFullscreen && !document.fullscreenElement) {
        await el.requestFullscreen();
      }
      if (screen.orientation && screen.orientation.lock) {
        await screen.orientation.lock('landscape');
        return true;
      }
    } catch (e) {
      // ignore
    }
    return false;
  }

  function applyPseudoLandscape(targetSelector) {
    const target = targetSelector ? document.querySelector(targetSelector) : document.body;
    if (!target) return false;
    document.body.classList.add('pseudo-landscape-active');
    let wrapper = document.getElementById('pseudo-landscape-wrapper');
    if (!wrapper) {
      wrapper = document.createElement('div');
      wrapper.id = 'pseudo-landscape-wrapper';
      // Move all children into wrapper to rotate as a whole
      while (document.body.firstChild && document.body.firstChild !== wrapper) {
        wrapper.appendChild(document.body.firstChild);
      }
      document.body.appendChild(wrapper);
    }
    return true;
  }

  function clearPseudoLandscape() {
    const wrapper = document.getElementById('pseudo-landscape-wrapper');
    if (!wrapper) return;
    // Move children out of wrapper back to body
    const frag = document.createDocumentFragment();
    while (wrapper.firstChild) frag.appendChild(wrapper.firstChild);
    wrapper.replaceWith(frag);
    document.body.classList.remove('pseudo-landscape-active');
  }

  function onOrientationSatisfied() {
    const overlay = document.getElementById('force-landscape-overlay');
    if (overlay) overlay.style.display = 'none';
    clearPseudoLandscape();
  }

  function onOrientationUnsatisfied(options) {
    const overlay = ensureOverlay();
    overlay.style.display = 'block';
    const btn = document.getElementById('flo-try-landscape');
    if (btn) {
      btn.onclick = async () => {
        const ok = await tryLockLandscape();
        if (!ok && options && options.allowRotateFallback) {
          applyPseudoLandscape(options.rotateTargetSelector);
        }
        // Re-evaluate after a short delay
        setTimeout(checkAndAct.bind(null, options), 300);
      };
    }
  }

  function isLandscape() {
    // Use matchMedia when available
    if (window.matchMedia) {
      return window.matchMedia('(orientation: landscape)').matches;
    }
    // Fallback heuristic
    return window.innerWidth > window.innerHeight;
  }

  function checkAndAct(options) {
    if (!isMobile()) return; // Desktop: do nothing
    if (isLandscape()) {
      onOrientationSatisfied();
    } else {
      onOrientationUnsatisfied(options || {});
    }
  }

  window.initForceLandscape = function initForceLandscape(options) {
    const opts = Object.assign({ allowRotateFallback: false, rotateTargetSelector: null, pageKey: '' }, options || {});
    document.addEventListener('DOMContentLoaded', function () {
      // Initial check
      setTimeout(() => checkAndAct(opts), 50);
    });
    // Respond to changes
    window.addEventListener('orientationchange', () => setTimeout(() => checkAndAct(opts), 100));
    window.addEventListener('resize', () => setTimeout(() => checkAndAct(opts), 100));
    if (screen.orientation && screen.orientation.addEventListener) {
      screen.orientation.addEventListener('change', () => setTimeout(() => checkAndAct(opts), 100));
    }
  };
})();

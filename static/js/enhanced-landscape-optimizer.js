/**
 * RiddleNet Enhanced Landscape Optimizer
 * Extends the existing auto-landscape system with improved mobile landscape support
 * Version: 2.0 - Touch-Optimized & Performance Enhanced
 */

(function() {
    'use strict';

    // Wait for existing auto-landscape optimizer to load
    const waitForAutoLandscape = () => {
        return new Promise((resolve) => {
            if (window.AutoLandscapeOptimizer || window.autoLandscapeOptimizer) {
                resolve();
            } else {
                setTimeout(() => waitForAutoLandscape().then(resolve), 100);
            }
        });
    };

    class EnhancedLandscapeOptimizer {
        constructor() {
            this.isEnhanced = false;
            this.touchTargets = new Map();
            this.tooltipTimeout = null;
            this.activeTooltip = null;
            this.resizeObserver = null;
            this.intersectionObserver = null;
            
            // Enhanced configuration
            this.config = {
                touchTargetMinSize: 44,
                tooltipDelay: 500,
                animationDuration: 300,
                debounceDelay: 150,
                performanceMode: this.detectPerformanceMode()
            };
            
            this.init();
        }

        detectPerformanceMode() {
            // Detect device performance capabilities
            const memory = navigator.deviceMemory || 4; // GB
            const cores = navigator.hardwareConcurrency || 4;
            const connection = navigator.connection?.effectiveType || '4g';
            
            // Low-end device detection
            if (memory <= 2 || cores <= 2 || connection === '2g' || connection === 'slow-2g') {
                return 'low';
            }
            
            return memory >= 8 && cores >= 8 ? 'high' : 'medium';
        }

        async init() {
            console.log('[Enhanced Landscape] Initializing...');
            
            // Wait for base auto-landscape system
            await waitForAutoLandscape();
            
            // Setup enhanced features
            this.setupTouchTargetEnhancement();
            this.setupNavigationTooltips();
            this.setupAccessibilityEnhancements();
            this.setupPerformanceOptimizations();
            this.setupOrientationHandling();
            
            // Listen for base auto-landscape events
            window.addEventListener('landscapeModeEnabled', this.onLandscapeModeEnabled.bind(this));
            window.addEventListener('landscapeModeDisabled', this.onLandscapeModeDisabled.bind(this));
            
            console.log('[Enhanced Landscape] Initialized with performance mode:', this.config.performanceMode);
        }

        onLandscapeModeEnabled(event) {
            console.log('[Enhanced Landscape] Landscape mode enabled');
            this.isEnhanced = true;
            this.enableEnhancements();
            this.optimizeForPage(event.detail.page);
        }

        onLandscapeModeDisabled(event) {
            console.log('[Enhanced Landscape] Landscape mode disabled');
            this.isEnhanced = false;
            this.disableEnhancements();
        }

        enableEnhancements() {
            // Add enhanced class to body
            document.body.classList.add('enhanced-landscape-active');
            
            // Enable touch target monitoring
            this.monitorTouchTargets();
            
            // Show tooltips for collapsed nav
            this.showNavigationTooltips();
            
            // Setup panel management
            this.setupPanelManagement();
            
            // Optimize scrolling
            this.optimizeScrolling();
            
            // Setup keyboard navigation
            this.setupKeyboardNavigation();
            
            // Performance monitoring
            if (this.config.performanceMode === 'high') {
                this.enablePerformanceMonitoring();
            }
        }

        disableEnhancements() {
            // Remove enhanced class
            document.body.classList.remove('enhanced-landscape-active');
            
            // Hide tooltips
            this.hideAllTooltips();
            
            // Cleanup observers
            this.cleanupObservers();
            
            // Reset panels
            this.resetPanels();
        }

        setupTouchTargetEnhancement() {
            // Find all interactive elements and ensure they meet touch requirements
            const selectors = [
                'button', '.btn', 'a', 'input[type="button"]', 'input[type="submit"]',
                '.touch-target', '.nav-item a', '.form-control', 'select',
                '.device-icon', '.tool-button', '.palette-item'
            ];
            
            const elements = document.querySelectorAll(selectors.join(', '));
            
            elements.forEach(element => {
                this.enhanceTouchTarget(element);
            });
        }

        enhanceTouchTarget(element) {
            if (this.touchTargets.has(element)) return;
            
            const rect = element.getBoundingClientRect();
            const minSize = this.config.touchTargetMinSize;
            
            // Check if element is too small
            if (rect.width < minSize || rect.height < minSize) {
                const currentPadding = window.getComputedStyle(element).padding;
                const currentMinHeight = window.getComputedStyle(element).minHeight;
                
                // Store original values for restoration
                this.touchTargets.set(element, {
                    originalPadding: currentPadding,
                    originalMinHeight: currentMinHeight,
                    enhanced: true
                });
                
                // Apply enhanced touch target styles
                element.style.minHeight = `${minSize}px`;
                element.style.minWidth = `${minSize}px`;
                
                if (!element.style.padding || element.style.padding === '0px') {
                    const paddingNeeded = Math.max(0, (minSize - rect.height) / 2);
                    element.style.padding = `${paddingNeeded}px`;
                }
                
                element.classList.add('touch-enhanced');
            }
        }

        setupNavigationTooltips() {
            const navItems = document.querySelectorAll('#sidebar .nav-links a');
            
            navItems.forEach(item => {
                const span = item.querySelector('span');
                if (span) {
                    const tooltipText = span.textContent.trim();
                    item.setAttribute('data-tooltip', tooltipText);
                    item.setAttribute('aria-label', tooltipText);
                    
                    // Add tooltip event listeners
                    item.addEventListener('mouseenter', (e) => this.showTooltip(e, tooltipText));
                    item.addEventListener('mouseleave', () => this.hideTooltip());
                    item.addEventListener('focus', (e) => this.showTooltip(e, tooltipText));
                    item.addEventListener('blur', () => this.hideTooltip());
                }
            });
        }

        showTooltip(event, text) {
            if (!this.isEnhanced) return;
            
            this.hideTooltip(); // Hide any existing tooltip
            
            this.tooltipTimeout = setTimeout(() => {
                const tooltip = document.createElement('div');
                tooltip.className = 'enhanced-tooltip';
                tooltip.textContent = text;
                tooltip.style.cssText = `
                    position: fixed;
                    background: var(--surface, #1A2B47);
                    border: 1px solid var(--cyber-glow, #00D4FF);
                    color: var(--text-primary, white);
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    white-space: nowrap;
                    z-index: 1000;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                    pointer-events: none;
                    opacity: 0;
                    transform: scale(0.8);
                    transition: opacity 0.2s ease, transform 0.2s ease;
                `;
                
                document.body.appendChild(tooltip);
                
                // Position tooltip
                const rect = event.target.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                
                let left = rect.right + 12;
                let top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                
                // Ensure tooltip stays in viewport
                if (left + tooltipRect.width > window.innerWidth) {
                    left = rect.left - tooltipRect.width - 12;
                }
                
                if (top + tooltipRect.height > window.innerHeight) {
                    top = window.innerHeight - tooltipRect.height - 12;
                }
                
                if (top < 12) {
                    top = 12;
                }
                
                tooltip.style.left = `${left}px`;
                tooltip.style.top = `${top}px`;
                
                // Animate in
                requestAnimationFrame(() => {
                    tooltip.style.opacity = '1';
                    tooltip.style.transform = 'scale(1)';
                });
                
                this.activeTooltip = tooltip;
            }, this.config.tooltipDelay);
        }

        hideTooltip() {
            if (this.tooltipTimeout) {
                clearTimeout(this.tooltipTimeout);
                this.tooltipTimeout = null;
            }
            
            if (this.activeTooltip) {
                this.activeTooltip.style.opacity = '0';
                this.activeTooltip.style.transform = 'scale(0.8)';
                
                setTimeout(() => {
                    if (this.activeTooltip && this.activeTooltip.parentNode) {
                        this.activeTooltip.parentNode.removeChild(this.activeTooltip);
                    }
                    this.activeTooltip = null;
                }, 200);
            }
        }

        hideAllTooltips() {
            this.hideTooltip();
            document.querySelectorAll('.enhanced-tooltip').forEach(tooltip => {
                tooltip.remove();
            });
        }

        setupPanelManagement() {
            // Add panel toggle buttons for landscape mode
            this.createPanelToggleButtons();
            
            // Setup panel slide animations
            this.setupPanelAnimations();
            
            // Handle panel backdrop clicks
            this.setupPanelBackdrops();
        }

        createPanelToggleButtons() {
            // Properties panel toggle
            const propertiesToggle = this.createToggleButton('properties', 'cog', 'Properties');
            
            // Terminal toggle
            const terminalToggle = this.createToggleButton('terminal', 'terminal', 'Terminal');
            
            // Performance panel toggle
            const performanceToggle = this.createToggleButton('performance', 'chart-line', 'Performance');
            
            // Add to main content
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                const toggleContainer = document.createElement('div');
                toggleContainer.className = 'landscape-panel-toggles';
                toggleContainer.style.cssText = `
                    position: fixed;
                    top: 50%;
                    right: 12px;
                    transform: translateY(-50%);
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                    z-index: 200;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                `;
                
                toggleContainer.appendChild(propertiesToggle);
                toggleContainer.appendChild(terminalToggle);
                toggleContainer.appendChild(performanceToggle);
                
                document.body.appendChild(toggleContainer);
                
                // Show in landscape mode
                window.addEventListener('landscapeModeEnabled', () => {
                    toggleContainer.style.opacity = '1';
                });
                
                window.addEventListener('landscapeModeDisabled', () => {
                    toggleContainer.style.opacity = '0';
                });
            }
        }

        createToggleButton(type, icon, label) {
            const button = document.createElement('button');
            button.className = `panel-toggle panel-toggle-${type}`;
            button.setAttribute('aria-label', `Toggle ${label}`);
            button.innerHTML = `<i class="fas fa-${icon}"></i>`;
            button.style.cssText = `
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: var(--surface, #1A2B47);
                border: 2px solid var(--cyber-glow, #00D4FF);
                color: var(--cyber-glow, #00D4FF);
                font-size: 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            `;
            
            // Hover/active states
            button.addEventListener('mouseenter', () => {
                button.style.background = 'var(--cyber-glow, #00D4FF)';
                button.style.color = 'var(--background, #0B1426)';
                button.style.transform = 'scale(1.1)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.background = 'var(--surface, #1A2B47)';
                button.style.color = 'var(--cyber-glow, #00D4FF)';
                button.style.transform = 'scale(1)';
            });
            
            // Toggle functionality
            button.addEventListener('click', () => {
                this.togglePanel(type);
            });
            
            return button;
        }

        togglePanel(type) {
            const selectors = {
                properties: '.properties-panel, .form-sidebar, .editor-sidebar',
                terminal: '#cli-terminal-container, .terminal-container',
                performance: '.performance-sidebar'
            };
            
            const panel = document.querySelector(selectors[type]);
            if (panel) {
                const isActive = panel.classList.contains('show') || panel.classList.contains('active');
                
                // Close all other panels first
                Object.values(selectors).forEach(selector => {
                    const otherPanel = document.querySelector(selector);
                    if (otherPanel && otherPanel !== panel) {
                        otherPanel.classList.remove('show', 'active');
                    }
                });
                
                // Toggle current panel
                if (isActive) {
                    panel.classList.remove('show', 'active');
                } else {
                    panel.classList.add('show', 'active');
                }
                
                // Update button state
                const button = document.querySelector(`.panel-toggle-${type}`);
                if (button) {
                    button.style.background = isActive ? 
                        'var(--surface, #1A2B47)' : 
                        'var(--cyber-glow, #00D4FF)';
                    button.style.color = isActive ? 
                        'var(--cyber-glow, #00D4FF)' : 
                        'var(--background, #0B1426)';
                }
            }
        }

        setupPanelAnimations() {
            // Add CSS for smooth panel transitions
            const style = document.createElement('style');
            style.textContent = `
                @media (orientation: landscape) and (max-width: 896px) {
                    .properties-panel,
                    .form-sidebar,
                    .editor-sidebar,
                    #cli-terminal-container,
                    .terminal-container,
                    .performance-sidebar {
                        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    }
                    
                    .landscape-panel-toggles {
                        transition: opacity 0.3s ease !important;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        setupAccessibilityEnhancements() {
            // Add skip link for landscape mode
            const skipLink = document.createElement('a');
            skipLink.href = '#main-content';
            skipLink.textContent = 'Skip to main content';
            skipLink.className = 'skip-to-content';
            skipLink.style.cssText = `
                position: fixed;
                top: -40px;
                left: 6px;
                background: var(--surface, #1A2B47);
                color: var(--text-primary, white);
                padding: 8px 16px;
                border-radius: 6px;
                text-decoration: none;
                border: 2px solid var(--cyber-glow, #00D4FF);
                z-index: 9999;
                transition: top 0.3s;
            `;
            
            skipLink.addEventListener('focus', () => {
                skipLink.style.top = '6px';
            });
            
            skipLink.addEventListener('blur', () => {
                skipLink.style.top = '-40px';
            });
            
            document.body.insertBefore(skipLink, document.body.firstChild);
            
            // Add main content landmark
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.setAttribute('role', 'main');
                mainContent.setAttribute('id', 'main-content');
            }
            
            // Enhance focus management
            this.setupFocusManagement();
        }

        setupFocusManagement() {
            // Trap focus in panels when open
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    // Close open panels on Escape
                    document.querySelectorAll('.properties-panel.show, .terminal-container.show, .performance-sidebar.show')
                        .forEach(panel => {
                            panel.classList.remove('show', 'active');
                        });
                }
            });
        }

        setupKeyboardNavigation() {
            // Add keyboard shortcuts for landscape mode
            document.addEventListener('keydown', (e) => {
                if (!this.isEnhanced) return;
                
                // Ctrl/Cmd + number keys for panel toggles
                if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey) {
                    switch(e.key) {
                        case '1':
                            e.preventDefault();
                            this.togglePanel('properties');
                            break;
                        case '2':
                            e.preventDefault();
                            this.togglePanel('terminal');
                            break;
                        case '3':
                            e.preventDefault();
                            this.togglePanel('performance');
                            break;
                    }
                }
            });
        }

        optimizeForPage(pageType) {
            console.log(`[Enhanced Landscape] Optimizing for page: ${pageType}`);
            
            switch(pageType) {
                case 'dynamic-simulation':
                    this.optimizeDynamicSimulation();
                    break;
                case 'crimping-simulation':
                    this.optimizeCrimpingSimulation();
                    break;
                case 'troubleshooting':
                    this.optimizeTroubleshooting();
                    break;
                case 'admin-simulation-edit':
                    this.optimizeAdminEditor();
                    break;
            }
        }

        optimizeDynamicSimulation() {
            // Enhance device palette interaction
            const palette = document.querySelector('.device-palette, #device-palette');
            if (palette) {
                palette.style.cssText += `
                    scrollbar-width: thin;
                    scrollbar-color: var(--cyber-glow) transparent;
                `;
            }
            
            // Optimize canvas touch handling
            const canvas = document.querySelector('.simulation-canvas, #topology-canvas');
            if (canvas) {
                canvas.style.touchAction = 'pan-zoom';
            }
        }

        optimizeCrimpingSimulation() {
            // Enhance wire slot touch targets
            const wireSlots = document.querySelectorAll('.wire-slot');
            wireSlots.forEach(slot => {
                this.enhanceTouchTarget(slot);
            });
            
            // Add haptic feedback for compatible devices
            if ('vibrate' in navigator) {
                wireSlots.forEach(slot => {
                    slot.addEventListener('touchstart', () => {
                        navigator.vibrate(10); // Short vibration
                    });
                });
            }
        }

        optimizeTroubleshooting() {
            // Enhance network diagram interaction
            const diagram = document.querySelector('.network-diagram-area');
            if (diagram) {
                diagram.style.touchAction = 'pan-zoom pinch-zoom';
            }
            
            // Optimize troubleshoot panel scrolling
            const panel = document.querySelector('.troubleshoot-panel');
            if (panel) {
                panel.style.webkitOverflowScrolling = 'touch';
            }
        }

        optimizeAdminEditor() {
            // Enhance editor canvas
            const canvas = document.querySelector('.topology-editor, .canvas-container');
            if (canvas) {
                canvas.style.touchAction = 'manipulation';
            }
            
            // Add double-tap to zoom
            let lastTap = 0;
            canvas?.addEventListener('touchend', (e) => {
                const currentTime = new Date().getTime();
                const tapLength = currentTime - lastTap;
                
                if (tapLength < 500 && tapLength > 0) {
                    // Double tap detected
                    e.preventDefault();
                    this.handleDoubleTapZoom(e);
                }
                
                lastTap = currentTime;
            });
        }

        handleDoubleTapZoom(e) {
            // Simple zoom implementation
            const target = e.currentTarget;
            const currentScale = target.style.transform.match(/scale\(([^)]+)\)/);
            const scale = currentScale ? parseFloat(currentScale[1]) : 1;
            const newScale = scale >= 1.5 ? 1 : 1.5;
            
            target.style.transform = `scale(${newScale})`;
            target.style.transformOrigin = 'center center';
            target.style.transition = 'transform 0.3s ease';
        }

        setupPerformanceOptimizations() {
            // Optimize based on device capabilities
            if (this.config.performanceMode === 'low') {
                // Reduce animations for low-end devices
                document.documentElement.style.setProperty('--landscape-transition-fast', '0.1s');
                document.documentElement.style.setProperty('--landscape-transition-medium', '0.2s');
                document.documentElement.style.setProperty('--landscape-transition-slow', '0.3s');
            }
            
            // Setup intersection observer for efficient rendering
            if ('IntersectionObserver' in window) {
                this.intersectionObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('visible');
                        } else {
                            entry.target.classList.remove('visible');
                        }
                    });
                }, { threshold: 0.1 });
            }
        }

        enablePerformanceMonitoring() {
            // Monitor frame rate and performance
            let frameCount = 0;
            let lastTime = performance.now();
            
            const monitor = () => {
                frameCount++;
                const currentTime = performance.now();
                
                if (currentTime - lastTime >= 1000) {
                    const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                    
                    if (fps < 30 && this.config.performanceMode !== 'low') {
                        console.warn('[Enhanced Landscape] Low FPS detected, reducing animations');
                        this.config.performanceMode = 'low';
                        this.setupPerformanceOptimizations();
                    }
                    
                    frameCount = 0;
                    lastTime = currentTime;
                }
                
                if (this.isEnhanced) {
                    requestAnimationFrame(monitor);
                }
            };
            
            requestAnimationFrame(monitor);
        }

        monitorTouchTargets() {
            // Use ResizeObserver to monitor touch target changes
            if ('ResizeObserver' in window) {
                this.resizeObserver = new ResizeObserver((entries) => {
                    entries.forEach(entry => {
                        this.enhanceTouchTarget(entry.target);
                    });
                });
                
                // Observe interactive elements
                document.querySelectorAll('button, .btn, a, input, .touch-target')
                    .forEach(element => {
                        this.resizeObserver.observe(element);
                    });
            }
        }

        optimizeScrolling() {
            // Apply smooth scrolling optimizations
            const scrollElements = document.querySelectorAll(
                '.device-palette, .properties-panel, .troubleshoot-panel, .main-content'
            );
            
            scrollElements.forEach(element => {
                element.style.scrollBehavior = 'smooth';
                element.style.webkitOverflowScrolling = 'touch';
            });
        }

        setupOrientationHandling() {
            // Enhanced orientation change handling
            let orientationTimeout;
            
            const handleOrientationChange = () => {
                clearTimeout(orientationTimeout);
                orientationTimeout = setTimeout(() => {
                    // Force layout recalculation
                    document.body.style.height = '100vh';
                    requestAnimationFrame(() => {
                        document.body.style.height = '';
                        this.recalculateLayout();
                    });
                }, 300);
            };
            
            window.addEventListener('orientationchange', handleOrientationChange);
            window.addEventListener('resize', handleOrientationChange);
            
            // Screen orientation API support
            if (screen.orientation) {
                screen.orientation.addEventListener('change', handleOrientationChange);
            }
        }

        recalculateLayout() {
            // Recalculate touch targets
            this.touchTargets.forEach((data, element) => {
                this.enhanceTouchTarget(element);
            });
            
            // Update panel positions
            document.querySelectorAll('.properties-panel, .terminal-container, .performance-sidebar')
                .forEach(panel => {
                    if (panel.classList.contains('show')) {
                        panel.style.transform = 'translateX(0)';
                    }
                });
            
            // Trigger custom event
            window.dispatchEvent(new CustomEvent('enhancedLandscapeLayoutRecalculated'));
        }

        cleanupObservers() {
            if (this.resizeObserver) {
                this.resizeObserver.disconnect();
                this.resizeObserver = null;
            }
            
            if (this.intersectionObserver) {
                this.intersectionObserver.disconnect();
                this.intersectionObserver = null;
            }
        }

        resetPanels() {
            // Close all panels
            document.querySelectorAll('.properties-panel, .terminal-container, .performance-sidebar')
                .forEach(panel => {
                    panel.classList.remove('show', 'active');
                });
            
            // Reset toggle buttons
            document.querySelectorAll('.panel-toggle')
                .forEach(button => {
                    button.style.background = 'var(--surface, #1A2B47)';
                    button.style.color = 'var(--cyber-glow, #00D4FF)';
                });
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.enhancedLandscapeOptimizer = new EnhancedLandscapeOptimizer();
        });
    } else {
        window.enhancedLandscapeOptimizer = new EnhancedLandscapeOptimizer();
    }

    // Export for external use
    window.EnhancedLandscapeOptimizer = EnhancedLandscapeOptimizer;

})();
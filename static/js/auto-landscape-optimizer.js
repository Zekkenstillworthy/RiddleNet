/**
 * RiddleNet Auto-Landscape Optimizer
 * Automatically optimizes page layouts when mobile devices switch to landscape orientation
 * Supports dynamic simulation, admin simulation editor, crimping simulation, and troubleshooting pages
 */

(function() {
    'use strict';

    const AUTO_LANDSCAPE_CONFIG = {
        // Detection settings
        mobileMaxWidth: 896,
        transitionDelay: 100,
        resizeDelay: 300,
        
        // Page-specific configurations
        pages: {
            'dynamic-simulation': {
                selectors: {
                    wrapper: '.simulation-wrapper, .main-content',
                    canvas: '#topology-canvas, .simulation-canvas, .network-topology-canvas',
                    palette: '.device-palette-container, .device-palette, #device-palette',
                    controls: '.controls-sidebar, .properties-panel',
                    terminal: '#cli-terminal-container',
                    header: '.simulation-header, .page-header'
                },
                classes: {
                    landscape: 'landscape-mode',
                    bodyClass: 'simulation-landscape-mode'
                }
            },
            'admin-simulation-edit': {
                selectors: {
                    wrapper: '.admin-editor-container, .main-content',
                    canvas: '.canvas-container, .topology-editor, .network-topology-canvas',
                    palette: '.device-palette, .tools-panel, .editing-tools',
                    properties: '.properties-panel, .form-sidebar, .editor-sidebar',
                    navbar: '.admin-top-navbar, .top-navbar'
                },
                classes: {
                    landscape: 'admin-landscape-mode',
                    bodyClass: 'admin-editor-landscape'
                }
            },
            'crimping-simulation': {
                selectors: {
                    wrapper: '.container',
                    simulation: '.simulation-area, .crimping-area',
                    controls: '.tools-panel, .controls-panel',
                    header: '.header-nav, .back-button'
                },
                classes: {
                    landscape: 'crimping-landscape-mode',
                    bodyClass: 'crimping-simulation-landscape'
                }
            },
            'troubleshooting': {
                selectors: {
                    wrapper: '.troubleshoot-container',
                    diagram: '.network-diagram-area',
                    panel: '.troubleshoot-panel',
                    palette: '.device-palette',
                    performance: '.performance-sidebar'
                },
                classes: {
                    landscape: 'troubleshoot-landscape-mode',
                    bodyClass: 'troubleshooting-landscape'
                }
            }
        }
    };

    class AutoLandscapeOptimizer {
        constructor() {
            this.currentPage = this.detectPageType();
            this.isLandscapeMode = false;
            this.isMobile = this.checkIfMobile();
            this.mediaQuery = window.matchMedia(`(max-width: ${AUTO_LANDSCAPE_CONFIG.mobileMaxWidth}px) and (orientation: landscape)`);
            this.orientationTimeout = null;
            
            this.init();
        }

        detectPageType() {
            const url = window.location.pathname;
            
            // Enhanced URL detection based on actual routes
            if (url.includes('/dynamic/simulation/') || url.includes('/simulation/')) {
                return 'dynamic-simulation';
            }
            if (url.includes('/admin/simulation/edit/') || (url.includes('/admin/') && url.includes('edit'))) {
                return 'admin-simulation-edit';
            }
            if (url.includes('/crimping-simulation') || url.includes('/crimping')) {
                return 'crimping-simulation';
            }
            if (url.includes('/troubleshooting') || url.includes('/troubleshoot')) {
                return 'troubleshooting';
            }
            
            // Enhanced fallback: detect by page elements from screenshots
            if (document.querySelector('.simulation-wrapper, #topology-canvas, .network-topology-canvas')) {
                return 'dynamic-simulation';
            }
            if (document.querySelector('.admin-top-navbar, .canvas-container, .editing-tools, .editor-container')) {
                return 'admin-simulation-edit';
            }
            if (document.querySelector('.crimping-area, .wire-slots, .container .cable-sections')) {
                return 'crimping-simulation';
            }
            if (document.querySelector('.troubleshoot-container, .network-diagram-area, .editing-tools')) {
                return 'troubleshooting';
            }

            return null;
        }

        checkIfMobile() {
            // Enhanced mobile detection with comprehensive checks
            const userAgent = navigator.userAgent;
            
            // Check for mobile user agents
            const isMobileUA = /Mobi|Android|iPhone|iPad|iPod|Mobile|BlackBerry|IEMobile|Opera Mini|webOS|Windows Phone/i.test(userAgent);
            
            // Screen size checks
            const isSmallScreen = window.innerWidth <= AUTO_LANDSCAPE_CONFIG.mobileMaxWidth;
            const isShortScreen = window.innerHeight <= 600;
            
            // Touch device detection
            const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0);
            
            // Device pixel ratio check (high DPI mobile screens)
            const isHighDPI = window.devicePixelRatio > 1.5;
            
            // Specific device checks
            const isTablet = /(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(userAgent);
            const isPhone = /phone|mobile/i.test(userAgent) && !isTablet;
            
            // Viewport meta tag presence (common on mobile-optimized sites)
            const hasViewportMeta = document.querySelector('meta[name="viewport"]');
            
            // Combine all checks for comprehensive mobile detection
            const isMobileDevice = isMobileUA || isPhone || isTablet;
            const isMobileEnvironment = (isSmallScreen && isTouchDevice) || (isShortScreen && isTouchDevice);
            const isMobileContext = hasViewportMeta && (isHighDPI || isTouchDevice);
            
            return isMobileDevice || isMobileEnvironment || isMobileContext;
        }

        init() {
            if (!this.isMobile || !this.currentPage) {
                return;
            }

            console.log(`[AutoLandscape] Initialized for page: ${this.currentPage}`);

            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setupListeners());
            } else {
                this.setupListeners();
            }
        }

        setupListeners() {
            // Initial check
            setTimeout(() => this.handleOrientationChange(), AUTO_LANDSCAPE_CONFIG.transitionDelay);

            // Orientation change listeners
            window.addEventListener('orientationchange', () => {
                setTimeout(() => this.handleOrientationChange(), AUTO_LANDSCAPE_CONFIG.transitionDelay);
            });

            window.addEventListener('resize', () => {
                setTimeout(() => this.handleOrientationChange(), AUTO_LANDSCAPE_CONFIG.resizeDelay);
            });

            // Media query listener
            this.mediaQuery.addEventListener('change', (e) => {
                if (e.matches) {
                    this.enableLandscapeMode();
                } else {
                    this.disableLandscapeMode();
                }
            });

            // Screen orientation API listener
            if (screen.orientation) {
                screen.orientation.addEventListener('change', () => {
                    setTimeout(() => this.handleOrientationChange(), AUTO_LANDSCAPE_CONFIG.transitionDelay);
                });
            }
        }

        handleOrientationChange() {
            // Clear any pending orientation change
            if (this.orientationTimeout) {
                clearTimeout(this.orientationTimeout);
            }
            
            // Debounce orientation changes to prevent rapid toggling
            this.orientationTimeout = setTimeout(() => {
                const isLandscape = this.isInLandscape();
                const isMobileSize = window.innerWidth <= AUTO_LANDSCAPE_CONFIG.mobileMaxWidth;
                
                // Additional checks for reliable detection
                const hasMinimumLandscapeWidth = window.innerWidth >= 480;
                const hasValidAspectRatio = (window.innerWidth / window.innerHeight) >= 1.2;
                
                if (isMobileSize && isLandscape && hasMinimumLandscapeWidth && hasValidAspectRatio && !this.isLandscapeMode) {
                    console.log('[AutoLandscape] Enabling landscape mode');
                    this.enableLandscapeMode();
                } else if ((!isMobileSize || !isLandscape || !hasValidAspectRatio) && this.isLandscapeMode) {
                    console.log('[AutoLandscape] Disabling landscape mode');
                    this.disableLandscapeMode();
                }
            }, AUTO_LANDSCAPE_CONFIG.transitionDelay);
        }

        isInLandscape() {
            // Multiple methods for reliable landscape detection
            let isLandscape = false;
            
            // Method 1: Media query (most reliable)
            if (window.matchMedia) {
                const landscapeQuery = window.matchMedia('(orientation: landscape)');
                if (landscapeQuery.matches) isLandscape = true;
            }
            
            // Method 2: Screen orientation API
            if (screen.orientation) {
                const angle = screen.orientation.angle;
                if (angle === 90 || angle === -90 || angle === 270) {
                    isLandscape = true;
                }
            }
            
            // Method 3: Window dimensions (fallback)
            if (!isLandscape && window.innerWidth > window.innerHeight) {
                isLandscape = true;
            }
            
            // Method 4: Screen dimensions (additional check)
            if (!isLandscape && screen.availWidth > screen.availHeight) {
                isLandscape = true;
            }
            
            return isLandscape;
        }

        enableLandscapeMode() {
            if (this.isLandscapeMode) return;

            console.log(`[AutoLandscape] Enabling landscape mode for ${this.currentPage}`);
            
            const config = AUTO_LANDSCAPE_CONFIG.pages[this.currentPage];
            if (!config) return;

            // Add transition class to prevent layout flashing
            document.body.classList.add('orientation-changing');

            // Apply body class
            document.body.classList.add('auto-landscape-active', config.classes.bodyClass);

            // Apply page-specific optimizations
            this.applyLandscapeOptimizations(config);
            
            this.isLandscapeMode = true;

            // Remove transition class after animation
            setTimeout(() => {
                document.body.classList.remove('orientation-changing');
                // Trigger resize event for components that need it
                this.triggerResize();
            }, 300);

            // Emit custom event
            window.dispatchEvent(new CustomEvent('landscapeModeEnabled', {
                detail: { page: this.currentPage }
            }));
        }

        disableLandscapeMode() {
            if (!this.isLandscapeMode) return;

            console.log(`[AutoLandscape] Disabling landscape mode for ${this.currentPage}`);
            
            const config = AUTO_LANDSCAPE_CONFIG.pages[this.currentPage];
            if (!config) return;

            // Add transition class
            document.body.classList.add('orientation-changing');

            // Remove body classes
            document.body.classList.remove('auto-landscape-active', config.classes.bodyClass);

            // Remove page-specific classes
            this.removeLandscapeOptimizations(config);
            
            this.isLandscapeMode = false;

            // Remove transition class after animation
            setTimeout(() => {
                document.body.classList.remove('orientation-changing');
                // Trigger resize event
                this.triggerResize();
            }, 300);

            // Emit custom event
            window.dispatchEvent(new CustomEvent('landscapeModeDisabled', {
                detail: { page: this.currentPage }
            }));
        }

        applyLandscapeOptimizations(config) {
            // Apply landscape class to main elements
            Object.values(config.selectors).forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    el.classList.add(config.classes.landscape);
                });
            });

            // Page-specific optimizations
            switch(this.currentPage) {
                case 'dynamic-simulation':
                    this.optimizeDynamicSimulation(config);
                    break;
                case 'admin-simulation-edit':
                    this.optimizeAdminEditor(config);
                    break;
                case 'crimping-simulation':
                    this.optimizeCrimpingSimulation(config);
                    break;
                case 'troubleshooting':
                    this.optimizeTroubleshooting(config);
                    break;
            }
        }

        removeLandscapeOptimizations(config) {
            // Remove landscape classes
            Object.values(config.selectors).forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    el.classList.remove(config.classes.landscape);
                });
            });

            // Remove page-specific classes
            const allLandscapeClasses = [
                'landscape-mode', 'landscape-palette', 'landscape-canvas', 
                'landscape-properties', 'landscape-terminal', 'admin-landscape-mode',
                'crimping-landscape-mode', 'troubleshoot-landscape-mode'
            ];
            
            document.querySelectorAll('*').forEach(el => {
                allLandscapeClasses.forEach(cls => {
                    el.classList.remove(cls);
                });
            });
        }

        optimizeDynamicSimulation(config) {
            // Optimize simulation wrapper
            const wrapper = document.querySelector(config.selectors.wrapper);
            if (wrapper) {
                wrapper.style.flexDirection = 'row';
                wrapper.style.height = '100vh';
            }

            // Optimize canvas
            const canvas = document.querySelector(config.selectors.canvas);
            if (canvas) {
                canvas.classList.add('landscape-canvas');
                canvas.style.height = '100vh';
            }

            // Optimize device palette
            const palette = document.querySelector(config.selectors.palette);
            if (palette) {
                palette.classList.add('landscape-palette');
                palette.style.maxWidth = '35vw';
                palette.style.height = '100vh';
            }

            // Hide header elements
            const headers = document.querySelectorAll('.simulation-header, .breadcrumb');
            headers.forEach(header => {
                header.style.display = 'none';
            });
        }

        optimizeAdminEditor(config) {
            // Optimize admin editor layout
            const navbar = document.querySelector(config.selectors.navbar);
            if (navbar) {
                navbar.style.height = '60px'; // Reduced height
            }

            // Optimize canvas container
            const canvas = document.querySelector(config.selectors.canvas);
            if (canvas) {
                canvas.style.height = 'calc(100vh - 60px)';
                canvas.classList.add('admin-landscape-canvas');
            }

            // Optimize properties panel
            const properties = document.querySelector(config.selectors.properties);
            if (properties) {
                properties.style.maxWidth = '30vw';
                properties.style.height = 'calc(100vh - 60px)';
                properties.classList.add('admin-landscape-properties');
            }
        }

        optimizeCrimpingSimulation(config) {
            // Set container to horizontal layout
            const container = document.querySelector(config.selectors.wrapper);
            if (container) {
                container.style.display = 'flex';
                container.style.flexDirection = 'row';
                container.style.height = '100vh';
                container.style.padding = '4px';
            }

            // Hide header elements
            const headers = document.querySelectorAll('.header-nav, .back-button');
            headers.forEach(header => {
                header.style.display = 'none';
            });

            // Optimize simulation area
            const simulation = document.querySelector(config.selectors.simulation);
            if (simulation) {
                simulation.style.flex = '2';
                simulation.style.height = '100vh';
            }

            // Optimize controls
            const controls = document.querySelector(config.selectors.controls);
            if (controls) {
                controls.style.flex = '1';
                controls.style.maxWidth = '30vw';
                controls.style.height = '100vh';
                controls.style.overflowY = 'auto';
            }
        }

        optimizeTroubleshooting(config) {
            // Set main container to horizontal layout
            const container = document.querySelector(config.selectors.wrapper);
            if (container) {
                container.style.display = 'flex';
                container.style.flexDirection = 'row';
                container.style.height = '100vh';
                container.style.padding = '0';
            }

            // Optimize network diagram
            const diagram = document.querySelector(config.selectors.diagram);
            if (diagram) {
                diagram.style.flex = '2.5';
                diagram.style.height = '100vh';
            }

            // Optimize troubleshoot panel
            const panel = document.querySelector(config.selectors.panel);
            if (panel) {
                panel.style.flex = '1';
                panel.style.height = '100vh';
                panel.style.overflowY = 'auto';
            }

            // Hide header elements
            const headers = document.querySelectorAll('.simulation-header, .breadcrumb');
            headers.forEach(header => {
                header.style.display = 'none';
            });

            // Optimize performance sidebar
            const performance = document.querySelector(config.selectors.performance);
            if (performance) {
                performance.style.width = '280px';
                performance.style.height = '100vh';
            }
        }

        triggerResize() {
            // Trigger resize for canvas and simulation components
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
                
                // Specific component resize triggers
                if (window.topologyRenderer && window.topologyRenderer.handleResize) {
                    window.topologyRenderer.handleResize();
                }

                if (window.networkSimulation && window.networkSimulation.resize) {
                    window.networkSimulation.resize();
                }

                if (window.crimpingSimulation && window.crimpingSimulation.adjustLayout) {
                    window.crimpingSimulation.adjustLayout();
                }
            }, 100);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.autoLandscapeOptimizer = new AutoLandscapeOptimizer();
        });
    } else {
        window.autoLandscapeOptimizer = new AutoLandscapeOptimizer();
    }

    // Export for manual initialization if needed
    window.AutoLandscapeOptimizer = AutoLandscapeOptimizer;

})();
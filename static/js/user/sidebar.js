/**
 * Sidebar functionality for RiddleNet user interface
 * Handles sidebar toggle, mobile menu, and navigation interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Sidebar functionality initialized');
    
    // Get sidebar elements
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mainWrapper = document.getElementById('main-wrapper');
    const navLinks = document.querySelectorAll('.nav-link');

    // Only proceed if sidebar elements exist
    if (!sidebar) {
        console.warn('Sidebar not found, skipping initialization');
        return;
    }

    // Sidebar toggle functionality
    function toggleSidebar() {
        sidebar.classList.toggle('collapsed');
        if (mainWrapper) {
            mainWrapper.classList.toggle('collapsed');
        }
        
        // Save sidebar state to localStorage
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
        
        // Add animation effect
        sidebar.style.transform = 'scale(0.98)';
        setTimeout(() => {
            sidebar.style.transform = 'scale(1)';
        }, 150);
        
        console.log('Sidebar toggled:', isCollapsed ? 'collapsed' : 'expanded');
    }

    // Mobile sidebar toggle
    function toggleMobileSidebar() {
        sidebar.classList.toggle('active');
        if (sidebarOverlay) {
            sidebarOverlay.classList.toggle('active');
        }
        document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
        
        console.log('Mobile sidebar toggled:', sidebar.classList.contains('active') ? 'open' : 'closed');
    }

    // Event listeners for sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
        console.log('Sidebar toggle button listener added');
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleMobileSidebar();
        });
        console.log('Mobile menu button listener added');
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function(e) {
            e.preventDefault();
            toggleMobileSidebar();
        });
        console.log('Sidebar overlay listener added');
    }

    // Restore sidebar state from localStorage
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true' && sidebar && mainWrapper) {
        sidebar.classList.add('collapsed');
        mainWrapper.classList.add('collapsed');
    }

    // Navigation functionality with enhanced error handling
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Handle special links (logout, external links)
            if (!href || href === '#' || href.includes('logout') || href.startsWith('http')) {
                return; // Let default behavior handle these
            }
            
            // For hash links, handle smooth scrolling
            if (href.startsWith('#')) {
                e.preventDefault();
                
                // Remove active class from all nav links
                navLinks.forEach(nav => nav.classList.remove('active'));
                
                // Add active class to clicked link
                this.classList.add('active');
                
                // Close mobile sidebar if open
                if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
                    toggleMobileSidebar();
                }
                
                // Handle section navigation
                const targetId = href.substring(1);
                const targetSection = document.getElementById(targetId);
                
                if (targetSection) {
                    targetSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
                
                console.log('Navigation to:', href);
                return;
            }
            
            // For regular page navigation, just highlight the active link
            navLinks.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            console.log('Navigating to page:', href);
        });
    });

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth > 768) {
                // Close mobile sidebar on desktop
                sidebar.classList.remove('active');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('active');
                }
                document.body.style.overflow = '';
            }
        }, 250);
    });

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Escape key to close mobile sidebar
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            toggleMobileSidebar();
        }
        
        // Ctrl+B to toggle sidebar (desktop only)
        if (e.ctrlKey && e.key === 'b' && window.innerWidth > 768) {
            e.preventDefault();
            toggleSidebar();
        }
    });

    // Set active navigation link based on current page
    function setActiveNavLink() {
        const currentPath = window.location.pathname;
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href === currentPath) {
                link.classList.add('active');
            }
        });
    }

    // Initialize active navigation
    setActiveNavLink();

    console.log('Sidebar functionality fully initialized');
});

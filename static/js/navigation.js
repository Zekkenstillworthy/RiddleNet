/**
 * Navigation helper script
 * This script fixes navigation issues with class enrollment pages and prevents
 * the main script.js from trying to use page URLs as CSS selectors
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get the current path
    const currentPath = window.location.pathname;
    
    // Safely get navbar elements
    const navbarLinks = document.querySelectorAll('.navbar a');
    
    if (navbarLinks.length === 0) {
        console.log('No navbar links found, skipping navigation highlighting');
        return;
    }
    
    // Highlight active navigation item based on current path
    navbarLinks.forEach(link => {
        if (!link) return; // Skip null elements
        
        const linkHref = link.getAttribute('href');
        
        // If this is a page link (not an anchor)
        if (linkHref && linkHref.startsWith('/')) {
            // For exact matches
            if (linkHref === currentPath) {
                link.classList.add('active');
            }
            // For partial matches (e.g. /class/1 should highlight /classes)
            else if ((currentPath.startsWith('/class/') && linkHref === '/classes') ||
                     (currentPath.startsWith(linkHref) && linkHref !== '/')) {
                link.classList.add('active');
            }
        }
    });
});

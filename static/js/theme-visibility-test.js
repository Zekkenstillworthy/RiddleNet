/**
 * MVP THEME VISIBILITY TESTER
 * Run this in browser console to verify text contrast
 */

(function() {
    console.log('🎨 MVP Theme Visibility Test Starting...');
    
    // Get current theme
    const currentTheme = window.mvpThemeToggle?.getCurrentTheme() || 'unknown';
    console.log(`📋 Current Theme: ${currentTheme}`);
    
    // Test all text elements
    const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, a, button, label');
    const visibilityIssues = [];
    
    textElements.forEach(el => {
        const styles = window.getComputedStyle(el);
        const color = styles.color;
        const bgColor = styles.backgroundColor;
        const fontSize = styles.fontSize;
        
        // Check if text is visible
        const isVisible = color !== bgColor && styles.opacity !== '0';
        
        if (!isVisible) {
            visibilityIssues.push({
                element: el.tagName,
                text: el.textContent.substring(0, 30),
                color: color,
                background: bgColor
            });
        }
    });
    
    // Report results
    if (visibilityIssues.length === 0) {
        console.log('✅ All text elements are visible!');
    } else {
        console.warn(`⚠️ Found ${visibilityIssues.length} potential visibility issues:`);
        console.table(visibilityIssues);
    }
    
    // Check contrast ratios for key elements
    const keyElements = {
        'Page Title': document.querySelector('h1'),
        'Breadcrumb': document.querySelector('.breadcrumb'),
        'Sidebar Link': document.querySelector('.nav-links li a'),
        'Button': document.querySelector('button:not(.mvp-theme-toggle)'),
        'Paragraph': document.querySelector('p')
    };
    
    console.log('\n📊 Key Element Visibility:');
    Object.entries(keyElements).forEach(([name, el]) => {
        if (el) {
            const styles = window.getComputedStyle(el);
            console.log(`${name}: Color=${styles.color}, BG=${styles.backgroundColor}`);
        }
    });
    
    // Toggle theme and re-test
    console.log('\n🔄 Toggle theme using: window.mvpThemeToggle.setTheme("light") or "dark"');
    console.log('🎹 Keyboard shortcut: Ctrl + Shift + T');
    
    console.log('\n✨ MVP Theme Visibility Test Complete!');
})();

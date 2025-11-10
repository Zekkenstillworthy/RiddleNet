/**
 * MVP THEME FORCE LIGHT MODE DEBUGGER
 * Use this to identify and fix remaining dark areas
 */

(function() {
    console.log('🔦 MVP Force Light Mode Debugger - Starting...');
    
    // Apply light theme
    if (window.mvpThemeToggle) {
        window.mvpThemeToggle.setTheme('light');
        console.log('✅ Light theme applied via mvpThemeToggle');
    }
    
    // Find all elements with dark backgrounds
    const darkElements = [];
    const allElements = document.querySelectorAll('*');
    
    allElements.forEach(el => {
        const styles = window.getComputedStyle(el);
        const bgColor = styles.backgroundColor;
        
        // Check if background is dark (rgb values < 100)
        if (bgColor.includes('rgb')) {
            const rgbMatch = bgColor.match(/\d+/g);
            if (rgbMatch && rgbMatch.length >= 3) {
                const [r, g, b] = rgbMatch.map(Number);
                if (r < 100 && g < 100 && b < 100) {
                    darkElements.push({
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        bgColor: bgColor,
                        element: el
                    });
                }
            }
        }
    });
    
    console.log(`🔍 Found ${darkElements.length} elements with dark backgrounds`);
    
    if (darkElements.length > 0) {
        console.warn('⚠️ Dark elements found in light mode:');
        console.table(darkElements.slice(0, 20)); // Show first 20
        
        // Highlight dark elements with red border
        darkElements.forEach(item => {
            item.element.style.outline = '2px solid red';
            item.element.style.outlineOffset = '-2px';
        });
        
        console.log('🎯 Dark elements highlighted with RED borders');
    } else {
        console.log('✅ No dark elements found - Light mode is working perfectly!');
    }
    
    // Force override CSS variables on root
    const root = document.documentElement;
    root.style.setProperty('--background', '#F8FAFC');
    root.style.setProperty('--surface', '#FFFFFF');
    root.style.setProperty('--surface-light', '#F1F5F9');
    root.style.setProperty('--dark-bg', '#E2E8F0');
    root.style.setProperty('--text-primary', '#0F172A');
    root.style.setProperty('--text-secondary', '#475569');
    
    console.log('🎨 CSS variables forcefully overridden');
    
    // Check if body has correct background
    const bodyBg = window.getComputedStyle(document.body).backgroundColor;
    console.log(`📋 Body background: ${bodyBg}`);
    
    // Force body background
    document.body.style.background = '#F8FAFC';
    
    // Find lesson content area and force light background
    const lessonContent = document.querySelector('.lesson-main-content, .lesson-content');
    if (lessonContent) {
        lessonContent.style.background = '#FFFFFF !important';
        lessonContent.style.color = '#0F172A !important';
        
        // Force all children to light mode
        lessonContent.querySelectorAll('*').forEach(el => {
            const styles = window.getComputedStyle(el);
            if (styles.backgroundColor.includes('rgb(')) {
                const rgbMatch = styles.backgroundColor.match(/\d+/g);
                if (rgbMatch && rgbMatch.length >= 3) {
                    const [r, g, b] = rgbMatch.map(Number);
                    if (r < 100 && g < 100 && b < 100) {
                        el.style.background = '#FFFFFF';
                        el.style.color = '#0F172A';
                    }
                }
            }
        });
        
        console.log('✅ Lesson content forced to light mode');
    }
    
    console.log('🎉 Force Light Mode Debugger Complete!');
    console.log('📝 Run this script again after page changes to reapply fixes');
    
})();

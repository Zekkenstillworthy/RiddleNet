# Dashboard Badges - Code Changes Reference

## 📍 Location: templates/user/dashboard.html

## Change 1: Added Badges Section HTML (After Stats Grid)

### Location: Line ~843 (after stats grid, before welcome card)

```html
<!-- ADDED: Achievements & Badges Section -->
<div class="modern-card" style="margin-bottom: 24px;">
  <div class="section-header" style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #ffd700, #ffed4e); border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);">
        <i class="fas fa-trophy" style="font-size: 1.5rem; color: #1a1a2e;"></i>
      </div>
      <div>
        <h2>Your Achievements</h2>
        <p>Badges earned from completing challenges</p>
      </div>
    </div>
  </div>

  <!-- Badges Display Grid -->
  <div id="badgesContainer" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px;">
    <!-- Badges will be dynamically added here -->
  </div>

  <!-- No Badges Message -->
  <div id="noBadgesMessage" style="text-align: center; padding: 40px 20px;">
    <i class="fas fa-medal" style="font-size: 3rem; color: rgba(255, 255, 255, 0.3);"></i>
    <h3>No Badges Yet</h3>
    <p>Complete challenges with high scores to earn your first badge!</p>
    <a href="{{ url_for('user.crimping_simulation') }}">
      <i class="fas fa-plug"></i> Try Cable Crimping
    </a>
  </div>
</div>
```

## Change 2: Added Badge Initialization JavaScript

### Location: Line ~2220 (in script section, before DOMContentLoaded)

```javascript
// ADDED: Initialize Badges Display
function initializeBadges() {
  const badgesContainer = document.getElementById('badgesContainer');
  const noBadgesMessage = document.getElementById('noBadgesMessage');
  const badges = [];
  
  // Get scores from backend
  const topologyScore = {{ topology_score|default(0) }};
  const crimpingScore = {{ crimping_score|default(0) }};
  const osiScore = {{ osi_score|default(0) }};
  
  console.log('🏆 Checking Badge Eligibility');
  console.log('Topology:', topologyScore, 'Crimping:', crimpingScore, 'OSI:', osiScore);
  
  // Cable Master Badge - Legendary
  if (crimpingScore === 100) {
    badges.push({
      name: 'Cable Master',
      description: 'Perfect Score in Cable Crimping!',
      image: "{{ url_for('static', filename='img/cable_master_badge.png') }}",
      category: 'crimping',
      rarity: 'legendary',
      glowColor: '#ffd700'
    });
  } else if (crimpingScore >= 75) {
    // Check hard mode from localStorage
    const crimpingProgress = localStorage.getItem('crimpingProgress');
    if (crimpingProgress) {
      try {
        const progress = JSON.parse(crimpingProgress);
        if (progress.lastMode === 'rollover' && progress.lastScore >= 75) {
          badges.push({
            name: 'Cable Master',
            description: 'Hard Mode Conquered!',
            image: "{{ url_for('static', filename='img/cable_master_badge.png') }}",
            category: 'crimping',
            rarity: 'legendary',
            glowColor: '#ffd700'
          });
        }
      } catch (e) {
        console.log('Could not parse crimping progress');
      }
    }
  }
  
  // Troubleshooting Pro Badge - Epic
  const troubleshootAchievements = localStorage.getItem('troubleshootAchievements');
  if (troubleshootAchievements) {
    try {
      const achievements = JSON.parse(troubleshootAchievements);
      if (achievements.includes('perfectionist')) {
        badges.push({
          name: 'Troubleshooting Pro',
          description: 'Zero Mistakes Achievement!',
          image: "{{ url_for('static', filename='img/troubleshooting_pro_badge.png') }}",
          category: 'troubleshoot',
          rarity: 'epic',
          glowColor: '#9333ea'
        });
      }
    } catch (e) {
      console.log('Could not parse troubleshoot achievements');
    }
  }
  
  // Network Topology Badges
  if (topologyScore >= 100) {
    badges.push({
      name: 'Network Architect',
      description: 'Master of Network Topology!',
      icon: '🏗️',
      category: 'topology',
      rarity: 'rare',
      glowColor: '#3b82f6'
    });
  } else if (topologyScore >= 75) {
    badges.push({
      name: 'Topology Builder',
      description: 'Excellent Network Design!',
      icon: '🔗',
      category: 'topology',
      rarity: 'uncommon',
      glowColor: '#10b981'
    });
  }
  
  // OSI Model Badges
  if (osiScore >= 100) {
    badges.push({
      name: 'OSI Expert',
      description: 'Perfect OSI Model Knowledge!',
      icon: '📚',
      category: 'osi',
      rarity: 'rare',
      glowColor: '#8b5cf6'
    });
  } else if (osiScore >= 75) {
    badges.push({
      name: 'Layer Master',
      description: 'Strong OSI Understanding!',
      icon: '📖',
      category: 'osi',
      rarity: 'uncommon',
      glowColor: '#6366f1'
    });
  }
  
  console.log(`✅ Found ${badges.length} earned badges`);
  
  // Display badges
  if (badges.length > 0) {
    noBadgesMessage.style.display = 'none';
    badgesContainer.innerHTML = '';
    
    badges.forEach((badge, index) => {
      const badgeCard = document.createElement('div');
      badgeCard.className = 'badge-card';
      badgeCard.style.cssText = `
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 2px solid ${badge.glowColor}40;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        opacity: 0;
        transform: translateY(20px);
      `;
      
      badgeCard.innerHTML = `
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle, ${badge.glowColor}20 0%, transparent 70%);"></div>
        <div style="position: relative; z-index: 1;">
          ${badge.image ? 
            `<img src="${badge.image}" alt="${badge.name}" style="width: 80px; height: 80px; object-fit: contain; margin-bottom: 12px; filter: drop-shadow(0 0 10px ${badge.glowColor}80);">` :
            `<div style="font-size: 3.5rem; margin-bottom: 12px;">${badge.icon}</div>`
          }
          <h3 style="font-size: 1.1rem; font-weight: 700;">${badge.name}</h3>
          <p style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">${badge.description}</p>
          <div style="background: ${badge.glowColor}20; border: 1px solid ${badge.glowColor}60; border-radius: 20px; padding: 4px 12px; font-size: 0.75rem; color: ${badge.glowColor}; text-transform: uppercase;">
            ${badge.rarity}
          </div>
        </div>
      `;
      
      // Hover effects
      badgeCard.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-8px) scale(1.02)';
        this.style.boxShadow = `0 12px 40px ${badge.glowColor}40`;
      });
      
      badgeCard.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
        this.style.boxShadow = 'none';
      });
      
      badgesContainer.appendChild(badgeCard);
      
      // Staggered animation
      setTimeout(() => {
        badgeCard.style.transition = 'all 0.6s ease-out';
        badgeCard.style.opacity = '1';
        badgeCard.style.transform = 'translateY(0)';
      }, 100 + (index * 100));
    });
  } else {
    noBadgesMessage.style.display = 'block';
    badgesContainer.innerHTML = '';
  }
}
```

## Change 3: Modified DOMContentLoaded Event

### Location: Line ~2397 (in existing DOMContentLoaded event)

```javascript
// MODIFIED: Added initializeBadges() call
window.addEventListener('DOMContentLoaded', function() {
  // ADDED: Initialize badges
  initializeBadges();
  
  // Existing welcome card code
  const welcomeCard = document.getElementById('welcomeCard');
  const isDismissed = localStorage.getItem('welcomeDismissed');
  
  if (isDismissed === 'true' && welcomeCard) {
    welcomeCard.style.display = 'none';
  } else if (welcomeCard) {
    welcomeCard.style.opacity = '0';
    welcomeCard.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      welcomeCard.style.transition = 'all 0.6s ease-out';
      welcomeCard.style.opacity = '1';
      welcomeCard.style.transform = 'translateY(0)';
    }, 300);
  }
});
```

## 📊 Summary of Changes

### Files Modified: 1
- `templates/user/dashboard.html`

### Lines Added: ~200 lines
- HTML Section: ~50 lines
- JavaScript Function: ~150 lines

### No Backend Changes Required
All logic uses existing:
- `{{ topology_score }}` - Already passed to template
- `{{ crimping_score }}` - Already passed to template  
- `{{ osi_score }}` - Already passed to template
- `localStorage` - Client-side storage

## 🎨 Visual Structure

```
Dashboard Page
│
├── Header/Nav (existing)
│
├── Stats Grid (existing)
│   ├── Topology Score
│   ├── Crimping Score
│   └── OSI Score
│
├── 🆕 Achievements Section ← NEW!
│   ├── Section Header
│   │   ├── Trophy Icon
│   │   └── "Your Achievements" Title
│   │
│   ├── Badges Container (Grid)
│   │   ├── Badge Card 1
│   │   ├── Badge Card 2
│   │   └── Badge Card N...
│   │
│   └── No Badges Message (if empty)
│
├── Welcome Card (existing)
├── Announcements (existing)
└── Leaderboards (existing)
```

## 🔧 Badge Card Components

Each badge card dynamically includes:

```
┌─────────────────────┐
│  [Glow Overlay]     │
│  ┌───────────────┐  │
│  │   📸 Image    │  │ ← Badge image or icon
│  │   or Icon     │  │
│  └───────────────┘  │
│                     │
│   Badge Name        │ ← Title (h3)
│   Description       │ ← Subtitle (p)
│                     │
│  ┌───────────────┐  │
│  │   LEGENDARY   │  │ ← Rarity tag
│  └───────────────┘  │
└─────────────────────┘
```

## 🎯 Data Flow

```
Backend (Flask)
    ↓ (Jinja2 Variables)
topology_score, crimping_score, osi_score
    ↓
Dashboard Template
    ↓
JavaScript initializeBadges()
    ↓
Evaluate Badge Requirements
    ↓
Create Badge Elements
    ↓
Display in badgesContainer
```

## 🧪 Testing Hooks

### Console Logs Added
```javascript
console.log('🏆 Checking Badge Eligibility');
console.log('Topology:', topologyScore, 'Crimping:', crimpingScore);
console.log(`✅ Found ${badges.length} earned badges`);
```

### DOM Elements to Inspect
- `#badgesContainer` - Main grid container
- `#noBadgesMessage` - Empty state message
- `.badge-card` - Individual badge elements

### localStorage Keys Used
- `crimpingProgress` - Crimping game data
- `troubleshootAchievements` - Troubleshoot achievements

---

**Note**: All changes are in the frontend only. No database migrations or backend modifications required!

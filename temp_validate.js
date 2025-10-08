
        (function() {
            'use strict';
            
            class NetworkLevelSystem {
                constructor() {
                    this.currentLevel = 1;
                    this.currentXP = 0;
                    this.levelData = this.initializeLevelData();
                    this.skills = this.initializeSkills();
                    this.challenges = this.initializeChallenges();
                    this.achievements = new Set();
                    this.completedChallenges = new Set();
                    this.sessionStart = Date.now();
                    
                    this.init();
                }

            initializeLevelData() {
                return {
                    1: { title: "Networking Novice", xpRequired: 100, rewards: ["Basic Tools", "Help System"] },
                    2: { title: "Junior Technician", xpRequired: 250, rewards: ["Protocol Analyzer", "Advanced Routing"] },
                    3: { title: "Network Engineer", xpRequired: 500, rewards: ["VLAN Tools", "Security Features"] },
                    4: { title: "Senior Engineer", xpRequired: 1000, rewards: ["OSPF Configuration", "QoS Tools"] },
                    5: { title: "Network Architect", xpRequired: 2000, rewards: ["Network Design", "Performance Optimization"] },
                    6: { title: "Master Engineer", xpRequired: 3500, rewards: ["Advanced Troubleshooting", "Automation Tools"] },
                    7: { title: "Network Guru", xpRequired: 5000, rewards: ["Expert Mode", "All Protocols"] }
                };
            }

            initializeSkills() {
                return {
                    routing: {
                        name: "Routing Protocols",
                        icon: "bx-git-merge",
                        skills: {
                            "basic-routing": { name: "Basic Routing", unlocked: true, progress: 100, level: 1 },
                            "rip-protocol": { name: "RIP Protocol", unlocked: false, progress: 0, level: 2 },
                            "ospf-protocol": { name: "OSPF", unlocked: false, progress: 0, level: 4 }
                        }
                    },
                    switching: {
                        name: "Switching & VLANs",
                        icon: "bx-shuffle",
                        skills: {
                            "basic-switching": { name: "Layer 2 Switching", unlocked: true, progress: 80, level: 1 },
                            "vlan-config": { name: "VLAN Config", unlocked: false, progress: 0, level: 3 }
                        }
                    },
                    troubleshooting: {
                        name: "Troubleshooting",
                        icon: "bx-wrench",
                        skills: {
                            "connectivity-troubleshooting": { name: "Connectivity", unlocked: true, progress: 60, level: 1 },
                            "protocol-analysis": { name: "Protocol Analysis", unlocked: false, progress: 0, level: 3 }
                        }
                    }
                };
            }

            initializeChallenges() {
                return [
                    {
                        id: "basic-connectivity",
                        title: "Basic Network Connectivity",
                        level: 1,
                        difficulty: 1,
                        xp: 50,
                        description: "Create a simple network with 2 PCs and 1 switch. Configure IP addresses and test connectivity.",
                        requirements: ["Place 2 PCs", "Place 1 Switch", "Connect devices", "Configure IPs"],
                        unlocked: true,
                        badge: "ðŸŒ"
                    },
                    {
                        id: "router-setup",
                        title: "First Router Configuration",
                        level: 1,
                        difficulty: 2,
                        xp: 75,
                        description: "Set up a router with basic configuration. Configure interfaces and establish routing.",
                        requirements: ["Place router", "Configure interfaces", "Set up routing table"],
                        unlocked: true,
                        badge: "ðŸ”„"
                    },
                    {
                        id: "rip-protocol",
                        title: "RIP Protocol Configuration",
                        level: 2,
                        difficulty: 2,
                        xp: 100,
                        description: "Configure RIP v1 and v2 on multiple routers. Troubleshoot routing issues.",
                        requirements: ["Multiple routers", "RIP configuration", "Network convergence"],
                        unlocked: false,
                        badge: "ðŸ”"
                    },
                    {
                        id: "vlan-basics",
                        title: "VLAN Segmentation",
                        level: 2,
                        difficulty: 2,
                        xp: 120,
                        description: "Create and configure VLANs on switches. Set up trunk ports.",
                        requirements: ["VLAN creation", "Trunk configuration", "Inter-VLAN routing"],
                        unlocked: false,
                        badge: "ðŸ”€"
                    },
                    {
                        id: "ospf-config",
                        title: "OSPF Implementation",
                        level: 3,
                        difficulty: 3,
                        xp: 200,
                        description: "Configure OSPF areas and analyze LSA databases for enterprise networks.",
                        requirements: ["OSPF areas", "LSA analysis", "Network optimization"],
                        unlocked: false,
                        badge: "ðŸ—ï¸"
                    },
                    {
                        id: "network-troubleshooting",
                        title: "Advanced Troubleshooting",
                        level: 3,
                        difficulty: 3,
                        xp: 250,
                        description: "Diagnose complex network issues including routing loops and protocol misconfigurations.",
                        requirements: ["Problem diagnosis", "Root cause analysis", "Solution implementation"],
                        unlocked: false,
                        badge: "ðŸ”§"
                    }
                ];
            }

            init() {
                this.loadProgress();
                this.updateUI();
                this.bindEvents();
                console.log('ðŸŽ® Network Level System initialized');
            }

            loadProgress() {
                const savedData = localStorage.getItem('networkLevelProgress');
                if (savedData) {
                    const data = JSON.parse(savedData);
                    this.currentLevel = data.level || 1;
                    this.currentXP = data.xp || 0;
                    this.achievements = new Set(data.achievements || []);
                    this.completedChallenges = new Set(data.completedChallenges || []);
                    
                    // Update skills progress
                    if (data.skills) {
                        Object.keys(data.skills).forEach(category => {
                            if (this.skills[category]) {
                                Object.keys(data.skills[category]).forEach(skillId => {
                                    if (this.skills[category].skills[skillId]) {
                                        Object.assign(this.skills[category].skills[skillId], data.skills[category][skillId]);
                                    }
                                });
                            }
                        });
                    }
                }
            }

            saveProgress() {
                const data = {
                    level: this.currentLevel,
                    xp: this.currentXP,
                    achievements: Array.from(this.achievements),
                    completedChallenges: Array.from(this.completedChallenges),
                    skills: this.skills,
                    lastSaved: Date.now()
                };
                localStorage.setItem('networkLevelProgress', JSON.stringify(data));
            }

            awardXP(amount, reason = '') {
                const oldLevel = this.currentLevel;
                this.currentXP += amount;
                
                // Check for level up
                while (this.shouldLevelUp()) {
                    this.levelUp();
                }
                
                this.updateUI();
                this.saveProgress();
                
                // Show XP notification
                this.showXPNotification(amount, reason);
                
                console.log(`ðŸŒŸ Awarded ${amount} XP: ${reason}`);
            }

            shouldLevelUp() {
                const nextLevel = this.currentLevel + 1;
                const nextLevelData = this.levelData[nextLevel];
                return nextLevelData && this.currentXP >= nextLevelData.xpRequired;
            }

            levelUp() {
                this.currentLevel++;
                const levelInfo = this.levelData[this.currentLevel];
                
                // Unlock new skills and challenges
                this.unlockContentForLevel(this.currentLevel);
                
                // Show level up notification
                this.showLevelUpNotification(levelInfo);
                
                // Award achievement
                this.unlockAchievement(`level_${this.currentLevel}`);
                
                console.log(`ðŸŽ‰ Level up! Now level ${this.currentLevel}: ${levelInfo.title}`);
            }

            unlockContentForLevel(level) {
                // Unlock skills
                Object.values(this.skills).forEach(category => {
                    Object.values(category.skills).forEach(skill => {
                        if (skill.level <= level) {
                            skill.unlocked = true;
                        }
                    });
                });
                
                // Unlock challenges
                this.challenges.forEach(challenge => {
                    if (challenge.level <= level) {
                        challenge.unlocked = true;
                    }
                });
            }

            completeChallenge(challengeId) {
                const challenge = this.challenges.find(c => c.id === challengeId);
                if (!challenge || this.completedChallenges.has(challengeId)) {
                    return false;
                }
                
                this.completedChallenges.add(challengeId);
                this.awardXP(challenge.xp, `Completed: ${challenge.title}`);
                
                // Update related skills
                this.updateSkillsFromChallenge(challenge);
                
                // Show completion notification
                this.showChallengeCompletionNotification(challenge);
                
                return true;
            }

            updateSkillsFromChallenge(challenge) {
                // Map challenges to skills and award progress
                const skillMappings = {
                    "basic-connectivity": ["connectivity-troubleshooting", "basic-switching"],
                    "router-setup": ["basic-routing"],
                    "rip-protocol": ["rip-protocol"],
                    "vlan-basics": ["vlan-config"],
                    "ospf-config": ["ospf-protocol"],
                    "network-troubleshooting": ["protocol-analysis"]
                };
                
                const skillsToUpdate = skillMappings[challenge.id] || [];
                skillsToUpdate.forEach(skillId => {
                    this.updateSkillProgress(skillId, 25);
                });
            }

            updateSkillProgress(skillId, progress) {
                // Find the skill across all categories
                let targetSkill = null;
                let categoryKey = null;
                
                Object.keys(this.skills).forEach(category => {
                    Object.keys(this.skills[category].skills).forEach(skill => {
                        if (skill === skillId) {
                            targetSkill = this.skills[category].skills[skill];
                            categoryKey = category;
                        }
                    });
                });
                
                if (targetSkill && targetSkill.unlocked) {
                    targetSkill.progress = Math.min(100, targetSkill.progress + progress);
                    
                    // If skill mastered, award bonus XP
                    if (targetSkill.progress >= 100 && targetSkill.progress - progress < 100) {
                        this.awardXP(25, `Mastered: ${targetSkill.name}`);
                        this.unlockAchievement(`skill_${skillId}_mastered`);
                    }
                }
            }

            unlockAchievement(achievementId) {
                if (this.achievements.has(achievementId)) {
                    return false;
                }
                
                this.achievements.add(achievementId);
                this.showAchievementNotification(achievementId);
                return true;
            }

            trackAction(actionType, data = {}) {
                // Award XP based on action type
                const xpValues = {
                    'device_placed': 5,
                    'connection_made': 8,
                    'device_configured': 15,
                    'problem_solved': 30,
                    'scenario_completed': 50,
                    'perfect_score': 100,
                    'speed_bonus': 20
                };
                
                const xp = xpValues[actionType] || 0;
                if (xp > 0) {
                    this.awardXP(xp, this.getActionDescription(actionType));
                }
                
                // Check for specific achievements
                this.checkActionAchievements(actionType, data);
            }

            getActionDescription(actionType) {
                const descriptions = {
                    'device_placed': 'Device Placement',
                    'connection_made': 'Network Connection',
                    'device_configured': 'Device Configuration',
                    'problem_solved': 'Problem Solved',
                    'scenario_completed': 'Scenario Completed',
                    'perfect_score': 'Perfect Score!',
                    'speed_bonus': 'Speed Bonus'
                };
                return descriptions[actionType] || 'Network Action';
            }

            checkActionAchievements(actionType, data) {
                // Achievement logic based on actions
                if (actionType === 'device_placed' && !this.achievements.has('first_device')) {
                    this.unlockAchievement('first_device');
                }
                
                if (actionType === 'scenario_completed' && data.time < 300 && !this.achievements.has('speed_demon')) {
                    this.unlockAchievement('speed_demon');
                }
                
                if (actionType === 'perfect_score' && !this.achievements.has('perfectionist')) {
                    this.unlockAchievement('perfectionist');
                }
            }

            updateUI() {
                this.updateLevelProgress();
                this.updateSkillTrees();
                this.updateChallenges();
            }

            updateLevelProgress() {
                const levelElement = document.getElementById('current-level');
                const xpElement = document.getElementById('current-xp');
                const nextXpElement = document.getElementById('next-level-xp');
                const titleElement = document.getElementById('level-title');
                const previewElement = document.getElementById('next-level-preview');
                const progressFill = document.getElementById('level-progress-fill');
                
                const currentLevelData = this.levelData[this.currentLevel];
                const nextLevelData = this.levelData[this.currentLevel + 1];
                
                if (levelElement) levelElement.textContent = `Level ${this.currentLevel}`;
                if (xpElement) xpElement.textContent = this.currentXP;
                if (titleElement) titleElement.textContent = currentLevelData?.title || 'Network Engineer';
                
                if (nextLevelData) {
                    if (nextXpElement) nextXpElement.textContent = nextLevelData.xpRequired;
                    if (previewElement) previewElement.textContent = `Next: ${nextLevelData.title}`;
                    
                    if (progressFill) {
                        const currentLevelXP = this.currentLevel > 1 ? this.levelData[this.currentLevel].xpRequired : 0;
                        const progress = ((this.currentXP - currentLevelXP) / (nextLevelData.xpRequired - currentLevelXP)) * 100;
                        progressFill.style.width = `${Math.max(0, Math.min(100, progress))}%`;
                    }
                } else {
                    if (nextXpElement) nextXpElement.textContent = 'MAX';
                    if (previewElement) previewElement.textContent = 'Max Level Reached!';
                    if (progressFill) progressFill.style.width = '100%';
                }
            }

            updateSkillTrees() {
                Object.keys(this.skills).forEach(categoryKey => {
                    const category = this.skills[categoryKey];
                    Object.keys(category.skills).forEach(skillId => {
                        const skill = category.skills[skillId];
                        const skillElement = document.querySelector(`[data-skill="${skillId}"]`);
                        
                        if (skillElement) {
                            skillElement.classList.remove('locked', 'unlocked', 'mastered');
                            
                            if (!skill.unlocked) {
                                skillElement.classList.add('locked');
                            } else if (skill.progress >= 100) {
                                skillElement.classList.add('mastered');
                            } else {
                                skillElement.classList.add('unlocked');
                            }
                            
                            const progressBar = skillElement.querySelector('.skill-progress-fill');
                            if (progressBar) {
                                progressBar.style.width = `${skill.progress}%`;
                            }
                        }
                    });
                });
            }

            updateChallenges() {
                this.challenges.forEach(challenge => {
                    const challengeElement = document.querySelector(`[data-challenge="${challenge.id}"]`);
                    if (challengeElement) {
                        challengeElement.classList.remove('locked', 'completed');
                        
                        if (!challenge.unlocked) {
                            challengeElement.classList.add('locked');
                        } else if (this.completedChallenges.has(challenge.id)) {
                            challengeElement.classList.add('completed');
                        }
                    }
                });
            }

            showXPNotification(amount, reason) {
                // Create floating XP notification
                const notification = document.createElement('div');
                notification.className = 'xp-notification';
                notification.innerHTML = `
                    <div class="xp-amount">+${amount} XP</div>
                    <div class="xp-reason">${reason}</div>
                `;
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 380px;
                    background: linear-gradient(135deg, #00D9FF, #8B5CF6);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-weight: 600;
                    z-index: 10000;
                    transform: translateY(-20px);
                    opacity: 0;
                    /* transition removed */
                    box-shadow: 0 4px 20px rgba(0, 217, 255, 0.3);
                `;
                
                document.body.appendChild(notification);
                
                // Animate in
                setTimeout(() => {
                    notification.style.transform = 'translateY(0)';
                    notification.style.opacity = '1';
                }, 100);
                
                // Remove after 3 seconds
                setTimeout(() => {
                    notification.style.transform = 'translateY(-20px)';
                    notification.style.opacity = '0';
                    setTimeout(() => notification.remove(), 300);
                }, 3000);
            }

            showLevelUpNotification(levelInfo) {
                const notification = document.getElementById('levelUpNotification');
                if (!notification) return;
                
                const newLevelText = document.getElementById('new-level-text');
                const levelTitleText = document.getElementById('level-title-text');
                const rewardsList = document.getElementById('rewards-list');
                
                if (newLevelText) newLevelText.textContent = `Level ${this.currentLevel}`;
                if (levelTitleText) levelTitleText.textContent = levelInfo.title;
                
                if (rewardsList) {
                    rewardsList.innerHTML = '';
                    levelInfo.rewards.forEach(reward => {
                        const rewardElement = document.createElement('div');
                        rewardElement.className = 'reward-item';
                        rewardElement.textContent = `ðŸŽ ${reward}`;
                        rewardsList.appendChild(rewardElement);
                    });
                }
                
                notification.classList.add('show');
                
                // Auto-hide after 5 seconds
                setTimeout(() => {
                    notification.classList.remove('show');
                }, 5000);
                
                // Add click to dismiss
                notification.onclick = () => notification.classList.remove('show');
            }

            showChallengeCompletionNotification(challenge) {
                if (window.performanceFeedback) {
                    window.performanceFeedback.addHint(
                        `ðŸŽ‰ Challenge Completed: ${challenge.title} (+${challenge.xp} XP)`,
                        'success'
                    );
                }
            }

            showAchievementNotification(achievementId) {
                const achievements = {
                    'first_device': { name: 'First Steps', icon: 'ðŸŒŸ', description: 'Placed your first device' },
                    'speed_demon': { name: 'Speed Demon', icon: 'âš¡', description: 'Completed scenario in under 5 minutes' },
                    'perfectionist': { name: 'Perfectionist', icon: 'ðŸ’Ž', description: 'Achieved perfect score' },
                    'level_2': { name: 'Rising Star', icon: 'â­', description: 'Reached Level 2' },
                    'level_3': { name: 'Network Engineer', icon: 'ðŸ”§', description: 'Reached Level 3' },
                    'level_4': { name: 'Senior Engineer', icon: 'ðŸ‘¨â€ðŸ’»', description: 'Reached Level 4' },
                    'level_5': { name: 'Network Architect', icon: 'ðŸ—ï¸', description: 'Reached Level 5' }
                };
                
                const achievement = achievements[achievementId];
                if (!achievement) return;
                
                // Update the achievement badge in the sidebar
                const badgeElement = document.querySelector(`[data-achievement="${achievementId}"]`);
                if (badgeElement) {
                    badgeElement.classList.remove('locked');
                    badgeElement.classList.add('unlocked');
                }
                
                // Show notification
                const notification = document.createElement('div');
                notification.className = 'achievement-notification';
                notification.innerHTML = `
                    <div class="achievement-icon">${achievement.icon}</div>
                    <div class="achievement-text">
                        <div class="achievement-title">Achievement Unlocked!</div>
                        <div class="achievement-name">${achievement.name}</div>
                    </div>
                `;
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: linear-gradient(135deg, rgba(0, 217, 255, 0.15), rgba(0, 150, 255, 0.15));
                    border: 1px solid #00D9FF;
                    border-radius: 12px;
                    padding: 16px 20px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    min-width: 280px;
                    backdrop-filter: blur(20px);
                    box-shadow: 0 8px 32px rgba(0, 217, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                    z-index: 10000;
                    transform: translateX(100%);
                    opacity: 0;
                    /* transition removed */
                    color: white;
                `;
                
                document.body.appendChild(notification);
                
                // Animate in
                setTimeout(() => {
                    notification.style.transform = 'translateX(0)';
                    notification.style.opacity = '1';
                }, 100);
                
                // Remove after 5 seconds
                setTimeout(() => {
                    notification.style.transform = 'translateX(100%)';
                    notification.style.opacity = '0';
                    setTimeout(() => notification.remove(), 300);
                }, 5000);
            }

            bindEvents() {
                // Bind challenge click events
                document.addEventListener('click', (e) => {
                    const challengeCard = e.target.closest('[data-challenge]');
                    if (challengeCard) {
                        const challengeId = challengeCard.dataset.challenge;
                        this.startChallenge(challengeId);
                    }
                });
                
                // Bind skill node events
                document.addEventListener('click', (e) => {
                    const skillNode = e.target.closest('[data-skill]');
                    if (skillNode) {
                        const skillId = skillNode.dataset.skill;
                        this.showSkillDetails(skillId);
                    }
                });
            }

            startChallenge(challengeId) {
                const challenge = this.challenges.find(c => c.id === challengeId);
                if (!challenge || !challenge.unlocked || this.completedChallenges.has(challengeId)) {
                    return;
                }
                
                console.log(`ðŸŽ¯ Starting challenge: ${challenge.title}`);
                
                // Close challenges modal
                closeChallengesModal();
                
                // Start the challenge scenario
                this.loadChallengeScenario(challenge);
                
                // Show performance sidebar with challenge tracking
                if (window.performanceFeedback) {
                    window.performanceFeedback.showSidebar();
                    window.performanceFeedback.addHint(`ðŸŽ¯ Challenge Started: ${challenge.title}`, 'info');
                }
            }

            loadChallengeScenario(challenge) {
                // Map challenges to scenario configurations
                const scenarioMappings = {
                    "basic-connectivity": { difficulty: 'easy', type: 'network' },
                    "router-setup": { difficulty: 'easy', type: 'router' },
                    "rip-protocol": { difficulty: 'medium', type: 'rip' },
                    "vlan-basics": { difficulty: 'medium', type: 'vlan' },
                    "ospf-config": { difficulty: 'hard', type: 'ospf' },
                    "network-troubleshooting": { difficulty: 'hard', type: 'troubleshooting' }
                };
                
                const scenario = scenarioMappings[challenge.id];
                if (scenario && typeof window.startScenario === 'function') {
                    // Store current challenge for completion tracking
                    this.currentChallenge = challenge;
                    window.startScenario(scenario.difficulty, scenario.type);
                }
            }

            showSkillDetails(skillId) {
                // Find the skill
                let skill = null;
                Object.values(this.skills).forEach(category => {
                    if (category.skills[skillId]) {
                        skill = category.skills[skillId];
                    }
                });
                
                if (skill && window.performanceFeedback) {
                    const message = skill.unlocked ? 
                        `ðŸ“Š ${skill.name}: ${skill.progress}% Complete` :
                        `ðŸ”’ ${skill.name}: Unlock at Level ${skill.level}`;
                    window.performanceFeedback.addHint(message, 'info');
                }
            }

            // Integration with existing scenario system
            onScenarioCompleted(difficulty, problemType, score, timeBonus) {
                // Award XP based on performance
                let baseXP = { 
                    foundation: 15, 
                    easy: 25, 
                    medium: 50, 
                    hard: 100 
                }[difficulty] || 15;
                let bonusXP = Math.floor(score / 10) + timeBonus;
                
                this.awardXP(baseXP + bonusXP, `${difficulty.toUpperCase()} Scenario Completed`);
                
                // Check if this was a challenge completion
                if (this.currentChallenge) {
                    this.completeChallenge(this.currentChallenge.id);
                    this.currentChallenge = null;
                }
                
                // Award achievements based on performance
                if (score >= 100) {
                    this.unlockAchievement('perfectionist');
                }
                
                if (timeBonus > 50) {
                    this.unlockAchievement('speed_demon');
                }
            }

            // Public API
            getStats() {
                return {
                    level: this.currentLevel,
                    xp: this.currentXP,
                    title: this.levelData[this.currentLevel]?.title,
                    achievements: Array.from(this.achievements),
                    completedChallenges: Array.from(this.completedChallenges),
                    skills: this.skills
                };
            }

            reset() {
                if (confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
                    localStorage.removeItem('networkLevelProgress');
                    location.reload();
                }
            }
        } // End of NetworkLevelSystem class

        // Global functions for modals
        function openChallengesModal() {
            const modal = document.getElementById('challengesModal');
            if (modal) {
                modal.classList.add('active');
                modal.style.display = 'flex';
            }
        }

        function closeChallengesModal() {
            const modal = document.getElementById('challengesModal');
            if (modal) {
                modal.classList.remove('active');
                modal.style.display = 'none';
            }
        }

        // Initialize the level system when page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize after a short delay to ensure all other systems are ready
            setTimeout(() => {
                window.networkLevelSystem = new NetworkLevelSystem();
                
                // Integrate with existing performance feedback system
                if (window.performanceFeedback) {
                    const originalTrackAction = window.performanceFeedback.trackAction;
                    window.performanceFeedback.trackAction = function(actionType, data) {
                        if (originalTrackAction) {
                            originalTrackAction.call(this, actionType, data);
                        }
                        // Also track with level system
                        window.networkLevelSystem.trackAction(actionType, data);
                    };
                }
                
                // Override scenario completion to include level system
                const originalCheckSolution = window.checkSolution;
                if (originalCheckSolution) {
                    window.checkSolution = function(scenario, autoSubmit = false) {
                        const result = originalCheckSolution.call(this, scenario, autoSubmit);
                        
                        if (result && window.networkLevelSystem) {
                            // Calculate score and time bonus (you may need to adjust this based on your existing scoring system)
                            const score = 85; // Example score
                            const timeBonus = 15; // Example time bonus
                            window.networkLevelSystem.onScenarioCompleted(
                                scenario.difficulty || 'medium',
                                scenario.problemType || 'general',
                                score,
                                timeBonus
                            );
                        }
                        
                        return result;
                    };
                }
                
                console.log('ðŸŽ® Network Level System fully integrated!');
            }, 1000);
        });

        // Export for global access
        window.openChallengesModal = openChallengesModal;
        window.closeChallengesModal = closeChallengesModal;
        
        })(); // End of Network Level System IIFE

        // ===== INTERACTIVE TOPOLOGY SIMULATOR FUNCTIONALITY =====
        
        // Topology simulator variables
        let topologyCanvas = null;
        let topologyCtx = null;
        let topologyDevices = [];
        let topologyConnections = [];
        let topologyConnectionMode = false;
        let selectedTopologyDevice = null;
        let draggedTopologyDevice = null;
        let topologyDeviceCounter = { router: 0, switch: 0, pc: 0 };

        // Device images for topology canvas
        const topologyImages = {
            router: new Image(),
            switch: new Image(),
            pc: new Image()
        };

        // Initialize topology simulator
        function initTopologySimulator() {
            topologyCanvas = document.getElementById('topologyReferenceCanvas');
            if (!topologyCanvas) return;
            
            topologyCtx = topologyCanvas.getContext('2d');
            
            // Load device images
            topologyImages.router.src = '{{ url_for("static", filename="img/Router.png") }}';
            topologyImages.switch.src = '{{ url_for("static", filename="img/Switch.png") }}';
            topologyImages.pc.src = '{{ url_for("static", filename="img/PC.png") }}';

            // Set up canvas event listeners
            setupTopologyCanvasEvents();
            setupTopologyDragAndDrop();
            
            // Initial canvas draw
            drawTopologyCanvas();
        }

        function setupTopologyCanvasEvents() {
            // Canvas click handling
            topologyCanvas.addEventListener('click', (e) => {
                const rect = topologyCanvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                if (topologyConnectionMode) {
                    handleTopologyConnection(x, y);
                } else {
                    selectTopologyDevice(x, y);
                }
            });

            // Mouse move for dragging
            topologyCanvas.addEventListener('mousemove', (e) => {
                if (draggedTopologyDevice) {
                    const rect = topologyCanvas.getBoundingClientRect();
                    draggedTopologyDevice.x = e.clientX - rect.left;
                    draggedTopologyDevice.y = e.clientY - rect.top;
                    drawTopologyCanvas();
                }
            });

            // Mouse up to stop dragging
            topologyCanvas.addEventListener('mouseup', () => {
                draggedTopologyDevice = null;
            });
        }

        function setupTopologyDragAndDrop() {
            const topologyDeviceElements = document.querySelectorAll('.topology-device');
            
            topologyDeviceElements.forEach(device => {
                device.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', device.dataset.deviceType);
                });
            });

            topologyCanvas.addEventListener('dragover', (e) => {
                e.preventDefault();
            });

            topologyCanvas.addEventListener('drop', (e) => {
                e.preventDefault();
                const deviceType = e.dataTransfer.getData('text/plain');
                const rect = topologyCanvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                addTopologyDevice(deviceType, x, y);
            });
        }

        function addTopologyDevice(type, x, y) {
            topologyDeviceCounter[type]++;
            const device = {
                id: `${type}_${topologyDeviceCounter[type]}`,
                type: type,
                x: x,
                y: y,
                name: `${type.charAt(0).toUpperCase() + type.slice(1)} ${topologyDeviceCounter[type]}`,
                width: 50,
                height: 50
            };
            
            topologyDevices.push(device);
            drawTopologyCanvas();
        }

        function selectTopologyDevice(x, y) {
            selectedTopologyDevice = null;
            for (let device of topologyDevices) {
                if (x >= device.x - device.width/2 && x <= device.x + device.width/2 &&
                    y >= device.y - device.height/2 && y <= device.y + device.height/2) {
                    selectedTopologyDevice = device;
                    draggedTopologyDevice = device;
                    break;
                }
            }
            drawTopologyCanvas();
        }

        function handleTopologyConnection(x, y) {
            const clickedDevice = findTopologyDeviceAt(x, y);
            if (!clickedDevice) return;

            if (selectedTopologyDevice && selectedTopologyDevice !== clickedDevice) {
                // Create connection
                const connection = {
                    device1: selectedTopologyDevice,
                    device2: clickedDevice,
                    id: `conn_${selectedTopologyDevice.id}_${clickedDevice.id}`
                };
                
                // Check if connection already exists
                const exists = topologyConnections.some(conn => 
                    (conn.device1 === selectedTopologyDevice && conn.device2 === clickedDevice) ||
                    (conn.device1 === clickedDevice && conn.device2 === selectedTopologyDevice)
                );
                
                if (!exists) {
                    topologyConnections.push(connection);
                }
                
                selectedTopologyDevice = null;
            } else {
                selectedTopologyDevice = clickedDevice;
            }
            
            drawTopologyCanvas();
        }

        function findTopologyDeviceAt(x, y) {
            for (let device of topologyDevices) {
                if (x >= device.x - device.width/2 && x <= device.x + device.width/2 &&
                    y >= device.y - device.height/2 && y <= device.y + device.height/2) {
                    return device;
                }
            }
            return null;
        }

        function drawTopologyCanvas() {
            if (!topologyCtx) return;
            
            // Clear canvas
            topologyCtx.clearRect(0, 0, topologyCanvas.width, topologyCanvas.height);
            
            // Draw connections
            topologyConnections.forEach(connection => {
                topologyCtx.strokeStyle = '#3B82F6';
                topologyCtx.lineWidth = 2;
                topologyCtx.beginPath();
                topologyCtx.moveTo(connection.device1.x, connection.device1.y);
                topologyCtx.lineTo(connection.device2.x, connection.device2.y);
                topologyCtx.stroke();
            });
            
            // Draw devices
            topologyDevices.forEach(device => {
                // Device background
                topologyCtx.fillStyle = device === selectedTopologyDevice ? '#F59E0B' : '#1E293B';
                topologyCtx.strokeStyle = device === selectedTopologyDevice ? '#F59E0B' : '#3B82F6';
                topologyCtx.lineWidth = 2;
                
                topologyCtx.fillRect(
                    device.x - device.width/2, 
                    device.y - device.height/2, 
                    device.width, 
                    device.height
                );
                topologyCtx.strokeRect(
                    device.x - device.width/2, 
                    device.y - device.height/2, 
                    device.width, 
                    device.height
                );
                
                // Device icon/text
                topologyCtx.fillStyle = '#FFFFFF';
                topologyCtx.font = '12px Arial';
                topologyCtx.textAlign = 'center';
                
                let icon = '';
                switch(device.type) {
                    case 'router': icon = 'ðŸ”€'; break;
                    case 'switch': icon = 'ðŸ”„'; break;
                    case 'pc': icon = 'ðŸ’»'; break;
                }
                
                topologyCtx.fillText(icon, device.x, device.y + 5);
                
                // Device name
                topologyCtx.font = '10px Arial';
                topologyCtx.fillText(device.name, device.x, device.y + 35);
            });
        }

        // Topology template functions
        function loadTopologyTemplate(topologyType) {
            clearTopologyCanvas();
            
            switch(topologyType) {
                case 'point-to-point':
                    addTopologyDevice('router', 150, 200);
                    addTopologyDevice('router', 450, 200);
                    setTimeout(() => {
                        if (topologyDevices.length >= 2) {
                            topologyConnections.push({
                                device1: topologyDevices[0],
                                device2: topologyDevices[1],
                                id: 'conn_template_1'
                            });
                            drawTopologyCanvas();
                        }
                    }, 100);
                    break;
                    
                case 'star':
                    addTopologyDevice('switch', 300, 200);
                    addTopologyDevice('pc', 200, 120);
                    addTopologyDevice('pc', 400, 120);
                    addTopologyDevice('pc', 200, 280);
                    addTopologyDevice('pc', 400, 280);
                    setTimeout(() => {
                        const center = topologyDevices[0];
                        for (let i = 1; i < topologyDevices.length; i++) {
                            topologyConnections.push({
                                device1: center,
                                device2: topologyDevices[i],
                                id: `conn_star_${i}`
                            });
                        }
                        drawTopologyCanvas();
                    }, 100);
                    break;
                    
                case 'ring':
                    addTopologyDevice('router', 300, 100);
                    addTopologyDevice('router', 450, 200);
                    addTopologyDevice('router', 300, 300);
                    addTopologyDevice('router', 150, 200);
                    setTimeout(() => {
                        for (let i = 0; i < topologyDevices.length; i++) {
                            const next = (i + 1) % topologyDevices.length;
                            topologyConnections.push({
                                device1: topologyDevices[i],
                                device2: topologyDevices[next],
                                id: `conn_ring_${i}`
                            });
                        }
                        drawTopologyCanvas();
                    }, 100);
                    break;
                    
                case 'mesh':
                    addTopologyDevice('router', 200, 150);
                    addTopologyDevice('router', 400, 150);
                    addTopologyDevice('router', 300, 250);
                    setTimeout(() => {
                        for (let i = 0; i < topologyDevices.length; i++) {
                            for (let j = i + 1; j < topologyDevices.length; j++) {
                                topologyConnections.push({
                                    device1: topologyDevices[i],
                                    device2: topologyDevices[j],
                                    id: `conn_mesh_${i}_${j}`
                                });
                            }
                        }
                        drawTopologyCanvas();
                    }, 100);
                    break;
                    
                case 'tree':
                    addTopologyDevice('router', 300, 100);
                    addTopologyDevice('switch', 200, 200);
                    addTopologyDevice('switch', 400, 200);
                    addTopologyDevice('pc', 150, 300);
                    addTopologyDevice('pc', 250, 300);
                    addTopologyDevice('pc', 350, 300);
                    addTopologyDevice('pc', 450, 300);
                    setTimeout(() => {
                        topologyConnections.push({
                            device1: topologyDevices[0],
                            device2: topologyDevices[1],
                            id: 'conn_tree_1'
                        });
                        topologyConnections.push({
                            device1: topologyDevices[0],
                            device2: topologyDevices[2],
                            id: 'conn_tree_2'
                        });
                        topologyConnections.push({
                            device1: topologyDevices[1],
                            device2: topologyDevices[3],
                            id: 'conn_tree_3'
                        });
                        topologyConnections.push({
                            device1: topologyDevices[1],
                            device2: topologyDevices[4],
                            id: 'conn_tree_4'
                        });
                        topologyConnections.push({
                            device1: topologyDevices[2],
                            device2: topologyDevices[5],
                            id: 'conn_tree_5'
                        });
                        topologyConnections.push({
                            device1: topologyDevices[2],
                            device2: topologyDevices[6],
                            id: 'conn_tree_6'
                        });
                        drawTopologyCanvas();
                    }, 100);
                    break;
            }
        }

        function clearTopologyCanvas() {
            topologyDevices = [];
            topologyConnections = [];
            selectedTopologyDevice = null;
            draggedTopologyDevice = null;
            topologyDeviceCounter = { router: 0, switch: 0, pc: 0 };
            drawTopologyCanvas();
        }

        function toggleTopologyConnectionMode() {
            topologyConnectionMode = !topologyConnectionMode;
            const btn = event.target;
            btn.classList.toggle('active', topologyConnectionMode);
            btn.textContent = topologyConnectionMode ? 'ðŸ”— Connecting...' : 'ðŸ”— Connect';
            topologyCanvas.className = topologyConnectionMode ? 'connection-mode' : '';
            selectedTopologyDevice = null;
            drawTopologyCanvas();
        }

        function validateTopologyConfiguration() {
            let validation = {
                devices: topologyDevices.length,
                connections: topologyConnections.length,
                deviceTypes: {}
            };
            
            topologyDevices.forEach(device => {
                validation.deviceTypes[device.type] = (validation.deviceTypes[device.type] || 0) + 1;
            });
            
            const message = `Topology Analysis:\\n` +
                          `â€¢ Devices: ${validation.devices}\\n` +
                          `â€¢ Connections: ${validation.connections}\\n` +
                          `â€¢ Routers: ${validation.deviceTypes.router || 0}\\n` +
                          `â€¢ Switches: ${validation.deviceTypes.switch || 0}\\n` +
                          `â€¢ PCs: ${validation.deviceTypes.pc || 0}`;
            
            alert(message);
        }

        // Initialize topology simulator when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(initTopologySimulator, 1000);
            // Initialize Topology Learning System
            // DISABLED: initializeTopologyLearning function not available in this context
            // initializeTopologyLearning();
        });

        // Export topology functions for global access
        window.loadTopologyTemplate = loadTopologyTemplate;
        window.clearTopologyCanvas = clearTopologyCanvas;
        window.toggleTopologyConnectionMode = toggleTopologyConnectionMode;
        window.validateTopologyConfiguration = validateTopologyConfiguration;
    

/**
 * Score Viewer JavaScript Module
 * Enhanced functionality for admin score management
 */

class ScoreViewer {
    constructor() {
        this.currentUserId = null;
        this.currentUsername = '';
        this.init();
    }

    init() {
        console.log('🎯 Score Viewer initialized');
        this.attachEventListeners();
        this.initDataTables();
    }

    attachEventListeners() {
        // View scores button functionality
        document.querySelectorAll('.view-scores-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const userId = button.dataset.userId;
                const username = button.dataset.username;
                this.showUserScores(userId, username);
            });
        });

        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(tab.dataset.view);
            });
        });

        // Filter functionality
        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.filterScoresByCategory(e.target.value);
            });
        }
    }    initDataTables() {
        // Initialize DataTables for better table functionality
        if (typeof $ !== 'undefined' && $.fn.DataTable) {
            // Helper function to safely initialize a DataTable
            function safeInitDataTable(selector, options) {
                const table = $(selector);
                if (table.length === 0) return; // Table doesn't exist
                
                try {
                    if ($.fn.DataTable.isDataTable(selector)) {
                        table.DataTable().destroy();
                    }
                    table.DataTable(options);
                } catch (error) {
                    console.warn(`Failed to initialize DataTable for ${selector}:`, error);
                }
            }

            // Initialize Users Table with 5 items per page
            safeInitDataTable('#users-table', {
                pageLength: 5,
                lengthChange: false,
                searching: true,
                info: true,
                paging: true,
                responsive: true,
                language: {
                    search: "Search Users:",
                    info: "Showing _START_ to _END_ of _TOTAL_ users",
                    infoEmpty: "No users found",
                    infoFiltered: "(filtered from _MAX_ total users)",
                    paginate: {
                        first: "First",
                        last: "Last",
                        next: "Next",
                        previous: "Prev"
                    }
                }
            });

            // Initialize Scores Table with 5 items per page
            safeInitDataTable('#scores-table', {
                pageLength: 5,
                lengthChange: false,
                searching: true,
                info: true,
                paging: true,
                responsive: true,
                language: {
                    search: "Search Scores:",
                    info: "Showing _START_ to _END_ of _TOTAL_ scores",
                    infoEmpty: "No scores found",
                    infoFiltered: "(filtered from _MAX_ total scores)",
                    paginate: {
                        first: "First",
                        last: "Last",
                        next: "Next",
                        previous: "Prev"
                    }
                }
            });
        }
    }

    showUserScores(userId, username) {
        this.currentUserId = userId;
        this.currentUsername = username;

        // Update username display
        const usernameDisplay = document.getElementById('username-display');
        if (usernameDisplay) {
            usernameDisplay.textContent = username;
        }

        // Switch to user scores view
        this.switchTab('user-scores');

        // Load user scores
        this.loadUserScores(userId);
    }

    switchTab(viewName) {
        // Remove active classes
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.view-container').forEach(view => {
            view.classList.remove('view-active');
        });

        // Add active to target tab
        const targetTab = document.querySelector(`[data-view="${viewName}"]`);
        if (targetTab) {
            targetTab.classList.add('active');
        }

        // Show target view
        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            setTimeout(() => {
                targetView.classList.add('view-active');
            }, 100);
        }
    }

    async loadUserScores(userId) {
        const userScoresTbody = document.getElementById('user-scores-tbody');
        
        if (!userScoresTbody) {
            console.error('User scores table body not found');
            return;
        }

        // Show loading state
        userScoresTbody.innerHTML = `
            <tr>
                <td colspan="5" class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loading user scores...
                </td>
            </tr>
        `;

        try {
            const response = await fetch(`/admin/scores/user/${userId}`);
            const data = await response.json();

            if (data.success) {
                this.updateUserScoresTable(data.scores);
                this.updateUserStats(data.stats);
            } else {
                this.showError(userScoresTbody, 'Failed to load user scores.');
            }
        } catch (error) {
            console.error('Error loading user scores:', error);
            this.showError(userScoresTbody, 'Network error. Please try again.');
        }
    }

    updateUserScoresTable(scores) {
        const userScoresTbody = document.getElementById('user-scores-tbody');        if (scores.length === 0) {
            userScoresTbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-state">
                        <i class="fas fa-chart-bar"></i>
                        <p>No scores found for this user.</p>
                    </td>
                </tr>
            `;
            
            // Destroy DataTable when no scores to show
            try {
                if (typeof $ !== 'undefined' && $.fn.DataTable && $.fn.DataTable.isDataTable('#user-scores-table')) {
                    $('#user-scores-table').DataTable().destroy();
                }
            } catch (error) {
                console.warn('Error destroying empty user scores DataTable:', error);
            }
            
            return;
        }        userScoresTbody.innerHTML = scores.map(score => {
            const scoreClass = score.score >= 80 ? 'high' : score.score >= 60 ? 'medium' : 'low';
            
            return `
                <tr>
                    <td>
                        <div class="score-value">
                            <span class="score-badge score-${scoreClass}">
                                ${score.score}%
                            </span>
                        </div>
                    </td>
                    <td>
                        <span class="category-tag category-${score.category}">
                            ${this.capitalizeFirst(score.category)}
                        </span>
                    </td>
                    <td>
                        <span class="date-time">${score.date_attempted}</span>
                    </td>
                    <td>
                        <form action="/admin/scores/delete/${score.id}" method="POST" style="display: inline;">
                            <button type="submit" class="btn btn-danger delete-score-btn" data-score-id="${score.id}">
                                <i class='fas fa-trash'></i>
                                Delete
                            </button>
                        </form>
                    </td>
                </tr>
            `;
        }).join('');// Reinitialize DataTable for user scores with pagination
        this.reinitUserScoresDataTable();
        
        // Re-attach delete event listeners
        this.attachDeleteEventListeners();
    }

    reinitUserScoresDataTable() {
        // Safely destroy existing DataTable if it exists
        try {
            if (typeof $ !== 'undefined' && $.fn.DataTable && $.fn.DataTable.isDataTable('#user-scores-table')) {
                $('#user-scores-table').DataTable().destroy();
            }
        } catch (error) {
            console.warn('Error destroying user scores DataTable:', error);
        }
        
        // Reinitialize with pagination settings
        try {
            if (typeof $ !== 'undefined' && $.fn.DataTable) {
                $('#user-scores-table').DataTable({
                    pageLength: 5,
                    lengthChange: false,
                    searching: true,
                    info: true,
                    paging: true,
                    responsive: true,
                    language: {
                        search: "Search User Scores:",
                        info: "Showing _START_ to _END_ of _TOTAL_ scores",
                        infoEmpty: "No scores found",
                        infoFiltered: "(filtered from _MAX_ total scores)",
                        paginate: {
                            first: "First",
                            last: "Last",
                            next: "Next",
                            previous: "Prev"
                        }
                    }
                });
            }
        } catch (error) {
            console.warn('Error initializing user scores DataTable:', error);
        }
    }

    updateUserStats(stats) {
        // Update category statistics for the user
        Object.keys(stats).forEach(category => {
            const statElement = document.getElementById(`user-stat-${category}`);
            const avgElement = document.getElementById(`user-stat-avg-${category}`);
            
            if (statElement) {
                statElement.textContent = stats[category].count;
            }
            if (avgElement) {
                avgElement.textContent = `Avg: ${stats[category].avg_score.toFixed(1)} | Max: ${stats[category].max_score}`;
            }
        });
    }

    attachDeleteEventListeners() {
        document.querySelectorAll('.delete-score-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.confirmDelete(button);
            });
        });
    }

    confirmDelete(button) {
        const scoreId = button.dataset.scoreId;
        
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to recover this score entry!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#e74c3c',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, delete it!',
                background: 'rgba(26, 35, 126, 0.9)',
                color: '#fff'
            }).then((result) => {
                if (result.isConfirmed) {
                    button.closest('form').submit();
                    this.playClickSound();
                }
            });
        } else {
            // Fallback to native confirm
            if (confirm('Are you sure you want to delete this score? This action cannot be undone.')) {
                button.closest('form').submit();
            }
        }
    }

    filterScoresByCategory(category) {
        const tableRows = document.querySelectorAll('#scores-table tbody tr');
        
        tableRows.forEach(row => {
            if (category === '') {
                row.style.display = '';
            } else {
                const categoryCell = row.querySelector('.category-tag');
                if (categoryCell && categoryCell.textContent.toLowerCase().includes(category.toLowerCase())) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        });
    }

    showError(container, message) {
        container.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>${message}</p>
                </td>
            </tr>
        `;
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    playClickSound() {
        const clickSound = document.getElementById('clickSound');
        if (clickSound) {
            clickSound.currentTime = 0;
            clickSound.play().catch(e => {
                // Audio play failed, ignore silently
                console.log('Audio play failed:', e.message);
            });
        }
    }
}

// Initialize the Score Viewer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('/admin/scores')) {
        window.scoreViewer = new ScoreViewer();
    }
});

// Export for global access
window.ScoreViewer = ScoreViewer;

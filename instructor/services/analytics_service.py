"""
Comprehensive Analytics Service for RiddleNet instructor Dashboard
Provides advanced analytics, reporting, and data export functionality
"""

from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_, extract, distinct
from collections import defaultdict
import json
import os
import csv
import io
import logging
from typing import Dict, List, Optional, Any, Tuple

# Import models
from __init__ import db
from user.models.user import User
from user.models.score import Score
from instructor.models.essay_response import EssayResponse
from instructor.models.activity_log import ActivityLog
from instructor.models.question import Question

class AnalyticsService:
    """Advanced analytics service for RiddleNet platform"""
    
    def __init__(self):
        self.categories = ['riddle', 'topology', 'troubleshoot', 'crimping', 'networking', 'collaboration']
        self.logger = logging.getLogger(__name__)
    
    # ==================== PERFORMANCE ANALYTICS ====================
    
    def get_student_performance_analytics(self, date_range: int = 30, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get comprehensive student performance analytics"""
        start_date = datetime.now() - timedelta(days=date_range)
        
        # Base query
        query = Score.query.filter(Score.date_attempted >= start_date)
        if user_id:
            query = query.filter(Score.user_id == user_id)
        
        scores = query.all()
        
        if not scores:
            return self._empty_performance_analytics()
        
        # Calculate comprehensive metrics
        score_values = [s.score for s in scores]
        analytics = {
            'total_attempts': len(scores),
            'average_score': round(sum(score_values) / len(score_values), 2),
            'median_score': self._calculate_median(score_values),
            'highest_score': max(score_values),
            'lowest_score': min(score_values),
            'score_distribution': self._get_score_distribution(score_values),
            'improvement_trend': self._calculate_improvement_trend(scores),
            'category_breakdown': self._get_category_breakdown(scores),
            'time_analysis': self._get_time_analysis(scores),
            'student_rankings': self._get_student_rankings(scores),
            'completion_rates': self._get_completion_rates(date_range),
            'engagement_metrics': self._get_engagement_metrics(scores, date_range)
        }
        
        return analytics
    
    def get_learning_path_analytics(self) -> Dict[str, Any]:
        """Analyze learning path progression and completion"""
        # Get progression data for each category
        progression_data = {}
        
        for category in self.categories:
            cat_scores = Score.query.filter(Score.category == category).all()
            if cat_scores:
                # Group by user to track individual progress
                user_progress = defaultdict(list)
                for score in cat_scores:
                    user_progress[score.user_id].append({
                        'score': score.score,
                        'date': score.date_attempted,
                        'category': score.category
                    })
                
                # Calculate progression metrics
                progression_data[category] = {
                    'total_users': len(user_progress),
                    'average_attempts_per_user': round(len(cat_scores) / len(user_progress), 2),
                    'completion_rate': self._calculate_category_completion_rate(user_progress),
                    'average_improvement': self._calculate_average_improvement(user_progress),
                    'difficulty_analysis': self._analyze_category_difficulty(cat_scores)
                }
        
        return {
            'category_progressions': progression_data,
            'overall_completion_rate': self._calculate_overall_completion_rate(),
            'learning_path_effectiveness': self._calculate_path_effectiveness(),
            'recommended_improvements': self._generate_learning_recommendations(progression_data)
        }
    
    def get_engagement_metrics(self, date_range: int = 30) -> Dict[str, Any]:
        """Calculate comprehensive engagement metrics"""
        start_date = datetime.now() - timedelta(days=date_range)
        
        # Active users per day
        daily_engagement = self._get_daily_engagement(start_date)
        
        # Session duration analysis (approximated from score submission patterns)
        session_data = self._analyze_session_patterns(start_date)
        
        # Category preference analysis
        category_preferences = self._analyze_category_preferences(start_date)
        
        # Peak activity times
        activity_patterns = self._analyze_activity_patterns(start_date)
        
        return {
            'daily_active_users': daily_engagement,
            'session_metrics': session_data,
            'category_preferences': category_preferences,
            'activity_patterns': activity_patterns,
            'retention_metrics': self._calculate_retention_metrics(start_date),
            'engagement_score': self._calculate_engagement_score(daily_engagement, session_data)
        }
    
    # ==================== COMPARATIVE ANALYSIS ====================
    
    def get_comparative_analysis(self, comparison_type: str = 'category') -> Dict[str, Any]:
        """Perform comparative analysis across different dimensions"""
        if comparison_type == 'category':
            return self._compare_categories()
        elif comparison_type == 'time_period':
            return self._compare_time_periods()
        elif comparison_type == 'user_groups':
            return self._compare_user_groups()
        else:
            return self._compare_categories()  # Default
    
    def _compare_categories(self) -> Dict[str, Any]:
        """Compare performance across different categories"""
        category_stats = {}
        
        for category in self.categories:
            scores = Score.query.filter(Score.category == category).all()
            if scores:
                score_values = [s.score for s in scores]
                category_stats[category] = {
                    'total_attempts': len(scores),
                    'unique_users': len(set(s.user_id for s in scores)),
                    'average_score': round(sum(score_values) / len(score_values), 2),
                    'success_rate': len([s for s in score_values if s >= 70]) / len(score_values) * 100,
                    'difficulty_rating': self._calculate_difficulty_rating(score_values),
                    'engagement_level': self._calculate_category_engagement(scores)
                }
        
        # Identify trends and insights
        insights = self._generate_category_insights(category_stats)
        
        return {
            'category_comparison': category_stats,
            'insights': insights,
            'recommendations': self._generate_category_recommendations(category_stats)
        }
    
    def _compare_time_periods(self) -> Dict[str, Any]:
        """Compare performance across different time periods"""
        current_month = datetime.now().replace(day=1)
        previous_month = (current_month - timedelta(days=1)).replace(day=1)
        
        current_scores = Score.query.filter(Score.date_attempted >= current_month).all()
        previous_scores = Score.query.filter(
            and_(Score.date_attempted >= previous_month, Score.date_attempted < current_month)
        ).all()
        
        current_stats = self._calculate_period_stats(current_scores)
        previous_stats = self._calculate_period_stats(previous_scores)
        
        # Calculate changes
        changes = {}
        for key in current_stats:
            if key in previous_stats and previous_stats[key] != 0:
                change = ((current_stats[key] - previous_stats[key]) / previous_stats[key]) * 100
                changes[f"{key}_change"] = round(change, 2)
        
        return {
            'current_period': current_stats,
            'previous_period': previous_stats,
            'changes': changes,
            'trend_analysis': self._analyze_trends(current_scores, previous_scores)
        }
    
    # ==================== EXPORT FUNCTIONALITY ====================
    
    # ==================== REAL-TIME ANALYTICS ====================
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for live dashboard updates"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Today's metrics
        today_scores = Score.query.filter(Score.date_attempted >= today_start).all()
        active_users_today = len(set(s.user_id for s in today_scores))
        
        # Recent activity (last hour)
        hour_ago = now - timedelta(hours=1)
        recent_activity = Score.query.filter(Score.date_attempted >= hour_ago).count()
        
        # Current online users (approximated by recent activity)
        minute_ago = now - timedelta(minutes=5)
        online_users = Score.query.filter(Score.date_attempted >= minute_ago).with_entities(Score.user_id).distinct().count()
        
        # Calculate average score properly
        avg_score_today = 0
        if today_scores:
            total_score = sum(s.score for s in today_scores)
            avg_raw = total_score / len(today_scores)
            # Convert to percentage using helper method
            avg_score_today = self._convert_score_to_percentage(avg_raw)
        
        return {
            'active_users_today': active_users_today,
            'recent_submissions': recent_activity,
            'estimated_online': online_users,
            'total_attempts_today': len(today_scores),
            'avg_score_today': avg_score_today,
            'timestamp': now.isoformat()
        }
    
    def get_recent_activity_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity feed for real-time monitoring"""
        recent_scores = Score.query.join(User).order_by(desc(Score.date_attempted)).limit(limit).all()
        
        activity_feed = []
        for score in recent_scores:
            # Convert score to percentage properly
            display_score = self._convert_score_to_percentage(score.score)
            
            activity_feed.append({
                'id': score.id,
                'username': score.user.username if score.user else f'User {score.user_id}',
                'action': f'Completed {score.category} quiz',
                'score': display_score,  # Use converted percentage
                'category': score.category,
                'timestamp': score.date_attempted.isoformat(),
                'time_ago': self._format_time_ago(score.date_attempted)
            })
        
        return activity_feed
    
    # ==================== CHART DATA METHODS ====================
    
    def get_performance_trend_chart_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get performance trend data formatted for Chart.js"""
        scores = Score.query.filter(
            and_(Score.date_attempted >= start_date, Score.date_attempted <= end_date)
        ).order_by(Score.date_attempted).all()
        
        # Group by date
        daily_data = defaultdict(list)
        for score in scores:
            date_key = score.date_attempted.strftime('%Y-%m-%d')
            daily_data[date_key].append(score.score)
        
        # Calculate daily averages
        dates = []
        avg_scores = []
        submission_counts = []
        
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            date_str = current_date.strftime('%Y-%m-%d')
            dates.append(date_str)
            
            if date_str in daily_data:
                day_scores = daily_data[date_str]
                avg_scores.append(round(sum(day_scores) / len(day_scores), 2))
                submission_counts.append(len(day_scores))
            else:
                avg_scores.append(0)
                submission_counts.append(0)
            
            current_date += timedelta(days=1)
        
        return {
            'labels': dates,
            'datasets': [
                {
                    'label': 'Average Score',
                    'data': avg_scores,
                    'borderColor': '#00D9FF',
                    'backgroundColor': 'rgba(0, 217, 255, 0.1)',
                    'tension': 0.4,
                    'yAxisID': 'y'
                },
                {
                    'label': 'Submissions',
                    'data': submission_counts,
                    'borderColor': '#39FF14',
                    'backgroundColor': 'rgba(57, 255, 20, 0.1)',
                    'tension': 0.4,
                    'yAxisID': 'y1'
                }
            ]
        }
    
    def get_score_distribution_chart_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get score distribution data formatted for Chart.js"""
        scores = Score.query.filter(
            and_(Score.date_attempted >= start_date, Score.date_attempted <= end_date)
        ).all()
        
        if not scores:
            return {
                'labels': ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%'],
                'datasets': [{'label': 'Distribution', 'data': [0, 0, 0, 0, 0]}]
            }
        
        # Convert scores to percentages using standardized method
        percentage_scores = [self._convert_score_to_percentage(s.score) for s in scores]
        
        # Create distribution buckets
        buckets = [0, 0, 0, 0, 0]  # [0-20, 21-40, 41-60, 61-80, 81-100]
        
        for score in percentage_scores:
            if score <= 20:
                buckets[0] += 1
            elif score <= 40:
                buckets[1] += 1
            elif score <= 60:
                buckets[2] += 1
            elif score <= 80:
                buckets[3] += 1
            else:
                buckets[4] += 1
        
        return {
            'labels': ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%'],
            'datasets': [{
                'label': 'Number of Scores',
                'data': buckets,
                'backgroundColor': [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(0, 217, 255, 0.8)',
                    'rgba(57, 255, 20, 0.8)'
                ],
                'borderColor': [
                    '#EF4444',
                    '#F59E0B',
                    '#10B981',
                    '#00D9FF',
                    '#39FF14'
                ],
                'borderWidth': 2
            }]
        }
    
    def get_category_performance_chart_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get category performance data formatted for Chart.js radar chart"""
        category_data = {}
        
        for category in self.categories:
            scores = Score.query.filter(
                and_(
                    Score.category == category,
                    Score.date_attempted >= start_date,
                    Score.date_attempted <= end_date
                )
            ).all()
            
            if scores:
                avg_score = sum(s.score for s in scores) / len(scores)
                # Convert to percentage using standardized method
                category_data[category] = self._convert_score_to_percentage(avg_score)
            else:
                category_data[category] = 0
        
        return {
            'labels': [cat.title() for cat in self.categories],
            'datasets': [{
                'label': 'Average Performance (%)',
                'data': [category_data.get(cat, 0) for cat in self.categories],
                'borderColor': '#8B5CF6',
                'backgroundColor': 'rgba(139, 92, 246, 0.2)',
                'pointBackgroundColor': '#8B5CF6',
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': '#8B5CF6'
            }]
        }
    
    def get_engagement_heatmap_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get engagement heatmap data"""
        scores = Score.query.filter(
            and_(Score.date_attempted >= start_date, Score.date_attempted <= end_date)
        ).all()
        
        # Create heatmap data: hour of day vs day of week
        heatmap_data = []
        
        for hour in range(24):
            hour_data = []
            for day in range(7):  # 0 = Monday, 6 = Sunday
                count = 0
                for score in scores:
                    if score.date_attempted.hour == hour and score.date_attempted.weekday() == day:
                        count += 1
                hour_data.append(count)
            heatmap_data.append(hour_data)
        
        return {
            'data': heatmap_data,
            'labels': {
                'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'hours': [f'{h:02d}:00' for h in range(24)]
            }
        }
    
    def export_analytics_report(self, format_type: str = 'pdf', date_range: int = 30) -> str:
        """Generate and export comprehensive analytics report"""
        data = {
            'performance': self.get_student_performance_analytics(date_range),
            'learning_paths': self.get_learning_path_analytics(),
            'engagement': self.get_engagement_metrics(date_range),
            'comparative': self.get_comparative_analysis()
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type.lower() == 'csv':
            return self._export_to_csv(data, timestamp)
        elif format_type.lower() == 'json':
            return self._export_to_json(data, timestamp)
        else:  # Default to PDF
            return self._export_to_pdf(data, timestamp)
    
    def _export_to_csv(self, data: Dict[str, Any], timestamp: str) -> str:
        """Export data to CSV format"""
        filename = f'riddlenet_analytics_{timestamp}.csv'
        filepath = os.path.join('static', 'exports', filename)
        
        # Ensure exports directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write performance data
            writer.writerow(['=== PERFORMANCE ANALYTICS ==='])
            writer.writerow(['Metric', 'Value'])
            for key, value in data['performance'].items():
                if isinstance(value, (int, float, str)):
                    writer.writerow([key.replace('_', ' ').title(), value])
            
            writer.writerow([])  # Empty row
            
            # Write category breakdown
            writer.writerow(['=== CATEGORY BREAKDOWN ==='])
            writer.writerow(['Category', 'Average Score', 'Total Attempts', 'Success Rate'])
            for category, stats in data['performance'].get('category_breakdown', {}).items():
                writer.writerow([
                    category.title(),
                    stats.get('avg_score', 0),
                    stats.get('total_attempts', 0),
                    f"{stats.get('success_rate', 0):.1f}%"
                ])
        
        return filepath
    
    def _export_to_json(self, data: Dict[str, Any], timestamp: str) -> str:
        """Export data to JSON format"""
        filename = f'riddlenet_analytics_{timestamp}.json'
        filepath = os.path.join('static', 'exports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Make data JSON serializable
        serializable_data = self._make_json_serializable(data)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(serializable_data, jsonfile, indent=2, default=str)
        
        return filepath
    
    def _export_to_pdf(self, data: Dict[str, Any], timestamp: str) -> str:
        """Export data to PDF format using ReportLab"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
        except ImportError:
            # Fallback to HTML report if ReportLab not available
            return self._export_to_html(data, timestamp)
        
        filename = f'riddlenet_analytics_{timestamp}.pdf'
        filepath = os.path.join('static', 'exports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("RiddleNet Analytics Report", title_style))
        story.append(Spacer(1, 20))
        
        # Report generation date
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Performance Summary
        story.append(Paragraph("Performance Summary", styles['Heading2']))
        perf_data = [
            ['Metric', 'Value'],
            ['Total Attempts', data['performance'].get('total_attempts', 0)],
            ['Average Score', f"{data['performance'].get('average_score', 0):.2f}"],
            ['Highest Score', data['performance'].get('highest_score', 0)],
            ['Lowest Score', data['performance'].get('lowest_score', 0)]
        ]
        
        perf_table = Table(perf_data)
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(perf_table)
        story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        return filepath
    
    def _export_to_html(self, data: Dict[str, Any], timestamp: str) -> str:
        """Export data to HTML format (fallback)"""
        filename = f'riddlenet_analytics_{timestamp}.html'
        filepath = os.path.join('static', 'exports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RiddleNet Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; color: #2c3e50; }}
                .section {{ margin: 30px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>RiddleNet Analytics Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Performance Overview</h2>
                <div class="metric">Total Attempts: {data['performance'].get('total_attempts', 0)}</div>
                <div class="metric">Average Score: {data['performance'].get('average_score', 0):.2f}</div>
                <div class="metric">Highest Score: {data['performance'].get('highest_score', 0)}</div>
            </div>
            
            <div class="section">
                <h2>Category Breakdown</h2>
                <table>
                    <tr><th>Category</th><th>Average Score</th><th>Total Attempts</th></tr>
        """
        
        # Add category data
        for category, stats in data['performance'].get('category_breakdown', {}).items():
            html_content += f"""
                    <tr>
                        <td>{category.title()}</td>
                        <td>{stats.get('avg_score', 0):.2f}</td>
                        <td>{stats.get('total_attempts', 0)}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        return filepath
    
    def _make_json_serializable(self, data: Any) -> Any:
        """Make data JSON serializable"""
        if isinstance(data, dict):
            return {k: self._make_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_json_serializable(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        elif hasattr(data, '__dict__'):
            return self._make_json_serializable(data.__dict__)
        else:
            try:
                json.dumps(data)
                return data
            except TypeError:
                return str(data)
        return filepath
    
    def get_live_activity_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get live activity feed for real-time monitoring"""
        activities = []
        
        # Recent scores
        recent_scores = Score.query.join(User).order_by(desc(Score.date_attempted)).limit(limit // 2).all()
        for score in recent_scores:
            # Convert score to percentage properly
            display_score = self._convert_score_to_percentage(score.score)
            
            activities.append({
                'type': 'score',
                'username': score.user.username if score.user else f'User {score.user_id}',
                'action': f"Completed {score.category} quiz",
                'message': f"{score.user.username if score.user else f'User {score.user_id}'} scored {display_score}% in {score.category}",
                'timestamp': score.date_attempted,
                'time_ago': self._format_time_ago(score.date_attempted),
                'category': score.category,
                'score': display_score,  # Use converted percentage
                'raw_score': score.score  # Keep raw score for debugging
            })
        
        # Recent essays
        try:
            recent_essays = EssayResponse.query.join(User).order_by(desc(EssayResponse.submission_date)).limit(limit // 2).all()
            for essay in recent_essays:
                # For essays, use the grade if available, otherwise no score
                essay_score = None
                if hasattr(essay, 'grade') and essay.grade is not None:
                    essay_score = self._convert_score_to_percentage(essay.grade)
                
                activities.append({
                    'type': 'essay',
                    'username': essay.user.username if essay.user else f'User {essay.user_id}',
                    'action': f"Submitted essay in {essay.category}",
                    'message': f"Submitted essay in {essay.category}" + (f" - Score: {essay_score}%" if essay_score is not None else ""),
                    'timestamp': essay.submission_date,
                    'time_ago': self._format_time_ago(essay.submission_date),
                    'category': essay.category,
                    'score': essay_score,  # Will be None if not graded
                    'graded': essay.is_graded
                })
        except Exception as e:
            print(f"Warning: Could not load essay data: {e}")
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    
    # ==================== HELPER METHODS ====================
    
    def _convert_score_to_percentage(self, score: float) -> float:
        """Standardized score to percentage conversion with strict bounds"""
        # Handle null/invalid scores
        if score is None or not isinstance(score, (int, float)):
            return 0.0
        
        # Convert to float and handle negative scores
        try:
            score = float(score)
        except (ValueError, TypeError):
            return 0.0
            
        if score < 0:
            return 0.0
        
        # If score appears to be in 0-3 scale (common quiz scoring), convert to percentage
        if 0 < score <= 3:
            return round((score / 3) * 100, 1)
        
        # If score is 0, keep as 0%
        elif score == 0:
            return 0.0
        
        # If score is already a reasonable percentage (4-100), use it
        elif 4 <= score <= 100:
            return round(score, 1)
        
        # For scores in 101-300 range, might be 0-300 scale
        elif 100 < score <= 300:
            return round((score / 300) * 100, 1)
        
        # For extremely high scores (like 3167, 2900), cap at 100%
        else:
            if hasattr(self, 'logger'):
                self.logger.warning(f"Capping extremely high score: {score}")
            else:
                print(f"Warning: Capping extremely high score: {score}")
            return 100.0
    
    def _empty_performance_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure"""
        return {
            'total_attempts': 0,
            'average_score': 0,
            'median_score': 0,
            'highest_score': 0,
            'lowest_score': 0,
            'score_distribution': {},
            'improvement_trend': 'no_data',
            'category_breakdown': {},
            'time_analysis': {},
            'student_rankings': [],
            'completion_rates': {},
            'engagement_metrics': {}
        }
    
    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median of a list of values"""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        return sorted_values[n//2]
    
    def _get_score_distribution(self, score_values: List[float]) -> Dict[str, int]:
        """Calculate score distribution across ranges"""
        distribution = {
            '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0
        }
        
        for score in score_values:
            if score <= 20:
                distribution['0-20'] += 1
            elif score <= 40:
                distribution['21-40'] += 1
            elif score <= 60:
                distribution['41-60'] += 1
            elif score <= 80:
                distribution['61-80'] += 1
            else:
                distribution['81-100'] += 1
        
        return distribution
    
    def _calculate_improvement_trend(self, scores: List[Score]) -> str:
        """Calculate if scores are improving over time"""
        if len(scores) < 5:
            return 'insufficient_data'
        
        # Sort by date
        sorted_scores = sorted(scores, key=lambda x: x.date_attempted)
        
        # Compare first half vs second half
        mid_point = len(sorted_scores) // 2
        first_half_avg = sum(s.score for s in sorted_scores[:mid_point]) / mid_point
        second_half_avg = sum(s.score for s in sorted_scores[mid_point:]) / (len(sorted_scores) - mid_point)
        
        improvement = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if improvement > 10:
            return 'improving'
        elif improvement < -10:
            return 'declining'
        else:
            return 'stable'
    
    def _get_category_breakdown(self, scores: List[Score]) -> Dict[str, Dict[str, Any]]:
        """Get detailed breakdown by category"""
        category_data = defaultdict(list)
        
        for score in scores:
            category_data[score.category].append(score.score)
        
        breakdown = {}
        for category, score_list in category_data.items():
            if score_list:
                success_count = len([s for s in score_list if s >= 70])
                breakdown[category] = {
                    'total_attempts': len(score_list),
                    'avg_score': round(sum(score_list) / len(score_list), 2),
                    'max_score': max(score_list),
                    'min_score': min(score_list),
                    'success_rate': round((success_count / len(score_list)) * 100, 1)
                }
        
        return breakdown
    
    def _get_time_analysis(self, scores: List[Score]) -> Dict[str, Any]:
        """Analyze performance over time periods"""
        if not scores:
            return {}
        
        # Group by day of week
        day_performance = defaultdict(list)
        for score in scores:
            day_name = score.date_attempted.strftime('%A')
            day_performance[day_name].append(score.score)
        
        # Group by hour
        hour_performance = defaultdict(list)
        for score in scores:
            hour = score.date_attempted.hour
            hour_performance[hour].append(score.score)
        
        return {
            'best_day': max(day_performance.items(), 
                          key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)[0] if day_performance else 'No data',
            'best_hour': max(hour_performance.items(), 
                           key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)[0] if hour_performance else 'No data',
            'daily_averages': {day: round(sum(scores)/len(scores), 2) for day, scores in day_performance.items() if scores}
        }
    
    def _get_student_rankings(self, scores: List[Score]) -> List[Dict[str, Any]]:
        """Get top performing students"""
        user_scores = defaultdict(list)
        
        for score in scores:
            user_scores[score.user_id].append(score.score)
        
        rankings = []
        for user_id, score_list in user_scores.items():
            try:
                user = User.query.get(user_id)
                username = user.username if user else f"User {user_id}"
            except:
                username = f"User {user_id}"
            
            rankings.append({
                'user_id': user_id,
                'username': username,
                'total_attempts': len(score_list),
                'average_score': round(sum(score_list) / len(score_list), 2),
                'highest_score': max(score_list)
            })
        
        return sorted(rankings, key=lambda x: x['highest_score'], reverse=True)[:10]
    
    def _get_completion_rates(self, date_range: int) -> Dict[str, float]:
        """Calculate completion rates for different categories"""
        completion_rates = {}
        
        for category in self.categories:
            # This is a simplified completion rate based on score attempts
            # In a real system, you'd compare against total available content
            category_scores = Score.query.filter(
                and_(
                    Score.category == category,
                    Score.date_attempted >= datetime.now() - timedelta(days=date_range)
                )
            ).all()
            
            if category_scores:
                # Assume completion is scoring above 60%
                completed = len([s for s in category_scores if s.score >= 60])
                completion_rates[category] = round((completed / len(category_scores)) * 100, 2)
            else:
                completion_rates[category] = 0
        
        return completion_rates
    
    def _get_engagement_metrics(self, scores: List[Score], date_range: int) -> Dict[str, Any]:
        """Calculate user engagement metrics"""
        if not scores:
            return {'active_users': 0, 'avg_sessions_per_user': 0}
        
        unique_users = len(set(s.user_id for s in scores))
        total_attempts = len(scores)
        
        return {
            'active_users': unique_users,
            'avg_attempts_per_user': round(total_attempts / unique_users, 2) if unique_users else 0,
            'engagement_rate': round((unique_users / User.query.count()) * 100, 2) if User.query.count() else 0
        }
    
    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median value from a list"""
        if not values:
            return 0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return sorted_vals[n//2] if n % 2 == 1 else (sorted_vals[n//2-1] + sorted_vals[n//2]) / 2
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Make object JSON serializable"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
    
    # Placeholder methods for complex analytics (implement based on specific needs)
    def _get_daily_engagement(self, start_date: datetime) -> Dict[str, int]:
        """Calculate daily active users"""
        daily_users = {}
        current_date = start_date.date()
        end_date = datetime.now().date()
        
        while current_date <= end_date:
            count = Score.query.filter(
                func.date(Score.date_attempted) == current_date
            ).with_entities(Score.user_id).distinct().count()
            
            daily_users[current_date.strftime('%Y-%m-%d')] = count
            current_date += timedelta(days=1)
        
        return daily_users
    
    def _analyze_session_patterns(self, start_date: datetime) -> Dict[str, Any]:
        """Analyze user session patterns"""
        # Simplified session analysis based on score submission patterns
        return {
            'avg_session_length': '25 minutes',  # Placeholder
            'peak_hours': [14, 15, 16, 20, 21],  # 2-4 PM, 8-9 PM
            'session_frequency': 'Daily'
        }
    
    def _analyze_category_preferences(self, start_date: datetime) -> Dict[str, int]:
        """Analyze which categories are most popular"""
        preferences = {}
        for category in self.categories:
            count = Score.query.filter(
                and_(Score.category == category, Score.date_attempted >= start_date)
            ).count()
            preferences[category] = count
        
        return dict(sorted(preferences.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_activity_patterns(self, start_date: datetime) -> Dict[str, Any]:
        """Analyze when users are most active"""
        hourly_activity = defaultdict(int)
        
        scores = Score.query.filter(Score.date_attempted >= start_date).all()
        for score in scores:
            hour = score.date_attempted.hour
            hourly_activity[hour] += 1
        
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 12
        
        return {
            'hourly_distribution': dict(hourly_activity),
            'peak_hour': peak_hour,
            'active_hours': [h for h, count in hourly_activity.items() if count > 0]
        }
    
    def _calculate_retention_metrics(self, start_date: datetime) -> Dict[str, float]:
        """Calculate user retention metrics"""
        total_users = User.query.count()
        active_users = Score.query.filter(
            Score.date_attempted >= start_date
        ).with_entities(Score.user_id).distinct().count()
        
        return {
            'retention_rate': round((active_users / total_users) * 100, 2) if total_users else 0,
            'active_user_ratio': round(active_users / total_users, 2) if total_users else 0
        }
    
    def _calculate_engagement_score(self, daily_engagement: Dict[str, int], session_data: Dict[str, Any]) -> float:
        """Calculate overall engagement score"""
        if not daily_engagement:
            return 0
        
        avg_daily_users = sum(daily_engagement.values()) / len(daily_engagement)
        total_users = User.query.count()
        
        engagement_score = (avg_daily_users / total_users) * 100 if total_users else 0
        return round(min(engagement_score, 100), 2)  # Cap at 100
    
    # Additional placeholder methods
    def _calculate_category_completion_rate(self, user_progress: Dict) -> float:
        """Calculate completion rate for a category"""
        if not user_progress:
            return 0
        
        completed_users = len([u for u, scores in user_progress.items() if len(scores) >= 3])  # 3+ attempts = completed
        return round((completed_users / len(user_progress)) * 100, 2)
    
    def _calculate_average_improvement(self, user_progress: Dict) -> float:
        """Calculate average improvement across users"""
        improvements = []
        
        for user_scores in user_progress.values():
            if len(user_scores) >= 2:
                sorted_scores = sorted(user_scores, key=lambda x: x['date'])
                first_score = sorted_scores[0]['score']
                last_score = sorted_scores[-1]['score']
                if first_score > 0:
                    improvement = ((last_score - first_score) / first_score) * 100
                    improvements.append(improvement)
        
        return round(sum(improvements) / len(improvements), 2) if improvements else 0
    
    def _analyze_category_difficulty(self, scores: List[Score]) -> Dict[str, Any]:
        """Analyze difficulty level of a category"""
        if not scores:
            return {'difficulty': 'unknown', 'success_rate': 0}
        
        score_values = [s.score for s in scores]
        avg_score = sum(score_values) / len(score_values)
        success_rate = len([s for s in score_values if s >= 70]) / len(score_values) * 100
        
        if avg_score >= 80:
            difficulty = 'easy'
        elif avg_score >= 60:
            difficulty = 'medium'
        else:
            difficulty = 'hard'
        
        return {
            'difficulty': difficulty,
            'success_rate': round(success_rate, 2),
            'average_score': round(avg_score, 2)
        }
    
    def _calculate_overall_completion_rate(self) -> float:
        """Calculate overall learning path completion rate"""
        total_users = User.query.count()
        if not total_users:
            return 0
        
        # Users who have attempted at least 3 categories
        active_users = db.session.query(Score.user_id).group_by(Score.user_id).having(
            func.count(distinct(Score.category)) >= 3
        ).count()
        
        return round((active_users / total_users) * 100, 2)
    
    def _calculate_path_effectiveness(self) -> Dict[str, Any]:
        """Calculate learning path effectiveness"""
        # Simplified effectiveness based on improvement trends
        improving_users = 0
        total_tracked_users = 0
        
        for user in User.query.all():
            user_scores = Score.query.filter(Score.user_id == user.id).order_by(Score.date_attempted).all()
            if len(user_scores) >= 3:
                total_tracked_users += 1
                first_avg = sum(s.score for s in user_scores[:len(user_scores)//2]) / (len(user_scores)//2)
                last_avg = sum(s.score for s in user_scores[len(user_scores)//2:]) / (len(user_scores) - len(user_scores)//2)
                
                if last_avg > first_avg:
                    improving_users += 1
        
        effectiveness = round((improving_users / total_tracked_users) * 100, 2) if total_tracked_users else 0
        
        return {
            'effectiveness_rate': effectiveness,
            'total_tracked_users': total_tracked_users,
            'improving_users': improving_users
        }
    
    def _generate_learning_recommendations(self, progression_data: Dict) -> List[str]:
        """Generate recommendations based on learning path analysis"""
        recommendations = []
        
        for category, data in progression_data.items():
            if data['completion_rate'] < 50:
                recommendations.append(f"Consider simplifying {category} content - low completion rate ({data['completion_rate']:.1f}%)")
            
            if data['difficulty_analysis']['success_rate'] < 40:
                recommendations.append(f"Review {category} difficulty - success rate is only {data['difficulty_analysis']['success_rate']:.1f}%")
        
        if not recommendations:
            recommendations.append("Learning paths are performing well! Consider adding more advanced content.")
        
        return recommendations
    
    # Additional helper methods for comparative analysis
    def _generate_category_insights(self, category_stats: Dict) -> List[str]:
        """Generate insights from category comparison"""
        insights = []
        
        if category_stats:
            best_category = max(category_stats.items(), key=lambda x: x[1]['average_score'])
            worst_category = min(category_stats.items(), key=lambda x: x[1]['average_score'])
            
            insights.append(f"Best performing category: {best_category[0]} (avg: {best_category[1]['average_score']:.1f})")
            insights.append(f"Needs attention: {worst_category[0]} (avg: {worst_category[1]['average_score']:.1f})")
            
            # Find most popular category
            most_popular = max(category_stats.items(), key=lambda x: x[1]['total_attempts'])
            insights.append(f"Most popular: {most_popular[0]} ({most_popular[1]['total_attempts']} attempts)")
        
        return insights
    
    def _generate_category_recommendations(self, category_stats: Dict) -> List[str]:
        """Generate recommendations based on category analysis"""
        recommendations = []
        
        for category, stats in category_stats.items():
            if stats['success_rate'] < 50:
                recommendations.append(f"Consider revising {category} content or adding more practice materials")
            elif stats['success_rate'] > 90:
                recommendations.append(f"{category} might be too easy - consider adding advanced challenges")
        
        return recommendations
    
    def _calculate_period_stats(self, scores: List[Score]) -> Dict[str, float]:
        """Calculate statistics for a time period"""
        if not scores:
            return {'total_attempts': 0, 'average_score': 0, 'unique_users': 0}
        
        score_values = [s.score for s in scores]
        
        return {
            'total_attempts': len(scores),
            'average_score': round(sum(score_values) / len(score_values), 2),
            'unique_users': len(set(s.user_id for s in scores)),
            'success_rate': round(len([s for s in score_values if s >= 70]) / len(score_values) * 100, 2)
        }
    
    def _analyze_trends(self, current_scores: List[Score], previous_scores: List[Score]) -> Dict[str, str]:
        """Analyze trends between periods"""
        trends = {}
        
        if len(current_scores) > len(previous_scores):
            trends['activity'] = 'increasing'
        elif len(current_scores) < len(previous_scores):
            trends['activity'] = 'decreasing'
        else:
            trends['activity'] = 'stable'
        
        if current_scores and previous_scores:
            current_avg = sum(s.score for s in current_scores) / len(current_scores)
            previous_avg = sum(s.score for s in previous_scores) / len(previous_scores)
            
            if current_avg > previous_avg:
                trends['performance'] = 'improving'
            elif current_avg < previous_avg:
                trends['performance'] = 'declining'
            else:
                trends['performance'] = 'stable'
        else:
            trends['performance'] = 'insufficient_data'
        
        return trends
    
    # Real-time monitoring helper methods
    def _count_active_sessions(self) -> int:
        """Count currently active sessions (simplified)"""
        # In a real implementation, you'd track actual sessions
        recent_activity = Score.query.filter(
            Score.date_attempted >= datetime.now() - timedelta(minutes=30)
        ).with_entities(Score.user_id).distinct().count()
        
        return recent_activity
    
    def _get_hourly_activity(self) -> Dict[int, int]:
        """Get activity count for each hour of the day"""
        hourly_counts = {}
        today = datetime.now().date()
        
        for hour in range(24):
            count = Score.query.filter(
                and_(
                    func.date(Score.date_attempted) == today,
                    extract('hour', Score.date_attempted) == hour
                )
            ).count()
            hourly_counts[hour] = count
        
        return hourly_counts
    
    def _calculate_system_load(self) -> Dict[str, Any]:
        """Calculate current system load metrics"""
        total_scores = Score.query.count()
        total_users = User.query.count()
        
        return {
            'total_data_points': total_scores,
            'user_load': total_users,
            'avg_scores_per_user': round(total_scores / total_users, 2) if total_users else 0,
            'status': 'normal'  # Simplified status
        }
    
    def _get_performance_alerts(self) -> List[Dict[str, str]]:
        """Get current performance alerts"""
        alerts = []
        
        # Check for recent low scores
        recent_low_scores = Score.query.filter(
            and_(
                Score.date_attempted >= datetime.now() - timedelta(hours=24),
                Score.score < 40
            )
        ).count()
        
        if recent_low_scores > 10:
            alerts.append({
                'type': 'warning',
                'message': f'{recent_low_scores} low scores in the last 24 hours',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        
        return alerts
    
    def _get_real_time_leaderboard(self) -> List[Dict[str, Any]]:
        """Get current top performers"""
        top_scores = db.session.query(
            Score.user_id,
            User.username,
            func.max(Score.score).label('highest_score'),
            func.count(Score.id).label('total_attempts')
        ).join(User).group_by(Score.user_id, User.username)\
         .order_by(desc(func.max(Score.score))).limit(5).all()
        
        leaderboard = []
        for rank, (user_id, username, highest_score, total_attempts) in enumerate(top_scores, 1):
            leaderboard.append({
                'rank': rank,
                'username': username,
                'highest_score': highest_score,
                'total_attempts': total_attempts
            })
        
        return leaderboard
    
    def _get_category_activity(self, since: datetime) -> Dict[str, int]:
        """Get activity count per category since a given time"""
        activity = {}
        
        for category in self.categories:
            count = Score.query.filter(
                and_(Score.category == category, Score.date_attempted >= since)
            ).count()
            activity[category] = count
        
        return activity
    
    def _calculate_difficulty_rating(self, score_values: List[float]) -> str:
        """Calculate difficulty rating based on scores"""
        if not score_values:
            return 'unknown'
        
        avg_score = sum(score_values) / len(score_values)
        
        if avg_score >= 80:
            return 'easy'
        elif avg_score >= 60:
            return 'medium'
        else:
            return 'hard'
    
    def _calculate_category_engagement(self, scores: List[Score]) -> str:
        """Calculate engagement level for a category"""
        if not scores:
            return 'low'
        
        # Simple engagement based on number of attempts and unique users
        unique_users = len(set(s.user_id for s in scores))
        avg_attempts_per_user = len(scores) / unique_users if unique_users else 0
        
        if avg_attempts_per_user >= 5:
            return 'high'
        elif avg_attempts_per_user >= 3:
            return 'medium'
        else:
            return 'low'

    # ==================== HELPER METHODS ====================
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as 'time ago' string"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    
    def _empty_performance_analytics(self) -> Dict[str, Any]:
        """Return empty performance analytics structure"""
        return {
            'total_attempts': 0,
            'average_score': 0,
            'median_score': 0,
            'highest_score': 0,
            'lowest_score': 0,
            'score_distribution': {'very_low': 0, 'low': 0, 'medium': 0, 'high': 0, 'very_high': 0},
            'improvement_trend': 'no_data',
            'category_breakdown': {},
            'time_analysis': {},
            'student_rankings': [],
            'completion_rates': {},
            'engagement_metrics': {}
        }
    
    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median of a list of values"""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def _get_score_distribution(self, score_values: List[float]) -> Dict[str, int]:
        """Calculate score distribution buckets"""
        if not score_values:
            return {'very_low': 0, 'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}
        
        # Convert to percentages using standardized method
        percentages = [self._convert_score_to_percentage(s) for s in score_values]
        
        distribution = {'very_low': 0, 'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}
        
        for percentage in percentages:
            if percentage <= 20:
                distribution['very_low'] += 1
            elif percentage <= 40:
                distribution['low'] += 1
            elif percentage <= 60:
                distribution['medium'] += 1
            elif percentage <= 80:
                distribution['high'] += 1
            else:
                distribution['very_high'] += 1
        
        return distribution
    
    def _calculate_improvement_trend(self, scores: List[Score]) -> str:
        """Calculate whether scores are improving, declining, or stable"""
        if len(scores) < 2:
            return 'no_data'
        
        # Sort by date
        sorted_scores = sorted(scores, key=lambda s: s.date_attempted)
        
        # Compare first half with second half
        mid_point = len(sorted_scores) // 2
        first_half_avg = sum(s.score for s in sorted_scores[:mid_point]) / mid_point
        second_half_avg = sum(s.score for s in sorted_scores[mid_point:]) / (len(sorted_scores) - mid_point)
        
        if second_half_avg > first_half_avg * 1.05:  # 5% improvement threshold
            return 'improving'
        elif second_half_avg < first_half_avg * 0.95:  # 5% decline threshold
            return 'declining'
        else:
            return 'stable'
    
    def _get_category_breakdown(self, scores: List[Score]) -> Dict[str, Dict]:
        """Get performance breakdown by category"""
        category_data = defaultdict(list)
        
        for score in scores:
            category_data[score.category].append(score.score)
        
        breakdown = {}
        for category, score_list in category_data.items():
            if score_list:
                breakdown[category] = {
                    'count': len(score_list),
                    'average': round(sum(score_list) / len(score_list), 2),
                    'highest': max(score_list),
                    'lowest': min(score_list)
                }
        
        return breakdown
    
    def _get_time_analysis(self, scores: List[Score]) -> Dict[str, Any]:
        """Analyze performance by time patterns"""
        if not scores:
            return {}
        
        # Group by hour of day
        hour_data = defaultdict(list)
        day_data = defaultdict(list)
        
        for score in scores:
            hour_data[score.date_attempted.hour].append(score.score)
            day_data[score.date_attempted.weekday()].append(score.score)
        
        # Find best performing hours and days
        best_hour = max(hour_data.keys(), key=lambda h: sum(hour_data[h]) / len(hour_data[h])) if hour_data else None
        best_day = max(day_data.keys(), key=lambda d: sum(day_data[d]) / len(day_data[d])) if day_data else None
        
        return {
            'best_performance_hour': best_hour,
            'best_performance_day': best_day,
            'hour_distribution': {h: len(scores) for h, scores in hour_data.items()},
            'day_distribution': {d: len(scores) for d, scores in day_data.items()}
        }
    
    def _get_student_rankings(self, scores: List[Score]) -> List[Dict]:
        """Get top performing students"""
        user_scores = defaultdict(list)
        
        for score in scores:
            user_scores[score.user_id].append(score.score)
        
        rankings = []
        for user_id, score_list in user_scores.items():
            try:
                user = User.query.get(user_id)
                username = user.username if user else f"User {user_id}"
            except:
                username = f"User {user_id}"
            
            rankings.append({
                'user_id': user_id,
                'username': username,
                'average_score': round(sum(score_list) / len(score_list), 2),
                'total_attempts': len(score_list),
                'highest_score': max(score_list)
            })
        
        return sorted(rankings, key=lambda x: x['average_score'], reverse=True)[:10]
    
    def _get_completion_rates(self, date_range: int) -> Dict[str, float]:
        """Calculate completion rates for different categories"""
        completion_rates = {}
        
        for category in self.categories:
            # This is simplified - in a real system, you'd track attempted vs completed
            scores = Score.query.filter(
                and_(
                    Score.category == category,
                    Score.date_attempted >= datetime.now() - timedelta(days=date_range)
                )
            ).all()
            
            # Assume completion if score is above minimum threshold
            completed = len([s for s in scores if s.score >= 1.0])  # Assuming 1.0 is minimum passing
            total = len(scores)
            
            completion_rates[category] = round((completed / total * 100), 1) if total > 0 else 0
        
        return completion_rates
    
    def _get_engagement_metrics(self, scores: List[Score], date_range: int) -> Dict[str, Any]:
        """Calculate engagement metrics from scores data"""
        if not scores:
            return {'total_active_users': 0, 'average_session_length': 0, 'retention_rate': 0}
        
        unique_users = len(set(s.user_id for s in scores))
        total_attempts = len(scores)
        
        return {
            'total_active_users': unique_users,
            'average_attempts_per_user': round(total_attempts / unique_users, 2) if unique_users > 0 else 0,
            'engagement_score': min(100, (total_attempts / max(1, unique_users)) * 10)  # Simplified engagement score
        }
    
    def _get_daily_engagement(self, start_date: datetime) -> Dict[str, int]:
        """Get daily engagement metrics"""
        daily_users = defaultdict(set)
        
        scores = Score.query.filter(Score.date_attempted >= start_date).all()
        
        for score in scores:
            date_key = score.date_attempted.strftime('%Y-%m-%d')
            daily_users[date_key].add(score.user_id)
        
        return {date: len(users) for date, users in daily_users.items()}
    
    def _analyze_session_patterns(self, start_date: datetime) -> Dict[str, Any]:
        """Analyze user session patterns"""
        # This is simplified - in a real implementation, you'd track actual sessions
        scores = Score.query.filter(Score.date_attempted >= start_date).all()
        
        user_sessions = defaultdict(list)
        for score in scores:
            user_sessions[score.user_id].append(score.date_attempted)
        
        avg_session_length = 0  # Placeholder - would need actual session tracking
        total_sessions = len(user_sessions)
        
        return {
            'average_session_length': avg_session_length,
            'total_sessions': total_sessions,
            'average_sessions_per_user': round(total_sessions / len(user_sessions), 2) if user_sessions else 0
        }
    
    def _analyze_category_preferences(self, start_date: datetime) -> Dict[str, int]:
        """Analyze which categories users prefer"""
        category_counts = defaultdict(int)
        
        scores = Score.query.filter(Score.date_attempted >= start_date).all()
        
        for score in scores:
            category_counts[score.category] += 1
        
        return dict(category_counts)
    
    def _analyze_activity_patterns(self, start_date: datetime) -> Dict[str, Any]:
        """Analyze when users are most active"""
        scores = Score.query.filter(Score.date_attempted >= start_date).all()
        
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        
        for score in scores:
            hour_counts[score.date_attempted.hour] += 1
            day_counts[score.date_attempted.weekday()] += 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1]) if hour_counts else (0, 0)
        peak_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else (0, 0)
        
        return {
            'peak_hour': peak_hour[0],
            'peak_day': peak_day[0],
            'hourly_distribution': dict(hour_counts),
            'daily_distribution': dict(day_counts)
        }
    
    def _calculate_retention_metrics(self, start_date: datetime) -> Dict[str, float]:
        """Calculate user retention metrics"""
        # This is simplified - would need more sophisticated tracking in practice
        all_users = set()
        returning_users = set()
        
        scores = Score.query.filter(Score.date_attempted >= start_date).all()
        user_dates = defaultdict(list)
        
        for score in scores:
            all_users.add(score.user_id)
            user_dates[score.user_id].append(score.date_attempted.date())
        
        for user_id, dates in user_dates.items():
            if len(set(dates)) > 1:  # User came back on different days
                returning_users.add(user_id)
        
        retention_rate = len(returning_users) / len(all_users) * 100 if all_users else 0
        
        return {
            'retention_rate': round(retention_rate, 1),
            'total_users': len(all_users),
            'returning_users': len(returning_users)
        }
    
    def _calculate_engagement_score(self, daily_engagement: Dict, session_data: Dict) -> float:
        """Calculate overall engagement score"""
        if not daily_engagement or not session_data:
            return 0
        
        # Simple engagement calculation
        avg_daily_users = sum(daily_engagement.values()) / len(daily_engagement) if daily_engagement else 0
        total_sessions = session_data.get('total_sessions', 0)
        
        # Normalized engagement score (0-100)
        engagement = min(100, (avg_daily_users * 10) + (total_sessions * 0.1))
        return round(engagement, 1)
    
    def _calculate_overall_completion_rate(self) -> float:
        """Calculate overall learning path completion rate"""
        # Simplified - would need more sophisticated tracking
        total_scores = Score.query.count()
        passing_scores = Score.query.filter(Score.score >= 2.0).count()  # Assuming 2.0+ is passing
        
        return round((passing_scores / total_scores * 100), 1) if total_scores > 0 else 0
    
    def _calculate_path_effectiveness(self) -> Dict[str, float]:
        """Calculate effectiveness of learning paths"""
        effectiveness = {}
        
        for category in self.categories:
            scores = Score.query.filter(Score.category == category).all()
            if scores:
                avg_score = sum(s.score for s in scores) / len(scores)
                effectiveness[category] = self._convert_score_to_percentage(avg_score)  # Convert to percentage
            else:
                effectiveness[category] = 0
        
        return effectiveness
    
    def _generate_learning_recommendations(self, progression_data: Dict) -> List[str]:
        """Generate learning recommendations based on data"""
        recommendations = []
        
        for category, data in progression_data.items():
            completion_rate = data.get('completion_rate', 0)
            avg_improvement = data.get('average_improvement', 0)
            
            if completion_rate < 50:
                recommendations.append(f"Consider simplifying {category} content - low completion rate ({completion_rate}%)")
            
            if avg_improvement < 0.1:
                recommendations.append(f"Review {category} learning path - students not showing improvement")
        
        return recommendations
    
    def _generate_category_insights(self, category_stats: Dict) -> List[str]:
        """Generate insights from category comparison"""
        insights = []
        
        if not category_stats:
            return insights
        
        # Find best and worst performing categories
        best_category = max(category_stats.keys(), key=lambda c: category_stats[c].get('average_score', 0))
        worst_category = min(category_stats.keys(), key=lambda c: category_stats[c].get('average_score', 0))
        
        insights.append(f"Best performing category: {best_category}")
        insights.append(f"Most challenging category: {worst_category}")
        
        # Find most popular category
        most_popular = max(category_stats.keys(), key=lambda c: category_stats[c].get('total_attempts', 0))
        insights.append(f"Most popular category: {most_popular}")
        
        return insights
    
    def _generate_category_recommendations(self, category_stats: Dict) -> List[str]:
        """Generate recommendations for category improvements"""
        recommendations = []
        
        for category, stats in category_stats.items():
            avg_score = stats.get('average_score', 0)
            engagement = stats.get('engagement_level', 'low')
            
            if avg_score < 50:
                recommendations.append(f"Consider revising {category} content difficulty")
            
            if engagement == 'low':
                recommendations.append(f"Improve engagement for {category} with more interactive elements")
        
        return recommendations
    
    def _calculate_period_stats(self, scores: List[Score]) -> Dict[str, float]:
        """Calculate statistics for a time period"""
        if not scores:
            return {'total_attempts': 0, 'average_score': 0, 'unique_users': 0}
        
        score_values = [s.score for s in scores]
        unique_users = len(set(s.user_id for s in scores))
        
        return {
            'total_attempts': len(scores),
            'average_score': round(sum(score_values) / len(score_values), 2),
            'unique_users': unique_users,
            'highest_score': max(score_values),
            'lowest_score': min(score_values)
        }
    
    def _analyze_trends(self, current_scores: List[Score], previous_scores: List[Score]) -> Dict[str, str]:
        """Analyze trends between two periods"""
        if not current_scores or not previous_scores:
            return {'trend': 'insufficient_data'}
        
        current_avg = sum(s.score for s in current_scores) / len(current_scores)
        previous_avg = sum(s.score for s in previous_scores) / len(previous_scores)
        
        if current_avg > previous_avg * 1.05:
            trend = 'improving'
        elif current_avg < previous_avg * 0.95:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {'trend': trend, 'change_percentage': round(((current_avg - previous_avg) / previous_avg) * 100, 2)}
        try:
            # Get activity by hour of day
            hourly_activity = (
                db.session.query(
                    func.extract('hour', Score.date_attempted).label('hour'),
                    func.count(Score.id).label('activity_count')
                )
                .filter(Score.date_attempted.between(start_date, end_date))
                .group_by(func.extract('hour', Score.date_attempted))
                .all()
            )
            
            # Create hourly data array (24 hours)
            hourly_data = {}
            for activity in hourly_activity:
                hourly_data[int(activity.hour)] = activity.activity_count
            
            return {
                'hourly_activity': hourly_data,
                'peak_hour': max(hourly_data.items(), key=lambda x: x[1])[0] if hourly_data else 12,
                'total_activities': sum(hourly_data.values())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting engagement heatmap data: {str(e)}")
            return {
                'hourly_activity': {},
                'peak_hour': 12,
                'total_activities': 0
            }

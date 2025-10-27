from datetime import datetime, timedelta
import json
from __init__ import db

class ScenarioTimer(db.Model):
    """
    Model for tracking scenario timer data and time-based performance metrics
    """
    __tablename__ = 'scenario_timers'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario_id = db.Column(db.String(100), nullable=False)  # Flexible ID for different scenario types
    scenario_type = db.Column(db.String(50), nullable=False)  # troubleshooting, networking, topology, etc.
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    
    # Timer Configuration
    time_limit_seconds = db.Column(db.Integer, nullable=False)  # Time limit in seconds
    warning_thresholds = db.Column(db.Text, nullable=True)  # JSON: warning levels (e.g., [300, 60] for 5min, 1min warnings)
    
    # Timer State
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    pause_time = db.Column(db.DateTime, nullable=True)
    resume_time = db.Column(db.DateTime, nullable=True)
    elapsed_seconds = db.Column(db.Integer, default=0)
    remaining_seconds = db.Column(db.Integer, nullable=True)
    
    # Status Tracking
    is_active = db.Column(db.Boolean, default=True)
    is_paused = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_expired = db.Column(db.Boolean, default=False)
    auto_submitted = db.Column(db.Boolean, default=False)
    
    # Performance Metrics
    time_efficiency = db.Column(db.Float, default=0.0)  # Percentage of time used effectively
    pressure_score = db.Column(db.Float, default=0.0)  # Performance under time pressure
    completion_percentage = db.Column(db.Float, default=0.0)  # How much was completed when time ended
    final_score = db.Column(db.Integer, default=0)
    time_bonus = db.Column(db.Integer, default=0)
    
    # Collaborative Session
    lobby_id = db.Column(db.String(100), nullable=True)  # For collaborative scenarios
    is_collaborative = db.Column(db.Boolean, default=False)
    sync_enabled = db.Column(db.Boolean, default=True)  # Whether timer syncs across participants
    
    # Metadata
    _warning_events = db.Column('warning_events', db.Text, nullable=True)  # JSON: timestamp of each warning
    _pause_events = db.Column('pause_events', db.Text, nullable=True)  # JSON: pause/resume history
    _timer_extensions = db.Column('timer_extensions', db.Text, nullable=True)  # JSON: any time extensions granted
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('scenario_timers', lazy=True))
    
    @property
    def warning_levels(self):
        """Get warning threshold levels as a list"""
        if not self.warning_thresholds:
            return [300, 60]  # Default: 5 minutes and 1 minute warnings
        try:
            return json.loads(self.warning_thresholds)
        except (ValueError, TypeError):
            return [300, 60]
    
    @warning_levels.setter
    def warning_levels(self, levels):
        """Set warning threshold levels from a list"""
        if isinstance(levels, list):
            self.warning_thresholds = json.dumps(levels)
        else:
            self.warning_thresholds = levels
    
    @property
    def warning_events(self):
        """Get warning events as a list of dictionaries"""
        if not self._warning_events:
            return []
        try:
            return json.loads(self._warning_events)
        except (ValueError, TypeError):
            return []
    
    @warning_events.setter
    def warning_events(self, events):
        """Set warning events from a list of dictionaries"""
        if isinstance(events, list):
            self._warning_events = json.dumps(events)
        else:
            self._warning_events = events
    
    @property
    def pause_events(self):
        """Get pause/resume events as a list of dictionaries"""
        if not self._pause_events:
            return []
        try:
            return json.loads(self._pause_events)
        except (ValueError, TypeError):
            return []
    
    @pause_events.setter
    def pause_events(self, events):
        """Set pause/resume events from a list of dictionaries"""
        if isinstance(events, list):
            self._pause_events = json.dumps(events)
        else:
            self._pause_events = events
    
    @property
    def timer_extensions(self):
        """Get timer extensions as a list of dictionaries"""
        if not self._timer_extensions:
            return []
        try:
            return json.loads(self._timer_extensions)
        except (ValueError, TypeError):
            return []
    
    @timer_extensions.setter
    def timer_extensions(self, extensions):
        """Set timer extensions from a list of dictionaries"""
        if isinstance(extensions, list):
            self._timer_extensions = json.dumps(extensions)
        else:
            self._timer_extensions = extensions
    
    def get_current_remaining_seconds(self):
        """Calculate current remaining seconds based on real-time"""
        if not self.is_active or self.is_completed or self.is_expired:
            return 0
        
        if self.is_paused:
            return self.remaining_seconds or 0
        
        current_time = datetime.utcnow()
        elapsed = (current_time - self.start_time).total_seconds()
        
        # Account for pause time
        total_pause_duration = self.get_total_pause_duration()
        effective_elapsed = elapsed - total_pause_duration
        
        remaining = self.time_limit_seconds - effective_elapsed
        return max(0, int(remaining))
    
    def get_total_pause_duration(self):
        """Calculate total time spent paused"""
        pause_events = self.pause_events
        total_pause = 0
        
        current_pause_start = None
        for event in pause_events:
            if event['action'] == 'pause':
                current_pause_start = datetime.fromisoformat(event['timestamp'])
            elif event['action'] == 'resume' and current_pause_start:
                resume_time = datetime.fromisoformat(event['timestamp'])
                total_pause += (resume_time - current_pause_start).total_seconds()
                current_pause_start = None
        
        # Account for current pause if still paused
        if self.is_paused and current_pause_start:
            total_pause += (datetime.utcnow() - current_pause_start).total_seconds()
        elif self.is_paused and self.pause_time:
            total_pause += (datetime.utcnow() - self.pause_time).total_seconds()
        
        return total_pause
    
    def add_warning_event(self, warning_type, remaining_seconds):
        """Add a warning event to the timer"""
        events = self.warning_events
        events.append({
            'type': warning_type,
            'remaining_seconds': remaining_seconds,
            'timestamp': datetime.utcnow().isoformat(),
            'message': self.get_warning_message(warning_type, remaining_seconds)
        })
        self.warning_events = events
    
    def add_pause_event(self, action, reason=None):
        """Add a pause/resume event to the timer"""
        events = self.pause_events
        events.append({
            'action': action,  # 'pause' or 'resume'
            'timestamp': datetime.utcnow().isoformat(),
            'reason': reason
        })
        self.pause_events = events
    
    def add_timer_extension(self, additional_seconds, reason, granted_by=None):
        """Add time extension to the timer"""
        extensions = self.timer_extensions
        extensions.append({
            'additional_seconds': additional_seconds,
            'reason': reason,
            'granted_by': granted_by,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.timer_extensions = extensions
        
        # Update time limit
        self.time_limit_seconds += additional_seconds
    
    def get_warning_message(self, warning_type, remaining_seconds):
        """Get appropriate warning message for time remaining"""
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        
        if remaining_seconds <= 60:
            return f"[WARNING] Only {remaining_seconds} seconds remaining!"
        elif remaining_seconds <= 300:  # 5 minutes
            return f"[WARNING] {minutes} minutes {seconds} seconds remaining!"
        elif remaining_seconds <= 600:  # 10 minutes
            return f"⏰ {minutes} minutes remaining - consider reviewing your progress"
        else:
            return f"⏱️ {minutes} minutes remaining"
    
    def calculate_time_efficiency(self, actual_progress=None):
        """Calculate time efficiency based on progress vs time used"""
        if not self.end_time or not self.start_time:
            return 0.0
        
        total_time = (self.end_time - self.start_time).total_seconds()
        time_used_percentage = (total_time / self.time_limit_seconds) * 100
        
        if actual_progress is not None:
            # Efficiency = Progress / Time Used
            efficiency = (actual_progress / time_used_percentage) if time_used_percentage > 0 else 0
            return min(100.0, efficiency)
        
        # Default efficiency based on completion
        if self.is_completed:
            return max(0, 100 - time_used_percentage)
        else:
            return max(0, self.completion_percentage - time_used_percentage)
    
    def calculate_pressure_score(self):
        """Calculate performance under time pressure"""
        if not self.final_score:
            return 0.0
        
        # Higher scores with less time used = better pressure performance
        time_used_percentage = self.elapsed_seconds / self.time_limit_seconds
        pressure_factor = 1 - time_used_percentage
        
        # Normalize score (assuming max score of 100)
        normalized_score = self.final_score / 100.0
        
        return min(100.0, normalized_score * pressure_factor * 100)
    
    def to_dict(self):
        """Convert timer to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scenario_id': self.scenario_id,
            'scenario_type': self.scenario_type,
            'difficulty': self.difficulty,
            'time_limit_seconds': self.time_limit_seconds,
            'warning_levels': self.warning_levels,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'elapsed_seconds': self.elapsed_seconds,
            'remaining_seconds': self.get_current_remaining_seconds(),
            'is_active': self.is_active,
            'is_paused': self.is_paused,
            'is_completed': self.is_completed,
            'is_expired': self.is_expired,
            'auto_submitted': self.auto_submitted,
            'time_efficiency': self.time_efficiency,
            'pressure_score': self.pressure_score,
            'completion_percentage': self.completion_percentage,
            'final_score': self.final_score,
            'time_bonus': self.time_bonus,
            'lobby_id': self.lobby_id,
            'is_collaborative': self.is_collaborative,
            'sync_enabled': self.sync_enabled,
            'warning_events': self.warning_events,
            'pause_events': self.pause_events,
            'timer_extensions': self.timer_extensions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def create_timer(cls, user_id, scenario_id, scenario_type, difficulty, 
                    time_limit_minutes=None, lobby_id=None, is_collaborative=False):
        """Create a new scenario timer with appropriate time limits"""
        
        # Default time limits by difficulty
        default_time_limits = {
            'easy': 15,      # 15 minutes
            'medium': 30,    # 30 minutes  
            'hard': 45       # 45 minutes
        }
        
        if time_limit_minutes is None:
            time_limit_minutes = default_time_limits.get(difficulty, 30)
        
        time_limit_seconds = time_limit_minutes * 60
        
        # Set warning thresholds based on time limit
        if time_limit_seconds <= 600:  # 10 minutes or less
            warning_levels = [300, 60]  # 5 min, 1 min
        elif time_limit_seconds <= 1800:  # 30 minutes or less
            warning_levels = [600, 300, 60]  # 10 min, 5 min, 1 min
        else:  # More than 30 minutes
            warning_levels = [900, 600, 300, 60]  # 15 min, 10 min, 5 min, 1 min
        
        timer = cls(
            user_id=user_id,
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            difficulty=difficulty,
            time_limit_seconds=time_limit_seconds,
            remaining_seconds=time_limit_seconds,
            lobby_id=lobby_id,
            is_collaborative=is_collaborative,
            sync_enabled=is_collaborative
        )
        
        timer.warning_levels = warning_levels
        
        return timer

    @classmethod
    def get_active_timer(cls, user_id, scenario_id=None):
        """Get the active timer for a user and scenario"""
        query = cls.query.filter_by(
            user_id=user_id,
            is_active=True,
            is_completed=False,
            is_expired=False
        )
        
        if scenario_id:
            query = query.filter_by(scenario_id=scenario_id)
        
        return query.first()

    @classmethod
    def get_user_timer_stats(cls, user_id, scenario_type=None):
        """Get comprehensive timer statistics for a user"""
        query = cls.query.filter_by(user_id=user_id, is_completed=True)
        
        if scenario_type:
            query = query.filter_by(scenario_type=scenario_type)
        
        timers = query.all()
        
        if not timers:
            return {
                'total_scenarios': 0,
                'average_completion_time': 0,
                'best_time_efficiency': 0,
                'average_pressure_score': 0,
                'scenarios_auto_submitted': 0,
                'total_time_bonuses': 0
            }
        
        total_scenarios = len(timers)
        total_time = sum(t.elapsed_seconds for t in timers)
        total_efficiency = sum(t.time_efficiency for t in timers)
        total_pressure = sum(t.pressure_score for t in timers)
        auto_submitted = sum(1 for t in timers if t.auto_submitted)
        total_bonuses = sum(t.time_bonus for t in timers)
        
        return {
            'total_scenarios': total_scenarios,
            'average_completion_time': total_time / total_scenarios,
            'best_time_efficiency': max(t.time_efficiency for t in timers),
            'average_pressure_score': total_pressure / total_scenarios,
            'scenarios_auto_submitted': auto_submitted,
            'total_time_bonuses': total_bonuses,
            'completion_rate': len([t for t in timers if not t.auto_submitted]) / total_scenarios * 100
        }

from datetime import datetime
import json
from __init__ import db

class Topology(db.Model):
    """
    Model for network topology challenges
    """
    __tablename__ = 'topologies'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # 'easy', 'medium', 'hard'
    topology_type = db.Column(db.String(50), default='point-to-point')  # 'point-to-point', 'mesh', 'star', etc.
    _initial_config = db.Column('initial_config', db.Text, nullable=True)  # JSON string
    _expected_config = db.Column('expected_config', db.Text, nullable=False)  # JSON string
    _scoring_metrics = db.Column('scoring_metrics', db.Text, nullable=True)  # JSON string for scoring metrics
    _device_requirements = db.Column('device_requirements', db.Text, nullable=True)  # JSON string for required devices
    base_score = db.Column(db.Integer, default=10)  # Base points for completing
    time_bonus = db.Column(db.Integer, default=0)  # Additional points for completing quickly
    perfect_match_bonus = db.Column(db.Integer, default=5)  # Bonus for exact match with expected solution
    time_limit = db.Column(db.Integer, default=300)  # Time limit in seconds (default 5 minutes)
    
    # Gamified features
    _tutorial_steps = db.Column('tutorial_steps', db.Text, nullable=True)  # JSON array of tutorial steps
    _hints = db.Column('hints', db.Text, nullable=True)  # JSON array of hints
    unlock_requirement = db.Column(db.String(100), nullable=True)  # Required achievement to unlock
    prerequisite_topology_id = db.Column(db.Integer, db.ForeignKey('topologies.id'), nullable=True)  # Previous topology required
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prerequisite_topology = db.relationship('Topology', remote_side=[id], backref='unlocks')

    @property
    def tutorial_steps(self):
        """Get tutorial steps as a Python list"""
        if not self._tutorial_steps:
            return []
        try:
            return json.loads(self._tutorial_steps)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @tutorial_steps.setter
    def tutorial_steps(self, steps):
        """Set tutorial steps from a Python list"""
        try:
            if isinstance(steps, list):
                self._tutorial_steps = json.dumps(steps)
            else:
                self._tutorial_steps = steps
        except Exception as e:
            print(f"Error setting tutorial_steps: {str(e)}")
            raise ValueError(f"Invalid tutorial_steps format: {str(e)}")
    
    @property
    def hints(self):
        """Get hints as a Python list"""
        if not self._hints:
            return []
        try:
            return json.loads(self._hints)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @hints.setter
    def hints(self, hint_list):
        """Set hints from a Python list"""
        try:
            if isinstance(hint_list, list):
                self._hints = json.dumps(hint_list)
            else:
                self._hints = hint_list
        except Exception as e:
            print(f"Error setting hints: {str(e)}")
            raise ValueError(f"Invalid hints format: {str(e)}")

    @property
    def initial_config(self):
        """Get the initial configuration as a Python object"""
        if not self._initial_config:
            return {"devices": [], "connections": []}
        return json.loads(self._initial_config)
        
    @initial_config.setter
    def initial_config(self, config):
        """Set the initial configuration from a Python object"""
        try:
            if isinstance(config, dict):
                self._initial_config = json.dumps(config)
            else:
                self._initial_config = config
        except Exception as e:
            print(f"Error setting initial_config: {str(e)}")
            raise ValueError(f"Invalid initial_config format: {str(e)}")
            
    @property
    def expected_config(self):
        """Get the expected configuration as a Python object"""
        if not self._expected_config:
            return {"devices": [], "connections": []}
        return json.loads(self._expected_config)
        
    @expected_config.setter
    def expected_config(self, config):
        """Set the expected configuration from a Python object"""
        try:
            if isinstance(config, dict):
                self._expected_config = json.dumps(config)
            else:
                self._expected_config = config
        except Exception as e:
            print(f"Error setting expected_config: {str(e)}")
            raise ValueError(f"Invalid expected_config format: {str(e)}")
            
    @property
    def scoring_metrics(self):
        """Get the scoring metrics as a Python object"""
        if not self._scoring_metrics:
            return {
                "time_efficiency": 20,
                "config_process": 20,
                "design_layout": 20,
                "completeness": 20,
                "correctness": 20
            }
        return json.loads(self._scoring_metrics)
        
    @scoring_metrics.setter
    def scoring_metrics(self, metrics):
        """Set the scoring metrics from a Python object"""
        try:
            if isinstance(metrics, dict):
                self._scoring_metrics = json.dumps(metrics)
            else:
                self._scoring_metrics = metrics
        except Exception as e:
            print(f"Error setting scoring_metrics: {str(e)}")
            raise ValueError(f"Invalid scoring_metrics format: {str(e)}")
            
    @property
    def device_requirements(self):
        """Get the device requirements as a Python object"""
        if not self._device_requirements:
            return {
                "pc": 0,
                "router": 0,
                "switch": 0
            }
        return json.loads(self._device_requirements)
        
    @device_requirements.setter
    def device_requirements(self, requirements):
        """Set the device requirements from a Python object"""
        try:
            if isinstance(requirements, dict):
                self._device_requirements = json.dumps(requirements)
            else:
                self._device_requirements = requirements
        except Exception as e:
            print(f"Error setting device_requirements: {str(e)}")
            raise ValueError(f"Invalid device_requirements format: {str(e)}")
            
    def get_initial_config(self):
        """Get the initial configuration as a Python object"""
        return self.initial_config
        
    def get_expected_config(self):
        """Get the expected configuration as a Python object"""
        return self.expected_config
        
    def to_dict(self):
        """Convert the model to a dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'topology_type': self.topology_type,
            'initial_config': self.initial_config,
            'expected_config': self.expected_config,
            'scoring_metrics': self.scoring_metrics,
            'device_requirements': self.device_requirements,
            'base_score': self.base_score,
            'time_bonus': self.time_bonus,
            'perfect_match_bonus': self.perfect_match_bonus,
            'time_limit': self.time_limit,
            'tutorial_steps': self.tutorial_steps,
            'hints': self.hints,
            'unlock_requirement': self.unlock_requirement,
            'prerequisite_topology_id': self.prerequisite_topology_id,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
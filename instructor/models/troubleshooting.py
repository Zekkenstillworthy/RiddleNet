from datetime import datetime
import json
from __init__ import db

class Troubleshooting(db.Model):
    """
    Model for troubleshooting scenarios in the admin panel
    """
    __tablename__ = 'troubleshootings'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    scenario = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    problem_type = db.Column(db.String(50), default='network')  # network, passive, version, etc.
    _hints = db.Column('hints', db.Text, nullable=True)  # JSON string
    _scoring_metrics = db.Column('scoring_metrics', db.Text, nullable=True)  # JSON string for custom scoring
    _initial_topology = db.Column('initial_topology', db.Text, nullable=True)  # JSON string for initial device setup
    _solution_topology = db.Column('solution_topology', db.Text, nullable=True)  # JSON string for solution topology
    _required_steps = db.Column('required_steps', db.Text, nullable=True)  # JSON string for required task steps
    time_limit = db.Column(db.Integer, default=15)  # Time limit in minutes
    base_score = db.Column(db.Integer, default=10)  # Default base score
    time_bonus = db.Column(db.Integer, default=5)  # Default time bonus
    solution_bonus = db.Column(db.Integer, default=5)  # Default bonus for perfect solution
    _required_devices = db.Column('required_devices', db.Text, nullable=True)  # JSON string
    _topology_config = db.Column('topology_config', db.Text, nullable=True)  # JSON string for network topology
    _expected_topology = db.Column('expected_topology', db.Text, nullable=True)  # JSON string for expected solution
    _tasks = db.Column('tasks', db.Text, nullable=True)  # JSON string for required tasks
    perfect_match_bonus = db.Column(db.Integer, default=10)
    topology_type = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def hints(self):
        """Get the hints as a list of strings"""
        if not self._hints:
            return []
        try:
            return json.loads(self._hints)
        except (ValueError, TypeError):
            return []

    @hints.setter
    def hints(self, hints_list):
        """Set the hints from a list of strings"""
        if isinstance(hints_list, list):
            self._hints = json.dumps(hints_list)
        else:
            self._hints = hints_list
            
    @property
    def scoring_metrics(self):
        """Get the scoring metrics as a dictionary"""
        if not self._scoring_metrics:
            return {
                "base_score": self.base_score,
                "time_bonus": self.time_bonus,
                "solution_bonus": self.solution_bonus,
                "hint_penalty": 1  # Default penalty for using a hint
            }
        try:
            return json.loads(self._scoring_metrics)
        except (ValueError, TypeError):
            return {
                "base_score": self.base_score,
                "time_bonus": self.time_bonus,
                "solution_bonus": self.solution_bonus,
                "hint_penalty": 1
            }
    
    @scoring_metrics.setter
    def scoring_metrics(self, metrics):
        """Set the scoring metrics from a dictionary"""
        if isinstance(metrics, dict):
            self._scoring_metrics = json.dumps(metrics)
        else:
            self._scoring_metrics = metrics
            
    @property
    def initial_topology(self):
        """Get the initial topology as a dictionary"""
        if not self._initial_topology:
            return {"devices": [], "connections": []}
        try:
            return json.loads(self._initial_topology)
        except (ValueError, TypeError):
            return {"devices": [], "connections": []}
    
    @initial_topology.setter
    def initial_topology(self, topology):
        """Set the initial topology from a dictionary"""
        if isinstance(topology, dict):
            self._initial_topology = json.dumps(topology)
        else:
            self._initial_topology = topology
            
    @property
    def solution_topology(self):
        """Get the solution topology as a dictionary"""
        if not self._solution_topology:
            return {"devices": [], "connections": []}
        try:
            return json.loads(self._solution_topology)
        except (ValueError, TypeError):
            return {"devices": [], "connections": []}
            
    @solution_topology.setter
    def solution_topology(self, topology):
        """Set the solution topology from a dictionary"""
        if isinstance(topology, dict):
            self._solution_topology = json.dumps(topology)
        else:
            self._solution_topology = topology
            
    @property
    def required_steps(self):
        """Get the required steps as a list of dictionaries"""
        if not self._required_steps:
            return []
        try:
            return json.loads(self._required_steps)
        except (ValueError, TypeError):
            return []
    
    @required_steps.setter
    def required_steps(self, steps):
        """Set the required steps from a list of dictionaries"""
        if isinstance(steps, list):
            self._required_steps = json.dumps(steps)
        else:
            self._required_steps = steps

    @property
    def required_devices(self):
        """Get the required devices as a dictionary"""
        if not self._required_devices:
            return {}
        try:
            return json.loads(self._required_devices)
        except (ValueError, TypeError):
            return {}

    @required_devices.setter
    def required_devices(self, devices_dict):
        """Set the required devices from a dictionary"""
        if isinstance(devices_dict, dict):
            self._required_devices = json.dumps(devices_dict)
        else:
            self._required_devices = devices_dict
            
    @property
    def topology_config(self):
        """Get the topology configuration as a dictionary"""
        if not self._topology_config:
            return {}
        try:
            return json.loads(self._topology_config)
        except (ValueError, TypeError):
            return {}

    @topology_config.setter
    def topology_config(self, config_dict):
        """Set the topology configuration from a dictionary"""
        if isinstance(config_dict, dict):
            self._topology_config = json.dumps(config_dict)
        else:
            self._topology_config = config_dict
            
    @property
    def expected_topology(self):
        """Get the expected topology as a dictionary"""
        if not self._expected_topology:
            return {}
        try:
            return json.loads(self._expected_topology)
        except (ValueError, TypeError):
            return {}

    @expected_topology.setter
    def expected_topology(self, topology_dict):
        """Set the expected topology from a dictionary"""
        if isinstance(topology_dict, dict):
            self._expected_topology = json.dumps(topology_dict)
        else:
            self._expected_topology = topology_dict
            
    @property
    def tasks(self):
        """Get the tasks list as a list of dictionaries"""
        if not self._tasks:
            return []
        try:
            return json.loads(self._tasks)
        except (ValueError, TypeError):
            return []
            
    @tasks.setter
    def tasks(self, tasks_list):
        """Set the tasks from a list of dictionaries"""
        if isinstance(tasks_list, list):
            self._tasks = json.dumps(tasks_list)
        else:
            self._tasks = tasks_list
            
    def to_dict(self):
        """Convert the model to a dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'problem_type': self.problem_type,
            'scenario': self.scenario,
            'solution': self.solution,
            'hints': self.hints,
            'scoring_metrics': self.scoring_metrics,
            'initial_topology': self.initial_topology,
            'solution_topology': self.solution_topology,
            'required_steps': self.required_steps,
            'time_limit': self.time_limit,
            'base_score': self.base_score,
            'time_bonus': self.time_bonus,
            'solution_bonus': self.solution_bonus,
            'required_devices': self.required_devices,
            'topology_config': self.topology_config,
            'expected_topology': self.expected_topology,
            'tasks': self.tasks,
            'perfect_match_bonus': self.perfect_match_bonus,
            'topology_type': self.topology_type,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

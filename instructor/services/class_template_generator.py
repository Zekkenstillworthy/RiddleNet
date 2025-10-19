"""
Dynamic Class Template Generation Service

This service automatically creates HTML templates and backend routes
for each classroom based on the class configuration.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import current_app
from instructor.models.class_model import Class
from instructor.models.question_group import QuestionGroup
from __init__ import db


class ClassTemplateGenerator:
    """Service for generating dynamic class templates and routes"""
    
    def __init__(self):
        try:
            from flask import current_app
            self.templates_dir = os.path.join(current_app.root_path, 'templates', 'user', 'classes')
            self.routes_dir = os.path.join(current_app.root_path, 'user', 'routes', 'generated')
            self.ensure_directories()
        except RuntimeError:
            # Handle case where no app context is available
            self.templates_dir = None
            self.routes_dir = None
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        if self.templates_dir and self.routes_dir:
            os.makedirs(self.templates_dir, exist_ok=True)
            os.makedirs(self.routes_dir, exist_ok=True)
    
    def _ensure_app_context_directories(self):
        """Initialize directories when in app context"""
        if not self.templates_dir or not self.routes_dir:
            from flask import current_app
            self.templates_dir = os.path.join(current_app.root_path, 'templates', 'user', 'classes')
            self.routes_dir = os.path.join(current_app.root_path, 'user', 'routes', 'generated')
            self.ensure_directories()
    
    def generate_class_template(self, class_obj: Class) -> str:
        """
        DEPRECATED: Template generation disabled - using universal dynamic template
        All classes now use the single dynamic_class_universal.html template
        """
        print(f"⚠️ Template generation disabled: Class {class_obj.name} will use universal dynamic template")
        return "dynamic_class_universal.html"
    
    def generate_class_routes(self, class_obj: Class) -> str:
        """
        DEPRECATED: Route generation disabled - using universal route handler
        All classes now use the universal_class_routes.py handler
        """
        print(f"⚠️ Route generation disabled: Class {class_obj.name} will use universal route handler")
        return "universal_class_routes.py"
    
    def _prepare_template_data(self, class_obj: Class) -> Dict[str, Any]:
        """Prepare data for template generation"""
        # Get Quiz and their details
        question_groups = []
        for qg in class_obj.question_groups:
            questions = []
            if hasattr(qg, 'questions'):
                for q in qg.questions:
                    questions.append({
                        'id': q.id,
                        'question': q.question,
                        'type': getattr(q, 'type', 'multiple_choice'),
                        'options': getattr(q, 'options', []),
                        'correct_answer': getattr(q, 'correct_answer', ''),
                        'difficulty': getattr(q, 'difficulty', 'medium'),
                        'category': getattr(q, 'category', 'general')
                    })
            
            question_groups.append({
                'id': qg.id,
                'name': qg.name,
                'description': qg.description,
                'category': qg.category,
                'questions': questions
            })
        
        return {
            'class_id': class_obj.id,
            'class_name': class_obj.name,
            'class_code': class_obj.code,
            'class_section': class_obj.section,
            'class_description': class_obj.description,
            'question_groups': question_groups,
            'modules': self._extract_modules_from_groups(question_groups),
            'simulations': self._generate_simulations_config(class_obj),
            'learning_paths': self._generate_learning_paths(class_obj)
        }
    
    def _prepare_routes_data(self, class_obj: Class) -> Dict[str, Any]:
        """Prepare data for routes generation"""
        return {
            'class_id': class_obj.id,
            'class_name': class_obj.name,
            'class_code': class_obj.code.lower().replace(' ', '_'),
            'blueprint_name': f"class_{class_obj.id}",
            'url_prefix': f"/class/{class_obj.id}",
            'question_groups': [qg.id for qg in class_obj.question_groups],
            'modules': self._extract_modules_from_groups([
                {'id': qg.id, 'name': qg.name, 'category': qg.category} 
                for qg in class_obj.question_groups
            ])
        }
    
    def _extract_modules_from_groups(self, question_groups: List[Dict]) -> List[Dict]:
        """Extract module structure from Quiz"""
        modules = {}
        
        for qg in question_groups:
            category = qg.get('category', 'general')
            
            if category not in modules:
                modules[category] = {
                    'name': category.title(),
                    'lessons': [],
                    'simulations': [],
                    'assessments': []
                }
            
            # Add lessons based on Quiz
            modules[category]['lessons'].append({
                'id': qg['id'],
                'name': qg['name'],
                'description': qg.get('description', ''),
                'questions': qg.get('questions', [])
            })
        
        return list(modules.values())
    
    def _generate_simulations_config(self, class_obj: Class) -> List[Dict]:
        """Generate simulations configuration based on class type"""
        simulations = []
        
        # Determine class type and generate appropriate simulations
        class_name_lower = class_obj.name.lower()
        
        if 'networking' in class_name_lower:
            if '1' in class_name_lower or 'fundamental' in class_name_lower:
                simulations.extend(self._get_networking1_simulations())
            elif '2' in class_name_lower or 'advanced' in class_name_lower:
                simulations.extend(self._get_networking2_simulations())
        elif 'security' in class_name_lower:
            simulations.extend(self._get_security_simulations())
        elif 'programming' in class_name_lower:
            simulations.extend(self._get_programming_simulations())
        
        return simulations
    
    def _generate_learning_paths(self, class_obj: Class) -> List[Dict]:
        """Generate learning paths based on class configuration"""
        paths = []
        
        for i, qg in enumerate(class_obj.question_groups):
            path = {
                'id': f"path_{qg.id}",
                'name': qg.name,
                'description': qg.description,
                'order': i + 1,
                'modules': [
                    {
                        'id': f"module_{qg.id}",
                        'name': qg.name,
                        'type': 'lesson',
                        'content_type': 'questions',
                        'estimated_time': len(getattr(qg, 'questions', [])) * 2  # 2 minutes per question
                    }
                ]
            }
            paths.append(path)
        
        return paths
    
    def _generate_template_content(self, data: Dict[str, Any]) -> str:
        """Generate the actual HTML template content"""
        template = f'''
{{% extends "user/base.html" %}}

{{% block title %}}{data['class_name']} - Learning Portal{{% endblock %}}

{{% block extra_css %}}
<link rel="stylesheet" href="{{{{ url_for('static', filename='css/user/dynamic_class.css') }}}}">
<style>
  :root {{
    --class-primary: #3B82F6;
    --class-secondary: #8B5CF6;
    --class-accent: #10B981;
  }}
  
  .class-header {{
    background: linear-gradient(135deg, var(--class-primary), var(--class-secondary));
    color: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }}
  
  .class-title {{
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
  }}
  
  .class-info {{
    opacity: 0.9;
    font-size: 1.1rem;
  }}
  
  .modules-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }}
  
  .module-card {{
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }}
  
  .module-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }}
  
  .module-title {{
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--class-primary);
  }}
  
  .lesson-list {{
    list-style: none;
    padding: 0;
    margin: 1rem 0;
  }}
  
  .lesson-item {{
    padding: 0.5rem 0;
    border-bottom: 1px solid #f3f4f6;
    cursor: pointer;
    transition: color 0.2s ease;
  }}
  
  .lesson-item:hover {{
    color: var(--class-primary);
  }}
  
  .simulations-section {{
    margin-top: 2rem;
    padding: 2rem;
    background: #f8fafc;
    border-radius: 12px;
  }}
  
  .simulations-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }}
  
  .simulation-card {{
    background: white;
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #e5e7eb;
    text-align: center;
    transition: transform 0.2s ease;
  }}
  
  .simulation-card:hover {{
    transform: translateY(-2px);
  }}
  
  .simulation-btn {{
    background: var(--class-accent);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s ease;
    margin-top: 1rem;
  }}
  
  .simulation-btn:hover {{
    background: #059669;
  }}
</style>
{{% endblock %}}

{{% block content %}}
<div class="class-container">
  <!-- Class Header -->
  <div class="class-header">
    <h1 class="class-title">{data['class_name']}</h1>
    <div class="class-info">
      <span>Section: {data['class_section'] or 'General'}</span>
      <span class="mx-3">•</span>
      <span>Code: {data['class_code']}</span>
    </div>
    {{% if data['class_description'] %}}
    <p class="mt-2">{data['class_description']}</p>
    {{% endif %}}
  </div>

  <!-- Navigation Tabs -->
  <div class="nav-tabs">
    <button class="nav-tab active" onclick="showTab('modules')">
      <i class="fas fa-book"></i> Modules
    </button>
    <button class="nav-tab" onclick="showTab('simulations')">
      <i class="fas fa-play-circle"></i> Simulations
    </button>
    <button class="nav-tab" onclick="showTab('assessments')">
      <i class="fas fa-clipboard-check"></i> Assessments
    </button>
    <button class="nav-tab" onclick="showTab('progress')">
      <i class="fas fa-chart-line"></i> Progress
    </button>
  </div>

  <!-- Modules Tab -->
  <div id="modules-tab" class="tab-content active">
    <div class="modules-grid">
      {{% for module in modules %}}
      <div class="module-card">
        <div class="module-title">
          <i class="fas fa-layer-group"></i>
          {{{{ module.name }}}}
        </div>
        <div class="module-description">
          {{{{ module.description or "Interactive learning module" }}}}
        </div>
        <ul class="lesson-list">
          {{% for lesson in module.lessons %}}
          <li class="lesson-item" onclick="loadLesson({{{{ lesson.id }}}})">
            <i class="fas fa-play-circle"></i>
            {{{{ lesson.name }}}}
          </li>
          {{% endfor %}}
        </ul>
        <div class="module-actions">
          <button class="btn btn-primary" onclick="startModule({{{{ module.id }}}})">
            Start Module
          </button>
        </div>
      </div>
      {{% endfor %}}
    </div>
  </div>

  <!-- Simulations Tab -->
  <div id="simulations-tab" class="tab-content">
    <div class="simulations-section">
      <h2>Interactive Simulations</h2>
      <div class="simulations-grid">
        {{% for sim in simulations %}}
        <div class="simulation-card">
          <div class="simulation-icon">
            <i class="{{{{ sim.icon or 'fas fa-play' }}}}"></i>
          </div>
          <h3>{{{{ sim.name }}}}</h3>
          <p>{{{{ sim.description }}}}</p>
          <button class="simulation-btn" onclick="launchSimulation('{{{{ sim.id }}}}')">
            Launch Simulation
          </button>
        </div>
        {{% endfor %}}
      </div>
    </div>
  </div>

  <!-- Assessments Tab -->
  <div id="assessments-tab" class="tab-content">
    <div class="assessments-section">
      <h2>Assessments & Quizzes</h2>
      <div class="assessments-grid">
        {{% for qg in question_groups %}}
        <div class="assessment-card">
          <div class="assessment-header">
            <h3>{{{{ qg.name }}}}</h3>
            <span class="question-count">{{{{ qg.questions|length }}}} questions</span>
          </div>
          <div class="assessment-info">
            <p>{{{{ qg.description or "Test your knowledge" }}}}</p>
            <div class="assessment-meta">
              <span><i class="fas fa-clock"></i> {{{{ (qg.questions|length * 2) }}}} minutes</span>
              <span><i class="fas fa-layer-group"></i> {{{{ qg.category|title }}}}</span>
            </div>
          </div>
          <div class="assessment-actions">
            <button class="btn btn-primary" onclick="startAssessment({{{{ qg.id }}}})">
              Start Assessment
            </button>
          </div>
        </div>
        {{% endfor %}}
      </div>
    </div>
  </div>

  <!-- Progress Tab -->
  <div id="progress-tab" class="tab-content">
    <div class="progress-section">
      <h2>Your Progress</h2>
      <div class="progress-overview">
        <div class="progress-stats">
          <div class="stat-card">
            <div class="stat-value">{{{{ modules|length }}}}</div>
            <div class="stat-label">Modules</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{{{ simulations|length }}}}</div>
            <div class="stat-label">Simulations</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{{{ question_groups|length }}}}</div>
            <div class="stat-label">Assessments</div>
          </div>
        </div>
        <div class="progress-chart">
          <canvas id="progressChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
// Class-specific JavaScript
const classData = {json.dumps(data, indent=2)};

// Tab switching
function showTab(tabName) {{
  // Hide all tabs
  document.querySelectorAll('.tab-content').forEach(tab => {{
    tab.classList.remove('active');
  }});
  document.querySelectorAll('.nav-tab').forEach(tab => {{
    tab.classList.remove('active');
  }});
  
  // Show selected tab
  document.getElementById(tabName + '-tab').classList.add('active');
  event.target.classList.add('active');
}}

// Load lesson content
function loadLesson(lessonId) {{
  fetch(`/api/class/{data['class_id']}/lesson/${{lessonId}}`)
    .then(response => response.json())
    .then(data => {{
      // Handle lesson loading
      showLessonModal(data);
    }});
}}

// Start module
function startModule(moduleId) {{
  window.location.href = `/class/{data['class_id']}/module/${{moduleId}}`;
}}

// Launch simulation
function launchSimulation(simId) {{
  window.open(`/class/{data['class_id']}/simulation/${{simId}}`, '_blank');
}}

// Start assessment
function startAssessment(assessmentId) {{
  window.location.href = `/class/{data['class_id']}/assessment/${{assessmentId}}`;
}}

// Initialize progress chart
function initProgressChart() {{
  const ctx = document.getElementById('progressChart').getContext('2d');
  // Chart.js implementation here
}}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {{
  initProgressChart();
}});
</script>
{{% endblock %}}
'''
        
        return template
    
    def _generate_routes_content(self, data: Dict[str, Any]) -> str:
        """Generate the routes file content"""
        routes = f'''
"""
Auto-generated routes for Class: {data['class_name']} (ID: {data['class_id']})
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from user.models.user import User
from instructor.models.class_model import Class
from instructor.models.question_group import QuestionGroup
from utils.auth_utils import flexible_login_required, get_current_user_context

# Create blueprint for this class
{data['blueprint_name']}_bp = Blueprint(
    '{data['blueprint_name']}', 
    __name__, 
    url_prefix='{data['url_prefix']}'
)

@{data['blueprint_name']}_bp.route('/')
@flexible_login_required
def class_home():
    """Main class page"""
    class_obj = Class.query.get_or_404({data['class_id']})
    
    # Get user context (handles both admin and user authentication)
    user_context = get_current_user_context()
    user_id = user_context['user_id'] if user_context['is_authenticated'] else None
    
    # Prepare template data
    template_data = {{
        'class_obj': class_obj,
        'data': {{
            'class_name': class_obj.name,
            'class_description': class_obj.description,
            'class_code': class_obj.code,
            'modules': get_class_modules({data['class_id']})
        }},
        'modules': get_class_modules({data['class_id']}),
        'simulations': get_class_simulations({data['class_id']}),
        'question_groups': get_class_question_groups({data['class_id']}),
        'user_progress': get_user_progress(user_id, {data['class_id']}) if user_id else None,
        'user_context': user_context
    }}
    
    return render_template(
        'user/classes/class_{data['class_id']}_{data['class_code']}.html',
        **template_data
    )

@{data['blueprint_name']}_bp.route('/module/<int:module_id>')
@flexible_login_required
def module_detail(module_id):
    """Module detail page"""
    # Implementation for module detail
    pass

@{data['blueprint_name']}_bp.route('/lesson/<int:lesson_id>')
@flexible_login_required
def lesson_detail(lesson_id):
    """Lesson detail page"""
    # Implementation for lesson detail
    pass

@{data['blueprint_name']}_bp.route('/simulation/<simulation_id>')
@flexible_login_required
def simulation_detail(simulation_id):
    """Simulation page"""
    # Implementation for simulation
    pass

@{data['blueprint_name']}_bp.route('/assessment/<int:assessment_id>')
@flexible_login_required
def assessment_detail(assessment_id):
    """Assessment page"""
    # Implementation for assessment
    pass

@{data['blueprint_name']}_bp.route('/api/lesson/<int:lesson_id>')
@flexible_login_required
def api_get_lesson(lesson_id):
    """API endpoint to get lesson content"""
    # Get lesson content from Quiz
    qg = QuestionGroup.query.get_or_404(lesson_id)
    
    return jsonify({{
        'id': qg.id,
        'name': qg.name,
        'description': qg.description,
        'content': format_lesson_content(qg),
        'questions': format_questions(qg.questions) if hasattr(qg, 'questions') else []
    }})

@{data['blueprint_name']}_bp.route('/api/progress')
@flexible_login_required
def api_get_progress():
    """API endpoint to get user progress"""
    user_context = get_current_user_context()
    user_id = user_context['user_id']
    progress = get_user_progress(user_id, {data['class_id']})
    
    return jsonify(progress)

@{data['blueprint_name']}_bp.route('/api/submit-answer', methods=['POST'])
@flexible_login_required
def api_submit_answer():
    """API endpoint to submit question answer"""
    data = request.json
    user_context = get_current_user_context()
    user_id = user_context['user_id']
    
    # Process answer submission
    result = process_answer_submission(user_id, data)
    
    return jsonify(result)

# Helper functions
def get_class_modules(class_id):
    """Get modules for the class"""
    class_obj = Class.query.get(class_id)
    modules = []
    
    for qg in class_obj.question_groups:
        modules.append({{
            'id': qg.id,
            'name': qg.name,
            'description': qg.description,
            'category': qg.category,
            'lessons': get_lessons_for_group(qg)
        }})
    
    return modules

def get_class_simulations(class_id):
    """Get simulations for the class"""
    # Implementation based on class type
    class_obj = Class.query.get(class_id)
    
    if 'networking' in class_obj.name.lower():
        return get_networking_simulations()
    elif 'security' in class_obj.name.lower():
        return get_security_simulations()
    else:
        return get_default_simulations()

def get_class_question_groups(class_id):
    """Get Quiz for the class"""
    class_obj = Class.query.get(class_id)
    return [qg for qg in class_obj.question_groups]

def get_user_progress(user_id, class_id):
    """Get user progress for the class"""
    # Implementation for tracking user progress
    return {{
        'modules_completed': 0,
        'simulations_completed': 0,
        'assessments_completed': 0,
        'overall_progress': 0
    }}

def format_lesson_content(question_group):
    """Format Quiz into lesson content"""
    return {{
        'title': question_group.name,
        'description': question_group.description,
        'type': 'questions',
        'content': question_group.description or "Interactive lesson content"
    }}

def format_questions(questions):
    """Format questions for API response"""
    formatted = []
    for q in questions:
        formatted.append({{
            'id': q.id,
            'question': q.question,
            'type': getattr(q, 'type', 'multiple_choice'),
            'options': getattr(q, 'options', []),
            'difficulty': getattr(q, 'difficulty', 'medium')
        }})
    return formatted

def get_lessons_for_group(question_group):
    """Get lessons for a Quiz"""
    return [{{
        'id': question_group.id,
        'name': question_group.name,
        'description': question_group.description,
        'type': 'questions',
        'estimated_time': len(getattr(question_group, 'questions', [])) * 2
    }}]

def get_networking_simulations():
    """Get networking-specific simulations"""
    return [
        {{
            'id': 'network_topology',
            'name': 'Network Topology Builder',
            'description': 'Build and configure network topologies',
            'icon': 'fas fa-network-wired'
        }},
        {{
            'id': 'routing_config',
            'name': 'Routing Configuration',
            'description': 'Configure static and dynamic routing',
            'icon': 'fas fa-route'
        }}
    ]

def get_security_simulations():
    """Get security-specific simulations"""
    return [
        {{
            'id': 'firewall_config',
            'name': 'Firewall Configuration',
            'description': 'Configure firewall rules and policies',
            'icon': 'fas fa-shield-alt'
        }},
        {{
            'id': 'intrusion_detection',
            'name': 'Intrusion Detection',
            'description': 'Set up and monitor IDS systems',
            'icon': 'fas fa-eye'
        }}
    ]

def get_default_simulations():
    """Get default simulations"""
    return [
        {{
            'id': 'general_lab',
            'name': 'Interactive Lab',
            'description': 'General purpose laboratory environment',
            'icon': 'fas fa-flask'
        }}
    ]

def process_answer_submission(user_id, data):
    """Process answer submission and update progress"""
    # Implementation for processing answers
    return {{
        'success': True,
        'score': 0,
        'feedback': 'Answer submitted successfully'
    }}
'''
        
        return routes
    
    def _get_networking1_simulations(self) -> List[Dict]:
        """Get Networking 1 simulations"""
        return [
            {
                'id': 'network_components',
                'name': 'Network Components',
                'description': 'Learn about network hardware components',
                'icon': 'fas fa-server'
            },
            {
                'id': 'osi_model',
                'name': 'OSI Model',
                'description': 'Interactive OSI model layers',
                'icon': 'fas fa-layer-group'
            },
            {
                'id': 'tcp_ip',
                'name': 'TCP/IP Stack',
                'description': 'Understand TCP/IP protocol stack',
                'icon': 'fas fa-network-wired'
            }
        ]
    
    def _get_networking2_simulations(self) -> List[Dict]:
        """Get Networking 2 simulations"""
        return [
            {
                'id': 'routing_fundamentals',
                'name': 'Routing Fundamentals',
                'description': 'Learn static and dynamic routing',
                'icon': 'fas fa-route'
            },
            {
                'id': 'dynamic_routing',
                'name': 'Dynamic Routing',
                'description': 'Configure RIP, OSPF, and EIGRP',
                'icon': 'fas fa-exchange-alt'
            },
            {
                'id': 'network_security',
                'name': 'Network Security',
                'description': 'Implement security measures',
                'icon': 'fas fa-shield-alt'
            }
        ]
    
    def _get_security_simulations(self) -> List[Dict]:
        """Get Security simulations"""
        return [
            {
                'id': 'firewall_lab',
                'name': 'Firewall Laboratory',
                'description': 'Configure and test firewall rules',
                'icon': 'fas fa-fire'
            },
            {
                'id': 'penetration_testing',
                'name': 'Penetration Testing',
                'description': 'Ethical hacking and vulnerability assessment',
                'icon': 'fas fa-bug'
            }
        ]
    
    def _get_programming_simulations(self) -> List[Dict]:
        """Get Programming simulations"""
        return [
            {
                'id': 'code_editor',
                'name': 'Interactive Code Editor',
                'description': 'Write and test code in real-time',
                'icon': 'fas fa-code'
            },
            {
                'id': 'algorithm_visualizer',
                'name': 'Algorithm Visualizer',
                'description': 'Visualize algorithm execution',
                'icon': 'fas fa-sitemap'
            }
        ]
    
    def generate_all_class_resources(self, class_id: int) -> Dict[str, str]:
        """Generate all resources for a class"""
        class_obj = Class.query.get_or_404(class_id)
        
        results = {
            'template': self.generate_class_template(class_obj),
            'routes': self.generate_class_routes(class_obj),
            'class_id': class_id,
            'class_name': class_obj.name,
            'status': 'success'
        }
        
        return results
    
    def regenerate_class_resources(self, class_id: int) -> Dict[str, str]:
        """Regenerate resources for an existing class"""
        return self.generate_all_class_resources(class_id)
    
    def cleanup_class_resources(self, class_id: int) -> bool:
        """Clean up generated resources for a deleted class"""
        try:
            # Remove template file
            template_files = [f for f in os.listdir(self.templates_dir) if f.startswith(f'class_{class_id}_')]
            for file in template_files:
                os.remove(os.path.join(self.templates_dir, file))
            
            # Remove routes file
            routes_files = [f for f in os.listdir(self.routes_dir) if f.startswith(f'class_{class_id}_')]
            for file in routes_files:
                os.remove(os.path.join(self.routes_dir, file))
            
            return True
        except Exception as e:
            print(f"Error cleaning up class resources: {e}")
            return False

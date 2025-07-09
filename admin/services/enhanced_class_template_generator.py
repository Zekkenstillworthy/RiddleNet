"""
Enhanced Class Template Generation Service

Extends the existing template generator with improved static template integration
and more sophisticated classroom automation logic.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import current_app, url_for
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from admin.services.class_template_generator import ClassTemplateGenerator


class EnhancedClassTemplateGenerator(ClassTemplateGenerator):
    """Enhanced service for generating dynamic class templates with better static integration"""
    
    def __init__(self):
        try:
            super().__init__()
        except RuntimeError:
            # Handle case where no app context is available
            self.templates_dir = None
            self.routes_dir = None
        self.static_templates_map = self._build_static_templates_map()
        self.simulation_routes_map = self._build_simulation_routes_map()
    
    def _build_static_templates_map(self) -> Dict[str, Dict]:
        """Map class types to existing static templates and simulations"""
        return {
            'networking1': {
                'learning_template': 'user/learning_networking1.html',
                'simulations_template': 'user/networking1_simulations.html',
                'simulations': [
                    {
                        'id': 'components',
                        'name': 'Network Components Builder',
                        'template': 'user/networking1-components-simulation.html',
                        'route': '/user/networking1/components-simulation',
                        'icon': 'fas fa-network-wired',
                        'description': 'Build and explore computer network components'
                    },
                    {
                        'id': 'osi',
                        'name': 'OSI Model Explorer',
                        'template': 'user/networking1-osi-simulation.html',
                        'route': '/user/networking1/osi-simulation',
                        'icon': 'fas fa-layer-group',
                        'description': 'Interactive OSI model demonstrations'
                    },
                    {
                        'id': 'tcpip',
                        'name': 'TCP/IP Protocol Stack',
                        'template': 'user/networking1-tcpip-simulation.html',
                        'route': '/user/networking1/tcpip-simulation',
                        'icon': 'fas fa-globe',
                        'description': 'Dive deep into TCP/IP protocol suite'
                    },
                    {
                        'id': 'ethernet',
                        'name': 'Ethernet Frame Builder',
                        'template': 'user/networking1-ethernet-simulation.html',
                        'route': '/user/networking1/ethernet-simulation',
                        'icon': 'fas fa-ethernet',
                        'description': 'Learn Ethernet technology through hands-on frame construction'
                    },
                    {
                        'id': 'application',
                        'name': 'Application Layer Protocols',
                        'template': 'user/networking1-application-simulation.html',
                        'route': '/user/networking1/application-simulation',
                        'icon': 'fas fa-server',
                        'description': 'Explore application layer protocols'
                    }
                ],
                'modules': [
                    'Computer Network Fundamentals',
                    'Ethernet Technology', 
                    'Transport Layer and TCP/IP',
                    'Application Layer'
                ]
            },
            'networking2': {
                'learning_template': 'user/learning_networking2.html',
                'simulations_template': 'user/networking2_simulations.html',
                'simulations': [
                    {
                        'id': 'routing-fundamentals',
                        'name': 'Routing Fundamentals Lab',
                        'template': 'user/networking2-routing-fundamentals-simulation.html',
                        'route': '/user/networking2/routing-fundamentals-simulation',
                        'icon': 'fas fa-route',
                        'description': 'Master fundamental routing concepts'
                    },
                    {
                        'id': 'dynamic-routing',
                        'name': 'Dynamic Routing Protocols',
                        'template': 'user/networking2-dynamic-routing-simulation.html',
                        'route': '/user/networking2/dynamic-routing-simulation',
                        'icon': 'fas fa-exchange-alt',
                        'description': 'Compare RIP, OSPF, and EIGRP behaviors'
                    },
                    {
                        'id': 'network-security',
                        'name': 'Network Security Lab',
                        'template': 'user/networking2-security-simulation.html',
                        'route': '/user/networking2/security-simulation',
                        'icon': 'fas fa-shield-alt',
                        'description': 'Implement security measures and policies'
                    },
                    {
                        'id': 'vlan',
                        'name': 'VLAN Trunking Lab',
                        'template': 'user/networking2-vlan-simulation.html',
                        'route': '/user/networking2/vlan-simulation',
                        'icon': 'fas fa-layer-group',
                        'description': 'Configure VLANs and trunking protocols'
                    },
                    {
                        'id': 'wireless',
                        'name': 'Wireless Networks Lab',
                        'template': 'user/networking2-wireless-simulation.html',
                        'route': '/user/networking2/wireless-simulation',
                        'icon': 'fas fa-wifi',
                        'description': 'Design wireless topologies and security'
                    },
                    {
                        'id': 'qos',
                        'name': 'Quality of Service Lab',
                        'template': 'user/networking2-qos-simulation.html',
                        'route': '/user/networking2/qos-simulation',
                        'icon': 'fas fa-tachometer-alt',
                        'description': 'Configure QoS policies and traffic shaping'
                    },
                    {
                        'id': 'management',
                        'name': 'Network Management Lab',
                        'template': 'user/networking2-management-simulation.html',
                        'route': '/user/networking2/management-simulation',
                        'icon': 'fas fa-chart-line',
                        'description': 'Monitor networks with SNMP and analysis tools'
                    }
                ],
                'modules': [
                    'Routing Fundamentals',
                    'Network Security Fundamentals',
                    'Wireless Networks',
                    'Network Management',
                    'Advanced Routing/OSPF',
                    'Network Security and VPN',
                    'Network Troubleshooting'
                ]
            }
        }
    
    def _build_simulation_routes_map(self) -> Dict[str, str]:
        """Map simulation IDs to their actual route patterns"""
        routes = {}
        
        # Networking 1 routes
        net1_base = '/user/networking1'
        for sim in self.static_templates_map['networking1']['simulations']:
            routes[f"networking1_{sim['id']}"] = sim['route']
        
        # Networking 2 routes  
        net2_base = '/user/networking2'
        for sim in self.static_templates_map['networking2']['simulations']:
            routes[f"networking2_{sim['id']}"] = sim['route']
            
        return routes
    
    def _detect_class_type(self, class_obj: Class) -> str:
        """Intelligently detect class type from name and question groups"""
        name_lower = class_obj.name.lower()
        
        # Direct name matching with more comprehensive patterns
        if any(pattern in name_lower for pattern in ['networking 1', 'network 1', 'networking1', 'intro to network', 'introduction to network', 'network fundamental', 'basic network']):
            return 'networking1'
        elif any(pattern in name_lower for pattern in ['networking 2', 'network 2', 'networking2', 'advanced network', 'intermediate network']):
            return 'networking2'
        elif any(pattern in name_lower for pattern in ['security', 'cybersecurity', 'cyber security', 'information security']):
            return 'security'
        
        # Question group analysis
        if class_obj.question_groups:
            categories = [qg.category.lower() if qg.category else '' for qg in class_obj.question_groups]
            category_text = ' '.join(categories)
            
            if any(term in category_text for term in ['osi', 'tcp', 'ethernet', 'fundamental', 'basic', 'intro']):
                return 'networking1'
            elif any(term in category_text for term in ['routing', 'ospf', 'vlan', 'wireless', 'advanced']):
                return 'networking2'
            elif any(term in category_text for term in ['security', 'firewall', 'vpn', 'encryption']):
                return 'security'
        
        return 'general'
    
    def _generate_enhanced_template_content(self, data: Dict[str, Any]) -> str:
        """Generate enhanced template content with static template integration"""
        class_type = data.get('class_type', 'general')
        
        if class_type in self.static_templates_map:
            return self._generate_integrated_template(data, class_type)
        else:
            return self._generate_general_template(data)
    
    def _generate_general_template(self, data: Dict[str, Any]) -> str:
        """Generate general template with standardized learning_base.html styling"""
        template = f'''
{{% if user_context and user_context.get('is_admin') %}}
{{% extends "admin/base.html" %}}
{{% else %}}
{{% extends "user/learning_base.html" %}}
{{% endif %}}

{{% block title %}}{data['class_name']} - Learning Portal{{% endblock %}}

{{% block head %}}
<style>
  .learning-container {{
    max-width: 1600px;
    margin: 0 auto;
    padding: 0 24px;
  }}
  
  /* Header section with learning_base.html styling */
  .learning-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
  }}
  
  .page-title {{
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
  }}
  
  .page-subtitle {{
    color: var(--text-secondary);
    font-size: 1.1rem;
    margin-top: 8px;
    font-weight: 400;
  }}

  /* Navigation button */
  .back-to-classes {{
    background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple));
    color: #fff;
    text-decoration: none;
    padding: 12px 20px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 300ms ease;
    border: 2px solid transparent;
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3);
    font-weight: 600;
  }}
  
  .back-to-classes:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.5);
    border-color: var(--cyber-glow);
    color: #fff;
  }}

  /* Class portal styling */
  .class-container {{
    background: var(--card-bg);
    border-radius: 20px;
    box-shadow: var(--glow-cyan), 0 8px 32px rgba(0, 0, 0, 0.3);
    padding: 32px;
    border: 2px solid rgba(0, 212, 255, 0.3);
    min-height: 600px;
  }}
  
  .class-header {{
    background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple));
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0, 217, 255, 0.3);
    position: relative;
    overflow: hidden;
  }}
  
  .class-header::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
  }}
  
  @keyframes rotate {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
  }}
  
  .class-title {{
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    position: relative;
    z-index: 2;
  }}
  
  .class-meta {{
    display: flex;
    gap: 2rem;
    align-items: center;
    position: relative;
    z-index: 2;
    font-size: 1.1rem;
  }}
  
  .nav-tabs {{
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    background: rgba(26, 35, 126, 0.3);
    border-radius: 15px;
    padding: 0.5rem;
    backdrop-filter: blur(20px);
  }}
  
  .nav-tab {{
    flex: 1;
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    padding: 1rem 2rem;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }}
  
  .nav-tab.active,
  .nav-tab:hover {{
    background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple));
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 217, 255, 0.4);
  }}
  
  .tab-content {{
    display: none;
    animation: fadeIn 0.5s ease;
  }}
  
  .tab-content.active {{
    display: block;
  }}

  @keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  /* Content grid and cards */
  .content-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
  }}
  
  .content-card {{
    background: rgba(26, 35, 126, 0.4);
    border: 1px solid rgba(0, 217, 255, 0.3);
    border-radius: 15px;
    padding: 2rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
  }}
  
  .content-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(135deg, var(--cyber-glow), var(--neon-green));
    opacity: 0.8;
  }}
  
  .content-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 217, 255, 0.4);
    border-color: var(--cyber-glow);
  }}

  .card-header {{
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }}
  
  .card-icon {{
    font-size: 2rem;
    color: var(--cyber-glow);
  }}
  
  .card-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
  }}
  
  .card-description {{
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 1.5rem;
    line-height: 1.6;
  }}
  
  .card-button {{
    background: linear-gradient(135deg, var(--cyber-glow), var(--neon-green));
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }}
  
  .card-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(57, 255, 20, 0.4);
    color: white;
  }}

  /* Progress stats */
  .progress-stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }}
  
  .stat-card {{
    background: rgba(0, 217, 255, 0.1);
    border: 1px solid rgba(0, 217, 255, 0.3);
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
  }}
  
  .stat-value {{
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--cyber-glow);
    display: block;
  }}
  
  .stat-label {{
    color: rgba(255, 255, 255, 0.8);
    font-weight: 500;
  }}

  /* Admin-specific styling differences */
  {{% if user_context and user_context.get('is_admin') %}}
  .learning-container {{
    margin-left: 0;
  }}
  
  .admin-badge {{
    background: linear-gradient(135deg, var(--warning-color), var(--danger-color));
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-left: 12px;
  }}
  {{% endif %}}

  /* Responsive design */
  @media (max-width: 768px) {{
    .learning-header {{
      flex-direction: column;
      gap: 16px;
    }}
    
    .content-grid {{
      grid-template-columns: 1fr;
    }}
  }}
</style>
{{% endblock %}}

{{% block content %}}
<div class="page-container">
  <div class="learning-container">
    <!-- Header Section -->
    <div class="learning-header">
      <div>
        <h1 class="page-title">{data['class_name']} - Class {data['class_code']}</h1>
        <p class="page-subtitle">Interactive Class Portal & Learning Environment
          {{% if user_context and user_context.get('is_admin') %}}
          <span class="admin-badge">Admin View</span>
          {{% endif %}}
        </p>
      </div>
      <div>
        {{% if user_context and user_context.get('is_admin') %}}
        <a href="/admin/classes" class="back-to-classes">
          <i class="fas fa-arrow-left"></i>
          Back to Admin
        </a>
        {{% else %}}
        <a href="/user/classes" class="back-to-classes">
          <i class="fas fa-arrow-left"></i>
          Back to Classes
        </a>
        {{% endif %}}
      </div>
    </div>

    <!-- Class Content -->
    <div class="class-container">
      <!-- Class Header -->
      <div class="class-header">
        <h1 class="class-title">{data['class_name']}</h1>
        <div class="class-meta">
          <span>Section: {data['class_section'] or 'General'}</span>
          <span class="mx-3">•</span>
          <span>Code: {data['class_code']}</span>
        </div>
        {{% if data.get('class_description') %}}
        <p class="mt-2" style="position: relative; z-index: 2; margin-top: 1rem;">{data['class_description']}</p>
        {{% endif %}}
      </div>

      <!-- Navigation Tabs -->
      <div class="nav-tabs">
        <button class="nav-tab active" onclick="showTab('modules')">
          <i class="fas fa-book"></i> Modules
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
        <div class="content-grid">
          <!-- Empty modules - Admin will create lessons in edit mode -->
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-plus-circle card-icon"></i>
              <h3 class="card-title">Create Your First Module</h3>
            </div>
            <p class="card-description">
              This class is ready for content! Use the admin panel to create modules and lessons.
            </p>
            {{% if user_context and user_context.get('is_admin') %}}
            <a href="/admin/modules/create?class_id={data['class_id']}" class="card-button">
              <i class="fas fa-edit"></i>
              Create Module
            </a>
            {{% else %}}
            <div class="card-button" style="opacity: 0.6; cursor: not-allowed;">
              <i class="fas fa-lock"></i>
              Admin Access Required
            </div>
            {{% endif %}}
          </div>
          
          {{% for module in modules %}}
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-layer-group card-icon"></i>
              <h3 class="card-title">{{{{ module.name }}}}</h3>
            </div>
            <p class="card-description">
              {{{{ module.description or "Interactive learning module" }}}}
            </p>
            <div style="margin-bottom: 1rem;">
              <span style="color: var(--cyber-glow);"><i class="fas fa-book-open"></i> Lessons coming soon</span>
            </div>
            <button class="card-button" onclick="startModule({{{{ module.id }}}})">
              <i class="fas fa-play-circle"></i>
              Start Module
            </button>
          </div>
          {{% endfor %}}
        </div>
      </div>

      <!-- Assessments Tab -->
      <div id="assessments-tab" class="tab-content">
        <div class="content-grid">
          {{% for qg in question_groups %}}
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-clipboard-check card-icon"></i>
              <h3 class="card-title">{{{{ qg.name }}}}</h3>
            </div>
            <p class="card-description">
              {{{{ qg.description or "Test your knowledge and skills" }}}}
            </p>
            <div style="margin-bottom: 1rem;">
              <span style="color: var(--cyber-glow);"><i class="fas fa-question-circle"></i> {{{{ qg.questions|length }}}} Questions</span>
              <span style="color: rgba(255,255,255,0.7); margin-left: 1rem;"><i class="fas fa-clock"></i> {{{{ (qg.questions|length * 2) }}}} min</span>
            </div>
            <button class="card-button" onclick="startAssessment({{{{ qg.id }}}})">
              <i class="fas fa-play-circle"></i>
              Start Assessment
            </button>
          </div>
          {{% endfor %}}
          
          {{% if not question_groups %}}
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-plus-circle card-icon"></i>
              <h3 class="card-title">Create Your First Assessment</h3>
            </div>
            <p class="card-description">
              No assessments have been created yet. Use the admin panel to add question groups and assessments.
            </p>
            {{% if user_context and user_context.get('is_admin') %}}
            <a href="/admin/question-groups/create?class_id={data['class_id']}" class="card-button">
              <i class="fas fa-edit"></i>
              Create Assessment
            </a>
            {{% else %}}
            <div class="card-button" style="opacity: 0.6; cursor: not-allowed;">
              <i class="fas fa-lock"></i>
              Admin Access Required
            </div>
            {{% endif %}}
          </div>
          {{% endif %}}
        </div>
      </div>

      <!-- Progress Tab -->
      <div id="progress-tab" class="tab-content">
        <div class="progress-section">
          <h2 style="color: white; font-size: 2rem; font-weight: 700; margin-bottom: 2rem; text-align: center; background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            Your Progress
          </h2>
          <div class="progress-stats">
            <div class="stat-card">
              <span class="stat-value">{{{{ modules|length }}}}</span>
              <span class="stat-label">Learning Modules</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{{{ question_groups|length }}}}</span>
              <span class="stat-label">Assessments</span>
            </div>
            <div class="stat-card">
              <span class="stat-value" id="overallProgress">0%</span>
              <span class="stat-label">Overall Progress</span>
            </div>
          </div>
          <div style="background: rgba(26, 35, 126, 0.3); border-radius: 15px; padding: 2rem; backdrop-filter: blur(20px); border: 1px solid rgba(0, 217, 255, 0.3);">
            <canvas id="progressChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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

// Module functions
function startModule(moduleId) {{
  window.location.href = `/class/{data['class_id']}/module/${{moduleId}}`;
}}

function startAssessment(assessmentId) {{
  window.location.href = `/class/{data['class_id']}/assessment/${{assessmentId}}`;
}}

// Progress chart initialization
function initProgressChart() {{
  const ctx = document.getElementById('progressChart').getContext('2d');
  new Chart(ctx, {{
    type: 'doughnut',
    data: {{
      labels: ['Completed', 'In Progress', 'Not Started'],
      datasets: [{{
        data: [0, 0, 100],
        backgroundColor: ['#39FF14', '#00D9FF', '#8B5CF6'],
        borderWidth: 2,
        borderColor: 'rgba(255, 255, 255, 0.1)'
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{
          labels: {{
            color: 'white',
            font: {{
              size: 14,
              family: 'Inter'
            }}
          }}
        }}
      }}
    }}
  }});
}}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {{
  initProgressChart();
  
  // Load user progress if available
  fetch(`/class/{data['class_id']}/api/progress`)
    .then(response => response.json())
    .then(progress => {{
      document.getElementById('overallProgress').textContent = progress.overall_progress + '%';
    }})
    .catch(error => {{
      console.log('Progress not available - class may be newly created');
      document.getElementById('overallProgress').textContent = '0%';
    }});
}});
</script>
{{% endblock %}}
'''
        
        return template
    
    def _generate_integrated_template(self, data: Dict[str, Any], class_type: str) -> str:
        """Generate template that integrates with existing static templates"""
        static_config = self.static_templates_map[class_type]
        
        template = f'''
{{% if user_context and user_context.get('is_admin') %}}
{{% extends "admin/base.html" %}}
{{% else %}}
{{% extends "user/learning_base.html" %}}
{{% endif %}}

{{% block title %}}{data['class_name']} - Learning Portal{{% endblock %}}

{{% block head %}}
<style>
  .learning-container {{
    max-width: 1600px;
    margin: 0 auto;
    padding: 0 24px;
  }}
  
  /* Header section with learning_base.html styling */
  .learning-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
  }}
  
  .page-title {{
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
  }}
  
  .page-subtitle {{
    color: var(--text-secondary);
    font-size: 1.1rem;
    margin-top: 8px;
    font-weight: 400;
  }}

  /* Navigation button */
  .back-to-classes {{
    background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple));
    color: #fff;
    text-decoration: none;
    padding: 12px 20px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 300ms ease;
    border: 2px solid transparent;
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3);
    font-weight: 600;
  }}
  
  .back-to-classes:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.5);
    border-color: var(--cyber-glow);
    color: #fff;
  }}

  /* Course navigation */
  .course-navigation {{
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  
  .course-nav-btn {{
    background: linear-gradient(135deg, var(--network-purple), var(--cyber-glow));
    color: #fff;
    text-decoration: none;
    padding: 16px 24px;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    transition: all 300ms ease;
    border: 2px solid transparent;
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.3);
    min-width: 200px;
    text-align: center;
  }}
  
  .course-nav-btn:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0, 212, 255, 0.5);
    border-color: var(--cyber-glow);
    color: #fff;
  }}

  /* Class portal styling */
  .class-container {{
    background: var(--card-bg);
    border-radius: 20px;
    box-shadow: var(--glow-cyan), 0 8px 32px rgba(0, 0, 0, 0.3);
    padding: 32px;
    border: 2px solid rgba(0, 212, 255, 0.3);
    min-height: 600px;
  }}
  
  .class-header {{
    background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple));
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0, 217, 255, 0.3);
    position: relative;
    overflow: hidden;
  }}
  
  .class-header::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
  }}
  
  @keyframes rotate {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
  }}
  
  .class-title {{
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    position: relative;
    z-index: 2;
  }}
  
  .class-meta {{
    display: flex;
    gap: 2rem;
    align-items: center;
    position: relative;
    z-index: 2;
    font-size: 1.1rem;
  }}
  
  .nav-tabs {{
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    background: rgba(26, 35, 126, 0.3);
    border-radius: 15px;
    padding: 0.5rem;
    backdrop-filter: blur(20px);
  }}
  
  .nav-tab {{
    flex: 1;
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    padding: 1rem 2rem;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }}
  
  .nav-tab.active,
  .nav-tab:hover {{
    background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple));
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 217, 255, 0.4);
  }}
  
  .tab-content {{
    display: none;
    animation: fadeIn 0.5s ease;
  }}
  
  .tab-content.active {{
    display: block;
  }}

  @keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  /* Content grid and cards */
  .content-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
  }}
  
  .content-card {{
    background: rgba(26, 35, 126, 0.4);
    border: 1px solid rgba(0, 217, 255, 0.3);
    border-radius: 15px;
    padding: 2rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
  }}
  
  .content-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(135deg, var(--cyber-glow), var(--neon-green));
    opacity: 0.8;
  }}
  
  .content-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 217, 255, 0.4);
    border-color: var(--cyber-glow);
  }}

  .card-header {{
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }}
  
  .card-icon {{
    font-size: 2rem;
    color: var(--cyber-glow);
  }}
  
  .card-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
  }}
  
  .card-description {{
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 1.5rem;
    line-height: 1.6;
  }}
  
  .card-button {{
    background: linear-gradient(135deg, var(--cyber-glow), var(--neon-green));
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }}
  
  .card-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(57, 255, 20, 0.4);
    color: white;
  }}

  /* Progress stats */
  .progress-stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }}
  
  .stat-card {{
    background: rgba(0, 217, 255, 0.1);
    border: 1px solid rgba(0, 217, 255, 0.3);
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
  }}
  
  .stat-value {{
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--cyber-glow);
    display: block;
  }}
  
  .stat-label {{
    color: rgba(255, 255, 255, 0.8);
    font-weight: 500;
  }}

  /* Admin-specific styling differences */
  {{% if user_context and user_context.get('is_admin') %}}
  .learning-container {{
    margin-left: 0;
  }}
  
  .admin-badge {{
    background: linear-gradient(135deg, var(--warning-color), var(--danger-color));
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-left: 12px;
  }}
  {{% endif %}}

  /* Responsive design */
  @media (max-width: 768px) {{
    .learning-header {{
      flex-direction: column;
      gap: 16px;
    }}
    
    .course-navigation {{
      flex-direction: column;
      gap: 12px;
    }}
    
    .course-nav-btn {{
      min-width: 100%;
    }}
    
    .content-grid {{
      grid-template-columns: 1fr;
    }}
  }}
</style>
{{% endblock %}}

{{% block content %}}
<div class="page-container">
  <div class="learning-container">
    <!-- Header Section -->
    <div class="learning-header">
      <div>
        <h1 class="page-title">{data['class_name']} - Class {data['class_code']}</h1>
        <p class="page-subtitle">Interactive Class Portal & Learning Environment
          {{% if user_context and user_context.get('is_admin') %}}
          <span class="admin-badge">Admin View</span>
          {{% endif %}}
        </p>
      </div>
      <div class="course-navigation">
        {{% if user_context and user_context.get('is_admin') %}}
        <a href="/admin/classes" class="back-to-classes">
          <i class="fas fa-arrow-left"></i>
          Back to Admin
        </a>
        {{% else %}}
        <a href="/user/classes" class="back-to-classes">
          <i class="fas fa-arrow-left"></i>
          Back to Classes
        </a>
        {{% endif %}}
        <a href="{static_config['learning_template'].replace('user/', '/user/')}" class="course-nav-btn">
          <i class="fas fa-graduation-cap"></i>
          <span>Learning Portal</span>
          <small>Interactive lessons</small>
        </a>
        <a href="{static_config['simulations_template'].replace('user/', '/user/')}" class="course-nav-btn">
          <i class="fas fa-flask"></i>
          <span>Simulations Lab</span>
          <small>Hands-on practice</small>
        </a>
      </div>
    </div>

    <!-- Class Content -->
    <div class="class-container">
      <!-- Class Header -->
      <div class="class-header">
        <h1 class="class-title">{data['class_name']}</h1>
        <div class="class-meta">
          <span>Section: {data['class_section'] or 'General'}</span>
          <span class="mx-3">•</span>
          <span>Code: {data['class_code']}</span>
        </div>
        {{% if data.get('class_description') %}}
        <p class="mt-2" style="position: relative; z-index: 2; margin-top: 1rem;">{data['class_description']}</p>
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
        <div class="content-grid">
          <!-- Learning Portal Card -->
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-graduation-cap card-icon"></i>
              <h3 class="card-title">Learning Portal</h3>
            </div>
            <p class="card-description">
              Access comprehensive learning materials and interactive content for {class_type.title()}.
            </p>
            <a href="{static_config['learning_template'].replace('user/', '/user/')}" class="card-button">
              <i class="fas fa-play"></i>
              Start Learning
            </a>
          </div>
          
          <!-- Empty modules - Admin will create lessons in edit mode -->
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-plus-circle card-icon"></i>
              <h3 class="card-title">Create Your First Module</h3>
            </div>
            <p class="card-description">
              This class is ready for content! Use the admin panel to create modules and lessons.
            </p>
            {{% if user_context and user_context.get('is_admin') %}}
            <a href="/admin/modules/create?class_id={data['class_id']}" class="card-button">
              <i class="fas fa-edit"></i>
              Create Module
            </a>
            {{% else %}}
            <div class="card-button" style="opacity: 0.6; cursor: not-allowed;">
              <i class="fas fa-lock"></i>
              Admin Access Required
            </div>
            {{% endif %}}
          </div>
          
          {{% for module in modules %}}
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-layer-group card-icon"></i>
              <h3 class="card-title">{{{{ module.name }}}}</h3>
            </div>
            <p class="card-description">
              {{{{ module.description or "Interactive learning module" }}}}
            </p>
            <div style="margin-bottom: 1rem;">
              <span style="color: var(--cyber-glow);"><i class="fas fa-book-open"></i> Lessons coming soon</span>
            </div>
            <button class="card-button" onclick="startModule({{{{ module.id }}}})">
              <i class="fas fa-play-circle"></i>
              Start Module
            </button>
          </div>
          {{% endfor %}}
        </div>
      </div>

      <!-- Simulations Tab -->
      <div id="simulations-tab" class="tab-content">
        <div class="content-grid">
          <!-- Simulations Hub Card -->
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-desktop card-icon"></i>
              <h3 class="card-title">Simulations Laboratory</h3>
            </div>
            <p class="card-description">
              Access the complete simulation laboratory for hands-on practice and experimentation.
            </p>
            <a href="{static_config['simulations_template'].replace('user/', '/user/')}" class="card-button">
              <i class="fas fa-rocket"></i>
              Open Lab
            </a>
          </div>
          
          {{% for sim in simulations %}}
          <div class="content-card">
            <div class="card-header">
              <i class="{{{{ sim.icon or 'fas fa-play' }}}} card-icon"></i>
              <h3 class="card-title">{{{{ sim.name }}}}</h3>
            </div>
            <p class="card-description">{{{{ sim.description }}}}</p>
            <a href="{{{{ sim.route }}}}" class="card-button" target="_blank">
              <i class="fas fa-external-link-alt"></i>
              Launch Simulation
            </a>
          </div>
          {{% endfor %}}
        </div>
      </div>

      <!-- Assessments Tab -->
      <div id="assessments-tab" class="tab-content">
        <div class="content-grid">
          {{% for qg in question_groups %}}
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-clipboard-check card-icon"></i>
              <h3 class="card-title">{{{{ qg.name }}}}</h3>
            </div>
            <p class="card-description">
              {{{{ qg.description or "Test your knowledge and skills" }}}}
            </p>
            <div style="margin-bottom: 1rem;">
              <span style="color: var(--cyber-glow);"><i class="fas fa-question-circle"></i> {{{{ qg.questions|length }}}} Questions</span>
              <span style="color: rgba(255,255,255,0.7); margin-left: 1rem;"><i class="fas fa-clock"></i> {{{{ (qg.questions|length * 2) }}}} min</span>
            </div>
            <button class="card-button" onclick="startAssessment({{{{ qg.id }}}})">
              <i class="fas fa-play-circle"></i>
              Start Assessment
            </button>
          </div>
          {{% endfor %}}
          
          {{% if not question_groups %}}
          <div class="content-card">
            <div class="card-header">
              <i class="fas fa-plus-circle card-icon"></i>
              <h3 class="card-title">Create Your First Assessment</h3>
            </div>
            <p class="card-description">
              No assessments have been created yet. Use the admin panel to add question groups and assessments.
            </p>
            {{% if user_context and user_context.get('is_admin') %}}
            <a href="/admin/question-groups/create?class_id={data['class_id']}" class="card-button">
              <i class="fas fa-edit"></i>
              Create Assessment
            </a>
            {{% else %}}
            <div class="card-button" style="opacity: 0.6; cursor: not-allowed;">
              <i class="fas fa-lock"></i>
              Admin Access Required
            </div>
            {{% endif %}}
          </div>
          {{% endif %}}
        </div>
      </div>

      <!-- Progress Tab -->
      <div id="progress-tab" class="tab-content">
        <div class="progress-section">
          <h2 style="color: white; font-size: 2rem; font-weight: 700; margin-bottom: 2rem; text-align: center; background: linear-gradient(135deg, var(--cyber-glow), var(--network-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            Your Progress
          </h2>
          <div class="progress-stats">
            <div class="stat-card">
              <span class="stat-value">{{{{ modules|length }}}}</span>
              <span class="stat-label">Learning Modules</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{{{ simulations|length }}}}</span>
              <span class="stat-label">Simulations</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{{{ question_groups|length }}}}</span>
              <span class="stat-label">Assessments</span>
            </div>
            <div class="stat-card">
              <span class="stat-value" id="overallProgress">0%</span>
              <span class="stat-label">Overall Progress</span>
            </div>
          </div>
          <div style="background: rgba(26, 35, 126, 0.3); border-radius: 15px; padding: 2rem; backdrop-filter: blur(20px); border: 1px solid rgba(0, 217, 255, 0.3);">
            <canvas id="progressChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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

// Module functions
function startModule(moduleId) {{
  window.location.href = `/class/{data['class_id']}/module/${{moduleId}}`;
}}

function startAssessment(assessmentId) {{
  window.location.href = `/class/{data['class_id']}/assessment/${{assessmentId}}`;
}}

// Progress chart initialization
function initProgressChart() {{
  const ctx = document.getElementById('progressChart').getContext('2d');
  new Chart(ctx, {{
    type: 'doughnut',
    data: {{
      labels: ['Completed', 'In Progress', 'Not Started'],
      datasets: [{{
        data: [0, 0, 100],
        backgroundColor: ['#39FF14', '#00D9FF', '#8B5CF6'],
        borderWidth: 2,
        borderColor: 'rgba(255, 255, 255, 0.1)'
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{
          labels: {{
            color: 'white',
            font: {{
              size: 14,
              family: 'Inter'
            }}
          }}
        }}
      }}
    }}
  }});
}}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {{
  initProgressChart();
  
  // Load user progress if available
  fetch(`/class/{data['class_id']}/api/progress`)
    .then(response => response.json())
    .then(progress => {{
      document.getElementById('overallProgress').textContent = progress.overall_progress + '%';
    }})
    .catch(error => {{
      console.log('Progress not available - class may be newly created');
      document.getElementById('overallProgress').textContent = '0%';
    }});
}});
</script>
{{% endblock %}}
'''
        
        return template
    
    def generate_class_template(self, class_obj: Class) -> str:
        """Enhanced class template generation with static integration"""
        template_data = self._prepare_template_data(class_obj)
        
        # Detect class type and enhance data
        class_type = self._detect_class_type(class_obj)
        template_data['class_type'] = class_type
        
        # Add static simulations if applicable
        if class_type in self.static_templates_map:
            template_data['simulations'] = self.static_templates_map[class_type]['simulations']
            template_data['static_learning_url'] = self.static_templates_map[class_type]['learning_template']
            template_data['static_simulations_url'] = self.static_templates_map[class_type]['simulations_template']
        
        # Generate enhanced template content
        template_content = self._generate_enhanced_template_content(template_data)
        
        # Save template file
        template_filename = f"class_{class_obj.id}_{class_obj.code.lower().replace(' ', '_')}.html"
        template_path = os.path.join(self.templates_dir, template_filename)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return template_filename
    
    def _generate_enhanced_routes_content(self, data: Dict[str, Any]) -> str:
        """Generate enhanced routes with static template integration"""
        class_type = data.get('class_type', 'general')
        
        base_routes = super()._generate_routes_content(data)
        
        # Add simulation proxies for static templates
        if class_type in self.static_templates_map:
            simulation_routes = self._generate_simulation_proxy_routes(data, class_type)
            base_routes += simulation_routes
        
        return base_routes
    
    def _generate_simulation_proxy_routes(self, data: Dict[str, Any], class_type: str) -> str:
        """Generate proxy routes that redirect to static simulations"""
        static_config = self.static_templates_map[class_type]
        
        proxy_routes = f'''

# Simulation proxy routes for {class_type}
'''
        
        for sim in static_config['simulations']:
            proxy_routes += f'''
@{data['blueprint_name']}_bp.route('/simulation/{sim['id']}')
@flexible_login_required
def simulation_{sim['id']}():
    """Proxy to {sim['name']} simulation"""
    return redirect('{sim['route']}')
'''
        
        return proxy_routes
    
    def generate_class_routes(self, class_obj: Class) -> str:
        """Enhanced route generation with static integration"""
        routes_data = self._prepare_routes_data(class_obj)
        
        # Add class type for enhanced route generation
        class_type = self._detect_class_type(class_obj)
        routes_data['class_type'] = class_type
        
        # Generate enhanced routes content
        routes_content = self._generate_enhanced_routes_content(routes_data)
        
        # Save routes file
        routes_filename = f"class_{class_obj.id}_routes.py"
        routes_path = os.path.join(self.routes_dir, routes_filename)
        
        with open(routes_path, 'w', encoding='utf-8') as f:
            f.write(routes_content)
        
        return routes_filename
    
    def create_class_dashboard_integration(self, class_obj: Class) -> Dict[str, Any]:
        """Create integration points for the class dashboard"""
        class_type = self._detect_class_type(class_obj)
        
        integration = {
            'class_id': class_obj.id,
            'class_type': class_type,
            'dashboard_url': f'/class/{class_obj.id}/',
            'api_endpoints': {
                'progress': f'/class/{class_obj.id}/api/progress',
                'lessons': f'/class/{class_obj.id}/api/lessons',
                'simulations': f'/class/{class_obj.id}/api/simulations',
                'assessments': f'/class/{class_obj.id}/api/assessments'
            },
            'static_integrations': []
        }
        
        if class_type in self.static_templates_map:
            static_config = self.static_templates_map[class_type]
            integration['static_integrations'] = [
                {
                    'type': 'learning',
                    'url': static_config['learning_template'].replace('user/', '/user/'),
                    'name': f'{class_type.title()} Learning Path'
                },
                {
                    'type': 'simulations',
                    'url': static_config['simulations_template'].replace('user/', '/user/'),
                    'name': f'{class_type.title()} Simulations'
                }
            ]
            
            for sim in static_config['simulations']:
                integration['static_integrations'].append({
                    'type': 'simulation',
                    'url': sim['route'],
                    'name': sim['name'],
                    'id': sim['id']
                })
        
        return integration
    
    def generate_all_class_resources(self, class_id: int) -> Dict[str, str]:
        """Generate all resources for a class (enhanced version)"""
        try:
            # Try to get class object from database
            try:
                from admin.models.class_model import Class
                class_obj = Class.query.get(class_id)
                if not class_obj:
                    raise ValueError(f"Class with ID {class_id} not found")
            except Exception as db_error:
                # If database query fails, we can't generate resources
                raise Exception(f"Database query failed: {str(db_error)}")
            
            # Generate template
            template_filename = self.generate_class_template(class_obj)
            
            # Generate routes
            routes_filename = self.generate_class_routes(class_obj)
            
            return {
                'template': template_filename,
                'routes': routes_filename,
                'class_id': class_id,
                'enhanced': True,
                'static_integrations': len(self.static_templates_map[self._detect_class_type(class_obj)]['simulations']) if self._detect_class_type(class_obj) in self.static_templates_map else 0
            }
            
        except Exception as e:
            raise Exception(f"Enhanced template generation failed: {str(e)}")
    
    def generate_class_resources_from_object(self, class_obj) -> Dict[str, str]:
        """Generate resources from an existing class object (for testing)"""
        try:
            # Generate template
            template_filename = self.generate_class_template(class_obj)
            
            # Generate routes
            routes_filename = self.generate_class_routes(class_obj)
            
            class_type = self._detect_class_type(class_obj)
            
            return {
                'template': template_filename,
                'routes': routes_filename,
                'class_id': class_obj.id,
                'enhanced': True,
                'class_type': class_type,
                'static_integrations': len(self.static_templates_map[class_type]['simulations']) if class_type in self.static_templates_map else 0
            }
            
        except Exception as e:
            raise Exception(f"Enhanced template generation from object failed: {str(e)}")
    
    def regenerate_class_resources(self, class_id: int) -> Dict[str, str]:
        """Regenerate resources for an existing class (enhanced version)"""
        return self.generate_all_class_resources(class_id)


# Export the enhanced generator
enhanced_template_generator = EnhancedClassTemplateGenerator()

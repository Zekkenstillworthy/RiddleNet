"""
Initialization script for Enhanced Classroom Automation System

Run this script to set up the enhanced automation system in your RiddleNet application.
"""

import os
from flask import Flask, current_app
from instructor.services.enhanced_class_template_generator import enhanced_template_generator
from instructor.services.dynamic_route_registry import route_registry


def initialize_enhanced_automation(app: Flask):
    """Initialize the enhanced classroom automation system"""
    
    with app.app_context():
        print("🚀 Initializing Enhanced Classroom Automation System...")
        
        # 1. Ensure required directories exist
        print("📁 Creating required directories...")
        templates_dir = os.path.join(app.root_path, 'templates', 'user', 'classes')
        routes_dir = os.path.join(app.root_path, 'user', 'routes', 'generated')
        
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(routes_dir, exist_ok=True)
        
        # Create __init__.py files
        init_files = [
            os.path.join(routes_dir, '__init__.py'),
            os.path.join(app.root_path, 'user', 'routes', '__init__.py')
        ]
        
        for init_file in init_files:
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('# Auto-generated package file\n')
        
        print(f"[OK] Created directories:")
        print(f"   - {templates_dir}")
        print(f"   - {routes_dir}")
        
        # 2. Initialize route registry
        print("🔗 Initializing dynamic route registry...")
        route_registry.init_app(app)
        
        # 3. Validate static template mappings
        print("[DEBUG] Validating static template integrations...")
        static_templates = enhanced_template_generator.static_templates_map
        
        for class_type, config in static_templates.items():
            print(f"   - {class_type.title()}: {len(config['simulations'])} simulations mapped")
            
            # Check if learning template exists
            learning_template = config['learning_template']
            template_path = os.path.join(app.root_path, 'templates', learning_template)
            if os.path.exists(template_path):
                print(f"     [OK] Learning template found: {learning_template}")
            else:
                print(f"     [WARNING]  Learning template missing: {learning_template}")
            
            # Check simulations template
            sim_template = config['simulations_template']
            sim_template_path = os.path.join(app.root_path, 'templates', sim_template)
            if os.path.exists(sim_template_path):
                print(f"     [OK] Simulations template found: {sim_template}")
            else:
                print(f"     [WARNING]  Simulations template missing: {sim_template}")
        
        # 4. Create CSS file for enhanced templates
        print("🎨 Creating enhanced CSS styles...")
        css_dir = os.path.join(app.root_path, 'static', 'css', 'user')
        os.makedirs(css_dir, exist_ok=True)
        
        css_file = os.path.join(css_dir, 'dynamic_class.css')
        if not os.path.exists(css_file):
            create_enhanced_css(css_file)
            print(f"[OK] Created enhanced CSS: {css_file}")
        
        # 5. Get statistics
        print("[STATS] System Statistics:")
        try:
            from instructor.models.class_model import Class
            total_classes = Class.query.count()
            stats = route_registry.get_statistics()
            
            print(f"   - Total Classes: {total_classes}")
            print(f"   - Registered Routes: {stats.get('registered_classes', 0)}")
            print(f"   - Registration Rate: {stats.get('registration_rate', 0):.1f}%")
            
        except Exception as e:
            print(f"   - Could not get statistics: {e}")
        
        print("\n🎉 Enhanced Classroom Automation System initialized successfully!")
        print("\n📖 Next Steps:")
        print("   1. Create a new class in /admin/classes")
        print("   2. System will auto-detect type and generate enhanced template")
        print("   3. Students can access via /class/{id}/ with full integration")
        print("\n📚 Documentation:")
        print("   - Architecture: docs/AUTOMATED_CLASSROOM_GENERATION.md")
        print("   - Usage Guide: docs/ENHANCED_AUTOMATION_USAGE_GUIDE.md")


def create_enhanced_css(css_file_path: str):
    """Create enhanced CSS for dynamic class templates"""
    
    css_content = """
/* Enhanced Dynamic Class Templates CSS */

.class-portal {
  background: linear-gradient(135deg, #0a0c14, #1a1b2e);
  min-height: 100vh;
  color: white;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

.class-integration-header {
  background: linear-gradient(135deg, #00D9FF, #8B5CF6);
  padding: 2rem;
  border-radius: 15px;
  margin: 1rem;
  position: relative;
  overflow: hidden;
}

.class-integration-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.enhanced-nav-tabs {
  display: flex;
  gap: 0.5rem;
  background: rgba(26, 35, 126, 0.3);
  border-radius: 15px;
  padding: 0.5rem;
  margin: 1rem;
  backdrop-filter: blur(20px);
}

.enhanced-nav-tab {
  flex: 1;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  padding: 1rem 2rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.enhanced-nav-tab.active,
.enhanced-nav-tab:hover {
  background: linear-gradient(135deg, #00D9FF, #8B5CF6);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 217, 255, 0.4);
}

.enhanced-content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  padding: 2rem;
}

.enhanced-content-card {
  background: rgba(26, 35, 126, 0.4);
  border: 1px solid rgba(0, 217, 255, 0.3);
  border-radius: 15px;
  padding: 2rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

.enhanced-content-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #00D9FF, #39FF14);
  opacity: 0.8;
}

.enhanced-content-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 217, 255, 0.4);
  border-color: #00D9FF;
}

.enhanced-card-button {
  background: linear-gradient(135deg, #00D9FF, #39FF14);
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
}

.enhanced-card-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(57, 255, 20, 0.4);
  color: white;
}

.enhanced-progress-chart {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 2rem;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .enhanced-content-grid {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
  
  .enhanced-nav-tabs {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .enhanced-nav-tab {
    padding: 0.75rem 1rem;
  }
}

/* Integration-specific styles */
.static-integration-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #00D9FF;
  text-decoration: none;
  transition: all 0.3s ease;
}

.static-integration-link:hover {
  color: #39FF14;
  transform: translateX(5px);
}

.simulation-proxy-card {
  border-left: 4px solid #39FF14;
}

.assessment-integration-card {
  border-left: 4px solid #FF6B6B;
}

.learning-integration-card {
  border-left: 4px solid #4ECDC4;
}
"""
    
    with open(css_file_path, 'w') as f:
        f.write(css_content)


def check_system_health():
    """Check the health of the automation system"""
    print("[DEBUG] Checking Enhanced Automation System Health...")
    
    try:
        # Check route registry
        stats = route_registry.get_statistics()
        print(f"[OK] Route Registry: {stats.get('registered_classes', 0)} classes registered")
        
        # Check template generator
        template_map = enhanced_template_generator.static_templates_map
        print(f"[OK] Template Generator: {len(template_map)} class types supported")
        
        # Check directories
        from flask import current_app
        templates_dir = os.path.join(current_app.root_path, 'templates', 'user', 'classes')
        routes_dir = os.path.join(current_app.root_path, 'user', 'routes', 'generated')
        
        template_files = len([f for f in os.listdir(templates_dir) if f.endswith('.html')]) if os.path.exists(templates_dir) else 0
        route_files = len([f for f in os.listdir(routes_dir) if f.endswith('.py')]) if os.path.exists(routes_dir) else 0
        
        print(f"[OK] Generated Files: {template_files} templates, {route_files} route files")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] System Health Check Failed: {e}")
        return False


if __name__ == "__main__":
    print("Enhanced Classroom Automation - Initialization Script")
    print("=" * 50)
    print("This script should be run from within your Flask application context.")
    print("Import and call initialize_enhanced_automation(app) in your main application.")


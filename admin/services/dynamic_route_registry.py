"""
Dynamic Route Registration Service

This service automatically registers routes for dynamically generated class templates.
"""

import os
import importlib.util
import sys
from typing import Dict, List
from flask import Flask, current_app
from admin.models.class_model import Class


class DynamicRouteRegistry:
    """Service for registering dynamic class routes"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.registered_classes = set()
        self.routes_dir = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the route registry with the Flask app"""
        self.app = app
        self.routes_dir = os.path.join(app.root_path, 'user', 'routes', 'generated')
        
        # Register existing class routes on startup
        with app.app_context():
            self.register_all_class_routes()
    
    def register_all_class_routes(self):
        """Register routes for all existing classes"""
        try:
            classes = Class.query.all()
            for class_obj in classes:
                self.register_class_routes(class_obj.id)
        except Exception as e:
            print(f"Error registering class routes on startup: {e}")
    
    def register_class_routes(self, class_id: int) -> bool:
        """Register routes for a specific class"""
        try:
            if class_id in self.registered_classes:
                print(f"Routes for class {class_id} already registered")
                return True
            
            routes_file = f"class_{class_id}_routes.py"
            routes_path = os.path.join(self.routes_dir, routes_file)
            
            if not os.path.exists(routes_path):
                print(f"Routes file not found: {routes_path}")
                return False
            
            # Import the routes module
            module_name = f"user.routes.generated.class_{class_id}_routes"
            spec = importlib.util.spec_from_file_location(module_name, routes_path)
            
            if spec is None or spec.loader is None:
                print(f"Could not load module spec for {module_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Get the blueprint from the module
            blueprint_name = f"class_{class_id}_bp"
            if hasattr(module, blueprint_name):
                blueprint = getattr(module, blueprint_name)
                
                # Register the blueprint with the app
                self.app.register_blueprint(blueprint)
                self.registered_classes.add(class_id)
                
                print(f"Successfully registered routes for class {class_id}")
                return True
            else:
                print(f"Blueprint {blueprint_name} not found in module")
                return False
                
        except Exception as e:
            print(f"Error registering routes for class {class_id}: {e}")
            return False
    
    def unregister_class_routes(self, class_id: int) -> bool:
        """Unregister routes for a specific class"""
        try:
            if class_id not in self.registered_classes:
                return True
            
            # Remove from registered classes
            self.registered_classes.discard(class_id)
            
            # Note: Flask doesn't support unregistering blueprints at runtime
            # The routes will remain until the app is restarted
            print(f"Marked class {class_id} routes for removal (restart required)")
            return True
            
        except Exception as e:
            print(f"Error unregistering routes for class {class_id}: {e}")
            return False
    
    def refresh_class_routes(self, class_id: int) -> bool:
        """Refresh routes for a class (unregister and register again)"""
        try:
            # For Flask, we can't truly unregister, so we just re-register
            # This will override existing routes
            self.registered_classes.discard(class_id)
            return self.register_class_routes(class_id)
        except Exception as e:
            print(f"Error refreshing routes for class {class_id}: {e}")
            return False
    
    def get_registered_classes(self) -> List[int]:
        """Get list of registered class IDs"""
        return list(self.registered_classes)
    
    def is_class_registered(self, class_id: int) -> bool:
        """Check if a class has registered routes"""
        return class_id in self.registered_classes
    
    def get_class_routes_info(self, class_id: int) -> Dict:
        """Get information about registered routes for a class"""
        if class_id not in self.registered_classes:
            return {'registered': False}
        
        try:
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return {'registered': False, 'error': 'Class not found'}
            
            routes_info = {
                'registered': True,
                'class_id': class_id,
                'class_name': class_obj.name,
                'blueprint_name': f"class_{class_id}",
                'url_prefix': f"/class/{class_id}",
                'routes': [
                    f"/class/{class_id}/",
                    f"/class/{class_id}/module/<int:module_id>",
                    f"/class/{class_id}/lesson/<int:lesson_id>",
                    f"/class/{class_id}/simulation/<simulation_id>",
                    f"/class/{class_id}/assessment/<int:assessment_id>",
                    f"/class/{class_id}/api/lesson/<int:lesson_id>",
                    f"/class/{class_id}/api/progress",
                    f"/class/{class_id}/api/submit-answer"
                ]
            }
            
            return routes_info
            
        except Exception as e:
            return {'registered': True, 'error': str(e)}
    
    def validate_routes_directory(self) -> bool:
        """Validate that the routes directory exists and is writable"""
        try:
            if not os.path.exists(self.routes_dir):
                os.makedirs(self.routes_dir, exist_ok=True)
            
            # Create __init__.py if it doesn't exist
            init_file = os.path.join(self.routes_dir, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('# Auto-generated routes package\n')
            
            return True
        except Exception as e:
            print(f"Error validating routes directory: {e}")
            return False
    
    def cleanup_orphaned_routes(self):
        """Clean up route files for classes that no longer exist"""
        try:
            if not os.path.exists(self.routes_dir):
                return
            
            # Get all existing class IDs
            existing_classes = {cls.id for cls in Class.query.all()}
            
            # Get all route files
            route_files = [f for f in os.listdir(self.routes_dir) if f.startswith('class_') and f.endswith('_routes.py')]
            
            for route_file in route_files:
                try:
                    # Extract class ID from filename
                    parts = route_file.replace('.py', '').split('_')
                    if len(parts) >= 2 and parts[1].isdigit():
                        class_id = int(parts[1])
                        
                        if class_id not in existing_classes:
                            # Remove orphaned route file
                            file_path = os.path.join(self.routes_dir, route_file)
                            os.remove(file_path)
                            print(f"Removed orphaned route file: {route_file}")
                            
                            # Remove from registered classes
                            self.registered_classes.discard(class_id)
                            
                except (ValueError, IndexError) as e:
                    print(f"Error processing route file {route_file}: {e}")
                    
        except Exception as e:
            print(f"Error cleaning up orphaned routes: {e}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about registered routes"""
        try:
            total_classes = Class.query.count()
            registered_count = len(self.registered_classes)
            
            route_files = []
            if os.path.exists(self.routes_dir):
                route_files = [f for f in os.listdir(self.routes_dir) if f.startswith('class_') and f.endswith('_routes.py')]
            
            return {
                'total_classes': total_classes,
                'registered_classes': registered_count,
                'route_files': len(route_files),
                'registration_rate': (registered_count / total_classes * 100) if total_classes > 0 else 0,
                'registered_class_ids': list(self.registered_classes)
            }
            
        except Exception as e:
            return {'error': str(e)}


# Global instance
route_registry = DynamicRouteRegistry()

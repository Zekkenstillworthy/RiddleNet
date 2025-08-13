#!/usr/bin/env python3
"""
Simulation Data Migration Script

This script migrates static simulation data from the templates/user and static directories
into the database-driven simulation system. It scans for existing simulation content,
parses the structure, and creates corresponding database records.

Usage:
    python migrate_simulations.py [--dry-run] [--force] [--backup]

Options:
    --dry-run    Show what would be migrated without making changes
    --force      Overwrite existing simulations with same name
    --backup     Create backup of existing database before migration
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.models.simulation import Simulation, SimulationAttempt
from admin.app import db, create_app
from utils.auth_utils import hash_password

class SimulationMigrator:
    def __init__(self, dry_run=False, force=False, backup=False):
        self.dry_run = dry_run
        self.force = force
        self.backup = backup
        self.app = None
        self.stats = {
            'scanned_files': 0,
            'found_simulations': 0,
            'migrated_simulations': 0,
            'skipped_simulations': 0,
            'errors': []
        }
        
    def initialize_app(self):
        """Initialize Flask app and database context"""
        print("Initializing Flask application...")
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        if self.backup:
            self.create_backup()
            
    def create_backup(self):
        """Create backup of existing database"""
        backup_file = f"riddlenet_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        source = os.path.join('instance', 'riddlenet.db')
        backup_path = os.path.join('instance', 'backups', backup_file)
        
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        if os.path.exists(source):
            import shutil
            shutil.copy2(source, backup_path)
            print(f"Database backup created: {backup_path}")
        else:
            print("No existing database found to backup")
    
    def scan_static_simulations(self):
        """Scan static directories for simulation content"""
        print("Scanning for static simulation content...")
        simulations = []
        
        # Common paths to check for simulation content
        paths_to_scan = [
            'templates/user/simulations',
            'static/simulations',
            'static/js/simulations',
            'user/routes/simulations',
            'services/simulation_data'
        ]
        
        for path in paths_to_scan:
            if os.path.exists(path):
                simulations.extend(self._scan_directory(path))
                
        # Also check for individual simulation files referenced in routes
        simulations.extend(self._scan_route_files())
        
        return simulations
    
    def _scan_directory(self, directory):
        """Scan a directory for simulation files"""
        simulations = []
        
        for root, dirs, files in os.walk(directory):
            self.stats['scanned_files'] += len(files)
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check for different types of simulation files
                if self._is_simulation_file(file, file_path):
                    sim_data = self._parse_simulation_file(file_path)
                    if sim_data:
                        simulations.append(sim_data)
                        self.stats['found_simulations'] += 1
                        
        return simulations
    
    def _is_simulation_file(self, filename, filepath):
        """Determine if a file contains simulation data"""
        simulation_indicators = [
            'simulation',
            'scenario',
            'lab',
            'exercise',
            'practical'
        ]
        
        # Check filename
        if any(indicator in filename.lower() for indicator in simulation_indicators):
            return True
            
        # Check file extension and content
        if filename.endswith(('.html', '.json', '.js', '.py')):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return any(indicator in content.lower() for indicator in simulation_indicators)
            except (UnicodeDecodeError, IOError):
                pass
                
        return False
    
    def _parse_simulation_file(self, filepath):
        """Parse a simulation file and extract structured data"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try different parsing strategies based on file type
            if filepath.endswith('.json'):
                return self._parse_json_simulation(filepath, content)
            elif filepath.endswith('.html'):
                return self._parse_html_simulation(filepath, content)
            elif filepath.endswith('.js'):
                return self._parse_js_simulation(filepath, content)
            elif filepath.endswith('.py'):
                return self._parse_python_simulation(filepath, content)
                
        except Exception as e:
            self.stats['errors'].append(f"Error parsing {filepath}: {str(e)}")
            
        return None
    
    def _parse_json_simulation(self, filepath, content):
        """Parse JSON simulation file"""
        try:
            data = json.loads(content)
            return self._normalize_simulation_data(filepath, data)
        except json.JSONDecodeError as e:
            self.stats['errors'].append(f"Invalid JSON in {filepath}: {str(e)}")
            return None
    
    def _parse_html_simulation(self, filepath, content):
        """Parse HTML template simulation file"""
        # Extract simulation data from HTML comments, data attributes, or JavaScript
        simulation_data = {
            'source_file': filepath,
            'title': self._extract_html_title(content),
            'description': self._extract_html_description(content),
            'type': self._infer_simulation_type(filepath, content),
            'steps': self._extract_html_steps(content),
            'difficulty': self._infer_difficulty(content),
            'estimated_duration': self._estimate_duration(content)
        }
        
        return self._normalize_simulation_data(filepath, simulation_data)
    
    def _parse_js_simulation(self, filepath, content):
        """Parse JavaScript simulation file"""
        # Look for simulation configuration objects
        simulation_configs = re.findall(r'(?:const|var|let)\s+(\w*[Ss]imulation\w*)\s*=\s*({.*?});', content, re.DOTALL)
        
        if simulation_configs:
            try:
                # Try to parse the first configuration found
                config_name, config_json = simulation_configs[0]
                # Simple JS object to JSON conversion (limited)
                config_json = re.sub(r'(\w+):', r'"\1":', config_json)  # Add quotes to keys
                config_json = re.sub(r"'([^']*)'", r'"\1"', config_json)  # Convert single quotes
                
                data = json.loads(config_json)
                data['source_file'] = filepath
                data['config_name'] = config_name
                
                return self._normalize_simulation_data(filepath, data)
            except:
                pass
                
        # Fallback: extract basic info from comments and function names
        return self._extract_js_basic_info(filepath, content)
    
    def _parse_python_simulation(self, filepath, content):
        """Parse Python simulation file"""
        # Look for simulation classes or configuration dictionaries
        simulation_data = {
            'source_file': filepath,
            'title': self._extract_python_title(content),
            'description': self._extract_python_description(content),
            'type': self._infer_simulation_type(filepath, content),
            'steps': self._extract_python_steps(content)
        }
        
        return self._normalize_simulation_data(filepath, simulation_data)
    
    def _extract_html_title(self, content):
        """Extract title from HTML content"""
        # Try various patterns
        patterns = [
            r'<title[^>]*>([^<]+)</title>',
            r'<h1[^>]*>([^<]+)</h1>',
            r'data-simulation-title=["\']([^"\']+)["\']',
            r'simulation.*title.*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return "Imported Simulation"
    
    def _extract_html_description(self, content):
        """Extract description from HTML content"""
        patterns = [
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
            r'data-simulation-description=["\']([^"\']+)["\']',
            r'<p[^>]*class=["\'][^"\']*description[^"\']*["\'][^>]*>([^<]+)</p>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return "Simulation imported from static content"
    
    def _extract_html_steps(self, content):
        """Extract simulation steps from HTML content"""
        steps = []
        
        # Look for step patterns in HTML
        step_patterns = [
            r'<div[^>]*class=["\'][^"\']*step[^"\']*["\'][^>]*>(.*?)</div>',
            r'<li[^>]*class=["\'][^"\']*step[^"\']*["\'][^>]*>(.*?)</li>',
            r'data-step=["\']([^"\']+)["\']'
        ]
        
        step_counter = 1
        for pattern in step_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Clean HTML tags and extract text
                step_text = re.sub(r'<[^>]+>', '', match).strip()
                if step_text and len(step_text) > 10:  # Minimum meaningful length
                    steps.append({
                        'title': f"Step {step_counter}",
                        'description': step_text[:200] + "..." if len(step_text) > 200 else step_text,
                        'type': 'instruction',
                        'order': step_counter
                    })
                    step_counter += 1
                    
        return steps
    
    def _scan_route_files(self):
        """Scan route files for simulation references"""
        simulations = []
        route_files = []
        
        # Find route files
        for root, dirs, files in os.walk('.'):
            for file in files:
                if 'route' in file.lower() and file.endswith('.py'):
                    route_files.append(os.path.join(root, file))
                    
        for route_file in route_files:
            try:
                with open(route_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for simulation route definitions
                route_patterns = [
                    r"@\w+\.route\(['\"]([^'\"]*simulation[^'\"]*)['\"]",
                    r"render_template\(['\"]([^'\"]*simulation[^'\"]*\.html)['\"]"
                ]
                
                for pattern in route_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        template_path = self._find_template_file(match)
                        if template_path and os.path.exists(template_path):
                            sim_data = self._parse_simulation_file(template_path)
                            if sim_data:
                                simulations.append(sim_data)
                                
            except (UnicodeDecodeError, IOError):
                pass
                
        return simulations
    
    def _find_template_file(self, template_name):
        """Find the full path to a template file"""
        template_dirs = ['templates', 'templates/user', 'templates/admin']
        
        for template_dir in template_dirs:
            full_path = os.path.join(template_dir, template_name)
            if os.path.exists(full_path):
                return full_path
                
        return None
    
    def _infer_simulation_type(self, filepath, content):
        """Infer simulation type from content"""
        type_indicators = {
            'network': ['network', 'routing', 'switch', 'router', 'ip', 'subnet'],
            'security': ['security', 'firewall', 'encryption', 'attack', 'vulnerability'],
            'troubleshooting': ['troubleshoot', 'debug', 'problem', 'issue', 'fix'],
            'configuration': ['config', 'setup', 'install', 'configure']
        }
        
        content_lower = content.lower()
        filepath_lower = filepath.lower()
        
        for sim_type, indicators in type_indicators.items():
            if any(indicator in content_lower or indicator in filepath_lower for indicator in indicators):
                return sim_type
                
        return 'mixed'
    
    def _infer_difficulty(self, content):
        """Infer difficulty level from content"""
        difficulty_indicators = {
            'beginner': ['basic', 'intro', 'beginner', 'start', 'simple'],
            'intermediate': ['intermediate', 'medium', 'regular'],
            'advanced': ['advanced', 'complex', 'difficult', 'expert']
        }
        
        content_lower = content.lower()
        
        for difficulty, indicators in difficulty_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return difficulty
                
        return 'intermediate'  # Default
    
    def _estimate_duration(self, content):
        """Estimate simulation duration from content"""
        # Look for explicit duration mentions
        duration_patterns = [
            r'(\d+)\s*(?:minute|min)',
            r'(\d+)\s*(?:hour|hr)',
            r'duration.*?(\d+)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, content.lower())
            if match:
                duration = int(match.group(1))
                if 'hour' in pattern or 'hr' in pattern:
                    duration *= 60
                return min(max(duration, 10), 180)  # Clamp between 10-180 minutes
                
        # Estimate based on content length
        content_length = len(content)
        if content_length < 1000:
            return 15
        elif content_length < 5000:
            return 30
        elif content_length < 10000:
            return 45
        else:
            return 60
    
    def _normalize_simulation_data(self, filepath, data):
        """Normalize simulation data to standard format"""
        if not data:
            return None
            
        normalized = {
            'title': data.get('title', 'Imported Simulation'),
            'description': data.get('description', 'Simulation imported from static content'),
            'simulation_type': data.get('type', data.get('simulation_type', 'mixed')),
            'difficulty': data.get('difficulty', 'intermediate'),
            'category': data.get('category', 'General'),
            'estimated_duration': data.get('estimated_duration', 30),
            'learning_objectives': data.get('learning_objectives', data.get('objectives', [])),
            'step_definitions': data.get('steps', data.get('step_definitions', [])),
            'validation_rules': data.get('validation_rules', {}),
            'scoring_config': data.get('scoring_config', {'total_points': 100}),
            'tags': data.get('tags', []),
            'source_file': filepath,
            'created_by': 'migration_script',
            'is_active': True
        }
        
        # Ensure steps have required fields
        for i, step in enumerate(normalized['step_definitions']):
            if isinstance(step, str):
                # Convert simple string steps to proper format
                normalized['step_definitions'][i] = {
                    'title': f"Step {i + 1}",
                    'description': step,
                    'type': 'instruction',
                    'order': i + 1
                }
            else:
                # Ensure required fields exist
                step.setdefault('title', f"Step {i + 1}")
                step.setdefault('type', 'instruction')
                step.setdefault('order', i + 1)
                
        return normalized
    
    def migrate_simulations(self, simulations):
        """Migrate simulations to database"""
        print(f"\nMigrating {len(simulations)} simulations...")
        
        for sim_data in simulations:
            try:
                # Check if simulation already exists
                existing = Simulation.query.filter_by(title=sim_data['title']).first()
                
                if existing and not self.force:
                    print(f"⚠️  Skipping '{sim_data['title']}' (already exists)")
                    self.stats['skipped_simulations'] += 1
                    continue
                    
                if self.dry_run:
                    print(f"🔍 Would migrate: '{sim_data['title']}'")
                    self.stats['migrated_simulations'] += 1
                    continue
                    
                # Create or update simulation
                if existing:
                    simulation = existing
                    print(f"🔄 Updating existing simulation: '{sim_data['title']}'")
                else:
                    simulation = Simulation()
                    print(f"✅ Creating new simulation: '{sim_data['title']}'")
                    
                # Set simulation properties
                for key, value in sim_data.items():
                    if hasattr(simulation, key) and key != 'id':
                        setattr(simulation, key, value)
                        
                # Set creation metadata
                simulation.created_at = datetime.utcnow()
                simulation.updated_at = datetime.utcnow()
                
                if not existing:
                    db.session.add(simulation)
                    
                db.session.commit()
                self.stats['migrated_simulations'] += 1
                
            except Exception as e:
                error_msg = f"Error migrating '{sim_data.get('title', 'Unknown')}': {str(e)}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)
                db.session.rollback()
    
    def run(self):
        """Run the complete migration process"""
        print("=== RiddleNet Simulation Migration ===\n")
        
        try:
            self.initialize_app()
            
            print("Scanning for simulation content...")
            simulations = self.scan_static_simulations()
            
            if not simulations:
                print("No simulation content found to migrate.")
                return
                
            print(f"Found {len(simulations)} simulations to migrate.")
            
            if self.dry_run:
                print("\n=== DRY RUN MODE - No changes will be made ===")
                
            self.migrate_simulations(simulations)
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            raise
        finally:
            if self.app_context:
                self.app_context.pop()
    
    def print_summary(self):
        """Print migration summary"""
        print("\n=== Migration Summary ===")
        print(f"Files scanned: {self.stats['scanned_files']}")
        print(f"Simulations found: {self.stats['found_simulations']}")
        print(f"Simulations migrated: {self.stats['migrated_simulations']}")
        print(f"Simulations skipped: {self.stats['skipped_simulations']}")
        
        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more errors")
                
        print("\nMigration completed!")

def main():
    parser = argparse.ArgumentParser(
        description="Migrate static simulation content to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate_simulations.py --dry-run    # Preview what would be migrated
  python migrate_simulations.py --backup     # Create backup before migration
  python migrate_simulations.py --force      # Overwrite existing simulations
        """
    )
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be migrated without making changes')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing simulations with same name')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup of existing database before migration')
    
    args = parser.parse_args()
    
    migrator = SimulationMigrator(
        dry_run=args.dry_run,
        force=args.force,
        backup=args.backup
    )
    
    migrator.run()

if __name__ == '__main__':
    main()

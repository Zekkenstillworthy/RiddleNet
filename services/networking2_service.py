"""
Networking 2 Service - Complete Implementation
Enhanced service for Networking 2 course content with full OOP architecture
Date: June 11, 2025
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import logging
import re

# Import the updated comprehensive content
from networking2_updated_content import get_networking2_content

logger = logging.getLogger(__name__)


@dataclass
class LessonMetadata:
    """Metadata for a single lesson"""
    id: str
    title: str
    description: str
    module_id: str
    source_file: Optional[str] = None
    difficulty: str = "intermediate"
    estimated_time: int = 60
    topics: List[str] = None
    prerequisites: List[str] = None
    learning_objectives: List[str] = None
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = []
        if self.prerequisites is None:
            self.prerequisites = []
        if self.learning_objectives is None:
            self.learning_objectives = []


@dataclass
class ModuleMetadata:
    """Metadata for a module"""
    id: str
    title: str
    description: str
    lesson_count: int
    total_estimated_time: int
    difficulty_level: str = "intermediate"
    topics_covered: List[str] = None
    
    def __post_init__(self):
        if self.topics_covered is None:
            self.topics_covered = []


class BaseNetworkingService(ABC):
    """Abstract base class for networking course services"""
    
    def __init__(self, course_name: str):
        self.course_name = course_name
        self._content_data: Dict[str, Any] = {}
        self._lesson_cache: Dict[str, LessonMetadata] = {}
        self._module_cache: Dict[str, ModuleMetadata] = {}
        self._initialized = False
        
        # Load and validate content
        self._load_content()
        self._validate_content()
        self._build_caches()
        self._initialized = True
        
        logger.info(f"✅ {self.course_name} service initialized successfully")
    
    @abstractmethod
    def _load_content(self) -> None:
        """Load course content - must be implemented by subclasses"""
        pass
    
    def _validate_content(self) -> None:
        """Validate loaded content structure"""
        if not self._content_data:
            raise ValueError(f"No content loaded for {self.course_name}")
        
        # Perform content validation
        validator = NetworkingContentValidator(self._content_data, self.course_name)
        validator.validate()
    
    def _build_caches(self) -> None:
        """Build metadata caches for performance"""
        for lesson_id, lesson_data in self._content_data.items():
            # Extract module ID from lesson ID
            if lesson_id.startswith('net2_'):
                module_id = lesson_id.split('_')[1].split('.')[0]
            else:
                module_id = lesson_id.split('.')[0]
            
            # Create lesson metadata
            self._lesson_cache[lesson_id] = LessonMetadata(
                id=lesson_id,
                title=lesson_data.get('title', 'Untitled'),
                description=lesson_data.get('description', ''),
                module_id=module_id,
                difficulty=lesson_data.get('difficulty', 'intermediate'),
                estimated_time=lesson_data.get('estimated_time', 45),
                topics=lesson_data.get('topics', []),
                prerequisites=lesson_data.get('prerequisites', []),
                learning_objectives=lesson_data.get('learning_objectives', [])
            )
        
        # Build module cache
        self._build_module_cache()
    
    def _build_module_cache(self) -> None:
        """Build module metadata cache"""
        modules: Dict[str, List[LessonMetadata]] = {}
        
        # Group lessons by module
        for lesson in self._lesson_cache.values():
            if lesson.module_id not in modules:
                modules[lesson.module_id] = []
            modules[lesson.module_id].append(lesson)
        
        # Create module metadata
        for module_id, lessons in modules.items():
            total_time = sum(lesson.estimated_time for lesson in lessons)
            all_topics = set()
            for lesson in lessons:
                all_topics.update(lesson.topics)
            
            self._module_cache[module_id] = ModuleMetadata(
                id=module_id,
                title=self._get_module_title(module_id),
                description=f"Advanced concepts in {self._get_module_title(module_id).lower()}",
                lesson_count=len(lessons),
                total_estimated_time=total_time,
                difficulty_level='intermediate',
                topics_covered=list(all_topics)
            )
    
    @abstractmethod
    def _get_module_title(self, module_id: str) -> str:
        """Get module title - must be implemented by subclasses"""
        pass


class NetworkingContentValidator:
    """Validates networking course content structure"""
    
    def __init__(self, content_data: Dict[str, Any], course_name: str):
        self.content_data = content_data
        self.course_name = course_name
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> None:
        """Perform comprehensive content validation"""
        self._validate_structure()
        self._validate_lesson_content()
        self._validate_metadata_consistency()
        
        if self.errors:
            error_msg = f"Content validation failed for {self.course_name}:\n" + "\n".join(self.errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if self.warnings:
            warning_msg = f"Content validation warnings for {self.course_name}:\n" + "\n".join(self.warnings)
            logger.warning(warning_msg)
        
        logger.info(f"✅ Content validation passed for {self.course_name}")
    
    def _validate_structure(self) -> None:
        """Validate basic content structure"""
        if not isinstance(self.content_data, dict):
            self.errors.append("Content data must be a dictionary")
            return
        
        if not self.content_data:
            self.errors.append("Content data is empty")
            return
        
        # Check lesson ID format
        for lesson_id in self.content_data.keys():
            if not self._is_valid_lesson_id(lesson_id):
                self.warnings.append(f"Unusual lesson ID format: {lesson_id}")
    
    def _validate_lesson_content(self) -> None:
        """Validate individual lesson content"""
        required_fields = ['title', 'content']
        recommended_fields = ['description', 'estimated_time', 'difficulty']
        
        for lesson_id, lesson_data in self.content_data.items():
            if not isinstance(lesson_data, dict):
                self.errors.append(f"Lesson {lesson_id}: content must be a dictionary")
                continue
            
            # Check required fields
            for field in required_fields:
                if field not in lesson_data:
                    self.errors.append(f"Lesson {lesson_id}: missing required field '{field}'")
            
            # Check recommended fields
            for field in recommended_fields:
                if field not in lesson_data:
                    self.warnings.append(f"Lesson {lesson_id}: missing recommended field '{field}'")
    
    def _validate_metadata_consistency(self) -> None:
        """Validate metadata consistency across lessons"""
        # Check for consistent module structure
        modules = set()
        for lesson_id in self.content_data.keys():
            if lesson_id.startswith('net2_'):
                module_id = lesson_id.split('_')[1].split('.')[0]
            else:
                module_id = lesson_id.split('.')[0]
            modules.add(module_id)
        
        logger.info(f"📚 Found modules for {self.course_name}: {sorted(modules)}")
    
    def _is_valid_lesson_id(self, lesson_id: str) -> bool:
        """Check if lesson ID follows expected format"""
        # Accept formats like "1.1", "2.3", "net2_1.1", etc.
        patterns = [
            r'^\d+\.\d+$',  # "1.1" format
            r'^net2_\d+\.\d+$',  # "net2_1.1" format
        ]
        return any(re.match(pattern, lesson_id) for pattern in patterns)


# =============================================================================
# Networking 2 Specific Implementation
# =============================================================================

class Networking2Service(BaseNetworkingService):
    """Enhanced service for Networking 2 course with full OOP architecture"""
    
    def __init__(self):
        super().__init__("Networking 2")
    
    def _load_content(self) -> None:
        """Load Networking 2 content"""
        try:
            self._content_data = get_networking2_content()
            logger.info(f"📚 Loaded {len(self._content_data)} lessons for Networking 2")
        except Exception as e:
            logger.error(f"Failed to load Networking 2 content: {e}")
            raise
    
    def _get_module_title(self, module_id: str) -> str:
        """Get module title for Networking 2"""
        module_titles = {
            '1': 'Routing Fundamentals',
            '2': 'Dynamic Routing Protocols',
            '3': 'Routing Information Protocol (RIP)',
            '4': 'Enhanced Interior Gateway Routing Protocol (EIGRP)',
            '5': 'Open Shortest Path First (OSPF)',
            '6': 'Network Security and VPN',
            '7': 'Advanced Routing Concepts'
        }
        return module_titles.get(module_id, f'Module {module_id}')
    
    # =============================================================================
    # Core Content Access Methods
    # =============================================================================
    
    def get_lesson_content(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Get complete lesson content by ID"""
        if not self._initialized:
            logger.error("Service not initialized")
            return None
        
        if lesson_id not in self._content_data:
            logger.warning(f"Lesson {lesson_id} not found")
            return None
        
        lesson_data = self._content_data[lesson_id].copy()
        
        # Add metadata
        if lesson_id in self._lesson_cache:
            metadata = self._lesson_cache[lesson_id]
            lesson_data.update({
                'metadata': {
                    'difficulty': metadata.difficulty,
                    'estimated_time': metadata.estimated_time,
                    'topics': metadata.topics,
                    'prerequisites': metadata.prerequisites,
                    'learning_objectives': metadata.learning_objectives,
                    'module_id': metadata.module_id,
                    'module_title': self._get_module_title(metadata.module_id)
                }
            })
        
        return lesson_data
    
    def get_all_lessons(self) -> Dict[str, Any]:
        """Get all lesson data"""
        return self._content_data.copy()
    
    def get_lesson_titles(self) -> Dict[str, str]:
        """Get mapping of lesson ID to title"""
        return {
            lesson_id: metadata.title 
            for lesson_id, metadata in self._lesson_cache.items()
        }
    
    def get_lessons_by_module(self, module_id: str) -> Dict[str, Any]:
        """Get all lessons for a specific module"""
        module_lessons = {}
        for lesson_id, lesson_data in self._content_data.items():
            # Handle both formats: "1.1" and "net2_1.1"
            if lesson_id.startswith('net2_'):
                lesson_module_id = lesson_id.split('_')[1].split('.')[0]
            else:
                lesson_module_id = lesson_id.split('.')[0]
            
            if lesson_module_id == module_id:
                module_lessons[lesson_id] = lesson_data
        
        return module_lessons
    
    # =============================================================================
    # Module and Structure Methods
    # =============================================================================
    
    def get_module_metadata(self) -> Dict[str, ModuleMetadata]:
        """Get metadata for all modules"""
        return self._module_cache.copy()
    
    def get_detailed_module_structure(self) -> Dict[str, Any]:
        """Get detailed module structure with lessons"""
        structure = {}
        
        for module_id, module_meta in self._module_cache.items():
            module_lessons = self.get_lessons_by_module(module_id)
            structure[module_id] = {
                'id': module_id,
                'title': module_meta.title,
                'description': module_meta.description,
                'lesson_count': module_meta.lesson_count,
                'total_estimated_time': module_meta.total_estimated_time,
                'difficulty_level': module_meta.difficulty_level,
                'topics_covered': module_meta.topics_covered,
                'lessons': [
                    {
                        'id': lesson_id,
                        'title': lesson_data.get('title', 'Untitled'),
                        'description': lesson_data.get('description', ''),
                        'estimated_time': lesson_data.get('estimated_time', 45),
                        'difficulty': lesson_data.get('difficulty', 'intermediate')
                    }
                    for lesson_id, lesson_data in sorted(module_lessons.items())
                ]
            }
        
        return structure
    
    # =============================================================================
    # Navigation and Progress Methods  
    # =============================================================================
    
    def get_next_lesson(self, current_lesson_id: str) -> Optional[str]:
        """Get the next lesson in sequence"""
        lesson_ids = sorted(self._content_data.keys())
        try:
            current_index = lesson_ids.index(current_lesson_id)
            if current_index < len(lesson_ids) - 1:
                return lesson_ids[current_index + 1]
        except ValueError:
            logger.warning(f"Current lesson {current_lesson_id} not found")
        return None
    
    def get_previous_lesson(self, current_lesson_id: str) -> Optional[str]:
        """Get the previous lesson in sequence"""
        lesson_ids = sorted(self._content_data.keys())
        try:
            current_index = lesson_ids.index(current_lesson_id)
            if current_index > 0:
                return lesson_ids[current_index - 1]
        except ValueError:
            logger.warning(f"Current lesson {current_lesson_id} not found")
        return None
    
    def get_progress_info(self, completed_lessons: List[str]) -> Dict[str, Any]:
        """Get detailed progress information"""
        total_lessons = len(self._content_data)
        completed_count = len([l for l in completed_lessons if l in self._content_data])
        
        # Calculate module progress
        module_progress = {}
        for module_id, module_meta in self._module_cache.items():
            module_lessons = self.get_lessons_by_module(module_id)
            module_completed = len([l for l in completed_lessons if l in module_lessons])
            
            module_progress[module_id] = {
                'title': module_meta.title,
                'total': len(module_lessons),
                'completed': module_completed,
                'percentage': (module_completed / len(module_lessons)) * 100 if module_lessons else 0
            }
        
        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_count,
            'completion_percentage': (completed_count / total_lessons) * 100 if total_lessons > 0 else 0,
            'module_progress': module_progress,
            'estimated_total_time': sum(m.total_estimated_time for m in self._module_cache.values()),
            'estimated_remaining_time': sum(
                lesson.estimated_time for lesson in self._lesson_cache.values()
                if lesson.id not in completed_lessons
            )
        }
    
    # =============================================================================
    # Search and Discovery Methods
    # =============================================================================
    
    def search_lessons(self, query: str, search_in: List[str] = None) -> List[Dict[str, Any]]:
        """Search lessons by query with enhanced options"""
        if search_in is None:
            search_in = ['title', 'content', 'description', 'topics']
        
        query_lower = query.lower()
        results = []
        
        for lesson_id, lesson_data in self._content_data.items():
            score = 0
            matched_fields = []
            
            # Search in different fields with different weights
            if 'title' in search_in and 'title' in lesson_data:
                if query_lower in lesson_data['title'].lower():
                    score += 10
                    matched_fields.append('title')
            
            if 'description' in search_in and 'description' in lesson_data:
                if query_lower in lesson_data['description'].lower():
                    score += 5
                    matched_fields.append('description')
            
            if 'content' in search_in and 'content' in lesson_data:
                content_text = str(lesson_data['content']).lower()
                if query_lower in content_text:
                    score += 3
                    matched_fields.append('content')
            
            if 'topics' in search_in and lesson_id in self._lesson_cache:
                lesson_topics = [topic.lower() for topic in self._lesson_cache[lesson_id].topics]
                if any(query_lower in topic for topic in lesson_topics):
                    score += 8
                    matched_fields.append('topics')
            
            # Add result if score > 0
            if score > 0:
                results.append({
                    'lesson_id': lesson_id,
                    'title': lesson_data.get('title', 'Untitled'),
                    'description': lesson_data.get('description', ''),
                    'score': score,
                    'matched_fields': matched_fields,
                    'module_id': self._lesson_cache[lesson_id].module_id if lesson_id in self._lesson_cache else None
                })
        
        # Sort by score descending
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def get_lessons_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Get lessons that contain any of the specified tags"""
        matching_lessons = []
        
        for lesson_id, metadata in self._lesson_cache.items():
            lesson_tags = [topic.lower() for topic in metadata.topics]
            if any(tag.lower() in lesson_tags for tag in tags):
                lesson_data = self._content_data[lesson_id]
                matching_lessons.append({
                    'lesson_id': lesson_id,
                    'title': metadata.title,
                    'description': metadata.description,
                    'topics': metadata.topics,
                    'module_id': metadata.module_id
                })
        
        return matching_lessons
    
    def get_all_tags(self) -> Set[str]:
        """Get all unique tags/topics across all lessons"""
        all_tags = set()
        for metadata in self._lesson_cache.values():
            all_tags.update(metadata.topics)
        return all_tags
    
    # =============================================================================
    # Statistics and Analytics Methods
    # =============================================================================
    
    def get_course_statistics(self) -> Dict[str, Any]:
        """Get comprehensive course statistics"""
        total_lessons = len(self._content_data)
        total_modules = len(self._module_cache)
        
        # Calculate difficulty distribution
        difficulty_count = {}
        total_estimated_time = 0
        
        for metadata in self._lesson_cache.values():
            difficulty = metadata.difficulty
            difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1
            total_estimated_time += metadata.estimated_time
        
        # Get all topics
        all_topics = self.get_all_tags()
        
        return {
            'course_name': self.course_name,
            'total_lessons': total_lessons,
            'total_modules': total_modules,
            'total_estimated_time_minutes': total_estimated_time,
            'total_estimated_time_hours': round(total_estimated_time / 60, 1),
            'difficulty_distribution': difficulty_count,
            'total_topics': len(all_topics),
            'topics_list': sorted(all_topics),
            'average_lesson_time': round(total_estimated_time / total_lessons, 1) if total_lessons > 0 else 0,
            'modules': {
                module_id: {
                    'title': meta.title,
                    'lesson_count': meta.lesson_count,
                    'estimated_time': meta.total_estimated_time
                }
                for module_id, meta in self._module_cache.items()
            }
        }
    
    # =============================================================================
    # Validation Methods
    # =============================================================================
    
    def validate_lesson_id(self, lesson_id: str) -> bool:
        """Validate if lesson ID exists"""
        return lesson_id in self._content_data
    
    def get_course_summary(self) -> Dict[str, Any]:
        """Get course summary information"""
        stats = self.get_course_statistics()
        return {
            'name': self.course_name,
            'description': f'Advanced networking course covering {stats["total_modules"]} modules',
            'total_lessons': stats['total_lessons'],
            'total_modules': stats['total_modules'],
            'estimated_duration': f"{stats['total_estimated_time_hours']} hours",
            'difficulty_levels': list(stats['difficulty_distribution'].keys()),
            'main_topics': list(stats['topics_list'][:10])  # Top 10 topics
        }


# =============================================================================
# Global Service Instance and Legacy Support
# =============================================================================

# Create global service instance
networking2_service = Networking2Service()


# =============================================================================
# Legacy Function Wrappers for Backward Compatibility
# =============================================================================

def get_all_networking2_modules_structure():
    """Legacy function - use networking2_service.get_detailed_module_structure()"""
    return networking2_service.get_detailed_module_structure()


def get_networking2_lesson_content_by_id(lesson_id):
    """Legacy function - use networking2_service.get_lesson_content()"""
    return networking2_service.get_lesson_content(lesson_id)


def get_all_networking2_lessons():
    """Legacy function - use networking2_service.get_all_lessons()"""
    return networking2_service.get_all_lessons()


def get_networking2_module_progress(completed_lessons):
    """Legacy function - use networking2_service.get_progress_info()"""
    return networking2_service.get_progress_info(completed_lessons)


def get_next_networking2_lesson(current_lesson_id):
    """Legacy function - use networking2_service.get_next_lesson()"""
    return networking2_service.get_next_lesson(current_lesson_id)


def get_previous_networking2_lesson(current_lesson_id):
    """Legacy function - use networking2_service.get_previous_lesson()"""
    return networking2_service.get_previous_lesson(current_lesson_id)


def get_networking2_lesson_by_module(module_id):
    """Legacy function - use networking2_service.get_lessons_by_module()"""
    return networking2_service.get_lessons_by_module(module_id)


def search_networking2_lessons(query):
    """Legacy function - use networking2_service.search_lessons()"""
    return networking2_service.search_lessons(query)


def get_networking2_statistics():
    """Legacy function - use networking2_service.get_course_statistics()"""
    return networking2_service.get_course_statistics()


if __name__ == "__main__":
    # Test the service
    print("=== Networking 2 Service Test ===")
    
    try:
        service = networking2_service
        print(f"✅ Service initialized successfully")
        print(f"📚 Total lessons loaded: {len(service.get_all_lessons())}")
        
        # Test course statistics
        stats = service.get_course_statistics()
        print(f"📊 Course Statistics:")
        print(f"   - Total modules: {stats['total_modules']}")
        print(f"   - Estimated time: {stats['total_estimated_time_hours']} hours")
        print(f"   - Main topics: {stats['topics_list'][:5]}")
        
        # Test module structure
        modules = service.get_detailed_module_structure()
        print(f"🏗️  Module Structure:")
        for module_id, module_info in modules.items():
            print(f"   - Module {module_id}: {module_info['title']} ({module_info['lesson_count']} lessons)")
        
        # Test search functionality
        search_results = service.search_lessons("routing")
        print(f"🔍 Search Results for 'routing': {len(search_results)} lessons found")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

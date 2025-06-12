"""
Networking 1 Service - Complete Implementation
Enhanced service for Networking 1 course content
Date: June 11, 2025
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Import the updated comprehensive content
from networking1_updated_content import get_networking1_content

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
    estimated_time: int = 45
    topics: List[str] = None
    prerequisites: List[str] = None


class Networking1Service:
    """
    Service class for Networking 1 course content and operations
    """
    
    def __init__(self):
        self.content_data = get_networking1_content()
        self._lesson_metadata = self._build_lesson_metadata()
    
    def _build_lesson_metadata(self) -> Dict[str, LessonMetadata]:
        """Build metadata for all lessons"""
        metadata = {}
        
        for lesson_id, lesson_data in self.content_data.items():
            metadata[lesson_id] = LessonMetadata(
                id=lesson_id,
                title=lesson_data.get('title', 'Untitled Lesson'),
                description=self._extract_description(lesson_data.get('content', '')),
                module_id=lesson_id.split('.')[0],
                source_file=lesson_data.get('source_file'),
                topics=self._extract_topics(lesson_data.get('content', ''))
            )
        
        return metadata
    
    def _extract_description(self, content: str) -> str:
        """Extract lesson description from content"""
        if 'lesson-description' in content:
            start = content.find('<div class="lesson-description">') + len('<div class="lesson-description">')
            end = content.find('</div>', start)
            desc_html = content[start:end]
            # Remove HTML tags for description
            import re
            desc_text = re.sub(r'<[^>]+>', '', desc_html)
            return desc_text.strip()[:200] + "..." if len(desc_text) > 200 else desc_text.strip()
        return "Networking fundamentals lesson"
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract key topics from lesson content"""
        topics = []
        if 'Computer Networks' in content:
            topics.append('Computer Networks')
        if 'OSI Model' in content:
            topics.append('OSI Model')
        if 'TCP/IP' in content:
            topics.append('TCP/IP')
        if 'Ethernet' in content:
            topics.append('Ethernet')
        if 'Routing' in content:
            topics.append('Routing')
        if 'Application Layer' in content:
            topics.append('Application Layer')
        if 'Network Architecture' in content:
            topics.append('Network Architecture')
        return topics
    
    def get_all_lessons(self) -> Dict[str, Dict[str, Any]]:
        """Get all lessons with their content and metadata"""
        result = {}
        for lesson_id, content in self.content_data.items():
            result[lesson_id] = {
                **content,
                'metadata': self._lesson_metadata.get(lesson_id)
            }
        return result
    
    def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Get specific lesson by ID"""
        if lesson_id in self.content_data:
            return {
                **self.content_data[lesson_id],
                'metadata': self._lesson_metadata.get(lesson_id)
            }
        return None
    
    def get_lessons_by_module(self, module_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all lessons for a specific module"""
        lessons = {}
        for lesson_id, content in self.content_data.items():
            if lesson_id.startswith(module_id + '.'):
                lessons[lesson_id] = {
                    **content,
                    'metadata': self._lesson_metadata.get(lesson_id)
                }
        return lessons
    
    def get_module_summary(self, module_id: str) -> Dict[str, Any]:
        """Get summary information for a module"""
        lessons = self.get_lessons_by_module(module_id)
        
        total_lessons = len(lessons)
        total_estimated_time = sum(
            meta.estimated_time for meta in [lesson['metadata'] for lesson in lessons.values()]
        )
        
        all_topics = set()
        for lesson in lessons.values():
            if lesson['metadata'] and lesson['metadata'].topics:
                all_topics.update(lesson['metadata'].topics)
        
        module_titles = {
            '1': 'Computer Network Fundamentals',
            '2': 'Network Technologies',
            '3': 'Transport Layer Protocols',
            '4': 'Application Layer and Advanced Concepts'
        }
        
        return {
            'module_id': module_id,
            'title': module_titles.get(module_id, f'Module {module_id}'),
            'lesson_count': total_lessons,
            'estimated_time': total_estimated_time,
            'topics': list(all_topics),
            'lessons': list(lessons.keys())
        }
    
    def search_content(self, query: str) -> List[Dict[str, Any]]:
        """Search for lessons containing specific content"""
        results = []
        query_lower = query.lower()
        
        for lesson_id, lesson_data in self.content_data.items():
            content = lesson_data.get('content', '').lower()
            title = lesson_data.get('title', '').lower()
            
            if query_lower in content or query_lower in title:
                results.append({
                    'lesson_id': lesson_id,
                    'title': lesson_data.get('title'),
                    'relevance_score': content.count(query_lower) + title.count(query_lower) * 2,
                    'metadata': self._lesson_metadata.get(lesson_id)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results
    
    def get_course_outline(self) -> Dict[str, Any]:
        """Get complete course outline"""
        modules = {}
        
        # Group lessons by module
        for lesson_id in self.content_data.keys():
            module_id = lesson_id.split('.')[0]
            if module_id not in modules:
                modules[module_id] = self.get_module_summary(module_id)
        
        return {
            'course_title': 'Networking 1 - Computer Network Fundamentals',
            'total_modules': len(modules),
            'total_lessons': len(self.content_data),
            'modules': modules
        }
    
    def get_lesson_navigation(self, current_lesson_id: str) -> Dict[str, Optional[str]]:
        """Get navigation information for a lesson"""
        lesson_ids = sorted(self.content_data.keys())
        
        try:
            current_index = lesson_ids.index(current_lesson_id)
            
            previous_lesson = lesson_ids[current_index - 1] if current_index > 0 else None
            next_lesson = lesson_ids[current_index + 1] if current_index < len(lesson_ids) - 1 else None
            
            return {
                'previous': previous_lesson,
                'current': current_lesson_id,
                'next': next_lesson,
                'total_lessons': len(lesson_ids),
                'current_position': current_index + 1
            }
        except ValueError:
            return {
                'previous': None,
                'current': current_lesson_id,
                'next': None,
                'total_lessons': len(lesson_ids),
                'current_position': 0
            }
    
    def validate_lesson_id(self, lesson_id: str) -> bool:
        """Validate if lesson ID exists"""
        return lesson_id in self.content_data
    
    def get_lesson_topics(self, lesson_id: str) -> List[str]:
        """Get topics covered in a specific lesson"""
        if lesson_id in self._lesson_metadata:
            return self._lesson_metadata[lesson_id].topics or []
        return []
    
    def get_course_statistics(self) -> Dict[str, Any]:
        """Get comprehensive course statistics"""
        total_lessons = len(self.content_data)
        
        # Calculate module distribution
        modules = set()
        difficulty_count = {}
        total_estimated_time = 0
        
        for metadata in self._lesson_metadata.values():
            modules.add(metadata.module_id)
            difficulty = metadata.difficulty
            difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1
            total_estimated_time += metadata.estimated_time
        
        # Get all topics
        all_topics = set()
        for metadata in self._lesson_metadata.values():
            all_topics.update(metadata.topics)
        
        return {
            'course_name': 'Networking 1',
            'total_lessons': total_lessons,
            'total_modules': len(modules),
            'total_estimated_time_minutes': total_estimated_time,
            'total_estimated_time_hours': round(total_estimated_time / 60, 1),
            'difficulty_distribution': difficulty_count,
            'total_topics': len(all_topics),
            'topics_list': sorted(all_topics),
            'average_lesson_time': round(total_estimated_time / total_lessons, 1) if total_lessons > 0 else 0,
            'modules': {
                module_id: {
                    'title': self.get_module_summary(module_id)['title'],
                    'lesson_count': len(self.get_lessons_by_module(module_id)),
                    'estimated_time': self.get_module_summary(module_id)['estimated_time']
                }
                for module_id in sorted(modules)
            }
        }
    
    def get_detailed_module_structure(self) -> Dict[str, Any]:
        """Get detailed module structure with lessons"""
        structure = {}
        
        # Get all module IDs
        modules = set()
        for lesson_id in self.content_data.keys():
            module_id = lesson_id.split('.')[0]
            modules.add(module_id)
        
        for module_id in sorted(modules):
            module_summary = self.get_module_summary(module_id)
            module_lessons = self.get_lessons_by_module(module_id)
            
            structure[module_id] = {
                'id': module_id,
                'title': module_summary['title'],
                'lesson_count': module_summary['lesson_count'],
                'total_estimated_time': module_summary['estimated_time'],
                'topics': module_summary['topics'],
                'lessons': [
                    {
                        'id': lesson_id,
                        'title': lesson_data.get('title', 'Untitled'),
                        'description': self._lesson_metadata[lesson_id].description if lesson_id in self._lesson_metadata else '',
                        'estimated_time': lesson_data.get('estimated_time', 45),
                        'difficulty': lesson_data.get('difficulty', 'intermediate')
                    }
                    for lesson_id, lesson_data in sorted(module_lessons.items())
                ]
            }
        
        return structure
    
    def get_progress_info(self, completed_lessons: List[str]) -> Dict[str, Any]:
        """Get detailed progress information"""
        total_lessons = len(self.content_data)
        completed_count = len([l for l in completed_lessons if l in self.content_data])
        
        # Calculate module progress
        modules = set()
        for lesson_id in self.content_data.keys():
            module_id = lesson_id.split('.')[0]
            modules.add(module_id)
        
        module_progress = {}
        for module_id in modules:
            module_lessons = self.get_lessons_by_module(module_id)
            module_completed = len([l for l in completed_lessons if l in module_lessons])
            
            module_progress[module_id] = {
                'title': self.get_module_summary(module_id)['title'],
                'total': len(module_lessons),
                'completed': module_completed,
                'percentage': (module_completed / len(module_lessons)) * 100 if module_lessons else 0
            }
        
        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_count,
            'completion_percentage': (completed_count / total_lessons) * 100 if total_lessons > 0 else 0,
            'module_progress': module_progress,
            'estimated_total_time': sum(m.estimated_time for m in self._lesson_metadata.values()),
            'estimated_remaining_time': sum(
                meta.estimated_time for meta in self._lesson_metadata.values()
                if meta.id not in completed_lessons
            )
        }
    

# Global instance
networking1_service = Networking1Service()


def get_networking1_service():
    """Get the global Networking 1 service instance"""
    return networking1_service


# Utility functions for backward compatibility
def get_lesson_content(lesson_id: str) -> Optional[str]:
    """Get lesson content by ID"""
    lesson = networking1_service.get_lesson_by_id(lesson_id)
    return lesson.get('content') if lesson else None


def get_lesson_title(lesson_id: str) -> Optional[str]:
    """Get lesson title by ID"""
    lesson = networking1_service.get_lesson_by_id(lesson_id)
    return lesson.get('title') if lesson else None


def search_lessons(query: str) -> List[Dict[str, Any]]:
    """Search lessons by query"""
    return networking1_service.search_content(query)


if __name__ == "__main__":
    # Test the service
    service = get_networking1_service()
    print("Networking 1 Service initialized")
    print(f"Total lessons: {len(service.content_data)}")
    
    outline = service.get_course_outline()
    print(f"Course: {outline['course_title']}")
    print(f"Modules: {outline['total_modules']}")
    
    # Test searching
    search_results = service.search_content("OSI")
    print(f"Found {len(search_results)} lessons about OSI")
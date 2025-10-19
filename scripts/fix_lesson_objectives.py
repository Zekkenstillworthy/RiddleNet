"""
Fix corrupted learning objectives and key concepts in lessons.
The data is stored as JSON strings with concatenated words (no spaces).
This script will parse and properly format them with spaces.
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import app
from __init__ import db
from instructor.models.module import Lesson
import json

def add_spaces_to_camel_case(text):
    """
    Add spaces to camelCase or concatenated words.
    Example: "Understandnetworkfundamentals" -> "Understand network fundamentals"
    """
    # Add space before capital letters (except at the start)
    text = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
    return text

def fix_concatenated_string(text):
    """
    Fix strings where words were concatenated without spaces.
    Uses common patterns to identify word boundaries.
    """
    if not text or not isinstance(text, str):
        return text
    
    # Common networking/learning terms to help split
    patterns = [
        (r'(Understand)(network)', r'\1 \2'),
        (r'(Learn)(about)', r'\1 \2'),
        (r'(Apply)(network)', r'\1 \2'),
        (r'(network)(fundamentals)', r'\1 \2'),
        (r'(network)(protocols)', r'\1 \2'),
        (r'(network)(security)', r'\1 \2'),
        (r'(security)(principles)', r'\1 \2'),
    ]
    
    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # General camelCase splitting
    result = add_spaces_to_camel_case(result)
    
    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:]
    
    return result

def fix_json_string_field(field_value):
    """
    Parse a JSON string field and fix concatenated words.
    Handles both proper JSON arrays and string representations.
    """
    if not field_value:
        return []
    
    # If it's already a proper list, check if items need fixing
    if isinstance(field_value, list):
        return [fix_concatenated_string(item) for item in field_value]
    
    # If it's a string, try to parse as JSON
    if isinstance(field_value, str):
        try:
            parsed = json.loads(field_value)
            if isinstance(parsed, list):
                return [fix_concatenated_string(item) for item in parsed]
            elif isinstance(parsed, str):
                return [fix_concatenated_string(parsed)]
        except json.JSONDecodeError:
            # Not valid JSON, return as single item
            return [fix_concatenated_string(field_value)]
    
    return []

def main():
    with app.app_context():
        print("Starting lesson objectives fix...")
        print("="*60)
        
        # Get all lessons
        lessons = Lesson.query.all()
        fixed_count = 0
        
        for lesson in lessons:
            fixed = False
            original_objectives = lesson.learning_objectives
            original_concepts = lesson.key_concepts
            
            # Fix learning_objectives
            if lesson.learning_objectives:
                fixed_objectives = fix_json_string_field(lesson.learning_objectives)
                if fixed_objectives != lesson.learning_objectives:
                    print(f"\n✓ Lesson {lesson.id}: {lesson.title}")
                    print(f"  OLD objectives: {original_objectives}")
                    print(f"  NEW objectives: {fixed_objectives}")
                    lesson.learning_objectives = fixed_objectives
                    fixed = True
            
            # Fix key_concepts
            if lesson.key_concepts:
                fixed_concepts = fix_json_string_field(lesson.key_concepts)
                if fixed_concepts != lesson.key_concepts:
                    if not fixed:
                        print(f"\n✓ Lesson {lesson.id}: {lesson.title}")
                    print(f"  OLD concepts: {original_concepts}")
                    print(f"  NEW concepts: {fixed_concepts}")
                    lesson.key_concepts = fixed_concepts
                    fixed = True
            
            if fixed:
                fixed_count += 1
        
        print("\n" + "="*60)
        if fixed_count > 0:
            print(f"\nFound and fixed {fixed_count} lessons with concatenated text.")
            print("\nCommitting changes to database...")
            db.session.commit()
            print("✓ Database updated successfully!")
        else:
            print("\nNo issues found. All lessons have properly formatted objectives!")
        
        print("\n" + "="*60)
        print("Fix complete! Refresh your browser to see the changes.")
        print("="*60)

if __name__ == '__main__':
    main()

"""
Test the get_networking_lesson function with the same import logic
"""
import sys
import os

# Simulate the Flask context
class MockSession:
    def __contains__(self, key):
        return key == 'user_id'
    
    def get(self, key, default=None):
        if key == 'user_id':
            return 1
        return default

# Mock Flask dependencies
class MockJsonify:
    def __init__(self, data):
        self.data = data
    
    def __repr__(self):
        return f"JSON Response: {self.data}"

def jsonify(data):
    return MockJsonify(data)

# Add the session mock
session = MockSession()

# Test the import logic from our updated function
def test_get_networking_lesson(lesson_id):
    """Test the exact import logic from get_networking_lesson"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Load lesson content from extracted module files
    try:
        import sys
        import os
        # Add the root directory to Python path
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        from module_loader import get_module_lesson_content
        print(f"✅ Successfully imported module_loader from: {root_dir}")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        return jsonify({"error": f"Module loader import failed: {str(e)}"}), 500
    
    lesson_content = get_module_lesson_content()
    print(f"✅ Successfully loaded {len(lesson_content)} lessons")
    
    # Check if the requested lesson exists
    if lesson_id in lesson_content:
        print(f"✅ Found lesson {lesson_id}: {lesson_content[lesson_id]['title']}")
        return jsonify({
            "title": lesson_content[lesson_id]["title"],
            "content": lesson_content[lesson_id]["content"][:200] + "..."  # Truncate for display
        })
    else:
        print(f"❌ Lesson {lesson_id} not found")
        available_lessons = list(lesson_content.keys())
        print(f"Available lessons: {available_lessons}")
        return jsonify({"error": "Lesson not found"}), 404

if __name__ == "__main__":
    print("Testing get_networking_lesson function...")
    result = test_get_networking_lesson("1.1")
    print(f"Result: {result}")

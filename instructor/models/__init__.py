# Models package initialization
from instructor.models.user import InstructorUser, Instructor
from instructor.models.question import Question
from instructor.models.question_group import QuestionGroup
from instructor.models.essay_response import EssayResponse
from instructor.models.score import InstructorScore  # Using the renamed class
from instructor.models.topology import Topology
from instructor.models.troubleshooting import Troubleshooting
from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
# ClassTopic removed - content now organized under Modules
# Import the User model to make it available for relationships
from user.models.user import User
# Import TroubleshootingProgress lazily to avoid circular imports
# from instructor.models.troubleshooting_progress import TroubleshootingProgress

# Models package initialization
from admin.models.user import AdminUser
from admin.models.question import Question
from admin.models.question_group import QuestionGroup
from admin.models.essay_response import EssayResponse
from admin.models.score import AdminScore  # Using the renamed class
from admin.models.topology import Topology
from admin.models.troubleshooting import Troubleshooting
from admin.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
# ClassTopic removed - content now organized under Modules
# Import the User model to make it available for relationships
from user.models.user import User
# Import TroubleshootingProgress lazily to avoid circular imports
# from admin.models.troubleshooting_progress import TroubleshootingProgress

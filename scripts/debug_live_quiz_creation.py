import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("FLASK_ENV", "development")

from flask import json
from flask_login import login_user

from __init__ import create_app, db


def attempt_create(instructor_id: int = 3, question_group_id: int = 1, class_id: int = 7):
    app = create_app()
    with app.app_context():
        from instructor.models.user import Instructor
        from instructor.api.live_quiz_api import create_quiz_session

        instructor = Instructor.query.get(instructor_id)
        if not instructor:
            raise RuntimeError(f"Instructor {instructor_id} not found")

        payload = {
            "question_group_id": question_group_id,
            "class_id": class_id,
            "module_id": None,
            "lesson_id": None,
            "title": "Debug Live Quiz",
            "time_per_question": 30,
        }

        with app.test_request_context(
            "/instructor/api/live-quiz/create",
            method="POST",
            json=payload,
        ):
            login_user(instructor)
            response = create_quiz_session()
            if hasattr(response, "get_json"):
                body = response.get_json()
            else:
                body = response[0] if isinstance(response, tuple) else response
            status = response.status_code if hasattr(response, "status_code") else response[1] if isinstance(response, tuple) and len(response) > 1 else "?"
            print(f"status={status}")
            print(json.dumps(body, indent=2))


if __name__ == "__main__":
    attempt_create()

from typing import Dict, Any
from __init__ import db
from admin.models.rubric import Rubric, RubricCriterion


class RubricService:
    @staticmethod
    def create_rubric(name: str, description: str, created_by: int, criteria: list[dict]) -> Rubric:
        rub = Rubric(name=name, description=description, created_by=created_by)
        db.session.add(rub)
        db.session.flush()
        order = 1
        for c in criteria:
            rc = RubricCriterion(rubric_id=rub.id, title=c.get('title', 'Criterion'), description=c.get('description'), max_points=c.get('max_points', 0.0), weight=c.get('weight', 1.0), order_index=c.get('order_index', order))
            db.session.add(rc)
            order += 1
        db.session.commit()
        return rub

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
from __init__ import db
from admin.models.lab import AntiCheatAction


class AntiCheatService:
    RAPID_SUBMISSION_WINDOW_SECONDS = 30
    RAPID_SUBMISSION_THRESHOLD = 3

    @staticmethod
    def log_action(user_id: Optional[int], lab_id: Optional[int], action: str, context: Dict[str, Any] = None, flagged: bool = False) -> AntiCheatAction:
        entry = AntiCheatAction(user_id=user_id, lab_id=lab_id, action=action, context_json=json.dumps(context or {}), flagged=flagged)
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def detect_rapid_submissions(user_id: int, lab_id: int) -> Optional[AntiCheatAction]:
        since = datetime.utcnow() - timedelta(seconds=AntiCheatService.RAPID_SUBMISSION_WINDOW_SECONDS)
        recent = AntiCheatAction.query.filter(
            AntiCheatAction.user_id == user_id,
            AntiCheatAction.lab_id == lab_id,
            AntiCheatAction.created_at >= since,
            AntiCheatAction.action == 'submit'
        ).count()
        if recent >= AntiCheatService.RAPID_SUBMISSION_THRESHOLD:
            return AntiCheatService.log_action(user_id, lab_id, 'rapid_submissions', {'count': recent}, flagged=True)
        return None

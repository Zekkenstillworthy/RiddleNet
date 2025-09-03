from typing import Optional, Dict
from sqlalchemy import func
from __init__ import db
from user.models.points import PointTransaction


class PointEconomyService:
    @staticmethod
    def get_balance(user_id: int) -> int:
        total = db.session.query(func.coalesce(func.sum(PointTransaction.change), 0)).filter(PointTransaction.user_id == user_id).scalar() or 0
        return int(total)

    @staticmethod
    def earn(user_id: int, amount: int, reason: str, metadata_json: Optional[str] = None) -> PointTransaction:
        tx = PointTransaction(user_id=user_id, change=abs(int(amount)), reason=reason, metadata_json=metadata_json)
        db.session.add(tx)
        db.session.commit()
        return tx

    @staticmethod
    def spend(user_id: int, amount: int, reason: str, metadata_json: Optional[str] = None) -> Dict:
        amount = abs(int(amount))
        balance = PointEconomyService.get_balance(user_id)
        if balance < amount:
            return {'success': False, 'error': 'Insufficient points', 'balance': balance}
        tx = PointTransaction(user_id=user_id, change=-amount, reason=reason, metadata_json=metadata_json)
        db.session.add(tx)
        db.session.commit()
        return {'success': True, 'transaction_id': tx.id, 'balance': balance - amount}

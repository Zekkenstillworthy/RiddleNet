
from functools import wraps
from flask import jsonify, request
from flask_login import current_user

def teacher_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if not getattr(current_user, 'is_authenticated', False):
			return jsonify({'error': 'Authentication required'}), 401
		role = getattr(current_user, 'role', None)
		if role not in ('admin', 'super_admin', 'instructor') and not getattr(current_user, 'is_instructor', False):
			return jsonify({'error': 'Instructor access required'}), 403
		return f(*args, **kwargs)
	return wrapper


def owner_required(model_cls, param_name: str = 'id', field_name: str = 'created_by', allow_superadmin: bool = True):
	def decorator(f):
		@wraps(f)
		def wrapper(*args, **kwargs):
			if not getattr(current_user, 'is_authenticated', False):
				return jsonify({'error': 'Authentication required'}), 401
			if allow_superadmin and getattr(current_user, 'role', None) == 'super_admin':
				return f(*args, **kwargs)
			obj_id = kwargs.get(param_name)
			if obj_id is None:
				return jsonify({'error': 'Missing identifier'}), 400
			try:
				obj = model_cls.query.get(obj_id)
			except Exception:
				obj = None
			if not obj:
				return jsonify({'error': 'Resource not found'}), 404
			if getattr(obj, field_name, None) != getattr(current_user, 'id', None):
				return jsonify({'error': 'Ownership required'}), 403
			return f(*args, **kwargs)
		return wrapper
	return decorator


from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def requer_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            role = get_jwt().get('role')
            if role not in roles:
                return jsonify({'error': 'Acesso negado.'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

apenas_ti = requer_role('ti')
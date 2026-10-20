from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from config import db

ROLES_TI = {'TI', 'Super Admin', 'Estagiario'}

def requer_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            membro = g.get('membro')
            if membro not in roles:
                from pessoas.equipe_ti.equipe_ti_model import EquipeTI
                membro = db.session.get(EquipeTI, int(get_jwt_identity()))
            if not membro or not membro.ativo:
                return jsonify({'error': 'Acesso negado.'}), 403

            roles_permitidas = set(roles) | ROLES_TI
            if membro.role not in roles_permitidas:
                return jsonify({'error': 'Acesso negado.'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

apenas_ti = requer_role('ti')
from flask import Blueprint, request
from auditoria.auditoria_model import AuditoriaLog
from pessoas.auth.decorators import apenas_ti

auditoria_bp = Blueprint('auditoria_routes', __name__, url_prefix='/auditoria')

@auditoria_bp.route('/', methods=['GET'])
@auditoria_bp.route('', methods=['GET'])
@apenas_ti
def listar_auditoria():
    limit = request.args.get('limit', 10)
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10

    logs = AuditoriaLog.query.order_by(AuditoriaLog.criado_em.desc()).limit(limit).all()
    return [log.to_dict() for log in logs], 200
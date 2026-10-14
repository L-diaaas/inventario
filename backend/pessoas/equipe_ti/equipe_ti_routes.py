from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.pessoas.equipe_ti.equipe_ti_model import EquipeTI
from backend.pessoas.auth.decorators import apenas_ti
from backend.config import db

equipe_ti_bp = Blueprint('equipe_ti_routes', __name__, url_prefix='/equipe-ti')

@equipe_ti_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''

    membro = EquipeTI.query.filter(
        db.func.lower(EquipeTI.email) == email,
        EquipeTI.ativo.is_(True),   # <-- NOVO: só ativos podem logar
    ).first()

    if not membro or not membro.verificar_senha(senha):
        return {'error': 'Credenciais inválidas.'}, 401

    token = create_access_token(
        identity=str(membro.id),
        additional_claims={'role': membro.role}
    )
    return {'access_token': token, 'membro': membro.to_dict()}, 200

@equipe_ti_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    membro = EquipeTI.query.get(int(get_jwt_identity()))
    if not membro or not membro.ativo:
        return {'error': 'Conta inexistente ou inativa.'}, 401
    return membro.to_dict(), 200

def _eh_ultimo_ti_ativo(id_excluindo):
    return EquipeTI.query.filter(
        EquipeTI.ativo.is_(True),
        EquipeTI.id != id_excluindo,
    ).count() == 0

@equipe_ti_bp.route('/', methods=['POST'])
@apenas_ti
def criar_membro():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''

    if not email or '@' not in email:
        return {'error': 'E-mail inválido.'}, 400
    if not senha or len(senha) < 8:
        return {'error': 'A senha deve ter pelo menos 8 caracteres.'}, 400

    if EquipeTI.query.filter(db.func.lower(EquipeTI.email) == email).first():
        return {'error': 'Já existe um membro com esse e-mail.'}, 409

    novo = EquipeTI(email=email, role='ti')
    novo.set_senha(senha)

    try:
        db.session.add(novo)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Já existe um membro com esse e-mail.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao criar membro da equipe TI.'}, 500

    return {'mensagem': 'Membro da equipe TI criado.', 'membro': novo.to_dict()}, 201

@equipe_ti_bp.route('/<int:id>/inativar', methods=['PATCH'])
@apenas_ti
def inativar_membro(id):
    alvo = EquipeTI.query.get_or_404(id)

    if not alvo.ativo:
        return {'error': 'Esse membro já está inativo.'}, 409

    if _eh_ultimo_ti_ativo(id):
        return {'error': 'Não é possível inativar o último membro ativo da equipe TI.'}, 409

    alvo.ativo = False
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao inativar membro.'}, 500

    # Log simples de auditoria
    from flask import current_app
    current_app.logger.info(
        f'TI {get_jwt_identity()} inativou TI {id} ({alvo.email})'
    )

    return {'mensagem': 'Membro inativado com sucesso.'}, 200


@equipe_ti_bp.route('/<int:id>/reativar', methods=['PATCH'])
@apenas_ti
def reativar_membro(id):
    alvo = EquipeTI.query.get_or_404(id)

    if alvo.ativo:
        return {'error': 'Esse membro já está ativo.'}, 409

    alvo.ativo = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao reativar membro.'}, 500

    from flask import current_app
    current_app.logger.info(
        f'TI {get_jwt_identity()} reativou TI {id} ({alvo.email})'
    )

    return {'mensagem': 'Membro reativado com sucesso.'}, 200


@equipe_ti_bp.route('/me/inativar', methods=['PATCH'])
@apenas_ti
def inativar_minha_conta():
    meu_id = int(get_jwt_identity())

    if _eh_ultimo_ti_ativo(meu_id):
        return {'error': 'Você é o último TI ativo. Não é possível inativar sua própria conta.'}, 409

    eu = EquipeTI.query.get(meu_id)
    eu.ativo = False
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao inativar sua conta.'}, 500

    from flask import current_app
    current_app.logger.info(f'TI {meu_id} inativou a própria conta.')

    return {'mensagem': 'Sua conta foi inativada.'}, 200
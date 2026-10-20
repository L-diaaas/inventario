from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from pessoas.equipe_ti.equipe_ti_model import EquipeTI
from pessoas.auth.decorators import apenas_ti
from config import db
from seguranca import limiter

equipe_ti_bp = Blueprint('equipe_ti_routes', __name__, url_prefix='/equipe-ti')

_HASH_FALSO = generate_password_hash('')

@equipe_ti_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute;30 per hour')
def login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''

    membro = EquipeTI.query.filter(
        db.func.lower(EquipeTI.email) == email,
        EquipeTI.ativo.is_(True), 
    ).first()

    senha_ok = check_password_hash(membro.senha_hash if membro else _HASH_FALSO, senha[:128])
    if not membro or not senha_ok or len(senha) > 128:
        current_app.logger.warning(f'Login falhou: email={email[:80]!r} ip={request.remote_addr}')
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

@equipe_ti_bp.route('/', methods=['GET'])
@apenas_ti
def listar_membros():
    membros = EquipeTI.query.all()
    return [m.to_dict() for m in membros], 200

@equipe_ti_bp.route('/', methods=['POST'])
@apenas_ti
def criar_membro():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''
    nome = (dados.get('nome') or '').strip()
    role = (dados.get('role') or 'ti').strip()


    if not email or '@' not in email:
        return {'error': 'E-mail inválido.'}, 400
    if not senha or len(senha) < 6:
        return {'error': 'A senha deve ter pelo menos 6 caracteres.'}, 400

    if EquipeTI.query.filter(db.func.lower(EquipeTI.email) == email).first():
        return {'error': 'Já existe um membro com esse e-mail.'}, 409

    novo = EquipeTI(email=email, role=role, nome=nome if nome else None)
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

@equipe_ti_bp.route('/<int:id>', methods=['PATCH'])
@apenas_ti
def atualizar_membro(id):
    alvo = EquipeTI.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('nome', 'role', 'senha', 'email', 'ativo')):
        return {'error': 'Nenhum capo para atualizar foi informado.'}, 400

    if 'nome' in dados:
        alvo.nome = dados['nome'].strip() if isinstance(dados['nome'], str) else None

    if 'role' in dados and isinstance(dados['role'], str) and dados['role'].strip():
        alvo.role = dados['role'].strip()

    if 'email' in dados and isinstance(dados['email'], str):
        email_novo = dados['email'].strip().lower()
        if not email_novo or '@' not in email_novo:
            return {'error': 'E-mail inválido.'}, 400
        existente = EquipeTI.query.filter(
            db.func.lower(EquipeTI.email) == email_novo,
            EquipeTI.id != id
        ).first()
        if existente:
            return {'error': 'Já existe um membro com esse e-mail.'}, 409
        alvo.email = email_novo

    if 'senha' in dados and dados['senha']:
        senha = dados['senha']
        if len(senha) < 8:
            return {'error': 'A senha deve ter pelo menos 8 caracteres.'}, 400
        alvo.set_senha(senha)

    if 'ativo' in dados and isinstance(dados['ativo'], bool):
        if not dados['ativo'] and _eh_ultimo_ti_ativo(id):
            return {'error': 'Não é possível inativar o último membro ativo da equipe TI.'}, 409
        alvo.ativo = dados['ativo']

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Já existe um membro com esse e-mail.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar membro da equipe TI.'}, 500

    return {'mensagem': 'Membro da equipe TI atualizado com sucesso.', 'membro': alvo.to_dict()}, 200

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
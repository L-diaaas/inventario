from flask import Blueprint, request
from config import db
from localizacao.mesa.mesa_model import Mesa, validar_nome
from localizacao.andar.andar_model import Andar
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

mesa_bp = Blueprint('mesa_routes', __name__, url_prefix='/mesas')

STATUS_VALIDOS = {'livre', 'ocupada', 'sucata', 'inativa', 'refeitorio'}


def validar_status(status):
    if not isinstance(status, str) or status.strip().lower() not in STATUS_VALIDOS:
        return None, ({'error': f'Status inválido. Use um de: {", ".join(sorted(STATUS_VALIDOS))}.'}, 400)
    return status.strip().lower(), None


def validar_andar_id(andar_id):
    if isinstance(andar_id, bool) or not isinstance(andar_id, int):
        return None, ({'error': 'O andar é obrigatório e deve ser o id (número inteiro) de um andar.'}, 400)
    if not db.session.get(Andar, andar_id):
        return None, ({'error': 'Esse andar não existe ou não foi cadastrado.'}, 400)
    return andar_id, None


@mesa_bp.route('/', methods=['POST'])
def adicionar_mesa():
    dados = request.get_json(silent=True) or {}

    nome, erro = validar_nome(dados.get('nome'))
    if erro:
        return erro

    andar_id, erro = validar_andar_id(dados.get('andar_id'))
    if erro:
        return erro

    status, erro = validar_status(dados.get('status', 'livre'))
    if erro:
        return erro

    try:
        nova_mesa = Mesa(nome=nome, andar_id=andar_id, status=status)
        db.session.add(nova_mesa)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Essa identificação já existe.'}, 409

    return {'mensagem': 'Nova mesa cadastrada com sucesso', 'mesa': nova_mesa.to_dict()}, 201

@mesa_bp.route('/', methods=['GET'])
def listar_mesas():
    mesas = Mesa.query.all()
    return [mesa.to_dict() for mesa in mesas], 200

@mesa_bp.route('/<int:id>', methods=['GET'])
def obter_mesa(id):
    mesa = Mesa.query.get_or_404(id)
    return mesa.to_dict(), 200

@mesa_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_mesa(id):
    mesa = Mesa.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('nome', 'andar_id', 'status')):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'nome' in dados:
        nome, erro = validar_nome(dados['nome'], id_atual=id)
        if erro:
            return erro
        mesa.nome = nome

    if 'andar_id' in dados:
        andar_id, erro = validar_andar_id(dados['andar_id'])
        if erro:
            return erro
        mesa.andar_id = andar_id

    if 'status' in dados:
        status, erro = validar_status(dados['status'])
        if erro:
            return erro
        mesa.status = status

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Essa identificação já existe.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar a mesa.'}, 500

    return {'mensagem': 'Mesa atualizada com sucesso', 'mesa': mesa.to_dict()}, 200

@mesa_bp.route('/<int:id>', methods=['DELETE'])
def deletar_mesa(id):
    mesa = Mesa.query.get_or_404(id)

    try:
        db.session.delete(mesa)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar essa mesa, pois ela está vinculada a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar a mesa.'}, 500

    return {'mensagem': 'Mesa deletada com sucesso.'}, 200
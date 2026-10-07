from flask import Blueprint, request
from config import db
from perifericos.headset.headset_model import Headset, validar_modelo
from catalogos.marca.marca_model import Marca
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

headset_bp = Blueprint('headset_routes', __name__, url_prefix='/headsets')

STATUS_VALIDOS = {'livre', 'ocupado', 'sucata', 'inativo'}


def validar_status(status):
    if not isinstance(status, str) or status.strip().lower() not in STATUS_VALIDOS:
        return None, ({'error': f'Status inválido. Use um de: {", ".join(sorted(STATUS_VALIDOS))}.'}, 400)
    return status.strip().lower(), None


def validar_marca_id(marca_id):
    if isinstance(marca_id, bool) or not isinstance(marca_id, int):
        return None, ({'error': 'A marca é obrigatória e deve ser o id (número inteiro) de uma marca.'}, 400)
    if not db.session.get(Marca, marca_id):
        return None, ({'error': 'Essa marca não existe ou não foi cadastrada.'}, 400)
    return marca_id, None


@headset_bp.route('/', methods=['POST'])
def adicionar_headset():
    dados = request.get_json(silent=True) or {}

    modelo, erro = validar_modelo(dados.get('modelo'))
    if erro:
        return erro

    marca_id, erro = validar_marca_id(dados.get('marca_id'))
    if erro:
        return erro

    status, erro = validar_status(dados.get('status', 'livre'))
    if erro:
        return erro

    try:
        novo_headset = Headset(modelo=modelo, marca_id=marca_id, status=status)
        db.session.add(novo_headset)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível cadastrar o headset. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao cadastrar o headset.'}, 500

    return {'mensagem': 'Novo headset cadastrado com sucesso', 'headset': novo_headset.to_dict()}, 201


@headset_bp.route('/', methods=['GET'])
def listar_headsets():
    headsets = Headset.query.all()
    return [headset.to_dict() for headset in headsets], 200


@headset_bp.route('/<int:id>', methods=['GET'])
def obter_headset(id):
    headset = Headset.query.get_or_404(id)
    return headset.to_dict(), 200


@headset_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_headset(id):
    headset = Headset.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('modelo', 'marca_id', 'status')):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'modelo' in dados:
        modelo, erro = validar_modelo(dados['modelo'])
        if erro:
            return erro
        headset.modelo = modelo

    if 'marca_id' in dados:
        marca_id, erro = validar_marca_id(dados['marca_id'])
        if erro:
            return erro
        headset.marca_id = marca_id

    if 'status' in dados:
        status, erro = validar_status(dados['status'])
        if erro:
            return erro
        headset.status = status

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível atualizar o headset. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar o headset.'}, 500

    return {'mensagem': 'Headset atualizado com sucesso', 'headset': headset.to_dict()}, 200


@headset_bp.route('/<int:id>', methods=['DELETE'])
def deletar_headset(id):
    headset = Headset.query.get_or_404(id)

    try:
        db.session.delete(headset)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse headset, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o headset.'}, 500

    return {'mensagem': 'Headset deletado com sucesso.'}, 200
from flask import Blueprint, request
from localizacao.andar.andar_model import Andar, validar_nome
from config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

andar_bp = Blueprint('andar_routes', __name__, url_prefix='/andares')


@andar_bp.route('/', methods=['POST'])
def adicionar_andar():
    dados = request.get_json(silent=True) or {}

    nome, erro = validar_nome(dados.get('nome'))
    if erro:
        return erro

    try:
        novo_andar = Andar(nome)
        db.session.add(novo_andar)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Já existe um andar com esse nome.'}, 409

    return {'mensagem': 'Andar cadastrado com sucesso', 'andar': novo_andar.to_dict()}, 201

@andar_bp.route('/', methods=['GET'])
def listar_andares():
    andares = Andar.query.all()
    return [andar.to_dict() for andar in andares], 200

@andar_bp.route('/<int:id>', methods=['GET'])
def obter_andar(id):
    andar = Andar.query.get_or_404(id)
    return andar.to_dict(), 200

@andar_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_andar(id):
    andar = Andar.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if 'nome' not in dados:
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    nome, erro = validar_nome(dados.get('nome'), id_atual=id)
    if erro:
        return erro

    andar.nome = nome

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Já existe um andar com esse nome.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar o andar.'}, 500

    return {'mensagem': 'Andar atualizado com sucesso', 'andar': andar.to_dict()}, 200


@andar_bp.route('/<int:id>', methods=['DELETE'])
def deletar_andar(id):
    andar = Andar.query.get_or_404(id)

    try:
        db.session.delete(andar)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse andar, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o andar.'}, 500

    return {'mensagem': 'Andar deletado com sucesso.'}, 200
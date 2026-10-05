from flask import Blueprint, request
from catalogos.marca.marca_model import Marca, validar_nome
from config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

marca_bp = Blueprint('marca_routes', __name__, url_prefix='/marcas')

@marca_bp.route('/', methods=['POST'])
def adicionar_marca():
    dados = request.get_json(silent=True) or {}

    nome, erro = validar_nome(dados.get('nome'))
    if erro:
        return erro

    try:
        nova_marca = Marca(nome)
        db.session.add(nova_marca)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Já existe uma marca com esse nome.'}, 409

    return {'mensagem': 'Marca cadastrada com sucesso', 'marca': nova_marca.to_dict()}, 201

@marca_bp.route('/', methods=['GET'])
def listar_marcas():
    marcas = Marca.query.all()
    return [marca.to_dict() for marca in marcas], 200

@marca_bp.route('/<int:id>', methods=['GET'])
def obter_marca(id):
    marca = Marca.query.get_or_404(id)
    return marca.to_dict(), 200

@marca_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_marca(id):
    marca = Marca.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if 'nome' not in dados:
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    nome, erro = validar_nome(dados.get('nome'), id_atual=id)
    if erro:
        return erro

    marca.nome = nome

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Já existe uma marca com esse nome.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar a marca.'}, 500

    return {'mensagem': 'Marca atualizada com sucesso', 'marca': marca.to_dict()}, 200

@marca_bp.route('/<int:id>', methods=['DELETE'])
def deletar_marca(id):
    marca = Marca.query.get_or_404(id)

    try:
        db.session.delete(marca)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar essa marca, pois ela está vinculada a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar a marca.'}, 500

    return {'mensagem': 'Marca deletada com sucesso.'}, 200
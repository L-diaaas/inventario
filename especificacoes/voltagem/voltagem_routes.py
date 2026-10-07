from flask import Blueprint, request
from .voltagem_model  import Voltagem, validar_voltagem
from config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

voltagem_bp = Blueprint('voltagem_routes', __name__, url_prefix='/voltagem')

@voltagem_bp.route('/', methods=['POST'])
def adicionar_voltagem():
    dados = request.get_json(silent=True) or {}

    voltagem, erro = validar_voltagem(dados.get('voltagem'))
    if erro:
        return erro

    try:
        nova_voltagem = Voltagem(voltagem)
        db.session.add(nova_voltagem)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Essa voltagem já está cadastrada.'}, 409

    return {'mensagem': 'Nova voltagem adicionada com sucesso', 'voltagem': nova_voltagem.to_dict()}, 201

@voltagem_bp.route('/', methods=['GET'])
def listar_voltagens():
    voltagens = Voltagem.query.all()
    return [vol.to_dict() for vol in voltagens], 200

@voltagem_bp.route('/<int:id>', methods=['GET'])
def obter_voltagem(id):
    voltagem = Voltagem.query.get_or_404(id)
    return voltagem.to_dict(), 200

@voltagem_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_voltagem(id):
    registro = Voltagem.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if 'voltagem' not in dados:
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    valor, erro = validar_voltagem(dados.get('voltagem'), id_atual=id)
    if erro:
        return erro

    registro.voltagem = valor

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Essa voltagem já está cadastrada.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar a voltagem.'}, 500

    return {'mensagem': 'voltagem atualizada com sucesso', 'voltagem': registro.to_dict()}, 200

@voltagem_bp.route('/<int:id>', methods=['DELETE'])
def deletar_voltagem(id):
    voltagem = Voltagem.query.get_or_404(id)

    try:
        db.session.delete(voltagem)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar essa voltagem, pois ela está vinculada a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar a voltagem.'}, 500

    return {'mensagem': 'Voltagem deletada com sucesso.'}, 200
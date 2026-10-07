from flask import Blueprint, request
from .qtd_tomadas_model import QuantidadeTomadas, validar_quantidade_tomadas
from config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

quantidade_tomadas_bp = Blueprint('quantidade_tomadas_routes', __name__, url_prefix='/quantidade-tomadas')

@quantidade_tomadas_bp.route('/', methods=['POST'])
def adicionar_quantidade_tomadas():
    dados = request.get_json(silent=True) or {}

    quantidade, erro = validar_quantidade_tomadas(dados.get('quantidade'))
    if erro:
        return erro

    try:
        nova_quantidade = QuantidadeTomadas(quantidade)
        db.session.add(nova_quantidade)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Essa quantidade de tomadas já está cadastrada.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao cadastrar a quantidade de tomadas.'}, 500

    return {
        'mensagem': 'Nova quantidade de tomadas adicionada com sucesso',
        'quantidade_tomadas': nova_quantidade.to_dict()
    }, 201

@quantidade_tomadas_bp.route('/', methods=['GET'])
def listar_quantidades_tomadas():
    quantidades = QuantidadeTomadas.query.order_by(QuantidadeTomadas.quantidade).all()
    return [q.to_dict() for q in quantidades], 200

@quantidade_tomadas_bp.route('/<int:id>', methods=['GET'])
def obter_quantidade_tomadas(id):
    registro = QuantidadeTomadas.query.get_or_404(id)
    return registro.to_dict(), 200

@quantidade_tomadas_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_quantidade_tomadas(id):
    registro = QuantidadeTomadas.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if 'quantidade' not in dados:
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    quantidade, erro = validar_quantidade_tomadas(dados.get('quantidade'), id_atual=id)
    if erro:
        return erro

    registro.quantidade = quantidade

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Essa quantidade de tomadas já está cadastrada.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar a quantidade de tomadas.'}, 500

    return {
        'mensagem': 'Quantidade de tomadas atualizada com sucesso',
        'quantidade_tomadas': registro.to_dict()
    }, 200

@quantidade_tomadas_bp.route('/<int:id>', methods=['DELETE'])
def deletar_quantidade_tomadas(id):
    registro = QuantidadeTomadas.query.get_or_404(id)

    try:
        db.session.delete(registro)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {
            'error': 'Não é possível deletar essa quantidade de tomadas, pois ela está vinculada a outros registros.'
        }, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar a quantidade de tomadas.'}, 500

    return {'mensagem': 'Quantidade de tomadas deletada com sucesso.'}, 200
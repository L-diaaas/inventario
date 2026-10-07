from flask import Blueprint, request
from .sistema_operacional_model import SistemaOperacional, validar_versao
from config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

sistema_operacional_bp = Blueprint('sistema_operacional_routes', __name__, url_prefix='/sistemas-operacionais')

@sistema_operacional_bp.route('/', methods=['POST'])
def adicionar_sistema_operacional():
    dados = request.get_json(silent=True) or {}

    versao, erro = validar_versao(dados.get('versao'))
    if erro:
        return erro

    try:
        nova_versao = SistemaOperacional(versao)
        db.session.add(nova_versao)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Essa versão de Sistema Operacional já está cadastrada.'}, 409

    return {'mensagem': 'Nova versão adicionada com sucesso', 'versao': nova_versao.to_dict()}, 201

@sistema_operacional_bp.route('/', methods=['GET'])
def listar_sistemas_operacionais():
    sistemas = SistemaOperacional.query.all()
    return [so.to_dict() for so in sistemas], 200

@sistema_operacional_bp.route('/<int:id>', methods=['GET'])
def obter_sistema_operacional(id):
    sistema_operacional = SistemaOperacional.query.get_or_404(id)
    return sistema_operacional.to_dict(), 200

@sistema_operacional_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_sistema_operacional(id):
    sistema_operacional = SistemaOperacional.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if 'versao' not in dados:
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    versao, erro = validar_versao(dados.get('versao'), id_atual=id)
    if erro:
        return erro

    sistema_operacional.versao = versao

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Essa versão de Sistema Operacional já está cadastrada.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar a versão do Sistema Operacional.'}, 500

    return {'mensagem': 'Versão atualizada com sucesso', 'versao': sistema_operacional.to_dict()}, 200

@sistema_operacional_bp.route('/<int:id>', methods=['DELETE'])
def deletar_sistema_operacional(id):
    sistema_operacional = SistemaOperacional.query.get_or_404(id)

    try:
        db.session.delete(sistema_operacional)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar essa versão, pois ela está vinculada a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar a versão do Sistema Operacional.'}, 500

    return {'mensagem': 'Versão do Sistema Operacional deletada com sucesso.'}, 200
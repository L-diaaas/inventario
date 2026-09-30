from flask import Blueprint, jsonify, request
from .sistema_operacional_model import SistemaOperacional
from config import db
from sqlalchemy.exc import IntegrityError 

sistema_operacional_bp = Blueprint('sistema_operacional_routes', __name__, url_prefix='/sistemas-operacionais')

@sistema_operacional_bp.route('/', methods=['POST'])
def adiconar_sistema_operacional():
    versao = request.json.get('versao')

    novo_sistema_operacional = SistemaOperacional(versao=versao)
    db.session.add(novo_sistema_operacional)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao cadastrar novo sistema operacional."}, 400
    return [novo_sistema_operacional.to_dict()], 201

@sistema_operacional_bp.route('/', methods=['GET'])
def listar_sistemas_operacionais():
    sistema_operacional = SistemaOperacional.query.all()
    return [sistemas_operacionais.to_dict for sistemas_operacionais in sistema_operacional], 200

@sistema_operacional_bp.route('/<int:id>', methods=['GET'])
def obter_sistema_opercional(id):
    sistema_operacional = SistemaOperacional.query.get_or_404(id)
    return sistema_operacional.to_dict(), 200

@sistema_operacional_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_versao_sistema_operacional(id):
    sistema_operacional = SistemaOperacional.query.get_or_404(id)

    dados = request.json or {}

    if 'versao' in  dados:
        versao = dados.get('versao')
        if versao and SistemaOperacional.query.filter(SistemaOperacional.versao == versao, SistemaOperacional.id != id).first():
            return {"error": "Essa versão de sistema operacional já está cadastrada"}, 400
        sistema_operacional.versao = versao

    try: 
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao atualizar a versao do sistema operacional"}, 500

    return sistema_operacional.to_dict()

@sistema_operacional_bp.route('/<int:id>', methods=['DELETE'])
def deleter_versao_sistema_operacional(id):
    sistema_operacional = SistemaOperacional.query.get_or_404(id)
    db.session.delete(sistema_operacional)
    db.session.commit()
    return {"message": "Versão do sitema operacional deletada com sucesso."}, 200
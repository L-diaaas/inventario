from flask import Blueprint, request, jsonify
from .processador_model import Processador
from config import db
from sqlalchemy.exc import IntegrityError

processador_bp = Blueprint('processador_routes', __name__, url_prefix='/processador')

@processador_bp.route('/', methods=['POST'])
def adicionar_processador():
    tipo = request.json.get('tipo')

    novo_processador = Processador(tipo=tipo)
    db.session.add(novo_processador)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao cadastrar novo processador."}, 400
    return [novo_processador.to_dict()], 201

@processador_bp.route('/', methods=['GET'])
def listar_processadores():
    processadores = Processador.query.all()
    return [processador.to_dict() for processador in processadores], 200

@processador_bp.route('/<int:id>', methods=['GET'])
def obter_processador(id):
    processador = Processador.query.get_or_404(id)
    return processador.to_dict(), 200

@processador_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_tipo_processador(id):
    processador = Processador.query.get_or_404(id)

    dados = request.json or {}

    if 'tipo' in dados:
        tipo = dados.get('tipo')
        if tipo and Processador.query.filter(Processador.tipo == tipo, Processador.id != id).first():
            return {"error": "Processador já cadastrado"}, 400
        processador.tipo = tipo

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao atualizar o tipo do processador"}, 500

    return processador.to_dict()

@processador_bp.route('/<int:id>', methods=['DELETE'])
def deletar_processador(id):
    processador = Processador.query.get_or_404(id)
    db.session.delete(processador)
    db.session.commit()
    return {"message": "Tipo do processador deletado com sucesso."}, 200

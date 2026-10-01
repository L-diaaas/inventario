from flask import Blueprint, request, jsonify
from colaboradores.colaboradores_model import Colaboradores
from config import db
from sqlalchemy.exc import IntegrityError

colaboradores_bp = Blueprint('colaboradores_routes', __name__, url_prefix='/colaboradores')

@colaboradores_bp.route('/', methods=['POST'])
def adicionar_colaborador():
    nome_completo = request.json.get('nome_completo')
    cargo = request.json.get('cargo')

    novo_colaborador = Colaboradores(nome_completo=nome_completo, cargo=cargo)
    db.session.add(novo_colaborador)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao cadastrar novo colaborador."}, 400
    return [novo_colaborador.to_dict()], 201

@colaboradores_bp.route('/', methods=['GET'])
def listar_colaboradores():
    colaboradores = Colaboradores.query.all()
    return [colaborador.to_dict() for colaborador in colaboradores]

@colaboradores_bp.route('/<int:id>', methods=['GET'])
def obter_colaboradores(id):
    colaborador = Colaboradores.query.get_or_404(id)
    return colaborador.to_dict()

@colaboradores_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_colaborador(id):
    colaborador = Colaboradores.query.get_or_404(id)

    dados = request.json or {}

    if 'nome_completo' in dados:
        nome_completo = dados.get('nome_completo')
        if 'nome_completo' and Colaboradores.query.filter(Colaboradores.nome_completo == nome_completo, Colaboradores.id !=id).first():
            return {'error': 'nome_completo de cliente já cadastro'}






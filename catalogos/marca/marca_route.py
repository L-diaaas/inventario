from flask import Blueprint, request, jsonify
from catalogos.marca.marca_model import db, Marca
from config import db
from sqlalchemy.exc import IntegrityError

marca_bp = Blueprint('marca_routes', __name__, url_prefix='/marcas')

@marca_bp.route('/', methods=['POST'])
def adicionar_marca():
    dados = request.get_json(silent=True) or {}
    nome = dados.get('nome')

    if not nome or not nome.strip():
        return {'error':'O nome da marca é obrigatório'}, 400

    nome = nome.strip()

    if len(nome) < 2:
        return {'error': 'O nome deve ter pelo menos 2 caracteres'}, 400
    if len(nome) > 100:
        return {'error': 'O nome deve ter no máximo 100 caracteres'}, 400

    existente = Marca.query.filter(db.func.lower(Marca.nome) == nome.lower()).first()

    if existente:
        return {'error': 'Já existe marca com esse nome'}, 409

    try: 
        nova_marca = Marca(nome)
        db.session.add(nova_marca)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Marca já cadastrada'}, 409

    return jsonify({'mensagem' : 'Marca cadastrada com sucesso', 'marca': {'id': nova_marca.id, 'nome': nova_marca.nome}}), 201

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

    dados = request.json or {}

    if 'nome' in dados:
        nome = dados.get('nome')
        if 'nome' and Marca.query.filter(Marca.nome == nome, Marca.id != id).first():
            return {'error': 'Essa marca já está cadastrada'}, 400
        marca.nome = nome

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar nome da marca'}, 400
    return marca.to_dict()

@marca_bp.route('/<int:id>', methods=['DELETE'])
def deletar_marca(id):
    marca = Marca.query.get_or_404(id)

    try:
        db.session.delete(marca)
        db.session.commit()
        return {'mensagem': 'Marca deletada com sucesso!'}, 200
    except IntegrityError:
        db.session.rollback()
        return {'mensagem': 'Erro ao deletar Marca.'}, 200




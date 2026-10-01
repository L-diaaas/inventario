from flask import Blueprint, request, jsonify
from localizacao.andar.andar_model import db, Andar
from config import db
from sqlalchemy.exc import IntegrityError

andar_bp = Blueprint('andar_routes', __name__, url_prefix='/andares')

@andar_bp.route('/', methods=['POST'])
def adicionar_andar():
    dados = request.get_json(silent=True) or {}
    nome = dados.get('nome')

    if not nome or not nome.strip():
        return {'error': 'O nome do andar é obrigatório'}, 400

    nome = nome.strip()

    if len(nome) < 2:
        return {'error': 'O nome do andar deve ter pelo menos 2 caracteres'}, 400
    if len(nome) > 20:
        return {'error': 'O nome do andar deve ter menos de 20 caracteres'}, 400

    existente = Andar.query.filter(db.func.lower(Andar.nome) == nome.lower()).first()

    if existente:
        return {'error':'Já existe um andar com esse nome.'}, 409

    try:
        novo_andar = Andar(nome)
        db.session.add(novo_andar)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return{'error': 'Erro ao cadastrar novo andar'}, 400

    return jsonify({'mensagem' : 'Andar cadastrado com sucesso', 'andar': {'id': novo_andar.id, 'nome': novo_andar.nome}}), 201

@andar_bp.route('/', methods=['GET'])
def listar_andares():
    andares = Andar.query.all()

    try:
        return [andar.to_dict() for andar in andares], 200
    except IntegrityError:
        return {'error': 'Não foi possivel listar os andares'}

@andar_bp.route('/<int:id>', methods=['GET'])
def obter_andar(id):
    andar = Andar.query.get_or_404(id)

    try:
        return andar.to_dict(), 200
    except IntegrityError:
        return {'error' : 'Andar não cadastrado'}

@andar_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_andar(id):
    andar = Andar.query.get_or_404(id)

    dados = request.json or {}

    if 'nome' in dados:
        nome = dados.get('nome')
        if 'nome' and Andar.query.filter(Andar.nome == nome, Andar.id != id).first():
            return {'error': 'Esse andar já está cadastrado'}, 400
        andar.nome = nome

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar andar'}, 400
    return andar.to_dict()

@andar_bp.route('/<int:id>', methods=['DELETE'])
def deletar_andar(id):
    andar = Andar.query.get_or_404(id)

    try: 
        db.session.delete(andar)
        db.session.commit()
        return {'mensagem': 'Andar deletado com sucesso'}, 200
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Erro ao deletar andar'}, 400
    
    

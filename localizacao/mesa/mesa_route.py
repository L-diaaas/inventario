from flask import Blueprint, request, jsonify
from config import db
from localizacao.mesa.mesa_model import db, Mesa
from localizacao.andar.andar_model import db, Andar
from sqlalchemy.exc import IntegrityError

mesa_bp = Blueprint('mesa_routes', __name__, url_prefix='/mesas')

status_validos = {'livre', 'ocupada', 'sucata', 'inativa', 'refeitorio'}

@mesa_bp.route('/', methods=['POST'])
def adicionar_mesa():
    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    andar_id = dados.get('andar_id')
    status = dados.get('status', 'livre')

    if not status in status_validos:
        return {'error': f'Status inválido. Use um de: {",".join(status_validos)}'}, 400

    # Verificação do nome atribuido a mesa

    if not nome or not nome.strip():
        return {'error' : 'A identificação da mesa é obrogatória'}, 400

    nome = nome.strip()

    if len(nome) < 2:
        return {'error': 'A identificação da mesa deve ter no mínimo 2 caracteres'}, 400
    if len(nome) > 100:
        return {'error': 'A identificação da mesa deve ter no máximo 100 caracteres'}, 400

    nome_existente = Mesa.query.filter(db.func.lower(Mesa.nome) == nome.lower()).first()

    if nome_existente:
        return {'error': 'Essa identificação já existe.'}, 409

    # Verificação se o andar foi informado e se ele existe

    if not andar_id:
        return {'error': 'O andar onde a mesa está é obrigatório.'}, 400

    andar_existe = Andar.query.filter(Andar.id == andar_id).first()

    if not andar_existe:
        return {'error': 'Esse andar não existe ou não foi cadastrado'}, 400

    try:
        nova_mesa = Mesa(nome=nome, andar_id=andar_id, status=status)
        db.session.add(nova_mesa)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível cadastrar nova mesa.'}, 400

    return jsonify({'mensagem': 'Nova mesa cadastrada com sucesso', 'mesa': nova_mesa.to_dict()})

@mesa_bp.route('/', methods=['GET']) #Lista todas as mesas
def listar_mesas():
    mesas = Mesa.query.all()

    try:
        return [mesa.to_dict() for mesa in mesas], 200
    except IntegrityError:
        return {'error': 'Não foi possível listar as mesas'}, 400

@mesa_bp.route('/<int:id>', methods=['GET']) # Lista mesa refernte ao ID informado
def obter_mesa(id):
    mesa = Mesa.query.get_or_404(id)

    try:
        return mesa.to_dict(), 200
    except IntegrityError:
        return {'error': 'Não foi possível encontrar mesa'}, 400
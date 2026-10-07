from flask import Blueprint, request
from config import db
from perifericos.monitor.monitor_model import Monitor, validar_polegadas
from catalogos.marca.marca_model import Marca
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

monitor_bp = Blueprint('monitor_routes', __name__, url_prefix='/monitores')

STATUS_VALIDOS = {'livre', 'ocupado', 'sucata', 'inativo'}

def validar_status(status):
    if not isinstance(status, str) or status.strip().lower() not in STATUS_VALIDOS:
        return None, ({'error': f'Status inválido. Use um de: {", ".join(sorted(STATUS_VALIDOS))}.'}, 400)
    return status.strip().lower(), None

def validar_marca_id(marca_id):
    if isinstance(marca_id, bool) or not isinstance(marca_id, int):
        return None, ({'error': 'A marca é obrigatória e deve ser o id (número inteiro) de uma marca.'}, 400)
    if not db.session.get(Marca, marca_id):
        return None, ({'error': 'Essa marca não existe ou não foi cadastrada.'}, 400)
    return marca_id, None

@monitor_bp.route('/', methods=['POST'])
def adicionar_monitor():
    dados = request.get_json(silent=True) or {}

    polegadas, erro = validar_polegadas(dados.get('polegadas'))
    if erro:
        return erro

    marca_id, erro = validar_marca_id(dados.get('marca_id'))
    if erro:
        return erro

    status, erro = validar_status(dados.get('status', 'livre'))
    if erro:
        return erro

    try:
        novo_monitor = Monitor(polegadas=polegadas, marca_id=marca_id, status=status)
        db.session.add(novo_monitor)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível cadastrar o monitor. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao cadastrar o monitor.'}, 500

    return {'mensagem': 'Novo monitor cadastrado com sucesso', 'monitor': novo_monitor.to_dict()}, 201

@monitor_bp.route('/', methods=['GET'])
def listar_monitores():
    monitores = Monitor.query.all()
    return [monitor.to_dict() for monitor in monitores], 200

@monitor_bp.route('/<int:id>', methods=['GET'])
def obter_monitor(id):
    monitor = Monitor.query.get_or_404(id)
    return monitor.to_dict(), 200

@monitor_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_monitor(id):
    monitor = Monitor.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('polegadas', 'marca_id', 'status')):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'polegadas' in dados:
        polegadas, erro = validar_polegadas(dados['polegadas'])
        if erro:
            return erro
        monitor.polegadas = polegadas

    if 'marca_id' in dados:
        marca_id, erro = validar_marca_id(dados['marca_id'])
        if erro:
            return erro
        monitor.marca_id = marca_id

    if 'status' in dados:
        status, erro = validar_status(dados['status'])
        if erro:
            return erro
        monitor.status = status

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível atualizar o monitor. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar o monitor.'}, 500

    return {'mensagem': 'Monitor atualizado com sucesso', 'monitor': monitor.to_dict()}, 200

@monitor_bp.route('/<int:id>', methods=['DELETE'])
def deletar_monitor(id):
    monitor = Monitor.query.get_or_404(id)

    try:
        db.session.delete(monitor)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse monitor, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o monitor.'}, 500

    return {'mensagem': 'Monitor deletado com sucesso.'}, 200
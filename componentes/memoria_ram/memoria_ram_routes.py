from flask import Blueprint, request
from config import db
from componentes.memoria_ram.memoria_ram_model import MemoriaRam, validar_quantidade
from catalogos.tipo_memoria_ram.tipo_memoria_ram_model import TipoMemoria
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

memoria_ram_bp = Blueprint('memoria_ram_routes', __name__, url_prefix='/memorias-ram')

STATUS_VALIDOS = {'em_uso', 'sucata'}


def validar_status(status):
    if not isinstance(status, str):
        return None, ({'error': f'Status inválido. Use um de: {", ".join(sorted(STATUS_VALIDOS))}.'}, 400)
    status = status.strip().lower().replace(' ', '_')
    if status not in STATUS_VALIDOS:
        return None, ({'error': f'Status inválido. Use um de: {", ".join(sorted(STATUS_VALIDOS))}.'}, 400)
    return status, None


def validar_tipo_memoria_ram_id(tipo_id):
    if isinstance(tipo_id, bool) or not isinstance(tipo_id, int):
        return None, ({'error': 'O tipo de memória é obrigatório e deve ser o id (número inteiro) de um tipo.'}, 400)
    if not db.session.get(TipoMemoria, tipo_id):
        return None, ({'error': 'Esse tipo de memória não existe ou não foi cadastrado.'}, 400)
    return tipo_id, None


@memoria_ram_bp.route('/', methods=['POST'])
def adicionar_memoria_ram():
    dados = request.get_json(silent=True) or {}

    quantidade, erro = validar_quantidade(dados.get('quantidade'))
    if erro:
        return erro

    tipo_id, erro = validar_tipo_memoria_ram_id(dados.get('tipo_memoria_ram_id'))
    if erro:
        return erro

    status, erro = validar_status(dados.get('status', 'em_uso'))
    if erro:
        return erro

    try:
        nova = MemoriaRam(quantidade=quantidade, tipo_memoria_ram_id=tipo_id, status=status)
        db.session.add(nova)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível cadastrar a memória RAM. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao cadastrar a memória RAM.'}, 500

    return {'mensagem': 'Nova memória RAM cadastrada com sucesso', 'memoria_ram': nova.to_dict()}, 201


@memoria_ram_bp.route('/', methods=['GET'])
def listar_memorias_ram():
    memorias = MemoriaRam.query.all()
    return [m.to_dict() for m in memorias], 200


@memoria_ram_bp.route('/<int:id>', methods=['GET'])
def obter_memoria_ram(id):
    memoria = MemoriaRam.query.get_or_404(id)
    return memoria.to_dict(), 200

@memoria_ram_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_memoria_ram(id):
    memoria = MemoriaRam.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('quantidade', 'tipo_memoria_ram_id', 'status')):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'quantidade' in dados:
        quantidade, erro = validar_quantidade(dados['quantidade'])
        if erro:
            return erro
        memoria.quantidade = quantidade

    if 'tipo_memoria_ram_id' in dados:
        tipo_id, erro = validar_tipo_memoria_ram_id(dados['tipo_memoria_ram_id'])
        if erro:
            return erro
        memoria.tipo_memoria_ram_id = tipo_id

    if 'status' in dados:
        status, erro = validar_status(dados['status'])
        if erro:
            return erro
        memoria.status = status

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível atualizar a memória RAM. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar a memória RAM.'}, 500

    return {'mensagem': 'Memória RAM atualizada com sucesso', 'memoria_ram': memoria.to_dict()}, 200


@memoria_ram_bp.route('/<int:id>', methods=['DELETE'])
def deletar_memoria_ram(id):
    memoria = MemoriaRam.query.get_or_404(id)

    try:
        db.session.delete(memoria)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar essa memória RAM, pois ela está vinculada a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar a memória RAM.'}, 500

    return {'mensagem': 'Memória RAM deletada com sucesso.'}, 200
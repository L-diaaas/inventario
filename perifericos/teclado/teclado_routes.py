from flask import Blueprint, request
from config import db
from perifericos.teclado.teclado_model import Teclado
from catalogos.marca.marca_model import Marca
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

teclado_bp = Blueprint('teclado_routes', __name__, url_prefix='/teclados')

STATUS_VALIDOS = {'livre', 'ocupado', 'sucata', 'inativo'}
TIPOS_VALIDOS = {'com_fio', 'bluetooth'}

def validar_status(status):
    if not isinstance(status, str) or status.strip().lower() not in STATUS_VALIDOS:
        return None, ({'error': f'Status inválido. Use um de: {", ".join(sorted(STATUS_VALIDOS))}.'}, 400)
    return status.strip().lower(), None

def validar_tipo(tipo):
    if not isinstance(tipo, str):
        return None, ({'error': f'O tipo é obrigatório. Use um de: {", ".join(sorted(TIPOS_VALIDOS))}.'}, 400)
    tipo = tipo.strip().lower().replace(' ', '_')
    if tipo not in TIPOS_VALIDOS:
        return None, ({'error': f'Tipo inválido. Use um de: {", ".join(sorted(TIPOS_VALIDOS))}.'}, 400)
    return tipo, None

def validar_marca_id(marca_id):
    if isinstance(marca_id, bool) or not isinstance(marca_id, int):
        return None, ({'error': 'A marca é obrigatória e deve ser o id (número inteiro) de uma marca.'}, 400)
    if not db.session.get(Marca, marca_id):
        return None, ({'error': 'Essa marca não existe ou não foi cadastrada.'}, 400)
    return marca_id, None

@teclado_bp.route('/', methods=['POST'])
def adicionar_teclado():
    dados = request.get_json(silent=True) or {}

    tipo, erro = validar_tipo(dados.get('tipo'))
    if erro:
        return erro

    marca_id, erro = validar_marca_id(dados.get('marca_id'))
    if erro:
        return erro

    status, erro = validar_status(dados.get('status', 'livre'))
    if erro:
        return erro

    try:
        novo_teclado = Teclado(tipo=tipo, marca_id=marca_id, status=status)
        db.session.add(novo_teclado)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível cadastrar o teclado. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao cadastrar o teclado.'}, 500

    return {'mensagem': 'Novo teclado cadastrado com sucesso', 'teclado': novo_teclado.to_dict()}, 201

@teclado_bp.route('/', methods=['GET'])
def listar_teclados():
    teclados = Teclado.query.all()
    return [teclado.to_dict() for teclado in teclados], 200

@teclado_bp.route('/<int:id>', methods=['GET'])
def obter_teclado(id):
    teclado = Teclado.query.get_or_404(id)
    return teclado.to_dict(), 200


@teclado_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_teclado(id):
    teclado = Teclado.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('tipo', 'marca_id', 'status')):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'tipo' in dados:
        tipo, erro = validar_tipo(dados['tipo'])
        if erro:
            return erro
        teclado.tipo = tipo

    if 'marca_id' in dados:
        marca_id, erro = validar_marca_id(dados['marca_id'])
        if erro:
            return erro
        teclado.marca_id = marca_id

    if 'status' in dados:
        status, erro = validar_status(dados['status'])
        if erro:
            return erro
        teclado.status = status

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível atualizar o teclado. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar o teclado.'}, 500

    return {'mensagem': 'teclado atualizado com sucesso', 'teclado': teclado.to_dict()}, 200


@teclado_bp.route('/<int:id>', methods=['DELETE'])
def deletar_teclado(id):
    teclado = Teclado.query.get_or_404(id)

    try:
        db.session.delete(teclado)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse teclado, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o teclado.'}, 500

    return {'mensagem': 'teclado deletado com sucesso.'}, 200
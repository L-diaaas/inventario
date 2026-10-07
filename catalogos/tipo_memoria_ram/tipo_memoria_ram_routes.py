from flask import Blueprint, request
from catalogos.tipo_memoria_ram.tipo_memoria_ram_model import TipoMemoria, validar_tipo
from config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

tipo_memoria_ram_bp = Blueprint('tipo_memoria_ram_routes', __name__, url_prefix='/tipo-memoria')


@tipo_memoria_ram_bp.route('/', methods=['POST'])
def adicionar_tipo_ram():
    dados = request.get_json(silent=True) or {}

    tipo, erro = validar_tipo(dados.get('tipo'))
    if erro:
        return erro

    try:
        novo_tipo = TipoMemoria(tipo=tipo)
        db.session.add(novo_tipo)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Esse tipo de memória RAM já está cadastrado.'}, 409

    return {'mensagem': 'Tipo de memória RAM cadastrado com sucesso', 'tipo': novo_tipo.to_dict()}, 201


@tipo_memoria_ram_bp.route('/', methods=['GET'])
def listar_tipos_memoria_ram():
    tipos = TipoMemoria.query.all()
    return [tipo.to_dict() for tipo in tipos], 200


@tipo_memoria_ram_bp.route('/<int:id>', methods=['GET'])
def obter_tipo_ram(id):
    tipo = TipoMemoria.query.get_or_404(id)
    return tipo.to_dict(), 200


@tipo_memoria_ram_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_tipo_memoria_ram(id):
    tipo_ram = TipoMemoria.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if 'tipo' not in dados:
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    tipo, erro = validar_tipo(dados.get('tipo'), id_atual=id)
    if erro:
        return erro

    tipo_ram.tipo = tipo

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Esse tipo de memória RAM já está cadastrado.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar o tipo de memória RAM.'}, 500

    return {'mensagem': 'Tipo de memória RAM atualizado com sucesso', 'tipo': tipo_ram.to_dict()}, 200


@tipo_memoria_ram_bp.route('/<int:id>', methods=['DELETE'])
def deletar_tipo_memoria_ram(id):
    tipo_ram = TipoMemoria.query.get_or_404(id)

    try:
        db.session.delete(tipo_ram)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse tipo, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o tipo de memória RAM.'}, 500

    return {'mensagem': 'Tipo de memória RAM deletado com sucesso.'}, 200
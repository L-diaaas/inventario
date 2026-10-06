from flask import Blueprint, request
from config import db
from componentes.armazenamento.armazenamento_model import Armazenamento, validar_quantidade
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

armazenamento_bp = Blueprint('armazenamento_routes', __name__, url_prefix='/armazenamentos')

STATUS_VALIDOS = {'em_uso', 'sucata'}


def validar_status(status):
    if not isinstance(status, str):
        return None, ({'error': f'Status inválido. Use um de: {", ".join(sorted(STATUS_VALIDOS))}.'}, 400)
    status = status.strip().lower().replace(' ', '_')
    if status not in STATUS_VALIDOS:
        return None, ({'error': f'Status inválido. Use um de: {", ".join(sorted(STATUS_VALIDOS))}.'}, 400)
    return status, None


@armazenamento_bp.route('/', methods=['POST'])
def adicionar_armazenamento():
    dados = request.get_json(silent=True) or {}

    quantidade, erro = validar_quantidade(dados.get('quantidade'))
    if erro:
        return erro

    status, erro = validar_status(dados.get('status', 'em_uso'))
    if erro:
        return erro

    try:
        novo = Armazenamento(quantidade=quantidade, status=status)
        db.session.add(novo)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível cadastrar o armazenamento. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao cadastrar o armazenamento.'}, 500

    return {'mensagem': 'Novo armazenamento cadastrado com sucesso', 'armazenamento': novo.to_dict()}, 201


@armazenamento_bp.route('/', methods=['GET'])
def listar_armazenamentos():
    armazenamentos = Armazenamento.query.all()
    return [a.to_dict() for a in armazenamentos], 200


@armazenamento_bp.route('/<int:id>', methods=['GET'])
def obter_armazenamento(id):
    armazenamento = Armazenamento.query.get_or_404(id)
    return armazenamento.to_dict(), 200


@armazenamento_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_armazenamento(id):
    armazenamento = Armazenamento.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('quantidade', 'status')):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'quantidade' in dados:
        quantidade, erro = validar_quantidade(dados['quantidade'])
        if erro:
            return erro
        armazenamento.quantidade = quantidade

    if 'status' in dados:
        status, erro = validar_status(dados['status'])
        if erro:
            return erro
        armazenamento.status = status

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não foi possível atualizar o armazenamento. Verifique os dados informados.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar o armazenamento.'}, 500

    return {'mensagem': 'Armazenamento atualizado com sucesso', 'armazenamento': armazenamento.to_dict()}, 200


@armazenamento_bp.route('/<int:id>', methods=['DELETE'])
def deletar_armazenamento(id):
    armazenamento = Armazenamento.query.get_or_404(id)

    try:
        db.session.delete(armazenamento)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse armazenamento, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o armazenamento.'}, 500

    return {'mensagem': 'Armazenamento deletado com sucesso.'}, 200
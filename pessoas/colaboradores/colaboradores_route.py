from flask import Blueprint, request
from pessoas.colaboradores.colaboradores_model import (
    Colaboradores, validar_nome_completo, validar_cargo, colaborador_duplicado
)
from config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

colaboradores_bp = Blueprint('colaboradores_routes', __name__, url_prefix='/colaboradores')

MSG_DUPLICADO = 'Já existe um colaborador com esse nome e esse cargo.'

@colaboradores_bp.route('/', methods=['POST'])
def adicionar_colaborador():
    dados = request.get_json(silent=True) or {}

    nome_completo, erro = validar_nome_completo(dados.get('nome_completo'))
    if erro:
        return erro

    cargo, erro = validar_cargo(dados.get('cargo'))
    if erro:
        return erro

    if colaborador_duplicado(nome_completo, cargo):
        return {'error': MSG_DUPLICADO}, 409

    try:
        novo_colaborador = Colaboradores(nome_completo=nome_completo, cargo=cargo)
        db.session.add(novo_colaborador)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': MSG_DUPLICADO}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao cadastrar o colaborador.'}, 500

    return {'mensagem': 'Colaborador cadastrado com sucesso', 'colaborador': novo_colaborador.to_dict()}, 201

@colaboradores_bp.route('/', methods=['GET'])
def listar_colaboradores():
    colaboradores = Colaboradores.query.all()
    return [colaborador.to_dict() for colaborador in colaboradores], 200

@colaboradores_bp.route('/<int:id>', methods=['GET'])
def obter_colaborador(id):
    colaborador = Colaboradores.query.get_or_404(id)
    return colaborador.to_dict(), 200

@colaboradores_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_colaborador(id):
    colaborador = Colaboradores.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('nome_completo', 'cargo')):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    nome_completo = colaborador.nome_completo
    cargo = colaborador.cargo

    if 'nome_completo' in dados:
        nome_completo, erro = validar_nome_completo(dados['nome_completo'])
        if erro:
            return erro

    if 'cargo' in dados:
        cargo, erro = validar_cargo(dados['cargo'])
        if erro:
            return erro

    if colaborador_duplicado(nome_completo, cargo, id_atual=id):
        return {'error': MSG_DUPLICADO}, 409

    colaborador.nome_completo = nome_completo
    colaborador.cargo = cargo

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': MSG_DUPLICADO}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar o colaborador.'}, 500

    return {'mensagem': 'Colaborador atualizado com sucesso', 'colaborador': colaborador.to_dict()}, 200

@colaboradores_bp.route('/<int:id>', methods=['DELETE'])
def deletar_colaborador(id):
    colaborador = Colaboradores.query.get_or_404(id)

    try:
        db.session.delete(colaborador)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse colaborador, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o colaborador.'}, 500

    return {'mensagem': 'Colaborador deletado com sucesso.'}, 200
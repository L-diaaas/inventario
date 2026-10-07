from flask import Blueprint, request
from config import db
from especificacoes.modelo_nobreak.modelo_nobreak_model import ModeloNobreak, validar_nome
from catalogos.marca.marca_model import Marca
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

modelo_nobreak_bp = Blueprint('modelo_nobreak_routes', __name__, url_prefix='/modelos-nobreaks')

def validar_marca(marca_id):
    if isinstance(marca_id,bool) or not isinstance(marca_id, int):
        return None, ({'error': 'A marca é obrigatória e deve ser o id (numero inteiro) de uma marca.'}, 400)
    if not db.session.get(Marca, marca_id):
        return None, ({'error': 'Essa marca não existe ou não foi cadastrada.'}, 400)
    return marca_id, None

@modelo_nobreak_bp.route('/', methods=['POST'])
def adicionar_modelo_nobreak():
    dados = request.get_json(silent=True) or {}

    nome, erro = validar_nome(dados.get('nome'))
    if erro:
        return erro

    marca_id, erro = validar_marca(dados.get('marca_id'))
    if erro:
        return erro

    try:
        novo_modelo_nobreak = ModeloNobreak(nome = nome, marca_id = marca_id)
        db.session.add(novo_modelo_nobreak)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Esse modelo de nobreak já existe.'}, 409

    return {'mensagem': 'Novo modelo de nobreak cadastrado com sucesso', 'modelo_nobreak': novo_modelo_nobreak.to_dict()}, 201

@modelo_nobreak_bp.route('/', methods=['GET'])
def listar_modelos_nobreak():
    modelos = ModeloNobreak.query.all()
    return [modelo.to_dict() for modelo in modelos], 200

@modelo_nobreak_bp.route('/<int:id>', methods=['GET'])
def obter_modelo_nobreak(id):
    modelo = ModeloNobreak.query.get_or_404(id)
    return modelo.to_dict(), 200

@modelo_nobreak_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_modelo_nobreak(id):
    modelo = ModeloNobreak.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in ('nome', 'marca_id')):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'nome' in dados:
        nome, erro = validar_nome(dados['nome'], id_atual=id)
        if erro: 
            return erro
        modelo.nome = nome

    if 'marca_id' in dados:
            marca_id, erro = validar_marca(dados['marca_id'])
            if erro: 
                return erro
            modelo.marca_id = marca_id

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Esse modelo de nobreak já existe.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar a modelo de nobreak.'}, 500

    return {'mensagem': 'Modelo de nobreak atualizado com sucesso', 'modelo_nobreak': modelo.to_dict()}, 200

@modelo_nobreak_bp.route('/<int:id>', methods=['DELETE'])
def deletar_modelo_nobreak(id):
    modelo = ModeloNobreak.query.get_or_404(id)

    try:
        db.session.delete(modelo)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse modelo de nobreak, pois ela está vinculada a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o modelo de nobreak.'}, 500

    return {'mensagem': 'Modelo de nobreak deletado com sucesso.'}, 200

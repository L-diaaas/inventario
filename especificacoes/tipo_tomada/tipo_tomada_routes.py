import os
import uuid
from flask import Blueprint, request, current_app, send_from_directory
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from config import db
from .tipo_tomada_model import TipoTomada, validar_tipo_tomada

tipo_tomada_bp = Blueprint('tipo_tomada_routes', __name__, url_prefix='/tipos-tomadas')

EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def pasta_upload():
    pasta = os.path.join(current_app.root_path, 'uploads', 'tipos_tomadas')
    os.makedirs(pasta, exist_ok=True)
    return pasta

def validar_foto(arquivo):
    if arquivo is None or arquivo.filename == '':
        return None, None

    extensao = arquivo.filename.rsplit('.', 1)[-1].lower() if '.' in arquivo.filename else ''
    if extensao not in EXTENSOES_PERMITIDAS:
        return None, ({'error': 'Formato de imagem inválido. Use: png, jpg, jpeg, webp ou gif.'}, 400)

    return arquivo, None

def salvar_foto(arquivo):
    extensao = arquivo.filename.rsplit('.', 1)[-1].lower()
    nome_arquivo = f'{uuid.uuid4().hex}.{extensao}'
    arquivo.save(os.path.join(pasta_upload(), nome_arquivo))
    return nome_arquivo

def remover_foto(nome_arquivo):
    if not nome_arquivo:
        return
    try:
        os.remove(os.path.join(pasta_upload(), nome_arquivo))
    except FileNotFoundError:
        pass

def obter_dados():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form

@tipo_tomada_bp.route('/', methods=['POST'])
def adicionar_tipo_tomada():
    dados = obter_dados()

    nome, erro = validar_tipo_tomada(dados.get('nome'))
    if erro:
        return erro

    arquivo, erro = validar_foto(request.files.get('foto'))
    if erro:
        return erro

    nome_foto = salvar_foto(arquivo) if arquivo else None

    try:
        novo = TipoTomada(nome, nome_foto)
        db.session.add(novo)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        remover_foto(nome_foto)
        return {'error': 'Esse tipo de tomada já está cadastrado.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        remover_foto(nome_foto)
        return {'error': 'Erro ao cadastrar o tipo de tomada.'}, 500

    return {'mensagem': 'Novo tipo de tomada adicionado com sucesso',
            'tipo_tomada': novo.to_dict()}, 201

@tipo_tomada_bp.route('/', methods=['GET'])
def listar_tipos_tomadas():
    tipos = TipoTomada.query.order_by(TipoTomada.nome).all()
    return [t.to_dict() for t in tipos], 200

@tipo_tomada_bp.route('/<int:id>', methods=['GET'])
def obter_tipo_tomada(id):
    registro = db.get_or_404(TipoTomada, id)
    return registro.to_dict(), 200

@tipo_tomada_bp.route('/<int:id>/foto', methods=['GET'])
def obter_foto_tipo_tomada(id):
    registro = db.get_or_404(TipoTomada, id)
    if not registro.foto:
        return {'error': 'Este tipo de tomada não possui foto.'}, 404
    return send_from_directory(pasta_upload(), registro.foto)

@tipo_tomada_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_tipo_tomada(id):
    registro = db.get_or_404(TipoTomada, id)
    dados = obter_dados()

    remover = str(dados.get('remover_foto', '')).lower() in ('true', '1')
    arquivo_enviado = request.files.get('foto')
    tem_foto_nova = arquivo_enviado is not None and arquivo_enviado.filename != ''

    if 'nome' not in dados and not tem_foto_nova and not remover:
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'nome' in dados:
        nome, erro = validar_tipo_tomada(dados.get('nome'), id_atual=id)
        if erro:
            return erro
        registro.nome = nome

    foto_antiga = registro.foto
    foto_nova = None

    if tem_foto_nova:
        arquivo, erro = validar_foto(arquivo_enviado)
        if erro:
            return erro
        foto_nova = salvar_foto(arquivo)
        registro.foto = foto_nova
    elif remover:
        registro.foto = None

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        remover_foto(foto_nova)
        return {'error': 'Esse tipo de tomada já está cadastrado.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        remover_foto(foto_nova)
        return {'error': 'Erro ao atualizar o tipo de tomada.'}, 500

    if foto_nova or remover:
        remover_foto(foto_antiga)

    return {'mensagem': 'Tipo de tomada atualizado com sucesso',
            'tipo_tomada': registro.to_dict()}, 200

@tipo_tomada_bp.route('/<int:id>', methods=['DELETE'])
def deletar_tipo_tomada(id):
    registro = db.get_or_404(TipoTomada, id)
    foto = registro.foto

    try:
        db.session.delete(registro)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse tipo de tomada, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o tipo de tomada.'}, 500

    remover_foto(foto)
    return {'mensagem': 'Tipo de tomada deletado com sucesso.'}, 200
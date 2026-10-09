import os
import uuid
from flask import Blueprint, request, current_app, send_from_directory
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from config import db
from equipamentos.nobreak.nobreak_model import (
    Nobreak, STATUS_NOBREAK, validar_codigo, validar_status, validar_data_troca_bateria
)
from especificacoes.modelo_nobreak.modelo_nobreak_model import ModeloNobreak
from especificacoes.voltagem.voltagem_model import Voltagem
from especificacoes.qtd_tomadas.qtd_tomadas_model import QuantidadeTomadas
from especificacoes.tipo_tomada.tipo_tomada_model import TipoTomada

nobreak_bp = Blueprint('nobreak_routes', __name__, url_prefix='/nobreaks')

EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

CHAVES_ESTRANGEIRAS = {
    'modelo_nobreak_id': (ModeloNobreak, 'modelo do nobreak'),
    'voltagem_id': (Voltagem, 'voltagem'),
    'qtd_tomadas_id': (QuantidadeTomadas, 'quantidade de tomadas'),
    'tipo_tomada_id': (TipoTomada, 'tipo de tomada'),
}

CAMPOS_EDITAVEIS = ('codigo', 'status', 'data_troca_bateria', *CHAVES_ESTRANGEIRAS)

def pasta_upload():
    pasta = os.path.join(current_app.root_path, 'uploads', 'nobreaks')
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

def validar_chave_estrangeira(campo, valor):
    modelo, descricao = CHAVES_ESTRANGEIRAS[campo]

    if isinstance(valor, str) and valor.strip().isdigit():
        valor = int(valor.strip())

    if isinstance(valor, bool) or not isinstance(valor, int):
        return None, ({'error': f'O campo {campo} é obrigatório e deve ser o id (número inteiro) de {descricao}.'}, 400)

    if not db.session.get(modelo, valor):
        return None, ({'error': f'Esse {descricao} não existe ou não foi cadastrado.'}, 400)

    return valor, None

# ---------- rotas ----------

@nobreak_bp.route('/', methods=['POST'])
def adicionar_nobreak():
    dados = obter_dados()

    codigo, erro = validar_codigo(dados.get('codigo'))
    if erro:
        return erro

    status, erro = validar_status(dados.get('status', 'em_uso'))
    if erro:
        return erro

    data_troca, erro = validar_data_troca_bateria(dados.get('data_troca_bateria'))
    if erro:
        return erro

    ids = {}
    for campo in CHAVES_ESTRANGEIRAS:
        ids[campo], erro = validar_chave_estrangeira(campo, dados.get(campo))
        if erro:
            return erro

    arquivo, erro = validar_foto(request.files.get('foto'))
    if erro:
        return erro

    nome_foto = salvar_foto(arquivo) if arquivo else None

    try:
        novo = Nobreak(codigo=codigo, status=status, data_troca_bateria=data_troca,
                       foto=nome_foto, **ids)
        db.session.add(novo)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        remover_foto(nome_foto)
        return {'error': 'Já existe um nobreak com esse código.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        remover_foto(nome_foto)
        return {'error': 'Erro ao cadastrar o nobreak.'}, 500

    return {'mensagem': 'Novo nobreak cadastrado com sucesso', 'nobreak': novo.to_dict()}, 201

@nobreak_bp.route('/', methods=['GET'])
def listar_nobreaks():
    query = Nobreak.query

    status = request.args.get('status')
    if status:
        status, erro = validar_status(status)
        if erro:
            return erro
        query = query.filter(Nobreak.status == status)

    nobreaks = query.order_by(Nobreak.codigo).all()
    return [n.to_dict() for n in nobreaks], 200

@nobreak_bp.route('/<int:id>', methods=['GET'])
def obter_nobreak(id):
    nobreak = db.get_or_404(Nobreak, id)
    return nobreak.to_dict(), 200

@nobreak_bp.route('/<int:id>/foto', methods=['GET'])
def obter_foto_nobreak(id):
    nobreak = db.get_or_404(Nobreak, id)
    if not nobreak.foto:
        return {'error': 'Este nobreak não possui foto.'}, 404
    return send_from_directory(pasta_upload(), nobreak.foto)

@nobreak_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_nobreak(id):
    nobreak = db.get_or_404(Nobreak, id)
    dados = obter_dados()

    remover = str(dados.get('remover_foto', '')).lower() in ('true', '1')
    arquivo_enviado = request.files.get('foto')
    tem_foto_nova = arquivo_enviado is not None and arquivo_enviado.filename != ''

    if not any(campo in dados for campo in CAMPOS_EDITAVEIS) and not tem_foto_nova and not remover:
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400

    if 'codigo' in dados:
        codigo, erro = validar_codigo(dados['codigo'], id_atual=id)
        if erro:
            return erro
        nobreak.codigo = codigo

    if 'status' in dados:
        status, erro = validar_status(dados['status'])
        if erro:
            return erro
        nobreak.status = status

    if 'data_troca_bateria' in dados:
        data_troca, erro = validar_data_troca_bateria(dados['data_troca_bateria'])
        if erro:
            return erro
        nobreak.data_troca_bateria = data_troca

    for campo in CHAVES_ESTRANGEIRAS:
        if campo in dados:
            valor, erro = validar_chave_estrangeira(campo, dados[campo])
            if erro:
                return erro
            setattr(nobreak, campo, valor)

    foto_antiga = nobreak.foto
    foto_nova = None

    if tem_foto_nova:
        arquivo, erro = validar_foto(arquivo_enviado)
        if erro:
            return erro
        foto_nova = salvar_foto(arquivo)
        nobreak.foto = foto_nova
    elif remover:
        nobreak.foto = None

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        remover_foto(foto_nova)
        return {'error': 'Já existe um nobreak com esse código.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        remover_foto(foto_nova)
        return {'error': 'Erro ao atualizar o nobreak.'}, 500

    if foto_nova or remover:
        remover_foto(foto_antiga)

    return {'mensagem': 'Nobreak atualizado com sucesso', 'nobreak': nobreak.to_dict()}, 200

@nobreak_bp.route('/<int:id>', methods=['DELETE'])
def deletar_nobreak(id):
    nobreak = db.get_or_404(Nobreak, id)
    foto = nobreak.foto

    try:
        db.session.delete(nobreak)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar esse nobreak, pois ele está vinculado a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar o nobreak.'}, 500

    remover_foto(foto)
    return {'mensagem': 'Nobreak deletado com sucesso.'}, 200
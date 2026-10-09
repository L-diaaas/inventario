from flask import Blueprint, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from config import db
from equipamentos.maquina.maquina_model import (
    Maquina, validar_nome_maquina, validar_s_tag, validar_status,
    validar_internet, validar_data, validar_coerencia_datas
)
from equipamentos.nobreak.nobreak_model import Nobreak
from especificacoes.modelo_maquina.modelo_maquina_model import ModeloMaquina
from catalogos.sistema_operacional.sistema_operacional_model import SistemaOperacional
from pessoas.colaboradores.colaboradores_model import Colaboradores
from perifericos.monitor.monitor_model import Monitor
from perifericos.teclado.teclado_model import Teclado
from perifericos.mouse.mouse_model import Mouse

maquina_bp = Blueprint('maquina_routes', __name__, url_prefix='/maquinas')

CHAVES_ESTRANGEIRAS = {
    'modelo_id': (ModeloMaquina, 'o modelo da máquina', True),
    'colaborador_id': (Colaboradores, 'o colaborador', False),
    'nobreak_id': (Nobreak, 'o nobreak', False),
    'sistema_operacional_id': (SistemaOperacional, 'o sistema operacional', False),
    'monitor_id': (Monitor, 'o monitor', False),
    'monitor_secundario_id': (Monitor, 'o monitor secundário', False),
    'teclado_id': (Teclado, 'o teclado', False),
    'mouse_id': (Mouse, 'o mouse', False),
}

PERIFERICOS_EXCLUSIVOS = {
    'monitor_id': (Monitor, ('monitor_id', 'monitor_secundario_id')),
    'monitor_secundario_id': (Monitor, ('monitor_id', 'monitor_secundario_id')),
    'teclado_id': (Teclado, ('teclado_id',)),
    'mouse_id': (Mouse, ('mouse_id',)),
}

STATUS_INDISPONIVEIS = ('sucata', 'inativo')

CAMPOS_DATA = {
    'data_compra': 'A data de compra',
    'fim_garantia': 'O fim da garantia',
    'data_manutencao': 'A data da manutenção',
}

CAMPOS_EDITAVEIS = ('nome', 's_tag', 'status', 'internet', *CAMPOS_DATA, *CHAVES_ESTRANGEIRAS)

def validar_chave_estrangeira(campo, valor):
    modelo, descricao, obrigatorio = CHAVES_ESTRANGEIRAS[campo]

    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if obrigatorio:
            return None, ({'error': f'O campo {campo} é obrigatório e deve ser o id de {descricao}.'}, 400)
        return None, None

    if isinstance(valor, str) and valor.strip().isdigit():
        valor = int(valor.strip())

    if isinstance(valor, bool) or not isinstance(valor, int):
        return None, ({'error': f'O campo {campo} deve ser o id (número inteiro) de {descricao}.'}, 400)

    if not db.session.get(modelo, valor):
        return None, ({'error': f'Não existe {descricao} com o id {valor}.'}, 400)

    return valor, None

def validar_equipamentos(final, campos_a_checar, id_atual=None):
    if final['monitor_secundario_id'] and not final['monitor_id']:
        return {'error': 'Não é possível definir o monitor secundário sem o monitor principal.'}, 400
    if final['monitor_id'] and final['monitor_id'] == final['monitor_secundario_id']:
        return {'error': 'O monitor principal e o secundário não podem ser o mesmo monitor.'}, 400

    for campo in campos_a_checar:
        if campo not in PERIFERICOS_EXCLUSIVOS or not final[campo]:
            continue
        modelo, colunas = PERIFERICOS_EXCLUSIVOS[campo]
        valor = final[campo]

        item = db.session.get(modelo, valor)
        if item.status in STATUS_INDISPONIVEIS:
            return {'error': f'O {campo.replace("_id", "").replace("_", " ")} informado está com status "{item.status}" e não pode ser vinculado.'}, 400

        query = Maquina.query.filter(or_(*[getattr(Maquina, c) == valor for c in colunas]))
        if id_atual:
            query = query.filter(Maquina.id != id_atual)
        outra = query.first()
        if outra:
            return {'error': f'Esse equipamento já está vinculado à máquina "{outra.nome}".'}, 409

    return None

@maquina_bp.route('/', methods=['POST'])
def adicionar_maquina():
    dados = request.get_json(silent=True) or {}
    campos = {}

    campos['nome'], erro = validar_nome_maquina(dados.get('nome'))
    if erro:
        return erro

    campos['s_tag'], erro = validar_s_tag(dados.get('s_tag'))
    if erro:
        return erro

    campos['status'], erro = validar_status(dados.get('status', 'em_uso'))
    if erro:
        return erro

    campos['internet'], erro = validar_internet(dados.get('internet', True))
    if erro:
        return erro

    for campo, rotulo in CAMPOS_DATA.items():
        campos[campo], erro = validar_data(dados.get(campo), rotulo)
        if erro:
            return erro

    erro = validar_coerencia_datas(campos['data_compra'], campos['fim_garantia'], campos['data_manutencao'])
    if erro:
        return erro

    for campo in CHAVES_ESTRANGEIRAS:
        campos[campo], erro = validar_chave_estrangeira(campo, dados.get(campo))
        if erro:
            return erro

    erro = validar_equipamentos(campos, campos_a_checar=PERIFERICOS_EXCLUSIVOS)
    if erro:
        return erro

    try:
        nova = Maquina(**campos)
        db.session.add(nova)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Já existe uma máquina com esse nome ou service tag.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao cadastrar a máquina.'}, 500

    return {'mensagem': 'Nova máquina cadastrada com sucesso', 'maquina': nova.to_dict()}, 201

@maquina_bp.route('/', methods=['GET'])
def listar_maquinas():
    query = Maquina.query

    status = request.args.get('status')
    if status:
        status, erro = validar_status(status)
        if erro:
            return erro
        query = query.filter(Maquina.status == status)

    colaborador_id = request.args.get('colaborador_id')
    if colaborador_id:
        if not colaborador_id.isdigit():
            return {'error': 'colaborador_id deve ser um número inteiro.'}, 400
        query = query.filter(Maquina.colaborador_id == int(colaborador_id))

    maquinas = query.order_by(Maquina.nome).all()
    return [m.to_dict() for m in maquinas], 200

@maquina_bp.route('/<int:id>', methods=['GET'])
def obter_maquina(id):
    maquina = db.get_or_404(Maquina, id)
    return maquina.to_dict(), 200

@maquina_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_maquina(id):
    maquina = db.get_or_404(Maquina, id)
    dados = request.get_json(silent=True) or {}

    if not any(campo in dados for campo in CAMPOS_EDITAVEIS):
        return {'error': 'Nenhum campo para atualizar foi informado.'}, 400
    novos = {}

    if 'nome' in dados:
        novos['nome'], erro = validar_nome_maquina(dados['nome'], id_atual=id)
        if erro:
            return erro

    if 's_tag' in dados:
        novos['s_tag'], erro = validar_s_tag(dados['s_tag'], id_atual=id)
        if erro:
            return erro

    if 'status' in dados:
        novos['status'], erro = validar_status(dados['status'])
        if erro:
            return erro

    if 'internet' in dados:
        novos['internet'], erro = validar_internet(dados['internet'])
        if erro:
            return erro

    for campo, rotulo in CAMPOS_DATA.items():
        if campo in dados:
            novos[campo], erro = validar_data(dados[campo], rotulo)
            if erro:
                return erro

    for campo in CHAVES_ESTRANGEIRAS:
        if campo in dados:
            novos[campo], erro = validar_chave_estrangeira(campo, dados[campo])
            if erro:
                return erro

    final = {campo: novos.get(campo, getattr(maquina, campo)) for campo in CAMPOS_EDITAVEIS}

    erro = validar_coerencia_datas(final['data_compra'], final['fim_garantia'], final['data_manutencao'])
    if erro:
        return erro

    alterados = [c for c in PERIFERICOS_EXCLUSIVOS if c in novos and novos[c] != getattr(maquina, c)]
    erro = validar_equipamentos(final, campos_a_checar=alterados, id_atual=id)
    if erro:
        return erro


    for campo, valor in novos.items():
        setattr(maquina, campo, valor)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Já existe uma máquina com esse nome ou service tag.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao atualizar a máquina.'}, 500

    return {'mensagem': 'Máquina atualizada com sucesso', 'maquina': maquina.to_dict()}, 200

@maquina_bp.route('/<int:id>', methods=['DELETE'])
def deletar_maquina(id):
    maquina = db.get_or_404(Maquina, id)

    try:
        db.session.delete(maquina)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Não é possível deletar essa máquina, pois ela está vinculada a outros registros.'}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {'error': 'Erro ao deletar a máquina.'}, 500

    return {'mensagem': 'Máquina deletada com sucesso.'}, 200
from flask import Blueprint, request, jsonify
from tipo_memoria_ram.tipo_memoria_ram_model import TipoMemoria
from config import db
from sqlalchemy.exc import IntegrityError

tipo_memoria_ram_bp = Blueprint('tipo_memoria_ram_routes', __name__, url_prefix='/tipo-memoria')

@tipo_memoria_ram_bp.route('/', methods=['POST'])
def adicionar_tipo_ram():
    tipo = request.json.get('tipo')

    novo_tipo_memoria_ram = TipoMemoria(tipo=tipo)
    db.session.add(novo_tipo_memoria_ram)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao cadastrar novo tipo de memoria ram."}, 400
    return [novo_tipo_memoria_ram.to_dict()], 201

@tipo_memoria_ram_bp.route('/', methods=['GET'])
def listar_tipos_memoria_ram():
    tipos_ram = TipoMemoria.query.all()
    return [tipo_ram.to_dict for tipo_ram in tipos_ram]

@tipo_memoria_ram_bp.route('/<int:id>', methods=['GET'])
def obter_tipo_ram(id):
    tipo_ram = TipoMemoria.query.get_or_404(id)
    return tipo_ram.to_dict(), 200

@tipo_memoria_ram_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_tipo_memoria_ram(id):
    tipo_ram = TipoMemoria.query.get_or_404(id)

    dados = request.json or {}

    if 'tipo' in dados:
        tipo = dados.get('tipo')
        if 'tipo' and TipoMemoria.query.filter(TipoMemoria.tipo == tipo, TipoMemoria.id != id).first():
            return {"error": "Esse tipo de memória ram já está cadastrado"}, 400
        tipo_ram.tipo = tipo

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao atualizar o tipo de memória ram"}, 400
    return tipo_ram.to_dict()

@tipo_memoria_ram_bp.route('/<int:id>', methods=['DELETE'])
def deletar_tipo_memoria_ram(id):
    tipo_memoria = TipoMemoria.query.get_or_404(id)
    db.session.delete(tipo_memoria)
    db.session.commit()
    return {"message": "Tipo de memoria ram deletado com sucesso."}, 201
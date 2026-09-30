from flask import Blueprint, request, jsonify
from memoria_ram.memoria_ram_model import MemoriaRam
from sqlalchemy.exc import IntegrityError
from config import db

memoria_ram_bp = Blueprint('memoria_ram_routes', __name__, url_prefix='/memoria-ram')

@memoria_ram_bp.route('/', methods=['POST'])
def adicionar_memoria_ram():
    quantidade = request.json.get('quantidade')

    nova_quantidade_memoria_ram = MemoriaRam(quantidade=quantidade)
    db.session.add(nova_quantidade_memoria_ram)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao cadastrar nova quantidade de memória ram"}, 400
    return [nova_quantidade_memoria_ram.to_dict()], 201

@memoria_ram_bp.route('/', methods=['GET'])
def listar_memorias_ram():
    memorias_ram = MemoriaRam.query.all()
    return [memoria_ram.to_dict() for memoria_ram in memorias_ram], 200

@memoria_ram_bp.route('/<int:id>', methods=['GET'])
def obter_memoria_ram(id):
    memoria_ram = MemoriaRam.query.get_or_404(id)
    return memoria_ram.to_dict(), 200

@memoria_ram_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_quantidade_memoria_ram(id):
    memoria_ram = MemoriaRam.query.get_or_404(id)

    dados = request.json or {}

    if 'quantidade' in dados:
        quantidade = dados.get('quantidade')
        if 'quantidade' and MemoriaRam.query.filter(MemoriaRam.quantidade == quantidade, MemoriaRam.id != id).first():
            return {"error": "Essa quantidade de memória ram já está cadastrada."}, 400
        memoria_ram.quantidade = quantidade

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao atualizar a quantidade de memória ram."}, 500
    return memoria_ram.to_dict()

@memoria_ram_bp.route('<int:id>', methods=['DELETE'])
def deletar_quantidade_memoria_ram(id):
    quantidade_memoria_ram = MemoriaRam.query.get_or_404(id)
    db.session.delete(quantidade_memoria_ram)
    db.session.commit()
    return {"message": "Quantidade de memória a deletada com sucesso."}, 200

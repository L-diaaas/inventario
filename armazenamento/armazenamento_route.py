from flask import Blueprint, request, jsonify
from armazenamento.armazenamento_model import Armazenamento
from config import db
from sqlalchemy.exc import IntegrityError

armazenamento_bp = Blueprint('armazenamento_routes', __name__, url_prefix='/armazenamento')

@armazenamento_bp.route('/', methods=['POST'])
def adicionar_armazenamento():
    quantidade = request.json.get('quantidade')

    novo_armazenamento = Armazenamento(quantidade=quantidade)
    db.session.add(novo_armazenamento)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao cadastrar nova quantidade de armazenamento"}, 400
    return[novo_armazenamento.to_dict()], 201 

@armazenamento_bp.route('/', methods=['GET'])
def listar_quantidades_armazenamento():
    quantidades = Armazenamento.query.all()
    return [quantidade.to_dict() for quantidade in quantidades]

@armazenamento_bp.route('/<int:id>', methods=['GET'])
def obter_quantidade_armazenamento(id):
    quantidade = Armazenamento.query.get_or_404(id)
    return quantidade.to_dict(), 200

@armazenamento_bp.route('/<int:id>', methods=['PATCH'])
def atualizar_quantidade_armazenamento(id):
    armazenamento = Armazenamento.query.get_or_404(id)

    dados = request.json or {}

    if 'quantidade' in dados:
        quantidade = dados.get('quantidade')
        if quantidade and Armazenamento.query.filter(Armazenamento.quantidade == quantidade, Armazenamento.id != id).first():
            return {"error": "Essa quantidade de armazenamento já existe."}, 400
        armazenamento.quantidade = quantidade

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Erro ao atualizar a quantidade de Armazenamento"}, 500
    
    return armazenamento.to_dict()

@armazenamento_bp.route('/<int:id>', methods=['DELETE'])
def deletar_quantidade_armazenamento(id):
    quantidade = Armazenamento.query.get_or_404(id)
    db.session.delete(quantidade)
    db.session.commit()
    return {"message": "Quantidade de armazenamento deletada com sucesso"}, 200


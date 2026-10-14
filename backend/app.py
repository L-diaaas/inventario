from backend.config import app, db
from flask import jsonify, request
from backend.registrar import registrar_blueprints
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from backend.pessoas.equipe_ti.equipe_ti_model import EquipeTI

jwt = JWTManager(app)
registrar_blueprints(app)

@app.route("/", methods=['GET'])
def home():
    return "API Inventario Cervix funcionando!"

@app.before_request
def checar_ativo():
    rotas_livres = {'/equipe-ti/login', '/'}
    if request.path in rotas_livres:
        return

    try:
        verify_jwt_in_request(optional=True)
    except Exception:
        return

    uid = get_jwt_identity()
    if not uid:
        return

    membro = EquipeTI.query.get(int(uid))
    if not membro or not membro.ativo:
        return jsonify({'error': 'Conta inativa ou inexistente.'}), 401
    
@jwt.unauthorized_loader
def faltando_token(msg):
    return jsonify({'error': 'Token de acesso ausente.'}), 401

@jwt.invalid_token_loader
def token_invalido(msg):
    return jsonify({'error': 'Token inválido.'}), 401

@jwt.expired_token_loader
def token_expirado(jwt_header, jwt_payload):
    return jsonify({'error': 'Token expirado.'}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
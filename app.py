from config import app, db
from flask import jsonify, request, g
from registrar import registrar_blueprints
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from pessoas.equipe_ti.equipe_ti_model import EquipeTI

jwt = JWTManager(app)
registrar_blueprints(app)

with app.app_context():
    db.create_all()

ROTAS_LIVRES = {'/', '/equipe-ti/login'}

@app.route("/", methods=['GET'])
def home():
    return "API Inventario Cervix funcionando!"

@app.before_request
def exigir_autenticacao():
    if request.method == 'OPTIONS' or request.path in ROTAS_LIVRES:
        return

    # Se faltar token ou ele for inválido/expirado, levanta erro e cai nos handlers abaixo (401)
    verify_jwt_in_request()

    membro = db.session.get(EquipeTI, int(get_jwt_identity()))
    if not membro or not membro.ativo:
        return jsonify({'error': 'Conta inativa ou inexistente.'}), 401
    g.membro = membro

@jwt.unauthorized_loader
def faltando_token(msg):
    return jsonify({'error': 'Token de acesso ausente.'}), 401

@jwt.invalid_token_loader
def token_invalido(msg):
    return jsonify({'error': 'Token inválido.'}), 401

@jwt.expired_token_loader
def token_expirado(jwt_header, jwt_payload):
    return jsonify({'error': 'Token expirado.'}), 401

@app.errorhandler(429)
def muitas_requisicoes(e):
    return jsonify({'error': 'Muitas requisições. Aguarde um pouco e tente novamente.'}), 429

@app.errorhandler(413)
def arquivo_grande(e):
    return jsonify({'error': 'Arquivo grande demais (máximo 5 MB).'}), 413

@app.errorhandler(500)
def erro_interno(e):
    app.logger.exception('Erro interno não tratado')
    return jsonify({'error': 'Erro interno do servidor.'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
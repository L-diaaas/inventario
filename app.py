from config import app, db
from registrar import registrar_blueprints

registrar_blueprints(app)

@app.route("/", methods=['GET'])
def home():
    return "API Inventario Cervix funcionando!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
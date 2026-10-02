from config import app, db
from processador.processador_route import processador_bp
from catalogos.sistema_operacional.sistema_operacional_route import sistema_operacional_bp
from armazenamento.armazenamento_route import armazenamento_bp
from memoria_ram.memoria_ram_route import memoria_ram_bp
from catalogos.tipo_memoria_ram.tipo_memoria_ram_route import tipo_memoria_ram_bp
from catalogos.marca.marca_route import marca_bp
from localizacao.andar.andar_route import andar_bp
from localizacao.mesa.mesa_route import mesa_bp


app.register_blueprint(processador_bp)
app.register_blueprint(sistema_operacional_bp)
app.register_blueprint(armazenamento_bp)
app.register_blueprint(memoria_ram_bp)
app.register_blueprint(tipo_memoria_ram_bp)
app.register_blueprint(marca_bp)
app.register_blueprint(andar_bp)
app.register_blueprint(mesa_bp)

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
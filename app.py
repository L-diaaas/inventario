from config import app, db
from componentes.processador.processador_route import processador_bp
from catalogos.sistema_operacional.sistema_operacional_route import sistema_operacional_bp
from componentes.armazenamento.armazenamento_route import armazenamento_bp
from componentes.memoria_ram.memoria_ram_route import memoria_ram_bp
from catalogos.tipo_memoria_ram.tipo_memoria_ram_route import tipo_memoria_ram_bp
from catalogos.marca.marca_route import marca_bp
from localizacao.andar.andar_route import andar_bp
from localizacao.mesa.mesa_route import mesa_bp
from especificacoes.modelo_maquina.modelo_maquina_route import modelo_maquina_bp
from especificacoes.modelo_nobreak.modelo_nobreak_route import modelo_nobreak_bp
from especificacoes.qtd_tomadas.qtd_tomadas_route import quantidade_tomadas_bp
from especificacoes.voltagem.voltagem_route import voltagem_bp
from especificacoes.tipo_tomada.tipo_tomada_route import tipo_tomada_bp

app.register_blueprint(processador_bp)
app.register_blueprint(sistema_operacional_bp)
app.register_blueprint(armazenamento_bp)
app.register_blueprint(memoria_ram_bp)
app.register_blueprint(tipo_memoria_ram_bp)
app.register_blueprint(marca_bp)
app.register_blueprint(andar_bp)
app.register_blueprint(mesa_bp)
app.register_blueprint(modelo_maquina_bp)
app.register_blueprint(modelo_nobreak_bp)
app.register_blueprint(quantidade_tomadas_bp)
app.register_blueprint(voltagem_bp)
app.register_blueprint(tipo_tomada_bp)

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
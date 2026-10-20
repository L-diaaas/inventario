from config import db

STATUS_PROCESSADOR = ('em_uso', 'sucata', 'sobrando')

class Processador(db.Model):
    __tablename__ = 'processador'

    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.Enum(*STATUS_PROCESSADOR, name='status_processador'),
        nullable=False,
        default='em_uso'
    )

    marca_id = db.Column(db.Integer, db.ForeignKey('marcas.id'), nullable=False)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquinas.id'), nullable=True)

    maquina = db.relationship('Maquina', backref='processadores')

    def __init__(self, modelo, marca_id, status='em_uso', maquina_id=None):
        self.modelo = modelo
        self.marca_id = marca_id
        self.status = status
        self.maquina_id = maquina_id

    def to_dict(self):
        return {
            'id': self.id,
            'modelo': self.modelo,
            'nome': self.modelo,
            'status': self.status,
            'maquina_id': self.maquina_id,
            'maquina': {
                'id': self.maquina.id,
                'nome': self.maquina.nome,
                's_tag': self.maquina.s_tag
            } if self.maquina else None,
            'marca': {
                'id': self.marca.id,
                'nome': self.marca.nome
            } if self.marca else None
        }

def validar_modelo(modelo):
    if not isinstance(modelo, str) or not modelo.strip():
        return None, ({'error': 'O modelo do processador é obrigatório.'}, 400)

    modelo = modelo.strip()
    if len(modelo) < 2 or len(modelo) > 100:
        return None, ({'error': 'O modelo deve ter entre 2 e 100 caracteres.'}, 400)

    return modelo, None
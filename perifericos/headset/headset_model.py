from config import db

class Headset(db.Model):
    __tablename__ = 'headsets'

    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.Enum('livre', 'ocupado', 'sucata', 'inativo', name='status_headset'),
        nullable=False,
        default='livre'
    )

    marca_id = db.Column(db.Integer, db.ForeignKey('marcas.id'), nullable=False)
    marca = db.relationship('Marca', backref='headsets')

    def __init__(self, modelo, marca_id, status='livre'):
        self.modelo = modelo
        self.marca_id = marca_id
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'modelo': self.modelo,
            'status': self.status,
            'marca': {
                'id': self.marca.id,
                'nome': self.marca.nome
            } if self.marca else None
        }


def validar_modelo(modelo):
    if not isinstance(modelo, str) or not modelo.strip():
        return None, ({'error': 'O modelo do headset é obrigatório.'}, 400)

    modelo = modelo.strip()

    if len(modelo) < 2:
        return None, ({'error': 'O modelo do headset deve ter no mínimo 2 caracteres.'}, 400)
    if len(modelo) > 100:
        return None, ({'error': 'O modelo do headset deve ter no máximo 100 caracteres.'}, 400)

    return modelo, None
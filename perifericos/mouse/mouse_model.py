from config import db

class Mouse(db.Model):
    __tablename__ = 'mouses'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(
        db.Enum('com_fio', 'bluetooth', name='tipo_mouse'),
        nullable=False
    )
    status = db.Column(
        db.Enum('livre', 'ocupado', 'sucata', 'inativo', name='status_mouse'),
        nullable=False,
        default='livre'
    )

    marca_id = db.Column(db.Integer, db.ForeignKey('marcas.id'), nullable=False)
    marca = db.relationship('Marca', backref='mouses')

    def __init__(self, tipo, marca_id, status='livre'):
        self.tipo = tipo
        self.marca_id = marca_id
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'status': self.status,
            'marca': {
                'id': self.marca.id,
                'nome': self.marca.nome
            } if self.marca else None
        }


from config import db

class Mesa(db.Model):
    __table__ = 'mesas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    andar_id = db.Column(db.Integer, db.ForeignKey('andares.id'), nullable=False)

    def __init__(self, nome, andar_id):
        self.nome = nome
        self.andar_id = andar_id

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'andar_id': self.andar_id
        }

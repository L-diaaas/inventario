from config import db

class Mesa(db.Model):
    __tablename__ = 'mesas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    status = db.Column( db.Enum('livre', 'ocupada', 'sucata', 'inativa', 'refeitorio', name='status_mesa'), nullable=False, default='livre')

    andar_id = db.Column(db.Integer, db.ForeignKey('andares.id'), nullable=False)

    def __init__(self, nome, andar_id, status):
        self.nome = nome
        self.andar_id = andar_id
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'status': self.status,
            'andar':{
                'id' : self.andar.id,
                'nome': self.andar.nome
            } if self.andar else None
        }


from config import db

class Andar(db.Model):
    __tablename__ = 'andares'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

    andar = db.relationship('Mesa', backref='andar')

    def __init__(self, nome):
        self.nome = nome

    def to_dict(self):
        return {
            'id' : self.id,
            'nome' : self.nome
        }
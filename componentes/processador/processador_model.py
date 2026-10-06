from config import db

class Processador(db.Model):
    __tablename__ = "processador"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)

    def __init__(self, tipo):
        self.tipo = tipo

    def to_dict(self):
        return {
            'id' : self.id,
            'tipo' : self.tipo
        }
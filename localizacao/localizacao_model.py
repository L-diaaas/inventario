from config import db

class Localizacao(db.Model):
    __tablename__ = 'localizacao'

    id = db.Column(db.Integer, primary_key=True)
    mesa = db.Column(db.Integer, nullable=False)
    andar = db.Column(db.String(20), nullable=False)

    def __init__(self, mesa, andar):
        self.mesa = mesa
        self.andar = andar
        
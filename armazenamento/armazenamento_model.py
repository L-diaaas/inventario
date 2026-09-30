from config import db

class Armazenamento(db.Model):
    __tablename__ = 'armazenamento'

    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.String(20), nullable=False)

    def __init__ (self, quantidade):
        self.quantidade = quantidade

    def to_dict(self):
        return {
            'id' : self.id,
            'quantidade' : self.quantidade
        }
from config import db

class MemoriaRam(db.Model):
    __tablename__ = 'memoria_ram'

    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False)

    def __init__ (self, quantidade):
        self.quantidade = quantidade

    def to_dict(self):
        return {
            'id': self.id,
            'quantidade': self.quantidade
        }
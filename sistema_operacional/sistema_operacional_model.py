from config import db

class SistemaOperacional(db.Model):
    __tablename__ = "sistemas_operacionais"

    id = db.Column(db.Integer, primary_key=True)
    versao = db.Column(db.String(50), nullable=False)

    def __init__(self, versao):
        self.versao = versao

    def to_dict(self):
        return {
            'id' : self.id,
            'versao' : self.versao
        }


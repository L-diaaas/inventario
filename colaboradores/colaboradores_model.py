from config import db

class Colaboradores(db.Model):
    __tablename__ = 'colaboradores'

    id = db.Column(db.Integrer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)

    def __init__(self,nome_completo,cargo):
        self.nome_completo = nome_completo
        self.cargo = cargo

    def to_dict(self):
        return {
            'id' : self.id,
            'nome_completo_completo': self.nome_completo,
            'cargo': self.cargo
        }
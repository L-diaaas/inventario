from config import db
from werkzeug.security import generate_password_hash, check_password_hash


class EquipeTI(db.Model):
    __tablename__ = 'equipe_ti'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='ti')
    ativo = db.Column(db.Boolean, nullable=False, default=True, index=True) 

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'ativo': self.ativo,
        }
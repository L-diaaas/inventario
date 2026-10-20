from datetime import datetime
from config import db

class AuditoriaLog(db.Model):
    __tablename__ = 'auditoria_logs'

    id = db.Column(db.Integer, primary_key=True)
    membro_id = db.Column(db.Integer, db.ForeignKey('equipe_ti.id'), nullable=True)
    acao = db.Column(db.String(20), nullable=False)
    entidade = db.Column(db.String(100), nullable=True)
    entidade_id = db.Column(db.Integer, nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    membro = db.relationship('EquipeTI')

    def to_dict(self):
        return {
            'id': self.id,
            'membro_id': self.membro_id,
            'membro': {
                'id': self.membro.id,
                'nome': self.membro.nome or self.membro.email,
                'email': self.membro.email
            } if self.membro else None,
            'acao': self.acao,
            'entidade': self.entidade,
            'entidade_id': self.entidade_id,
            'descricao': self.descricao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
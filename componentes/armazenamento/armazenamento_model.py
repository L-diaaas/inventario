from config import db

STATUS_ARMAZENAMENTO = ('em_uso', 'sucata', 'sobrando')

class Armazenamento(db.Model):
    __tablename__ = 'armazenamento'

    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.Enum(*STATUS_ARMAZENAMENTO, name='status_armazenamento'),
        nullable=False,
        default='em_uso'
    )

    maquina_id = db.Column(db.Integer, db.ForeignKey('maquinas.id'), nullable=True)
    maquina = db.relationship('Maquina', backref='armazenamentos')

    def __init__(self, quantidade, status='em_uso', maquina_id=None):
        self.quantidade = quantidade
        self.status = status
        self.maquina_id = maquina_id

    def to_dict(self):
        return {
            'id': self.id,
            'quantidade': self.quantidade,
            'status': self.status,
            'maquina_id': self.maquina_id,
            'maquina': {
                'id': self.maquina.id,
                'nome': self.maquina.nome,
                's_tag': self.maquina.s_tag
            } if self.maquina else None
        }

def validar_quantidade(quantidade):
    if not isinstance(quantidade, str) or not quantidade.strip():
        return None, ({'error': 'A quantidade de armazenamento é obrigatória.'}, 400)

    quantidade = quantidade.strip()
    if len(quantidade) < 2 or len(quantidade) > 20:
        return None, ({'error': 'A quantidade deve ter entre 2 e 20 caracteres.'}, 400)

    return quantidade, None
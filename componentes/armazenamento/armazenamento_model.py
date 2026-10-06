from config import db

class Armazenamento(db.Model):
    __tablename__ = 'armazenamento'

    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.Enum('em_uso', 'sucata', name='status_armazenamento'),
        nullable=False,
        default='em_uso'
    )

    def __init__(self, quantidade, status='em_uso'):
        self.quantidade = quantidade
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'quantidade': self.quantidade,
            'status': self.status
        }


def validar_quantidade(quantidade):
    if not isinstance(quantidade, str) or not quantidade.strip():
        return None, ({'error': 'A quantidade de armazenamento é obrigatória.'}, 400)

    quantidade = quantidade.strip()

    if len(quantidade) < 2:
        return None, ({'error': 'A quantidade deve ter no mínimo 2 caracteres.'}, 400)
    if len(quantidade) > 20:
        return None, ({'error': 'A quantidade deve ter no máximo 20 caracteres.'}, 400)

    return quantidade, None
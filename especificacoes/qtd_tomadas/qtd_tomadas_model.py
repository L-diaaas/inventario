from config import db

class QuantidadeTomadas(db.Model):
    __tablename__ = "quantidade_tomadas"

    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, quantidade):
        self.quantidade = quantidade

    def to_dict(self):
        return {
            'id': self.id,
            'quantidade': self.quantidade
        }

def validar_quantidade_tomadas(quantidade, id_atual=None):
    if quantidade is None or quantidade == '':
        return None, ({'error': 'A quantidade de tomadas é obrigatória.'}, 400)

    if isinstance(quantidade, bool):
        return None, ({'error': 'A quantidade de tomadas deve ser um número inteiro.'}, 400)

    try:
        quantidade = int(quantidade)
    except (ValueError, TypeError):
        return None, ({'error': 'A quantidade de tomadas deve ser um número inteiro.'}, 400)

    if quantidade < 1:
        return None, ({'error': 'A quantidade de tomadas deve ser no mínimo 1.'}, 400)
    if quantidade > 50:
        return None, ({'error': 'A quantidade de tomadas deve ser no máximo 50.'}, 400)

    query = QuantidadeTomadas.query.filter(QuantidadeTomadas.quantidade == quantidade)
    if id_atual:
        query = query.filter(QuantidadeTomadas.id != id_atual)
    if query.first():
        return None, ({'error': 'Essa quantidade de tomadas já está cadastrada.'}, 409)

    return quantidade, None
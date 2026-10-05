from config import db

class Marca(db.Model):
    __tablename__ = 'marcas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def __init__(self, nome):
        self.nome = nome

    def to_dict(self):
        return {
            'id' : self.id,
            'nome': self.nome
        }

def validar_nome(nome, id_atual=None):
    if not isinstance(nome, str) or not nome.strip():
        return None, ({'error': 'O nome da marca é obrigatório.'}, 400)

    nome = nome.strip()

    if len(nome) < 2:
        return None, ({'error': 'O nome deve ter pelo menos 2 caracteres.'}, 400)
    if len(nome) > 100:
        return None, ({'error': 'O nome deve ter no máximo 100 caracteres.'}, 400)

    query = Marca.query.filter(db.func.lower(Marca.nome) == nome.lower())
    if id_atual:
        query = query.filter(Marca.id != id_atual)
    if query.first():
        return None, ({'error': 'Já existe uma marca com esse nome.'}, 409)

    return nome, None
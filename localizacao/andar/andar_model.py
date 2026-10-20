from config import db

class Andar(db.Model):
    __tablename__ = 'andares'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

    andar = db.relationship('Mesa', backref='andar')

    def __init__(self, nome):
        self.nome = nome

    def to_dict(self):
        return {
            'id' : self.id,
            'nome' : self.nome
        }

def validar_nome(nome, id_atual=None):
    if not isinstance(nome, str) or not nome.strip():
        return None, ({'error': 'O nome do andar é obrigatório.'}, 400)

    nome = nome.strip()

    if len(nome) < 2:
        return None, ({'error': 'O nome do andar deve ter pelo menos 2 caracteres.'}, 400)
    if len(nome) > 50:
        return None, ({'error': 'O nome do andar deve ter no máximo 50 caracteres.'}, 400)

    query = Andar.query.filter(db.func.lower(Andar.nome) == nome.lower())
    if id_atual:
        query = query.filter(Andar.id != id_atual)
    if query.first():
        return None, ({'error': 'Já existe um andar com esse nome.'}, 409)

    return nome, None
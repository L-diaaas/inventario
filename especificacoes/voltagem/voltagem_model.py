from config import db

class Voltagem(db.Model):
    __tablename__ = "voltagem"

    id = db.Column(db.Integer, primary_key=True)
    voltagem = db.Column(db.String(50), nullable=False)

    def __init__(self, voltagem):
        self.voltagem = voltagem

    def to_dict(self):
        return {
            'id' : self.id,
            'voltagem' : self.voltagem
        }

def validar_voltagem(voltagem, id_atual=None):
    if not isinstance(voltagem, str) or not voltagem.strip():
        return None, ({'error': 'O número da voltagem é obrigatório.'}, 400)

    voltagem = voltagem.strip()
    if len(voltagem) < 2:
        return None, ({'error': 'A voltagem deve ter no mínimo 2 caracteres.'}, 400)
    if len(voltagem) > 50:
        return None, ({'error': 'A voltagem deve ter no máximo 50 caracteres.'}, 400)

    query = Voltagem.query.filter(db.func.lower(Voltagem.voltagem) == voltagem.lower())
    if id_atual:
        query = query.filter(Voltagem.id != id_atual)
    if query.first():
        return None, ({'error': 'Essa voltagem já está cadastrada.'}, 409)

    return voltagem, None
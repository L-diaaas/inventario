from config import db

class TipoTomada(db.Model):
    __tablename__ = "tipos_tomadas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(255), nullable=True)

    nobreak = db.relationship('Nobreak', backref='tipos_tomada')

    def __init__(self, nome, foto=None):
        self.nome = nome
        self.foto = foto

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'foto': self.foto,
            'foto_url': f'/tipos-tomadas/{self.id}/foto' if self.foto else None
        }

def validar_tipo_tomada(nome, id_atual=None):
    if not isinstance(nome, str) or not nome.strip():
        return None, ({'error': 'O nome do tipo de tomada é obrigatório.'}, 400)

    nome = nome.strip()
    if len(nome) < 2:
        return None, ({'error': 'O nome deve ter no mínimo 2 caracteres.'}, 400)
    if len(nome) > 100:
        return None, ({'error': 'O nome deve ter no máximo 100 caracteres.'}, 400)

    query = TipoTomada.query.filter(db.func.lower(TipoTomada.nome) == nome.lower())
    if id_atual:
        query = query.filter(TipoTomada.id != id_atual)
    if query.first():
        return None, ({'error': 'Esse tipo de tomada já está cadastrado.'}, 409)

    return nome, None
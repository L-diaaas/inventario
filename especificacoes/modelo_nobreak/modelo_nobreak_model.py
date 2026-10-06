from config import db

class ModeloNobreak(db.Model):
    __tablename__ = "modelos_nobreaks"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)

    marca_id = db.Column(db.Integer, db.ForeignKey('marcas.id'), nullable=False)

    def __init__(self, nome, marca_id):
        self.nome = nome
        self.marca_id = marca_id

    def to_dict(self):
        return{
            'id': self.id,
            'nome': self.nome,
            'marca_id': {
                'id': self.marca.id,
                'nome': self.marca.nome
            } if self.marca else None
        }

def validar_nome(nome, id_atual=None):
    if not isinstance(nome,str) or not nome.strip():
        return None, ({'error': 'O nome do modelo do Nobreak é obrigatório.'}, 400)

    nome = nome.strip()

    if len(nome) < 2:
        return None, ({'error': 'A identificação do modelo do Nobreak deve ter no mínimo 2 caracteres.'}, 400)
    if len(nome) > 150:
        return None, ({'error': 'A identificação do modelo do Nobreak deve ter no máximo 150 caracteres'}, 400)

    query = ModeloNobreak.query.filter(db.func.lower(ModeloNobreak.nome) == nome.lower())
    if id_atual:
        query = query.filter(ModeloNobreak.id != id_atual)
    if query.first():
        return None, ({'error': 'Esse modelo de Nobreak já existe.'}, 409)

    return nome, None
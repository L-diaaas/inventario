from config import db

class Mesa(db.Model):
    __tablename__ = 'mesas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    status = db.Column( db.Enum('livre', 'ocupada', 'sucata', 'inativa', 'refeitorio', name='status_mesa'), nullable=False, default='livre')

    andar_id = db.Column(db.Integer, db.ForeignKey('andares.id'), nullable=False)

    def __init__(self, nome, andar_id, status):
        self.nome = nome
        self.andar_id = andar_id
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'status': self.status,
            'andar':{
                'id' : self.andar.id,
                'nome': self.andar.nome
            } if self.andar else None
        }

def validar_nome(nome, id_atual=None):
    if not isinstance(nome, str) or not nome.strip():
        return None, ({'error': 'A identificação da mesa é obrigatória.'}, 400)

    nome = nome.strip()

    if len(nome) < 2:
        return None, ({'error': 'A identificação da mesa deve ter no mínimo 2 caracteres.'}, 400)
    if len(nome) > 100:
        return None, ({'error': 'A identificação da mesa deve ter no máximo 100 caracteres.'}, 400)

    query = Mesa.query.filter(db.func.lower(Mesa.nome) == nome.lower())
    if id_atual:
        query = query.filter(Mesa.id != id_atual)
    if query.first():
        return None, ({'error': 'Essa identificação já existe.'}, 409)

    return nome, None

from config import db

class Monitor(db.Model):
    __tablename__ = 'monitores'

    id = db.Column(db.Integer, primary_key=True)
    polegadas = db.Column(db.Numeric(4, 1), nullable=False)
    status = db.Column(db.Enum('livre', 'ocupado', 'sucata', 'inativo', name='status_monitor'),nullable=False,default='livre')

    marca_id = db.Column(db.Integer, db.ForeignKey('marcas.id'), nullable=False)

    def __init__(self, polegadas, marca_id, status='livre'):
        self.polegadas = polegadas
        self.marca_id = marca_id
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'polegadas': float(self.polegadas),
            'status': self.status,
            'marca': {
                'id': self.marca.id,
                'nome': self.marca.nome
            } if self.marca else None
        }


def validar_polegadas(polegadas, marca_id,id_atual=None):
    if polegadas is None or isinstance(polegadas, bool):
        return None, ({'error': 'As polegadas do monitor são obrigatórias.'}, 400)

    try:
        if isinstance(polegadas, str):
            polegadas = polegadas.strip().replace(',', '.')
        valor = round(float(polegadas), 1)
    except (ValueError, TypeError):
        return None, ({'error': 'As polegadas devem ser um número válido.'}, 400)

    if valor < 10:
        return None, ({'error': 'As polegadas devem ser no mínimo 10.'}, 400)
    if valor > 100:
        return None, ({'error': 'As polegadas devem ser no máximo 100.'}, 400)

    query = Monitor.query.filter_by(polegadas=valor, marca_id=marca_id)
    if id_atual:
        query = query.filter(Monitor.id != id_atual)
    if query.first():
        return None, ({'error': 'Já existe um monitor dessa marca com essas polegadas.'}, 409)

    return valor, None
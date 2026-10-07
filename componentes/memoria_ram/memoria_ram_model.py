from config import db

class MemoriaRam(db.Model):
    __tablename__ = 'memoria_ram'

    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum('em_uso', 'sucata', name='status_memoria_ram'),
        nullable=False,
        default='em_uso'
    )

    tipo_memoria_ram_id = db.Column(db.Integer, db.ForeignKey('tipo_memoria_ram.id'), nullable=False)


    def __init__(self, quantidade, tipo_memoria_ram_id, status='em_uso'):
        self.quantidade = quantidade
        self.tipo_memoria_ram_id = tipo_memoria_ram_id
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'quantidade': self.quantidade,
            'status': self.status,
            'tipo_memoria_ram': {
                'id': self.tipo_memoria_ram.id,
                'tipo': self.tipo_memoria_ram.tipo
            } if self.tipo_memoria_ram else None
        }


def validar_quantidade(quantidade):
    if isinstance(quantidade, bool) or not isinstance(quantidade, int):
        return None, ({'error': 'A quantidade de memória RAM é obrigatória e deve ser um número inteiro (em GB).'}, 400)
    if quantidade < 1:
        return None, ({'error': 'A quantidade deve ser no mínimo 1 GB.'}, 400)
    if quantidade > 1024:
        return None, ({'error': 'A quantidade deve ser no máximo 1024 GB.'}, 400)

    return quantidade, None
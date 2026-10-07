from config import db

class TipoMemoria(db.Model):
    __tablename__ = 'tipo_memoria_ram'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)

    memoria_ram = db.relationship('MemoriaRam', backref='tipo_memoria_ram')

    def  __init__ (self, tipo):
        self.tipo = tipo

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo
        }

def validar_tipo(tipo, id_atual=None):
    if not isinstance(tipo, str) or not tipo.strip():
        return None, ({'error': 'O tipo de memória RAM é obrigatório.'}, 400)

    tipo = tipo.strip()

    if len(tipo) > 50:  # ajuste para o tamanho da sua coluna
        return None, ({'error': 'O tipo deve ter no máximo 50 caracteres.'}, 400)

    query = TipoMemoria.query.filter(db.func.lower(TipoMemoria.tipo) == tipo.lower())
    if id_atual:
        query = query.filter(TipoMemoria.id != id_atual)
    if query.first():
        return None, ({'error': 'Esse tipo de memória RAM já está cadastrado.'}, 409)

    return tipo, None
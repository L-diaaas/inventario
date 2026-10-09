from datetime import date, datetime
from config import db

STATUS_NOBREAK = ('em_uso', 'para_arrumar', 'sobrando')

class Nobreak(db.Model):
    __tablename__ = "nobreaks"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(
        db.Enum(*STATUS_NOBREAK, name='status_nobreak'),
        nullable=False,
        default='em_uso'
    )
    data_troca_bateria = db.Column(db.Date, nullable=True)
    foto = db.Column(db.String(255), nullable=True)

    modelo_nobreak_id = db.Column(db.Integer, db.ForeignKey('modelos_nobreaks.id'), nullable=False)
    voltagem_id = db.Column(db.Integer, db.ForeignKey('voltagem.id'), nullable=False)
    qtd_tomadas_id = db.Column(db.Integer, db.ForeignKey('quantidade_tomadas.id'), nullable=False)
    tipo_tomada_id = db.Column(db.Integer, db.ForeignKey('tipos_tomadas.id'), nullable=False)




    

    def __init__(self, codigo, modelo_nobreak_id, voltagem_id, qtd_tomadas_id,
                 tipo_tomada_id, status='em_uso', data_troca_bateria=None, foto=None):
        self.codigo = codigo
        self.modelo_nobreak_id = modelo_nobreak_id
        self.voltagem_id = voltagem_id
        self.qtd_tomadas_id = qtd_tomadas_id
        self.tipo_tomada_id = tipo_tomada_id
        self.status = status
        self.data_troca_bateria = data_troca_bateria
        self.foto = foto

    def to_dict(self):
        modelo = self.modelo_nobreak
        return {
            'id': self.id,
            'codigo': self.codigo,
            'status': self.status,
            'data_troca_bateria': self.data_troca_bateria.isoformat() if self.data_troca_bateria else None,
            'foto': self.foto,
            'foto_url': f'/nobreaks/{self.id}/foto' if self.foto else None,
            'modelo_nobreak': {
                'id': modelo.id,
                'nome': modelo.nome,
                'marca': {
                    'id': modelo.marca.id,
                    'nome': modelo.marca.nome
                } if modelo.marca else None
            } if modelo else None,
            'voltagem': self.voltagem.to_dict() if self.voltagem else None,
            'qtd_tomadas': self.qtd_tomadas.to_dict() if self.qtd_tomadas else None,
            'tipo_tomada': {
                'id': self.tipo_tomada.id,
                'nome': self.tipo_tomada.nome
            } if self.tipo_tomada else None
        }

def validar_codigo(codigo, id_atual=None):
    if not isinstance(codigo, str) or not codigo.strip():
        return None, ({'error': 'O código do nobreak é obrigatório.'}, 400)

    codigo = codigo.strip()
    if len(codigo) < 2:
        return None, ({'error': 'O código deve ter no mínimo 2 caracteres.'}, 400)
    if len(codigo) > 50:
        return None, ({'error': 'O código deve ter no máximo 50 caracteres.'}, 400)

    query = Nobreak.query.filter(db.func.lower(Nobreak.codigo) == codigo.lower())
    if id_atual:
        query = query.filter(Nobreak.id != id_atual)
    if query.first():
        return None, ({'error': 'Já existe um nobreak com esse código.'}, 409)

    return codigo, None

def validar_status(status):
    if status not in STATUS_NOBREAK:
        opcoes = ', '.join(STATUS_NOBREAK)
        return None, ({'error': f'Status inválido. Use um destes: {opcoes}.'}, 400)
    return status, None

def validar_data_troca_bateria(valor):
    """Aceita 'AAAA-MM-DD'. Vazio/None limpa o campo (a data é opcional)."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None, None

    if not isinstance(valor, str):
        return None, ({'error': 'A data da troca da bateria deve ser uma string no formato AAAA-MM-DD.'}, 400)

    try:
        data = datetime.strptime(valor.strip(), '%Y-%m-%d').date()
    except ValueError:
        return None, ({'error': 'Data da troca da bateria inválida. Use o formato AAAA-MM-DD.'}, 400)

    if data > date.today():
        return None, ({'error': 'A data da troca da bateria não pode estar no futuro.'}, 400)

    return data, None

    
from datetime import date, datetime
from config import db

STATUS_MAQUINA = ('em_uso', 'para_arrumar', 'sobrando')

class Maquina(db.Model):
    __tablename__ = 'maquinas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    s_tag = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(
        db.Enum(*STATUS_MAQUINA, name='status_maquina'),
        nullable=False,
        default='em_uso'
    )
    internet = db.Column(db.Boolean, nullable=False, default=True)
    data_compra = db.Column(db.Date, nullable=True)
    fim_garantia = db.Column(db.Date, nullable=True)
    data_manutencao = db.Column(db.Date, nullable=True)

    modelo_id = db.Column(db.Integer, db.ForeignKey('modelos_maquinas.id'), nullable=False)

    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaboradores.id'), nullable=True)
    nobreak_id = db.Column(db.Integer, db.ForeignKey('nobreaks.id'), nullable=True)
    sistema_operacional_id = db.Column(db.Integer, db.ForeignKey('sistemas_operacionais.id'), nullable=True)
    monitor_id = db.Column(db.Integer, db.ForeignKey('monitores.id'), nullable=True)
    monitor_secundario_id = db.Column(db.Integer, db.ForeignKey('monitores.id'), nullable=True)
    teclado_id = db.Column(db.Integer, db.ForeignKey('teclados.id'), nullable=True)
    mouse_id = db.Column(db.Integer, db.ForeignKey('mouses.id'), nullable=True)

    modelo = db.relationship('ModeloMaquina')
    colaborador = db.relationship('Colaboradores')
    nobreak = db.relationship('Nobreak')
    sistema_operacional = db.relationship('SistemaOperacional')
    monitor = db.relationship('Monitor', foreign_keys=[monitor_id])
    monitor_secundario = db.relationship('Monitor', foreign_keys=[monitor_secundario_id])
    teclado = db.relationship('Teclado')
    mouse = db.relationship('Mouse')

    def __init__(self, nome, s_tag, modelo_id, status='em_uso', internet=True,
                 data_compra=None, fim_garantia=None, data_manutencao=None,
                 colaborador_id=None, nobreak_id=None, sistema_operacional_id=None,
                 monitor_id=None, monitor_secundario_id=None, teclado_id=None, mouse_id=None):
        self.nome = nome
        self.s_tag = s_tag
        self.modelo_id = modelo_id
        self.status = status
        self.internet = internet
        self.data_compra = data_compra
        self.fim_garantia = fim_garantia
        self.data_manutencao = data_manutencao
        self.colaborador_id = colaborador_id
        self.nobreak_id = nobreak_id
        self.sistema_operacional_id = sistema_operacional_id
        self.monitor_id = monitor_id
        self.monitor_secundario_id = monitor_secundario_id
        self.teclado_id = teclado_id
        self.mouse_id = mouse_id

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            's_tag': self.s_tag,
            'status': self.status,
            'internet': self.internet,
            'data_compra': _iso(self.data_compra),
            'fim_garantia': _iso(self.fim_garantia),
            'em_garantia': bool(self.fim_garantia and self.fim_garantia >= date.today()),
            'data_manutencao': _iso(self.data_manutencao),
            'modelo': _modelo_dict(self.modelo),
            'colaborador': {
                'id': self.colaborador.id,
                'nome': self.colaborador.nome_completo,
                'cargo': self.colaborador.cargo
            } if self.colaborador else None,
            'nobreak': {
                'id': self.nobreak.id,
                'nome': self.nobreak.codigo,
                'status': self.nobreak.status
            } if self.nobreak else None,
            'sistema_operacional': {
                'id': self.sistema_operacional.id,
                'nome': self.sistema_operacional.versao
            } if self.sistema_operacional else None,
            'monitor': _monitor_dict(self.monitor),
            'monitor_secundario': _monitor_dict(self.monitor_secundario),
            'teclado': _teclado_mouse_dict(self.teclado),
            'mouse': _teclado_mouse_dict(self.mouse)
        }

def _iso(data):
    return data.isoformat() if data else None

def _modelo_dict(modelo):
    if not modelo:
        return None
    return {
        'id': modelo.id,
        'nome': modelo.nome,
        'marca': {'id': modelo.marca.id, 'nome': modelo.marca.nome} if modelo.marca else None
    }

def _monitor_dict(monitor):
    if not monitor:
        return None
    marca = monitor.marca.nome if monitor.marca else 'Sem marca'
    polegadas = f'{float(monitor.polegadas):g}'
    return {
        'id': monitor.id,
        'nome': f'{marca} {polegadas}"',
        'polegadas': float(monitor.polegadas),
        'marca': marca,
        'status': monitor.status
    }

def _teclado_mouse_dict(item):
    if not item:
        return None
    marca = item.marca.nome if item.marca else 'Sem marca'
    return {
        'id': item.id,
        'nome': f'{marca} ({item.tipo})',
        'tipo': item.tipo,
        'marca': marca,
        'status': item.status
    }

def _validar_texto_unico(valor, coluna, rotulo, minimo, maximo, id_atual):
    if not isinstance(valor, str) or not valor.strip():
        return None, ({'error': f'{rotulo} é obrigatório.'}, 400)

    valor = valor.strip()
    if len(valor) < minimo:
        return None, ({'error': f'{rotulo} deve ter no mínimo {minimo} caracteres.'}, 400)
    if len(valor) > maximo:
        return None, ({'error': f'{rotulo} deve ter no máximo {maximo} caracteres.'}, 400)

    query = Maquina.query.filter(db.func.lower(coluna) == valor.lower())
    if id_atual:
        query = query.filter(Maquina.id != id_atual)
    if query.first():
        return None, ({'error': f'Já existe uma máquina com esse valor em {rotulo.lower()}.'}, 409)

    return valor, None

def validar_nome_maquina(nome, id_atual=None):
    return _validar_texto_unico(nome, Maquina.nome, 'O nome da máquina', 2, 100, id_atual)

def validar_s_tag(s_tag, id_atual=None):
    return _validar_texto_unico(s_tag, Maquina.s_tag, 'A service tag', 2, 50, id_atual)

def validar_status(status):
    if status not in STATUS_MAQUINA:
        return None, ({'error': f'Status inválido. Use um destes: {", ".join(STATUS_MAQUINA)}.'}, 400)
    return status, None

def validar_internet(valor):
    """Aceita true/false, 1/0 ou 'sim'/'não'."""
    if isinstance(valor, bool):
        return valor, None
    if isinstance(valor, int) and valor in (0, 1):
        return bool(valor), None
    if isinstance(valor, str):
        texto = valor.strip().lower()
        if texto in ('sim', 's', 'true', '1'):
            return True, None
        if texto in ('nao', 'não', 'n', 'false', '0'):
            return False, None
    return None, ({'error': 'O campo internet deve ser sim ou não (true/false).'}, 400)

def validar_data(valor, rotulo):
    """Aceita 'AAAA-MM-DD'. Vazio/None limpa o campo (as datas são opcionais)."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None, None
    if not isinstance(valor, str):
        return None, ({'error': f'{rotulo} deve ser uma string no formato AAAA-MM-DD.'}, 400)
    try:
        return datetime.strptime(valor.strip(), '%Y-%m-%d').date(), None
    except ValueError:
        return None, ({'error': f'{rotulo} inválida. Use o formato AAAA-MM-DD.'}, 400)

def validar_coerencia_datas(data_compra, fim_garantia, data_manutencao):
    hoje = date.today()
    if data_compra and data_compra > hoje:
        return ({'error': 'A data de compra não pode estar no futuro.'}, 400)
    if data_manutencao and data_manutencao > hoje:
        return ({'error': 'A data da manutenção não pode estar no futuro.'}, 400)
    if data_compra and fim_garantia and fim_garantia < data_compra:
        return ({'error': 'O fim da garantia não pode ser anterior à data de compra.'}, 400)
    if data_compra and data_manutencao and data_manutencao < data_compra:
        return ({'error': 'A data da manutenção não pode ser anterior à data de compra.'}, 400)
    return None
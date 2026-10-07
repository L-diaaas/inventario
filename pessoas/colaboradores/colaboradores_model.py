from config import db

class Colaboradores(db.Model):
    __tablename__ = 'colaboradores'

    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)

    def __init__(self,nome_completo,cargo):
        self.nome_completo = nome_completo
        self.cargo = cargo

    def to_dict(self):
        return {
            'id' : self.id,
            'nome_completo': self.nome_completo,
            'cargo': self.cargo
        }

def validar_texto(valor, rotulo, minimo, maximo):
    if not isinstance(valor, str) or not valor.strip():
        return None, ({'error': f'{rotulo} é obrigatório.'}, 400)

    valor = ' '.join(valor.split())  # tira espaços das pontas e duplicados no meio

    if len(valor) < minimo:
        return None, ({'error': f'{rotulo} deve ter pelo menos {minimo} caracteres.'}, 400)
    if len(valor) > maximo:
        return None, ({'error': f'{rotulo} deve ter no máximo {maximo} caracteres.'}, 400)

    return valor, None

def validar_nome_completo(nome):
    return validar_texto(nome, 'O nome completo', 2, 100)

def validar_cargo(cargo):
    return validar_texto(cargo, 'O cargo', 2, 100)

def colaborador_duplicado(nome_completo, cargo, id_atual=None):
    query = Colaboradores.query.filter(
        db.func.lower(Colaboradores.nome_completo) == nome_completo.lower(),
        db.func.lower(Colaboradores.cargo) == cargo.lower(),
    )
    if id_atual:
        query = query.filter(Colaboradores.id != id_atual)
    return query.first() is not None
from config import db

class SistemaOperacional(db.Model):
    __tablename__ = "sistemas_operacionais"

    id = db.Column(db.Integer, primary_key=True)
    versao = db.Column(db.String(50), nullable=False)

    def __init__(self, versao):
        self.versao = versao

    def to_dict(self):
        return {
            'id' : self.id,
            'versao' : self.versao
        }

def validar_versao(versao, id_atual=None):
    if not isinstance(versao, str) or not versao.strip():
        return None, ({'error': 'O número da versão é obrigatório.'}, 400)

    versao = versao.strip()
    if len(versao) < 2:
        return None, ({'error': 'A versão deve ter no mínimo 2 caracteres.'}, 400)
    if len(versao) > 50:
        return None, ({'error': 'A versão deve ter no máximo 50 caracteres.'}, 400)

    query = SistemaOperacional.query.filter(db.func.lower(SistemaOperacional.versao) == versao.lower())
    if id_atual:
        query = query.filter(SistemaOperacional.id != id_atual)
    if query.first():
        return None, ({'error': 'Essa versão de Sistema Operacional já está cadastrada.'}, 409)

    return versao, None
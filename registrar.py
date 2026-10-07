import importlib
from pathlib import Path
from flask import Blueprint

BASE = Path(__file__).parent
PASTAS = ['catalogos', 'componentes', 'especificacoes',
          'localizacao', 'perifericos', 'pessoas']  # adicione 'equipamentos' quando criar

def registrar_blueprints(app):
    for pasta in PASTAS:
        for arquivo in sorted((BASE / pasta).rglob('*_route*.py')):
            modulo = '.'.join(arquivo.relative_to(BASE).with_suffix('').parts)
            mod = importlib.import_module(modulo)
            for obj in vars(mod).values():
                if isinstance(obj, Blueprint) and obj.name not in app.blueprints:
                    app.register_blueprint(obj)
from flask import Blueprint
from equipamentos.maquina.maquina_model import Maquina
from equipamentos.nobreak.nobreak_model import Nobreak
from componentes.memoria_ram.memoria_ram_model import MemoriaRam
from pessoas.auth.decorators import apenas_ti

dashboard_bp = Blueprint('dashboard_routes', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/', methods=['GET'])
@dashboard_bp.route('', methods=['GET'])
@apenas_ti
def obter_dashboard():
    total_maquinas = Maquina.query.count()
    maquinas_em_uso = Maquina.query.filter_by(status='em_uso').count()

    total_nobreaks = Nobreak.query.count()
    nobreaks_em_uso = Nobreak.query.filter_by(status='em_uso').count()

    rams_disponiveis = MemoriaRam.query.filter(
        MemoriaRam.maquina_id.is_(None),
        MemoriaRam.status != 'sucata'
    ).count()

    return {
        'maquinas': {
            'total': total_maquinas,
            'em_uso': maquinas_em_uso
        },
        'nobreaks': {
            'total': total_nobreaks,
            'em_uso': nobreaks_em_uso
        },
        'memorias_ram': {
            'disponiveis': rams_disponiveis
        }
    }, 200
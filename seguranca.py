from flask import request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func = get_remote_address,
    default_limits=["300 per minute"],
    storage_uri="memory://"
)

METODOS_AUDITADOS = {'POST', 'PUT', 'PATCH', 'DELETE'}

def detectar_tipo_imagem(arquivo):
    cabecalho = arquivo.stream.read(16)
    arquivo.stream.seek(0)
    if cabecalho.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if cabecalho.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    if cabecalho[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    if cabecalho[:4] == b'RIFF' and cabecalho[8:12] == b'WEBP':
        return 'webp'
    return None

def registrar_hooks(app):
    @app.after_request
    def headers_de_seguranca(resp):
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        resp.headers['X-Frame-Options'] = 'DENY'
        resp.headers['Referrer-Policy'] = 'no-referrer'
        resp.headers['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none'"
        if request.is_secure:
            resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        if resp.mimetype == 'application/json':
            resp.headers['Cache-Control'] = 'no-store'
        return resp

    @app.after_request
    def auditoria(resp):
        if request.method in METODOS_AUDITADOS:
            membro = g.get('membro')
            quem = f'ti_id={membro.id}' if membro else 'anonimo'
            app.logger.info(
                f'AUDIT {quem} {request.method} {request.path} -> {resp.status_code} ip={request.remote_addr}'
            )
        return resp
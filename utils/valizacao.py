from flask import request, jsonify

def obter_payload():
    dados = request.get_json(silent=True) or {}
    if not isinstance(dados,dict):
        return dados
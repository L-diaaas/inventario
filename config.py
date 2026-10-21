import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
load_dotenv()

from seguranca import limiter, registrar_hooks

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

origens = [o.strip() for o in os.environ.get('CORS_ORIGINS', '').split(',') if o.strip()]
CORS(
    app,
    origins= origens,
    methods=['GET','POST','PATCH','DELETE','OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    max_age=600
)

app.config['HOST'] = os.environ.get('HOST', '127.0.0.1')
app.config['PORT'] = int(os.environ.get('PORT', 5000))
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', '0') == '1'
db_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
if not app.config['JWT_SECRET_KEY'] or len(app.config['JWT_SECRET_KEY']) < 32:
    raise RuntimeError('JWT_SECRET_KEY ausente ou curta demais (mínimo 32 caracteres).')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
    minutes=int(os.environ.get('JWT_EXPIRA_MINUTOS', 60))
)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db = SQLAlchemy(app)
limiter.init_app(app)
registrar_hooks(app)
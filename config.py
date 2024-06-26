# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '.databases/app.db') #no se crea en el directorio
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://vicente:vblp2267@81.19.160.18/mc_mutual_latest'

SQLALCHEMY_TRACK_MODIFICATIONS = False


#IDS_ESCANEO = []  # Reemplaza con los IDs específicos que se proporcionarán

DOMINIOS_ESPECIFICOS = []

SECRET_KEY = 'your_secret_key_here'

URL_BASE = "https://mc-monitor.zonnox.net/"

URL_OFFLINE = ""

SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'

LOG_LEVEL = 'DEBUG' #os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FILE = '.logs/app.log' #os.environ.get('LOG_FILE') #no se crea en el directorio

# dias a mostrar
SCOPE_MONITOR = 1


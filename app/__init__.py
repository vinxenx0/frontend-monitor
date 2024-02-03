# app/__init__.py

import os
import logging
import traceback
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_talisman import Talisman
from flask_babel import Babel, _
#from flask_jwt_extended import JWTManager
#from flask_uploads import UploadSet, IMAGES, configure_uploads
#from werkzeug.utils import secure_filename
#from werkzeug.utils import secure_filename, FileStorage
from sqlalchemy.orm import aliased
from sqlalchemy import and_, func

from config import DOMINIOS_ESPECIFICOS #, IDS_ESCANEO

IDS_ESCANEO = []

app = Flask(__name__)

app.config.from_object('config')

app.config['DEBUG'] = True


# Configure logging
log_level = os.environ.get('LOG_LEVEL') or 'DEBUG'
# Configure logging in "paranoid" mode
log_format = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
logging.basicConfig(level=log_level, format=log_format)  # Setting level to 10 for DEBUG
# Get a logger for this module
logger = logging.getLogger(__name__)

# Set up a file handler with detailed format for logs
log_file = os.environ.get('LOG_FILE') or '.logs/app.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Importa las clases Resultado y Sumario
from app.models.database import Resultado, Sumario
from app.controllers import user_controller
from app.views import user_view
from app.models.user_model import User

# Configuración de Flask-Uploads
#photos = UploadSet('photos', IMAGES)
#app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/photos'  # Directorio para almacenar las fotos
#configure_uploads(app, photos)


# Add Talisman for security headers
csp = {
    'default-src': '\'self\'',
    'script-src': [
        '\'self\'',
        'https://code.jquery.com',
        'https://cdn.jsdelivr.net',
        'https://maxcdn.bootstrapcdn.com',
        '/static/js/scripts.js',  # Include the external script source
    ],
    'style-src': [
        '\'self\'',
        'https://stackpath.bootstrapcdn.com',
        'https://fonts.googleapis.com',
    ],
    'script-src-elem': [
        '\'self\'',
        'https://code.jquery.com',
        'https://cdn.jsdelivr.net',
        'https://maxcdn.bootstrapcdn.com',
        '/static/js/scripts.js',
    ],
    'style-src-elem': [
        '\'self\'',
        'https://stackpath.bootstrapcdn.com',
        'https://fonts.googleapis.com',
        '/static/css/styles.css',
    ],
    # Add other directives as needed
}

Talisman(app, content_security_policy=None)



# Add Babel for i18n support
babel = Babel(app)
# Configure Babel
babel.init_app(app, default_locale='es')

def obtener_ultimos_ids_escaneo():
    # Subconsulta para obtener el máximo id para cada dominio
    subconsulta = (
        db.session.query(
            Sumario.dominio,
            func.max(Sumario.id).label('max_id')
        )
        .filter(Sumario.dominio.in_(DOMINIOS_ESPECIFICOS))
        .group_by(Sumario.dominio)
        .subquery()
    )

    # Consulta principal para obtener el último id_escaneo para cada dominio
    ultimos_ids = (
        db.session.query(Sumario.id_escaneo)
        .join(subconsulta, and_(Sumario.id == subconsulta.c.max_id))
        .order_by(subconsulta.c.max_id.desc())
        .limit(7)
        .all()
    )

    # Almacena los resultados en la lista global
    global IDS_ESCANEO
    IDS_ESCANEO = [id_escaneo for id_escaneo, in ultimos_ids]
    
    print(IDS_ESCANEO)

    return IDS_ESCANEO




# Add JWTManager for token-based authentication
#jwt = JWTManager(app)


with app.app_context():
 
    db.create_all()
    
    # Obtiene los últimos IDs de escaneo y actualiza IDS_ESCANEO
    obtener_ultimos_ids_escaneo()


    if not User.query.first():
       
        # Create default users with hashed passwords and roles
        default_user = User(username='user', email='user@user.com', password=bcrypt.generate_password_hash('user').decode('utf-8'), role='user')
        default_admin = User(username='admin', email='admin@admin.com', password=bcrypt.generate_password_hash('admin').decode('utf-8'), role='superadmin')

        # Add default users to the database
        db.session.add(default_user)
        db.session.add(default_admin)
        db.session.commit()
        
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import SECRET_KEY for CSRF protection
from config import SECRET_KEY
app.config['SECRET_KEY'] = SECRET_KEY


# Error handling for common HTTP error codes
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    db.session.rollback()
    print("Excepción detectada:", str(e))
    traceback.print_exc()
    return render_template('errors/500.html'), 500

@app.before_request
def log_request_info():
    app.logger.debug('URL solicitada: %s', request.url)
    app.logger.debug('Argumentos de la URL: %s', request.view_args)


# Include the admin controller
from app.controllers import admin_controllers

# Function to check if the current user is an admin
def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'
app.jinja_env.globals.update(is_admin=is_admin)

# Add Bootstrap pagination script
app.jinja_env.globals.update(enumerate=enumerate)

from app.controllers import services_controller  # Add this line to import the new controller
from app.controllers import tools_controller  # Add this line to import the new controller


# import pdfkit

# pdfkit_config = pdfkit.configuration(wkhtmltopdf='/path/to/wkhtmltopdf')
# pdfkit.from_url('http://google.com', 'out.pdf', configuration=pdfkit_config)

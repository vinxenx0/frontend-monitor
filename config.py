# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '.databases/app.db') #no se crea en el directorio
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:dldlt741@81.19.160.10/mc_mutua'

SQLALCHEMY_TRACK_MODIFICATIONS = False


#IDS_ESCANEO = ['4332f81c1ebe5cbb4c026a903972b37bafd2c83f4639e59ee28473bc83e7b1e6',
#'fca77e48066dd1f625b7446c6a80d30ec0a0d2b5b982340b62780784bc60b2fd',  
    #'53725a9b49b2462468da642515d65b0e33930b0d9430d5817993686f1a7fddd1',
               #'6fadbf57e9a716477d517fee28aa26e00d0cd9a60435246931c14741fd885cb1',
#    '770a2c889b8ca913f024381f3ab3e1478aeb69d9c04e65b3eb50d652e30473b0',
#    '705a86070a66ff69489edababe6bda3e0e8cbc79ddafc6165a4933d2766cf25c',
#    '8ee2d9d04988dfb74813ca3d450e2d0d720f4ed1a3ddbd8d1a052c940599bf62',
#    'f3dbdbb3fdea6376a9ab796c42adf1f9fc2b45f2eeddcbbaf29e3d82618a34f8',
#'4dee580ebee58a23faa2bffb617ea25d391029ffdd1da4024605268e115e6e85',
#'d14d4fbb84f2633e3dba48730e86884e027e2e55aec368f10c5f025db2d8a245',
#'d8876252d72462e4de9333d0d5a1884a21f9e0be63bf88f992950646cdb0ed33'
#'53725a9b49b2462468da642515d65b0e33930b0d9430d5817993686f1a7fddd1',
#'6fadbf57e9a716477d517fee28aa26e00d0cd9a60435246931c14741fd885cb1',
#'d8876252d72462e4de9333d0d5a1884a21f9e0be63bf88f992950646cdb0ed33'
#'86f538982f1320806c24075bb37691f16eb473d49220c1c987f12d0270d9973d',
#'2489a76d7bbed3a1dd36e8601d37065c2ca75ed6978ddcb2d27cb83e3d2b9a07'
#'e74bf0f09948506b038831aebabd04025993bf5d17ad7fe0e6de539f3ccdb193',
#'0f8e2195fc98d44af1db7655cccbf3eabe35adde8c9cf383e95d91540b2688a0',
#'d8876252d72462e4de9333d0d5a1884a21f9e0be63bf88f992950646cdb0ed33'
#           ]  # Reemplaza con los IDs específicos que se proporcionarán

DOMINIOS_ESPECIFICOS = ["www.mc-mutual.com","mejoratuabsentismo.mc-mutual.com","prevencion.mc-mutual.com"]

SECRET_KEY = 'your_secret_key_here'

SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'

LOG_LEVEL = 'DEBUG' #os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FILE = '.logs/app.log' #os.environ.get('LOG_FILE') #no se crea en el directorio

# dias a mostrar
SCOPE_MONITOR = 1


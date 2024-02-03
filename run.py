# run.py

from app import app

if __name__ == '__main__':

   app.secret_key = 'tu_clave_secreta'  # Cambia esto a una clave secreta fuerte
   app.run(debug=True)
   # app.run(ssl_context='adhoc')
   #app.run(ssl_context=('.ssl/cert.pem', '.ssl/privkey.pem'), debug=True)

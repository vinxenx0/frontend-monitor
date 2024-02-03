from app import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), default='user')  # Default role is 'user'
    # New field for language preference
    language = db.Column(db.String(5), default='en')  # Add this line for language preference
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    departamento = db.Column(db.String(50))  # Puedes ajustar el tipo de datos según tus necesidades
    recibir_correos = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(255), default='default.jpg')  # Nombre del archivo del avatar

    
    def __repr__(self):
        return f'<User {self.username}>'
    
    
    def get_id(self):
        return str(self.id)
    
    def is_super_admin(self):
        return 'super_admin' in self.roles

# app/models/user.py

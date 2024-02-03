# app/views/user_view.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class UserProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin'), ('superadmin', 'Super Admin')], validators=[DataRequired()])
    language = SelectField('Language', choices=[('en', 'English'), ('es', 'Spanish')], validators=[DataRequired()])
    departamento = StringField('Departamento', validators=[Length(max=50)])  # Add this line for the "Departamento" field
    recibir_correos = BooleanField('Recibir Correos')  # Add this line for the "Recibir Correos" field
    submit = SubmitField('Update')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

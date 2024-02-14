# app/controllers/user_controller.py

import logging
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from app.models.user_model import User
from app.views.user_view import UserProfileForm, LoginForm
from sqlalchemy.exc import IntegrityError
from flask_babel import g, _
from flask import render_template, send_file
import tempfile
from weasyprint import HTML
from datetime import datetime
from app.views.user_view import ChangePasswordForm
#from email_validator import EmailNotValidError
#from flask_uploads import secure_filename
from werkzeug.utils import secure_filename

# Get a logger for this module
logger = logging.getLogger(__name__)


@app.route('/generate_pdf')
@login_required
def generate_pdf():
    # Obtén el nombre del template actual
    template_name = request.endpoint.split('.')[-1]

    # Get the current URL
    current_url = request.url_root + request.path

    # Render the HTML content with the specified template
    #html = render_template(f'{template_name}.html')
    html = render_template(f'tools/usa/enlaces_rotos.html')

    # Create a name for the PDF based on the template's name and timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    pdf_filename = f'{template_name}_{timestamp}.pdf'

    # Create a temporary file to store the PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        # Generate PDF using WeasyPrint
        HTML(string=html, base_url=current_url).write_pdf(temp_pdf.name)

    # Send the PDF as an attachment with the generated filename
    return send_file(temp_pdf.name,
                     as_attachment=True,
                     download_name=pdf_filename)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        #return redirect(url_for('informe_resumen'))
        return redirect(url_for('user_profile', user_id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            login_user(user, remember=form.remember.data)
            if user.role not in ['admin', 'superadmin']:
                #return redirect(url_for('admin'))
                return redirect(url_for('informe_resumen'))
            next_page = request.args.get('next')
            flash('Acceso correcto!', 'success')
            logger.info(f"Usuario {user.username} se ha identificado.")
            #return redirect(next_page) if next_page else redirect(url_for('user_profile', user_id=user.id))
            return redirect(url_for('user_profile', user_id=current_user.id))
        else:
            flash('Acceso fallido, comprueba email y contraseña.', 'danger')
            logger.error("Invalid login attempt.")
    return render_template('user/login.html', form=form)


@app.route('/admin')
@login_required
def admin():
    if current_user.role not in ['admin', 'superadmin']:
        flash(_('No tienes permisos para acceder a esta pagina..'), 'danger')
        return redirect(url_for('index'))

    # Your admin-specific logic here
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Adjust the number of users per page as needed
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/admin.html', users=users)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('user/logout.html')


@app.route('/')
@login_required
def index():
    # Redirige a la ruta de informe_resumen
    return redirect(url_for('informe_resumen'))


@app.route('/usuarios')
@login_required
def usuarios():
    #if current_user.role not in ['admin', 'superadmin']:
    #    flash('Permission Denied. You do not have access to this page.', 'danger')
    #    return redirect(url_for('home'))

    page = request.args.get('page', 1, type=int)
    per_page = 9  # Adjust the number of users per page as needed
    order_by = request.args.get('order_by',
                                'created_at')  # Default order by created_at
    users = User.query.order_by(db.desc(getattr(User, order_by))).all()
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/list.html', users=users, order_by=order_by)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Implement password change logic
        flash('Contraseña cambiada correctamente', 'success')
        return redirect(url_for('user_profile', user_id=current_user.id))

    return render_template('user/change_password.html', form=form)


@app.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_authenticated and (current_user == user
                                          or current_user.role == 'admin' or
                                          current_user.role == 'superadmin'):
        return render_template('user/profile.html', user=user)
    else:
        flash('Permiso denegado. Solo puedes ver tu propio perfil.', 'danger')
        return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role not in ['admin', 'superadmin']:
        flash('Solo administradores pueden añadir usuarios.', 'danger')
        return redirect(url_for('index'))

    form = UserProfileForm()
    try:
        #if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        new_user = User(username=form.username.data,
                        email=form.email.data,
                        password=hashed_password,
                        role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario nuevo añadido correctamente!', 'success')
        logger.debug(f"User {new_user.username} created.")
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error al añadir usuario: {e}', 'danger')
        logger.error(f"Error adding user: {e}")

    return render_template('user/add.html', form=form)


#@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
#@login_required
#def edit_user(user_id):
#    user = User.query.get_or_404(user_id)
#    form = UserProfileForm(obj=user)  # Pre-populate the form with the existing user data
#    if form.validate_on_submit():
#        form.populate_obj(user)  # Update the user object with the form data
#        user.updated_at = db.func.current_timestamp()
#        db.session.commit()
#        flash('User updated successfully!', 'success')
#        return redirect(url_for('admin'))
#    return render_template('user/edit.html', form=form, user=user)


@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = UserProfileForm(obj=user)

    if form.validate_on_submit():
        # Verifica la unicidad del nuevo nombre de usuario
        new_username = form.username.data
        if new_username != user.username and User.query.filter_by(
                username=new_username).first():
            flash('Ese nombre ya existe, elige otro.', 'danger')
            return render_template('user/edit.html', form=form, user=user)

        # Manejar carga de avatar
        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            avatar_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],
                                       filename)
            form.avatar.data.save(avatar_path)
            user.avatar = filename

        # Actualiza los campos del usuario con los datos del formulario
        form.populate_obj(user)
        user.updated_at = db.func.current_timestamp()

        try:
            db.session.commit()
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('admin'))
        except IntegrityError as e:
            db.session.rollback()
            flash('Ha ocurrido un error, inténtalo de nuevo.', 'danger')
            app.logger.error(f"IntegrityError during user update: {e}")

    return render_template('user/profile.html', form=form, user=user)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserProfileForm(obj=user)

    if form.validate_on_submit():
        # Verifica la unicidad del nuevo nombre de usuario
        new_username = form.username.data
        if new_username != user.username and User.query.filter_by(
                username=new_username).first():
            flash('Ese nombre ya existe, elige otro.', 'danger')
            return render_template('user/edit.html', form=form, user=user)

        # Actualiza los campos del usuario con los datos del formulario
        form.populate_obj(user)
        user.updated_at = db.func.current_timestamp()

        try:
            db.session.commit()
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('admin'))
        except IntegrityError as e:
            db.session.rollback()
            flash('Ha ocurrido un error, inténtalo de nuevo.', 'danger')
            app.logger.error(f"IntegrityError during user update: {e}")

    return render_template('user/edit.html', form=form, user=user)


@app.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash('Usuario borrado correctamente', 'success')
        return redirect(url_for('admin'))
    return render_template('user/delete.html', user=user)


@app.route('/set_locale', methods=['POST'])
def set_locale():
    if current_user.is_authenticated:
        current_user.locale = request.form['language']
        db.session.commit()
    g.locale = request.form['language']
    return redirect(request.referrer)


# app/controllers/user_controller.py

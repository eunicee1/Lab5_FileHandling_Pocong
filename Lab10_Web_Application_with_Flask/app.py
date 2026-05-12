
from werkzeug.utils import secure_filename

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegisterForm, LoginForm
from models import db, User, Student

import os

app = Flask(__name__, instance_relative_config=True)

app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.route('/')
def home():
    return render_template('home.html', name="Eunice G. Pocong", section="BSECE-1A")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Print Form Validation Result
        print("Form submitted!")

        # Prevent Duplicate Email Registration
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(form.password.data)
        user = User(email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for('login'))
    else:
        # Print Form Validation Result
        print("Validation failed.")

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for('students'))
        else:
            flash("Invalid email or password.")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))

@app.route('/students')
@login_required
def students():
    students = Student.query.order_by(Student.full_name).all()
    return render_template('students.html', students=students)

@app.route('/add-student', methods=['POST'])
@login_required
def add_student():
    if current_user.role != 'admin':
        flash("You do not have permission to add students.")
        return redirect(url_for('students'))

    name = request.form['name']
    email = request.form['email']
    student = Student(full_name=name, email=email)
    db.session.add(student)
    db.session.commit()
    return redirect(url_for('students'))


@app.route('/delete-student/<int:id>')
@login_required
def delete_student(id):
    if current_user.role != 'admin':
        flash("You do not have permission to delete students.")
        return redirect(url_for('students'))

    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))


# Add 404 Error Handler to app.py
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        display_name = request.form['display_name']
        file = request.files['profile_picture']

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.image_filename = filename

        current_user.display_name = display_name
        db.session.commit()
        flash("Profile updated successfully.")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user)


if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()

        try:
            db.session.execute(db.text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'viewer'"))
            db.session.commit()
        except Exception:
            db.session.rollback()

        try:
            db.session.execute(db.text("ALTER TABLE users ADD COLUMN display_name VARCHAR(150)"))
            db.session.commit()
        except Exception:
            db.session.rollback()

        try:
            db.session.execute(db.text("ALTER TABLE users ADD COLUMN image_filename VARCHAR(150)"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    app.run(debug=True)

    app.run(debug=True)

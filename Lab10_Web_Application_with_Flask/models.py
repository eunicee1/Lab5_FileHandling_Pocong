from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # optional but good practice
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='viewer')
    display_name = db.Column(db.String(150))
    image_filename = db.Column(db.String(150))

    def __repr__(self):
        return f'<User {self.email}>'

class Student(db.Model):
    __tablename__ = 'students'  # optional but good practice
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

    def __repr__(self):
        return f'<Student {self.full_name}>'

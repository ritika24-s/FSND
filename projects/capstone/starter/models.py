from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime, time as time_
import os
from flask_wtf import Form
# from forms import *

#database_path = os.environ['DATABASE_URL']
database_path = postgres://postgres:password123@localhost:5432/capstone

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Movie

'''
class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    release_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def __repr__(self):
        return f'<Movie {self.id} {self.title}>'
    
    def insert(self):
        db.session.add(self)
        db.commit()

    def update(self):
        db.commit()

    def delete(self):
        db.session.delete()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
            }
  
    
'''
Actor

'''
class Actor(db.Model):
    __tablename__ = 'actors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Actor {self.id} {self.name}>'

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.commit()

    def update(self):
        db.commit()

    def delete(self):
        db.session.delete()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
            }
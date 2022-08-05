import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_path = 'postgres://rmirvxxujnyole:dc40049f8a3219969496371a3260ffdeec50a809cd46f38271082f8b102714eb@ec2-44-197-128-108.compute-1.amazonaws.com:5432/d3jhhfs07qm45t'

# 'postgres://csllgrnr:CSeILnYSip_PiQynNx7KsDewRsYBZ0qg@kandula.db.elephantsql.com/csllgrnr'

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

"""
Person

"""
class Person(db.Model):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    f_name= Column(String)
    l_name = Column(String)
    age = Column(Integer)
    image = Column(String)

    def __init__(self, f_name, l_name, age):
        self.f_name = f_name
        self.l_name = l_name
        self.age = age

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'first name': self.f_name,
            'last name': self.l_name,
            'age': self.age,
            }

"""
Category

"""
class Image(db.Model):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    link = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'image link': self.link
            }

import os
import datetime
import base64

import sqlalchemy
from sqlalchemy.dialects.mysql import MEDIUMBLOB, MEDIUMTEXT
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

from main import app

# Environment variables are defined in app.yaml.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Profile(db.Model):

    __tablename__ = 'profile'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(46))
    password = db.Column(db.String(46))
    phone = db.Column(db.String(46))
    name = db.Column(db.String(46))
    breed = db.Column(db.String(46))
    sex = db.Column(db.String(46))
    age = db.Column(db.String(46))
    location = db.Column(db.String(46))
    photo = db.relationship("Photo", uselist=False, cascade="all,delete", back_populates="profile")

    def __init__(self, email, password, fields: dict):
        self.email = email
        self.password = password

        self.phone = fields.get('phone', '')
        self.name = fields.get('name', '')
        self.breed = fields.get('breed', '')
        self.sex = fields.get('sex', '')
        self.age = fields.get('age', '')
        self.location = fields.get('location', '')
        pass

    @classmethod
    def create(cls, fields: dict):

        email = fields.get('email', '')
        password = fields.get('password', '')

        if not email or not password:
            return None, { 'status': 400, 'message': 'invalid credentials' }

        if cls.find_by_email(email) is not None:
            return None, { 'status': 409, 'message': 'profile with this email already exists' }

        p = Profile(email, password, fields)
        p.photo = Photo()

        db.session.add(p)
        db.session.commit()

        return p, None

    @classmethod
    def find_by_id(cls, id):

        profile = db.session.query(cls)\
            .filter_by(id=id)\
            .one_or_none()

        return profile

    @classmethod
    def find_by_email(cls, email):

        profile = db.session.query(cls)\
            .filter_by(email=email)\
            .one_or_none()

        return profile

    @classmethod
    def set_photo(cls, id, image_data, image_type):

        profile = db.session.query(cls)\
            .filter_by(id=id)\
            .one_or_none()

        if profile is None:
            return { 'status': 409, 'message': 'profile not found' }

        profile.photo.set_base64(image_data, image_type)

        db.session.commit()

        return None

    def get_fields(self):

        return {
            'name' : self.name if self.name else '',
            'breed' : self.breed if self.breed else '',
            'sex' : self.sex if self.sex else '',
            'age' : self.age if self.age else '',
            'location' : self.location if self.location else ''
            }

    def update_fields(self, fields):

        allowed_fields = ['name', 'breed', 'sex', 'age', 'location']

        for k,v in fields.items():
            if k in allowed_fields and isinstance(v,str):
                setattr(self, k, v);

        db.session.commit()
        pass


class Photo(db.Model):

    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    profile = relationship("Profile", back_populates="photo")

    data = db.Column(MEDIUMBLOB)
    type = db.Column(db.String(46))

    def __init__(self):
        pass

    def set_base64(self, data, type):

        if not data:
            self.data = None
            self.type = None
        else:
            self.data = base64.b64decode(data)
            self.type = type

    def set_binary(self, data, type):
        self.data = data
        self.type = type

    def get_base64(self):
        if not self.data:
            return None, None
        return base64.b64encode(self.data), self.type

    def get_binary(self):
        return self.data, self.type

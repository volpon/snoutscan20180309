import base64
import sys
import os

is_heroku = 'DATABASE_URL' in os.environ.keys()
is_postgres = is_heroku

from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


if is_postgres:
    MEDIUMBLOB = db.LargeBinary
else:
    from sqlalchemy.dialects.mysql import MEDIUMBLOB

from main import app
from main.api.matcher import ImageFeatures

# Environment variables are defined in app.yaml.

if is_heroku:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Profile(db.Model):

    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(46))
    password = db.Column(db.String(46))
    isadmin = db.Column(db.Boolean)

    phone = db.Column(db.String(46))
    use_phone = db.Column(db.Boolean)
    use_msg = db.Column(db.Boolean)

    friends = db.relationship("Friend", cascade="all,delete", back_populates="profile")

    def __init__(self, email, password, fields: dict = {}):

        self.email = email
        self.password = password
        self.isadmin = False

        self.phone = fields.get('phone', '')
        self.use_phone = bool(fields.get('use_phone', False))
        self.use_msg = bool(fields.get('use_msg', False))
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

    def get_fields(self):

        return {
            'phone' : self.phone if self.phone else '',
            'use_phone' : self.use_phone if self.use_phone else False,
            'use_msg' : self.use_msg if self.use_msg else False,
            }

    def update_fields(self, fields):

        allowed_fields = {
            'phone':str, 
            'use_phone':bool, 
            'use_msg':bool, 
        }

        for k,v in fields.items():
            tp = allowed_fields.get(k)
            if tp and isinstance(v,tp):
                setattr(self, k, v);

        db.session.commit()
        pass

class Friend(db.Model):

    __tablename__ = 'friends'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
    profile = relationship("Profile", back_populates="friends")

    name = db.Column(db.String(46))
    breed = db.Column(db.String(46))
    sex = db.Column(db.String(46))
    age = db.Column(db.String(46))
    location = db.Column(db.String(46))
    status= db.Column(db.String(16))

    photo = db.relationship("Photo", uselist=False, cascade="all,delete", back_populates="friend")

    def __init__(self, profile, fields: dict):

        self.profile = profile

        self.name = fields.get('name', '')
        self.breed = fields.get('breed', '')
        self.sex = fields.get('sex', '')
        self.age = fields.get('age', '')
        self.location = fields.get('location', '')
        self.status = fields.get('status', '')

        self.photo = Photo()

        pass

    @classmethod
    def create(cls, profile, fields: dict):

        f = Friend(profile, fields)

        db.session.add(f)
        db.session.commit()

        return f, None

    @classmethod
    def find_by_id(cls, id):

        obj = db.session.query(cls)\
            .filter_by(id=id)\
            .one_or_none()

        return obj

    @classmethod
    def find_by_profile_id(cls, profile_id):

        obj = db.session.query(cls)\
            .filter_by(profile_id=profile_id)

        return obj


    def get_fields(self, with_id=False):
        
        fx = {
            'name' : self.name if self.name else '',
            'breed' : self.breed if self.breed else '',
            'sex' : self.sex if self.sex else '',
            'age' : self.age if self.age else '',
            'location' : self.location if self.location else '',
            'status' : self.status if self.status else '',
            }

        if with_id:
            fx.update({'friend_id': self.id})

        return fx

    def update_fields(self, fields):

        allowed_fields = {
            'name':str, 
            'breed':str, 
            'sex':str, 
            'age':str, 
            'location':str,
            'status':str
        }

        for k,v in fields.items():
            tp = allowed_fields.get(k)
            if tp and isinstance(v,tp):
                setattr(self, k, v);

        db.session.commit()
        pass


    def set_photo(self, image_data, image_type):

        self.photo.set_base64(image_data, image_type)
        
        db.session.commit()
        return None

class Photo(db.Model):

    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('friends.id'))
    friend = relationship("Friend", back_populates="photo")

    data = db.Column(MEDIUMBLOB)
    type = db.Column(db.String(46))

    #Don't store the keypoints in the databsae.  They're difficult to serialize and currently 
    #only used for visualization/debugging:    
    featureKeypoints=None
    featureDescriptors=None
    
    #Feature descriptors, in encoded format:
    featureDescriptorsEncoded = db.Column(MEDIUMBLOB)

    def __init__(self):
        pass 

    def set_base64(self, data, type):

        if isinstance(data, str):
            self.set_binary(base64.b64decode(data), type)
        else:
            self.data = None
            self.type = None
            self.featureDescriptors = None
            self.featureDescriptorsEncoded = None

    def set_binary(self, data, type):

        self.data = data
        self.type = type
        
        fs=ImageFeatures()

        (self.featureKeypoints, self.featureDescriptors) = fs.from_image(self.data)
        
        self.featureDescriptorsEncoded = fs.encode() 
     

    def get_base64(self):

        if not self.data:
            return None, None

        return str(base64.b64encode(self.data), "utf-8"), self.type

    def get_binary(self):
        '''
        Gets the image in binary form, and it's type.
        '''
        return self.data, self.type

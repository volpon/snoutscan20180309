
from flask import jsonify
from flask_jwt import JWT, jwt_required, current_identity

from main import app
from main.api.model import db, Profile

app.config['SECRET_KEY'] = 'snoutscan-secret'
app.config['JWT_AUTH_URL_RULE'] = '/api/auth'
app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
#app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=24*3600)   # 2do: change in future


#####################################################
## JWT implementation

class User(object):
    def __init__(self, profile):
        self.id = profile.id
        self.email = profile.email

def authenticate(email, password):

    print('authenticate: {}:{}'.format(email, password))

    profile = db.session.query(Profile)\
        .filter_by(email=email, password=password)\
        .one_or_none()

    if profile is None:
        return None

    return User(profile)

def identity(payload):

    print('identity: {}'.format(str(payload)))

    user_id = payload['identity']

    return {'profile_id': user_id}

jwt = JWT(app, authenticate, identity)

@jwt.auth_response_handler
def auth_response_handler(access_token, identity):
    return jsonify({'access_token': access_token.decode('utf-8'), 'profile' : identity.id})

@jwt.jwt_error_handler
def error_handler(e):
    return jsonify({'error': {'message': e.description}}), e.status_code

#@jwt.auth_response_handler
#def auth_response_handler():
#   return jsonify({'error': {'message': 'login fail'}}), 401

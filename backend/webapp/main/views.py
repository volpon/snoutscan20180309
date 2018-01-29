"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import request, render_template
from main import app
from main.api.model import Profile, Friend
from main.api.auth import jwt


def is_access_denied(profile_id):

    access_token = request.cookies.get("access_token", None)

    user_id = None

    if access_token:
        try:
            payload = jwt.jwt_decode_callback(access_token)
            user_id = payload['identity'] if payload else None
        except:
            user_id = None

    return not user_id or user_id != profile_id

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""


    profiles = Profile.query.all()

    ps = [ { 'id' : p.id, 'email': p.email } for p in profiles if not p.isadmin ]

    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        profiles=ps
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.',
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/login')
def login():
    return render_template(
        'login.html',
        title='Login',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/signup')
def signup():
    """Creates new Profile."""
    return render_template(
        'signup.html',
        title='Create Profile',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/profile/<int:profile_id>')
def profile(profile_id):

    if is_access_denied(profile_id):
        message = 'not authorized profile'
    else:
        message = 'authorized profile'

    profile = Profile.find_by_id(profile_id)

    if profile is None:
        return 'Not Found', 404

    return render_template(
        'profile.html',
        title='Profile',
        year=datetime.now().year,
        message=message,
        profile_id = profile_id,
        fields=profile.get_fields()
    )

@app.route('/friend/<int:friend_id>/photo')
def profile_photo(friend_id: int):

    friend = Friend.find_by_id(friend_id)

    if friend is None:
        return 'Not found', 404, {'Content-Type': 'text/plain; charset=utf-8'}

    data, type = friend.photo.get_binary()

    if not data or not type:
        return 'Not found', 404, {'Content-Type': 'text/plain; charset=utf-8'}

    return data, 200, { 'Content-Type': type }

@app.route('/match')
def match():

    return render_template(
        'match.html',
        title='Match Photo',
        year=datetime.now().year,
        message='upload photo for match check',
    )

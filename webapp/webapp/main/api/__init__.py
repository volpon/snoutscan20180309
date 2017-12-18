import os
from flask import Flask, request, jsonify
#from flask_jwt import jwt_required

from main import app
from main.api.auth import jwt_required, current_identity

from main.api.matcher import ImageFeatures, find_best_match

from main.api.model import db, Profile, Photo

import main.api.test


def decode_input():

    input = request.get_json()

    if input is None:
        # in case x-www-form-urlencoded
        input = dict([ (k,v[0]) for k,v in dict(request.form).items() ])

    return input

def is_access_denied(profile_id):
    return current_identity is None or current_identity['profile_id'] != profile_id

@app.route('/api/profile/signup', methods=["POST"])
def api_profile_signup():

    fields = decode_input()

    if fields is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    profile, error = Profile.create(fields)

    if profile is None:
        return jsonify({'error': error}), error['status']

    return jsonify({'profile_id': profile.id}), 201

@app.route('/api/profile/<int:profile_id>', methods=["DELETE"])
@jwt_required()
def api_profile_delete(profile_id: int):

    if is_access_denied(profile_id):
        return jsonify({'error': {'message': 'forbidden'}}), 403

    profile = Profile.find_by_id(profile_id)

    if profile is None:
        return jsonify({'error': {'message': 'Not Found'}}), 404

    db.session.delete(profile)
    db.session.commit()

    return '', 204

@app.route('/api/profile/<int:profile_id>', methods=["PUT"])
@jwt_required()
def api_profile_set(profile_id: int):

    if is_access_denied(profile_id):
        return jsonify({'error': {'message': 'forbidden'}}), 403

    profile = Profile.find_by_id(profile_id)

    if profile is None:
        return jsonify({'error': {'message': 'profile not found'}}), 404

    fields = decode_input()

    if fields is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    profile.update_fields(fields)

    return '', 204

@app.route('/api/profile/<int:profile_id>', methods=["GET"])
def api_profile_get(profile_id: int):

    profile = Profile.find_by_id(profile_id)

    if profile is None:
        return jsonify({'error': {'message': 'profile not found'}}), 404

    fields = profile.get_fields()

    return jsonify(fields), 200

@app.route('/api/profile/<int:profile_id>/photo', methods=["GET"])
def api_profile_get_photo(profile_id: int):

    profile = Profile.find_by_id(profile_id)

    if profile is None:
        return jsonify({'error': {'message': 'Profile not exists'}}), 404

    data, type = profile.photo.get_base64()
    if data is None:
        return jsonify({'error': {'message': 'Photo not uploaded'}}), 404

    return jsonify({'image' : {'data' : data, 'type' : type}}), 200

@app.route('/api/profile/<int:profile_id>/photo', methods=["PUT"])
@jwt_required()
def api_profile_set_photo(profile_id: int):

    if is_access_denied(profile_id):
        return jsonify({'error': {'message': 'forbidden'}}), 403

    data = request.get_json()

    if data is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    image = data.get('image', None)

    if image is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    image_data = image.get('data', None)
    image_type = image.get('type', None)

    error = Profile.set_photo(profile_id, image_data, image_type)

    #print("{}: {}".format(image_type, image_data))

    return '', 204

@app.route('/api/query_match', methods=["POST"])
def api_query_match():

    data = request.get_json()

    if data is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    image = data.get('image', None)

    if image is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    image_data = image.get('data', None)
    image_type = image.get('type', None)

    profile_id, per = find_best_match(image_data, image_type, profiles = Profile.query.all())

    if profile_id is None:
        return jsonify({'status': 'not found'}), 200

    return jsonify({'status': 'found', 'profile' : profile_id, 'percent' : per }), 200

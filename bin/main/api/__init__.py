from main.api.auth import jwt_required, current_identity
from main.api.model import db, Profile, Friend
from main.api.matcher import find_best_match
#from flask_jwt import jwt_required
from flask import request, jsonify
from main import app




def decode_input():

    input = request.get_json()

    if input is None:
        # in case x-www-form-urlencoded
        input = dict([ (k,v[0]) for k,v in dict(request.form).items() ])

    return input

def is_access_denied(profile_id):

    if current_identity is None:
        return True

    if current_identity['profile_id'] == profile_id:
        return False

    if current_identity['isadmin']:
        return False

    return True

###
### Profile
###

@app.route('/api/profile/signup', methods=["POST"])
def api_profile_signup():

    fields = decode_input()

    if fields is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    profile, error = Profile.create(fields)

    if profile is None:
        return jsonify({'error': error}), error['status']

    return jsonify({'profile_id': profile.id}), 201, {'location': '/api/profile/{}'.format(profile.id)}

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

    output = {'profile_id': profile_id }
    output.update(profile.get_fields())

    return jsonify(output), 200

###
### Friend
###

@app.route('/api/profile/<int:profile_id>/friends', methods=["GET"])
@jwt_required()
def api_profile_friends_get(profile_id: int):
    """
    @return list of friends for profile
    """

    if is_access_denied(profile_id):
        return jsonify({'error': {'message': 'forbidden'}}), 403

    friends = Friend.find_by_profile_id(profile_id)

    if friends is None:
        return jsonify({'error': {'message': 'not found'}}), 404

    out = [ f.get_fields(with_id=True) for f in friends ]

    return jsonify(out), 200

@app.route('/api/profile/<int:profile_id>/friends/new', methods=["POST"])
@jwt_required()
def api_friend_create(profile_id:int):

    if is_access_denied(profile_id):
        return jsonify({'error': {'message': 'forbidden'}}), 403

    profile = Profile.find_by_id(profile_id)

    if profile is None:
        print('profile not found')
        return jsonify({'error': {'message': 'profile not found'}}), 404

    fields = decode_input()

    if fields is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    friend, error = Friend.create(profile, fields)

    if friend is None:
        return jsonify({'error': error}), error['status']

    return jsonify({'friend_id': friend.id}), 201, {'location': '/api/friend/{}'.format(friend.id)}

@app.route('/api/friend/<int:friend_id>', methods=["GET"])
def api_friend_get(friend_id: int):

    friend = Friend.find_by_id(friend_id)

    if friend is None:
        return jsonify({'error': {'message': 'friend not found'}}), 404

    output = {'friend_id': friend_id }
    output.update(friend.get_fields())

    return jsonify(output), 200

@app.route('/api/friend/<int:friend_id>', methods=["PUT"])
@jwt_required()
def api_friend_put(friend_id: int):

    friend = Friend.find_by_id(friend_id)

    if friend is None:
        return jsonify({'error': {'message': 'friend not exists'}}), 404

    if is_access_denied(friend.profile_id):
        return jsonify({'error': {'message': 'forbidden'}}), 403

    fields = decode_input()

    if fields is None:
        return jsonify({'error': {'message': 'invalid input'}}), 400

    friend.update_fields(fields)

    return '', 204

@app.route('/api/friend/<int:friend_id>', methods=["DELETE"])
@jwt_required()
def api_friend_delete(friend_id: int):

    friend = Friend.find_by_id(friend_id)

    if friend is None:
        return jsonify({'error': {'message': 'friend not found'}}), 404

    if is_access_denied(friend.profile_id):
        return jsonify({'error': {'message': 'forbidden'}}), 403

    db.session.delete(friend)
    db.session.commit()

    return '', 204

###
### Photo
###

@app.route('/api/friend/<int:friend_id>/photo', methods=["GET"])
def api_friend_get_photo(friend_id: int):

    #print("accept: ", request.headers.getlist('accept'))
    #print("application/json: ", request.accept_mimetypes["application/json"])
    #print("image/*: ", request.accept_mimetypes["image/*"])

    friend = Friend.find_by_id(friend_id)

    if request.accept_mimetypes["application/json"] >= 1:

        if friend is None:
            return jsonify({'error': {'message': 'friend not exists'}}), 404

        image_data, type = friend.photo.get_base64()
        if image_data is None:
            return jsonify({'error': {'message': 'Photo not uploaded'}}), 404

        #print("GET: ", image_data)
        #print("GET: image_data size: ", len(image_data))

        return jsonify({'image' : {'data' : image_data, 'type' : type}}), 200

    else:

        if friend is None:
            return 'Not found', 404, {'Content-Type': 'text/plain; charset=utf-8'}

        data, type = friend.photo.get_binary()

        if not data or not type:
            return 'Not found', 404, {'Content-Type': 'text/plain; charset=utf-8'}

        return data, 200, { 'Content-Type': type }

@app.route('/api/friend/<int:friend_id>/photo', methods=["PUT"])
@jwt_required()
def api_friend_set_photo(friend_id: int):

    friend = Friend.find_by_id(friend_id)

    if friend is None:
        return jsonify({'error': {'message': 'friend not exists'}}), 404

    if is_access_denied(friend.profile_id):
        return jsonify({'error': {'message': 'forbidden'}}), 403

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({'error': {'message': 'invalid input'}}), 400

    image = data.get('image', None)

    if not isinstance(image, dict):
        return jsonify({'error': {'message': 'invalid input'}}), 400

    image_data = image.get('data', None)
    image_type = image.get('type', None)

    #print("PUT: ", image_data)
    #print("PUT: image_data size: ", len(image_data))
    
    #image_data = bytes(image_data, "utf-8")

    #print("PUT: ", image_data)

    error = friend.set_photo(image_data, image_type)

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

    #image_data = bytes(image_data, "utf-8")

    friend_id, per, best_index = find_best_match(image_data, image_type, friends = Friend.query.all())

    if friend_id is None:
        return jsonify({'status': 'not found'}), 200

    return jsonify({'status': 'found', 'friend' : friend_id, 'percent' : per }), 200

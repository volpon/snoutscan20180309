from main import app
from main.api.model import db
from main.api.auth import jwt_required

@app.route('/api/test')
@jwt_required()
def api_test():

    #m = MatchFragment()
    #r = m.compareTwoImages("name1", "./image1001.jpg", "./image1002.jpg")
    #r.saveImage("./result0001.jpg")

    return 'Test', 200, {'Content-Type': 'text/plain; charset=utf-8'}

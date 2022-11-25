from flask_httpauth import HTTPDigestAuth
from Model.models import Visitor
import json
from main import db,app

auth = HTTPDigestAuth()

users = {
    "john": "hello"
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/Visitors', methods=['GET'])
@auth.login_required
def get_visitors():
    list_visitors=Visitor.query.all()
    results = [obj.to_dict() for obj in list_visitors]
    return json.dumps(results)

if __name__=='__main__':
    app.run(host='myapp')
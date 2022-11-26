from flask_httpauth import HTTPDigestAuth
from Model.models import Visitor
import json
from flask import request
from main import db,app
import yaml
import os

with open(os.path.join(os.path.dirname(__file__), 'users.yml'), 'r') as f:
    try:
        users=yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(exc)

auth = HTTPDigestAuth()

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/Visitors', methods=['GET'])
@auth.login_required
def get_visitors():
    args=request.args
    user_id=args.get('user_id',type=int)
    page_id=args.get('page_id',type=int)

    if user_id==None and page_id==None:
        list_visitors=Visitor.query.all()
        results = [obj.to_dict() for obj in list_visitors]
        return json.dumps(results)
    elif user_id!=None and page_id==None:
        list_visitors=Visitor.get_by_user(user_id)
        results = [obj.to_dict() for obj in list_visitors]
        return json.dumps(results)
    else:
        list_visitors=Visitor.get_by_page(page_id)
        results = [obj.to_dict() for obj in list_visitors]
        return json.dumps(results)


@app.route('/Visitors/<int:id>', methods=['GET'])
@auth.login_required
def get_visitor_byid(id):
    visitor=Visitor.get_by_id(id)
    return json.dumps(visitor.to_dict())

if __name__=='__main__':
    app.run(host='myapp')
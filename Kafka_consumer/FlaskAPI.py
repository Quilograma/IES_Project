from flask_httpauth import HTTPDigestAuth
from Model.models import Visitor
import json
from flask import request
from main import db,app
import yaml
import os
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor

def to_supervised(timeseries,n_lags,n_output=1):
    
    N=len(timeseries)
    X=np.zeros((N-n_lags-n_output+1,n_lags))
    y=np.zeros((X.shape[0],n_output))
    
    for i in range(N-n_lags):
        aux=np.zeros(n_lags)
        for j in range(i,i+n_lags,1):
            aux[j-i]=timeseries[j]
        if i+n_lags+n_output<=N:
            X[i,:]=aux
            y[i,:]=timeseries[i+n_lags:i+n_lags+n_output]

    return X,y

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

@app.route('/train/<int:page_id>',methods=['GET'])
@auth.login_required
def train(page_id):
    print(request.form.values())
    list_visitors=Visitor.get_by_page(page_id)
    results = [obj.to_dict() for obj in list_visitors]
    data=pd.DataFrame.from_dict(results)
    data['accessed_at'] = pd.to_datetime(data['accessed_at'])
    df_counts=data.groupby([pd.Grouper(key='accessed_at', freq='H')]).count()
    df_counts.reset_index(inplace=True)
    X,y=to_supervised(df_counts['page_id'].values,n_lags=10,n_output=1)
    mlp=MLPRegressor(max_iter=10)
    mlp.fit(X,y)
    output=X[10].reshape(1,-1)
    
    return json.dumps(list(mlp.predict(output)))


if __name__=='__main__':
    app.run(host='myapp')
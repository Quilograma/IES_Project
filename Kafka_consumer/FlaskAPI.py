from flask_httpauth import HTTPDigestAuth
from Model.models import Visitor,Model
import json
from flask import request, Blueprint,send_from_directory,send_file
from main import db,app
import yaml
import sys
import os
import pandas as pd
import numpy as np
from flask_swagger_ui import get_swaggerui_blueprint
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
import pickle
from datetime import datetime


### swagger specific ###
SWAGGER_URL = '/docs'
API_URL = '/docs/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "FlaskAPI"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


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

@app.route('/Models/<int:pageid>',methods=['GET'])
@auth.login_required
def get_models(pageid):
    list_models=Model.get_by_pageid(pageid)
    results = [obj.to_dict() for obj in list_models]
    return json.dumps(results)

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

@app.route('/train1',methods=['POST'])
@auth.login_required
def train1():

    content = json.loads(request.data)
    page_id=int(content['page_id'])
    lags=int(content['lags'])
    forecastperiod=int(content['forecastperiod'])
    alpha=float(content['alpha'])
    del content['page_id']
    
    list_visitors=Visitor.get_by_page(page_id)
    results = [obj.to_dict() for obj in list_visitors]
    data=pd.DataFrame.from_dict(results)
    data['accessed_at'] = pd.to_datetime(data['accessed_at'])
    df_counts=data.groupby([pd.Grouper(key='accessed_at', freq='H')]).count()
    df_counts.reset_index(inplace=True)
    X,y=to_supervised(df_counts['page_id'].values,n_lags=lags,n_output=forecastperiod)
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1)
    training_start=datetime.now()
    mlpr=MLPRegressor(random_state=1, max_iter=500).fit(X_train, y_train)
    training_end=datetime.now()
    forecast=mlpr.predict(X_test)
    forecast[forecast<0]=0
    epsilon=np.abs(y_test.flatten()-forecast.flatten())
    q_hat=np.quantile(epsilon,1-alpha)
    model=Model(model_pickle=pickle.dumps(mlpr),TrainingStart=training_start,TrainingEnd=training_end,page_id=page_id,model_params=json.dumps(content),q_hat=q_hat,model_metrics=np.round(np.mean(epsilon),3))
    model.save()

    return 'Model sucessfully trained'

@app.route('/train',methods=['POST'])
@auth.login_required
def train():

    content = json.loads(request.data)
    page_id=int(content['page_id'])
    lags=int(content['lags'])
    forecastperiod=int(content['forecastperiod'])
    alpha=float(content['alpha'])
    del content['page_id']
    
    list_visitors=Visitor.get_by_page(page_id)
    results = [obj.to_dict() for obj in list_visitors]
    data=pd.DataFrame.from_dict(results)
    data['accessed_at'] = pd.to_datetime(data['accessed_at'])
    df_counts=data.groupby([pd.Grouper(key='accessed_at', freq='H')]).count()
    df_counts.reset_index(inplace=True)
    X,y=to_supervised(df_counts['page_id'].values,n_lags=lags,n_output=forecastperiod)
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1)
    training_start=datetime.now()
    mlpr=MLPRegressor(random_state=1, max_iter=500).fit(X_train, y_train)
    training_end=datetime.now()
    forecast=mlpr.predict(X_test)
    forecast[forecast<0]=0
    epsilon=np.abs(y_test.flatten()-forecast.flatten())
    q_hat=np.quantile(epsilon,1-alpha)
    model=Model(model_pickle=pickle.dumps(mlpr),TrainingStart=training_start,TrainingEnd=training_end,page_id=page_id,model_params=json.dumps(content),q_hat=q_hat,model_metrics=np.round(np.mean(epsilon),3))
    model.save()
    output=X_test[0].reshape(1,-1)
    forecast=mlpr.predict(output)
    print(forecast,q_hat)
    lower_bound=forecast[0]-q_hat
    upper_bound=forecast[0]+q_hat
    lower_bound = list(lower_bound.astype('float64'))
    upper_bound= list(upper_bound.astype('float64'))

    r={'lower_bound':lower_bound,'upper_bound':upper_bound}


    return json.dumps(r)

@app.route("/docs/swagger.json")
def specs():
    return  send_file('swagger.json')



if __name__=='__main__':
    app.run(host='myapp')
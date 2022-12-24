from flask_httpauth import HTTPDigestAuth
from Model.models import Visitor
import json
from flask import request, Blueprint,send_from_directory,send_file
from main import db,app
import yaml
import os
import pandas as pd
import numpy as np
from keras import Sequential
from keras.models import Model
from keras.layers import Dense, Input,Dropout
import keras.backend as K
from flask_swagger_ui import get_swaggerui_blueprint

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




def tilted_loss(q,y,f):
    # q: Quantile to be evaluated, e.g., 0.5 for median.
    # y: True value.
    # f: Fitted (predicted) value.
    e = (y-f)
    return K.mean(K.maximum(q*e, (q-1)*e), axis=-1)

# Feedforward neural network QR architecture

def QuantileRegressionModel(n_in,n_out,qs=[0.1, 0.5, 0.9]):
    ipt_layer = Input((n_in,))
    layer1 = Dense(100, activation='relu')(ipt_layer)
    drop1=Dropout(0.1)(layer1)
    layer2 = Dense(100, activation='relu')(drop1)
    drop2=Dropout(0.1)(layer2)
    
    out1 = Dense(n_out, name='out1')(drop2)
    out2 = Dense(n_out, name='out2')(drop2)
    out3 = Dense(n_out, name='out3')(drop2)
    
    q1, q2, q3 = qs
    model = Model(inputs=ipt_layer, outputs=[out1, out2, out3])
    model.compile(loss={'out1': lambda y,f: tilted_loss(q1,y,f),
                        'out2': lambda y,f: tilted_loss(q2,y,f),
                        'out3': lambda y,f: tilted_loss(q3,y,f),}, 
                  loss_weights={'out1': 1, 'out2': 1, 'out3': 1},
                 optimizer='adam')
    
    return model

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

@app.route('/train',methods=['POST'])
@auth.login_required
def train():

    content = json.loads(request.data)
    page_id=int(content['page_id'])
    lags=int(content['lags'])
    forecastperiod=int(content['forecastperiod'])
    alpha=float(content['alpha'])
    
    list_visitors=Visitor.get_by_page(page_id)
    results = [obj.to_dict() for obj in list_visitors]
    data=pd.DataFrame.from_dict(results)
    data['accessed_at'] = pd.to_datetime(data['accessed_at'])
    df_counts=data.groupby([pd.Grouper(key='accessed_at', freq='H')]).count()
    df_counts.reset_index(inplace=True)
    X,y=to_supervised(df_counts['page_id'].values,n_lags=lags,n_output=forecastperiod)
    qr=QuantileRegressionModel(lags,forecastperiod,qs=[alpha/2, 0.5, 1-alpha/2])
    qr.fit(X,y,epochs=100,verbose=0,batch_size=100)
    output=X[10].reshape(1,-1)
    forecast=qr.predict(output)
    lower_bound=forecast[0].flatten()
    upper_bound=forecast[2].flatten()
    lower_bound = list(lower_bound.astype('float64'))
    upper_bound= list(upper_bound.astype('float64'))

    r={'lower_bound':lower_bound,'upper_bound':upper_bound}


    return json.dumps(r)

@app.route("/docs/swagger.json")
def specs():
    return  send_file('swagger.json')



if __name__=='__main__':
    app.run(host='myapp')
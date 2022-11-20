from confluent_kafka import Consumer
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import datetime
import yaml
import json


################ kafka consumer
c=Consumer({'bootstrap.servers':'broker:29092','group.id':'python-consumer','auto.offset.reset':'earliest'})
print('Kafka Consumer has been initiated...')

print('Available topics to consume: ', c.list_topics().topics)
c.subscribe(['visitor_topic'])
################

#### flask app ####
app = Flask(__name__)
db = yaml.full_load(open('db.yml'))
#mysql+driver://username:password@host:port/database_name
connection_str='mysql+pymysql://'+db['mysql_user']+':'+db['mysql_password']+'@'+db['mysql_host']+'/'+db['mysql_db']
app.config['SQLALCHEMY_DATABASE_URI']=connection_str
print(connection_str)

db = SQLAlchemy(app)

class Visitor(db.Model):
    __tablename__ = 'Visitors'
    id = db.Column(db.Integer, primary_key=True)
    accessed_at=db.Column(db.Float)
    user_id=db.Column(db.Integer)
    page_id=db.Column(db.Integer)


        
if __name__ == '__main__':
    with app.app_context():
        while True:
            msg=c.poll(1.0) #timeout
            if msg is None:
                continue
            if msg.error():
                print('Error: {}'.format(msg.error()))
                continue
            data=json.loads(msg.value().decode('utf-8'))
            db.create_all()
            print(data,'ok')
            print(type(data))
            print(data.keys())
            print(data['accessed_at'],data['user_id'],data['page_id'])
            visitor=Visitor(accessed_at=data['accessed_at'],user_id=data['user_id'], page_id=data['page_id'])
            db.session.add(visitor)
            db.session.commit()
            print(data)
            print(Visitor.query.all())
            #app.run(host="0.0.0.0", debug=False,port=85)
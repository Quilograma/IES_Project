from Consumer.kafka_consumer import c
import json
import datetime
from Model.models import Visitor
from Utils.db import db
from Config.app_config import app
from flask_httpauth import HTTPDigestAuth
from flask_sqlalchemy import SQLAlchemy
db.init_app(app)




if __name__ == '__main__':
    with app.app_context():
        print('Available topics to consume: ', c.list_topics().topics)
        c.subscribe(['visitor_topic'])
        db.create_all()
        while True:
            msg=c.poll(1.0) #timeout
            if msg is None:
                continue
            if msg.error():
                print('Error: {}'.format(msg.error()))
                continue
            data=json.loads(msg.value().decode('utf-8'))
            visitor=Visitor(accessed_at=datetime.datetime.utcfromtimestamp(data['accessed_at']),user_id=data['user_id'], page_id=data['page_id'])
            visitor.save()
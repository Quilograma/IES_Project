from Model.flask_mysql_conn import db,app,Visitor
from Consumer.kafka_consumer import c
import json
import datetime


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
            db.session.add(visitor)
            db.session.commit()
            print(data)
            print(Visitor.query.all())
            #app.run(host="0.0.0.0", debug=False,port=85)
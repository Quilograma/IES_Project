from Model.flask_mysql_conn import db,app,Visitor
from Consumer.kafka_consumer import c
import json


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
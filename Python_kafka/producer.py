from confluent_kafka import Producer
from faker import Faker
import json
import time
import logging
import random
import  datetime

fake=Faker()

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='producer.log',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

####################
p=Producer({'bootstrap.servers':'localhost:9092'})
print('Kafka Producer has been initiated...')
#####################
def receipt(err,msg):
    if err is not None:
        print('Error: {}'.format(err))
    else:
        message = 'Produced message on topic {} with value of {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)
        
#####################
def main():
    while True:
        data={
            'accessed_at': datetime.datetime.now().timestamp(),
            'user_id': random.randint(0,10000),
            'page_id': random.randint(1,10)
           }
        m=json.dumps(data)
        p.poll(1)
        p.produce('visitor_topic', m.encode('utf-8'),callback=receipt)
        p.flush()
        time.sleep(random.randint(0,60))
        
if __name__ == '__main__':
    main()
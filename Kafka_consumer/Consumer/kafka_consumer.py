from confluent_kafka import Consumer

c=Consumer({'bootstrap.servers':'broker:29092','group.id':'python-consumer','auto.offset.reset':'earliest'})
print('Kafka Consumer has been initiated...')

print('Available topics to consume: ', c.list_topics().topics)
c.subscribe(['visitor_topic'])
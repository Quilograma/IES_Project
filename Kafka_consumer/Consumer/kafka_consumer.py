from confluent_kafka import Consumer

c=Consumer({'bootstrap.servers':'broker:29092','group.id':'python-consumer','auto.offset.reset':'earliest'})
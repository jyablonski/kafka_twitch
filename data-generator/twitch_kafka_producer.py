#!/usr/bin/env python
import os
import datetime
import sys
import twitch
from itertools import islice
import json
from confluent_kafka import Producer

# pass in credentials to connect to the twitch api.
client = twitch.TwitchHelix(client_id=os.environ.get('client_id'),
                            client_secret=os.environ.get('client_secret'),
                            scopes=[twitch.constants.OAUTH_SCOPE_ANALYTICS_READ_EXTENSIONS])
client.get_oauth()

# connect to the kafka cluster
p = Producer({'bootstrap.servers': 'kafka:29092'})

# this is an acknowledgement function from 
# https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html
# this ensures a notification upon delivery or failure of any message.
def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: {0}: {1}"
              .format(msg.value(), err.str()))
    else:
        print("Message produced: {0}".format(msg.value()))

# this takes the data out of a datetime.date(2022, 04, 06) format and into a human readable string
def json_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise "Type %s not serializable" % type(obj)


try:
    streams = client.get_streams(page_size=1) # this value can be 100 for maximum amount of data, but i kept as 1.

    while streams.next:

        p.poll(0.0)

        for stream in islice(streams, 0, 1): #100
            payload = json.dumps(stream, default=json_serializer, ensure_ascii=False).encode('utf-8')
            # have to dump json into string then encode it into bytes before being able to send it across the network.

            key = stream['id']

            p.produce(topic='twitch-streams', key=stream['id'], value=json.dumps(stream, default=json_serializer, ensure_ascii=False).encode('utf-8'), callback=acked)

    p.flush()

except Exception as e:
    print(f"Exception Occurred, {e}")
    sys.exit(1)

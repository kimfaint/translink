#!/usr/bin/env python3
from google.transit import gtfs_realtime_pb2
import requests
import psycopg2

conn = psycopg2.connect(database="translink", user = "translink", password = "translink", host = "127.0.0.1", port = "5432")
cur = conn.cursor()

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://gtfsrt.api.translink.com.au/Feed/SEQ')
feed.ParseFromString(response.content)
total = 0
total_inserted = 0
print('vehicles')
print('-'*20)
for entity in feed.entity:
    if entity.HasField('vehicle'):
        vid = entity.vehicle.vehicle.id
        timestamp = entity.vehicle.timestamp
        label = entity.vehicle.vehicle.label
        lat = entity.vehicle.position.latitude
        lon = entity.vehicle.position.longitude
        latest_timestamp = 0
        select_latest_query = "SELECT timestamp FROM vehicles WHERE id='%s' ORDER BY timestamp DESC limit 1" % vid
        print(select_latest_query)
        cur.execute(select_latest_query)
        latest = cur.fetchone()
        if latest:
            latest_timestamp = latest[0]
            if latest_timestamp != timestamp:
                insert_query = "INSERT INTO vehicles (id, timestamp, label, lat, lon) VALUES ('%s', %i, '%s', %f, %f)" % (vid, timestamp, label, lat, lon)
                print(insert_query)
                cur.execute(insert_query)
                total_inserted += 1
        total += 1
print('-'*20)
print('total vechicles:', total)
print('total inserted:', total_inserted)
conn.commit()
conn.close()

#!/usr/bin/env python3

"""
Experiment with tracking vehicle locations and how often they change.
"""

import time
import sys

from google.transit import gtfs_realtime_pb2
import requests
import psycopg2

# Set starting sample period from argument
sample_period = 60
if len(sys.argv) > 1:
    sample_period = int(sys.argv[1])

# Setup database connection
conn = psycopg2.connect(database="translink", user = "translink", password = "translink", host = "127.0.0.1", port = "5432")
cur = conn.cursor()

# Main loop
run = True
while (run):
    try:
        # Read feed
        feed = gtfs_realtime_pb2.FeedMessage()
        response = requests.get('https://gtfsrt.api.translink.com.au/Feed/SEQ')
        feed.ParseFromString(response.content)

        # Iterate over vehicles
        total = 0
        total_existing = 0
        total_inserted = 0
        total_updated = 0
        #print('vehicles')
        #print('-'*20)
        for entity in feed.entity:
            if entity.HasField('vehicle'):

                # Get vehicle details of interest
                vid = entity.vehicle.vehicle.id
                timestamp = entity.vehicle.timestamp
                label = entity.vehicle.vehicle.label
                lat = entity.vehicle.position.latitude
                lon = entity.vehicle.position.longitude
                insert = True

                # Don't insert if latest timestamp for vehicle is the same
                latest_timestamp = 0
                select_latest_query = "SELECT timestamp FROM vehicles WHERE id='%s' ORDER BY timestamp DESC limit 1" % vid
                #print(select_latest_query)
                cur.execute(select_latest_query)
                latest = cur.fetchone()
                if latest:
                    latest_timestamp = latest[0]
                    insert = latest_timestamp != timestamp
                    total_existing += 1

                # Insert vehicle details
                if insert:
                    insert_query = "INSERT INTO vehicles (id, timestamp, label, lat, lon) VALUES ('%s', %i, '%s', %f, %f)" % (vid, timestamp, label, lat, lon)
                    #print(insert_query)
                    cur.execute(insert_query)
                    total_inserted += 1
                    if latest:
                        total_updated += 1
                    
                total += 1

        # Calculate percent of existing vehicles updated
        percent_updated = -1
        if total_existing:
            percent_updated = 100 * total_updated / total_existing

        # Print summary
        print('-'*20)
        print('  sample period:', sample_period)
        print('total vechicles:', total)
        print('       inserted:', total_inserted)
        print('       existing:', total_existing)
        print('        updated: %i (%.2f%s)' % (total_updated, percent_updated, '%'))

        # Adjust sample period
        if percent_updated > -1:
            if percent_updated < 95:
                sample_period += 1
        
        # Sleep until next loop
        time.sleep(sample_period)
    except KeyboardInterrupt:
        run = False

print("Finished")
conn.commit()
conn.close()

## SCRIPT TO INSERT GTFS DATA INTO SQLITE DATABASE ##
import pandas as pd
import numpy as np
import sqlite3
from create_database import db, Routes, Trips, Stops, Transfers, Stop_times, Stops_routes, Timetable
from functions import minutes
#function to automate data insertion from  a.txt file into a mapped table with same name
def insert_data (Class):
    object_list = []
    gtfsfile = pd.read_csv("data/tub/%s.txt" % Class.__tablename__)
    for i in range(0, len(gtfsfile)):
        row = gtfsfile.loc[i,:]
        mapped_row = Class(*row.astype(str).replace("nan", np.nan))
        object_list.append(mapped_row)
    db.session.add_all(object_list)
    db.session.commit()

#inserting data from GTFS .txt into routes, trips, stops, stop_times and transfers mapped tables
insert_data(Routes);insert_data(Trips);insert_data(Stops);insert_data(Transfers);insert_data(Stop_times)

#inserting data into Stop_routes customized table : retrieving all route id for each stop id

conn = sqlite3.connect("TUB.sqlite3")
cur = conn.cursor()
query_stops_routes =        "SELECT DISTINCT  stops.id, routes.id \
                            FROM stops, stop_times, trips, routes \
                            WHERE stops.id = stop_times.stop_id \
                            AND trips.id = stop_times.trip_id \
                            AND routes.id = trips.route_id "
cur.execute(query_stops_routes)

results = cur.fetchall()
object_list = []
for element in results:
    mapped_row = Stops_routes(*element)
    object_list.append(mapped_row)
db.session.add_all(object_list)
db.session.commit()

#inserting data into Timetable customozed table 

## PART 1: inserting modified results from a query: get the travel time to transit between 2 stops for each trip

cur = conn.cursor()
query_travel_time =     "SELECT trips.id, stop_times.departure_time, stop_times.stop_id \
                        FROM routes, trips, stop_times, stops \
                        WHERE routes.id = trips.route_id \
                        AND trips.id = stop_times.trip_id \
                        AND stops.id = stop_times.stop_id "

cur.execute(query_travel_time)
results = cur.fetchall()
#computing travelling time between 2 stops on the same trip
modified_results =  []
for i in range(0, len(results)-1):
    if results[i][0] == results[i+1][0]:
        from_stop_id = results[i][2]
        to_stop_id = results[i+1][2]
        departure_time = minutes(results[i][1])
        travel_time = minutes(results[i+1][1]) - departure_time
        trip_id = results[i][0]
        mytuple = tuple([from_stop_id,to_stop_id, departure_time, travel_time, trip_id])
        modified_results.append(mytuple)
#inserting modified results in Timetable database
object_list = []
for element in modified_results:
    mapped_row = Timetable(*element)
    object_list.append(mapped_row)
db.session.add_all(object_list)
db.session.commit()


## PART 2: inserting transfers in timetable , to keep recording travelling time when transferring from a stop to another one 

query_transfers = "SELECT transfers.from_stop_id, transfers.to_stop_id, -1, transfers.min_transfer_time / 60, 'transfers' \
                   FROM transfers"
cur.execute(query_transfers)
results = cur.fetchall()
object_list = []
for element in results:
    mapped_row = Timetable(*element)
    object_list.append(mapped_row)
db.session.add_all(object_list)
db.session.commit()

### --- ####
###  IMPORTING PACKAGES, FUNCTIONS AND OBJECTS  ###

import os
import sqlite3
import csv
from math import acos, cos, sin, radians
from heapq import heappop, heappush
from functions import minutes, minutes_to_string
import pandas as pd
import numpy as np
import sqlite3
from mapping_database import db, Routes, Trips, Stops, Transfers, Stop_times, Timetable, Stops_routes
import datetime

### PREPARING DATA FOR RUNNING DIJKSTRA###

#querying all data from timetable
query_timetable = Timetable.query.with_entities(Timetable.from_stop_id, Timetable.to_stop_id, Timetable.departure_time, Timetable.travel_time).order_by(Timetable.from_stop_id, Timetable.to_stop_id, Timetable.departure_time, Timetable.travel_time)
results = query_timetable.all()

#storing results into a dataframe object
timetable_df = pd.DataFrame.from_records(data=results,columns=["from_stop_id", "to_stop_id", "departure_time", "travel_time"])

# from timetable dataframe, get a dictonnary listing all possible successors at each departure node, with departure schedules 
successors_by_departure= {}
successors={}
for i in range(0, len(timetable_df)-1): 
    travel, travel_next = (timetable_df.loc[i],timetable_df.loc[i+1]) #iterating on timetable 2 rows by 2 rows
    from_stop_id, to_stop_id, departure_time, travel_time= travel
    from_stop_id_next, _,_,_ = travel_next
    if to_stop_id not in successors: successors[to_stop_id] = []
    successors[to_stop_id].append( (departure_time, travel_time) )
    if from_stop_id != from_stop_id_next:
        successors_by_departure[from_stop_id] = successors
        successors = {}
    elif from_stop_id == timetable_df['from_stop_id'].loc[len(timetable_df)-1]: #when reaching end of listing
        successors_by_departure[from_stop_id] = successors
successors_by_departure[timetable_df['from_stop_id'].loc[len(timetable_df)-1]][timetable_df['to_stop_id'].loc[len(timetable_df)-1]].append((timetable_df['departure_time'].loc[len(timetable_df)-1], timetable_df['travel_time'].loc[len(timetable_df)-1]))  #don't forget last row


### DEFINING REQUIRED FUNCTION FOR BUILDING DIJIKSTRA's ALGORTIHM ###

## get optimal arrival time at a successor given its departure schedules and an input departure time (the earliest arrival time) ## 

def optimal_arrival_time_at_successor (successor, input_departure_time):
    # a successor is described by 2 components A & B  where A: destination name and B: list of departure schedules to go to A (with travel time associated)
    destination_name, schedules_and_traveltime = successor 
    optimal_arrival_time = float('inf')  #we assume it unknown 
    for departure_schedule, travel_time in schedules_and_traveltime : 
        if departure_schedule == -1 : #it is a transfer
           optimal_arrival_time = input_departure_time + travel_time  
        elif departure_schedule >= input_departure_time and departure_schedule + travel_time < optimal_arrival_time: 
            optimal_arrival_time = departure_schedule + travel_time 
    return travel_time, destination_name, optimal_arrival_time 


## get successor(s) of a departure node with earliest  arrival time  given an input departure time : actualise the transit network given a time frame constraint##

def successors(departure_node, departure_time) : 
    successors = successors_by_departure[departure_node].items()
    return sorted(map(lambda successor : optimal_arrival_time_at_successor(successor, departure_time), successors)) #successors with optimal arrival time



### BUILDING DIJKSTRA'S ALGORITHM ###

## dijkstra's algorithm to output shortest path through the transit network to go from an inpput departure to an input destination, given a departure time ##

def shortest_path(departure, input_departure_time, destination):

    ## NOTES ##
    
    #each node we push in the queue to be explored by the algo is described  by a 3-uplet (cost,name,time) 
        # cost : amount of time needed to reach this node from input departure node given input departure time (travel time between the nodes + waiting time for a bus to go over there) == the earliest arrival time at the node
        # name: name of the bus stop  in the transit nework
        # time: optimal arrival time at this stop given departure time input by user

    #the arrival time at a bus stop = the departure time from this bus stop in the transit network we are studying


    ## CONVERTING INPUT DEPARTURE TIME INTO MINUTES ##

    if input_departure_time == "": #case if not input departure time, consider leaving now
        now = datetime.now()
        input_departure_time = minutes(now.strftime("%H:%M"))
    else: 
         input_departure_time = minutes(input_departure_time)
    
     ## INITIALIZING OBJECTS TO KEEP TRACK OF ALGORITHM'S OPTIMAL CHOICES ##

    explored = set() # explored nodes
    costs = {departure: 0}  # cost from departure node to reach each selected node 
    times = {departure: input_departure_time} # arrival times at each selected node (time memory)
    path={}  # path to arrive at current selected node (space memory)
    to_explore = [ (0, departure, input_departure_time)] # queue of nodes to explore, start with departure node (the higher the amount of time needed, the farer in the queue)

    ## STARTING  GREEDY ALGORITHM : FIND SHORTEST PATH FROM DEPARTURE NODE TO ALL OTHER NODES ## 
    
    while to_explore != []: 

        # PICK THE NEXT UNEXPLORED NODE IN THE QUEUE : THE ONE HAVING LOWEST TRAVEL TIME #

        _, current_stop_name, departure_time_at_current = heappop(to_explore) 
        if current_stop_name in explored: continue   #if node has already been explored, take next one in the queue
        explored.add(current_stop_name) #else, mark it as explored and start exploring it

        for _, successor_name, arrival_time_at_successor in successors(current_stop_name,departure_time_at_current):

            # STUDY SUCCESSOR(S) OF CURRENT NODE WE ARE EXPLORING

            if successor_name in explored : continue  #if successor already marked as explored, study another successor if any, or explore another node
            if arrival_time_at_successor == float('inf'): continue # if impossible to reach successor given today's services (ex: current node is a terminus) , study another successor if any, or explore another node

            total_time_from_departure_to_successor =  arrival_time_at_successor - input_departure_time  #total time needed from departure to reach this neighbour passing by the current node (cost)

            # if cost to reach successor from departure is unknown or if a lower cost is found : keep track of it and add this successor node to the  epxloring queue
            if successor_name not in costs or costs[successor_name] > total_time_from_departure_to_successor :
                costs[successor_name] = total_time_from_departure_to_successor
                heappush(to_explore, (total_time_from_departure_to_successor, successor_name, arrival_time_at_successor)) 
                path[successor_name] = current_stop_name  
                times[successor_name] = arrival_time_at_successor


    ## WHEN GREEDY ALGORITHM IS DONE : TRY TO FIND SHORTEST PATH FROM DEPARTURE NODE TO DESTINATION NODE GIVEN TIME FRAME

    try:
        #start from destination node and try to go backward to retrieve the departure node
        stops_list = [destination]
        stop_times = [times[destination]]
        stop = destination
        while stop != departure:
            stop=path[stop] 
            stops_list.insert(0,stop) #insert the current stop at beginning of list
            stop_times.insert(0,times[stop])
    except: return "Impossible de trouver un itinéraire pour ce voyage. Consultez le plan et les horaires, certaines lignes ne sont plus en service après 17h. "

    return stops_list, stop_times
### IMPORT DEFINED FUNCTIONS  ###
import dijkstra
import functions
from mapping_database import db, Routes, Trips, Stops, Transfers, Stop_times, Timetable, Stops_routes, Stops


### function describing the ride requested by user in a dictionnary ###
def get_ride_dictionnary(departure, input_departure_time, destination):

    ## intializing object to track every necessary info for end user on its requested ride ##
    ride_dict = dict()
    ride_dict['Ride_initialization'] = [departure, functions.minutes(input_departure_time), '', '']

    #get the shortest path by executing Dijkstra's algorithm
    ride = dijkstra.shortest_path(departure, input_departure_time, destination)

    stops_of_ride = ride[0]
    times_of_ride = ride[1]

    for stop,time in zip(stops_of_ride, times_of_ride):

            ## retrieving full name of recommended stop by dijkstra ##
        stop_name = Stops.query.with_entities(Stops.stop_name).filter(Stops.id == stop).all()[0][0]

            #if it a current stop needs a transfer and is not the arrival: mark it as transfer 
        if  (stop != stops_of_ride[-1]) and (stop,  stops_of_ride[stops_of_ride.index(stop)+1]) in Transfers.query.with_entities(Transfers.from_stop_id,Transfers.to_stop_id ).all(): 
            departure_time_at_stop = time
            route_of_trip = "Transfer"
            direction_of_trip = stops_of_ride[stops_of_ride.index(stop)+1]  #where to move for the transfer
            ride_dict[stop] = [stop_name, departure_time_at_stop, route_of_trip,direction_of_trip]
            is_terminus ="No"   
            #if not a transfer
        else:

            ## retreiving departure time at this stop  ##
            schedules_and_tripid_at_stop = Stop_times.query.with_entities(Stop_times.departure_time, Stop_times.trip_id).filter(Stop_times.stop_id == stop) #get all departure schedules at this stop & associated trip id
            schedules_and_tripid_at_stop_in_minutes = [(functions.minutes(i[0]), i[1]) for i in schedules_and_tripid_at_stop] #convert schedules in minutes
            departure_time_at_stop =  min(filter(lambda x : x >=0,[i - time for (i,_) in schedules_and_tripid_at_stop_in_minutes])) + time #retrieve the departure time recommended by dijkstra (will only change for the departure)

            ## retreiving the trip id of stop given its departure time ##
            trip_of_stop = list(filter(lambda tuple: tuple[0]==departure_time_at_stop, schedules_and_tripid_at_stop_in_minutes))[0][1]

            
            ## checking if current stop is a service terminus (no departure time from it, it is actually just an  arrival time so it will need a transit, or it can a departure time but for a different destination, so a different service)
            check_for_departure_at_this_time = Timetable.query.with_entities(Timetable.departure_time).filter(Timetable.from_stop_id == stop , Timetable.departure_time == int(departure_time_at_stop)).all()
                #flagging if its the case
            if check_for_departure_at_this_time == [] : #it is just an arrival time (end of service)
                is_terminus = "Yes"
            else:
                is_terminus = "No"
            
            ## retrieving the route associated to the stop ##
            route_of_trip = Trips.query.with_entities(Trips.route_id).filter(Trips.id == trip_of_stop).all()[0][0]

            ## retreiving the direction informaiton associated to the trip ##
            direction_of_trip = Trips.query.with_entities(Trips.trip_headsign).filter(Trips.id == trip_of_stop).all()[0][0]

            ## storing every useful info on the stop given its departure time, for documenting the requested ride by user ##
            ride_dict[stop] = [stop_name, departure_time_at_stop, route_of_trip,direction_of_trip, is_terminus, trip_of_stop]


    return ride_dict


### function to indicate the different route to take in a sequence ###
def get_routes_to_take (ride_dict):
    routes_list =[]

    for (stop,info) in ride_dict.items():
        if info[2] not in routes_list:
            routes_list.append(info[2])

    routes_list.remove('') #removing route at dictionary initialization
    if 'Transfer' in routes_list: routes_list.remove('Transfer')
    return routes_list

### function to output the total travel time ###
def get_total_travel_time (ride_dict):
    ride_start_time = ride_dict['Ride_initialization'][1]
    next_times=[]
    for (stop,info) in ride_dict.items():
        next_times.append(info[1])
    arrival_time = next_times[-1]
    total_travel_time = arrival_time - ride_start_time
    return total_travel_time

 ### function to ouput the arrival time at destination ###   
def get_arrival_time_at_destination (ride_dict):
    ride_start_time = ride_dict['Ride_initialization'][1]
    total_travel_time = get_total_travel_time (ride_dict)
    arrival_time = ride_start_time + total_travel_time
    return arrival_time

### function to ouput waiting time at departure ###
def waiting_time_at_departure (ride_dict):
    ride_start_time = ride_dict['Ride_initialization'][1]
    retrieved_departure_name = ride_dict[['Ride_initialization'][0]][0]

    #if starting stop implies a transfer
    if ride_dict[retrieved_departure_name][2] == "Transfer": 
        real_departure_index = list(ride_dict.keys()).index(retrieved_departure_name)+1 #retreive the stop from wich the user will wait for the bus
        real_departure_time = ride_dict[list(ride_dict.keys())[real_departure_index]][1]
        waiting_time_at_departure =  real_departure_time - ride_start_time

    #if not a transfer:    
    else:
        departure_time_at_start = ride_dict[retrieved_departure_name][1]
        waiting_time_at_departure =  departure_time_at_start - ride_start_time

    return waiting_time_at_departure

### function to retrieve and describe  all possible transit during the ride (stop to transit, waiting time at stop..) ###
def get_transit(ride_dict) :
    #îtinializing transit tracking dictionary 
    transit =dict()

    #list the different stops of the ride in a sequence
    iterate_on_stops = list(ride_dict.keys())[1:]

    #start interating on the stop and the next one
    for i in range(0, len(iterate_on_stops)-2):
        current_stop = iterate_on_stops[i]
        next_stop = iterate_on_stops[i+1]

        #if facing a transfer, skip it and move to the next stop
        if ride_dict[next_stop][2] == 'Transfer':
            next_stop = iterate_on_stops[i+2]
            change_at = next_stop #where to change
            prev_route  = ride_dict[current_stop][2] #from which route 
            next_route = ride_dict[change_at][2] #to which route
            travel_time_current_to_next = Timetable.query.with_entities(Timetable.travel_time,Timetable.departure_time , Timetable.from_stop_id).filter(Timetable.from_stop_id == current_stop, Timetable.departure_time == int(ride_dict[current_stop][1])).all()[0][0]
            arrival_at_change = ride_dict[current_stop][1] + travel_time_current_to_next #at what time the user arrives at the change, given the travel time from current stop
            waiting_time_for_change = ride_dict[change_at][1] - arrival_at_change #how long he will have to wait for the next departure

            #tracking all that change info in the dict (a transfer can implie a transit)
            transit[change_at] = [prev_route, next_route, arrival_at_change, waiting_time_for_change]

        #if current stop studying is associated to a different route than the next stop, but its not a transfer: there is a change and it is done at next stop

        elif ride_dict[current_stop][2] != ride_dict[next_stop][2] and  ride_dict[current_stop][2] != 'Transfer':
            #checking if it is a terminus of a service:
            if ride_dict[current_stop][4] == "No":
                #retrieve all useful info to explain the change to the user:
                change_at = next_stop #where to change
                prev_route  = ride_dict[current_stop][2] #from which route 
                next_route = ride_dict[change_at][2] #to which route
                travel_time_current_to_next = Timetable.query.with_entities(Timetable.travel_time,Timetable.departure_time , Timetable.from_stop_id).filter(Timetable.from_stop_id == current_stop, Timetable.departure_time == int(ride_dict[current_stop][1])).all()[0][0]
                arrival_at_change = ride_dict[current_stop][1] + travel_time_current_to_next #at what time the user arrives at the change, given the travel time from current stop
                waiting_time_for_change = ride_dict[change_at][1] - arrival_at_change #how long he will have to wait for the next departure
                #tracking all that change info in the dict
                transit[current_stop] = [prev_route, next_route, arrival_at_change, waiting_time_for_change]

            else: #current stop is a terminus of current service : passenger will have to transit at this stop
                change_at = current_stop
                prev_route  = ride_dict[current_stop][2]
                next_route = ride_dict[next_stop][2]
                arrival_at_change = ride_dict[current_stop][1]
                waiting_time_for_change = ride_dict[next_stop][1] - ride_dict[current_stop][1]
                transit[change_at] = [prev_route, next_route, arrival_at_change, waiting_time_for_change]

        #if current stop studied is associated to a different service than the next stop (but same line) : transit needs to be done at this stop, not the next one
        
        elif ride_dict[current_stop][2] == ride_dict[next_stop][2] and  ride_dict[current_stop][2] != 'Transfer' and ride_dict[current_stop][5] != ride_dict[next_stop][5]  and ride_dict[current_stop][3] == ride_dict[next_stop][3]:
            if ride_dict[current_stop][4] == "No":
                change_at = next_stop 
                prev_route  = ride_dict[current_stop][2] 
                next_route = ride_dict[change_at][2] 
                travel_time_current_to_next = Timetable.query.with_entities(Timetable.travel_time,Timetable.departure_time , Timetable.from_stop_id).filter(Timetable.from_stop_id == current_stop, Timetable.departure_time == int(ride_dict[current_stop][1])).all()[0][0]
                arrival_at_change = ride_dict[current_stop][1] + travel_time_current_to_next 
                waiting_time_for_change = ride_dict[change_at][1] - arrival_at_change 
                transit[current_stop] = [prev_route, next_route, arrival_at_change, waiting_time_for_change]

            else:
                change_at = current_stop
                prev_route  = ride_dict[current_stop][2]
                next_route = ride_dict[next_stop][2]
                arrival_at_change = ride_dict[current_stop][1]
                waiting_time_for_change = ride_dict[next_stop][1] - ride_dict[current_stop][1]
                transit[change_at] = [prev_route, next_route, arrival_at_change, waiting_time_for_change]
        else: 
            i=i+1
            current_stop = next_stop
            next_stop = iterate_on_stops[i+1]


    #checking the conditions  for the last stop before arrival :
    #lines are different
    if ride_dict[current_stop][2] != ride_dict[next_stop][2] and  ride_dict[current_stop][2] != 'Transfer':

        if ride_dict[current_stop][4] == "No":
            change_at = current_stop 
            arrival = next_stop
            prev_route  = ride_dict[current_stop][2] 
            next_route = ride_dict[arrival][2] 
            travel_time_to_arrival = Timetable.query.with_entities(Timetable.travel_time,Timetable.departure_time , Timetable.from_stop_id).filter(Timetable.from_stop_id == current_stop,Timetable.to_stop_id == arrival).all()[0][0]
            arrival_at_change = ride_dict[change_at][1] 
            waiting_time_for_change = (ride_dict[arrival][1] - ride_dict[change_at][1]) - travel_time_to_arrival
            transit[change_at] = [prev_route, next_route, arrival_at_change, waiting_time_for_change]

        else: 

            change_at = current_stop
            prev_route  = ride_dict[current_stop][2]
            next_route = ride_dict[next_stop][2]
            arrival_at_change = ride_dict[current_stop][1]
            waiting_time_for_change = ride_dict[next_stop][1] - ride_dict[current_stop][1]
            transit[change_at] = [prev_route, next_route, arrival_at_change, waiting_time_for_change]

    #service are different
    elif ride_dict[current_stop][2] == ride_dict[next_stop][2] and  ride_dict[current_stop][2] != 'Transfer' and ride_dict[current_stop][5] != ride_dict[next_stop][5] and  ride_dict[current_stop][3] == ride_dict[next_stop][3]:
        if ride_dict[current_stop][4] == "No":
            change_at = next_stop 
            prev_route  = ride_dict[current_stop][2] 
            next_route = ride_dict[change_at][2] 
            travel_time_current_to_next = Timetable.query.with_entities(Timetable.travel_time,Timetable.departure_time , Timetable.from_stop_id).filter(Timetable.from_stop_id == current_stop, Timetable.departure_time == int(ride_dict[current_stop][1])).all()[0][0]
            arrival_at_change = ride_dict[current_stop][1] + travel_time_current_to_next 
            waiting_time_for_change = ride_dict[change_at][1] - arrival_at_change 
            transit[current_stop] = [prev_route, next_route, arrival_at_change, waiting_time_for_change]

    return transit

### fonction to retrieve transfers in the ride dictionnary & describe them (destination for transfer, travel time to make it) ###
def get_transfers(ride_dict):
     #îtinializing transit tracking dictionary 
    transfers =dict()

    #list the different stops of the ride in a sequence
    iterate_on_stops = list(ride_dict.keys())[1:]

    #start interating on the stop and the next one
    for i in range(0, len(iterate_on_stops)-2):
        current_stop = iterate_on_stops[i]
        next_stop = iterate_on_stops[i+1]

        #if facing a transfer, skip it and move to the next stop
        if ride_dict[current_stop][2] == 'Transfer':
            transfer_from = current_stop
            transfer_to = next_stop #where to transfer

            travel_time_transfer = Timetable.query.with_entities(Timetable.travel_time).filter(Timetable.from_stop_id == transfer_from, Timetable.to_stop_id == transfer_to ).all()[0][0] #how long to do the transfer

            #tracking all the transfer info in the dict
            transfers[transfer_from] = [transfer_to, travel_time_transfer]
        
        else: 
            i=i+1
            current_stop = next_stop
            next_stop = iterate_on_stops[i+1]
    
    #checking if the last two stops of the list involves a transfer
    if ride_dict[iterate_on_stops[-2]][2] == "Transfer":
        transfer_from = current_stop
        transfer_to = next_stop #where to transfer
        travel_time_transfer = Timetable.query.with_entities(Timetable.travel_time).filter(Timetable.from_stop_id == transfer_from, Timetable.to_stop_id == transfer_to ).all()[0][0] #how long to do the transfer
        transfers[transfer_from] = [transfer_to, travel_time_transfer]
    return transfers
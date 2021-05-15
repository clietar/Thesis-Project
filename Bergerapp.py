#importing necessary packages to handle, process and render information to end-users
from pprint import pprint as pp
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

#connecting to the SQLite database
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TUB.sqlite3'

db = SQLAlchemy(app)

#importing back-end scripts and objects for data processing and shortest path computationn
import shortest_path_tuning
from functions import minutes_to_string
from mapping_database import Routes, Trips, Stops, Transfers, Stop_times, Timetable, Stops_routes, Stops



#handling users' ride request 
@app.route('/', methods=['POST', 'GET'])

def get_ride():

    #retrieving stops information to let the user select it in the forms
    stops_names_query = Stops.query.with_entities(Stops.stop_name).all()
    stop_names_list = [r[0] for r in stops_names_query]
    stop_names_list = sorted(stop_names_list)

    #if the user submit input information in the form: process his ride request
    if request.method == "POST":

        #retrieve information input by end user
        departure = request.form['departure']
        destination = request.form['destination']
        departure_time = request.form['departure_time']

        #if he input the same departure as the destination, render an error page
        if departure == destination : return render_template("error.html")
        #if not, process the information collected  with back-end functions and render the ride information
        else:
            #retrieve ids of departure and destination in database to trigger shortest path computation
            departure_id = Stops.query.with_entities(Stops.id).filter(Stops.stop_name == departure).all()[0][0]
            destination_id = Stops.query.with_entities(Stops.id).filter(Stops.stop_name == destination).all()[0][0]
            #get the ride dictionnary and stops to take for the ride
            ride_dict = shortest_path_tuning.get_ride_dictionnary(departure_id, departure_time, destination_id)
            stops = [stop for stop in ride_dict.keys()]

            #get the estimated arrival time
            arrival_time = shortest_path_tuning.get_arrival_time_at_destination(ride_dict)

            #get the total travel time
            travel_time = shortest_path_tuning.get_total_travel_time(ride_dict)

            #get the transfers
            transfers  = shortest_path_tuning.get_transfers(ride_dict)

            #get the transit
            transits = shortest_path_tuning.get_transit(ride_dict)

            #get waiting time at departure
            waiting_time = shortest_path_tuning.waiting_time_at_departure(ride_dict)

            return render_template('ride_results.html', ride_dict = ride_dict, stops= stops, destination=destination, departure = departure, departure_time = departure_time, transfers = transfers, transits = transits, arrival_time = arrival_time, travel_time = travel_time, func=minutes_to_string, waiting_time = waiting_time)

    #if he does not submit anything, just render the landing page
    return render_template('get_ride.html', stop_names_list=stop_names_list)

#handling any shortest computation error that can occur by rendering an error page
@app.errorhandler(Exception)          
def basic_error(e):          
    return render_template("error.html")

#redirecting the user when clicking on the about table 
@app.route('/about')
def about():
    return render_template('about.html')


if __name__=='__main__':
    app.run(debug=True)
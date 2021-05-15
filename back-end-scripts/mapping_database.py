
### SCRIPT TO MAP THE DATABASE WHERE WE WILL STORE THE GTFS FEED ###
from flask_sqlalchemy import SQLAlchemy
from Bergerapp import app
db = SQLAlchemy(app)

# mapping the SQLite tables from Bergerac's GTFS feed using SQLAlchemy

class Routes(db.Model):
    __tablename__ = "routes" 
    id = db.Column(db.String(3), primary_key = True) 
    agency_id = db.Column(db.String(3))
    route_short_name = db.Column(db.String(7)) 
    route_long_name = db.Column(db.Text)
    route_desc = db.Column(db.Text)
    route_type = db.Column(db.Integer)
    route_url = db.Column(db.Text)
    route_color = db.Column(db.String(10))
    route_text_color = db.Column(db.String(10))
    trips  = db.relationship('Trips', backref='routes')

    def __init__(self, id, agency_id,route_short_name, route_long_name, route_desc, route_type, route_url,route_color, route_text_color):
        self.id = id
        self.agency_id =agency_id 
        self.route_short_name = route_short_name
        self.route_long_name = route_long_name
        self.route_desc = route_desc
        self.route_type = route_type
        self.route_url = route_url
        self.route_color = route_color
        self.route_text_color = route_text_color


class Trips(db.Model):
    __tablename__ = "trips"
    route_id =  db.Column(db.String(3), db.ForeignKey('routes.id'))
    service_id =  db.Column(db.Integer)
    id =  db.Column(db.String(7), primary_key=True)
    trip_headsign =  db.Column(db.Text)
    trip_short_name = db.Column(db.String(40))
    direction_id =  db.Column(db.Integer)
    block_id = db.Column(db.Integer)
    trips  = db.relationship('Stop_times', backref="trips")

    def __init__(self, route_id,service_id,id, trip_headsign,trip_short_name,direction_id,block_id):
        self.route_id = route_id
        self.service_id =service_id 
        self.id = id
        self.trip_headsign = trip_headsign
        self.trip_short_name = trip_short_name
        self.direction_id = direction_id
        self.block_id = block_id


# A class to represent the Stops table as an object
class Stops(db.Model):
    
    #name of the table
    __tablename__= "stops"

    #defining its attributes as its columns
    id= db.Column(db.String(15), primary_key=True) #specifying the primary key
    stop_code= db.Column(db.String(30))
    stop_name= db.Column(db.Text)
    stop_desc= db.Column(db.Text)
    stop_lat= db.Column(db.Float)
    stop_lon= db.Column(db.Float) #specifying that the longitude must be a float number

    #defining the one-to-many relationships with other tables 
    stop_times  = db.relationship('Stop_times', backref='stops')
    transfer1  = db.relationship('Transfers', backref='stops')
    transfer2  = db.relationship('Transfers', backref='stops')

    #constructor method : allows to instantiate the stops table as an object by intializing its attributes
    def __init__(self, id, stop_code,stop_name, stop_desc, stop_lat, stop_lon):
        self.id = id
        self.stop_code = stop_code
        self.stop_name = stop_name
        self.stop_desc = stop_desc
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon

class Stop_times(db.Model):
    __tablename__ = "stop_times"
    trip_id= db.Column(db.String(7), db.ForeignKey('trips.id'), primary_key=True)
    arrival_time= db.Column(db.String(10), primary_key=True)
    departure_time= db.Column(db.String(10))
    stop_id= db.Column(db.String(15), db.ForeignKey('stops.id'))
    stop_sequence= db.Column(db.Integer)
    pickup_type= db.Column(db.Integer)
    drop_off_type= db.Column(db.Integer)

    def __init__(self, trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type, drop_off_type):
        self.trip_id = trip_id
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.stop_id = stop_id
        self.stop_sequence = stop_sequence
        self.pickup_type = pickup_type
        self.drop_off_type = drop_off_type


class Transfers(db.Model):
    __tablename__ = "transfers"
    from_stop_id= db.Column(db.String(30),db.ForeignKey('stops.id'), primary_key=True)
    to_stop_id= db.Column(db.String(30),db.ForeignKey('stops.id'),primary_key=True)
    transfer_type= db.Column(db.Integer)
    min_transfer_time= db.Column(db.Integer)
    from_stop = db.relationship("Stops", foreign_keys=[from_stop_id])
    to_stop = db.relationship("Stops", foreign_keys=[to_stop_id])
    __mapper_args__ = {'polymorphic_identity': 'transfers', 'inherit_condition': from_stop_id == Stops.id}

    def __init__(self, from_stop_id, to_stop_id, transfer_type, min_transfer_time):
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.transfer_type = transfer_type
        self.min_transfer_time = min_transfer_time

# adding new tables we will use for computing the shortest path

class Timetable(db.Model):  # table to reference the expected time to transit between 2 stops
    __tablename__ = "timetable"
    from_stop_id= db.Column(db.String(30), primary_key=True)
    to_stop_id= db.Column(db.String(30), primary_key=True)
    departure_time= db.Column(db.Integer, primary_key=True)
    travel_time = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column (db.String(30), primary_key=True)

    def __init__(self, from_stop_id, to_stop_id, departure_time, travel_time, trip_id):
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.departure_time = departure_time
        self.travel_time = travel_time
        self.trip_id = trip_id

class Stops_routes(db.Model): # table to reference all the stops by route 
    __tablename__ = "stops_routes"
    stop_id = db.Column(db.String(30), primary_key=True)
    route_id = db.Column(db.String(40), primary_key=True)

    def __init__(self, stop_id, route_id):
        self.stop_id = stop_id
        self.route_id= route_id

# will create a .sqlite3 file, the database file

db.create_all()   
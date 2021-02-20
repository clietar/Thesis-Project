import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

#connection to sqlite database
conn = sqlite3.connect("TUB.sqlite3")
cur = conn.cursor()
#querying all data from timetable
query_transfers = ("SELECT * FROM timetable")
cur.execute(query_transfers)
results = cur.fetchall()

#storing data into a pandas dataframe object for modelling the directed graph
network = pd.DataFrame(data= results, columns=["from_stop_id", "to_stop_id", "time_departure", "travel_time", "trip_id"])
len(network)
network = network.drop("time_departure", axis= 1)

#create a graph object from the dataframe by specifying the source, target and edge attribute columns
G = nx.from_pandas_edgelist(network,"from_stop_id", "to_stop_id",  "travel_time", create_using=nx.DiGraph())
edge_labels =nx.get_edge_attributes(G, "travel_time")
nodes = nx.spring_layout(G)

#plotting the directed graph of the transit network
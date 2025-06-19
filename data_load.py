import pandas as pd
from neo4j import GraphDatabase

URI = "neo4j://localhost"
AUTH = ("neo4j", "dataarchca2")  #use your own password, mine was 'dataarchca2'
driver = GraphDatabase.driver(URI, auth=AUTH)
driver.verify_connectivity()

trains = pd.read_csv('trains.csv')

station_names = pd.concat([trains['source'], trains['destination']]).unique().tolist()

station_query = '''
UNWIND $stations AS station_name
MERGE (:Station {name: station_name})
'''

driver.execute_query(station_query, stations=station_names)

print("Stations loaded")

route_data = trains.to_dict('records')

route_query = '''
UNWIND $routes AS row
MATCH (src:Station {name: row.source})
MATCH (dest:Station {name: row.destination})
CREATE (src)-[:ROUTE {
    train_number: row.train_number,
    train_name: row.train_name,
    distance: toFloat(row.distance),
    total_time: row.total_time,
    departure: row.departure,
    arrival: row.arrival
}]->(dest)
'''

driver.execute_query(route_query, routes=route_data)

print("Routes loaded")
print("Data loading completed!")

#run by: python data_load.py
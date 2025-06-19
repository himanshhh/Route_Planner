import pandas as pd
import matplotlib.pyplot as plt
from neo4j import GraphDatabase

URI = "neo4j://localhost"
AUTH = ("neo4j", "dataarchca2") #use your own password, mine was 'dataarchca2'
driver = GraphDatabase.driver(URI, auth=AUTH)
driver.verify_connectivity()

def get_count(query):
    result = driver.execute_query(query)
    count = result[0][0]['count']
    return count

station_count_query = "MATCH (n:Station) RETURN count(n) AS count"
station_count = get_count(station_count_query)

route_count_query = "MATCH ()-[r:ROUTE]->() RETURN count(r) AS count"
route_count = get_count(route_count_query)

print(f"Number of Station nodes: {station_count}")
print(f"Number of ROUTE relationships: {route_count}")

top_sources_query = """
MATCH (s:Station)-[r:ROUTE]->()
RETURN s.name AS station, count(r) AS outgoing_routes
ORDER BY outgoing_routes DESC
LIMIT 5
"""
result = driver.execute_query(top_sources_query)

records = [record.data() for record in result[0]]
df = pd.DataFrame(records)

if not df.empty:
    print("\nTop 5 stations by outgoing routes:")
    print(df.to_string(index=False))
    
#visualization to plot the top 5 busiest stations
    plt.figure(figsize=(10, 6))
    plt.bar(df['station'], df['outgoing_routes'], color='mediumpurple')
    plt.title("Top 5 Stations by Outgoing Routes", fontsize=14)
    plt.xlabel("Station", fontsize=12)
    plt.ylabel("Number of Outgoing Routes", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
else:
    print("\n(No outgoing routes found)")

#run by: python statistics.py
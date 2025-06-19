import argparse
import pandas as pd
import matplotlib.pyplot as plt
from neo4j import GraphDatabase

URI = "neo4j://localhost"
AUTH = ("neo4j", "dataarchca2")  #use your own password, mine was 'dataarchca2'
driver = GraphDatabase.driver(URI, auth=AUTH)

def find_shortest_path(origin, destination):
    query = '''
    MATCH (start:Station {name:$origin}), (end:Station {name:$destination})
    CALL apoc.algo.dijkstra(start, end, 'ROUTE>', 'distance') YIELD path, weight
    RETURN [n IN nodes(path) | n.name] AS station_names, weight
    '''
    result = driver.execute_query(query, origin=origin, destination=destination)
    records = result[0]

    if not records:
        print(f"No path found from '{origin}' to '{destination}'.")
        return None

    path_info = []
    for record in records:
        station_names = record['station_names']
        total_distance = record['weight']
        hops = len(station_names) - 1
        path_info.append({
            'origin': origin,
            'destination': destination,
            'station_names': station_names,
            'path': ' → '.join(station_names),
            'total_distance': total_distance,
            'hops': hops
        })

    df = pd.DataFrame(path_info)
    print(f"Shortest path from '{origin}' to '{destination}':")
    print(df[['path', 'total_distance', 'hops']])

    #Enhancement for exporting output to HTML
    df.drop(columns=['station_names']).to_html('route_result.html', index=False)
    print("Results exported to 'route_result.html'.")

    plot_path(path_info[0]['station_names'])

    return df

#Visualization to plot the chosen route
def plot_path(station_names):
    plt.figure(figsize=(10, 2))
    plt.plot(range(len(station_names)), [1] * len(station_names), marker='o', color='tab:red')
    plt.xticks(range(len(station_names)), station_names, rotation=45, ha='right')
    plt.yticks([])
    plt.title('Shortest Path')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Route Planner")
    parser.add_argument("--origin", required=True, help="Origin station name")
    parser.add_argument("--destination", required=True, help="Destination station name")
    args = parser.parse_args()

    find_shortest_path(args.origin, args.destination)

#run example: python planner.py --origin "NEW DELHI" --destination "MUMBAI CST"

#you can choose any origin or destination stations that are present in the dataset
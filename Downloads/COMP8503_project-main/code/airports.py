import pandas as pd
from pathlib import Path
from model import Edge, Node

def get_airpors_data(d, assets_dir: Path):
    nodes_list = pd.read_csv(assets_dir / "airports-extended.csv")
    edges_list = pd.read_csv(assets_dir / "routes-preprocessed.csv")

    nodes = {}
    edges = []

    for _, row in nodes_list.iterrows():
        id = row['1']
        name = row['2']
        lat = row['7']
        long = row['8']
        nodes[id] = Node(id, long, lat, name)

    for _, row in edges_list.iterrows():
        source_id = row['source_id']
        dest_id = row['destination_id']
        if source_id not in nodes or dest_id not in nodes:
            continue

        edge = Edge(source_id, dest_id)
        source = nodes[source_id]
        dest = nodes[dest_id]
        distance = source.distance_to(dest)

        edge.distance = distance
        edge.weight = pow(distance, d)

        edges.append(edge)
        source.edges.append(edge)
        dest.edges.append(edge)

    to_remove = [node.id for node in nodes.values() if len(node.edges) == 0]
    for key in to_remove:
        del nodes[key]

    for node in nodes.values():
        node.edges.sort(key=lambda x: x.distance)

    edges.sort(key=lambda x: x.weight, reverse=True)
    return nodes, edges

import json
from pathlib import Path
from model import Edge, Node


def get_migrations_data(d, assets_dir: Path):
    f = open(assets_dir / 'migrations.json')
    data = json.load(f)

    nodes_list = data['nodes']
    edges_list = data['links']

    nodes = {}
    edges = []

    # Load nodes first to make membership checks cheap
    for node_entry in nodes_list:
        node_id = node_entry['id']
        n = Node(node_id, node_entry['x'], node_entry['y'], "")
        nodes[node_id] = n

    for edge_entry in edges_list:
        source_id = edge_entry['source']
        dest_id = edge_entry['target']
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

    # Eliminate nodes without edges
    to_remove = [node.id for node in nodes.values() if len(node.edges) == 0]
    for key in to_remove:
        del nodes[key]

    # Sort edges inside nodes in ascending order
    for node in nodes.values():
        node.edges.sort(key=lambda x: x.distance)

    # Sort edges
    edges.sort(key=lambda x: x.weight, reverse=True)

    f.close()
    return nodes, edges

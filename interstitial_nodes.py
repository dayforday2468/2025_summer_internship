import os
import osmnx as ox
import networkx as nx
from config import cities
from shapely.geometry import LineString


def delete_interstitial_node(G, node):
    neighbors = list(set(G.successors(node)) | set(G.predecessors(node)))
    if len(neighbors) != 2:
        return

    u, v = neighbors

    def extract_coords(a, b):
        if G.has_edge(a, b):
            edge_data = G.get_edge_data(a, b)
        elif G.has_edge(b, a):
            edge_data = G.get_edge_data(b, a)
        else:
            return None

        geom = edge_data[list(edge_data.keys())[0]].get("geometry", None)
        if geom:
            return list(geom.coords)
        else:
            return [
                (G.nodes[a]["x"], G.nodes[a]["y"]),
                (G.nodes[b]["x"], G.nodes[b]["y"]),
            ]

    # (1) u → node → v → u→v 간선 생성
    if G.has_edge(u, node) and G.has_edge(node, v):
        coords1 = extract_coords(u, node)
        coords2 = extract_coords(node, v)
        if coords1 and coords2:
            coords = coords1 + coords2[1:]
            G.add_edge(u, v, geometry=LineString(coords), simplified=True)

    # (2) v → node → u → v→u 간선 생성
    if G.has_edge(v, node) and G.has_edge(node, u):
        coords1 = extract_coords(v, node)
        coords2 = extract_coords(node, u)
        if coords1 and coords2:
            coords = coords1 + coords2[1:]
            G.add_edge(v, u, geometry=LineString(coords), simplified=True)

    # (3) 노드 제거
    G.remove_node(node)


def run_interstitial_nodes(input_stage, iteration):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "interstitial_nodes")
    os.makedirs(output_base, exist_ok=True)

    for city_name, _ in cities:
        print(f"Interstitial Nodes Processing {city_name}...")

        if input_stage == "data":
            input_path = os.path.join(input_base, f"{city_name}.graphml")
        else:
            input_path = os.path.join(
                input_base, city_name, f"{city_name}_{input_stage}_{iteration}.graphml"
            )
        G = ox.load_graphml(input_path)

        true_end_nodes = set()

        for node in G.nodes:
            neighbors = list(set(G.successors(node)) | set(G.predecessors(node)))
            degree = G.degree(node)
            in_deg = G.in_degree(node)
            out_deg = G.out_degree(node)

            if (node, node, 0) in G.edges(keys=True):
                true_end_nodes.add(node)
                continue
            elif in_deg == 0 or out_deg == 0:
                true_end_nodes.add(node)
                continue
            elif len(neighbors) == 1:
                true_end_nodes.add(node)
                continue
            elif len(neighbors) > 2:
                true_end_nodes.add(node)
                continue
            elif len(neighbors) == 2 and degree == 3:
                true_end_nodes.add(node)

        interstitial_nodes = [
            n
            for n in G.nodes
            if n not in true_end_nodes
            and len(list(set(G.successors(n)) | set(G.predecessors(n)))) == 2
        ]

        while True:
            deleted_any = False
            removed_nodes = []

            for node in interstitial_nodes:
                neighbors = list(set(G.successors(node)) | set(G.predecessors(node)))
                if any(n in true_end_nodes for n in neighbors):
                    delete_interstitial_node(G, node)
                    removed_nodes.append(node)
                    deleted_any = True

            interstitial_nodes = [
                n for n in interstitial_nodes if n not in removed_nodes
            ]

            if not deleted_any:
                break

        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)
        output_path = os.path.join(
            city_output_dir, f"{city_name}_interstitial_nodes_{iteration}.graphml"
        )
        ox.save_graphml(G, filepath=output_path)
        print(f"Saved to {output_path}")

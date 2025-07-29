import os
import osmnx as ox
from config import cities


def run_interstitial_nodes_view(input_stage):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, input_stage)
    output_dir = os.path.join(base_dir, "interstitial_nodes_view")
    os.makedirs(output_dir, exist_ok=True)

    for city_name, _ in cities:
        print(f"Interstitial Nodes View Processing {city_name}...")

        # 그래프 경로 설정
        if input_stage == "data":
            input_path = os.path.join(input_dir, f"{city_name}.graphml")
        else:
            input_path = os.path.join(
                input_dir, city_name, f"{city_name}_{input_stage}.graphml"
            )

        G = ox.load_graphml(input_path)

        true_end_nodes = set()

        for node in G.nodes:
            neighbors = list(set(G.successors(node)) | set(G.predecessors(node)))
            degree = G.degree(node)
            in_deg = G.in_degree(node)
            out_deg = G.out_degree(node)

            # 조건 1: self-loop
            if (node, node, 0) in G.edges(keys=True):
                true_end_nodes.add(node)
                continue

            # 조건 2: all in or all out
            if in_deg == 0 or out_deg == 0:
                true_end_nodes.add(node)
                continue

            # 조건 3: dead-end
            if len(neighbors) == 1:
                true_end_nodes.add(node)
                continue

            # 조건 4: intersection of >2
            if len(neighbors) > 2:
                true_end_nodes.add(node)
                continue

            # 조건 5: 2 neighbors but degree 3 (1-way to 2-way transition)
            if len(neighbors) == 2 and degree == 3:
                true_end_nodes.add(node)

        # 노드 색상 지정
        node_colors = ["black" if node in true_end_nodes else "red" for node in G.nodes]

        # 출력 디렉토리 및 경로 설정
        city_output_dir = os.path.join(output_dir, city_name)
        os.makedirs(city_output_dir, exist_ok=True)
        savepath = os.path.join(city_output_dir, f"{city_name}_interstitial_nodes.png")

        # 시각화 및 저장
        fig, ax = ox.plot_graph(
            G,
            node_color=node_colors,
            node_size=5,
            edge_color="gray",
            edge_linewidth=0.8,
            bgcolor="white",
            show=False,
            close=True,
            save=True,
            filepath=savepath,
            dpi=300,
        )

        print(f"Saved to {savepath}")

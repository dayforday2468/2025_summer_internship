import os
import osmnx as ox
from config import cities


def run_gridiron_view(input_stage, iteration):
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "gridiron_view")
    os.makedirs(output_base, exist_ok=True)

    for city_name, _ in cities:
        print(f"Gridiron View Processing {city_name}...")

        # 그래프 경로 설정
        if input_stage == "data":
            input_path = os.path.join(input_base, f"{city_name}.graphml")
        else:
            input_path = os.path.join(
                input_base, city_name, f"{city_name}_{input_stage}_{iteration}.graphml"
            )
        G = ox.load_graphml(input_path)

        grid_candidates = set()

        # (1)~(3) 조건 만족하는 노드 선별
        for node in G.nodes:
            neighbors = list(set(G.successors(node)) | set(G.predecessors(node)))
            if len(neighbors) != 4:
                continue

            incident_edges = G.edges(node, data=True)
            lengths = [
                edata.get("length", float("inf")) for _, _, edata in incident_edges
            ]
            highway_types = [
                edata.get("highway", None) for _, _, edata in incident_edges
            ]

            if max(lengths) >= 300:
                continue
            if not all(htype == "residential" for htype in highway_types):
                continue

            grid_candidates.add(node)

        # (4) 인접 노드 중 같은 조건 만족하는 노드가 2개 이상
        final_nodes = []
        for node in grid_candidates:
            count = sum(
                1
                for nbr in list(set(G.successors(node)) | set(G.predecessors(node)))
                if nbr in grid_candidates
            )
            if count >= 2:
                final_nodes.append(node)

        # 노드 색상 지정
        node_colors = ["red" if node in final_nodes else "black" for node in G.nodes]

        # 간선 색상 지정
        final_nodes_set = set(final_nodes)
        edge_colors = [
            "red" if u in final_nodes_set or v in final_nodes_set else "gray"
            for u, v, _ in G.edges(keys=True)
        ]

        # 저장 경로
        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)

        savepath = os.path.join(
            city_output_dir, f"{city_name}_gridiron_view_{iteration}.png"
        )

        fig, ax = ox.plot_graph(
            G,
            node_color=node_colors,
            node_size=3,
            edge_color=edge_colors,
            edge_linewidth=0.8,
            bgcolor="white",
            show=False,
            close=True,
            save=True,
            filepath=savepath,
            dpi=300,
        )

        print(f"Saved to {savepath}")

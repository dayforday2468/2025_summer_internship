import os
import osmnx as ox
from config import cities


def run_gridiron(input_stage, iteration):
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "gridiron")
    os.makedirs(output_base, exist_ok=True)

    for city_name, _ in cities:
        print(f"Gridiron Processing {city_name}...")

        # 그래프 불러오기
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
        final_nodes = set()
        for node in grid_candidates:
            count = sum(
                1
                for nbr in list(set(G.successors(node)) | set(G.predecessors(node)))
                if nbr in grid_candidates
            )
            if count >= 2:
                final_nodes.add(node)

        # 제거
        G.remove_nodes_from(final_nodes)

        # 저장
        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)

        output_path = os.path.join(
            city_output_dir, f"{city_name}_gridiron_{iteration}.graphml"
        )
        ox.save_graphml(G, filepath=output_path)

        print(f"Saved to {output_path}")

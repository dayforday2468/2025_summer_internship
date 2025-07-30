import os
import osmnx as ox
from config import cities


def run_dead_ends(input_stage, iteration):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "dead_ends")
    os.makedirs(output_base, exist_ok=True)

    for city_name, _ in cities:
        print(f"Dead-end Processing {city_name}...")

        # 입력 파일 경로
        if input_stage == "data":
            input_path = os.path.join(input_base, f"{city_name}.graphml")
        else:
            input_path = os.path.join(
                input_base, city_name, f"{city_name}_{input_stage}_{iteration}.graphml"
            )

        G = ox.load_graphml(input_path)

        # 제거 대상 노드: is_dead_end == 1
        dead_end_nodes = [
            n for n, data in G.nodes(data=True) if int(data.get("is_dead_end", 0)) == 1
        ]

        neighbor_candidates = set()
        for node in dead_end_nodes:
            neighbor_candidates.update(G.neighbors(node))

        # dead-end 노드 제거
        G.remove_nodes_from(dead_end_nodes)

        # 새로운 dead-end가 된 노드 업데이트
        for node in neighbor_candidates:
            if (
                node in G
                and len(list(set(G.successors(node)) | set(G.predecessors(node)))) == 1
            ):
                G.nodes[node]["is_dead_end"] = 1

        # 저장
        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)
        output_path = os.path.join(
            city_output_dir, f"{city_name}_dead_ends_{iteration}.graphml"
        )
        ox.save_graphml(G, filepath=output_path)
        print(f"Saved graph to {output_path}")

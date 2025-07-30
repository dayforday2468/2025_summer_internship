import os
import osmnx as ox
from config import cities


def run_parallel_edges(input_stage, iteration, is_first=False):
    # 디렉토리 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, input_stage)
    output_dir = os.path.join(script_dir, "parallel_edges")
    os.makedirs(output_dir, exist_ok=True)

    for city_name, _ in cities:
        print(f"Parallel Edges Processing {city_name}...")

        # 그래프 불러오기
        if input_stage == "data":
            graph_path = os.path.join(input_dir, f"{city_name}.graphml")
        else:
            graph_path = os.path.join(
                input_dir,
                city_name,
                f"{city_name}_{input_stage}_{iteration-1 if is_first else iteration}.graphml",
            )
        G = ox.load_graphml(graph_path)

        # 병렬 간선 중 가장 짧은 것만 남김
        edges_to_remove = []
        for u, v in G.edges():
            edge_dict = G.get_edge_data(u, v)
            if len(edge_dict) > 1:
                min_key = min(
                    edge_dict, key=lambda k: edge_dict[k].get("length", float("inf"))
                )
                for k in edge_dict:
                    if k != min_key:
                        edges_to_remove.append((u, v, k))

        # 병렬 간선 제거
        G.remove_edges_from(edges_to_remove)

        # 출력 경로 생성 및 저장
        city_output_dir = os.path.join(output_dir, city_name)
        os.makedirs(city_output_dir, exist_ok=True)
        output_path = os.path.join(
            city_output_dir, f"{city_name}_parallel_edges_{iteration}.graphml"
        )

        ox.save_graphml(G, filepath=output_path)
        print(f"Saved graph to {output_path}")

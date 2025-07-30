import os
import osmnx as ox
from config import cities


def run_self_loops(input_stage, iteration):
    # 디렉토리 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "self_loops")
    os.makedirs(output_base, exist_ok=True)

    # 각 도시별 self-loop 제거
    for city_name, _ in cities:
        print(f"Self-loop Processing {city_name}...")

        # 입력 파일 경로
        if input_stage == "data":
            graph_path = os.path.join(input_base, f"{city_name}.graphml")
        else:
            graph_path = os.path.join(
                input_base, city_name, f"{city_name}_{input_stage}_{iteration}.graphml"
            )
        G = ox.load_graphml(graph_path)

        # self-loop 간선 수집 및 제거
        edges_to_remove = [(u, v, k) for u, v, k in G.edges(keys=True) if u == v]
        G.remove_edges_from(edges_to_remove)

        # 출력 디렉토리 생성
        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)

        # 출력 파일 경로 (output_stage 반영)
        output_path = os.path.join(
            city_output_dir, f"{city_name}_self_loops_{iteration}.graphml"
        )
        ox.save_graphml(G, filepath=output_path)

        print(f"Saved graph to {output_path}")

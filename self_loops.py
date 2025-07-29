import os
import osmnx as ox
from config import cities


def run_self_loops(input_stage):
    # 디렉토리 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "self_loops")
    os.makedirs(output_base, exist_ok=True)

    # 각 도시별 self-loop 제거
    for name, _ in cities:
        print(f"Self-loop Processing {name}...")

        # 입력 파일 경로
        if input_stage == "data":
            graph_path = os.path.join(input_base, f"{name}.graphml")
        else:
            graph_path = os.path.join(input_base, name, f"{name}_{input_stage}.graphml")
        G = ox.load_graphml(graph_path)

        # self-loop 간선 수집 및 제거
        edges_to_remove = [(u, v, k) for u, v, k in G.edges(keys=True) if u == v]
        G.remove_edges_from(edges_to_remove)

        # 출력 디렉토리 생성
        city_output_dir = os.path.join(output_base, name)
        os.makedirs(city_output_dir, exist_ok=True)

        # 출력 파일 경로
        output_path = os.path.join(city_output_dir, f"{name}_self_loops.graphml")
        ox.save_graphml(G, filepath=output_path)

        print(f"Saved graph to {output_path}")

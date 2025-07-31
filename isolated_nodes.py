import os
import osmnx as ox
import networkx as nx
from config import cities


def run_isolated_nodes(input_stage, iteration):
    # 디렉토리 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "isolated_nodes")
    os.makedirs(output_base, exist_ok=True)

    for city_name, _ in cities:
        print(f"Isolated Nodes Processing {city_name}...")

        # 그래프 불러오기
        if input_stage == "data":
            input_path = os.path.join(input_base, f"{city_name}.graphml")
        else:
            input_path = os.path.join(
                input_base, city_name, f"{city_name}_{input_stage}_{iteration}.graphml"
            )
        G = ox.load_graphml(input_path)

        # ✅ 가장 큰 strongly connected component만 남김
        largest_cc = max(nx.strongly_connected_components(G), key=len)
        nodes_to_remove = set(G.nodes()) - largest_cc
        G.remove_nodes_from(nodes_to_remove)

        # 출력 디렉토리 생성
        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)

        output_path = os.path.join(
            city_output_dir, f"{city_name}_isolated_nodes_{iteration}.graphml"
        )

        # 저장
        ox.save_graphml(G, filepath=output_path)
        print(f"Saved to {output_path}")

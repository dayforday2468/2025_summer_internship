import os
import osmnx as ox
from config import cities


def run_isolated_nodes_view(input_stage, iteration):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, input_stage)
    output_dir = os.path.join(base_dir, "isolated_nodes_view")
    os.makedirs(output_dir, exist_ok=True)

    for city_name, _ in cities:
        print(f"Isolated Nodes View Processing {city_name}...")

        # 그래프 경로 설정
        if input_stage == "data":
            input_path = os.path.join(input_dir, f"{city_name}.graphml")
        else:
            input_path = os.path.join(
                input_dir, city_name, f"{city_name}_{input_stage}_{iteration}.graphml"
            )

        G = ox.load_graphml(input_path)

        # 고립 노드 탐지
        isolated_nodes = [
            n for n in G.nodes if G.in_degree(n) == 0 and G.out_degree(n) == 0
        ]

        # 노드 색상 지정
        node_colors = ["red" if node in isolated_nodes else "black" for node in G.nodes]

        # 출력 경로 설정
        city_output_dir = os.path.join(output_dir, city_name)
        os.makedirs(city_output_dir, exist_ok=True)
        savepath = os.path.join(
            city_output_dir, f"{city_name}_isolated_nodes_view_{iteration}.png"
        )

        # 시각화 및 저장
        fig, ax = ox.plot_graph(
            G,
            node_color=node_colors,
            node_size=3,
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

import os
import osmnx as ox
from config import cities


def run_dead_ends_view(input_stage):
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "dead_ends_view")
    os.makedirs(output_base, exist_ok=True)

    for city_name, _ in cities:
        print(f"Dead-end View Processing {city_name}...")

        # 그래프 불러오기
        if input_stage == "data":
            input_path = os.path.join(input_base, f"{city_name}.graphml")
        else:
            input_path = os.path.join(
                input_base, city_name, f"{city_name}_{input_stage}.graphml"
            )
        G = ox.load_graphml(input_path)

        # 노드 색상 지정: dead-end는 빨간색
        node_colors = [
            "red" if int(G.nodes[node].get("is_dead_end", 0)) == 1 else "black"
            for node in G.nodes
        ]

        # 출력 경로
        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)

        savepath = os.path.join(city_output_dir, f"{city_name}_deadends_view.png")

        # 저장
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

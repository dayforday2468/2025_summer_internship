import os
import osmnx as ox
from config import cities


def run_parallel_edges_view(input_stage):
    # 디렉토리 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, input_stage)
    output_dir = os.path.join(script_dir, "parallel_edges_view")
    os.makedirs(output_dir, exist_ok=True)

    # 병렬 간선 시각화
    for city_name, _ in cities:
        print(f"Parallel Edges View Processing {city_name}...")

        # 그래프 불러오기
        if input_stage == "data":
            graph_path = os.path.join(input_dir, f"{city_name}.graphml")
        else:
            graph_path = os.path.join(
                input_dir, city_name, f"{city_name}_{input_stage}.graphml"
            )

        G = ox.load_graphml(graph_path)

        # 병렬 간선이면 빨간색, 아니면 검정색
        edge_colors = [
            "red" if len(G.get_edge_data(u, v)) > 1 else "black" for u, v in G.edges()
        ]

        # 저장 경로
        city_output_dir = os.path.join(output_dir, city_name)
        os.makedirs(city_output_dir, exist_ok=True)
        savepath = os.path.join(city_output_dir, f"{city_name}_parallel_edges_view.png")

        # 저장
        fig, ax = ox.plot_graph(
            G,
            node_size=5,
            node_color="black",
            edge_color=edge_colors,
            edge_linewidth=0.8,
            bgcolor="white",
            show=False,
            close=True,
            save=True,
            filepath=savepath,
            dpi=300,
        )

        print(f"Saved Parallel Edges view to {savepath}")

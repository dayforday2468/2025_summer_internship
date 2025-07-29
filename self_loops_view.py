import os
import osmnx as ox
from config import cities


def run_self_loops_view(input_stage):
    # 디렉토리 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "self_loops_view")
    os.makedirs(output_base, exist_ok=True)

    # 각 도시별 self-loop 시각화
    for city_name, _ in cities:
        print(f"Self-loops View Processing {city_name}...")

        # 그래프 경로 설정
        if input_stage == "data":
            graph_path = os.path.join(input_base, f"{city_name}.graphml")
        else:
            graph_path = os.path.join(
                input_base,
                city_name,
                f"{city_name}_{input_stage}.graphml",
            )

        G = ox.load_graphml(graph_path)

        # 간선별 색상 지정 (self-loop는 빨간색)
        edge_colors = ["red" if u == v else "black" for u, v, k in G.edges(keys=True)]

        # 출력 경로
        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)

        savepath = os.path.join(city_output_dir, f"{city_name}_self_loops_view.png")

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

        print(f"Saved self-loops view to {savepath}")

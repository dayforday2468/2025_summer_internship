import os
import osmnx as ox
import matplotlib.pyplot as plt
from config import cities


def run_osm_view(input_stage):
    # 디렉토리 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, input_stage)
    output_dir = os.path.join(script_dir, "data_view")
    os.makedirs(output_dir, exist_ok=True)

    for name, _ in cities:
        # 그래프 파일 경로
        if input_stage == "data":
            graph_path = os.path.join(input_dir, f"{name}.graphml")
            savepath = os.path.join(output_dir, f"{name}_network_original.png")
        else:
            graph_path = os.path.join(input_dir, name, f"{name}_{input_stage}.graphml")
            savepath = os.path.join(output_dir, f"{name}_network_{input_stage}.png")

        # 그래프 불러오기
        G = ox.load_graphml(graph_path)

        # 그래프 저장
        ox.plot_graph(
            G,
            node_size=5,
            node_color="black",
            edge_color="black",
            edge_linewidth=0.8,
            bgcolor="white",
            save=True,
            filepath=savepath,
            dpi=300,
            show=False,
        )

        print(f"Saved {name} network to {savepath}")

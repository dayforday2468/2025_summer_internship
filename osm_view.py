import os
import osmnx as ox
import matplotlib.pyplot as plt
from config import cities
import networkx as nx
import random


def plot_strongly_connected_components(G, figsize=(12, 12), dpi=300):
    """
    방향 그래프 G의 strongly connected components를 색깔별로 시각화합니다.
    방향성까지 고려한 덩어리입니다.
    """
    components = list(nx.strongly_connected_components(G))
    print(f"Number of strongly connected components: {len(components)}")

    # 각 노드에 색 할당
    color_map = {}
    for comp in components:
        color = "#" + "".join(random.choices("0123456789ABCDEF", k=6))
        for node in comp:
            color_map[node] = color

    # 엣지별 색 지정 (출발 노드 기준 색상)
    edge_colors = [color_map.get(u, "#000000") for u, v in G.edges()]

    # 시각화
    ox.plot_graph(
        G,
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=1,
        bgcolor="white",
        show=True,
        close=True,
        figsize=figsize,
        dpi=dpi,
    )


def run_osm_view(input_stage, iteration):
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
            graph_path = os.path.join(
                input_dir, name, f"{name}_{input_stage}_{iteration}.graphml"
            )
            savepath = os.path.join(
                output_dir, f"{name}_network_{input_stage}_{iteration}.png"
            )

        # 그래프 불러오기
        G = ox.load_graphml(graph_path)

        plot_strongly_connected_components(G)

        # 그래프 저장
        ox.plot_graph(
            G,
            node_size=3,
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


run_osm_view("data", 0)
run_osm_view("isolated_nodes", 3)

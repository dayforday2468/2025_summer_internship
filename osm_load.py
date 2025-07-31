import os
import math
import osmnx as ox
import networkx as nx
from config import cities


def run_osm_load():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    for name, place in cities:
        print(f"Downloading {name} ...")

        # 원래 지도 다운로드
        G = ox.graph_from_place(place, network_type="drive")

        # 노드 좌표 기반 바운더리 계산
        xs = [data["x"] for _, data in G.nodes(data=True)]
        ys = [data["y"] for _, data in G.nodes(data=True)]

        west = min(xs)
        east = max(xs)
        south = min(ys)
        north = max(ys)

        # 중심 위도 기반 보정
        center_lat = (north + south) / 2
        lat_buffer = 1000 / 111000
        lon_buffer = 1000 / (111000 * math.cos(math.radians(center_lat)))

        north_big = north + lat_buffer
        south_big = south - lat_buffer
        east_big = east + lon_buffer
        west_big = west - lon_buffer

        # 큰 지도 다운로드
        G_big = ox.graph_from_bbox(
            (west_big, north_big, east_big, south_big), network_type="drive"
        )

        # dead-end 후보: 이웃 1개
        small_dead_ends = {
            n
            for n in G.nodes
            if len(list(set(G.successors(n)) | set(G.predecessors(n)))) == 1
        }
        big_dead_ends = {
            n
            for n in G_big.nodes
            if len(list(set(G_big.successors(n)) | set(G_big.predecessors(n)))) == 1
        }

        # 교집합 중에서 연결 길이가 500m 미만인 경우만 dead-end로 간주
        true_dead_ends = set()
        for node in small_dead_ends & big_dead_ends:
            neighbors = set(G.successors(node)) | set(G.predecessors(node))
            # 연결된 edge의 길이 가져오기
            edge_lengths = []
            for nbr in neighbors:
                for u, v in [(node, nbr), (nbr, node)]:
                    if G.has_edge(u, v):
                        edge_data_dict = G.get_edge_data(u, v, default={})
                        for attr in edge_data_dict.values():
                            try:
                                edge_lengths.append(float(attr.get("length", 0)))
                            except:
                                continue
            max_length = max(edge_lengths) if edge_lengths else 0
            if max_length < 500:
                true_dead_ends.add(node)

        # 모든 노드에 is_dead_end attribute 설정
        nx.set_node_attributes(G, 0, "is_dead_end")
        for node in true_dead_ends:
            G.nodes[node]["is_dead_end"] = 1

        # 저장
        savepath = os.path.join(data_dir, f"{name}.graphml")
        ox.save_graphml(G, filepath=savepath)
        print(f"Saved {name} to {savepath}")

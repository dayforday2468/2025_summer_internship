import os
import osmnx as ox
import geopandas as gpd
from config import cities
from shapely.geometry import Point, LineString


def run_make_osm_shape_file(input_stage, iteration):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(script_dir, input_stage)
    output_base = os.path.join(script_dir, "shape")
    os.makedirs(output_base, exist_ok=True)

    for city_name, _ in cities:
        print(f"Converting to Shapefile: {city_name}...")

        if input_stage == "data":
            input_path = os.path.join(input_base, f"{city_name}.graphml")
        else:
            input_path = os.path.join(
                input_base, city_name, f"{city_name}_{input_stage}_{iteration}.graphml"
            )

        G = ox.load_graphml(input_path)

        # GeoDataFrame으로 변환
        _, gdf_edges = ox.graph_to_gdfs(
            G, nodes=True, edges=True, node_geometry=True, fill_edge_geometry=True
        )

        # 출력 폴더 생성
        city_output_dir = os.path.join(output_base, city_name)
        os.makedirs(city_output_dir, exist_ok=True)

        # shapefile 저장
        edge_output_path = os.path.join(
            city_output_dir, f"{city_name}_{input_stage}_{iteration}_edges.shp"
        )

        gdf_edges.to_file(edge_output_path)

        print(f"Saved edge shapefile to {edge_output_path}")


def run_make_visum_shape_file(input_stage, iteration):

    print("Converting to Shapefile: Hwaseong...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    visum_base = os.path.join(script_dir, "VISUM")
    input_base = os.path.join(script_dir, input_stage, "Hwaseong")
    output_base = os.path.join(script_dir, "shape")
    os.makedirs(output_base, exist_ok=True)

    # VISUM 원본 shapefile 불러오기
    original_nodes = gpd.read_file(os.path.join(visum_base, "map_node.shp"))
    original_links = gpd.read_file(os.path.join(visum_base, "map_link.shp"))

    print(
        f"Original nodes: {len(original_nodes)}, Original links: {len(original_links)}"
    )

    # simplification 결과 graph 불러오기
    graph_path = os.path.join(input_base, f"Hwaseong_{input_stage}_{iteration}.graphml")
    G = ox.load_graphml(graph_path)

    # 초기 simplification된 노드/간선 목록
    simplified_nodes = set(int(n) for n in G.nodes())
    simplified_edges = set((int(u), int(v)) for u, v in G.edges())

    print(
        f"Simplified graph nodes: {len(simplified_nodes)}, edges: {len(simplified_edges)}"
    )

    # 좌표 기반 VISUM 노드 lookup table 생성
    visum_node_lookup = {
        (round(pt.x, 6), round(pt.y, 6)): int(node_id)
        for node_id, pt in zip(original_nodes["NO"], original_nodes.geometry)
    }

    # 간선 geometry로부터 추가 노드 및 엣지 추출
    for u, v in G.edges():
        data = G.get_edge_data(u, v)
        edge_info = data[list(data.keys())[0]]  # 첫 번째 edge 정보 사용
        geom = edge_info.get("geometry", None)

        if isinstance(geom, LineString):
            coords = list(geom.coords)

            for i in range(len(coords) - 1):
                pt1 = tuple(round(c, 6) for c in coords[i])
                pt2 = tuple(round(c, 6) for c in coords[i + 1])

                if pt1 in visum_node_lookup and pt2 in visum_node_lookup:
                    node1 = visum_node_lookup[pt1]
                    node2 = visum_node_lookup[pt2]

                    simplified_nodes.add(node1)
                    simplified_nodes.add(node2)
                    simplified_edges.add((node1, node2))

    print(f"Augmented nodes: {len(simplified_nodes)}, edges: {len(simplified_edges)}")

    # 노드 필터링
    filtered_nodes = original_nodes[
        original_nodes["NO"].astype(int).isin(simplified_nodes)
    ]

    # 엣지 필터링
    def edge_in_simplified(row):
        u = int(row["FROMNODENO"])
        v = int(row["TONODENO"])
        return (u, v) in simplified_edges or (v, u) in simplified_edges

    filtered_links = original_links[original_links.apply(edge_in_simplified, axis=1)]
    print(f"Filtered nodes: {len(filtered_nodes)}, edges: {len(filtered_links)}")

    # 출력 경로
    city_output_dir = os.path.join(output_base, "Hwaseong")
    os.makedirs(city_output_dir, exist_ok=True)

    nodes_output_path = os.path.join(
        city_output_dir, f"Hwaseong_{input_stage}_{iteration}_nodes.shp"
    )
    edges_output_path = os.path.join(
        city_output_dir, f"Hwaseong_{input_stage}_{iteration}_edges.shp"
    )

    # 저장
    filtered_nodes.to_file(nodes_output_path)
    filtered_links.to_file(edges_output_path)

    print(f"Saved filtered VISUM node shapefile to: {nodes_output_path}")
    print(f"Saved filtered VISUM edge shapefile to: {edges_output_path}")

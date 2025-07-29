import os
import osmnx as ox
import geopandas as gpd
from config import cities


def run_make_shape_file(input_stage):
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
                input_base, city_name, f"{city_name}_{input_stage}.graphml"
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
            city_output_dir, f"{city_name}_{input_stage}_edges.shp"
        )

        gdf_edges.to_file(edge_output_path)

        print(f"Saved edge shapefile to {edge_output_path}")


run_make_shape_file("isolated_nodes")

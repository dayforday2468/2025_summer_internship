import os
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt


# ✅ TYPENO to highway type 매핑
def map_typeno_to_highway(typeno):
    if typeno in [0, 1, 2, 3, 4, 5, 17]:
        return "motorway"
    elif typeno in [6, 7]:
        return "trunk"
    elif typeno in range(8, 30):
        return "residential"
    elif typeno == 16:
        return "service"
    elif typeno in [30, 31, 32, 33, 34]:
        return "road"
    else:
        return "unclassified"


def load_shp_to_graph(links_path, nodes_path):
    G = nx.MultiDiGraph()
    node_positions = {}

    gdf_nodes = gpd.read_file(nodes_path)
    for _, row in gdf_nodes.iterrows():
        node_id = str(row["NO"])
        x = float(row["XCOORD"])
        y = float(row["YCOORD"])
        point = Point(x, y)
        G.add_node(node_id, geometry=point, x=x, y=y)
        node_positions[node_id] = (x, y)

    gdf_links = gpd.read_file(links_path)

    # # ✅ CAPPRT가 0인 도로는 제거
    # gdf_links = gdf_links[gdf_links["CAPPRT"] > 0]

    for _, row in gdf_links.iterrows():
        u = str(row.get("FROMNODENO"))
        v = str(row.get("TONODENO"))

        if u not in node_positions or v not in node_positions:
            continue
        start_point = node_positions[u]
        end_point = node_positions[v]
        geom = LineString([start_point, end_point])

        # ✅ 길이 변환 (예: "0.160km" → 160.0)
        length_str = row.get("LENGTH", "0km")
        try:
            length = float(str(length_str).replace("km", "").strip()) * 1000
        except:
            length = None

        # ✅ highway 타입 변환
        typeno = row.get("TYPENO", -1)
        try:
            typeno = int(typeno)
        except:
            typeno = -1
        highway = map_typeno_to_highway(typeno)

        G.add_edge(u, v, geometry=geom, length=length, highway=highway)

    G.graph["crs"] = gdf_nodes.crs.to_string()

    # ✅ 추가된 부분: dead-end 탐지
    nx.set_node_attributes(G, str(0), "is_dead_end")
    for node in G.nodes:
        neighbors = set(G.successors(node)) | set(G.predecessors(node))
        if len(neighbors) == 1:
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
                G.nodes[node]["is_dead_end"] = str(1)

    return G


def save_graph_to_graphml(G, output_path):
    import copy
    from shapely.geometry import Point, LineString

    G_copy = copy.deepcopy(G)

    for node, data in G_copy.nodes(data=True):
        # x, y를 문자열로 저장
        if "x" in data and "y" in data:
            data["x"] = str(data["x"])
            data["y"] = str(data["y"])

        # geometry를 WKT 문자열로 저장
        geom = data.get("geometry")
        if isinstance(geom, Point):
            data["geometry"] = geom.wkt

    for u, v, data in G_copy.edges(data=True):
        # geometry를 WKT 문자열로 저장
        geom = data.get("geometry")
        if isinstance(geom, LineString):
            data["geometry"] = geom.wkt

        # ✅ length와 highway도 문자열로 저장
        if "length" in data:
            data["length"] = str(data["length"])
        if "highway" in data:
            data["highway"] = str(data["highway"])

    nx.write_graphml(G_copy, output_path)
    print(f"Graph saved to: {output_path}")


def run_shp_load():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    input_dir = os.path.join(script_dir, "VISUM")
    os.makedirs(data_dir, exist_ok=True)

    links_path = os.path.join(input_dir, "map_link.shp")
    nodes_path = os.path.join(input_dir, "map_node.shp")
    output_path = os.path.join(data_dir, "Hwaseong.graphml")

    print("Loading VISUM shapefiles...")
    G = load_shp_to_graph(links_path, nodes_path)
    save_graph_to_graphml(G, output_path)
    print("Shapefile graph successfully saved.")

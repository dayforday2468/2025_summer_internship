import os
import shutil

from osm_load import run_osm_load
from shp_load import run_shp_load
from osm_view import run_osm_view
from parallel_edges import run_parallel_edges
from parallel_edges_view import run_parallel_edges_view
from self_loops import run_self_loops
from self_loops_view import run_self_loops_view
from dead_ends import run_dead_ends
from dead_ends_view import run_dead_ends_view
from gridiron import run_gridiron
from gridiron_view import run_gridiron_view
from isolated_nodes import run_isolated_nodes
from isolated_nodes_view import run_isolated_nodes_view
from interstitial_nodes import run_interstitial_nodes
from interstitial_nodes_view import run_interstitial_nodes_view
from make_shape_file import run_make_shape_file
from report import run_report


# 초기화
def initialize():
    print("Initializing project...")

    folders_to_delete = [
        "data",
        "data_view",
        "parallel_edges",
        "parallel_edges_view",
        "self_loops",
        "self_loops_view",
        "dead_ends",
        "dead_ends_view",
        "gridiron",
        "gridiron_view",
        "isolated_nodes",
        "isolated_nodes_view",
        "interstitial_nodes",
        "interstitial_nodes_view",
        "shape",
        "report",
    ]

    for folder in folders_to_delete:
        folder_path = os.path.join(os.path.dirname(__file__), folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Deleted: {folder_path}")

    print("Initialization complete.")


# 파이프라인 실행
def run_pipeline(source):
    if source == "osm":
        run_osm_load()
    elif source == "visum":
        run_shp_load()
    run_osm_view("data", 0)

    for i in range(1, 4):
        print(f"\nIteration: {i}")
        if i == 1:
            run_parallel_edges("data", i)
            run_parallel_edges_view("data", i)
        else:
            run_parallel_edges("interstitial_nodes", i, True)
            run_parallel_edges_view("interstitial_nodes", i, True)

        run_self_loops("parallel_edges", i)
        run_self_loops_view("parallel_edges", i)

        run_dead_ends("self_loops", i)
        run_dead_ends_view("self_loops", i)

        run_gridiron("dead_ends", i)
        run_gridiron_view("dead_ends", i)

        run_interstitial_nodes("gridiron", i)
        run_interstitial_nodes_view("gridiron", i)

    run_isolated_nodes("interstitial_nodes", 3)
    run_isolated_nodes_view("interstitial_nodes", 3)

    run_osm_view("isolated_nodes", 3)
    run_make_shape_file("isolated_nodes", 3)
    run_report("isolated_nodes", 3)
    print("Pipeline complete.")


if __name__ == "__main__":
    initialize()
    run_pipeline("visum")

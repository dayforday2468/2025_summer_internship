import os
import shutil

from osm_load import run_osm_load
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
    ]

    for folder in folders_to_delete:
        folder_path = os.path.join(os.path.dirname(__file__), folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Deleted: {folder_path}")

    print("Initialization complete.")


# 파이프라인 실행
def run_pipeline():
    run_osm_load()
    run_osm_view("data")

    run_parallel_edges("data")
    run_parallel_edges_view("data")

    run_interstitial_nodes("parallel_edges")
    run_interstitial_nodes_view("parallel_edges")

    run_self_loops("interstitial_nodes")
    run_self_loops_view("interstitial_nodes")

    run_dead_ends("self_loops")
    run_dead_ends_view("self_loops")

    run_gridiron("dead_ends")
    run_gridiron_view("dead_ends")

    run_isolated_nodes("gridiron")
    run_isolated_nodes_view("gridiron")

    run_osm_view("isolated_nodes")
    run_make_shape_file("isolated_nodes")
    print("Pipeline complete. Final graph saved.")


if __name__ == "__main__":
    initialize()
    run_pipeline()

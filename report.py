import os
import osmnx as ox
from config import cities


def run_report(input_stage, iteration):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_base = os.path.join(script_dir, "data")
    simplified_base = os.path.join(script_dir, input_stage)
    stats_base = os.path.join(script_dir, "report")
    os.makedirs(stats_base, exist_ok=True)

    for city_name, _ in cities:
        print(f"📊 Processing: {city_name}...")

        # 경로 설정
        original_path = os.path.join(data_base, f"{city_name}.graphml")
        simplified_path = os.path.join(
            simplified_base, city_name, f"{city_name}_{input_stage}_{iteration}.graphml"
        )

        # 그래프 불러오기
        G_original = ox.load_graphml(original_path)
        G_simplified = ox.load_graphml(simplified_path)

        # 노드/엣지 수 계산
        orig_nodes, orig_edges = len(G_original.nodes), len(G_original.edges)
        simp_nodes, simp_edges = len(G_simplified.nodes), len(G_simplified.edges)

        # 결과 작성
        result_text = (
            f"City: {city_name}\n"
            f"Original Graph:   {orig_nodes} nodes, {orig_edges} edges\n"
            f"Simplified Graph: {simp_nodes} nodes, {simp_edges} edges\n"
            f"Node reduction:   {orig_nodes - simp_nodes} ({(orig_nodes - simp_nodes) / orig_nodes:.1%})\n"
            f"Edge reduction:   {orig_edges - simp_edges} ({(orig_edges - simp_edges) / orig_edges:.1%})\n"
        )

        # 텍스트 파일 저장
        stats_path = os.path.join(stats_base, f"{city_name}_report.txt")
        with open(stats_path, "w", encoding="utf-8") as f:
            f.write(result_text)

        print(f"✅ Saved: {stats_path}")

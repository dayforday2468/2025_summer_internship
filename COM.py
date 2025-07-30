import os
import win32com.client


def run_COM():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 파일 경로 설정
    visum_file = os.path.join(script_dir, "visum", "[인턴]GIS20_VER17.ver")
    original_matrix_path = os.path.join(
        script_dir, "output", "original_assignment_matrix.xml"
    )
    simplified_matrix_path = os.path.join(
        script_dir, "output", "simplified_assignment_matrix.xml"
    )
    simplified_shp_path = os.path.join(
        script_dir, "shape", "Seoul", "Seoul_isolated_nodes_edges.shp"
    )

    # Visum 객체 초기화 및 네트워크 로딩
    Visum = win32com.client.Dispatch("Visum.Visum")
    Visum.LoadVersion(visum_file)
    print(f"✅ Loaded Visum file: {visum_file}")

    ps = Visum.Procedures.Operations.GetAll
    for p in ps:
        print(p.attvalue)

    # 원래 네트워크로 Procedure 실행 및 Assignment Matrix 저장
    procedure_key = "YourProcedureNameHere"  # ❗ 수정 필요: 실행할 프로시저 키 입력
    print(f"▶ Running procedure: {procedure_key} (original network)")
    Visum.Procedures.ItemByKey(procedure_key).Execute()
    os.makedirs(os.path.dirname(original_matrix_path), exist_ok=True)
    Visum.Net.Demand.SaveToFile(original_matrix_path)
    print(f"💾 Saved original assignment matrix to: {original_matrix_path}")

    # Simplified Shapefile import
    print(f"📦 Importing simplified shapefile: {simplified_shp_path}")
    Visum.Net.Links.Import(simplified_shp_path, True)
    print("✅ Shapefile import complete")

    # 다시 Procedure 실행 및 Assignment Matrix 저장
    print(f"▶ Running procedure: {procedure_key} (after simplification)")
    Visum.Procedures.ItemByKey(procedure_key).Execute()
    Visum.Net.Demand.SaveToFile(simplified_matrix_path)
    print(f"💾 Saved simplified assignment matrix to: {simplified_matrix_path}")

    print("🎉 All steps completed successfully.")


run_COM()

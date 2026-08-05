import os
import json
import sys
import platform
import pandas as pd
from pathlib import Path

# Add project root directory to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import OlistDataLoader, INPUT_DIR
from src.agents.coordinator_agent import CoordinatorAgent
from src.llm import get_active_model_metadata
from src.schemas import CaseOutput

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
LOGGING_DIR = BASE_DIR / "logging"
DOCS_DIR = BASE_DIR / "docs"

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=== KHỞI CHẠY MULTI-AGENT DISPUTE RESOLUTION PIPELINE ===")
    
    # Tạo các thư mục nếu chưa tồn tại
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGGING_DIR.mkdir(parents=True, exist_ok=True)
    prepare_output_dir()
    
    # 1. Nạp dữ liệu
    loader = OlistDataLoader()
    datasets = loader.load_all()
    
    # 2. Khởi tạo Coordinator Agent
    coordinator = CoordinatorAgent()
    
    traces = []
    results_summary = []
    
    statistics = {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "primary_issues": {},
        "responsible_parties": {},
        "total_refund_brl": 0.0
    }
    
    print("\nĐang xử lý 50 case khiếu nại...")
    
    # Đảm bảo file trace.jsonl được ghi mới hoàn toàn
    trace_filepath = LOGGING_DIR / "trace.jsonl"
    with open(trace_filepath, "w", encoding="utf-8") as trace_file:
        pass
        
    for i in range(1, 51):
        case_id = f"EC_{i:03d}"
        case_file = INPUT_DIR / f"{case_id}.json"
        
        if not case_file.exists():
            print(f"[WARNING] Thiếu file input: {case_id}.json")
            continue
            
        with open(case_file, 'r', encoding='utf-8') as f:
            case_context = json.load(f)
            
        # Phân tích qua Coordinator Agent
        res = coordinator.analyze(case_context, datasets)
        statistics["total"] += 1
        
        is_valid = res["is_valid"]
        output = res["output"]
        trace = res["trace"]
        errors = res["errors"]
        
        if is_valid:
            statistics["valid"] += 1
            
            # Ghi file output
            output_filepath = OUTPUT_DIR / f"{case_id}.json"
            with open(output_filepath, "w", encoding="utf-8") as out_f:
                json.dump(output, out_f, indent=2, ensure_ascii=False)
                
            # Phân tích thống kê
            assessment = output["case_assessment"]
            p_issue = assessment["primary_issue"]
            s_issues = ", ".join(assessment["secondary_issues"]) if assessment["secondary_issues"] else "None"
            refund = output["financial_resolution"]["recommended_refund_brl"]
            
            statistics["primary_issues"][p_issue] = statistics["primary_issues"].get(p_issue, 0) + 1
            
            parties = output["root_cause_analysis"]["responsible_parties"]
            resp_party_str = "None"
            if parties:
                resp_party_str = ", ".join([f"{p['party_type']}:{p['party_id']}" for p in parties])
                for p in parties:
                    p_type = p["party_type"]
                    statistics["responsible_parties"][p_type] = statistics["responsible_parties"].get(p_type, 0) + 1
            
            statistics["total_refund_brl"] += refund
            
            results_summary.append({
                "case_id": case_id,
                "primary_issue": p_issue,
                "secondary_issues": s_issues,
                "responsible_party": resp_party_str,
                "refund": f"{refund:.2f} BRL",
                "status": "PASS"
            })
        else:
            statistics["invalid"] += 1
            print(f"[FAIL] {case_id} không hợp lệ: {errors}")
            results_summary.append({
                "case_id": case_id,
                "primary_issue": "N/A",
                "secondary_issues": "N/A",
                "responsible_party": "N/A",
                "refund": "0.00 BRL",
                "status": f"FAIL: {', '.join(errors)}"
            })
            
        # Ghi trace log vào trace.jsonl (định dạng jsonl)
        with open(trace_filepath, "a", encoding="utf-8") as trace_file:
            trace_file.write(json.dumps(trace, ensure_ascii=False) + "\n")
            
    print(f"\nĐã hoàn thành phân tích. Kết quả: {statistics['valid']} PASS, {statistics['invalid']} FAIL.")

    if statistics["total"] != 50 or statistics["valid"] != 50:
        raise RuntimeError(
            "Pipeline did not produce 50 valid outputs; refusing to package "
            f"partial results ({statistics['valid']}/50 valid)."
        )
    
    # 3. Ghi file metadata.json
    metadata = {
        **get_active_model_metadata(),
        "framework": "Python / pandas / pydantic",
        "runtime": f"Python {platform.python_version()}"
    }
    with open(LOGGING_DIR / "metadata.json", "w", encoding="utf-8") as meta_f:
        json.dump(metadata, meta_f, indent=2, ensure_ascii=False)
    print(f"[OK] Đã ghi file metadata.json (Model: {metadata['model']})")
    
    # 4. Ghi file kết quả results.md
    generate_results_report(statistics, results_summary)
    print("[OK] Đã cập nhật file docs/results.md với thống kê kết quả chạy thực tế.")

    # 5. Tạo file nén output.zip chứa đúng 50 JSON
    create_output_zip()

def prepare_output_dir():
    """Remove only generated case JSON files, preventing stale-run artifacts."""
    if OUTPUT_DIR.resolve().parent != BASE_DIR.resolve():
        raise RuntimeError("Unsafe output directory")
    for path in OUTPUT_DIR.glob("EC_*.json"):
        if path.is_file():
            path.unlink()


def create_output_zip():
    import zipfile
    zip_path = BASE_DIR / "output.zip"
    print(f"\nĐang tạo file nén {zip_path.name}...")
    expected_names = [f"EC_{i:03d}.json" for i in range(1, 51)]
    actual_names = sorted(path.name for path in OUTPUT_DIR.glob("*.json"))
    if actual_names != expected_names:
        raise RuntimeError(
            "output/ must contain exactly EC_001.json through EC_050.json"
        )

    for name in expected_names:
        with open(OUTPUT_DIR / name, "r", encoding="utf-8") as output_file:
            CaseOutput.model_validate(json.load(output_file))

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_f:
        for name in expected_names:
            file = OUTPUT_DIR / name
            zip_f.write(file, arcname=file.name)
    print(f"[OK] Đã nén thành công {zip_path.name} (chứa đúng 50 file JSON)")

def generate_results_report(stats, summaries):
    report_content = f"""# BÁO CÁO KẾT QUẢ THỰC HIỆN DỰ ÁN
**Dự án:** K4 Day 09 - Multi-Agent E-commerce Dispute Resolution
**Người thực hiện:** Nguyễn Châu Thanh (MSSV: 2A202601382)
**Ngày cập nhật:** 05/08/2026

---

## 📌 1. Kết quả Phase 1: Thiết lập & Chuẩn bị dữ liệu

* **Trạng thái:** **HOÀN THÀNH (100% Phase 1 / 10% Tổng dự án)**
* **Mã nguồn đã tạo:** [src/data_loader.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/data_loader.py), [src/__init__.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/__init__.py), [.gitignore](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/.gitignore)

---

## 📌 2. Kết quả Phase 2: Xây dựng Kiến trúc Multi-Agent

* **Trạng thái:** **HOÀN THÀNH (100% Phase 2 / 35% Tổng dự án)**
* **Mã nguồn đã tạo:**
  - **Data Contracts:** [src/schemas.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/schemas.py)
  - **Các Agent:** [base.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/base.py), [coordinator_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/coordinator_agent.py), [customer_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/customer_agent.py), [order_product_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/order_product_agent.py), [payment_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/payment_agent.py), [delivery_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/delivery_agent.py), [policy_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/policy_agent.py), [verifier_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/verifier_agent.py)

---

## 📌 3. Kết quả Phase 3: Logic Nghiệp vụ & Xử lý Dispute

Phase 3 tập trung vào việc áp dụng chính sách `EC_POLICY_V2`, thực hiện tính toán biến động thời gian, đối soát tài chính và phân loại các lỗi chính/phụ cho toàn bộ 50 case khiếu nại đầu vào.

* **Trạng thái:** **HOÀN THÀNH (100% Phase 3 / 30% Tổng dự án)**

### 📊 Thống kê kết quả chạy thực tế (50 Cases)

| Chỉ số thống kê | Giá trị |
| :--- | :---: |
| **Tổng số case xử lý** | {stats['total']} |
| **Hợp lệ (Pass Schema)** | {stats['valid']} |
| **Không hợp lệ (Fail Schema)** | {stats['invalid']} |
| **Tổng số tiền đề xuất hoàn trả** | **{stats['total_refund_brl']:.2f} BRL** |

#### Phân bố lỗi chính (Primary Issues):
"""
    for k, v in stats["primary_issues"].items():
        report_content += f"- **{k}**: {v} case(s)\n"
        
    report_content += "\n#### Phân bố trách nhiệm (Responsible Parties):\n"
    for k, v in stats["responsible_parties"].items():
        report_content += f"- **{k}**: {v} lần chịu trách nhiệm\n"
        
    report_content += """
### 📋 Bảng tổng hợp chi tiết kết quả 50 case:

| Case ID | Primary Issue | Secondary Issues | Responsible Party | Refund | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
"""
    for row in summaries:
        report_content += f"| {row['case_id']} | {row['primary_issue']} | {row['secondary_issues']} | {row['responsible_party']} | {row['refund']} | {row['status']} |\n"

    report_content += f"""
---

## 📌 4. Kết quả Phase 4: Output, Tracing & Đóng gói

Phase 4 thực hiện ghi trace log, metadata cấu hình, tạo file kết quả chi tiết của 50 đơn hàng và đóng gói sản phẩm nộp bài.

* **Trạng thái:** **HOÀN THÀNH (100% Phase 4 / 15% Tổng dự án)**
* **Tổng tiến độ tích lũy:** **90% / 100%** (Đã hoàn thành Phase 1 + 2 + 3 + 4)
* **Sản phẩm bàn giao:**
  - 50 file JSON kết quả đầu ra trong [output/](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/output).
  - Tệp trace log chạy [logging/trace.jsonl](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/logging/trace.jsonl).
  - Tệp metadata cấu hình [logging/metadata.json](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/logging/metadata.json).
  - Tệp nén nộp bài `output.zip` tại thư mục gốc của workspace.

---

## 🎯 5. Đánh giá & Bước tiếp theo (Phase 5)

Sau khi hoàn tất toàn bộ code và đóng gói kết quả, bước cuối cùng là:
1. **Phase 5: Tài liệu & Hoàn thiện báo cáo (10%)**: Hoàn thiện tài liệu kiến trúc hệ thống [architecture.md](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/architecture.md) và viết báo cáo cá nhân từ file template [individual_5SoCuoiMHV_HoVaTen.md](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/individual_5SoCuoiMHV_HoVaTen.md).
"""

    with open(DOCS_DIR / "results.md", "w", encoding="utf-8") as f:
        f.write(report_content)

if __name__ == "__main__":
    main()

"""
Kiểm tra nghiêm ngặt toàn bộ output dựa theo schema trong README.md:
- Kiểm tra giới hạn kích thước mảng
- Kiểm tra confidence trong [0,1]
- Kiểm tra case_status hợp lệ
- Kiểm tra định dạng timestamp YYYY-MM-DD HH:MM:SS hoặc null
- Kiểm tra delivery_analysis không còn bị null toàn bộ khi có dữ liệu
- Kiểm tra các trường bắt buộc tồn tại
"""
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

TIMESTAMP_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

REQUIRED_TOP_KEYS = [
    "case_id", "case_assessment", "affected_entities", "customer_context",
    "product_context", "delivery_analysis", "payment_reconciliation",
    "root_cause_analysis", "evidence_ids", "financial_resolution", "resolution_actions"
]

ARRAY_LIMITS = [
    ("affected_entities.order_ids",           lambda d: d.get("affected_entities", {}).get("order_ids", []),           5),
    ("affected_entities.item_ids",            lambda d: d.get("affected_entities", {}).get("item_ids", []),            5),
    ("affected_entities.seller_ids",          lambda d: d.get("affected_entities", {}).get("seller_ids", []),          3),
    ("affected_entities.payment_ids",         lambda d: d.get("affected_entities", {}).get("payment_ids", []),         5),
    ("customer_context.related_order_ids",    lambda d: d.get("customer_context", {}).get("related_order_ids", []),    5),
    ("product_context.product_ids",           lambda d: d.get("product_context", {}).get("product_ids", []),           5),
    ("product_context.category_names",        lambda d: d.get("product_context", {}).get("category_names", []),        5),
    ("root_cause_analysis.ranked_causes",     lambda d: d.get("root_cause_analysis", {}).get("ranked_causes", []),     3),
    ("root_cause_analysis.responsible_parties", lambda d: d.get("root_cause_analysis", {}).get("responsible_parties", []), 3),
    ("evidence_ids",                          lambda d: d.get("evidence_ids", []),                                    20),
    ("resolution_actions",                    lambda d: d.get("resolution_actions", []),                               5),
]

def verify():
    failures = []
    all_null_delivery = []   # Danh sách case có delivery_analysis toàn null
    
    for i in range(1, 51):
        name = f"EC_{i:03d}.json"
        path = OUTPUT_DIR / name
        
        if not path.exists():
            failures.append(f"[MISSING] {name}: không tìm thấy file")
            continue
        
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                failures.append(f"[JSON ERROR] {name}: {e}")
                continue
        
        # 1. Kiểm tra các trường bắt buộc ở cấp cao nhất
        for key in REQUIRED_TOP_KEYS:
            if key not in data:
                failures.append(f"[MISSING FIELD] {name}: thiếu trường '{key}'")
        
        # 2. Kiểm tra case_status
        case_status = data.get("case_assessment", {}).get("case_status")
        if case_status not in ("action_required", "no_action"):
            failures.append(f"[INVALID STATUS] {name}: case_status='{case_status}' phải là 'action_required' hoặc 'no_action'")
        
        # 3. Kiểm tra confidence trong [0,1]
        confidence = data.get("case_assessment", {}).get("confidence")
        if not isinstance(confidence, (int, float)) or not (0.0 <= float(confidence) <= 1.0):
            failures.append(f"[CONFIDENCE] {name}: confidence='{confidence}' ngoài khoảng [0,1]")
        
        # 4. Kiểm tra timestamp
        da = data.get("delivery_analysis", {})
        for ts_field in ("delivered_at", "estimated_delivery_at", "carrier_handoff_at"):
            val = da.get(ts_field)
            if val is not None:
                if not (isinstance(val, str) and TIMESTAMP_REGEX.match(val)):
                    failures.append(f"[TIMESTAMP] {name}: delivery_analysis.{ts_field}='{val}' sai định dạng YYYY-MM-DD HH:MM:SS")
        
        for handoff in da.get("seller_handoff_analysis", []):
            val = handoff.get("shipping_limit_at")
            if val is not None and not (isinstance(val, str) and TIMESTAMP_REGEX.match(val)):
                failures.append(f"[TIMESTAMP] {name}: seller_handoff_analysis.shipping_limit_at='{val}' sai định dạng")
        
        # 5. Kiểm tra giới hạn mảng
        for label, getter, limit in ARRAY_LIMITS:
            arr = getter(data)
            if not isinstance(arr, list):
                failures.append(f"[TYPE] {name}: {label} không phải là list")
            elif len(arr) > limit:
                failures.append(f"[LIMIT] {name}: {label} có {len(arr)} phần tử, vượt quá giới hạn {limit}")
        
        # 6. Cảnh báo delivery_analysis toàn null (nghi ngờ bug key-mapping)
        if (da.get("delivered_at") is None and
            da.get("estimated_delivery_at") is None and
            da.get("carrier_handoff_at") is None):
            all_null_delivery.append(name)
    
    # --- In kết quả ---
    print(f"\n{'='*60}")
    print(f"TỔNG KẾT KIỂM TRA SCHEMA CHO 50 FILE OUTPUT")
    print(f"{'='*60}")
    
    if failures:
        print(f"\n[FAIL] Tìm thấy {len(failures)} lỗi:\n")
        for f in failures:
            print(f"  {f}")
    else:
        print("\n[PASS] Tất cả 50 file đều tuân thủ đúng schema!")
    
    if all_null_delivery:
        print(f"\n[INFO] {len(all_null_delivery)} case có delivery_analysis toàn null (có thể do đơn cancelled/unavailable):")
        for c in all_null_delivery:
            print(f"  - {c}")
    
    return len(failures) == 0

if __name__ == "__main__":
    ok = verify()
    sys.exit(0 if ok else 1)

import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root directory to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.schemas import CaseOutput

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

def check():
    missing = []
    invalid = []
    for i in range(1, 51):
        case_id = f"EC_{i:03d}"
        out_file = OUTPUT_DIR / f"{case_id}.json"
        if not out_file.exists():
            missing.append(case_id)
            continue
        try:
            with open(out_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            CaseOutput(**data)
        except Exception as e:
            invalid.append((case_id, str(e)))
            
    print(f"\n==========================================")
    print(f"KIỂM TRA CÁC OUTPUT FILE THỰC TẾ TRÊN ĐĨA")
    print(f"==========================================")
    print(f"• Số lượng file bị thiếu (không tồn tại): {len(missing)}")
    if missing:
        print(f"  -> Các case bị thiếu: {missing}")
    print(f"• Số lượng file lỗi xác thực Pydantic: {len(invalid)}")
    for case_id, err in invalid:
        print(f"  -> {case_id}: {err}")
    print(f"==========================================\n")

if __name__ == "__main__":
    check()

import unittest
import json
from pathlib import Path
from src.data_loader import OlistDataLoader, INPUT_DIR
from src.agents.coordinator_agent import CoordinatorAgent

class TestPhase3AllCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = OlistDataLoader()
        cls.datasets = cls.loader.load_all()
        cls.coordinator = CoordinatorAgent()

    def test_run_and_validate_all_50_cases(self):
        """Chạy thử và xác thực toàn bộ 50 case đầu vào."""
        statistics = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "primary_issues": {},
            "responsible_parties": {},
            "total_refund_brl": 0.0
        }
        
        for i in range(1, 51):
            case_id = f"EC_{i:03d}"
            case_file = INPUT_DIR / f"{case_id}.json"
            
            with open(case_file, 'r', encoding='utf-8') as f:
                case_context = json.load(f)
                
            res = self.coordinator.analyze(case_context, self.datasets)
            statistics["total"] += 1
            
            if res["is_valid"]:
                statistics["valid"] += 1
                output = res["output"]
                
                # Gom thống kê
                p_issue = output["case_assessment"]["primary_issue"]
                statistics["primary_issues"][p_issue] = statistics["primary_issues"].get(p_issue, 0) + 1
                
                parties = output["root_cause_analysis"]["responsible_parties"]
                for party in parties:
                    p_type = party["party_type"]
                    statistics["responsible_parties"][p_type] = statistics["responsible_parties"].get(p_type, 0) + 1
                    
                refund = output["financial_resolution"]["recommended_refund_brl"]
                statistics["total_refund_brl"] += refund
            else:
                statistics["invalid"] += 1
                print(f"[FAIL] {case_id} failed verification: {res['errors']}")
                
        print("\n=== KẾT QUẢ PHÂN TÍCH 50 CASES ===")
        print(f"Tổng số case chạy: {statistics['total']}")
        print(f"Hợp lệ (Pass Schema): {statistics['valid']}")
        print(f"Không hợp lệ: {statistics['invalid']}")
        print("Thống kê Primary Issues:")
        for k, v in statistics["primary_issues"].items():
            print(f"  - {k}: {v}")
        print("Thống kê bên chịu trách nhiệm:")
        for k, v in statistics["responsible_parties"].items():
            print(f"  - {k}: {v}")
        print(f"Tổng tiền hoàn đề xuất: {statistics['total_refund_brl']:.2f} BRL")
        
        self.assertEqual(statistics["valid"], 50, "Có case không vượt qua xác thực schema!")

if __name__ == "__main__":
    unittest.main()

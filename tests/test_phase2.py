import unittest
import json
from pathlib import Path
from src.data_loader import OlistDataLoader, INPUT_DIR
from src.agents.customer_agent import CustomerAgent
from src.agents.order_product_agent import OrderProductAgent
from src.agents.payment_agent import PaymentAgent
from src.agents.delivery_agent import DeliveryAgent
from src.agents.policy_agent import PolicyAgent
from src.agents.verifier_agent import VerifierAgent
from src.agents.coordinator_agent import CoordinatorAgent

class TestPhase2MultiAgentSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Khởi chạy nạp toàn bộ dataset dùng chung cho toàn bộ test case."""
        cls.loader = OlistDataLoader()
        cls.datasets = cls.loader.load_all()

        # Đọc case EC_001.json làm mẫu thử nghiệm
        cls.case_file = INPUT_DIR / "EC_001.json"
        with open(cls.case_file, 'r', encoding='utf-8') as f:
            cls.case_context = json.load(f)

    def test_01_agents_instantiation(self):
        """Kiểm tra khởi tạo thành công tất cả các Agent."""
        agents = [
            CustomerAgent(),
            OrderProductAgent(),
            PaymentAgent(),
            DeliveryAgent(),
            PolicyAgent(),
            VerifierAgent(),
            CoordinatorAgent()
        ]
        for agent in agents:
            self.assertIsNotNone(agent.name)
            self.assertIsNotNone(agent.description)

    def test_02_coordinator_orchestration_ec001(self):
        """Kiểm tra điều phối viên Coordinator Agent phân tích case EC_001."""
        coordinator = CoordinatorAgent()
        result = coordinator.analyze(self.case_context, self.datasets)

        # Kiểm tra trạng thái phân tích của Agent
        self.assertTrue(result["is_valid"], f"Xác thực thất bại với lỗi: {result['errors']}")
        self.assertIn("output", result)
        self.assertIn("trace", result)

        output = result["output"]
        
        # Kiểm tra cấu trúc các phần chính của output schema
        self.assertEqual(output["case_id"], "EC_001")
        self.assertIn("case_assessment", output)
        self.assertIn("affected_entities", output)
        self.assertIn("customer_context", output)
        self.assertIn("product_context", output)
        self.assertIn("delivery_analysis", output)
        self.assertIn("payment_reconciliation", output)
        self.assertIn("root_cause_analysis", output)
        self.assertIn("evidence_ids", output)
        self.assertIn("financial_resolution", output)
        self.assertIn("resolution_actions", output)

    def test_03_verifier_agent_validation(self):
        """Kiểm tra Verifier Agent bắt được lỗi Schema khi thiếu dữ liệu bắt buộc."""
        verifier = VerifierAgent()
        
        # Test case thiếu trường bắt buộc (ví dụ: thiếu case_assessment)
        invalid_context = {
            "case_id": "EC_TEST_ERR",
            "claimed_order_id": "mock_id",
            "order_analysis": {},
            "payment_analysis": {},
            "delivery_analysis": {},
            "policy_analysis": {},  # Thiếu case_assessment
            "customer_analysis": {}
        }
        
        res = verifier.analyze(invalid_context)
        self.assertFalse(res["is_valid"])
        self.assertGreater(len(res["errors"]), 0)

if __name__ == "__main__":
    unittest.main()

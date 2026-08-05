import pandas as pd
from typing import Dict, Any
from src.agents.base import BaseAgent
from src.agents.customer_agent import CustomerAgent
from src.agents.order_product_agent import OrderProductAgent
from src.agents.payment_agent import PaymentAgent
from src.agents.delivery_agent import DeliveryAgent
from src.agents.policy_agent import PolicyAgent
from src.agents.verifier_agent import VerifierAgent

class CoordinatorAgent(BaseAgent):
    """Agent điều phối trung tâm của toàn bộ hệ thống Multi-Agent."""
    def __init__(self):
        super().__init__(
            name="Coordinator Agent",
            description="Điều phối các agent thành phần để xử lý dispute từ đầu đến cuối."
        )
        self.customer_agent = CustomerAgent()
        self.order_product_agent = OrderProductAgent()
        self.payment_agent = PaymentAgent()
        self.delivery_agent = DeliveryAgent()
        self.policy_agent = PolicyAgent()
        self.verifier_agent = VerifierAgent()

    def analyze(self, case_context: Dict[str, Any], datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Quy trình điều phối phân tích dispute:
        1. Gọi Customer Agent phân tích thông tin khách hàng.
        2. Gọi Order & Product Agent phân tích sản phẩm và gian hàng.
        3. Gọi Payment Agent đối soát tiền thanh toán.
        4. Gọi Delivery Agent đánh giá thời hạn bàn giao và vận chuyển.
        5. Gọi Policy Agent áp dụng quy tắc nghiệp vụ.
        6. Gọi Verifier Agent kiểm chứng, tạo evidence và kiểm tra Schema.
        """
        # Khởi tạo context chạy case
        case_id = case_context["case_id"]
        claimed_order_id = case_context["customer_request"]["claimed_order_id"]
        
        running_context = {
            "case_id": case_id,
            "claimed_order_id": claimed_order_id,
            "policy_version": case_context.get("policy_version", "EC_POLICY_V2"),
            "investigation_scope": case_context.get("investigation_scope", {})
        }

        # Step 1: Customer Agent
        customer_res = self.customer_agent.analyze(running_context, datasets)
        running_context["customer_analysis"] = customer_res

        # Step 2: Order & Product Agent
        order_res = self.order_product_agent.analyze(running_context, datasets)
        running_context["order_analysis"] = order_res

        # Step 3: Payment Agent
        payment_res = self.payment_agent.analyze(running_context, datasets)
        running_context["payment_analysis"] = payment_res

        # Step 4: Delivery Agent
        delivery_res = self.delivery_agent.analyze(running_context, datasets)
        running_context["delivery_analysis"] = delivery_res

        # Step 5: Policy Agent
        policy_res = self.policy_agent.analyze(running_context, datasets)
        running_context["policy_analysis"] = policy_res

        # Step 6: Verifier Agent
        verifier_res = self.verifier_agent.analyze(running_context)
        
        # Ghi nhận log chạy (Trace)
        trace_log = {
            "case_id": case_id,
            "steps": {
                "customer_agent": customer_res,
                "order_product_agent": order_res,
                "payment_agent": payment_res,
                "delivery_agent": delivery_res,
                "policy_agent": policy_res,
                "verifier_agent": {
                    "is_valid": verifier_res.get("is_valid", False),
                    "errors": verifier_res.get("errors", [])
                }
            }
        }

        return {
            "output": verifier_res.get("output"),
            "is_valid": verifier_res.get("is_valid", False),
            "errors": verifier_res.get("errors", []),
            "trace": trace_log
        }

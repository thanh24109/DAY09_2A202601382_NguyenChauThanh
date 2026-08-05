from typing import Dict, Any, List
from src.agents.base import BaseAgent
from src.schemas import CaseOutput

class VerifierAgent(BaseAgent):
    """Agent xác thực toàn bộ dữ liệu, schema và thiết lập bằng chứng (Evidence IDs)."""
    def __init__(self):
        super().__init__(
            name="Verifier Agent",
            description="Tạo các evidence_ids, kiểm tra giới hạn mảng, xử lý null và xác thực schema JSON."
        )

    def analyze(self, case_context: Dict[str, Any], datasets: Dict[str, Any] = None) -> Dict[str, Any]:
        claimed_order_id = case_context["claimed_order_id"]
        
        # Lấy thông tin từ các agent trước
        order_info = case_context.get("order_analysis", {})
        payment_info = case_context.get("payment_analysis", {})
        delivery_info = case_context.get("delivery_analysis", {})
        policy_info = case_context.get("policy_analysis", {})
        customer_info = case_context.get("customer_analysis", {})

        # 1. Tạo danh sách evidence_ids
        evidence_ids = []
        
        # a. order:<order_id>
        evidence_ids.append(f"order:{claimed_order_id}")
        
        # b. item:<order_id>:<order_item_id>
        item_ids = order_info.get("item_ids", [])
        for item_id in item_ids:
            evidence_ids.append(f"item:{item_id}")
            
        # c. payment:<order_id>:<payment_sequential>
        payment_ids = payment_info.get("payment_ids", [])
        for payment_id in payment_ids:
            evidence_ids.append(f"payment:{payment_id}")
            
        # d. seller:<seller_id> chịu trách nhiệm (nếu có)
        root_cause_analysis = policy_info.get("root_cause_analysis", {})
        responsible_parties = root_cause_analysis.get("responsible_parties", [])
        for party in responsible_parties:
            if party.get("party_type") == "seller":
                evidence_ids.append(f"seller:{party.get('party_id')}")

        # e. policy:<root_cause_code>
        ranked_causes = root_cause_analysis.get("ranked_causes", [])
        if ranked_causes:
            root_cause_code = ranked_causes[0].get("cause_code")
            if root_cause_code:
                evidence_ids.append(f"policy:{root_cause_code}")

        # Giới hạn số lượng evidence tối đa là 20
        evidence_ids = list(dict.fromkeys(evidence_ids))[:20]

        # 2. Xây dựng cấu trúc output cuối cùng
        # Kết hợp dữ liệu từ tất cả các Agent
        final_output = {
            "case_id": case_context["case_id"],
            "case_assessment": policy_info.get("case_assessment", {}),
            "affected_entities": {
                "order_ids": order_info.get("order_ids", []),
                "item_ids": order_info.get("item_ids", []),
                "seller_ids": order_info.get("seller_ids", []),
                "payment_ids": payment_info.get("payment_ids", [])
            },
            "customer_context": {
                "customer_unique_id": customer_info.get("customer_unique_id", ""),
                "related_order_ids": customer_info.get("related_order_ids", [])
            },
            "product_context": {
                "product_ids": order_info.get("product_ids", []),
                "category_names": order_info.get("category_names", [])
            },
            "delivery_analysis": delivery_info.get("delivery_analysis", {}),
            "payment_reconciliation": payment_info.get("payment_reconciliation", {}),
            "root_cause_analysis": root_cause_analysis,
            "evidence_ids": evidence_ids,
            "financial_resolution": policy_info.get("financial_resolution", {}),
            "resolution_actions": policy_info.get("resolution_actions", [])
        }

        # 3. Xác thực bằng Pydantic Schema để phát hiện lỗi kiểu dữ liệu
        try:
            validated_output = CaseOutput(**final_output)
            # Trả về dictionary đã xác thực thành công
            return {
                "is_valid": True,
                "output": validated_output.model_dump(),
                "errors": []
            }
        except Exception as e:
            return {
                "is_valid": False,
                "output": final_output,
                "errors": [str(e)]
            }

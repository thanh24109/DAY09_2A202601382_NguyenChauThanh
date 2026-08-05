import pandas as pd
from typing import Dict, Any
from src.agents.base import BaseAgent

class CustomerAgent(BaseAgent):
    """Agent xác định định danh khách hàng và truy xuất lịch sử đơn hàng."""
    def __init__(self):
        super().__init__(
            name="Customer Agent",
            description="Tìm customer_unique_id và danh sách các đơn hàng liên quan của khách."
        )

    def analyze(self, case_context: Dict[str, Any], datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        claimed_order_id = case_context["claimed_order_id"]
        orders_df = datasets["orders"]
        customers_df = datasets["customers"]

        # 1. Tìm customer_id từ orders
        order_row = orders_df[orders_df["order_id"] == claimed_order_id]
        if order_row.empty:
            return {
                "customer_unique_id": "",
                "related_order_ids": [],
                "error": f"Không tìm thấy đơn hàng {claimed_order_id} trong hệ thống."
            }
        
        customer_id = order_row.iloc[0]["customer_id"]

        # 2. Tìm customer_unique_id từ customers
        cust_row = customers_df[customers_df["customer_id"] == customer_id]
        if cust_row.empty:
            return {
                "customer_unique_id": "",
                "related_order_ids": [],
                "error": f"Không tìm thấy customer_id {customer_id} trong bảng customers."
            }
        
        customer_unique_id = cust_row.iloc[0]["customer_unique_id"]

        # 3. Tìm tất cả order_id khác của cùng customer_unique_id này
        # Lấy danh sách customer_id của customer_unique_id này
        all_cust_ids = customers_df[customers_df["customer_unique_id"] == customer_unique_id]["customer_id"].tolist()
        
        # Tìm tất cả order_id tương ứng
        related_orders = orders_df[orders_df["customer_id"].isin(all_cust_ids)]["order_id"].tolist()
        
        # Loại trừ đơn hàng đang khiếu nại (claimed_order_id) ra khỏi related_order_ids
        related_order_ids = [oid for oid in related_orders if oid != claimed_order_id]

        return {
            "customer_unique_id": customer_unique_id,
            "related_order_ids": related_order_ids[:5]  # Giới hạn tối đa 5 theo yêu cầu đề bài
        }

import pandas as pd
from typing import Dict, Any
from src.agents.base import BaseAgent

class DeliveryAgent(BaseAgent):
    """Agent phân tích thời gian giao hàng và bàn giao của seller."""
    def __init__(self):
        super().__init__(
            name="Delivery Agent",
            description="Tính toán biến động thời gian giao hàng (delivery variance) và bàn giao (seller handoff)."
        )

    def analyze(self, case_context: Dict[str, Any], datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        claimed_order_id = case_context["claimed_order_id"]
        orders_df = datasets["orders"]
        order_items_df = datasets["order_items"]

        # 1. Tìm thông tin đơn hàng
        order_row = orders_df[orders_df["order_id"] == claimed_order_id]
        if order_row.empty:
            return {
                "delivery_analysis": {
                    "delivered_at": None,
                    "estimated_delivery_at": None,
                    "carrier_handoff_at": None,
                    "delivery_variance_hours": None,
                    "seller_handoff_analysis": [],
                    "late_handoff_seller_ids": []
                }
            }

        order = order_row.iloc[0]
        delivered_at_str = order.get("order_delivered_customer_date") if pd.notna(order.get("order_delivered_customer_date")) else None
        estimated_delivery_at_str = order.get("order_estimated_delivery_date") if pd.notna(order.get("order_estimated_delivery_date")) else None
        carrier_handoff_at_str = order.get("order_delivered_carrier_date") if pd.notna(order.get("order_delivered_carrier_date")) else None

        # Tính toán delivery_variance_hours
        delivery_variance_hours = None
        if delivered_at_str and estimated_delivery_at_str:
            t_delivered = pd.to_datetime(delivered_at_str)
            t_estimated = pd.to_datetime(estimated_delivery_at_str)
            delivery_variance_hours = round((t_delivered - t_estimated).total_seconds() / 3600.0, 2)

        # 2. Phân tích seller handoff
        items = order_items_df[order_items_df["order_id"] == claimed_order_id]
        seller_handoff_analysis = []
        late_handoff_seller_ids = []

        if not items.empty and carrier_handoff_at_str:
            t_carrier_handoff = pd.to_datetime(carrier_handoff_at_str)
            sellers = items["seller_id"].unique()[:3]
            
            for seller_id in sellers:
                seller_items = items[items["seller_id"] == seller_id]
                # Lấy shipping_limit_date sớm nhất của seller này trong order
                earliest_limit_str = seller_items["shipping_limit_date"].min()
                
                handoff_variance_hours = None
                late_handoff = False
                
                if pd.notna(earliest_limit_str):
                    t_limit = pd.to_datetime(earliest_limit_str)
                    handoff_variance_hours = round((t_carrier_handoff - t_limit).total_seconds() / 3600.0, 2)
                    late_handoff = handoff_variance_hours > 0

                seller_handoff_analysis.append({
                    "seller_id": seller_id,
                    "shipping_limit_at": earliest_limit_str if pd.notna(earliest_limit_str) else None,
                    "handoff_variance_hours": handoff_variance_hours,
                    "late_handoff": late_handoff
                })
                
                if late_handoff:
                    late_handoff_seller_ids.append(seller_id)

        return {
            "delivery_analysis": {
                "delivered_at": delivered_at_str,
                "estimated_delivery_at": estimated_delivery_at_str,
                "carrier_handoff_at": carrier_handoff_at_str,
                "delivery_variance_hours": delivery_variance_hours,
                "seller_handoff_analysis": seller_handoff_analysis,
                "late_handoff_seller_ids": late_handoff_seller_ids
            }
        }

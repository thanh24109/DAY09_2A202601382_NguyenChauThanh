import pandas as pd
from typing import Dict, Any
from src.agents.base import BaseAgent

class PaymentAgent(BaseAgent):
    """Agent tổng hợp thông tin thanh toán và thực hiện đối soát."""
    def __init__(self):
        super().__init__(
            name="Payment Agent",
            description="Tìm các mã thanh toán và thực hiện đối soát tài chính."
        )

    def analyze(self, case_context: Dict[str, Any], datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        claimed_order_id = case_context["claimed_order_id"]
        order_items_df = datasets["order_items"]
        order_payments_df = datasets["order_payments"]

        # Lọc thông tin payments
        payments = order_payments_df[order_payments_df["order_id"] == claimed_order_id]
        
        # Tạo danh sách payment_ids: <order_id>:<payment_sequential>
        payment_ids = [f"{claimed_order_id}:{row['payment_sequential']}" for _, row in payments.iterrows()]
        payment_types = list(payments["payment_type"].dropna().unique())
        payment_total_brl = round(payments["payment_value"].sum(), 2) if not payments.empty else 0.0

        # Lọc thông tin items để tínhexpected_total
        items = order_items_df[order_items_df["order_id"] == claimed_order_id]

        if items.empty:
            # Nếu order không có item row, các trường phải là None (null)
            return {
                "payment_ids": payment_ids[:5],
                "payment_reconciliation": {
                    "currency": "BRL",
                    "item_total_brl": None,
                    "freight_total_brl": None,
                    "expected_total_brl": None,
                    "payment_total_brl": payment_total_brl,
                    "difference_brl": None,
                    "reconciled": None,
                    "payment_types": payment_types
                }
            }

        item_total_brl = round(items["price"].sum(), 2)
        freight_total_brl = round(items["freight_value"].sum(), 2)
        expected_total_brl = round(item_total_brl + freight_total_brl, 2)
        difference_brl = round(payment_total_brl - expected_total_brl, 2)
        reconciled = abs(difference_brl) <= 0.10

        return {
            "payment_ids": payment_ids[:5],
            "payment_reconciliation": {
                "currency": "BRL",
                "item_total_brl": float(item_total_brl),
                "freight_total_brl": float(freight_total_brl),
                "expected_total_brl": float(expected_total_brl),
                "payment_total_brl": float(payment_total_brl),
                "difference_brl": float(difference_brl),
                "reconciled": bool(reconciled),
                "payment_types": payment_types
            }
        }

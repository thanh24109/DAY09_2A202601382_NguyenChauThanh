import pandas as pd
from typing import Dict, Any
from src.agents.base import BaseAgent

class OrderProductAgent(BaseAgent):
    """Agent phân tích thông tin đơn hàng, danh sách mặt hàng, người bán và sản phẩm."""
    def __init__(self):
        super().__init__(
            name="Order & Product Agent",
            description="Tìm các mã orders, items, sellers, products và danh mục sản phẩm."
        )

    def analyze(self, case_context: Dict[str, Any], datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        claimed_order_id = case_context["claimed_order_id"]
        order_items_df = datasets["order_items"]
        products_df = datasets["products"]
        translation_df = datasets["product_category_name_translation"]

        # Lọc các item thuộc order_id này
        items = order_items_df[order_items_df["order_id"] == claimed_order_id]
        
        if items.empty:
            # Trường hợp order không có item row
            return {
                "order_ids": [claimed_order_id],
                "item_ids": [],
                "seller_ids": [],
                "product_ids": [],
                "category_names": []
            }

        # Tạo danh sách item_ids: <order_id>:<order_item_id>
        item_ids = [f"{claimed_order_id}:{row['order_item_id']}" for _, row in items.iterrows()]
        
        # Lấy danh sách duy nhất các seller_ids
        seller_ids = list(items["seller_id"].unique())
        
        # Lấy danh sách duy nhất các product_ids
        product_ids = list(items["product_id"].unique())

        # Tìm các category tương ứng của product_ids
        category_names = []
        prod_cats = products_df[products_df["product_id"].isin(product_ids)]["product_category_name"].dropna().unique()
        
        # Tạo map dịch từ tiếng Bồ Đào Nha sang tiếng Anh
        translation_map = dict(zip(translation_df["product_category_name"], translation_df["product_category_name_english"]))

        for cat in prod_cats:
            english_cat = translation_map.get(cat, cat)
            category_names.append(english_cat)

        # Áp dụng giới hạn mảng của output schema
        return {
            "order_ids": [claimed_order_id][:5],
            "item_ids": item_ids[:5],
            "seller_ids": seller_ids[:3],
            "product_ids": product_ids[:5],
            "category_names": list(set(category_names))[:5]
        }

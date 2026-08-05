import pandas as pd
from typing import Dict, Any

class BaseAgent:
    """Lớp cơ sở định nghĩa các Agent trong hệ thống Multi-Agent."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def analyze(self, case_context: Dict[str, Any], datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Phương thức phân tích chính, nhận vào ngữ cảnh hiện tại và tập dữ liệu, trả về kết quả phân tích.
        
        Args:
            case_context: Chứa thông tin input của case (case_id, claimed_order_id, v.v.) và kết quả phân tích của các agent khác.
            datasets: Từ điển chứa các DataFrame tương ứng với các bảng dữ liệu Olist.
        """
        raise NotImplementedError("Các Agent con bắt buộc phải triển khai phương thức analyze.")

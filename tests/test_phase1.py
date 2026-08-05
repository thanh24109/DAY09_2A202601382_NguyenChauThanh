import unittest
import json
from pathlib import Path
import pandas as pd
from src.data_loader import OlistDataLoader, CSV_FILES, DATA_DIR, INPUT_DIR

class TestPhase1DataPipeline(unittest.TestCase):
    def test_01_csv_files_exist_and_readable(self):
        """Kiểm tra tất cả 9 file CSV dữ liệu Olist có tồn tại và không rỗng."""
        for csv_file in CSV_FILES:
            filepath = DATA_DIR / csv_file
            self.assertTrue(filepath.exists(), f"Thiếu file CSV: {csv_file}")
            self.assertGreater(filepath.stat().st_size, 0, f"File CSV rỗng: {csv_file}")

    def test_02_input_json_cases_count_and_schema(self):
        """Kiểm tra đủ 50 file JSON khiếu nại và tuân thủ schema."""
        json_files = list(INPUT_DIR.glob("EC_*.json"))
        self.assertEqual(len(json_files), 50, f"Số lượng file input không đúng 50 (hiện có {len(json_files)})")

        for i in range(1, 51):
            filename = f"EC_{i:03d}.json"
            filepath = INPUT_DIR / filename
            self.assertTrue(filepath.exists(), f"Thiếu file input: {filename}")

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Kiểm tra schema bắt buộc
            self.assertEqual(data.get("case_id"), f"EC_{i:03d}")
            self.assertIn("customer_request", data)
            self.assertIn("claimed_order_id", data["customer_request"])
            self.assertTrue(bool(data["customer_request"]["claimed_order_id"]))
            self.assertEqual(data.get("policy_version"), "EC_POLICY_V2")

    def test_03_data_loader_functionality(self):
        """Kiểm tra class OlistDataLoader nạp thành công các DataFrame."""
        loader = OlistDataLoader(data_dir=DATA_DIR)
        datasets = loader.load_all()

        expected_keys = [
            "customers", "geolocation", "order_items", "order_payments",
            "order_reviews", "orders", "products", "sellers",
            "product_category_name_translation"
        ]

        for key in expected_keys:
            self.assertIn(key, datasets, f"Thiếu dataset key: {key}")
            self.assertIsInstance(datasets[key], pd.DataFrame, f"Dataset {key} không phải DataFrame")
            self.assertGreater(len(datasets[key]), 0, f"Dataset {key} rỗng")

if __name__ == "__main__":
    unittest.main()

import os
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = BASE_DIR / "input"

CSV_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
]

REQUIRED_COLUMNS = {
    "olist_customers_dataset.csv": {"customer_id", "customer_unique_id"},
    "olist_geolocation_dataset.csv": {"geolocation_zip_code_prefix"},
    "olist_order_items_dataset.csv": {
        "order_id", "order_item_id", "product_id", "seller_id",
        "shipping_limit_date", "price", "freight_value"
    },
    "olist_order_payments_dataset.csv": {
        "order_id", "payment_sequential", "payment_type", "payment_value"
    },
    "olist_order_reviews_dataset.csv": {"review_id", "order_id"},
    "olist_orders_dataset.csv": {
        "order_id", "customer_id", "order_status",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    },
    "olist_products_dataset.csv": {"product_id", "product_category_name"},
    "olist_sellers_dataset.csv": {"seller_id"},
    "product_category_name_translation.csv": {
        "product_category_name", "product_category_name_english"
    },
}


def _validate_dataframe(csv_file: str, df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError(f"{csv_file} is empty")
    missing = REQUIRED_COLUMNS[csv_file] - set(df.columns)
    if missing:
        raise ValueError(f"{csv_file} missing columns: {sorted(missing)}")

def check_data_files():
    print("=== CHECKING OLIST DATASET CSVs ===")
    csv_stats = {}
    for csv_file in CSV_FILES:
        filepath = DATA_DIR / csv_file
        if not filepath.exists():
            print(f"[ERROR] Missing file: {csv_file}")
            csv_stats[csv_file] = {"status": "MISSING"}
            continue
        
        try:
            df = pd.read_csv(filepath)
            _validate_dataframe(csv_file, df)
            csv_stats[csv_file] = {
                "status": "OK",
                "rows": len(df),
                "columns": list(df.columns),
                "memory_mb": round(filepath.stat().st_size / (1024 * 1024), 2)
            }
            print(f"[OK] {csv_file}: {len(df):,} rows, {len(df.columns)} columns ({csv_stats[csv_file]['memory_mb']} MB)")
        except Exception as e:
            print(f"[ERROR] Reading {csv_file}: {str(e)}")
            csv_stats[csv_file] = {"status": f"ERROR: {str(e)}"}
    return csv_stats

def check_input_cases():
    print("\n=== CHECKING INPUT JSON CASES ===")
    json_files = list(INPUT_DIR.glob("EC_*.json"))
    json_stats = {
        "total_files": len(json_files),
        "valid_cases": 0,
        "cases": []
    }
    
    for i in range(1, 51):
        filename = f"EC_{i:03d}.json"
        filepath = INPUT_DIR / filename
        if not filepath.exists():
            print(f"[ERROR] Missing input case: {filename}")
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            case_id = data.get("case_id")
            claimed_order_id = data.get("customer_request", {}).get("claimed_order_id")
            policy_version = data.get("policy_version")
            
            expected_case_id = f"EC_{i:03d}"
            if case_id != expected_case_id:
                raise ValueError(f"case_id must be {expected_case_id}")
            if not claimed_order_id:
                raise ValueError("customer_request.claimed_order_id is required")
            if policy_version != "EC_POLICY_V2":
                raise ValueError("policy_version must be EC_POLICY_V2")

            json_stats["cases"].append({
                "filename": filename,
                "case_id": case_id,
                "claimed_order_id": claimed_order_id,
                "policy_version": policy_version
            })
            json_stats["valid_cases"] += 1
        except Exception as e:
            print(f"[ERROR] Reading {filename}: {str(e)}")

    print(f"[OK] Total valid input cases: {json_stats['valid_cases']} / 50")
    return json_stats

class OlistDataLoader:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.datasets = {}

    def load_all(self):
        print("\nLoading all CSV datasets into memory...")
        for csv_file in CSV_FILES:
            name = csv_file.replace("olist_", "").replace("_dataset.csv", "").replace(".csv", "")
            filepath = self.data_dir / csv_file
            if not filepath.exists():
                raise FileNotFoundError(f"Missing required dataset: {filepath}")
            self.datasets[name] = pd.read_csv(filepath)
            _validate_dataframe(csv_file, self.datasets[name])
            print(f"Loaded '{name}': {len(self.datasets[name]):,} rows")
        return self.datasets

if __name__ == "__main__":
    csv_stats = check_data_files()
    json_stats = check_input_cases()
    
    loader = OlistDataLoader()
    datasets = loader.load_all()
    print("\nPhase 1 Data Inspection & Loading completed successfully.")

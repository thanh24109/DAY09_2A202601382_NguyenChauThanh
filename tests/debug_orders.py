import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
orders_file = BASE_DIR / "data" / "olist_orders_dataset.csv"

def debug():
    df = pd.read_csv(orders_file)
    print("Columns in orders dataset:")
    print(df.columns.tolist())
    
    order_id = "1118f05e23d1a8082fa47f8a377de658"
    row = df[df["order_id"] == order_id]
    print(f"\nRow for order_id '{order_id}':")
    print(row.to_dict(orient="records"))

if __name__ == "__main__":
    debug()

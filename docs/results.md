# BÁO CÁO KẾT QUẢ THỰC HIỆN DỰ ÁN
**Dự án:** K4 Day 09 - Multi-Agent E-commerce Dispute Resolution
**Người thực hiện:** Nguyễn Châu Thanh (MSSV: 2A202601382)
**Ngày cập nhật:** 05/08/2026

---

## 📌 1. Kết quả Phase 1: Thiết lập & Chuẩn bị dữ liệu

* **Trạng thái:** **HOÀN THÀNH (100% Phase 1 / 10% Tổng dự án)**
* **Mã nguồn đã tạo:** [src/data_loader.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/data_loader.py), [src/__init__.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/__init__.py), [.gitignore](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/.gitignore)

---

## 📌 2. Kết quả Phase 2: Xây dựng Kiến trúc Multi-Agent

* **Trạng thái:** **HOÀN THÀNH (100% Phase 2 / 35% Tổng dự án)**
* **Mã nguồn đã tạo:**
  - **Data Contracts:** [src/schemas.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/schemas.py)
  - **Các Agent:** [base.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/base.py), [coordinator_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/coordinator_agent.py), [customer_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/customer_agent.py), [order_product_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/order_product_agent.py), [payment_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/payment_agent.py), [delivery_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/delivery_agent.py), [policy_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/policy_agent.py), [verifier_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/verifier_agent.py)

---

## 📌 3. Kết quả Phase 3: Logic Nghiệp vụ & Xử lý Dispute

Phase 3 tập trung vào việc áp dụng chính sách `EC_POLICY_V2`, thực hiện tính toán biến động thời gian, đối soát tài chính và phân loại các lỗi chính/phụ cho toàn bộ 50 case khiếu nại đầu vào.

* **Trạng thái:** **HOÀN THÀNH (100% Phase 3 / 30% Tổng dự án)**

### 📊 Thống kê kết quả chạy thực tế (50 Cases)

| Chỉ số thống kê | Giá trị |
| :--- | :---: |
| **Tổng số case xử lý** | 50 |
| **Hợp lệ (Pass Schema)** | 50 |
| **Không hợp lệ (Fail Schema)** | 0 |
| **Tổng số tiền đề xuất hoàn trả** | **3437.76 BRL** |

#### Phân bố lỗi chính (Primary Issues):
- **unsupported_late_claim**: 8 case(s)
- **late_delivery_seller**: 10 case(s)
- **late_delivery_logistics**: 10 case(s)
- **canceled_order_paid**: 8 case(s)
- **valid_split_payment**: 8 case(s)
- **unavailable_order_paid**: 6 case(s)

#### Phân bố trách nhiệm (Responsible Parties):
- **seller**: 10 lần chịu trách nhiệm
- **logistics_provider**: 10 lần chịu trách nhiệm
- **platform**: 14 lần chịu trách nhiệm

### 📋 Bảng tổng hợp chi tiết kết quả 50 case:

| Case ID | Primary Issue | Secondary Issues | Responsible Party | Refund | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| EC_001 | unsupported_late_claim | multi_item_order, repeat_customer | None | 0.00 BRL | PASS |
| EC_002 | late_delivery_seller | split_payment, repeat_customer | seller:c3867b4666c7d76867627c2f7fb22e21 | 18.27 BRL | PASS |
| EC_003 | late_delivery_logistics | multi_item_order, repeat_customer | logistics_provider:LOGISTICS_PROVIDER | 32.22 BRL | PASS |
| EC_004 | canceled_order_paid | multi_item_order | platform:OLIST_PLATFORM | 290.16 BRL | PASS |
| EC_005 | late_delivery_logistics | multi_item_order, multi_seller_order | logistics_provider:LOGISTICS_PROVIDER | 32.75 BRL | PASS |
| EC_006 | late_delivery_seller | multi_item_order, repeat_customer | seller:897060da8b9a21f655304d50fd935913 | 60.40 BRL | PASS |
| EC_007 | late_delivery_logistics | multi_item_order, multi_seller_order, multiple_categories | logistics_provider:LOGISTICS_PROVIDER | 44.13 BRL | PASS |
| EC_008 | valid_split_payment | multi_item_order, multi_seller_order, split_payment | None | 0.00 BRL | PASS |
| EC_009 | canceled_order_paid | multi_item_order | platform:OLIST_PLATFORM | 144.30 BRL | PASS |
| EC_010 | valid_split_payment | multi_item_order, multi_seller_order, split_payment | None | 0.00 BRL | PASS |
| EC_011 | canceled_order_paid | multi_item_order | platform:OLIST_PLATFORM | 127.12 BRL | PASS |
| EC_012 | unavailable_order_paid | repeat_customer | platform:OLIST_PLATFORM | 226.23 BRL | PASS |
| EC_013 | late_delivery_seller | multi_item_order, split_payment | seller:4d6d651bd7684af3fffabd5f08d12e5a | 48.14 BRL | PASS |
| EC_014 | late_delivery_logistics | multi_item_order, repeat_customer | logistics_provider:LOGISTICS_PROVIDER | 50.37 BRL | PASS |
| EC_015 | valid_split_payment | multi_item_order, multi_seller_order, split_payment | None | 0.00 BRL | PASS |
| EC_016 | late_delivery_logistics | split_payment, repeat_customer | logistics_provider:LOGISTICS_PROVIDER | 18.15 BRL | PASS |
| EC_017 | late_delivery_logistics | multi_item_order, repeat_customer | logistics_provider:LOGISTICS_PROVIDER | 48.54 BRL | PASS |
| EC_018 | unsupported_late_claim | multi_item_order, multi_seller_order | None | 0.00 BRL | PASS |
| EC_019 | late_delivery_seller | multi_item_order, repeat_customer | seller:4a3ca9315b744ce9f8e9374361493884 | 23.48 BRL | PASS |
| EC_020 | late_delivery_seller | multi_item_order, repeat_customer | seller:7c67e1448b00f6e969d365cea6b010ab | 68.64 BRL | PASS |
| EC_021 | unsupported_late_claim | multi_item_order, multi_seller_order | None | 0.00 BRL | PASS |
| EC_022 | valid_split_payment | multi_item_order, split_payment, repeat_customer | None | 0.00 BRL | PASS |
| EC_023 | late_delivery_logistics | multi_item_order, repeat_customer | logistics_provider:LOGISTICS_PROVIDER | 101.00 BRL | PASS |
| EC_024 | canceled_order_paid | multi_item_order | platform:OLIST_PLATFORM | 333.62 BRL | PASS |
| EC_025 | unsupported_late_claim | multi_item_order, repeat_customer | None | 0.00 BRL | PASS |
| EC_026 | canceled_order_paid | multi_item_order | platform:OLIST_PLATFORM | 670.04 BRL | PASS |
| EC_027 | late_delivery_logistics | multi_item_order, repeat_customer | logistics_provider:LOGISTICS_PROVIDER | 30.38 BRL | PASS |
| EC_028 | canceled_order_paid | multi_item_order | platform:OLIST_PLATFORM | 242.62 BRL | PASS |
| EC_029 | valid_split_payment | multi_item_order, multi_seller_order, split_payment, repeat_customer, multiple_categories | None | 0.00 BRL | PASS |
| EC_030 | canceled_order_paid | multi_item_order | platform:OLIST_PLATFORM | 81.48 BRL | PASS |
| EC_031 | unavailable_order_paid | repeat_customer | platform:OLIST_PLATFORM | 138.92 BRL | PASS |
| EC_032 | late_delivery_seller | multi_item_order, multiple_categories | seller:76d5af76d0271110f9af36c92573f765 | 31.64 BRL | PASS |
| EC_033 | unavailable_order_paid | repeat_customer | platform:OLIST_PLATFORM | 35.96 BRL | PASS |
| EC_034 | unavailable_order_paid | repeat_customer | platform:OLIST_PLATFORM | 85.14 BRL | PASS |
| EC_035 | unavailable_order_paid | repeat_customer | platform:OLIST_PLATFORM | 132.37 BRL | PASS |
| EC_036 | valid_split_payment | multi_item_order, multi_seller_order, split_payment | None | 0.00 BRL | PASS |
| EC_037 | late_delivery_logistics | multi_item_order, repeat_customer | logistics_provider:LOGISTICS_PROVIDER | 24.38 BRL | PASS |
| EC_038 | unsupported_late_claim | multi_item_order, repeat_customer | None | 0.00 BRL | PASS |
| EC_039 | late_delivery_seller | multi_item_order, repeat_customer | seller:88460e8ebdecbfecb5f9601833981930 | 30.54 BRL | PASS |
| EC_040 | late_delivery_logistics | multi_item_order, multiple_categories | logistics_provider:LOGISTICS_PROVIDER | 75.98 BRL | PASS |
| EC_041 | valid_split_payment | multi_item_order, multi_seller_order, split_payment | None | 0.00 BRL | PASS |
| EC_042 | late_delivery_seller | split_payment, repeat_customer | seller:cce6ab8d1682639fe45ab70234f1665f | 17.60 BRL | PASS |
| EC_043 | unavailable_order_paid | repeat_customer | platform:OLIST_PLATFORM | 18.37 BRL | PASS |
| EC_044 | unsupported_late_claim | multi_item_order, multi_seller_order | None | 0.00 BRL | PASS |
| EC_045 | unsupported_late_claim | multi_item_order, multi_seller_order, multiple_categories | None | 0.00 BRL | PASS |
| EC_046 | late_delivery_seller | multi_item_order, split_payment | seller:cca3071e3e9bb7d12640c9fbe2301306 | 25.52 BRL | PASS |
| EC_047 | canceled_order_paid | repeat_customer | platform:OLIST_PLATFORM | 79.56 BRL | PASS |
| EC_048 | late_delivery_seller | multi_item_order, repeat_customer | seller:8160255418d5aaa7dbdc9f4c64ebda44 | 49.74 BRL | PASS |
| EC_049 | valid_split_payment | multi_item_order, multi_seller_order, split_payment | None | 0.00 BRL | PASS |
| EC_050 | unsupported_late_claim | multi_item_order, multi_seller_order, multiple_categories | None | 0.00 BRL | PASS |

---

## 📌 4. Kết quả Phase 4: Output, Tracing & Đóng gói

Phase 4 thực hiện ghi trace log, metadata cấu hình, tạo file kết quả chi tiết của 50 đơn hàng và đóng gói sản phẩm nộp bài.

* **Trạng thái:** **HOÀN THÀNH (100% Phase 4 / 15% Tổng dự án)**
* **Tổng tiến độ tích lũy:** **90% / 100%** (Đã hoàn thành Phase 1 + 2 + 3 + 4)
* **Sản phẩm bàn giao:**
  - 50 file JSON kết quả đầu ra trong [output/](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/output).
  - Tệp trace log chạy [logging/trace.jsonl](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/logging/trace.jsonl).
  - Tệp metadata cấu hình [logging/metadata.json](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/logging/metadata.json).
  - Tệp nén nộp bài `output.zip` tại thư mục gốc của workspace.

---

## 🎯 5. Đánh giá & Bước tiếp theo (Phase 5)

Sau khi hoàn tất toàn bộ code và đóng gói kết quả, bước cuối cùng là:
1. **Phase 5: Tài liệu & Hoàn thiện báo cáo (10%)**: Hoàn thiện tài liệu kiến trúc hệ thống [architecture.md](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/architecture.md) và viết báo cáo cá nhân từ file template [individual_5SoCuoiMHV_HoVaTen.md](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/individual_5SoCuoiMHV_HoVaTen.md).

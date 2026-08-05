# BÁO CÁO TIẾN ĐỘ HOÀN THÀNH DỰ ÁN (PROGRESS REPORT)
**Dự án:** K4 Day 09 - Multi-Agent E-commerce Dispute Resolution
**Học viên:** Nguyễn Châu Thanh
**Mã số sinh viên (MSSV):** 2A202601382
**Workspace:** `E:\LabVin\DAY09_2A202601382_NguyenChauThanh`

---

## 📊 Tổng quan tiến độ chung: 0% / 100%

```
[░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0%
```

| Giai đoạn | Trọng số | Tiến độ hoàn thành | Trạng thái |
| :--- | :---: | :---: | :--- |
| **Phase 1: Thiết lập & Chuẩn bị dữ liệu** | 10% | 0% | Chưa bắt đầu |
| **Phase 2: Xây dựng Kiến trúc Multi-Agent** | 35% | 0% | Chưa bắt đầu |
| **Phase 3: Logic Nghiệp vụ & Xử lý Dispute** | 30% | 0% | Chưa bắt đầu |
| **Phase 4: Output, Tracing & Đóng gói** | 15% | 0% | Chưa bắt đầu |
| **Phase 5: Tài liệu & Hoàn thiện báo cáo** | 10% | 0% | Chưa bắt đầu |

---

## 📝 Bảng chi tiết các Task & Yêu cầu đề bài

### Phase 1: Thiết lập & Chuẩn bị dữ liệu (Trọng số: 10%)
- [ ] **Task 1.1:** Khởi tạo môi trường ảo Python và cài đặt các thư viện cần thiết (`pandas`, `openai` / `google-generativeai`, `python-dotenv`, v.v.) *(2%)*
- [ ] **Task 1.2:** Viết module nạp và kiểm tra dữ liệu từ 9 file CSV trong thư mục [data/](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/data) *(5%)*
- [ ] **Task 1.3:** Kiểm tra và chuẩn bị đầy đủ 50 file JSON đầu vào (`EC_001.json` đến `EC_050.json`) trong thư mục [input/](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/input) *(3%)*

### Phase 2: Xây dựng Kiến trúc Multi-Agent (Trọng số: 35%)
- [ ] **Task 2.1:** **Coordinator Agent**: Quản lý nhận case, điều phối công việc cho các agent phụ trợ và tổng hợp output cuối cùng. *(5%)*
- [ ] **Task 2.2:** **Customer Agent**: Xác định định danh khách hàng (`customer_unique_id`) và truy vấn lịch sử order để phân tích hành vi khách hàng cũ. *(5%)*
- [ ] **Task 2.3:** **Order & Product Agent**: Kiểm tra chi tiết đơn hàng (items, giá tiền, sellers, thông tin sản phẩm và phân loại category). *(5%)*
- [ ] **Task 2.4:** **Payment Agent**: Đối soát dữ liệu thanh toán (payment rows) và tính toán tổng số tiền thanh toán thực tế. *(5%)*
- [ ] **Task 2.5:** **Delivery Agent**: Phân tích thời gian vận chuyển (delivery variance) và thời gian bàn giao của seller (seller handoff variance). *(5%)*
- [ ] **Task 2.6:** **Policy Agent**: Áp dụng quy tắc nghiệp vụ (`EC_POLICY_V2`) để xác định lỗi chính/phụ, bên chịu trách nhiệm, khoản hoàn trả và actions. *(5%)*
- [ ] **Task 2.7:** **Verifier Agent**: Kiểm tra chéo toàn bộ dữ liệu output (định dạng ID, số tiền làm tròn, giới hạn mảng, xử lý giá trị null, schema JSON). *(5%)*

### Phase 3: Logic Nghiệp vụ & Xử lý Dispute (Trọng số: 30%)
- [ ] **Task 3.1:** Phân loại chính xác **Primary Issue** theo đúng mức độ ưu tiên quy định trong chính sách `EC_POLICY_V2`. *(8%)*
- [ ] **Task 3.2:** Phân loại **Secondary Issues** (multi-item, multi-seller, split-payment, repeat-customer, multiple-categories) theo đúng điều kiện và thứ tự quy định. *(6%)*
- [ ] **Task 3.3:** Tính toán chuẩn xác các công thức chênh lệch thời gian (`delivery_variance_hours`, `handoff_variance_hours`) và tài chính (`expected_total_brl`, `difference_brl`, `reconciled`). *(5%)*
- [ ] **Task 3.4:** Thiết lập cấu trúc **Evidence IDs** chính xác theo định dạng yêu cầu (`order:`, `item:`, `payment:`, `seller:`, `policy:`). *(8%)*
- [ ] **Task 3.5:** Tự động quyết định **Resolution Actions** bổ sung dựa trên Primary Issue và hoàn cảnh đơn hàng. *(3%)*

### Phase 4: Output, Tracing & Đóng gói (Trọng số: 15%)
- [ ] **Task 4.1:** Ghi vết (Trace log) toàn bộ quá trình chạy của 50 case vào file [logging/trace.jsonl](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/logging/trace.jsonl) theo đúng lượt chạy mới nhất. *(5%)*
- [ ] **Task 4.2:** Tạo file cấu hình [logging/metadata.json](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/logging/metadata.json) chứa các thông số: model sử dụng (dưới 10B parameters), số lượng parameters, framework, runtime. *(2%)*
- [ ] **Task 4.3:** Tạo ra 50 file JSON kết quả đầu ra trong thư mục [output/](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/output) khớp 100% với schema yêu cầu. *(5%)*
- [ ] **Task 4.4:** Nén thư mục `output/` thành file zip để nộp bài (đảm bảo chỉ chứa đúng 50 JSON file và không chứa file thừa). *(3%)*

### Phase 5: Tài liệu & Hoàn thiện báo cáo (Trọng số: 10%)
- [ ] **Task 5.1:** Hoàn thiện file [architecture.md](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/architecture.md) (sơ đồ agent, vai trò, quyền truy cập và luồng handoff dữ liệu). *(5%)*
- [ ] **Task 5.2:** Đổi tên và hoàn thiện báo cáo cá nhân từ template [individual_5SoCuoiMHV_HoVaTen.md](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/individual_5SoCuoiMHV_HoVaTen.md) thành `individual_2A202601382_NguyenChauThanh.md` tại root repo. *(5%)*

---

## 🔍 Hướng dẫn cập nhật tiến độ
Để cập nhật tiến độ, bạn chỉ cần đánh dấu `[x]` vào các task đã hoàn thành và thay đổi tỷ lệ phần trăm tương ứng tại phần **Tổng quan tiến độ chung** theo công thức cộng dồn trọng số của các task đã hoàn thành.

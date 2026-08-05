# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin         | Nội dung      |
| ------------------ | -------------- |
| Họ và tên       | Nguyễn Châu Thanh |
| MSSV               | 2A202601382         |
| Khóa/Lớp         | K4           |
| Vai trò chính    | Multi-Agent System Developer / Coordinator |
| Ngày hoàn thành | 2026-08-05   |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| **Kiến trúc Multi-Agent** | [src/agents/](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/) | Các file dữ liệu CSV của Olist. | Cấu trúc các Agent con: Customer, OrderProduct, Payment, Delivery, Policy, Verifier. | Hoàn thành |
| **Coordinator & Pipeline** | [src/agents/coordinator_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/coordinator_agent.py)<br>[src/run_pipeline.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/run_pipeline.py) | Đầu vào khiếu nại (input/*.json). | Sắp xếp luồng chuyển tiếp dữ liệu (handoff), xuất file JSON kết quả, nén output.zip và ghi trace.jsonl. | Hoàn thành |
| **Logic đối soát tài chính** | [src/agents/payment_agent.py](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/src/agents/payment_agent.py) | Bảng dữ liệu `order_payments`, `order_items`. | Đối soát số tiền thanh toán thực tế và đề xuất hoàn tiền. | Hoàn thành |

---

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                  | Thành viên/module được hỗ trợ | Kết quả                    |
| ----------------------------- | ------------------------------------ | ---------------------------- |
| **Tối ưu hóa rate-limiting và retry LLM** | Toàn bộ hệ thống gọi LLM | Thiết lập độ giãn cách 4.2s (Gemini) và 2.0s (Qwen/OpenRouter) cùng cơ chế Exponential Backoff để tránh lỗi 429 vượt quota Free Tier. |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh  |
| --------------------------- | ----------------------------- | ------------------------- | ---------------- |
| Xây dựng khung Multi-Agent | `src/agents/` | 6 Agent chuyên trách hoàn chỉnh độc lập. | Chạy lệnh `pytest tests/test_phase2.py` |
| Xử lý trọn vẹn 50 vụ khiếu nại | `output/` | 50 file JSON đầu ra khớp 100% định dạng schema và các ràng buộc độ dài mảng. | Chạy lệnh `python tests/verify_output_rules.py` |
| Tích hợp hệ thống ghi vết | `logging/trace.jsonl` | Ghi log toàn bộ luồng chạy của 50 đơn hàng mà không bị ghi đè. | Kiểm tra file `logging/trace.jsonl` |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Trong quy trình chăm sóc khách hàng của Olist, các khiếu nại về giao hàng trễ, hoàn tiền hoặc thanh toán lỗi đòi hỏi phải đối soát chéo thông tin từ nhiều bảng dữ liệu nguồn (orders, items, payments, sellers). Một hệ thống AI đơn thuần (Single Prompt) rất dễ bị hallucination hoặc bỏ sót các quy tắc nghiệp vụ chặt chẽ của `EC_POLICY_V2`. 

### Cách triển khai
Tôi đã chia nhỏ luồng phân tích thành 6 bước tuần tự, mỗi bước do một Agent chuyên trách phụ trách để tối đa hóa tính deterministic:
1. **CustomerAgent**: Lấy `customer_unique_id` và lịch sử mua sắm.
2. **OrderProductAgent**: Lấy danh sách item, seller và dịch danh mục sản phẩm.
3. **PaymentAgent**: So khớp số tiền thực thu và lý thuyết để phát hiện chênh lệch.
4. **DeliveryAgent**: Tính toán độ lệch ngày giao hàng thực tế/dự kiến và kiểm tra seller giao trễ hạn.
5. **PolicyAgent**: Đóng vai trò logic áp dụng thứ tự ưu tiên của `EC_POLICY_V2` và gọi mô hình AI chấm điểm tin cậy `confidence`.
6. **VerifierAgent**: Gom bằng chứng (`evidence_ids`), lọc mảng và dùng Pydantic Schema (`CaseOutput`) để ép kiểu dữ liệu đầu ra nghiêm ngặt.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Context khiếu nại (chứa `case_id`, `claimed_order_id`) và 9 bảng dữ liệu CSV của Olist. |
| Output                         | Dict kết quả khớp 100% với Pydantic class `CaseOutput`. |
| Module phụ thuộc             | `src/data_loader.py` để nạp dữ liệu. |
| Module sử dụng output        | `src/run_pipeline.py` để ghi file JSON và đóng gói tệp nén zip. |
| Điều kiện lỗi cần xử lý | Lỗi key-mapping khi chuyển dữ liệu từ Delivery Agent sang các agent sau làm thông tin bị null (đã được sửa bằng cách đồng bộ gán nguyên bản thay vì tự ý bóc tách trước). |

### Cách xác minh

```bash
python tests/verify_output_rules.py
```
* **Kết quả mong đợi:** In ra dòng `[SUCCESS] Kiểm tra hoàn tất! Toàn bộ 50 file trong output/ đều tuân thủ 100% tất cả các giới hạn và định dạng yêu cầu.`
* **Kết quả thực tế:** Khớp chính xác với kết quả mong đợi, không có bất kỳ lỗi định dạng nào.
* **Artifact/log:** Xem tại [logging/trace.jsonl](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/logging/trace.jsonl) và [logging/metadata.json](file:///E:/LabVin/DAY09_2A202601382_NguyenChauThanh/logging/metadata.json).

---

## 5. Một quyết định kỹ thuật quan trọng

* **Bối cảnh:** Chọn lựa cơ chế xác thực đầu ra JSON cho toàn bộ 50 case để tránh sai lệch dữ liệu thô/kiểu dữ liệu khi nộp bài.
* **Các phương án đã cân nhắc:**
  1. Sử dụng Regular Expression và Regex parser để định dạng chuỗi thủ công.
  2. Sử dụng thư viện **Pydantic** để xây dựng các mô hình Schema và ép kiểu bắt buộc trước khi ghi file.
* **Phương án đã chọn:** Phương án 2 (Sử dụng Pydantic Schema).
* **Lý do:** Pydantic cung cấp khả năng tự động ép kiểu số thực (float), tự động thiết lập các mảng rỗng làm mặc định, và dễ dàng bắt các ngoại lệ dữ liệu (validation errors) trước khi ghi file, đảm bảo các trường bắt buộc không bao giờ bị thiếu hoặc sai định dạng thô.

---

## 6. Một lỗi hoặc blocker đã xử lý

* **Triệu chứng/lỗi nguyên văn:** Lỗi key-mapping làm dữ liệu `delivery_analysis` trong 50 file JSON đầu ra luôn bị `null` và `[]` dù đơn hàng có dữ liệu ngày tháng đầy đủ.
* **Nguyên nhân gốc:** Tại `CoordinatorAgent`, kết quả trả về của Delivery Agent đã bị bóc tách sớm một lần bằng câu lệnh `running_context["delivery_analysis"] = delivery_res["delivery_analysis"]`. Khi truyền sang Policy/Verifier Agent, các agent này lại tìm tiếp khoá `"delivery_analysis"` lần nữa nên nhận về kết quả rỗng `{}`.
* **Cách xử lý:** Sửa lại dòng gán trong `CoordinatorAgent` thành `running_context["delivery_analysis"] = delivery_res` để giữ nguyên gốc sơ đồ đóng gói, đồng bộ với cách Payment/Order Agent chuyển giao dữ liệu.
* **Cách xác minh sau khi sửa:** Chạy lại `python src/run_pipeline.py` và kiểm tra lại `output/EC_001.json` thấy trường `delivered_at` đã có giá trị thời gian thật.

---

## 7. Hiểu biết về luồng end-to-end
*(Lưu ý: Mẫu template gốc hiển thị các câu hỏi về Crossref/Retrieval của bài Lab trước, dưới đây là câu trả lời được liên kết tương ứng với bài Lab Multi-Agent Dispute Resolution hiện tại)*

1. **Dữ liệu đi từ dữ liệu gốc đến hệ thống quyết định như thế nào?**
   Dữ liệu từ 9 file CSV của Olist được nạp thông qua `OlistDataLoader` vào bộ nhớ dưới dạng các `pd.DataFrame`. Khi chạy mỗi case khiếu nại, `claimed_order_id` được chuyển giao tuần tự qua các Worker Agents để truy vấn, chọn lọc và tổng hợp thành cấu trúc thông tin có ngữ nghĩa trước khi chuyển giao cho Policy Agent và Verifier Agent.
2. **Sự khác biệt giữa kiểm soát dữ liệu thô và việc ra quyết định nghiệp vụ?**
   Các Worker Agent (Customer, Order, Payment, Delivery) chỉ thực hiện các phép toán deterministic trên dữ liệu thô (so khớp ID, tính thời gian lệch, tính tổng tiền). Trong khi đó, Policy Agent là nơi áp dụng cây quyết định của `EC_POLICY_V2` để phân loại và LLM chỉ đóng vai trò kiểm toán và chấm điểm tin cậy dựa trên tin nhắn ngôn ngữ tự nhiên của khách hàng.
3. **Tại sao cần sử dụng Pydantic để xác thực schema đầu ra thay vì chỉ tin tưởng vào LLM?**
   LLM có tính chất ngẫu nhiên (non-deterministic) và có khả năng trả về sai kiểu dữ liệu, thiếu trường hoặc vi phạm độ dài mảng tối đa quy định. Pydantic đóng vai trò là chốt chặn cuối cùng (guardrail) bắt buộc định dạng đầu ra phải đúng 100% trước khi lưu file.
4. **Ý nghĩa của trace log (trace.jsonl) trong việc giám sát hoạt động của các Agent?**
   `trace.jsonl` ghi vết chính xác đầu ra của từng bước phân tích của từng Agent con. Điều này giúp lập trình viên và người vận hành hệ thống dễ dàng debug, biết lỗi phát sinh từ Agent nào (ví dụ: phát hiện lỗi tính sai tiền hoặc sai lệch ngày tháng) thay vì chỉ nhìn thấy file kết quả cuối cùng.

---

## 8. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Châu Thanh
**Ngày xác nhận:** 2026-08-05

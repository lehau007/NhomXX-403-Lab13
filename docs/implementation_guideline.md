# Hướng dẫn Triển khai chi tiết (Implementation Guideline)

Dưới đây là checklist các bước thực hiện cụ thể (nhắm vào các file cần sửa) cho từng thành viên.

---

## 🧑‍💻 Thành viên 1: Core Instrumentation (Logging, PII & Tracing)

**Nhiệm vụ chính:** Giải quyết các `TODO` trong thư mục `app/`.

1.  **Bước 1: Correlation ID (Truy vết request)**
    *   **File:** `app/middleware.py`
    *   **Hành động:** Tìm TODO. Khởi tạo một `uuid4` làm `request_id`. Thêm nó vào header của response `x-request-id` và đưa nó vào context của logger hiện tại.
2.  **Bước 2: Structured & Enriched Logging (Làm giàu Log)**
    *   **File:** `app/main.py`
    *   **Hành động:** Chỉnh sửa code khởi tạo FastAPI hoặc các route để bind (gắn thêm) các thông tin cố định vào log (ví dụ: `user_id`, `session_id`, `feature_name` nếu có trong payload hoặc headers).
3.  **Bước 3: PII Scrubbing (Ẩn thông tin nhạy cảm)**
    *   **File:** `app/logging_config.py` (và có thể là `app/pii.py`)
    *   **Hành động:** Tìm TODO về PII. Sử dụng Regex (ví dụ: tìm mẫu email, số điện thoại, thẻ tín dụng) để thay thế dữ liệu thật bằng các ký tự ẩn (ví dụ: `***@***.com` hoặc `[REDACTED]`) trước khi log được in ra.
4.  **Bước 4: Langfuse Tracing**
    *   **File:** `app/tracing.py` và `app/agent.py`
    *   **Hành động:** Import thư viện Langfuse. Bọc (wrap) các function xử lý chính (LLM call, RAG retrieval) bằng decorator `@observe()` của Langfuse để theo dõi độ trễ, token usage.
5.  **Nghiệm thu:**
    *   Chạy lệnh: `python scripts/validate_logs.py`
    *   Đảm bảo script trả về thành công, log không chứa thông tin nhạy cảm thật. Mở web Langfuse xem đã có dữ liệu traces đổ về chưa.

---

## 🕵️ Thành viên 2: Reliability & Testing (SLOs, Alerts & Load Testing)

**Nhiệm vụ chính:** Làm việc với thư mục `config/` và `scripts/`.

1.  **Bước 1: Cấu hình Alert Rules (Cảnh báo)**
    *   **File:** `config/alert_rules.yaml`
    *   **Hành động:** Dựa vào file mẫu, viết thêm các quy tắc cảnh báo. (Ví dụ: Alert khi số lượng lỗi HTTP 500 > 5 trong vòng 1 phút, hoặc thời gian phản hồi (latency) > 2 giây).
2.  **Bước 2: Cấu hình SLOs**
    *   **File:** `config/slo.yaml`
    *   **Hành động:** Định nghĩa rõ ràng SLI (Service Level Indicator) và SLO. Ví dụ: Mục tiêu 99% requests phản hồi dưới 500ms.
3.  **Bước 3: Chạy Load Test (Tạo Traffic)**
    *   **File:** `scripts/load_test.py`
    *   **Hành động:** Chạy lệnh `python scripts/load_test.py --concurrency 5`. Theo dõi xem hệ thống có chịu được tải hay bắt đầu nghẽn. Ghi chú lại giới hạn.
4.  **Bước 4: Mô phỏng sự cố (Incident Injection)**
    *   **File:** `scripts/inject_incident.py`
    *   **Hành động:** Chạy lệnh `python scripts/inject_incident.py --scenario rag_slow`. Hệ thống sẽ bị tiêm lỗi chậm RAG.
    *   **Phối hợp:** Thông báo cho Thành viên 3 quan sát dashboard xem có spike (đỉnh nhọn) nào về thời gian phản hồi hay số lượng log lỗi (Error Rate) tăng vọt không.

---

## 📊 Thành viên 3: Visualization & Reporting (Dashboard, Evidence & Demo)

**Nhiệm vụ chính:** Làm việc chủ yếu với thư mục `docs/` và công cụ tạo Dashboard.

1.  **Bước 1: Thiết kế Dashboard (Giao diện giám sát)**
    *   **File tham chiếu:** `docs/dashboard-spec.md`
    *   **Hành động:** Dựa trên metric sinh ra từ app, cấu hình một Dashboard (có thể dùng Grafana, Datadog, hoặc Langfuse UI nếu hỗ trợ đủ). Đảm bảo phải có đủ **6 panels** (Ví dụ: Request Rate, Error Rate, Latency p95, Token Usage, Active Traces, ...).
2.  **Bước 2: Chụp bằng chứng (Evidence Collection)**
    *   **File:** `docs/grading-evidence.md`
    *   **Hành động:** Khi Thành viên 2 bơm traffic và tiêm lỗi, hãy chụp lại màn hình:
        *   Dashboard hiển thị lỗi rõ ràng.
        *   Traces chi tiết trên Langfuse chỉ ra đúng hàm nào đang bị chậm/lỗi.
        *   Log JSON đã được làm mờ PII.
    *   Chèn các link ảnh và text log chứng minh vào file này.
3.  **Bước 3: Viết Báo cáo Blueprint & Phân tích Sự cố (RCA)**
    *   **File:** `docs/blueprint-template.md`
    *   **Hành động:** Điền chi tiết kiến trúc của ứng dụng. Ở phần Incident Response (10 điểm), mô tả chi tiết: Sự cố `rag_slow` lúc nãy là gì? Làm sao phát hiện (nhờ alert/dashboard)? Nguyên nhân gốc rễ thấy trên trace là gì? Và đề xuất cách khắc phục.
4.  **Bước 4: Chuẩn bị Demo**
    *   Soạn ra vài gạch đầu dòng để trình bày với giảng viên: Ai làm phần nào, show code ở đâu, thực hiện chạy script lỗi live trên máy và mở dashboard chứng minh. Mở Langfuse show ra 1 trace hoàn chỉnh.

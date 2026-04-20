# Dashboard Spec (Hướng dẫn thiếp lập 6 Panels)

Dưới đây là đặc tả (Specification) và hướng dẫn dành cho Thành viên 3 để cấu hình Dashboard giám sát hệ thống. Bạn có thể sử dụng giao diện Langfuse UI (Analytics) hoặc Grafana.

## Danh sách 6 biểu đồ (Panels) bắt buộc

1. **Latency P50/P95/P99 (Thời gian phản hồi)**
   * **Mục đích:** Theo dõi độ trễ của Agent. Phát hiện ngay lập tức khi hệ thống bị chậm (như sự cố `rag_slow`).
   * **Dữ liệu nguồn:** Giá trị `latency_ms` từ Trace API của Langfuse hoặc Logs.
   * **Kiểu biểu đồ:** Line chart (Đường kẻ).

2. **Traffic / Request Rate (Lưu lượng truy cập)**
   * **Mục đích:** Biết được hệ thống đang phục vụ bao nhiêu request (QPS - Queries Per Second) hoặc tổng số request trong khoảng thời gian.
   * **Dữ liệu nguồn:** Đếm tổng số Traces hoặc tổng log `request_received`.
   * **Kiểu biểu đồ:** Bar chart hoặc Line chart.

3. **Error rate with breakdown (Tỷ lệ lỗi)**
   * **Mục đích:** Theo dõi tỷ lệ phần trăm request bị lỗi (HTTP 500) so với request thành công.
   * **Dữ liệu nguồn:** Đếm các log có `level="error"` hoặc trace có HTTP status != 200.
   * **Kiểu biểu đồ:** Stacked bar chart hoặc Gauge.

4. **Cost over time (Chi phí Model theo thời gian)**
   * **Mục đích:** Quản lý ngân sách sử dụng LLM API (Claude/OpenAI).
   * **Dữ liệu nguồn:** Tổng hợp biến `cost_usd` từ log `response_sent`.
   * **Kiểu biểu đồ:** Bar chart (nhóm theo giờ/ngày).

5. **Tokens in/out (Sử dụng Token)**
   * **Mục đích:** Đo lường lượng prompt token (in) và completion token (out) để xem context window có bị phình to không.
   * **Dữ liệu nguồn:** Tổng hợp `tokens_in` và `tokens_out` từ log.
   * **Kiểu biểu đồ:** Line chart (2 đường).

6. **Quality proxy (Chất lượng phản hồi)**
   * **Mục đích:** Đánh giá điểm chất lượng của LLM (dựa trên thuật toán heuristic hoặc user feedback).
   * **Dữ liệu nguồn:** Giá trị `quality_score`.
   * **Kiểu biểu đồ:** Gauge (Đồng hồ đo) hoặc Line chart.

---

## Tiêu chuẩn chất lượng (Quality Bar)

Khi chụp ảnh màn hình nộp bài (Evidence), hãy đảm bảo Dashboard thỏa mãn các yêu cầu sau:
- Khung thời gian (Time range) hiển thị: **1 hour (1 giờ qua)**.
- Đang bật chế độ tự động làm mới (Auto refresh) mỗi **15-30 giây**.
- Có vẽ thêm đường ngang cảnh báo đỏ (Threshold/SLO line). Ví dụ: Đường gạch đứt tại vạch `3000ms` cho biểu đồ Latency.
- Trục X, Y có đơn vị đo lường rõ ràng (ms, $, số đếm).
- Sắp xếp gọn gàng: Tổng cộng khoảng 6-8 panels nằm vừa trên 1 màn hình Layer-2.

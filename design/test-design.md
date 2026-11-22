# Thiết kế Kịch bản Đo kiểm Hiệu năng (Test Design)

**MSSV:** 23120127  
**Ngày thực hiện:** 2026-11-22  
**Mục tiêu:** Thiết lập cấu hình đo kiểm chuẩn hóa cho 3 kịch bản Load, Stress, Spike và bài đo mở rộng Soak trên hệ thống E-Shop SUT.

---

## 1. Workflow Cố định và Chi tiết 6 Request

Hệ thống sử dụng chung một workflow gồm 6 request với các thông số cấu hình kỹ thuật:

| STT | Nhãn Sampler | Phương thức | Endpoint | Header | Body (JSON) | Trích xuất / Correlation | Kiểm tra (Assertions) |
|---|---|---|---|---|---|---|---|
| 1 | `01_login` | `POST` | `/api/login` | `Content-Type: application/json` | `{"email": "${email}", "password": "${password}"}` | `token = $.token` | Response Code 200, JSON Assertion `$.user.role == "admin"` |
| 2 | `02_categories_list` | `GET` | `/api/categories` | `Authorization: Bearer ${token}` | *(Không có)* | *(Không có)* | Response Code 200 |
| 3 | `03_products_list` | `GET` | `/api/products` | *(Không có)* | *(Không có)* | *(Không có)* | Response Code 200 |
| 4 | `04_category_create` | `POST` | `/api/categories` | `Content-Type: application/json`, `Authorization: Bearer ${token}` | `{"name": "${categoryName}"}` | `categoryId = $.id` | Response Code 200, JSON Assertion `$.id` tồn tại |
| 5 | `05_category_update` | `PUT` | `/api/categories/${categoryId}` | `Content-Type: application/json`, `Authorization: Bearer ${token}` | `{"name": "${categoryName}_updated"}` | *(Không có)* | Response Code 200 |
| 6 | `06_category_delete` | `DELETE` | `/api/categories/${categoryId}` | `Authorization: Bearer ${token}` | *(Không có)* | *(Không có)* | Response Code 200 |

### 1.1 Quy tắc sinh dữ liệu & Trích xuất (Correlation)
- **Tài khoản:** Nạp từ CSV tương đối `../data/admin${__threadNum}.csv` với các biến `email,password,category_prefix`.
- **Tên danh mục duy nhất:** Mỗi iteration sinh động biến `categoryName` bằng cú pháp `${category_prefix}_${__time(yyyyMMddHHmmss,)}_${__UUID()}` nhằm chống trùng lặp tuyệt đối giữa các VU và các lần lặp.
- **Correlation:**
  - Token JWT trích xuất từ `$.token` tại bước 1, truyền vào `Authorization: Bearer ${token}` ở các bước 2, 4, 5, 6.
  - `categoryId` trích xuất từ `$.id` tại bước 4, truyền vào URL của bước 5 và 6.

### 1.2 Xử lý phân nhánh lỗi & Rác dữ liệu
- **Lỗi Login:** Nếu bước 1 thất bại hoặc không trích xuất được `token`, JMeter được cấu hình chuyển ngay sang vòng lặp tiếp theo (`Start Next Thread Loop`) để tránh gửi các request rác không có token gây lỗi 401 giả tạo và giảm nguy cơ chạm ngưỡng khóa tài khoản 180s.
- **Lỗi Tạo Category:** Sử dụng bộ điều khiển If Controller kiểm tra `"${categoryId}" != ""`. Nếu bước 4 thất bại, không thực hiện bước 5 và 6 với ID rác.
- **Dọn dẹp (Cleanup):** Bước 6 xóa trực tiếp danh mục vừa tạo. Số lượng bản ghi `categories` sẽ được kiểm tra trước và sau mỗi đợt đo bằng script độc lập để phát hiện rác dữ liệu.

---

## 2. Thiết kế Workload cho 3 Kịch bản Chính và Soak

*(Lưu ý: Mọi thông số tải và ngưỡng đề xuất bên dưới là GIẢ THUYẾT ĐO, cần được hiệu chỉnh qua smoke test và calibration).*

### 2.1 Load Test (`23120127_Load_20261122.jmx`)
- **Mục đích:** Đánh giá tính ổn định và thời gian phản hồi của hệ thống dưới tải thông thường.
- **VU (Virtual Users):** Mặc định 20 VU, hỗ trợ tham số hóa qua biến JMeter Property `${__P(vus,20)}`.
- **Ramp-up:** Mặc định 60 giây (`${__P(ramp,60)}`).
- **Thời gian giữ tải (Duration):** Mặc định 480 giây (8 phút, trong đó ~7 phút giữ tải ổn định) (`${__P(duration,480)}`).
- **Think-time:** Uniform Random Timer với khoảng trễ 1000ms đến 3000ms giữa các request.
- **Listener chính:** `Summary Report` (`SummaryReport`).

### 2.2 Stress Test (`23120127_Stress_20261122.jmx`)
- **Mục đích:** Tìm điểm gãy (breaking point) hoặc suy giảm hiệu năng của hệ thống dưới các mức tải tăng dần.
- **Cấu trúc:** Thực thi tuần tự 4 Thread Group liên tiếp (`serialize_threadgroups = true`):
  1. Mức 1: 10 VU (Ramp-up 15s, Duration 120s).
  2. Mức 2: 20 VU (Ramp-up 15s, Duration 120s).
  3. Mức 3: 40 VU (Ramp-up 15s, Duration 120s).
  4. Mức 4: 80 VU (Ramp-up 15s, Duration 120s).
- **Think-time:** 1000ms – 3000ms.
- **Listener chính:** `Aggregate Report` (`StatVisualizer`).

### 2.3 Spike Test (`23120127_Spike_20261122.jmx`)
- **Mục đích:** Đánh giá khả năng chống chịu khi tải tăng đột biến tức thì và khả năng tự hồi phục sau đột biến.
- **Cấu trúc lõi (Core JMeter - 3 Thread Groups tuần tự):**
  1. Giai đoạn nền (Base): 10 VU (Ramp-up 10s, Duration 120s).
  2. Giai đoạn đột biến (Spike): 80 VU (Ramp-up 5s, Duration 60s).
  3. Giai đoạn hồi phục (Recovery): 10 VU (Ramp-up 5s, Duration 120s).
- **Think-time:** 1000ms – 3000ms.
- **Listener chính:** `View Results Tree` (`ViewResultsFullVisualizer`) được tắt (`enabled="false"`) khi chạy tải CLI và chỉ bật phục vụ debug 1 VU hoặc xem lại file kết quả.

### 2.4 Soak Test (Tái sử dụng Load plan)
- Chạy plan Load với tham số dòng lệnh: `-Jvus=<mức_ổn_định> -Jramp=60 -Jduration=900` (giữ tải 15 phút).

---

## 3. Tiêu chí Đánh giá Ổn định Trước Đo (Hypotheses)

Hệ thống được coi là đạt tiêu chuẩn chấp nhận ban đầu nếu:
1. **Tỷ lệ lỗi:** Error rate tổng thể $\le 1\%$, không xuất hiện mã lỗi 500 (Internal Server Error) hay lỗi crash Node.js.
2. **Thời gian đáp ứng (Response Time):**
   - Đọc (`02_categories_list`, `03_products_list`): $p95 \le 500\text{ ms}$.
   - Xác thực & Ghi (`01_login`, `04_category_create`, `05_category_update`, `06_category_delete`): $p95 \le 2000\text{ ms}$.
3. **Bộ nhớ & Tài nguyên:** Bộ nhớ RAM của `node.exe` không tăng liên tục không giới hạn (không rò rỉ bộ nhớ nghiêm trọng).
4. **Tính toàn vẹn dữ liệu:** Không phát sinh bản ghi mồ côi (orphan categories) sau khi hoàn tất phiên kiểm thử.

---

## 4. Các Giả định Kỹ thuật và Rủi ro Chưa Xác minh

1. **Rủi ro phân loại "Transactional":** Đề bài minh họa transactional qua giỏ hàng/thanh toán. Nhóm endpoint `POST/PUT/DELETE /api/categories` thực chất là thao tác ghi dữ liệu quản trị (Write/CRUD), cần xác nhận lại nếu giảng viên yêu cầu bắt buộc phải là luồng checkout.
2. **Khóa ghi SQLite:** SQLite khóa toàn bộ file cơ sở dữ liệu khi có giao dịch ghi. Dưới tải 40–80 VU đồng thời, có thể xuất hiện lỗi `SQLITE_BUSY` ở bước 4.
3. **Trùng lặp workflow trong nhóm:** Cần sự xác nhận độc lập từ các thành viên khác trong nhóm để đảm bảo không bị trùng lặp workflow kiểm thử.

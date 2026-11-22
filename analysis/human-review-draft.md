# Human Review & AI Misinterpretation Hunt — HW05

**Student:** 23120127  
**Artifact Analyzed:** `hw05-work/analysis/ai-first-pass.md`  
**Ground-Truth Sources:** `results/{load,stress,spike,soak}/*.jtl`, `scripts/analyze_jtl.py`, `analysis/jtl-metrics-ground-truth.json`, `analysis/edge-cases.json`, SUT source code (`src/eshop-sut/backend/{server.js,database.js}`).

---

## 1. AI Misinterpretation Hunt Table

Dưới đây là bảng đối chiếu từng nhận định sai lệch hoặc gây hiểu nhầm trong bản phân tích đầu tiên của AI (`ai-first-pass.md`) với dữ liệu log thô và nguyên nhân kỹ thuật thực tế:

| STT | Khẳng định nguyên văn của AI | Giá trị đúng từ JTL thô / Log thực tế | File nguồn / Cửa sổ / n mẫu | Công thức / Phép tính | Nguyên nhân AI sai / hiểu nhầm |
|---|---|---|---|---|---|
| **1** | *"Overall test p95 is 18 ms. The backend handled 80 VU without breaking, and latency scaled smoothly with load."* | **Tầng 80 VU có p95 toàn cục = 23 ms**; các thao tác ghi có p95 từ **28–32 ms** và p99 DELETE lên tới **152 ms**. (Chỉ riêng tầng 10 VU và 20 VU mới có p95 = 8 ms; tầng 40 VU có p95 = 9 ms). | `results/stress/stress.jtl`, Thread Group `TG_Stress_Level_4_80VU`, n = 4.491. | Sắp xếp 4.491 giá trị elapsed của tầng 80 VU: vị trí ceil(0.95 * 4491) = 4267 cho kết quả 23 ms. Với `06_category_delete`: ceil(0.95 * 716) = 681 cho kết quả 32 ms, p99 là 152 ms. | **Ngụy biện gộp mẫu (Aggregation bias):** AI lấy p95 trên toàn bộ file JTL (8.364 mẫu gồm cả 3 tầng tải thấp 10, 20, 40 VU) để che mờ độ trễ tăng vọt ở tầng tải cao nhất 80 VU. |
| **2** | *"The throughput achieved is approximately 9.40 transactions per second for the application." (ở mục Load)* | **Throughput giao dịch nghiệp vụ (Business Workflows) chỉ đạt ~1,55 workflow/giây.** Con số 9,404 chỉ là **Request Throughput** (gross HTTP requests/second). | `results/load/load.jtl`, n = 4.499 mẫu trong 478,41 giây. | Một workflow hoàn chỉnh gồm 6 HTTP request tuần tự. Thao tác hoàn tất cuối cùng `06_category_delete` có n = 741 mẫu trong 478,41 s → 741 / 478.41 ≈ 1.549 workflow/s. | **Đánh đồng Request với Transaction/Workflow:** AI nhầm lẫn giữa số lượng HTTP request đơn lẻ với số lượng chu trình nghiệp vụ hoàn tất (end-to-end transactions). |
| **3** | *"Node.js v25 garbage collection effectively cleaned up unreferenced heap buffers under high throughput, proving that Node.js operates with a memory ceiling of around 32.4 MiB without memory leaks."* | **Node.js Private Memory giữ quanh 95–96 MiB (Max 96,45 MiB).** RSS giảm xuống 32,38 MiB không chứng minh GC hay trần bộ nhớ 32 MiB. | `results/soak/resources.csv`, cửa sổ 17:21:33 – 17:32:03 (630s), n = 127 mẫu monitor. | Tại 17:31:10, cả `node_rss_mib` lẫn `jmeter_rss_mib` giảm mạnh đồng thời, trong khi `node_private_mib` gần như giữ nguyên. | **Ngộ nhận cơ chế bộ nhớ:** Diễn biến phù hợp với Windows working-set trim, nhưng số liệu không chứng minh nguyên nhân. 96,45 MiB là mức cao nhất đã thấy, chưa phải trần bộ nhớ. |
| **4** | *"A short gap of ~2 seconds between Phase 2 and Phase 3 indicates a brief recovery delay before resuming traffic."* | Khoảng trống 2,155 giây giữa Peak và Recovery bao gồm chuyển Thread Group và think-time của JMeter; không đủ căn cứ xác định thời gian backend hồi phục. | `results/spike/spike.jtl`, timestamp giữa sampler cuối Phase 2 và sampler đầu Phase 3. | `TG_Spike_Phase_2` kết thúc ở epoch ms 1795342797686; `TG_Spike_Phase_3` bắt đầu ở 1795342799841. Chênh lệch 2.155 ms. | **Suy diễn sai hiện tượng công cụ thành lỗi hệ thống:** khoảng không có sampler không phải phép đo downtime. |
| **5** | *"Across all four runs, the recorded HTTP response code was uniformly 200 OK with a 0.00% error rate... zero degradation."* | **HTTP 200 không đảm bảo 100% nghiệp vụ thành công:** Có **6 (Load), 49 (Stress), 43 (Spike), 24 (Soak) Category rác bị bỏ lại** do scheduler dừng giữa chừng. Ngoài ra, API DELETE/PUT trả 200 ngay cả khi ID không tồn tại. | `results/*/categories_after.csv` và `analysis/edge-cases.json` (C09). | Đếm số bản ghi trong bảng `categories` sau mỗi run: trước run = 3, sau run tăng thêm từ 6 đến 49 bản ghi chưa được DELETE. Thử nghiệm C09: `DELETE /api/categories/2147483647` trả HTTP 200 `{"message":"Category deleted"}` dù không xóa dòng nào. | **Thiên kiến dựa vào mã HTTP (HTTP status code bias):** AI chỉ kiểm tra `success=true` / `status=200` của JMeter mà không đối chiếu tính toàn vẹn trạng thái dữ liệu (Data Integrity) trong CSDL backend. |

---

## 2. Đánh giá tính khả thi các đề xuất tối ưu hóa (Optimization Feasibility)

| Đề xuất của AI | Phân loại | Căn cứ mã nguồn / Dữ liệu thực nghiệm | Kế hoạch đo kiểm A/B nếu khả thi |
|---|---|---|---|
| **1. Thêm Index trên bảng `categories` (`name`, `id`)** | **Không có căn cứ cho workload này** | Schema thực tế là `id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT`. Khóa chính `id` đã có đường truy cập theo rowid trong SQLite; các thao tác UPDATE/DELETE dùng `WHERE id = ?`. Không thấy truy vấn `WHERE name = ?` trong workflow. Index `name` có chi phí ghi và cần query plan/benchmark mới kết luận lợi ích. | Chỉ thử nếu bổ sung truy vấn tìm theo tên; dùng `EXPLAIN QUERY PLAN` và so thời gian đọc/ghi. |
| **2. Cấu hình Connection Pool cho SQLite (generic-pool size 10–20)** | **Chưa có căn cứ; không nên áp dụng nguyên đề xuất** | SQLite là CSDL tệp nhúng và SUT đang dùng một đối tượng `sqlite3.Database`. Có thể mở nhiều connection về mặt kỹ thuật, nhưng pool 10–20 chưa được chứng minh giúp workflow đọc/ghi này; có thể tăng tranh chấp writer. | Nếu thử, so p95/p99, `SQLITE_BUSY`, CPU và throughput với cấu hình hiện tại. |
| **3. Bật chế độ SQLite WAL (Write-Ahead Logging)** | **Khả thi, hiệu quả chưa được đo** | WAL có thể cải thiện đồng thời đọc/ghi. JTL chỉ cho thấy DELETE p99 = 152 ms ở 80 VU, chưa chứng minh nguyên nhân do khóa SQLite. | So Stress 80 VU cùng tham số, seed DB và phần cứng trước/sau khi bật WAL; theo dõi p95/p99, `SQLITE_BUSY` và throughput. |
| **4. Thêm B-Tree Index cho `users(email)`** | **Khả thi khi dữ liệu tăng; chưa cần với 102 user** | Schema thực tế là `email TEXT` (không có `UNIQUE` hay index). Login truy vấn theo `email`, nên index có thể giảm scan khi bảng lớn hơn. Chưa có benchmark đủ lớn để khẳng định mức cải thiện. | Tạo dữ liệu thử trong bản DB sao chép, dùng `EXPLAIN QUERY PLAN`, rồi so p95 và CPU trước/sau index. |
| **5. Giảm Think-Time từ 1–3s xuống 100–300ms** | **Khả thi cho thí nghiệm tải bổ sung** | Mức 80 VU hiện tại tạo khoảng 40 req/s; giảm think-time sẽ tăng tốc độ gửi nhưng **chưa thể dự đoán 150–200 req/s** khi chưa chạy. Kết quả khi đó không còn đại diện cho pacing ban đầu. | Chạy riêng với 80 VU, think-time 100–300 ms; đo RPS, lỗi, CPU và p95/p99. |

---

## 3. Dự thảo hai GitHub Issues và một quan sát cần làm rõ (C07, C08, C09)

**Trạng thái:** Chưa đăng Issues; chưa có ảnh chụp tái hiện. Cần chụp màn hình kết quả thử nghiệm và đính kèm khi đăng C07/C08.

### Issue 1: Lỗi nghiệp vụ Khóa tài khoản (Account Lockout)
* **Tiêu đề:** `[BUG] Account Lockout locks account after only 2 failed attempts and sets 180s duration instead of spec FR-02`
* **Mức độ:** High (Sai lệch đặc tả yêu cầu chức năng)
* **File liên quan:** `src/eshop-sut/backend/server.js` (Route `POST /api/login`)
* **Mô tả:**
  * Theo đặc tả `FR-02`: Hệ thống phải khóa tài khoản sau **3 lần đăng nhập sai liên tiếp** trong khoảng thời gian **30 giây**.
  * Hành vi thực tế: Mã nguồn tăng biến đếm `login_attempts += 2` trong mỗi lần sai (`server.js` line ~86). Do đó, chỉ sau **2 lần đăng nhập sai**, biến đếm đạt giá trị 4 (vượt ngưỡng ≥ 3) và kích hoạt khóa tài khoản. Ngoài ra, thời gian khóa được gán là `Date.now() + 180 * 1000` (**180 giây** thay vì 30 giây).
* **Bằng chứng tái hiện:** Đã chạy script `probe_edge_cases.py`, kết quả lưu tại `analysis/edge-cases.json` (C07):
  * Lần 1: Sai mật khẩu → HTTP 401
  * Lần 2: Sai mật khẩu → HTTP 401 (`login_attempts` trong DB = 4)
  * Lần 3: Dùng đúng mật khẩu → Bị chặn HTTP 403: `"Tài khoản đã bị khóa. Vui lòng thử lại sau."`

### Issue 2: Lỗ hổng bảo mật Phân quyền danh mục (Authorization Bypass)
* **Tiêu đề:** `[SECURITY] Regular user tokens can create, modify, and delete categories (Violation of FR-12)`
* **Mức độ:** Critical (Lỗ hổng phân quyền truy cập)
* **File liên quan:** `src/eshop-sut/backend/server.js` (`/api/categories` POST/PUT/DELETE)
* **Mô tả:**
  * Theo đặc tả `FR-12` & `FR-14`: Quản lý danh mục (Category CRUD) là chức năng thuộc Web Admin (Pool C), bắt buộc phải có quyền Quản trị viên (`role === 'admin'`).
  * Hành vi thực tế: Các route POST, PUT, DELETE `/api/categories` chỉ sử dụng middleware `authenticateToken` để kiểm tra tính hợp lệ của JWT, nhưng **hoàn toàn bỏ quên middleware kiểm tra quyền `requireAdmin`**.
* **Bằng chứng tái hiện:** Thử nghiệm C08 trong `analysis/edge-cases.json`:
  * Tạo JWT với payload `role: 'user'` (tài khoản người mua hàng thông thường).
  * Gửi `POST /api/categories` với body `{"name":"Hacked Category"}` → Trả về **HTTP 200 OK**, `id: 7345`.
  * Gửi PUT và DELETE với token user → Đều trả về **HTTP 200 OK**.

### Quan sát C09: Xử lý ID không tồn tại
* **Tiêu đề:** `[API] PUT and DELETE /api/categories/:id return 200 OK when category ID does not exist`
* **Mức độ:** Hành vi API cần xác nhận với đặc tả; chưa phân loại bug
* **File liên quan:** `src/eshop-sut/backend/server.js`
* **Mô tả:** Khi gửi request cập nhật hoặc xóa với ID không tồn tại trong CSDL (ví dụ `id = 2147483647`), API trả về `HTTP 200 OK` với thông báo `Category updated` / `Category deleted`. Không có dòng nào thay đổi. API spec chưa quy định mã trạng thái cho trường hợp này; 404 là đề xuất cải thiện cần xác nhận.


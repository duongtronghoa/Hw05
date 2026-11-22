# Human Review & AI Misinterpretation Hunt — HW05

**Student:** 23120127  
**Artifact Analyzed:** `hw05-work/analysis/ai-first-pass.md`  
**Ground-Truth Sources:** `results/{load,stress,spike,soak}/*.jtl`, `scripts/analyze_jtl.py`, `analysis/jtl-metrics-ground-truth.json`, `analysis/edge-cases.json`, SUT source code (`src/eshop-sut/backend/{server.js,database.js}`).

---

## 1. AI Misinterpretation Hunt Table

Dưới đây là bảng đối chiếu từng nhận định sai lệch hoặc gây hiểu nhầm trong bản phân tích đầu tiên của AI (`ai-first-pass.md`) với dữ liệu log thô và nguyên nhân kỹ thuật thực tế:

| STT | Khẳng định nguyên văn của AI | Giá trị đúng từ JTL thô / Log thực tế | File nguồn / Cửa sổ / n mẫu | Công thức / Phép tính | Nguyên nhân AI sai / hiểu nhầm |
|---|---|---|---|---|---|
| **1** | *"Overall test p95 is 18 ms. The backend handled 80 VU without breaking, and latency scaled smoothly with load."* | **Tầng 80 VU có p95 toàn cục = 23 ms**; các thao tác ghi có p95 từ **28–32 ms** và p99 DELETE lên tới **152 ms**. (Chỉ riêng tầng 10 VU và 20 VU mới có p95 = 8 ms; tầng 40 VU có p95 = 9 ms). | `results/stress/stress.jtl`, Thread Group `TG_Stress_Level_4_80VU`, n = 4.491. | Sắp xếp 4.491 giá trị elapsed của tầng 80 VU: vị trí $\lceil 0,95 \times 4491 \rceil = 4267$ cho kết quả 23 ms. Với `06_category_delete`: $\lceil 0,95 \times 716 \rceil = 681$ cho kết quả 32 ms, p99 là 152 ms. | **Ngụy biện gộp mẫu (Aggregation bias):** AI lấy p95 trên toàn bộ file JTL (8.364 mẫu gồm cả 3 tầng tải thấp 10, 20, 40 VU) để che mờ độ trễ tăng vọt ở tầng tải cao nhất 80 VU. |
| **2** | *"The throughput achieved is approximately 9.40 transactions per second for the application." (ở mục Load)* | **Throughput giao dịch nghiệp vụ (Business Workflows) chỉ đạt ~1,55 workflow/giây.** Con số 9,404 chỉ là **Request Throughput** (gross HTTP requests/second). | `results/load/load.jtl`, n = 4.499 mẫu trong 478,41 giây. | Một workflow hoàn chỉnh gồm 6 HTTP request tuần tự. Thao tác hoàn tất cuối cùng `06_category_delete` có n = 741 mẫu trong 478,41 s $\rightarrow 741 / 478,41 \approx 1,549$ workflow/s. | **Đánh đồng Request với Transaction/Workflow:** AI nhầm lẫn giữa số lượng HTTP request đơn lẻ với số lượng chu trình nghiệp vụ hoàn tất (end-to-end transactions). |
| **3** | *"Node.js v25 garbage collection effectively cleaned up unreferenced heap buffers under high throughput, proving that Node.js operates with a memory ceiling of around 32.4 MiB without memory leaks."* | **Node.js Private Memory thực tế giữ ổn định ở mức 95,82 $\rightarrow$ 95,65 MiB (Max 96,45 MiB).** Việc RSS giảm xuống 32,38 MiB lúc 17:31:10 là do **Windows OS Working-Set Trim**, không phải GC hay "trần bộ nhớ" 32 MiB. | `results/soak/resources.csv`, cửa sổ 17:21:33 – 17:32:03 (630s), n = 127 mẫu monitor. | Tại 17:31:10, cả `node_rss_mib` (92 $\rightarrow$ 32 MiB) lẫn `jmeter_rss_mib` (640 $\rightarrow$ 180 MiB) đều bị giảm mạnh đồng thời, trong khi `node_private_mib` không hề giảm (giữ nguyên ~95,6 MiB). | **Ngộ nhận cơ chế bộ nhớ:** AI chỉ nhìn cột RSS (Working Set) và suy đoán chủ quan về GC của V8 engine, trong khi RSS chịu sự thu hồi trang vật lý của Windows OS khi có tiến trình khác đòi bộ nhớ. Trần bộ nhớ thực tế phải dựa vào Private Bytes (~96 MiB). |
| **4** | *"A short gap of ~2 seconds between Phase 2 and Phase 3 indicates a brief recovery delay before resuming traffic."* | Khoảng trống 2,155 giây giữa timestamp của Peak 80 VU và Recovery 10 VU là **độ trễ tuần tự giữa 2 Thread Group của JMeter**, hoàn toàn **không phải server bị downtime hay trễ hồi phục**. | `results/spike/spike.jtl`, timestamp giữa sampler cuối Phase 2 và sampler đầu Phase 3. | `TG_Spike_Phase_2` kết thúc ở epoch ms 1795342797686; `TG_Spike_Phase_3` bắt đầu ở 1795342799841. Khoảng cách = 2.155 ms = thời gian JMeter tear down nhóm cũ và khởi động nhóm mới + UniformRandomTimer (1–3s). | **Suy diễn sai hiện tượng công cụ thành lỗi hệ thống:** AI coi khoảng chờ giữa hai nhóm luồng JMeter độc lập là sự suy giảm năng lực xử lý của backend. |
| **5** | *"Across all four runs, the recorded HTTP response code was uniformly 200 OK with a 0.00% error rate... zero degradation."* | **HTTP 200 không đảm bảo 100% nghiệp vụ thành công:** Có **6 (Load), 49 (Stress), 43 (Spike), 24 (Soak) Category rác bị bỏ lại** do scheduler dừng giữa chừng. Ngoài ra, API DELETE/PUT trả 200 ngay cả khi ID không tồn tại. | `results/*/categories_after.csv` và `analysis/edge-cases.json` (C09). | Đếm số bản ghi trong bảng `categories` sau mỗi run: trước run = 3, sau run tăng thêm từ 6 đến 49 bản ghi chưa được DELETE. Thử nghiệm C09: `DELETE /api/categories/2147483647` trả HTTP 200 `{"message":"Category deleted"}` dù không xóa dòng nào. | **Thiên kiến dựa vào mã HTTP (HTTP status code bias):** AI chỉ kiểm tra `success=true` / `status=200` của JMeter mà không đối chiếu tính toàn vẹn trạng thái dữ liệu (Data Integrity) trong CSDL backend. |

---

## 2. Đánh giá tính khả thi các đề xuất tối ưu hóa (Optimization Feasibility)

| Đề xuất của AI | Phân loại | Căn cứ mã nguồn / Dữ liệu thực nghiệm | Kế hoạch đo kiểm A/B nếu khả thi |
|---|---|---|---|
| **1. Thêm Index trên bảng `categories` (`name`, `id`)** | **Hallucinated (Ảo tưởng / Vô nghĩa)** | Bảng `categories` trong `src/eshop-sut/backend/database.js` có schema: `id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL`. Trong SQLite, `PRIMARY KEY` tự động được đánh B-Tree index. Mọi thao tác UPDATE/DELETE đều dùng `WHERE id = ?`. Cột `name` không hề có câu truy vấn tìm kiếm `WHERE name = ?`. Do đó index thêm là lãng phí tài nguyên ghi. | Không khả thi; không cần thử nghiệm. |
| **2. Cấu hình Connection Pool cho SQLite (generic-pool size 10–20)** | **Hallucinated (Sai kiến trúc / Không áp dụng)** | SQLite là một thư viện C nhúng chạy in-process và truy cập tệp cục bộ (`database.sqlite`), không phải Client-Server RDBMS (như PostgreSQL hay MySQL). Thư viện `sqlite3` trong Node.js sử dụng một đối tượng `new sqlite3.Database()` duy nhất. Tạo nhiều connection không tăng tính song song mà còn gây lỗi `SQLITE_BUSY` do tranh chấp khóa file cấp tiến trình. | Không áp dụng được cho CSDL file-based SQLite. |
| **3. Bật chế độ SQLite WAL (Write-Ahead Logging)** | **Feasible (Khả thi & Khuyến nghị cao)** | Mặc định SQLite sử dụng rollback journal (`DELETE` mode). Khi có thao tác ghi (POST/PUT/DELETE category), toàn bộ database bị khóa độc quyền (Exclusive Lock), khiến các request đọc (`/api/categories`, `/api/products`) bị block nhẹ, dẫn đến p99 DELETE đạt 152 ms ở 80 VU. WAL mode cho phép Readers và Writer chạy đồng thời mà không nghẽn. | **Baseline:** Run Stress 80 VU hiện tại (DELETE p95 = 32 ms, p99 = 152 ms).<br>**Experiment:** Thêm `db.run('PRAGMA journal_mode = WAL;')` trong `database.js`. Chạy lại Stress 80 VU cùng tham số, so sánh p95/p99 của nhóm transactional và read-heavy. |
| **4. Thêm B-Tree Index cho `users(email)`** | **Feasible (Khả thi)** | Trong `database.js`, bảng `users` được tạo với `email TEXT UNIQUE`, nhưng chưa có index tường minh và endpoint `/api/login` thực hiện `SELECT * FROM users WHERE email = ?`. Dù hiện tại 102 tài khoản test latency p95 login chỉ là 8 ms, nhưng khi hệ thống mở rộng quy mô lên hàng trăm nghìn người dùng, việc thiếu index sẽ chuyển truy vấn đăng nhập thành Full Table Scan ($O(N)$), làm sụp đổ thông lượng authentication. | **Baseline:** Tạo 50.000 user giả lập trong SQLite, chạy 80 VU Login.<br>**Experiment:** Tạo `CREATE INDEX idx_users_email ON users(email);`, chạy lại và so sánh CPU Node.js và p95 latency của `/api/login`. |
| **5. Giảm Think-Time từ 1–3s xuống 100–300ms** | **Feasible (Khả thi phục vụ Stress Test)** | Think-time 1–3s hiện tại phản ánh đúng hành vi người dùng thật (realistic human pacing), nhưng khiến 80 VU chỉ tạo ra ~40 req/s. Để tìm điểm bão hòa tuyệt đối của Node.js Event Loop trên laptop TRONGHOA, việc hạ think-time xuống 100–300ms sẽ đẩy RPS lên 150–200 req/s, làm bộc lộ ngưỡng nghẽn CPU hoặc disk I/O. | Giữ nguyên 80 VU, giảm UniformRandomTimer trong JMX xuống `min=100ms, max=300ms`. Chạy trong 2 phút và ghi nhận mức trần CPU core của backend. |

---

## 3. Dự thảo GitHub Issues dựa trên thử nghiệm thực tế (Edge Cases C07, C08, C09)

### Issue 1: Lỗi nghiệp vụ Khóa tài khoản (Account Lockout)
* **Tiêu đề:** `[BUG] Account Lockout locks account after only 2 failed attempts and sets 180s duration instead of spec FR-02`
* **Mức độ:** High (Sai lệch đặc tả yêu cầu chức năng)
* **File liên quan:** `src/eshop-sut/backend/server.js` (Route `POST /api/login`)
* **Mô tả:**
  * Theo đặc tả `FR-02`: Hệ thống phải khóa tài khoản sau **3 lần đăng nhập sai liên tiếp** trong khoảng thời gian **30 giây**.
  * Hành vi thực tế: Mã nguồn tăng biến đếm `login_attempts += 2` trong mỗi lần sai (`server.js` line ~86). Do đó, chỉ sau **2 lần đăng nhập sai**, biến đếm đạt giá trị 4 (vượt ngưỡng $\ge 3$) và kích hoạt khóa tài khoản. Ngoài ra, thời gian khóa được gán là `Date.now() + 180 * 1000` (**180 giây** thay vì 30 giây).
* **Bằng chứng tái hiện:** Đã chạy script `probe_edge_cases.py`, kết quả lưu tại `analysis/edge-cases.json` (C07):
  * Lần 1: Sai mật khẩu $\rightarrow$ HTTP 401
  * Lần 2: Sai mật khẩu $\rightarrow$ HTTP 401 (`login_attempts` trong DB = 4)
  * Lần 3: Dùng đúng mật khẩu $\rightarrow$ Bị chặn HTTP 403: `"Tài khoản đã bị khóa. Vui lòng thử lại sau."`

### Issue 2: Lỗ hổng bảo mật Phân quyền danh mục (Authorization Bypass)
* **Tiêu đề:** `[SECURITY] Regular user tokens can create, modify, and delete categories (Violation of FR-12)`
* **Mức độ:** Critical (Lỗ hổng phân quyền truy cập)
* **File liên quan:** `src/eshop-sut/backend/server.js` (`/api/categories` POST/PUT/DELETE)
* **Mô tả:**
  * Theo đặc tả `FR-12` & `FR-14`: Quản lý danh mục (Category CRUD) là chức năng thuộc Web Admin (Pool C), bắt buộc phải có quyền Quản trị viên (`role === 'admin'`).
  * Hành vi thực tế: Các route POST, PUT, DELETE `/api/categories` chỉ sử dụng middleware `authenticateToken` để kiểm tra tính hợp lệ của JWT, nhưng **hoàn toàn bỏ quên middleware kiểm tra quyền `requireAdmin`**.
* **Bằng chứng tái hiện:** Thử nghiệm C08 trong `analysis/edge-cases.json`:
  * Tạo JWT với payload `role: 'user'` (tài khoản người mua hàng thông thường).
  * Gửi `POST /api/categories` với body `{"name":"Hacked Category"}` $\rightarrow$ Trả về **HTTP 200 OK**, `id: 7345`.
  * Gửi PUT và DELETE với token user $\rightarrow$ Đều trả về **HTTP 200 OK**.

### Issue 3: Xử lý ngoại lệ ID không tồn tại trả về thành công giả (Fake Success)
* **Tiêu đề:** `[API] PUT and DELETE /api/categories/:id return 200 OK when category ID does not exist`
* **Mức độ:** Low / Improvement
* **File liên quan:** `src/eshop-sut/backend/server.js`
* **Mô tả:** Khi gửi request cập nhật hoặc xóa với ID không tồn tại trong CSDL (ví dụ `id = 2147483647`), API vẫn trả về `HTTP 200 OK` với thông báo `Category updated` / `Category deleted` thay vì trả về `HTTP 404 Not Found`. Do câu lệnh SQLite `UPDATE` / `DELETE` thực thi thành công nhưng ảnh hưởng 0 dòng (`this.changes === 0`).
